# bot_4_movies — Telegram-бот-киногид

Бот для поиска информации о фильмах и сериалах через TMDB API.

## Стек

- Python 3.12
- aiogram 3.26
- SQLAlchemy 2 + asyncpg + PostgreSQL 16
- aiohttp (запросы к TMDB API)
- Docker + docker-compose

## Быстрый старт

```bash
cp .env.example .env
# заполнить .env: BOT_TOKEN, TMDB_API_KEY, DB_PASSWORD, ADMIN_IDS

docker compose up --build -d
```

## Структура

```
bot/
├── main.py              # точка входа
├── config.py            # настройки из .env
├── i18n.py              # переводы ru/uz/en
├── emojis.py            # кастомные эмодзи
├── database/            # модели и CRUD
├── handlers/            # хэндлеры команд
│   ├── start.py         # /start, профиль, язык
│   ├── admin.py         # /admin
│   └── __todo_domain.py # TODO: поиск, карточки, избранное
├── middlewares/         # subscription, rate_limit
├── keyboards/           # inline-клавиатуры
├── services/
│   └── __todo_domain.py # TODO: TMDB API клиент
└── utils/
    └── commands.py      # меню команд Telegram
```

## Переменные окружения

| Переменная | Описание |
|-----------|----------|
| `BOT_TOKEN` | Токен от @BotFather |
| `TMDB_API_KEY` | Ключ TMDB API (my.telegram.org) |
| `TMDB_LANGUAGE` | Язык ответов (ru-RU) |
| `DB_NAME` | bot_4_movies |
| `ADMIN_IDS` | Telegram ID через запятую |
| `CACHE_TTL_DAYS` | Кэш TMDB в днях (7) |
