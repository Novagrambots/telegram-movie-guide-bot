"""Карточка фильма/сериала и связанные действия"""
import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)

from bot.emojis import E_ID
from bot.database import async_session
from bot.database.crud import (
    add_favorite,
    add_watched,
    get_user_language,
    increment_request_count,
    is_favorite,
    is_watched,
    remove_favorite,
    remove_watched,
    save_poster_file_id,
)
from bot.i18n import t, t_plain
from bot.keyboards.inline import (
    _result_title,
    get_back_keyboard,
    get_close_keyboard,
    get_movie_keyboard,
    get_results_keyboard,
)
from bot.services import tmdb

logger = logging.getLogger(__name__)
router = Router()


def _format_card(data: dict, media_type: str, lang: str) -> str:
    """Форматирует карточку фильма/сериала"""
    if media_type == "movie":
        title = data.get("title") or data.get("original_title") or "?"
        date_str = data.get("release_date") or ""
        icon = "🎬"
    else:
        title = data.get("name") or data.get("original_name") or "?"
        date_str = data.get("first_air_date") or ""
        icon = "📺"
    year = f" ({date_str[:4]})" if date_str else ""
    rating = data.get("vote_average") or 0
    votes = data.get("vote_count") or 0
    rating_line = ""
    if rating:
        rating_line = f"⭐ <b>{rating:.1f}</b> ({votes} {t('movie.votes', lang)})\n"
    genres = data.get("genres") or []
    genres_line = ""
    if genres:
        genres_line = "🎭 " + ", ".join(g["name"] for g in genres[:5])
    overview = data.get("overview") or t("movie.no_overview", lang)
    if len(overview) > 700:
        overview = overview[:700].rsplit(" ", 1)[0] + "…"

    text = t(
        "movie.card",
        lang,
        icon=icon,
        title=title,
        year=year,
        rating=rating_line,
        genres=genres_line,
        overview=overview,
    )
    if media_type == "tv":
        seasons = data.get("number_of_seasons")
        episodes = data.get("number_of_episodes")
        if seasons:
            text += "\n\n📚 " + t("movie.seasons", lang, seasons=seasons, episodes=episodes or "?")
    runtime = data.get("runtime")
    if runtime:
        h, m = divmod(runtime, 60)
        h_label = t("movie.hours", lang)
        m_label = t("movie.minutes", lang)
        text += f"\n\n⏱ {h}{h_label} {m}{m_label}" if h else f"\n\n⏱ {m}{m_label}"
    return text


async def _send_card(
    callback: CallbackQuery,
    tmdb_id: int,
    media_type: str,
) -> None:
    async with async_session() as session:
        lang = await get_user_language(session, callback.from_user.id)

    try:
        if media_type == "movie":
            data = await tmdb.get_movie(tmdb_id, lang)
        else:
            data = await tmdb.get_tv(tmdb_id, lang)
    except tmdb.TMDBNotFound:
        await callback.answer(t_plain("error.not_found", lang), show_alert=True)
        return
    except tmdb.TMDBQuotaError:
        await callback.answer(t_plain("error.tmdb_unavailable", lang), show_alert=True)
        return
    except tmdb.TMDBError as exc:
        logger.warning("TMDB error: %s", exc)
        await callback.answer(t_plain("error.generic", lang), show_alert=True)
        return

    text = _format_card(data, media_type, lang)
    has_trailer = bool(_find_trailer(data))

    async with async_session() as session:
        is_fav = await is_favorite(session, callback.from_user.id, tmdb_id, media_type)
        is_seen = await is_watched(session, callback.from_user.id, tmdb_id, media_type)
        await increment_request_count(session, callback.from_user.id)

    kb = get_movie_keyboard(
        tmdb_id=tmdb_id,
        media_type=media_type,
        is_fav=is_fav,
        is_seen=is_seen,
        has_trailer=has_trailer,
        lang=lang,
    )

    poster = tmdb.poster_url(data.get("poster_path"))
    # пробуем file_id из кэша
    file_id = None
    async with async_session() as session:
        from bot.database.crud import get_cached_movie
        cached = await get_cached_movie(session, tmdb_id, media_type, lang=lang, ttl_days=0)
        if cached:
            file_id = cached.poster_file_id

    media_src = file_id or poster
    try:
        if media_src:
            sent = await callback.message.answer_photo(
                photo=media_src,
                caption=text[:1024],
                reply_markup=kb,
                parse_mode="HTML",
            )
            # сохраняем file_id для будущих запросов
            if not file_id and sent.photo:
                async with async_session() as session:
                    await save_poster_file_id(
                        session, tmdb_id, media_type, sent.photo[-1].file_id
                    )
        else:
            await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
    except TelegramBadRequest as exc:
        logger.warning("Не удалось отправить постер: %s", exc)
        await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")

    await callback.answer()


@router.callback_query(F.data.regexp(r"^movie:\d+$"))
async def open_movie(callback: CallbackQuery) -> None:
    tmdb_id = int(callback.data.split(":", 1)[1])
    await _send_card(callback, tmdb_id, "movie")


@router.callback_query(F.data.regexp(r"^tv:\d+$"))
async def open_tv(callback: CallbackQuery) -> None:
    tmdb_id = int(callback.data.split(":", 1)[1])
    await _send_card(callback, tmdb_id, "tv")


# === Трейлер ===

def _find_trailer(data: dict) -> dict | None:
    videos = (data.get("videos") or {}).get("results") or []
    # сначала Trailer + YouTube
    for v in videos:
        if v.get("site") == "YouTube" and v.get("type") == "Trailer":
            return v
    for v in videos:
        if v.get("site") == "YouTube":
            return v
    return None


@router.callback_query(F.data.regexp(r"^trailer:(movie|tv):\d+$"))
async def show_trailer(callback: CallbackQuery) -> None:
    _, media_type, mid = callback.data.split(":")
    tmdb_id = int(mid)
    async with async_session() as session:
        lang = await get_user_language(session, callback.from_user.id)
    try:
        data = await (tmdb.get_movie(tmdb_id, lang) if media_type == "movie"
                      else tmdb.get_tv(tmdb_id, lang))
    except tmdb.TMDBError:
        await callback.answer(t_plain("error.generic", lang), show_alert=True)
        return
    trailer = _find_trailer(data)
    if not trailer:
        await callback.answer(t_plain("movie.no_trailer", lang), show_alert=True)
        return
    url = f"https://www.youtube.com/watch?v={trailer['key']}"
    await callback.message.answer(
        t("movie.trailer", lang, url=url, name=trailer.get("name", "Trailer")),
        reply_markup=get_close_keyboard(lang),
        parse_mode="HTML",
        disable_web_page_preview=False,
    )
    await callback.answer()


# === Где посмотреть ===

@router.callback_query(F.data.regexp(r"^watch:(movie|tv):\d+$"))
async def show_watch_providers(callback: CallbackQuery) -> None:
    _, media_type, mid = callback.data.split(":")
    tmdb_id = int(mid)
    async with async_session() as session:
        lang = await get_user_language(session, callback.from_user.id)
    try:
        data = await (tmdb.get_movie(tmdb_id, lang) if media_type == "movie"
                      else tmdb.get_tv(tmdb_id, lang))
    except tmdb.TMDBError:
        await callback.answer(t_plain("error.generic", lang), show_alert=True)
        return

    user_region = {"ru": "RU", "uz": "UZ", "en": "US"}.get(lang, "RU")
    providers_root = (data.get("watch/providers") or {}).get("results") or {}
    # фолбэк по регионам: сначала юзерский, потом популярные англоязычные/СНГ
    region = None
    region_data = None
    for r in [user_region, "US", "GB", "RU", "UA", "KZ", "DE", "FR"]:
        if providers_root.get(r):
            region = r
            region_data = providers_root[r]
            break
    # последний шанс — любой регион где есть данные
    if not region_data:
        for r, rd in providers_root.items():
            if rd:
                region = r
                region_data = rd
                break
    if not region_data:
        await callback.answer(
            t_plain("movie.no_watch", lang, region=user_region), show_alert=True,
        )
        return

    text_parts = [t("movie.watch_title", lang, region=region)]
    for kind_key in ("flatrate", "rent", "buy", "free"):
        items = region_data.get(kind_key) or []
        if items:
            names = ", ".join(x.get("provider_name", "?") for x in items[:6])
            text_parts.append(f"<b>{t(f'movie.provider.{kind_key}', lang)}:</b> {names}")
    link = region_data.get("link")
    kb_buttons = []
    if link:
        kb_buttons.append([InlineKeyboardButton(text="🔗 TMDB", url=link)])
    kb_buttons.append([InlineKeyboardButton(text=t("btn.back", lang), callback_data="close_msg", style="success", icon_custom_emoji_id=E_ID["back"])])
    await callback.message.answer(
        "\n".join(text_parts),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_buttons),
        parse_mode="HTML",
    )
    await callback.answer()


# === Актёры ===

@router.callback_query(F.data.regexp(r"^cast:(movie|tv):\d+$"))
async def show_cast(callback: CallbackQuery) -> None:
    logger.info("CAST clicked: %s by user %s", callback.data, callback.from_user.id)
    _, media_type, mid = callback.data.split(":")
    tmdb_id = int(mid)
    async with async_session() as session:
        lang = await get_user_language(session, callback.from_user.id)
    try:
        data = await (tmdb.get_movie(tmdb_id, lang) if media_type == "movie"
                      else tmdb.get_tv(tmdb_id, lang))
    except tmdb.TMDBError:
        await callback.answer(t_plain("error.generic", lang), show_alert=True)
        return
    cast = (data.get("credits") or {}).get("cast") or []
    # фолбэк: TMDB для uz-UZ часто не возвращает credits — пробуем ru, потом en
    if not cast and lang != "ru":
        try:
            fb = await (tmdb.get_movie(tmdb_id, "ru") if media_type == "movie"
                        else tmdb.get_tv(tmdb_id, "ru"))
            cast = (fb.get("credits") or {}).get("cast") or []
        except tmdb.TMDBError:
            pass
    if not cast and lang != "en":
        try:
            fb = await (tmdb.get_movie(tmdb_id, "en") if media_type == "movie"
                        else tmdb.get_tv(tmdb_id, "en"))
            cast = (fb.get("credits") or {}).get("cast") or []
        except tmdb.TMDBError:
            pass
    if not cast:
        await callback.answer(t_plain("movie.no_cast", lang), show_alert=True)
        return
    lines = [t("movie.cast_title", lang)]
    rows: list[list[InlineKeyboardButton]] = []
    for c in cast[:10]:
        name = c.get("name") or "?"
        char = c.get("character") or ""
        person_id = c.get("id")
        if char:
            lines.append(f"• <b>{name}</b> — <i>{char}</i>")
        else:
            lines.append(f"• <b>{name}</b>")
        if person_id:
            label = f"👤 {name}" + (f" — {char}" if char else "")
            rows.append([InlineKeyboardButton(
                text=label[:60],
                callback_data=f"person:{person_id}",
                style="primary",
            )])
    rows.append([InlineKeyboardButton(
        text=t("btn.back", lang),
        callback_data="close_msg",
        style="success",
        icon_custom_emoji_id=E_ID["back"],
    )])
    await callback.message.answer(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
        parse_mode="HTML",
    )
    await callback.answer()


# === Карточка персоны (актёр/режиссёр) ===

@router.callback_query(F.data.regexp(r"^person:\d+$"))
async def show_person(callback: CallbackQuery) -> None:
    person_id = int(callback.data.split(":", 1)[1])
    async with async_session() as session:
        lang = await get_user_language(session, callback.from_user.id)
    try:
        credits = await tmdb.get_person_credits(person_id, lang)
    except tmdb.TMDBError:
        await callback.answer(t_plain("error.generic", lang), show_alert=True)
        return

    cast_items = credits.get("cast") or []
    crew_items = credits.get("crew") or []
    person_name = ""
    if cast_items:
        person_name = ""  # not in credits response
    # лучше дёрнуть имя через /person/{id}
    try:
        from bot.services.tmdb import _request, _tmdb_locale
        language, _ = _tmdb_locale(lang)
        info = await _request(f"/person/{person_id}", {"language": language})
        person_name = info.get("name") or ""
    except Exception:
        pass

    EXCLUDED_GENRES = {10763, 10764, 10767}  # News, Reality, Talk

    def _filter(order_threshold: int) -> list[dict]:
        seen: set[tuple[int, str]] = set()
        out: list[dict] = []
        for c in cast_items:
            mt = c.get("media_type") or "movie"
            cid = c.get("id")
            if not cid or (cid, mt) in seen:
                continue
            order = c.get("order") if c.get("order") is not None else 99
            if order >= order_threshold:
                continue
            if set(c.get("genre_ids") or []) & EXCLUDED_GENRES:
                continue
            if mt == "tv" and (c.get("episode_count") or 0) < 3:
                continue
            seen.add((cid, mt))
            c["media_type"] = mt
            out.append(c)
        return out

    # сначала жёсткий фильтр (order<5); если меньше 3 фильмов — расширяем до order<10, потом до 99
    items = _filter(5)
    if len(items) < 3:
        items = _filter(10)
    if len(items) < 3:
        items = _filter(99)
    items.sort(key=lambda x: x.get("popularity") or 0, reverse=True)
    items = items[:10]

    if not items:
        await callback.answer(t_plain("actor.not_found", lang), show_alert=True)
        return

    title = t("actor.title", lang, name=person_name or "?")
    await callback.message.answer(
        title,
        reply_markup=get_results_keyboard(items, lang, back_callback="close_msg"),
        parse_mode="HTML",
    )
    await callback.answer()


# === Похожие ===

@router.callback_query(F.data.regexp(r"^similar:(movie|tv):\d+$"))
async def show_similar(callback: CallbackQuery) -> None:
    _, media_type, mid = callback.data.split(":")
    tmdb_id = int(mid)
    async with async_session() as session:
        lang = await get_user_language(session, callback.from_user.id)
    try:
        data = await (tmdb.get_movie(tmdb_id, lang) if media_type == "movie"
                      else tmdb.get_tv(tmdb_id, lang))
    except tmdb.TMDBError:
        await callback.answer(t_plain("error.generic", lang), show_alert=True)
        return
    # TMDB recommendations использует алгоритм рекомендаций (на основе поведения юзеров),
    # similar — просто совпадение по жанру/ключевым словам и часто отдаёт мусор
    similar = (data.get("recommendations") or {}).get("results") or []
    if not similar:
        similar = (data.get("similar") or {}).get("results") or []
    if not similar:
        await callback.answer(t_plain("movie.no_similar", lang), show_alert=True)
        return
    for s in similar:
        s["media_type"] = media_type
    kb = get_results_keyboard(similar[:10], lang, back_callback="close_msg")
    await callback.message.answer(
        t("movie.similar_title", lang),
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


# === Избранное toggle ===

# защита от двойного клика: {(user_id, callback_data): timestamp}
_toggle_throttle: dict[tuple[int, str], float] = {}
_TOGGLE_THROTTLE_SEC = 1.5


def _is_double_click(user_id: int, data: str) -> bool:
    import time
    key = (user_id, data)
    now = time.time()
    last = _toggle_throttle.get(key, 0)
    if now - last < _TOGGLE_THROTTLE_SEC:
        return True
    _toggle_throttle[key] = now
    # очистка протухших записей (раз в ~100 кликов)
    if len(_toggle_throttle) > 500:
        cutoff = now - _TOGGLE_THROTTLE_SEC
        for k in [k for k, v in _toggle_throttle.items() if v < cutoff]:
            _toggle_throttle.pop(k, None)
    return False


@router.callback_query(F.data.regexp(r"^fav:(movie|tv):\d+$"))
async def toggle_favorite(callback: CallbackQuery) -> None:
    if _is_double_click(callback.from_user.id, callback.data):
        await callback.answer()
        return
    _, media_type, mid = callback.data.split(":")
    tmdb_id = int(mid)
    async with async_session() as session:
        lang = await get_user_language(session, callback.from_user.id)
        # атомарный toggle: пытаемся удалить, если не было — добавляем (UPSERT)
        removed = await remove_favorite(
            session, callback.from_user.id, tmdb_id, media_type
        )
        if removed:
            await callback.answer(t_plain("fav.removed", lang))
            new_fav = False
        else:
            await add_favorite(session, callback.from_user.id, tmdb_id, media_type)
            await callback.answer(t_plain("fav.added", lang))
            new_fav = True
        is_seen = await is_watched(session, callback.from_user.id, tmdb_id, media_type)

    # обновляем клавиатуру под сообщением
    try:
        await callback.message.edit_reply_markup(
            reply_markup=get_movie_keyboard(
                tmdb_id, media_type, is_fav=new_fav, is_seen=is_seen, lang=lang,
            )
        )
    except TelegramBadRequest:
        pass


# === Просмотрено toggle ===

@router.callback_query(F.data.regexp(r"^seen:(movie|tv):\d+$"))
async def toggle_watched(callback: CallbackQuery) -> None:
    if _is_double_click(callback.from_user.id, callback.data):
        await callback.answer()
        return
    _, media_type, mid = callback.data.split(":")
    tmdb_id = int(mid)
    async with async_session() as session:
        lang = await get_user_language(session, callback.from_user.id)
        # атомарный toggle: пытаемся удалить, если не было — добавляем (UPSERT)
        removed = await remove_watched(
            session, callback.from_user.id, tmdb_id, media_type
        )
        if removed:
            await callback.answer(t_plain("seen.removed", lang))
            new_seen = False
        else:
            await add_watched(session, callback.from_user.id, tmdb_id, media_type)
            await callback.answer(t_plain("seen.added", lang))
            new_seen = True
        is_fav = await is_favorite(session, callback.from_user.id, tmdb_id, media_type)

    try:
        await callback.message.edit_reply_markup(
            reply_markup=get_movie_keyboard(
                tmdb_id, media_type, is_fav=is_fav, is_seen=new_seen, lang=lang,
            )
        )
    except TelegramBadRequest:
        pass
