"""
Module 4: Language Detection
Detects the language of each review, including code-mixed Telugu+English.
Uses langdetect as the primary library and Unicode heuristics as fallback.
"""

import re
from typing import Optional

# Telugu Unicode block: U+0C00–U+0C7F
_TELUGU_PATTERN = re.compile(r"[\u0C00-\u0C7F]")
# Hindi / Devanagari: U+0900–U+097F
_HINDI_PATTERN   = re.compile(r"[\u0900-\u097F]")
# Tamil: U+0B80–U+0BFF
_TAMIL_PATTERN   = re.compile(r"[\u0B80-\u0BFF]")
# Kannada: U+0C80–U+0CFF
_KANNADA_PATTERN = re.compile(r"[\u0C80-\u0CFF]")
# Malayalam: U+0D00–U+0D7F
_MALAYALAM_PATTERN = re.compile(r"[\u0D00-\u0D7F]")


def _unicode_language_hint(text: str) -> Optional[str]:
    """Fast Unicode-range heuristic — returns script name or None."""
    if _TELUGU_PATTERN.search(text):
        return "Telugu"
    if _HINDI_PATTERN.search(text):
        return "Hindi"
    if _TAMIL_PATTERN.search(text):
        return "Tamil"
    if _KANNADA_PATTERN.search(text):
        return "Kannada"
    if _MALAYALAM_PATTERN.search(text):
        return "Malayalam"
    return None


def _is_code_mixed(text: str) -> bool:
    """
    True if text contains both Latin characters and a South-Asian script.
    Indicates code-mixing (e.g., Tanglish / Telugu+English).
    """
    has_latin  = bool(re.search(r"[a-zA-Z]", text))
    has_script = bool(_unicode_language_hint(text))
    return has_latin and has_script


# ISO 639-1 → readable name map (subset)
_LANG_MAP = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "bn": "Bengali",
    "ur": "Urdu",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "zh-cn": "Chinese",
    "ar": "Arabic",
    "ja": "Japanese",
    "ko": "Korean",
}


def detect_language(text: str) -> str:
    """
    Returns a human-readable language label for the given text.
    Detects code-mixed languages such as 'Telugu+English (Code-Mixed)'.
    """
    # 1. Unicode heuristic
    script = _unicode_language_hint(text)

    # 2. Code-mix check
    if script and _is_code_mixed(text):
        return f"{script}+English (Code-Mixed)"
    if script:
        return script

    # 3. langdetect
    try:
        from langdetect import detect, LangDetectException
        lang_code = detect(text)
        return _LANG_MAP.get(lang_code, lang_code.upper())
    except Exception:
        pass

    # 4. Final fallback
    return "English"
