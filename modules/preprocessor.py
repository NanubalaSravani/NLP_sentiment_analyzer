"""
Module 3: Preprocessing - No filtering, keeps all input as-is.
"""

import re
import html
from typing import List, Dict


def _clean_text(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _handle_code_mixed(text: str) -> str:
    replacements = {
        r"\bbagundi\b": "good",
        r"\bchala\b":   "very",
        r"\bnaku\b":    "to me",
        r"\bchinda\b":  "bad",
        r"\bledu\b":    "not",
        r"\bkaadu\b":   "not",
    }
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def preprocess_reviews(reviews: List[Dict]) -> List[Dict]:
    """Keep ALL reviews. Never filter anything out."""
    cleaned = []
    for rev in reviews:
        raw_text = rev.get("text", "")
        if not raw_text.strip():
            continue
        text = _clean_text(raw_text)
        text = _handle_code_mixed(text)
        # Always keep — even if just 1 character
        cleaned.append({
            "text": text if text.strip() else raw_text,
            "rating": rev.get("rating"),
            "timestamp": rev.get("timestamp"),
        })
    return cleaned
