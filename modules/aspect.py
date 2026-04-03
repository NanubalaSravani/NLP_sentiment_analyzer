"""
Module 7: Aspect-Based Sentiment Analysis (ABSA)
Extracts sentiment for product aspects: Price, Quality, Delivery.
Uses keyword-window matching with contextual negation handling.
"""

import re
from typing import List, Dict


# ── Aspect keyword banks ──────────────────────────────────────────────────────

ASPECT_KEYWORDS = {
    "price": [
        "price", "cost", "expensive", "cheap", "afford", "value", "worth",
        "money", "rate", "budget", "overpriced", "costly", "inexpensive",
        "pricing", "discounted", "deal", "offer",
    ],
    "quality": [
        "quality", "build", "material", "durable", "sturdy", "finish",
        "premium", "flimsy", "fragile", "solid", "workmanship", "made",
        "plastic", "metal", "texture", "feel", "looks", "appearance",
        "design", "defective", "broken", "genuine", "authentic", "original",
    ],
    "delivery": [
        "delivery", "shipping", "arrived", "dispatch", "courier", "transit",
        "package", "packaging", "delay", "late", "fast", "quick", "on time",
        "early", "speed", "shipped", "delivered", "tracking",
    ],
}

POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing", "fast", "quick", "cheap",
    "affordable", "reasonable", "value", "solid", "durable", "premium",
    "authentic", "genuine", "perfect", "satisfied", "happy", "love",
    "nice", "awesome", "best", "quality", "beautiful", "reliable",
}

NEGATIVE_WORDS = {
    "bad", "poor", "terrible", "awful", "expensive", "overpriced", "slow",
    "late", "delayed", "cheap" ,"flimsy", "broken", "defective", "fake",
    "damaged", "fragile", "worst", "horrible", "useless", "waste", "ugly",
}

NEGATION_WORDS = {"not", "no", "never", "don't", "doesn't", "didn't",
                  "isn't", "wasn't", "hardly", "barely", "neither"}

WINDOW_SIZE = 6  # words to the left and right of an aspect keyword


def _tokenize(text: str) -> List[str]:
    return re.findall(r"\w+", text.lower())


def _sentiment_score_in_window(tokens: List[str], center: int) -> str:
    """
    Scores sentiment in a ±WINDOW_SIZE token window around `center`.
    Returns 'positive', 'negative', or 'neutral'.
    """
    start = max(0, center - WINDOW_SIZE)
    end   = min(len(tokens), center + WINDOW_SIZE + 1)
    window = tokens[start:end]

    pos = neg = 0
    negate = False

    for tok in window:
        if tok in NEGATION_WORDS:
            negate = True
            continue
        if tok in POSITIVE_WORDS:
            if negate:
                neg += 1
            else:
                pos += 1
        elif tok in NEGATIVE_WORDS:
            if negate:
                pos += 1
            else:
                neg += 1
        negate = False

    if pos > neg:
        return "positive"
    if neg > pos:
        return "negative"
    return "neutral"


def _analyze_one(text: str) -> Dict[str, Dict[str, int]]:
    tokens = _tokenize(text)
    result = {
        "price":    {"positive": 0, "negative": 0, "neutral": 0},
        "quality":  {"positive": 0, "negative": 0, "neutral": 0},
        "delivery": {"positive": 0, "negative": 0, "neutral": 0},
    }

    for aspect, keywords in ASPECT_KEYWORDS.items():
        for i, tok in enumerate(tokens):
            if tok in keywords:
                sentiment = _sentiment_score_in_window(tokens, i)
                result[aspect][sentiment] += 1

    return result


def aspect_based_analysis(texts: List[str]) -> Dict[str, Dict[str, int]]:
    """
    Aggregates aspect-level sentiment counts across all reviews.
    Returns:
        {
          "price":    {"positive": int, "negative": int, "neutral": int},
          "quality":  {"positive": int, "negative": int, "neutral": int},
          "delivery": {"positive": int, "negative": int, "neutral": int},
        }
    """
    totals = {
        "price":    {"positive": 0, "negative": 0, "neutral": 0},
        "quality":  {"positive": 0, "negative": 0, "neutral": 0},
        "delivery": {"positive": 0, "negative": 0, "neutral": 0},
    }
    for text in texts:
        per_review = _analyze_one(text)
        for aspect in totals:
            for sent in ("positive", "negative", "neutral"):
                totals[aspect][sent] += per_review[aspect][sent]

    # Ensure at least a minimal display so the chart is never empty
    for aspect in totals:
        if sum(totals[aspect].values()) == 0:
            totals[aspect]["neutral"] = 1

    return totals
