"""Точка входа — запуск бота-киногида"""
import asyncio
import logging
import os
import sys

# uvloop ускоряет asyncio в 2-4 раза (не работает на Windows!)
try:
    import uvloop
    uvloop.install()
except ImportError:
    pass  # на Windows — работаем без uvloop

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import settings

# настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# флаг-файл для crash recovery
CRASH_FLAG = ".crash_flag"


async def main() -> None:
    """Инициализация и запуск бота"""
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # подключаем хэндлеры (порядок важен: start → admin → команды → search последним)
    from bot.handlers import (
        actors,
        admin,
        favorites,
        inline_mode,
        lists,
        movies,
        search,
        start,
    )
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(lists.router)
    dp.include_router(favorites.router)
    dp.include_router(movies.router)
    dp.include_router(actors.router)
    dp.include_router(inline_mode.router)
    # search должен быть ПОСЛЕДНИМ — его текстовый хэндлер ловит всё подряд
    dp.include_router(search.router)

    # подключаем мидлвари
    from bot.middlewares.rate_limit import RateLimitMiddleware
    from bot.middlewares.subscription import SubscriptionMiddleware

    dp.message.middleware(RateLimitMiddleware())
    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())

    # фоновая очистка
    async def _background_cleanup() -> None:
        """Фоновая задача: очистка памяти каждые 5 минут"""
        from bot.middlewares.rate_limit import cleanup_stale_entries
        from bot.handlers.search import cleanup_last_queries
        while True:
            await asyncio.sleep(300)  # 5 минут
            removed_rl = cleanup_stale_entries()
            removed_q = cleanup_last_queries()
            if removed_rl or removed_q:
                logger.info(
                    "Фоновая очистка: rate limit -%d, last_query -%d",
                    removed_rl, removed_q,
                )

    # фоновое обновление популярных чартов раз в 6 часов (прогрев кэша TMDB)
    async def _refresh_charts() -> None:
        """Раз в 6 часов прогреваем кэш топ-фильмов на ru/uz/en, чтобы юзеры получали быстро."""
        from bot.services import tmdb
        # первый прогон через 1 минуту после старта
        await asyncio.sleep(60)
        while True:
            try:
                for lang_ in ("ru", "uz", "en"):
                    for fetch in (tmdb.get_trending, tmdb.get_top_rated, tmdb.get_now_playing):
                        try:
                            data = await fetch(lang_)
                            results = (data.get("results") or [])[:5]
                            # прогреваем карточки топ-5 фильмов (с переводом для uz)
                            for item in results:
                                tmdb_id = item.get("id")
                                mt = item.get("media_type") or "movie"
                                if not tmdb_id or mt not in ("movie", "tv"):
                                    continue
                                try:
                                    if mt == "movie":
                                        await tmdb.get_movie(tmdb_id, lang_)
                                    else:
                                        await tmdb.get_tv(tmdb_id, lang_)
                                except Exception:
                                    pass
                        except Exception as e:
                            logger.warning("Прогрев чартов (%s): %s", lang_, e)
                logger.info("Прогрев чартов завершён")
            except Exception as e:
                logger.error("Ошибка прогрева чартов: %s", e)
            await asyncio.sleep(6 * 3600)  # 6 часов

    # ежедневная очистка БД от старых записей
    async def _daily_db_cleanup() -> None:
        """Удаляем устаревший кэш TMDB и старые логи поиска раз в сутки."""
        from bot.database import async_session
        from bot.database.crud import cleanup_old_cache, cleanup_old_searches
        while True:
            await asyncio.sleep(24 * 3600)  # 24 часа
            try:
                async with async_session() as session:
                    cache_removed = await cleanup_old_cache(session, days=30)
                    search_removed = await cleanup_old_searches(session, days=90)
                logger.info(
                    "Очистка БД: удалено %d записей movie_cache, %d записей search_requests",
                    cache_removed, search_removed,
                )
            except Exception as e:
                logger.error("Ошибка ежедневной очистки БД: %s", e)

    @dp.startup()
    async def on_startup() -> None:
        # создаём таблицы в БД
        from bot.database import engine
        from bot.database.models import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Таблицы БД созданы")

        # проверяем crash recovery
        if os.path.exists(CRASH_FLAG):
            logger.warning("Обнаружен crash-flag — предыдущий запуск завершился аварийно")
            os.remove(CRASH_FLAG)

        # ставим crash-flag (уберём при нормальном завершении)
        with open(CRASH_FLAG, "w") as f:
            f.write("running")

        # запускаем фоновую очистку
        asyncio.create_task(_background_cleanup())
        asyncio.create_task(_daily_db_cleanup())
        asyncio.create_task(_refresh_charts())
        logger.info("Фоновые задачи запущены (rate limit 5 мин, БД 24 ч)")

        bot_info = await bot.get_me()
        logger.info(f"Бот @{bot_info.username} запущен!")

        # ставим дефолтное меню команд (глобально, ru — для новых юзеров)
        from bot.utils.commands import set_default_commands
        await set_default_commands(bot)
        logger.info("Дефолтное меню команд установлено")

    @dp.shutdown()
    async def on_shutdown() -> None:
        # убираем crash-flag при нормальном завершении
        if os.path.exists(CRASH_FLAG):
            os.remove(CRASH_FLAG)
        # закрываем глобальный httpx-клиент TMDB
        from bot.services.tmdb import close_client
        await close_client()
        logger.info("Бот остановлен")

    # запускаем polling
    try:
        logger.info("Запуск polling...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
