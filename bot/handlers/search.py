"""Поиск фильмов / сериалов / актёров"""
import logging
import time

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.database import async_session
from bot.database.crud import (
    get_user_language,
    increment_request_count,
    log_search,
)
from bot.i18n import t
from bot.keyboards.inline import get_back_keyboard, get_results_keyboard
from bot.services import tmdb

logger = logging.getLogger(__name__)
router = Router()

# последний поиск пользователя (для пагинации) — {user_id: (query, ts)}
_last_query: dict[int, tuple[str, float]] = {}
_LAST_QUERY_TTL = 30 * 60  # 30 минут


def cleanup_last_queries() -> int:
    """Удаляет протухшие (>30 мин) записи из _last_query. Возвращает кол-во удалённых."""
    now = time.time()
    stale = [uid for uid, (_, ts) in _last_query.items() if now - ts > _LAST_QUERY_TTL]
    for uid in stale:
        _last_query.pop(uid, None)
    return len(stale)


@router.message(Command("search"))
async def cmd_search(message: Message) -> None:
    """/search [запрос]"""
    parts = message.text.split(maxsplit=1)
    async with async_session() as session:
        lang = await get_user_language(session, message.from_user.id)
    if len(parts) < 2:
        await message.answer(t("search.prompt", lang), parse_mode="HTML")
        return
    await _do_search(message, parts[1], lang)


@router.callback_query(F.data == "search_movie")
async def prompt_search(callback: CallbackQuery) -> None:
    async with async_session() as session:
        lang = await get_user_language(session, callback.from_user.id)
    await callback.message.answer(
        t("search.prompt", lang),
        reply_markup=get_back_keyboard(lang),
        parse_mode="HTML",
    )
    await callback.answer()


async def _do_search_and_reply(send_to, user_id: int, query: str, lang: str, page: int = 1) -> None:
    """send_to — объект с .answer(text, reply_markup, parse_mode), либо bot для send_message."""
    query = query.strip()
    if not query:
        await send_to.answer(t("search.prompt", lang), parse_mode="HTML")
        return
    try:
        result = await tmdb.search_multi(query, lang, page=page)
    except tmdb.TMDBQuotaError:
        await send_to.answer(t("error.tmdb_unavailable", lang), parse_mode="HTML")
        return
    except tmdb.TMDBError as exc:
        logger.warning("TMDB search error: %s", exc)
        await send_to.answer(t("error.generic", lang), parse_mode="HTML")
        return

    items = result.get("results") or []
    items = [
        x for x in items
        if x.get("media_type") in ("movie", "tv", "person")
    ][:10]
    total_pages = min(result.get("total_pages") or 1, 50)

    if page == 1:
        async with async_session() as session:
            await log_search(session, user_id, query, len(items))
            await increment_request_count(session, user_id)

    if not items:
        await send_to.answer(
            t("search.no_results", lang, query=query),
            reply_markup=get_back_keyboard(lang),
            parse_mode="HTML",
        )
        return

    _last_query[user_id] = (query, time.time())

    await send_to.answer(
        t("search.results", lang, query=query, count=len(items)),
        reply_markup=get_results_keyboard(
            items, lang, page=page, total_pages=total_pages,
        ),
        parse_mode="HTML",
    )


async def _do_search(message: Message, query: str, lang: str, page: int = 1) -> None:
    await _do_search_and_reply(message, message.from_user.id, query, lang, page)


@router.callback_query(F.data.regexp(r"^searchpg:\d+$"))
async def search_page(callback: CallbackQuery) -> None:
    """Пагинация: searchpg:N → страница N последнего запроса юзера."""
    page = int(callback.data.split(":", 1)[1])
    user_id = callback.from_user.id
    async with async_session() as session:
        lang = await get_user_language(session, user_id)
    entry = _last_query.get(user_id)
    if not entry or (time.time() - entry[1]) > _LAST_QUERY_TTL:
        await callback.answer(t("search.expired", lang), show_alert=True)
        return
    query = entry[0]
    await _do_search_and_reply(callback.message, user_id, query, lang, page=page)
    await callback.answer()


# Любой текст не-команда → поиск (роутер регистрируется ПОСЛЕДНИМ в main.py)
@router.message(F.text & ~F.text.startswith("/"))
async def text_search(message: Message, state: FSMContext) -> None:
    # пропускаем если есть активное FSM-состояние (например админ-флоу)
    current = await state.get_state()
    if current is not None:
        return
    if not message.text:
        return
    # игнорируем слишком короткие свободные сообщения — чтобы не ловить случайный текст
    if len(message.text.strip()) < 3:
        return
    async with async_session() as session:
        lang = await get_user_language(session, message.from_user.id)
    await _do_search(message, message.text, lang)
