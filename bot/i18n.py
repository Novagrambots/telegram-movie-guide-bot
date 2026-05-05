"""Мультиязычность — русский, узбекский, английский
Использование: from bot.i18n import t
  t("start.welcome", lang="en", name="John")
"""

from bot.emojis import E

TRANSLATIONS = {
    # === /start ===
    "start.welcome": {
        "ru": (
            f"{E['bot']} <b>Привет, {{name}}!</b>\n\n"
            f"{E['video']} Я твой персональный киногид.\n\n"
            f"{E['pin']} <b>Что я умею:</b>\n"
            "Ищу фильмы, сериалы и актёров в базе TMDB — "
            f"быстро и удобно! {E['star']}\n\n"
            "Выбери действие ниже:"
        ),
        "uz": (
            f"{E['bot']} <b>Salom, {{name}}!</b>\n\n"
            f"{E['video']} Men sening shaxsiy kino gidingman.\n\n"
            f"{E['pin']} <b>Nima qila olaman:</b>\n"
            "TMDB bazasida filmlar, seriallar va aktyorlarni qidiraman — "
            f"tez va qulay! {E['star']}\n\n"
            "Quyidagi tugmani tanlang:"
        ),
        "en": (
            f"{E['bot']} <b>Hello, {{name}}!</b>\n\n"
            f"{E['video']} I'm your personal movie guide.\n\n"
            f"{E['pin']} <b>What I can do:</b>\n"
            "Search movies, TV shows and actors in TMDB — "
            f"fast and easy! {E['star']}\n\n"
            "Choose an action below:"
        ),
    },

    # === Кнопки главного меню ===
    "btn.search": {
        "ru": "Поиск фильма",
        "uz": "Film qidirish",
        "en": "Search movie",
    },
    "btn.profile": {
        "ru": "Мой профиль",
        "uz": "Mening profilim",
        "en": "My profile",
    },
    "btn.help": {
        "ru": "Помощь",
        "uz": "Yordam",
        "en": "Help",
    },
    "btn.back": {
        "ru": "Назад",
        "uz": "Orqaga",
        "en": "Back",
    },
    "btn.language": {
        "ru": "Сменить язык",
        "uz": "Tilni o'zgartirish",
        "en": "Change language",
    },
    "btn.trending": {
        "ru": "🔥 В тренде",
        "uz": "🔥 Trendda",
        "en": "🔥 Trending",
    },
    "btn.top": {
        "ru": "🏆 Топ рейтинга",
        "uz": "🏆 Top reyting",
        "en": "🏆 Top rated",
    },
    "btn.now_playing": {
        "ru": "🎬 В прокате",
        "uz": "🎬 Hozir kinoda",
        "en": "🎬 Now playing",
    },
    "btn.upcoming": {
        "ru": "📅 Скоро",
        "uz": "📅 Tez kunda",
        "en": "📅 Upcoming",
    },
    "btn.random": {
        "ru": "🎲 Случайный",
        "uz": "🎲 Tasodifiy",
        "en": "🎲 Random",
    },
    "btn.genres": {
        "ru": "🎭 Жанры",
        "uz": "🎭 Janrlar",
        "en": "🎭 Genres",
    },
    "btn.favorites": {
        "ru": "Избранное",
        "uz": "Sevimlilar",
        "en": "Favorites",
    },
    "btn.watched": {
        "ru": "Просмотренное",
        "uz": "Ko'rilgan",
        "en": "Watched",
    },

    # === Профиль ===
    "profile.title": {
        "ru": (
            f"{E['profile']} <b>Твой профиль</b>\n\n"
            f"{E['edit']} Имя: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['search']} Запросов (всего): {{download_count}}\n"
        ),
        "uz": (
            f"{E['profile']} <b>Sizning profilingiz</b>\n\n"
            f"{E['edit']} Ism: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['search']} So'rovlar (jami): {{download_count}}\n"
        ),
        "en": (
            f"{E['profile']} <b>Your profile</b>\n\n"
            f"{E['edit']} Name: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['search']} Requests (total): {{download_count}}\n"
        ),
    },

    # === Помощь ===
    "help.text": {
        "ru": (
            f"{E['book']} <b>Помощь</b>\n\n"
            f"{E['star']} Отправь название фильма или сериала — найду информацию\n"
            f"{E['star']} Поддерживается поиск на русском и английском\n"
            f"{E['star']} Можно искать по актёрам и режиссёрам\n"
            f"{E['bulb']} Используй инлайн-режим: @{{bot_username}} <i>название</i>\n\n"
            f"{E['plane']} По вопросам: @{{admin_username}}"
        ),
        "uz": (
            f"{E['book']} <b>Yordam</b>\n\n"
            f"{E['star']} Film yoki serial nomini yuboring — ma'lumot topaman\n"
            f"{E['star']} Rus va ingliz tillarida qidirish qo'llab-quvvatlanadi\n"
            f"{E['star']} Aktyorlar va rejissyorlar bo'yicha qidirish mumkin\n"
            f"{E['bulb']} Inline rejimdan foydalaning: @{{bot_username}} <i>nomi</i>\n\n"
            f"{E['plane']} Savollar uchun: @{{admin_username}}"
        ),
        "en": (
            f"{E['book']} <b>Help</b>\n\n"
            f"{E['star']} Send a movie or TV show title — I'll find info\n"
            f"{E['star']} Search in Russian and English is supported\n"
            f"{E['star']} You can search by actors and directors\n"
            f"{E['bulb']} Use inline mode: @{{bot_username}} <i>title</i>\n\n"
            f"{E['plane']} Contact: @{{admin_username}}"
        ),
    },

    # === Подписка ===
    "sub.welcome": {
        "ru": (
            f"{E['bot']} <b>Привет!</b>\n\n"
            f"{E['video']} Этот бот — твой киногид: находит информацию о фильмах, "
            "сериалах и актёрах из базы TMDB!\n\n"
            f"{E['lock']} <b>Для начала подпишись на каналы ниже:</b>\n\n"
            f"После подписки нажми «{E['check']} Проверить подписку»"
        ),
        "uz": (
            f"{E['bot']} <b>Salom!</b>\n\n"
            f"{E['video']} Bu bot — sizning kino gidingiz: TMDB bazasidan filmlar, "
            "seriallar va aktyorlar haqida ma'lumot topadi!\n\n"
            f"{E['lock']} <b>Boshlash uchun quyidagi kanallarga obuna bo'ling:</b>\n\n"
            f"Obuna bo'lgandan keyin «{E['check']} Obunani tekshirish» tugmasini bosing"
        ),
        "en": (
            f"{E['bot']} <b>Hello!</b>\n\n"
            f"{E['video']} This bot is your movie guide: finds info about movies, "
            "TV shows and actors from TMDB!\n\n"
            f"{E['lock']} <b>To start, subscribe to the channels below:</b>\n\n"
            f"After subscribing, tap «{E['check']} Check subscription»"
        ),
    },
    "sub.not_subscribed": {
        "ru": (
            f"{E['cross']} <b>Ты ещё не подписался на все каналы:</b>\n\n"
            f"Подпишись и нажми «{E['check']} Проверить подписку» ещё раз."
        ),
        "uz": (
            f"{E['cross']} <b>Siz hali barcha kanallarga obuna bo'lmadingiz:</b>\n\n"
            f"Obuna bo'ling va «{E['check']} Obunani tekshirish» tugmasini qayta bosing."
        ),
        "en": (
            f"{E['cross']} <b>You haven't subscribed to all channels yet:</b>\n\n"
            f"Subscribe and tap «{E['check']} Check subscription» again."
        ),
    },
    "sub.success": {
        "ru": (
            f"{E['check']} <b>Отлично, {{name}}!</b>\n\n"
            f"Теперь ты можешь пользоваться ботом! {E['star']}\n\n"
            "Отправь название фильма или сериала."
        ),
        "uz": (
            f"{E['check']} <b>Ajoyib, {{name}}!</b>\n\n"
            f"Endi siz botdan foydalanishingiz mumkin! {E['star']}\n\n"
            "Film yoki serial nomini yuboring."
        ),
        "en": (
            f"{E['check']} <b>Great, {{name}}!</b>\n\n"
            f"You can now use the bot! {E['star']}\n\n"
            "Send a movie or TV show title."
        ),
    },
    "btn.check_sub": {
        "ru": "Проверить подписку",
        "uz": "Obunani tekshirish",
        "en": "Check subscription",
    },
    "sub.check_alert_fail": {
        "ru": f"{E['cross']} Подпишись на все каналы!",
        "uz": f"{E['cross']} Barcha kanallarga obuna bo'ling!",
        "en": f"{E['cross']} Subscribe to all channels!",
    },
    "sub.check_alert_ok": {
        "ru": f"{E['check']} Подписка подтверждена!",
        "uz": f"{E['check']} Obuna tasdiqlandi!",
        "en": f"{E['check']} Subscription confirmed!",
    },
    "sub.not_required": {
        "ru": f"{E['check']} Подписка не требуется!",
        "uz": f"{E['check']} Obuna talab qilinmaydi!",
        "en": f"{E['check']} No subscription required!",
    },

    # === Ошибки ===
    "error.not_found": {
        "ru": f"{E['cross']} <b>Ничего не найдено</b>\n\nПопробуй другой запрос.",
        "uz": f"{E['cross']} <b>Hech narsa topilmadi</b>\n\nBoshqa so'rov bilan urinib ko'ring.",
        "en": f"{E['cross']} <b>Nothing found</b>\n\nTry a different query.",
    },
    "error.timeout": {
        "ru": f"{E['clock']} <b>Превышено время ожидания</b>\n\nПопробуй ещё раз через пару секунд.",
        "uz": f"{E['clock']} <b>Kutish vaqti tugadi</b>\n\nBir necha soniyadan keyin qayta urinib ko'ring.",
        "en": f"{E['clock']} <b>Request timed out</b>\n\nPlease try again in a few seconds.",
    },
    "error.generic": {
        "ru": f"{E['cross']} <b>Произошла ошибка</b>\n\nПопробуй позже.",
        "uz": f"{E['cross']} <b>Xato yuz berdi</b>\n\nKeyinroq urinib ko'ring.",
        "en": f"{E['cross']} <b>An error occurred</b>\n\nTry again later.",
    },
    "error.rate_limit": {
        "ru": f"{E['clock']} <b>Слишком много запросов!</b>\n\nПодожди {{seconds}} секунд и попробуй снова.",
        "uz": f"{E['clock']} <b>Juda ko'p so'rovlar!</b>\n\n{{seconds}} soniya kuting va qayta urinib ko'ring.",
        "en": f"{E['clock']} <b>Too many requests!</b>\n\nWait {{seconds}} seconds and try again.",
    },
    "error.tmdb_unavailable": {
        "ru": f"{E['warning']} <b>TMDB недоступен</b>\n\nСервис временно не работает. Попробуй позже.",
        "uz": f"{E['warning']} <b>TMDB mavjud emas</b>\n\nXizmat vaqtincha ishlamayapti. Keyinroq urinib ko'ring.",
        "en": f"{E['warning']} <b>TMDB unavailable</b>\n\nService is temporarily down. Try again later.",
    },

    # === Выбор языка ===
    "lang.choose": {
        "ru": f"{E['gear']} <b>Выберите язык:</b>",
        "uz": f"{E['gear']} <b>Tilni tanlang:</b>",
        "en": f"{E['gear']} <b>Choose language:</b>",
    },
    "lang.changed": {
        "ru": f"{E['check']} Язык изменён на русский",
        "uz": f"{E['check']} Til o'zbek tiliga o'zgartirildi",
        "en": f"{E['check']} Language changed to English",
    },

    # === Админ-панель ===
    "admin.title": {
        "ru": f"{E['gear']} <b>Админ-панель</b>\n\nВыбери действие:",
        "uz": f"{E['gear']} <b>Admin panel</b>\n\nAmalni tanlang:",
        "en": f"{E['gear']} <b>Admin panel</b>\n\nChoose an action:",
    },
    "admin.no_access": {
        "ru": f"{E['lock']} У тебя нет доступа к админке.",
        "uz": f"{E['lock']} Sizda admin panelga kirish huquqi yo'q.",
        "en": f"{E['lock']} You don't have access to admin panel.",
    },
    "admin.stats": {
        "ru": (
            f"{E['chart']} <b>Статистика бота</b>\n\n"
            f"{E['users']} Всего юзеров: <b>{{total_users}}</b>\n"
            f"{E['star']} Новых юзеров сегодня: <b>{{today_users}}</b>\n"
            f"{E['search']} Всего запросов: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Каналов: <b>{{total_channels}}</b>"
        ),
        "uz": (
            f"{E['chart']} <b>Bot statistikasi</b>\n\n"
            f"{E['users']} Jami foydalanuvchilar: <b>{{total_users}}</b>\n"
            f"{E['star']} Bugungi yangi foydalanuvchilar: <b>{{today_users}}</b>\n"
            f"{E['search']} Jami so'rovlar: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Kanallar: <b>{{total_channels}}</b>"
        ),
        "en": (
            f"{E['chart']} <b>Bot statistics</b>\n\n"
            f"{E['users']} Total users: <b>{{total_users}}</b>\n"
            f"{E['star']} New users today: <b>{{today_users}}</b>\n"
            f"{E['search']} Total requests: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Channels: <b>{{total_channels}}</b>"
        ),
    },
    "admin.channels_empty": {
        "ru": f"{E['megaphone']} <b>Каналы</b>\n\nСписок пуст. Добавь канал кнопкой ниже.",
        "uz": f"{E['megaphone']} <b>Kanallar</b>\n\nRo'yxat bo'sh. Quyidagi tugma orqali kanal qo'shing.",
        "en": f"{E['megaphone']} <b>Channels</b>\n\nList is empty. Add a channel using the button below.",
    },
    "admin.channels_title": {
        "ru": f"{E['megaphone']} <b>Каналы для подписки:</b>\n",
        "uz": f"{E['megaphone']} <b>Obuna kanallari:</b>\n",
        "en": f"{E['megaphone']} <b>Subscription channels:</b>\n",
    },
    "admin.add_channel_id": {
        "ru": (
            f"{E['megaphone']} <b>Добавление канала</b>\n\n"
            "Отправь <b>ID канала</b> (например <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} Узнать ID: добавь бота @getmyid_bot в канал"
        ),
        "uz": (
            f"{E['megaphone']} <b>Kanal qo'shish</b>\n\n"
            "<b>Kanal ID</b> raqamini yuboring (masalan <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} ID bilish: @getmyid_bot ni kanalga qo'shing"
        ),
        "en": (
            f"{E['megaphone']} <b>Add channel</b>\n\n"
            "Send the <b>channel ID</b> (e.g. <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} Get ID: add @getmyid_bot to the channel"
        ),
    },
    "admin.add_channel_title": {
        "ru": f"{E['edit']} Теперь отправь <b>название канала</b>:",
        "uz": f"{E['edit']} Endi <b>kanal nomini</b> yuboring:",
        "en": f"{E['edit']} Now send the <b>channel name</b>:",
    },
    "admin.add_channel_link": {
        "ru": (
            f"{E['link']} Теперь отправь <b>ссылку или юзернейм канала</b>\n\n"
            "Принимаю любой формат:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
        "uz": (
            f"{E['link']} Endi <b>kanal havolasi yoki username</b> yuboring\n\n"
            "Istalgan formatda:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
        "en": (
            f"{E['link']} Now send the <b>channel link or username</b>\n\n"
            "Any format accepted:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
    },
    "admin.channel_added": {
        "ru": f"{E['check']} <b>Канал добавлен!</b>",
        "uz": f"{E['check']} <b>Kanal qo'shildi!</b>",
        "en": f"{E['check']} <b>Channel added!</b>",
    },
    "admin.confirm_delete": {
        "ru": f"{E['warning']} <b>Удалить канал?</b>\n\nID: <code>{{channel_id}}</code>\n\nЭто действие нельзя отменить.",
        "uz": f"{E['warning']} <b>Kanalni o'chirishni xohlaysizmi?</b>\n\nID: <code>{{channel_id}}</code>\n\nBu amalni qaytarib bo'lmaydi.",
        "en": f"{E['warning']} <b>Delete channel?</b>\n\nID: <code>{{channel_id}}</code>\n\nThis action cannot be undone.",
    },
    "admin.id_not_number": {
        "ru": f"{E['cross']} ID должен быть числом. Попробуй ещё раз:",
        "uz": f"{E['cross']} ID raqam bo'lishi kerak. Qayta urinib ko'ring:",
        "en": f"{E['cross']} ID must be a number. Try again:",
    },
    "admin.title_too_long": {
        "ru": f"{E['cross']} Название слишком длинное (макс 200 символов)",
        "uz": f"{E['cross']} Nom juda uzun (maks 200 belgi)",
        "en": f"{E['cross']} Name is too long (max 200 characters)",
    },
    "admin.link_invalid": {
        "ru": f"{E['cross']} Не удалось распознать ссылку.\nПопробуй ещё:",
        "uz": f"{E['cross']} Havolani aniqlab bo'lmadi.\nQayta urinib ko'ring:",
        "en": f"{E['cross']} Could not parse the link.\nTry again:",
    },
    "admin.channel_removed": {
        "ru": f"{E['check']} Канал удалён!",
        "uz": f"{E['check']} Kanal o'chirildi!",
        "en": f"{E['check']} Channel removed!",
    },
    "admin.channel_not_found": {
        "ru": f"{E['cross']} Канал не найден",
        "uz": f"{E['cross']} Kanal topilmadi",
        "en": f"{E['cross']} Channel not found",
    },
    "admin.no_message": {
        "ru": f"{E['cross']} Нет сообщения для рассылки",
        "uz": f"{E['cross']} Yuborish uchun xabar yo'q",
        "en": f"{E['cross']} No message to broadcast",
    },
    "admin.no_access_alert": {
        "ru": f"{E['lock']} Нет доступа",
        "uz": f"{E['lock']} Kirish huquqi yo'q",
        "en": f"{E['lock']} No access",
    },

    # === Кнопки админки ===
    "btn.admin_stats": {"ru": "Статистика", "uz": "Statistika", "en": "Statistics"},
    "btn.admin_channels": {"ru": "Каналы", "uz": "Kanallar", "en": "Channels"},
    "btn.admin_home": {"ru": "Главное меню", "uz": "Bosh menyu", "en": "Main menu"},
    "btn.admin_add": {"ru": "Добавить канал", "uz": "Kanal qo'shish", "en": "Add channel"},
    "btn.admin_back": {"ru": "Назад", "uz": "Orqaga", "en": "Back"},
    "btn.admin_cancel": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "btn.admin_confirm_del": {"ru": "Да, удалить", "uz": "Ha, o'chirish", "en": "Yes, delete"},
    "btn.admin_cancel_del": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "btn.admin_panel": {"ru": "Админ-панель", "uz": "Admin panel", "en": "Admin panel"},
    "btn.admin_broadcast": {"ru": "Рассылка", "uz": "Xabar yuborish", "en": "Broadcast"},

    # === Рассылка ===
    "admin.broadcast_prompt": {
        "ru": f"{E['plane']} <b>Массовая рассылка</b>\n\nОтправь текст/фото/видео для рассылки.\nПоддерживается HTML.",
        "uz": f"{E['plane']} <b>Ommaviy xabar</b>\n\nYuborish uchun matn/rasm/video yuboring.\nHTML qo'llab-quvvatlanadi.",
        "en": f"{E['plane']} <b>Mass broadcast</b>\n\nSend text/photo/video to broadcast.\nHTML supported.",
    },
    "admin.broadcast_preview": {
        "ru": f"{E['eye']} <b>Предпросмотр</b>\n\nОтправить это сообщение всем юзерам?",
        "uz": f"{E['eye']} <b>Oldindan ko'rish</b>\n\nBu xabarni barcha foydalanuvchilarga yuborishni xohlaysizmi?",
        "en": f"{E['eye']} <b>Preview</b>\n\nSend this message to all users?",
    },
    "admin.broadcast_confirm": {"ru": "Да, отправить", "uz": "Ha, yuborish", "en": "Yes, send"},
    "admin.broadcast_cancel": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "admin.broadcast_started": {
        "ru": f"{E['plane']} Рассылка запущена... Ожидай отчёт.",
        "uz": f"{E['plane']} Xabar yuborilmoqda... Hisobotni kuting.",
        "en": f"{E['plane']} Broadcast started... Wait for report.",
    },
    "admin.broadcast_done": {
        "ru": f"{E['chart']} <b>Рассылка завершена!</b>\n\n{E['check']} Доставлено: <b>{{success}}</b>\n{E['cross']} Ошибок: <b>{{failed}}</b>\n{E['users']} Всего: <b>{{total}}</b>",
        "uz": f"{E['chart']} <b>Xabar yuborish tugadi!</b>\n\n{E['check']} Yetkazildi: <b>{{success}}</b>\n{E['cross']} Xatolar: <b>{{failed}}</b>\n{E['users']} Jami: <b>{{total}}</b>",
        "en": f"{E['chart']} <b>Broadcast complete!</b>\n\n{E['check']} Delivered: <b>{{success}}</b>\n{E['cross']} Failed: <b>{{failed}}</b>\n{E['users']} Total: <b>{{total}}</b>",
    },

    # === TMDB-специфика ===
    "search.prompt": {
        "ru": f"{E['search']} <b>Введи название фильма, сериала или имя актёра:</b>",
        "uz": f"{E['search']} <b>Film, serial yoki aktyor nomini kiriting:</b>",
        "en": f"{E['search']} <b>Enter a movie, TV show or actor name:</b>",
    },
    "search.results": {
        "ru": f"{E['search']} <b>Результаты по запросу:</b> <i>{{query}}</i>\n\nНайдено: {{count}}",
        "uz": f"{E['search']} <b>So'rov natijalari:</b> <i>{{query}}</i>\n\nTopildi: {{count}}",
        "en": f"{E['search']} <b>Results for:</b> <i>{{query}}</i>\n\nFound: {{count}}",
    },
    "search.no_results": {
        "ru": f"{E['cross']} По запросу <i>{{query}}</i> ничего не найдено.",
        "uz": f"{E['cross']} <i>{{query}}</i> bo'yicha hech narsa topilmadi.",
        "en": f"{E['cross']} Nothing found for <i>{{query}}</i>.",
    },
    "search.expired": {
        "ru": "Запрос устарел. Введи поиск заново.",
        "uz": "So'rov eskirdi. Qidiruvni qaytadan kiriting.",
        "en": "Query expired. Please search again.",
    },
    "movie.card": {
        "ru": (
            "{icon} <b>{title}</b>{year}\n"
            "{rating}{genres}\n\n"
            "{overview}"
        ),
        "uz": (
            "{icon} <b>{title}</b>{year}\n"
            "{rating}{genres}\n\n"
            "{overview}"
        ),
        "en": (
            "{icon} <b>{title}</b>{year}\n"
            "{rating}{genres}\n\n"
            "{overview}"
        ),
    },
    "inline.open_bot": {
        "ru": "Открой бота для подробностей.",
        "uz": "Batafsil ma'lumot uchun botni oching.",
        "en": "Open the bot for details.",
    },
    "movie.no_overview": {
        "ru": "<i>Описание отсутствует.</i>",
        "uz": "<i>Tavsif yo'q.</i>",
        "en": "<i>No overview available.</i>",
    },
    "movie.no_trailer": {
        "ru": f"{E['cross']} Трейлер не найден.",
        "uz": f"{E['cross']} Treyler topilmadi.",
        "en": f"{E['cross']} Trailer not found.",
    },
    "movie.trailer": {
        "ru": f"{E['video']} <b>Трейлер:</b> <a href='{{url}}'>{{name}}</a>",
        "uz": f"{E['video']} <b>Treyler:</b> <a href='{{url}}'>{{name}}</a>",
        "en": f"{E['video']} <b>Trailer:</b> <a href='{{url}}'>{{name}}</a>",
    },
    "movie.cast_title": {
        "ru": f"{E['users']} <b>Актёры:</b>\n",
        "uz": f"{E['users']} <b>Aktyorlar:</b>\n",
        "en": f"{E['users']} <b>Cast:</b>\n",
    },
    "movie.no_cast": {
        "ru": f"{E['cross']} Информация об актёрах отсутствует.",
        "uz": f"{E['cross']} Aktyorlar haqida ma'lumot yo'q.",
        "en": f"{E['cross']} No cast information.",
    },
    "movie.similar_title": {
        "ru": f"{E['video']} <b>Похожие фильмы/сериалы:</b>",
        "uz": f"{E['video']} <b>O'xshash filmlar/seriallar:</b>",
        "en": f"{E['video']} <b>Similar movies/TV shows:</b>",
    },
    "movie.no_similar": {
        "ru": f"{E['cross']} Похожих не найдено.",
        "uz": f"{E['cross']} O'xshashlar topilmadi.",
        "en": f"{E['cross']} No similar items.",
    },
    "movie.watch_title": {
        "ru": f"{E['video']} <b>Где посмотреть</b> ({{region}}):\n",
        "uz": f"{E['video']} <b>Qayerda ko'rish</b> ({{region}}):\n",
        "en": f"{E['video']} <b>Where to watch</b> ({{region}}):\n",
    },
    "movie.no_watch": {
        "ru": f"{E['cross']} Информация о провайдерах для региона {{region}} отсутствует.",
        "uz": f"{E['cross']} {{region}} mintaqasi uchun provayderlar haqida ma'lumot yo'q.",
        "en": f"{E['cross']} No provider info for region {{region}}.",
    },
    "fav.added": {
        "ru": f"{E['check']} Добавлено в избранное",
        "uz": f"{E['check']} Sevimlilarga qo'shildi",
        "en": f"{E['check']} Added to favorites",
    },
    "fav.removed": {
        "ru": f"{E['check']} Удалено из избранного",
        "uz": f"{E['check']} Sevimlilardan o'chirildi",
        "en": f"{E['check']} Removed from favorites",
    },
    "seen.added": {
        "ru": f"{E['check']} Отмечено как просмотренное",
        "uz": f"{E['check']} Ko'rilgan deb belgilandi",
        "en": f"{E['check']} Marked as watched",
    },
    "seen.removed": {
        "ru": f"{E['check']} Снято с просмотренного",
        "uz": f"{E['check']} Ko'rilganlardan o'chirildi",
        "en": f"{E['check']} Unmarked watched",
    },
    "favorites.title": {
        "ru": f"{E['star']} <b>Избранное</b> ({{count}})",
        "uz": f"{E['star']} <b>Sevimlilar</b> ({{count}})",
        "en": f"{E['star']} <b>Favorites</b> ({{count}})",
    },
    "favorites.empty": {
        "ru": f"{E['star']} Избранное пусто. Открой карточку фильма и нажми ❤️",
        "uz": f"{E['star']} Sevimlilar bo'sh. Film kartasini oching va ❤️ bosing",
        "en": f"{E['star']} Favorites is empty. Open a movie card and tap ❤️",
    },
    "watched.title": {
        "ru": f"{E['check']} <b>Просмотрено</b> ({{count}})",
        "uz": f"{E['check']} <b>Ko'rilgan</b> ({{count}})",
        "en": f"{E['check']} <b>Watched</b> ({{count}})",
    },
    "watched.empty": {
        "ru": f"{E['check']} Список просмотренных пуст.",
        "uz": f"{E['check']} Ko'rilganlar ro'yxati bo'sh.",
        "en": f"{E['check']} Watched list is empty.",
    },
    "lists.trending": {
        "ru": f"{E['lightning']} <b>В тренде на этой неделе</b>",
        "uz": f"{E['lightning']} <b>Bu hafta trendda</b>",
        "en": f"{E['lightning']} <b>Trending this week</b>",
    },
    "lists.top": {
        "ru": f"{E['star']} <b>Топ по рейтингу</b>",
        "uz": f"{E['star']} <b>Reyting bo'yicha eng yaxshi</b>",
        "en": f"{E['star']} <b>Top rated</b>",
    },
    "lists.now_playing": {
        "ru": f"{E['video']} <b>Сейчас в кинотеатрах</b>",
        "uz": f"{E['video']} <b>Hozir kinoteatrlarda</b>",
        "en": f"{E['video']} <b>Now playing</b>",
    },
    "lists.upcoming": {
        "ru": f"{E['clock']} <b>Скоро в прокате</b>",
        "uz": f"{E['clock']} <b>Tez orada prokatda</b>",
        "en": f"{E['clock']} <b>Upcoming</b>",
    },
    "lists.genres": {
        "ru": f"{E['folder']} <b>Выбери жанр:</b>",
        "uz": f"{E['folder']} <b>Janrni tanlang:</b>",
        "en": f"{E['folder']} <b>Choose a genre:</b>",
    },
    "actor.not_found": {
        "ru": f"{E['cross']} Актёр/режиссёр не найден.",
        "uz": f"{E['cross']} Aktyor/rejissyor topilmadi.",
        "en": f"{E['cross']} Actor/director not found.",
    },
    "actor.usage": {
        "ru": f"{E['info']} Использование: <code>/actor Том Хэнкс</code>",
        "uz": f"{E['info']} Foydalanish: <code>/actor Tom Hanks</code>",
        "en": f"{E['info']} Usage: <code>/actor Tom Hanks</code>",
    },
    "director.usage": {
        "ru": f"{E['info']} Использование: <code>/director Кристофер Нолан</code>",
        "uz": f"{E['info']} Foydalanish: <code>/director Christopher Nolan</code>",
        "en": f"{E['info']} Usage: <code>/director Christopher Nolan</code>",
    },
    "actor.title": {
        "ru": f"{E['profile']} <b>{{name}}</b>\n\n{E['video']} Известные работы:",
        "uz": f"{E['profile']} <b>{{name}}</b>\n\n{E['video']} Mashhur ishlari:",
        "en": f"{E['profile']} <b>{{name}}</b>\n\n{E['video']} Known for:",
    },
    "btn.trailer": {"ru": "Трейлер", "uz": "Treyler", "en": "Trailer"},
    "btn.where_watch": {"ru": "Где посмотреть", "uz": "Qayerda ko'rish", "en": "Where to watch"},
    "btn.cast": {"ru": "Актёры", "uz": "Aktyorlar", "en": "Cast"},
    "btn.similar": {"ru": "Похожие", "uz": "O'xshash", "en": "Similar"},
    "btn.add_fav": {"ru": "В избранное", "uz": "Sevimlilarga", "en": "To favorites"},
    "btn.remove_fav": {"ru": "Убрать", "uz": "O'chirish", "en": "Remove"},
    "btn.mark_seen": {"ru": "Посмотрено", "uz": "Ko'rildi", "en": "Watched"},
    "btn.unseen": {"ru": "Не смотрел", "uz": "Ko'rmadim", "en": "Not seen"},

    # === Провайдеры просмотра (movie.py: show_watch_providers) ===
    "movie.provider.flatrate": {
        "ru": "Подписка",
        "uz": "Obuna",
        "en": "Streaming",
    },
    "movie.provider.rent": {
        "ru": "Аренда",
        "uz": "Ijara",
        "en": "Rent",
    },
    "movie.provider.buy": {
        "ru": "Покупка",
        "uz": "Sotib olish",
        "en": "Buy",
    },
    "movie.provider.free": {
        "ru": "Бесплатно",
        "uz": "Bepul",
        "en": "Free",
    },

    # === Счётчик голосов в карточке фильма ===
    "movie.votes": {
        "ru": "голосов",
        "uz": "ovoz",
        "en": "votes",
    },

    # === Карточка сериала (доп. поля) ===
    "movie.seasons": {
        "ru": "Сезонов: {seasons}, эпизодов: {episodes}",
        "uz": "Mavsum: {seasons}, qism: {episodes}",
        "en": "Seasons: {seasons}, episodes: {episodes}",
    },
    "movie.hours": {
        "ru": "ч",
        "uz": "soat",
        "en": "h",
    },
    "movie.minutes": {
        "ru": "м",
        "uz": "daq",
        "en": "m",
    },

    # === Описания команд бота (для меню Telegram) ===
    "cmd.start": {
        "ru": "Запустить бота",
        "uz": "Botni boshlash",
        "en": "Start the bot",
    },
    "cmd.menu": {
        "ru": "Главное меню",
        "uz": "Bosh menyu",
        "en": "Main menu",
    },
    "cmd.profile": {
        "ru": "Мой профиль",
        "uz": "Mening profilim",
        "en": "My profile",
    },
    "cmd.help": {
        "ru": "Помощь",
        "uz": "Yordam",
        "en": "Help",
    },
    "cmd.language": {
        "ru": "Сменить язык",
        "uz": "Tilni o'zgartirish",
        "en": "Change language",
    },
    "cmd.search": {"ru": "Поиск фильма/сериала", "uz": "Film qidirish", "en": "Search movie"},
    "cmd.trending": {"ru": "В тренде", "uz": "Trendda", "en": "Trending"},
    "cmd.top": {"ru": "Топ рейтинг", "uz": "Eng yuqori reyting", "en": "Top rated"},
    "cmd.now_playing": {"ru": "Сейчас в кино", "uz": "Hozir kinoda", "en": "Now playing"},
    "cmd.upcoming": {"ru": "Скоро в прокате", "uz": "Tez orada", "en": "Upcoming"},
    "cmd.random": {"ru": "Случайный фильм", "uz": "Tasodifiy film", "en": "Random movie"},
    "cmd.genres": {"ru": "Жанры", "uz": "Janrlar", "en": "Genres"},
    "cmd.favorites": {"ru": "Избранное", "uz": "Sevimlilar", "en": "Favorites"},
    "cmd.watched": {"ru": "Просмотренное", "uz": "Ko'rilgan", "en": "Watched"},
    "cmd.actor": {"ru": "Поиск по актёру", "uz": "Aktyor bo'yicha", "en": "Search by actor"},
    "cmd.director": {"ru": "Поиск по режиссёру", "uz": "Rejissyor bo'yicha", "en": "Search by director"},
}


import re as _re

_HTML_TAG_RE = _re.compile(r"<[^>]+>")


def t(key: str, lang: str = "ru", **kwargs) -> str:
    """Получить перевод по ключу и языку"""
    translations = TRANSLATIONS.get(key, {})
    text = translations.get(lang, translations.get("ru", key))
    if kwargs:
        text = text.format(**kwargs)
    return text


def t_plain(key: str, lang: str = "ru", **kwargs) -> str:
    """Перевод без HTML-тегов — для callback.answer (toast/alert не парсят HTML)."""
    return _HTML_TAG_RE.sub("", t(key, lang, **kwargs))


def detect_language(language_code: str | None) -> str:
    """Определяет язык по Telegram: ru → русский, uz → узбекский, остальное → английский"""
    if not language_code:
        return "en"
    if language_code.startswith("ru"):
        return "ru"
    if language_code.startswith("uz"):
        return "uz"
    return "en"
