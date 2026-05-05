# Telegram-бот-киногид

Мультиязычный (ru/uz/en) бот для поиска фильмов, сериалов и актёров через TMDB API. Карточки с постером, рейтингом, трейлерами, актёрами, "где посмотреть", избранное, инлайн-режим, авто-перевод описаний на узбекский.

## Стек

- Python 3.12, aiogram 3
- SQLAlchemy 2 (async) + asyncpg + PostgreSQL 16
- httpx (TMDB API), deep-translator (Google Translate)
- Docker + docker-compose

## Быстрый старт

```bash
cp .env.example .env
# заполнить: BOT_TOKEN, BOT_USERNAME, TMDB_API_KEY, DB_PASSWORD, ADMIN_IDS

docker compose up --build -d
```

TMDB-ключ: https://www.themoviedb.org/settings/api (бесплатно).

## Команды

`/start` `/help` `/search <название>` `/trending` `/top` `/now_playing` `/upcoming` `/random` `/genres` `/favorites` `/watched` `/actor <имя>` `/director <имя>` `/lang` `/profile`

Админ: `/admin` `/stats` `/broadcast`

Инлайн: `@bot_username inception` — быстрый поиск из любого чата.

## Структура

```
bot/
├── main.py              # точка входа
├── config.py            # настройки
├── i18n.py              # переводы ru/uz/en
├── emojis.py            # custom emoji ID
├── database/            # модели + CRUD
├── handlers/            # start, admin, search, lists, movies, favorites, actors, inline_mode
├── middlewares/         # subscription, rate_limit
├── keyboards/           # inline + admin клавиатуры
├── services/            # tmdb клиент, переводчик
└── utils/               # меню команд
```

## Переменные окружения

| Переменная | Описание |
|-----------|----------|
| `BOT_TOKEN` | Токен от @BotFather |
| `BOT_USERNAME` | Юзернейм бота (без @) |
| `TMDB_API_KEY` | Ключ TMDB API v3 |
| `TMDB_BEARER_TOKEN` | Альтернативно — TMDB v4 token |
| `DB_PASSWORD` | Пароль к PostgreSQL |
| `ADMIN_IDS` | Telegram ID админов через запятую |
| `CACHE_TTL_DAYS` | TTL кэша TMDB в днях (по умолчанию 7) |

## Фоновые задачи

- Каждые 5 мин — очистка RAM-кэшей (rate limit, история поиска)
- Каждые 6 часов — прогрев чартов (trending/top/now_playing на ru/uz/en)
- Раз в сутки — очистка БД (`movie_cache > 30 дней`, `search_requests > 90 дней`)
