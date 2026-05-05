"""Inline-режим: @bot_username <query> → список фильмов с постерами"""
import hashlib
import logging

from aiogram import Router
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InlineQueryResultPhoto,
    InputTextMessageContent,
)

from bot.i18n import detect_language
from bot.services import tmdb

logger = logging.getLogger(__name__)
router = Router()


def _make_id(prefix: str, value: str) -> str:
    return prefix + hashlib.md5(value.encode()).hexdigest()[:16]


@router.inline_query()
async def inline_search(query: InlineQuery) -> None:
    text = (query.query or "").strip()
    if not text or len(text) < 2:
        await query.answer(results=[], cache_time=10, is_personal=True)
        return
    lang = detect_language(query.from_user.language_code)
    try:
        result = await tmdb.search_multi(text, lang=lang)
    except tmdb.TMDBError as exc:
        logger.warning("Inline TMDB error: %s", exc)
        await query.answer(results=[], cache_time=5, is_personal=True)
        return

    items = result.get("results") or []
    items = [
        x for x in items
        if x.get("media_type") in ("movie", "tv")
    ][:10]

    answers = []
    for item in items:
        mt = item["media_type"]
        tmdb_id = item["id"]
        title = item.get("title") or item.get("name") or "?"
        date = item.get("release_date") or item.get("first_air_date") or ""
        year = f" ({date[:4]})" if date else ""
        rating = item.get("vote_average") or 0
        overview = (item.get("overview") or "").strip() or t("movie.no_overview", lang)
        if len(overview) > 300:
            overview = overview[:300].rsplit(" ", 1)[0] + "…"
        poster = tmdb.poster_url(item.get("poster_path"))
        bot_user = query.bot
        deeplink_text = (
            f"🎬 <b>{title}</b>{year}\n"
            f"⭐ {rating:.1f}\n\n"
            f"{overview}\n\n"
            f"<i>{t('inline.open_bot', lang)}</i>"
        )
        msg_content = InputTextMessageContent(
            message_text=deeplink_text,
            parse_mode="HTML",
        )
        if poster:
            answers.append(InlineQueryResultPhoto(
                id=_make_id(f"{mt}_", str(tmdb_id)),
                photo_url=poster,
                thumbnail_url=poster,
                title=f"{title}{year}",
                description=f"⭐ {rating:.1f} • {overview[:120]}",
                caption=deeplink_text,
                parse_mode="HTML",
            ))
        else:
            answers.append(InlineQueryResultArticle(
                id=_make_id(f"{mt}_", str(tmdb_id)),
                title=f"{title}{year}",
                description=f"⭐ {rating:.1f} • {overview[:120]}",
                input_message_content=msg_content,
            ))

    await query.answer(results=answers, cache_time=60, is_personal=True)
