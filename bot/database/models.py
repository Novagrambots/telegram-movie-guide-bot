"""Модели базы данных — User, Channel + доменные модели киногида"""
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class User(Base):
    """Пользователь бота"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    download_count: Mapped[int] = mapped_column(default=0)
    language: Mapped[str] = mapped_column(String(5), default="ru")

    def __repr__(self) -> str:
        return f"<User {self.telegram_id} ({self.username})>"


class Channel(Base):
    """Канал/группа для обязательной подписки"""
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    title: Mapped[str] = mapped_column(String(255))
    invite_link: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Channel {self.channel_id} ({self.title})>"


class MovieCache(Base):
    """Кэш данных фильма/сериала из TMDB"""
    __tablename__ = "movie_cache"
    __table_args__ = (
        UniqueConstraint(
            "tmdb_id", "media_type", "language",
            name="uq_movie_cache_tmdb_type_lang",
        ),
        Index("ix_movie_cache_tmdb", "tmdb_id", "media_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tmdb_id: Mapped[int] = mapped_column(BigInteger, index=True)
    media_type: Mapped[str] = mapped_column(String(10))  # movie | tv
    language: Mapped[str] = mapped_column(String(5), default="ru")
    title_ru: Mapped[str | None] = mapped_column(String(500), nullable=True)
    title_orig: Mapped[str | None] = mapped_column(String(500), nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    poster_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    poster_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    data: Mapped[dict] = mapped_column(JSONB)
    cached_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<MovieCache {self.media_type}:{self.tmdb_id}>"


class Favorite(Base):
    """Избранные фильмы/сериалы"""
    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "tmdb_id", "media_type", name="uq_fav_user_tmdb_type"
        ),
        Index("ix_fav_user", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id"), index=True
    )
    tmdb_id: Mapped[int] = mapped_column(BigInteger)
    media_type: Mapped[str] = mapped_column(String(10))
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Watched(Base):
    """Просмотренные фильмы/сериалы"""
    __tablename__ = "watched"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "tmdb_id", "media_type", name="uq_watched_user_tmdb_type"
        ),
        CheckConstraint(
            "user_rating IS NULL OR (user_rating BETWEEN 1 AND 10)",
            name="ck_watched_rating_range",
        ),
        Index("ix_watched_user", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id"), index=True
    )
    tmdb_id: Mapped[int] = mapped_column(BigInteger)
    media_type: Mapped[str] = mapped_column(String(10))
    user_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    watched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class SearchRequest(Base):
    """Лог поисковых запросов"""
    __tablename__ = "search_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id"), index=True
    )
    query: Mapped[str] = mapped_column(String(500))
    results_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
