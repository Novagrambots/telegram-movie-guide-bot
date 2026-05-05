"""Конфигурация бота — все настройки из .env"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # токен бота
    bot_token: str

    # PostgreSQL
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "bot_4_movies"
    db_user: str = "bot_4_movies"
    db_password: str = ""

    # юзернейм бота (для инлайн-режима и справки)
    bot_username: str = ""

    # админы бота (через запятую в .env)
    admin_ids: str = ""
    admin_username: str = "admin"

    # TMDB API
    tmdb_api_key: str = ""
    tmdb_bearer_token: str = ""

    # кэш TMDB (дни) — не дёргаем API повторно для одного и того же запроса
    cache_ttl_days: int = 7

    @property
    def admin_id_list(self) -> list[int]:
        """Парсит admin_ids из строки в список int"""
        if not self.admin_ids:
            return []
        return [int(x.strip()) for x in self.admin_ids.split(",") if x.strip()]

    @property
    def db_url(self) -> str:
        """URL для подключения к PostgreSQL через asyncpg"""
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# глобальный экземпляр настроек
settings = Settings()
