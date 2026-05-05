"""Inline-клавиатуры — меню, подписка, выбор языка"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.config import settings
from bot.emojis import E_ID
from bot.i18n import t


def get_start_keyboard(user_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """Главное меню бота"""
    buttons = [
        [InlineKeyboardButton(
            text=t("btn.search", lang),
            callback_data="search_movie",
            style="primary",
            icon_custom_emoji_id=E_ID["search"],
        )],
        [
            InlineKeyboardButton(
                text=t("btn.trending", lang),
                callback_data="menu_trending",
                style="primary",
            ),
            InlineKeyboardButton(
                text=t("btn.top", lang),
                callback_data="menu_top",
                style="primary",
            ),
        ],
        [
            InlineKeyboardButton(
                text=t("btn.now_playing", lang),
                callback_data="menu_now_playing",
                style="primary",
            ),
            InlineKeyboardButton(
                text=t("btn.upcoming", lang),
                callback_data="menu_upcoming",
                style="primary",
            ),
        ],
        [
            InlineKeyboardButton(
                text=t("btn.random", lang),
                callback_data="menu_random",
                style="primary",
            ),
            InlineKeyboardButton(
                text=t("btn.genres", lang),
                callback_data="menu_genres",
                style="primary",
            ),
        ],
        [
            InlineKeyboardButton(
                text=t("btn.favorites", lang),
                callback_data="user_favorites",
                style="success",
                icon_custom_emoji_id=E_ID["heart"],
            ),
            InlineKeyboardButton(
                text=t("btn.watched", lang),
                callback_data="user_watched",
                style="success",
                icon_custom_emoji_id=E_ID["check"],
            ),
        ],
        [
            InlineKeyboardButton(
                text=t("btn.profile", lang),
                callback_data="my_profile",
                style="success",
                icon_custom_emoji_id=E_ID["profile"],
            ),
            InlineKeyboardButton(
                text=t("btn.help", lang),
                callback_data="my_help",
                style="success",
                icon_custom_emoji_id=E_ID["info"],
            ),
        ],
        [InlineKeyboardButton(
            text=t("btn.language", lang),
            callback_data="change_language",
            style="success",
            icon_custom_emoji_id=E_ID["gear"],
        )],
    ]

    # кнопка админки для админов
    if user_id in settings.admin_id_list:
        buttons.append([InlineKeyboardButton(
            text=t("btn.admin_panel", lang),
            callback_data="admin_panel",
            style="danger",
            icon_custom_emoji_id=E_ID["lock"],
        )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Кнопка 'Назад' в главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=t("btn.back", lang),
            callback_data="back_to_menu",
            style="success",
            icon_custom_emoji_id=E_ID["back"],
        )],
    ])


def get_close_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Кнопка 'Назад' = закрыть текущее сообщение (вернуться к предыдущему виду)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=t("btn.back", lang),
            callback_data="close_msg",
            style="success",
            icon_custom_emoji_id=E_ID["back"],
        )],
    ])


def get_subscription_keyboard(
    channels: list[dict], lang: str = "ru"
) -> InlineKeyboardMarkup:
    """Клавиатура подписки на каналы"""
    buttons = []
    for ch in channels:
        buttons.append([InlineKeyboardButton(
            text=f"{ch['title']}",
            url=ch["invite_link"],
            icon_custom_emoji_id=E_ID["megaphone"],
        )])
    buttons.append([InlineKeyboardButton(
        text=t("btn.check_sub", lang),
        callback_data="check_subscription",
        style="success",
        icon_custom_emoji_id=E_ID["check"],
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора языка"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Русский",
                callback_data="set_lang_ru",
                style="success",
                icon_custom_emoji_id=E_ID["flag_ru"],
            ),
            InlineKeyboardButton(
                text="O'zbek",
                callback_data="set_lang_uz",
                style="success",
                icon_custom_emoji_id=E_ID["flag_uz"],
            ),
            InlineKeyboardButton(
                text="English",
                callback_data="set_lang_en",
                style="success",
                icon_custom_emoji_id=E_ID["flag_gb"],
            ),
        ],
    ])


def _result_title(item: dict) -> str:
    """Подпись результата поиска с типом-эмодзи (custom emoji ID непредсказуем для некоторых клиентов)"""
    mt = item.get("media_type") or ("movie" if item.get("title") else "tv")
    if mt == "person":
        return f"👤 {item.get('name', '?')}"
    icon = "🎬" if mt == "movie" else "📺"
    title = item.get("title") or item.get("name") or "?"
    date = item.get("release_date") or item.get("first_air_date") or ""
    year = date[:4] if date else ""
    parts = [f"{icon} {title}"]
    if year:
        parts.append(f"({year})")
    return " ".join(parts)


def get_results_keyboard(
    results: list[dict],
    lang: str = "ru",
    back_callback: str = "back_to_menu",
    page: int = 1,
    total_pages: int = 1,
) -> InlineKeyboardMarkup:
    """Список до 10 результатов поиска с пагинацией."""
    buttons = []
    for item in results[:10]:
        mt = item.get("media_type") or ("movie" if item.get("title") else "tv")
        tmdb_id = item.get("id")
        if not tmdb_id:
            continue
        if mt == "person":
            cb = f"person:{tmdb_id}"
        else:
            cb = f"{mt}:{tmdb_id}"
        buttons.append([InlineKeyboardButton(
            text=_result_title(item)[:60],
            callback_data=cb,
            style="primary",
        )])
    # пагинация: ← / индикатор / →
    if total_pages > 1:
        nav = []
        if page > 1:
            nav.append(InlineKeyboardButton(
                text="←", callback_data=f"searchpg:{page-1}", style="primary",
            ))
        nav.append(InlineKeyboardButton(
            text=f"{page}/{total_pages}", callback_data="noop", style="success",
        ))
        if page < total_pages:
            nav.append(InlineKeyboardButton(
                text="→", callback_data=f"searchpg:{page+1}", style="primary",
            ))
        buttons.append(nav)
    buttons.append([InlineKeyboardButton(
        text=t("btn.back", lang),
        callback_data=back_callback,
        style="success",
        icon_custom_emoji_id=E_ID["back"],
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_movie_keyboard(
    tmdb_id: int,
    media_type: str,
    is_fav: bool = False,
    is_seen: bool = False,
    has_trailer: bool = True,
    lang: str = "ru",
) -> InlineKeyboardMarkup:
    """Карточка фильма/сериала: трейлер, актёры, похожие, избранное, просмотрено"""
    fav_text = t("btn.remove_fav", lang) if is_fav else t("btn.add_fav", lang)
    fav_icon = E_ID["broken_heart"] if is_fav else E_ID["heart"]
    seen_text = t("btn.unseen", lang) if is_seen else t("btn.mark_seen", lang)
    seen_icon = E_ID["cross"] if is_seen else E_ID["check"]
    rows = []
    row1 = []
    if has_trailer:
        row1.append(InlineKeyboardButton(
            text=t("btn.trailer", lang),
            callback_data=f"trailer:{media_type}:{tmdb_id}",
            style="primary",
            icon_custom_emoji_id=E_ID["film"],
        ))
    row1.append(InlineKeyboardButton(
        text=t("btn.where_watch", lang),
        callback_data=f"watch:{media_type}:{tmdb_id}",
        style="primary",
        icon_custom_emoji_id=E_ID["tv"],
    ))
    rows.append(row1)
    rows.append([
        InlineKeyboardButton(
            text=t("btn.cast", lang),
            callback_data=f"cast:{media_type}:{tmdb_id}",
            style="primary",
            icon_custom_emoji_id=E_ID["group"],
        ),
        InlineKeyboardButton(
            text=t("btn.similar", lang),
            callback_data=f"similar:{media_type}:{tmdb_id}",
            style="primary",
            icon_custom_emoji_id=E_ID["dice"],
        ),
    ])
    rows.append([
        InlineKeyboardButton(
            text=fav_text,
            callback_data=f"fav:{media_type}:{tmdb_id}",
            style="danger" if is_fav else "success",
            icon_custom_emoji_id=fav_icon,
        ),
        InlineKeyboardButton(
            text=seen_text,
            callback_data=f"seen:{media_type}:{tmdb_id}",
            style="danger" if is_seen else "success",
            icon_custom_emoji_id=seen_icon,
        ),
    ])
    rows.append([InlineKeyboardButton(
        text=t("btn.back", lang),
        callback_data="back_to_menu",
        style="success",
        icon_custom_emoji_id=E_ID["back"],
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_genres_keyboard(genres: list[dict], lang: str = "ru") -> InlineKeyboardMarkup:
    """Список жанров (по 2 в строке)"""
    buttons = []
    row = []
    for g in genres:
        row.append(InlineKeyboardButton(
            text=g.get("name") or "?",
            callback_data=f"genre:{g['id']}",
            style="primary",
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(
        text=t("btn.back", lang),
        callback_data="back_to_menu",
        style="success",
        icon_custom_emoji_id=E_ID["back"],
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
