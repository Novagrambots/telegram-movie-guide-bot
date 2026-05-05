"""Избранное и просмотренное"""
import asyncio
import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.database import async_session
from bot.database.crud import (
    get_cached_movie,
    get_user_favorites,
    get_user_language,
    get_user_watched,
)
from bot.i18n import t
from bot.keyboards.inline import get_back_keyboard, get_results_keyboard
from bot.services import tmdb

logger = logging.getLogger(__name__)
router = Router()


async def _resolve_one(rec, lang: str) -> dict:
    """Подгружает заголовок одной записи (Favorite/Watched) → TMDB-like item"""
    item: dict = {
        "id": rec.tmdb_id,
        "media_type": rec.media_type,
    }
    # пытаемся достать заголовок из кэша
    async with async_session() as session:
        cached = await get_cached_movie(
            session, rec.tmdb_id, rec.media_type, lang=lang, ttl_days=0
        )
    title = None
    year = None
    if cached:
        title = cached.title_ru or cached.title_orig
        year = cached.year
    else:
        # подтягиваем из TMDB (вызов уйдёт в кэш)
        try:
            if rec.media_type == "movie":
                data = await tmdb.get_movie(rec.tmdb_id, lang)
            else:
                data = await tmdb.get_tv(rec.tmdb_id, lang)
            title = data.get("title") or data.get("name")
            date = data.get("release_date") or data.get("first_air_date") or ""
            year = int(date[:4]) if date[:4].isdigit() else None
        except Exception:
            year = None
    if rec.media_type == "movie":
        item["title"] = title or "?"
        if year:
            item["release_date"] = f"{year}-01-01"
    else:
        item["name"] = title or "?"
        if year:
            item["first_air_date"] = f"{year}-01-01"
    return item


async def _items_from_records(records, lang: str) -> list[dict]:
    """Превращаем Favorite/Watched записи в формат TMDB items (параллельно)"""
    if not records:
        return []
    return await asyncio.gather(*[_resolve_one(rec, lang) for rec in records])


async def _reply(event, text: str, reply_markup=None) -> None:
    if isinstance(event, CallbackQuery):
        await event.message.answer(text, reply_markup=reply_markup, parse_mode="HTML")
        await event.answer()
    else:
        await event.answer(text, reply_markup=reply_markup, parse_mode="HTML")


@router.message(Command("favorites"))
@router.callback_query(F.data == "user_favorites")
async def cmd_favorites(event) -> None:
    user_id = event.from_user.id
    async with async_session() as session:
        lang = await get_user_language(session, user_id)
        favs = await get_user_favorites(session, user_id)
    if not favs:
        await _reply(event, t("favorites.empty", lang), reply_markup=get_back_keyboard(lang))
        return
    items = await _items_from_records(favs, lang)
    await _reply(
        event,
        t("favorites.title", lang, count=len(items)),
        reply_markup=get_results_keyboard(items, lang),
    )


@router.message(Command("watched"))
@router.callback_query(F.data == "user_watched")
async def cmd_watched(event) -> None:
    user_id = event.from_user.id
    async with async_session() as session:
        lang = await get_user_language(session, user_id)
        seen = await get_user_watched(session, user_id)
    if not seen:
        await _reply(event, t("watched.empty", lang), reply_markup=get_back_keyboard(lang))
        return
    items = await _items_from_records(seen, lang)
    await _reply(
        event,
        t("watched.title", lang, count=len(items)),
        reply_markup=get_results_keyboard(items, lang),
    )
