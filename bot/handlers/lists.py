"""Списки: trending, top, now_playing, upcoming, random, genres"""
import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.database import async_session
from bot.database.crud import get_user_language, increment_request_count
from bot.i18n import t, t_plain
from bot.keyboards.inline import (
    get_back_keyboard,
    get_genres_keyboard,
    get_results_keyboard,
)
from bot.services import tmdb

logger = logging.getLogger(__name__)
router = Router()


def _user_id(event) -> int:
    return event.from_user.id


async def _reply(event, text: str, reply_markup=None) -> None:
    """Универсальный ответ: для CallbackQuery — новое сообщение под карточкой."""
    if isinstance(event, CallbackQuery):
        await event.message.answer(text, reply_markup=reply_markup, parse_mode="HTML")
        await event.answer()
    else:
        await event.answer(text, reply_markup=reply_markup, parse_mode="HTML")


async def _send_list(
    event,
    title_key: str,
    fetch_coro,
    media_type: str = "movie",
) -> None:
    async with async_session() as session:
        lang = await get_user_language(session, _user_id(event))
        await increment_request_count(session, _user_id(event))
    try:
        data = await fetch_coro(lang)
    except tmdb.TMDBError as exc:
        logger.warning("TMDB list error: %s", exc)
        await _reply(event, t("error.generic", lang))
        return
    items = data.get("results") or []
    for x in items:
        x.setdefault("media_type", media_type)
    items = items[:10]
    if not items:
        await _reply(event, t("error.not_found", lang))
        return
    await _reply(event, t(title_key, lang), reply_markup=get_results_keyboard(items, lang))


@router.message(Command("trending"))
@router.callback_query(F.data == "menu_trending")
async def cmd_trending(event) -> None:
    await _send_list(event, "lists.trending", lambda l: tmdb.get_trending(l))


@router.message(Command("top"))
@router.callback_query(F.data == "menu_top")
async def cmd_top(event) -> None:
    await _send_list(event, "lists.top", lambda l: tmdb.get_top_rated(l))


@router.message(Command("now_playing"))
@router.callback_query(F.data == "menu_now_playing")
async def cmd_now(event) -> None:
    await _send_list(event, "lists.now_playing", lambda l: tmdb.get_now_playing(l))


@router.message(Command("upcoming"))
@router.callback_query(F.data == "menu_upcoming")
async def cmd_upcoming(event) -> None:
    await _send_list(event, "lists.upcoming", lambda l: tmdb.get_upcoming(l))


@router.message(Command("random"))
@router.callback_query(F.data == "menu_random")
async def cmd_random(event) -> None:
    async with async_session() as session:
        lang = await get_user_language(session, _user_id(event))
        await increment_request_count(session, _user_id(event))
    try:
        item = await tmdb.get_random(lang)
    except tmdb.TMDBError:
        await _reply(event, t("error.generic", lang))
        return
    if not item:
        await _reply(event, t("error.not_found", lang))
        return
    item.setdefault("media_type", "movie")
    await _reply(
        event,
        f"🎲 <b>{item.get('title') or '?'}</b>",
        reply_markup=get_results_keyboard([item], lang),
    )


@router.message(Command("genres"))
@router.callback_query(F.data == "menu_genres")
async def cmd_genres(event) -> None:
    async with async_session() as session:
        lang = await get_user_language(session, _user_id(event))
    try:
        data = await tmdb.get_genres("movie", lang)
    except tmdb.TMDBError:
        await _reply(event, t("error.generic", lang))
        return
    genres = data.get("genres") or []
    if not genres:
        await _reply(event, t("error.not_found", lang))
        return
    await _reply(event, t("lists.genres", lang), reply_markup=get_genres_keyboard(genres, lang))


@router.callback_query(F.data.regexp(r"^genre:\d+$"))
async def cb_genre(callback: CallbackQuery) -> None:
    genre_id = int(callback.data.split(":", 1)[1])
    async with async_session() as session:
        lang = await get_user_language(session, callback.from_user.id)
        await increment_request_count(session, callback.from_user.id)
    try:
        data = await tmdb.get_by_genre(genre_id, lang)
    except tmdb.TMDBError:
        await callback.answer(t_plain("error.generic", lang), show_alert=True)
        return
    items = data.get("results") or []
    for x in items:
        x.setdefault("media_type", "movie")
    items = items[:10]
    if not items:
        await callback.answer(t_plain("error.not_found", lang), show_alert=True)
        return
    await callback.message.answer(
        t("lists.genres", lang),
        reply_markup=get_results_keyboard(items, lang),
        parse_mode="HTML",
    )
    await callback.answer()
