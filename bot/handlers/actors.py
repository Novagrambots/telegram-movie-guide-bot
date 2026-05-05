"""Поиск актёров и режиссёров"""
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.database import async_session
from bot.database.crud import get_user_language, increment_request_count
from bot.i18n import t
from bot.keyboards.inline import get_back_keyboard, get_results_keyboard
from bot.services import tmdb

logger = logging.getLogger(__name__)
router = Router()


async def _person_lookup(message: Message, role: str) -> None:
    parts = message.text.split(maxsplit=1)
    async with async_session() as session:
        lang = await get_user_language(session, message.from_user.id)
    if len(parts) < 2:
        key = "actor.usage" if role == "actor" else "director.usage"
        await message.answer(t(key, lang), parse_mode="HTML")
        return
    query = parts[1].strip()

    try:
        search = await tmdb.search_person(query, lang)
    except tmdb.TMDBError:
        await message.answer(t("error.generic", lang), parse_mode="HTML")
        return
    persons = search.get("results") or []
    if not persons:
        await message.answer(
            t("actor.not_found", lang),
            reply_markup=get_back_keyboard(lang),
            parse_mode="HTML",
        )
        return

    person = persons[0]
    person_id = person["id"]

    try:
        credits = await tmdb.get_person_credits(person_id, lang)
    except tmdb.TMDBError:
        await message.answer(t("error.generic", lang), parse_mode="HTML")
        return

    if role == "director":
        crew = credits.get("crew") or []
        items = [c for c in crew if c.get("job") == "Director"]
    else:
        items = credits.get("cast") or []

    # сортируем по популярности и берем топ-10
    items.sort(key=lambda x: x.get("popularity") or 0, reverse=True)
    items = items[:10]
    for x in items:
        x.setdefault("media_type", x.get("media_type") or "movie")

    async with async_session() as session:
        await increment_request_count(session, message.from_user.id)

    if not items:
        await message.answer(
            t("actor.not_found", lang),
            reply_markup=get_back_keyboard(lang),
            parse_mode="HTML",
        )
        return

    text = t("actor.title", lang, name=person.get("name", "?"))
    await message.answer(
        text,
        reply_markup=get_results_keyboard(items, lang),
        parse_mode="HTML",
    )


@router.message(Command("actor"))
async def cmd_actor(message: Message) -> None:
    await _person_lookup(message, role="actor")


@router.message(Command("director"))
async def cmd_director(message: Message) -> None:
    await _person_lookup(message, role="director")
