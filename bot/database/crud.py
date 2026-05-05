"""CRUD операции с базой данных"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import (
    Channel,
    Favorite,
    MovieCache,
    SearchRequest,
    User,
    Watched,
)


# === USER ===

async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
    full_name: str,
    language: str | None = None,
) -> User:
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
            language=language or "ru",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


async def get_user_language(session: AsyncSession, telegram_id: int) -> str:
    result = await session.execute(
        select(User.language).where(User.telegram_id == telegram_id)
    )
    lang = result.scalar_one_or_none()
    return lang or "ru"


async def update_user_language(
    session: AsyncSession, telegram_id: int, language: str
) -> None:
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if user:
        user.language = language
        await session.commit()


async def increment_request_count(session: AsyncSession, telegram_id: int) -> None:
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if user:
        user.download_count += 1
        await session.commit()


# === CHANNELS ===

async def get_active_channels(session: AsyncSession) -> list[Channel]:
    result = await session.execute(select(Channel))
    return list(result.scalars().all())


async def add_channel(
    session: AsyncSession,
    channel_id: int,
    title: str,
    invite_link: str,
) -> Channel:
    result = await session.execute(
        select(Channel).where(Channel.channel_id == channel_id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise ValueError(f"Канал {channel_id} уже добавлен")

    channel = Channel(
        channel_id=channel_id,
        title=title,
        invite_link=invite_link,
    )
    session.add(channel)
    await session.commit()
    await session.refresh(channel)
    return channel


async def remove_channel(session: AsyncSession, channel_id: int) -> bool:
    result = await session.execute(
        select(Channel).where(Channel.channel_id == channel_id)
    )
    channel = result.scalar_one_or_none()
    if not channel:
        return False
    await session.delete(channel)
    await session.commit()
    return True


# === STATS ===

async def get_user_stats(session: AsyncSession) -> dict:
    from sqlalchemy import func as sa_func

    total = await session.execute(select(sa_func.count(User.id)))
    total_users = total.scalar() or 0

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_result = await session.execute(
        select(sa_func.count(User.id)).where(User.created_at >= today)
    )
    today_users = today_result.scalar() or 0

    requests = await session.execute(
        select(sa_func.sum(User.download_count))
    )
    total_downloads = requests.scalar() or 0

    channels = await session.execute(select(sa_func.count(Channel.id)))
    total_channels = channels.scalar() or 0

    return {
        "total_users": total_users,
        "today_users": today_users,
        "total_downloads": total_downloads,
        "total_channels": total_channels,
    }


async def get_all_user_ids(session: AsyncSession) -> list[int]:
    result = await session.execute(select(User.telegram_id))
    return [row[0] for row in result.all()]


# === MOVIE CACHE ===

async def get_cached_movie(
    session: AsyncSession,
    tmdb_id: int,
    media_type: str,
    lang: str = "ru",
    ttl_days: int = 7,
) -> MovieCache | None:
    """Получить кэш фильма если не протух (по tmdb_id+media_type+language)"""
    result = await session.execute(
        select(MovieCache).where(
            MovieCache.tmdb_id == tmdb_id,
            MovieCache.media_type == media_type,
            MovieCache.language == lang,
        )
    )
    item = result.scalar_one_or_none()
    if item is None:
        return None
    if ttl_days <= 0 or ttl_days > 36500:
        return item
    cutoff = datetime.now(timezone.utc) - timedelta(days=ttl_days)
    cached_at = item.cached_at
    if cached_at.tzinfo is None:
        cached_at = cached_at.replace(tzinfo=timezone.utc)
    if cached_at < cutoff:
        return None
    return item


async def save_movie_cache(
    session: AsyncSession,
    tmdb_id: int,
    media_type: str,
    data: dict,
    lang: str = "ru",
    title_ru: str | None = None,
    title_orig: str | None = None,
    year: int | None = None,
    poster_url: str | None = None,
) -> MovieCache:
    """Сохранить/обновить кэш (отдельная запись на каждый язык)"""
    stmt = pg_insert(MovieCache).values(
        tmdb_id=tmdb_id,
        media_type=media_type,
        language=lang,
        title_ru=title_ru,
        title_orig=title_orig,
        year=year,
        poster_url=poster_url,
        data=data,
        cached_at=datetime.now(timezone.utc),
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["tmdb_id", "media_type", "language"],
        set_={
            "title_ru": stmt.excluded.title_ru,
            "title_orig": stmt.excluded.title_orig,
            "year": stmt.excluded.year,
            "poster_url": stmt.excluded.poster_url,
            "data": stmt.excluded.data,
            "cached_at": stmt.excluded.cached_at,
        },
    )
    await session.execute(stmt)
    await session.commit()
    result = await session.execute(
        select(MovieCache).where(
            MovieCache.tmdb_id == tmdb_id,
            MovieCache.media_type == media_type,
            MovieCache.language == lang,
        )
    )
    return result.scalar_one()


async def save_poster_file_id(
    session: AsyncSession,
    tmdb_id: int,
    media_type: str,
    file_id: str,
) -> None:
    """Сохраняет file_id постера во все языковые записи фильма (постер общий)"""
    result = await session.execute(
        select(MovieCache).where(
            MovieCache.tmdb_id == tmdb_id,
            MovieCache.media_type == media_type,
        )
    )
    items = list(result.scalars().all())
    if items:
        for item in items:
            item.poster_file_id = file_id
        await session.commit()


# === FAVORITES ===

async def add_favorite(
    session: AsyncSession,
    user_id: int,
    tmdb_id: int,
    media_type: str,
) -> bool:
    """Добавить в избранное через UPSERT. True — добавлено, False — уже было.

    Использует INSERT ... ON CONFLICT DO NOTHING чтобы избежать race condition
    между двумя одновременными нажатиями пользователя.
    """
    stmt = pg_insert(Favorite).values(
        user_id=user_id, tmdb_id=tmdb_id, media_type=media_type,
    ).on_conflict_do_nothing(
        index_elements=["user_id", "tmdb_id", "media_type"],
    )
    res = await session.execute(stmt)
    await session.commit()
    return res.rowcount > 0


async def remove_favorite(
    session: AsyncSession,
    user_id: int,
    tmdb_id: int,
    media_type: str,
) -> bool:
    res = await session.execute(
        delete(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.tmdb_id == tmdb_id,
            Favorite.media_type == media_type,
        )
    )
    await session.commit()
    return res.rowcount > 0


async def is_favorite(
    session: AsyncSession,
    user_id: int,
    tmdb_id: int,
    media_type: str,
) -> bool:
    result = await session.execute(
        select(Favorite.id).where(
            Favorite.user_id == user_id,
            Favorite.tmdb_id == tmdb_id,
            Favorite.media_type == media_type,
        )
    )
    return result.scalar_one_or_none() is not None


async def get_user_favorites(
    session: AsyncSession,
    user_id: int,
    limit: int = 50,
) -> list[Favorite]:
    result = await session.execute(
        select(Favorite)
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.added_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


# === WATCHED ===

async def add_watched(
    session: AsyncSession,
    user_id: int,
    tmdb_id: int,
    media_type: str,
) -> bool:
    """Добавить в просмотренное через UPSERT. True — добавлено, False — уже было."""
    stmt = pg_insert(Watched).values(
        user_id=user_id, tmdb_id=tmdb_id, media_type=media_type,
    ).on_conflict_do_nothing(
        index_elements=["user_id", "tmdb_id", "media_type"],
    )
    res = await session.execute(stmt)
    await session.commit()
    return res.rowcount > 0


async def remove_watched(
    session: AsyncSession,
    user_id: int,
    tmdb_id: int,
    media_type: str,
) -> bool:
    res = await session.execute(
        delete(Watched).where(
            Watched.user_id == user_id,
            Watched.tmdb_id == tmdb_id,
            Watched.media_type == media_type,
        )
    )
    await session.commit()
    return res.rowcount > 0


async def is_watched(
    session: AsyncSession,
    user_id: int,
    tmdb_id: int,
    media_type: str,
) -> bool:
    result = await session.execute(
        select(Watched.id).where(
            Watched.user_id == user_id,
            Watched.tmdb_id == tmdb_id,
            Watched.media_type == media_type,
        )
    )
    return result.scalar_one_or_none() is not None


async def set_user_rating(
    session: AsyncSession,
    user_id: int,
    tmdb_id: int,
    media_type: str,
    rating: int,
) -> bool:
    if not 1 <= rating <= 10:
        return False
    result = await session.execute(
        select(Watched).where(
            Watched.user_id == user_id,
            Watched.tmdb_id == tmdb_id,
            Watched.media_type == media_type,
        )
    )
    w = result.scalar_one_or_none()
    if not w:
        w = Watched(
            user_id=user_id,
            tmdb_id=tmdb_id,
            media_type=media_type,
            user_rating=rating,
        )
        session.add(w)
    else:
        w.user_rating = rating
    await session.commit()
    return True


async def get_user_watched(
    session: AsyncSession,
    user_id: int,
    limit: int = 50,
) -> list[Watched]:
    result = await session.execute(
        select(Watched)
        .where(Watched.user_id == user_id)
        .order_by(Watched.watched_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


# === SEARCH LOG ===

async def log_search(
    session: AsyncSession,
    user_id: int,
    query: str,
    results_count: int,
) -> SearchRequest:
    sr = SearchRequest(
        user_id=user_id,
        query=query[:500],
        results_count=results_count,
    )
    session.add(sr)
    await session.commit()
    return sr


# === ОЧИСТКА ===

async def cleanup_old_cache(session: AsyncSession, days: int = 30) -> int:
    """Удаляет записи MovieCache старше N дней. Возвращает количество удалённых."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result = await session.execute(
        delete(MovieCache).where(MovieCache.cached_at < cutoff)
    )
    await session.commit()
    return result.rowcount or 0


async def cleanup_old_searches(session: AsyncSession, days: int = 90) -> int:
    """Удаляет записи SearchRequest старше N дней. Возвращает количество удалённых."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result = await session.execute(
        delete(SearchRequest).where(SearchRequest.created_at < cutoff)
    )
    await session.commit()
    return result.rowcount or 0
