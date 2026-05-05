"""Перевод текстов через бесплатный Google Translate (deep-translator).
Используется как фолбэк, когда TMDB не возвращает описание/жанры на нужном языке.
"""
import asyncio
import logging

from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

# Кэш переведённых строк в памяти процесса (хэш текста + lang → перевод).
# Полные карточки фильмов всё равно кэшируются в БД — этот кэш страхует на случай
# параллельных запросов к одному фильму до записи в БД.
_cache: dict[tuple[str, str], str] = {}
_MAX_CACHE = 2000
_semaphore = asyncio.Semaphore(10)


async def translate(text: str, target_lang: str, source_lang: str = "auto") -> str:
    """Переводит текст. При ошибке возвращает оригинал."""
    if not text or not text.strip():
        return text
    if target_lang in ("ru", "en") and source_lang in ("ru", "en") and target_lang == source_lang:
        return text

    # deep-translator использует двухбуквенные коды
    target = {"ru": "ru", "uz": "uz", "en": "en"}.get(target_lang, target_lang)
    source = {"ru": "ru", "uz": "uz", "en": "en", "auto": "auto"}.get(source_lang, source_lang)

    key = (text, target)
    if key in _cache:
        return _cache[key]

    async with _semaphore:
        try:
            # GoogleTranslator синхронный — гоняем в thread pool
            result = await asyncio.to_thread(
                lambda: GoogleTranslator(source=source, target=target).translate(text[:4500])
            )
            if result and result.strip():
                if len(_cache) >= _MAX_CACHE:
                    # простая стратегия: вычистить половину
                    for k in list(_cache.keys())[: _MAX_CACHE // 2]:
                        _cache.pop(k, None)
                _cache[key] = result
                return result
        except Exception as e:
            logger.warning("Translate error (%s→%s): %s", source, target, e)
    return text
