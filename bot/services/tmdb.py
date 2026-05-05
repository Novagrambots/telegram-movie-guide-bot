"""TMDB API клиент с кэшированием в БД и rate-limit"""
import asyncio
import logging
import random
from typing import Any

import httpx

from bot.config import settings
from bot.database import async_session
from bot.database.crud import get_cached_movie, save_movie_cache

logger = logging.getLogger(__name__)

TMDB_BASE = "https://api.themoviedb.org/3"
IMG_BASE = "https://image.tmdb.org/t/p/w500"

# глобальный семафор: не более 10 параллельных запросов к TMDB
_semaphore = asyncio.Semaphore(10)

# глобальный httpx-клиент (lazy, с keepalive) — один на всё приложение
_client: httpx.AsyncClient | None = None
_client_lock = asyncio.Lock()


async def _get_client() -> httpx.AsyncClient:
    """Возвращает глобальный httpx-клиент, создавая его при первом вызове"""
    global _client
    if _client is None or _client.is_closed:
        async with _client_lock:
            if _client is None or _client.is_closed:
                _client = httpx.AsyncClient(
                    timeout=30,
                    limits=httpx.Limits(
                        max_keepalive_connections=10,
                        max_connections=20,
                        keepalive_expiry=30,
                    ),
                )
    return _client


async def close_client() -> None:
    """Закрывает глобальный httpx-клиент (вызывается на shutdown)"""
    global _client
    if _client is not None and not _client.is_closed:
        await _client.aclose()
    _client = None

# языки TMDB
LANG_MAP = {"ru": "ru-RU", "uz": "uz-UZ", "en": "en-US"}
REGION_MAP = {"ru": "RU", "uz": "UZ", "en": "US"}


def _tmdb_locale(lang: str | None) -> tuple[str, str]:
    """Возвращает (language, region) для TMDB по короткому коду языка"""
    if not lang:
        return ("ru-RU", "RU")
    return {
        "ru": ("ru-RU", "RU"),
        "uz": ("uz-UZ", "UZ"),
        "en": ("en-US", "US"),
    }.get(lang, ("ru-RU", "RU"))


def _lang(lang: str | None) -> str:
    """Резолв только языка (для обратной совместимости)"""
    return _tmdb_locale(lang)[0]


def poster_url(path: str | None) -> str | None:
    """Полный URL постера TMDB"""
    if not path:
        return None
    return f"{IMG_BASE}{path}"


class TMDBError(Exception):
    pass


class TMDBNotFound(TMDBError):
    pass


class TMDBQuotaError(TMDBError):
    pass


async def _request(
    endpoint: str,
    params: dict[str, Any] | None = None,
) -> dict:
    """Базовый запрос к TMDB с retry на 429/5xx"""
    if not settings.tmdb_api_key and not settings.tmdb_bearer_token:
        raise TMDBError("TMDB ключ не задан в .env")

    url = f"{TMDB_BASE}{endpoint}"
    params = dict(params or {})
    headers: dict[str, str] = {"Accept": "application/json"}

    if settings.tmdb_bearer_token:
        headers["Authorization"] = f"Bearer {settings.tmdb_bearer_token}"
    else:
        params["api_key"] = settings.tmdb_api_key

    last_exc: Exception | None = None
    for attempt in range(3):
        async with _semaphore:
            try:
                client = await _get_client()
                resp = await client.get(url, params=params, headers=headers)
                if resp.status_code == 404:
                    raise TMDBNotFound(f"404: {endpoint}")
                if resp.status_code == 401:
                    raise TMDBError("401 Unauthorized — проверь TMDB ключ")
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", "2"))
                    logger.warning("TMDB 429 — жду %s сек", retry_after)
                    await asyncio.sleep(retry_after)
                    last_exc = TMDBQuotaError("429 rate limit")
                    continue
                if resp.status_code >= 500:
                    last_exc = TMDBError(f"{resp.status_code} server error")
                    delay = (2 ** attempt) + random.random()
                    await asyncio.sleep(delay)
                    continue
                resp.raise_for_status()
                return resp.json()
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                last_exc = exc
                logger.warning("TMDB сеть, попытка %d: %s", attempt + 1, exc)
                await asyncio.sleep((2 ** attempt) + random.random())
            except TMDBNotFound:
                raise
    raise last_exc or TMDBError("TMDB запрос не удался")


# === Поиск ===

async def search_multi(query: str, lang: str = "ru", page: int = 1) -> dict:
    language, _ = _tmdb_locale(lang)
    return await _request(
        "/search/multi",
        {"query": query, "language": language, "page": page,
         "include_adult": "false"},
    )


async def search_person(query: str, lang: str = "ru", page: int = 1) -> dict:
    language, _ = _tmdb_locale(lang)
    return await _request(
        "/search/person",
        {"query": query, "language": language, "page": page,
         "include_adult": "false"},
    )


async def get_person_credits(person_id: int, lang: str = "ru") -> dict:
    language, _ = _tmdb_locale(lang)
    return await _request(
        f"/person/{person_id}/combined_credits",
        {"language": language},
    )


# === Карточка фильма/сериала с кэшем ===

def _extract_meta(data: dict, media_type: str) -> tuple[str | None, str | None, int | None, str | None]:
    if media_type == "movie":
        title_ru = data.get("title")
        title_orig = data.get("original_title")
        date_str = data.get("release_date") or ""
    else:
        title_ru = data.get("name")
        title_orig = data.get("original_name")
        date_str = data.get("first_air_date") or ""
    year = None
    if date_str and len(date_str) >= 4:
        try:
            year = int(date_str[:4])
        except ValueError:
            year = None
    return title_ru, title_orig, year, poster_url(data.get("poster_path"))


async def get_movie(tmdb_id: int, lang: str = "ru", use_cache: bool = True) -> dict:
    """Карточка фильма + videos, credits, watch/providers, similar"""
    return await _get_media(tmdb_id, "movie", lang, use_cache)


async def get_tv(tmdb_id: int, lang: str = "ru", use_cache: bool = True) -> dict:
    """Карточка сериала + videos, credits, watch/providers, similar"""
    return await _get_media(tmdb_id, "tv", lang, use_cache)


async def _get_media(
    tmdb_id: int, media_type: str, lang: str, use_cache: bool
) -> dict:
    language, _ = _tmdb_locale(lang)
    if use_cache:
        async with async_session() as session:
            cached = await get_cached_movie(
                session, tmdb_id, media_type, lang=lang,
                ttl_days=settings.cache_ttl_days,
            )
            if cached:
                return cached.data

    data = await _request(
        f"/{media_type}/{tmdb_id}",
        {
            "language": language,
            "append_to_response": "videos,credits,watch/providers,similar,recommendations",
        },
    )

    # Fallback на пустое описание/жанры: для uz/en пробуем сначала en, потом ru
    fb_order = ("en", "ru") if lang != "ru" else ("en",)
    needs_overview = not (data.get("overview") or "").strip()
    needs_genres = not (data.get("genres") or [])
    if needs_overview or needs_genres:
        for fb_lang in fb_order:
            fb_language, _ = _tmdb_locale(fb_lang)
            if fb_language == language:
                continue
            try:
                fb_data = await _request(
                    f"/{media_type}/{tmdb_id}",
                    {"language": fb_language},
                )
            except TMDBError:
                continue
            if needs_overview:
                fb_overview = (fb_data.get("overview") or "").strip()
                if fb_overview:
                    data["overview"] = fb_overview
                    needs_overview = False
            if needs_genres:
                fb_genres = fb_data.get("genres") or []
                if fb_genres:
                    data["genres"] = fb_genres
                    needs_genres = False
            if not needs_overview and not needs_genres:
                break

    # Если юзер на uz и TMDB вернул всё на ru/en — переводим overview и жанры (параллельно)
    if lang == "uz":
        from bot.services.translator import translate
        import asyncio as _asyncio
        overview = (data.get("overview") or "").strip()
        genres = data.get("genres") or []
        labels: list = []
        coros: list = []
        if overview:
            labels.append("overview")
            coros.append(translate(overview, target_lang="uz", source_lang="auto"))
        for idx, g in enumerate(genres):
            name = g.get("name")
            if name:
                labels.append(("genre", idx))
                coros.append(translate(name, target_lang="uz", source_lang="en"))
        if coros:
            results = await _asyncio.gather(*coros, return_exceptions=True)
            for label, res in zip(labels, results):
                if isinstance(res, Exception) or not res:
                    continue
                if label == "overview" and res != overview:
                    data["overview"] = res
                elif isinstance(label, tuple) and label[0] == "genre":
                    genres[label[1]]["name"] = res

    title_ru, title_orig, year, p_url = _extract_meta(data, media_type)
    async with async_session() as session:
        await save_movie_cache(
            session=session,
            tmdb_id=tmdb_id,
            media_type=media_type,
            data=data,
            lang=lang,
            title_ru=title_ru,
            title_orig=title_orig,
            year=year,
            poster_url=p_url,
        )
    return data


# === Списки ===

async def get_trending(lang: str = "ru", window: str = "week") -> dict:
    language, _ = _tmdb_locale(lang)
    return await _request(
        f"/trending/all/{window}",
        {"language": language},
    )


async def get_top_rated(lang: str = "ru", page: int = 1) -> dict:
    language, _ = _tmdb_locale(lang)
    return await _request(
        "/movie/top_rated",
        {"language": language, "page": page},
    )


async def get_now_playing(lang: str = "ru", region: str | None = None, page: int = 1) -> dict:
    language, loc_region = _tmdb_locale(lang)
    return await _request(
        "/movie/now_playing",
        {"language": language, "region": region or loc_region, "page": page},
    )


async def get_upcoming(lang: str = "ru", region: str | None = None, page: int = 1) -> dict:
    language, loc_region = _tmdb_locale(lang)
    return await _request(
        "/movie/upcoming",
        {"language": language, "region": region or loc_region, "page": page},
    )


async def get_popular(lang: str = "ru", page: int = 1) -> dict:
    language, _ = _tmdb_locale(lang)
    return await _request(
        "/movie/popular",
        {"language": language, "page": page},
    )


async def get_random(lang: str = "ru") -> dict:
    """Случайный фильм с рейтингом >= 7"""
    language, _ = _tmdb_locale(lang)
    page = random.randint(1, 20)
    data = await _request(
        "/discover/movie",
        {
            "language": language,
            "sort_by": "popularity.desc",
            "vote_count.gte": 500,
            "vote_average.gte": 7,
            "include_adult": "false",
            "page": page,
        },
    )
    results = data.get("results") or []
    if not results:
        return {}
    return random.choice(results)


# === Жанры / discover ===

async def get_genres(media_type: str = "movie", lang: str = "ru") -> dict:
    language, _ = _tmdb_locale(lang)
    endpoint = "/genre/movie/list" if media_type == "movie" else "/genre/tv/list"
    data = await _request(endpoint, {"language": language})
    # TMDB для uz часто возвращает name=null — фолбэк на en + перевод
    genres = data.get("genres") or []
    needs_fallback = any(not (g.get("name") or "").strip() for g in genres)
    if needs_fallback:
        try:
            en_data = await _request(endpoint, {"language": "en-US"})
            en_by_id = {g["id"]: g.get("name") for g in (en_data.get("genres") or [])}
            from bot.services.translator import translate
            for g in genres:
                if not (g.get("name") or "").strip():
                    en_name = en_by_id.get(g["id"]) or "?"
                    if lang == "uz" and en_name != "?":
                        g["name"] = await translate(en_name, target_lang="uz", source_lang="en")
                    else:
                        g["name"] = en_name
        except Exception:
            pass
    return data


async def get_by_genre(
    genre_id: int,
    lang: str = "ru",
    page: int = 1,
    media_type: str = "movie",
) -> dict:
    language, _ = _tmdb_locale(lang)
    endpoint = "/discover/movie" if media_type == "movie" else "/discover/tv"
    return await _request(
        endpoint,
        {
            "language": language,
            "with_genres": genre_id,
            "sort_by": "popularity.desc",
            "vote_count.gte": 200,
            "include_adult": "false",
            "page": page,
        },
    )
