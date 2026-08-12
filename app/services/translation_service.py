import logging
import time

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

MAX_CHARS_PER_REQUEST = 450


def _translate_chunk(text: str, source_lang: str, target_lang: str) -> str:
    response = httpx.get(
        settings.translation_api_url,
        params={"q": text, "langpair": f"{source_lang}|{target_lang}"},
        timeout=15.0,
    )
    response.raise_for_status()
    data = response.json()

    translated = data.get("responseData", {}).get("translatedText")
    if not translated:
        detail = data.get("responseDetails") or (
            "Quota exceeded" if data.get("quotaFinished") else "Translation failed"
        )
        raise RuntimeError(detail)

    return translated


def _translate_long_text(text: str, source_lang: str, target_lang: str) -> str:
    if len(text.encode("utf-8")) <= MAX_CHARS_PER_REQUEST:
        return _translate_chunk(text, source_lang, target_lang)

    chunks: list[str] = []
    remaining = text
    while remaining:
        chunk = remaining[:MAX_CHARS_PER_REQUEST]
        last_space = chunk.rfind(" ")
        if last_space > MAX_CHARS_PER_REQUEST // 2:
            chunk = chunk[: last_space + 1]
        chunks.append(chunk)
        remaining = remaining[len(chunk) :]

    return "".join(_translate_chunk(part, source_lang, target_lang) for part in chunks)


def translate_text(text: str, target_lang: str, source_lang: str | None = None) -> str:
    source = source_lang or settings.i18n_source_lang
    if not text or not target_lang or target_lang == source:
        return text

    try:
        return _translate_chunk(text, source, target_lang)
    except Exception as exc:
        logger.warning("Traducción fallida %s→%s: %s", source, target_lang, exc)
        return text


def translate_text_with_retry(
    text: str,
    target_lang: str,
    source_lang: str | None = None,
    delay_ms: int | None = None,
) -> str:
    source = source_lang or settings.i18n_source_lang
    if not text or not target_lang or target_lang == source:
        return text

    wait_ms = delay_ms if delay_ms is not None else settings.translation_delay_ms
    if wait_ms > 0:
        time.sleep(wait_ms / 1000)

    max_retries = 2
    for attempt in range(1, max_retries + 1):
        try:
            return _translate_long_text(text, source, target_lang)
        except Exception as exc:
            if attempt < max_retries:
                time.sleep(attempt)
                logger.warning(
                    "Reintento traducción %s→%s (intento %s): %s",
                    source,
                    target_lang,
                    attempt,
                    exc,
                )
            else:
                logger.error("Traducción fallida %s→%s: %s", source, target_lang, exc)
                return text

    return text


def translate_to_all_languages(
    text: str,
    source_lang: str | None = None,
) -> dict[str, str]:
    source = source_lang or settings.i18n_source_lang
    results: dict[str, str] = {source: text}

    for lang in settings.i18n_target_languages_list:
        if lang == source:
            continue
        results[lang] = translate_text_with_retry(text, lang, source)
        time.sleep(settings.translation_delay_ms / 1000)

    return results
