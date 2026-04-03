"""
Module 6: Emotion Detection
Uses rule-based analysis - no model download needed, works instantly.
Detects: Joy, Anger, Sadness, Surprise, Sarcasm, Neutral.
"""

import re
from typing import List, Dict

_JOY_WORDS = {
    "happy", "love", "great", "amazing", "joy", "excited", "wonderful",
    "fantastic", "best", "excellent", "good", "pleased", "glad", "enjoy",
    "delight", "cheerful", "satisfied", "thrilled", "awesome", "superb",
    "bagundi", "chala bagundi", "perfect", "brilliant", "wow", "yay",
}

_ANGER_WORDS = {
    "angry", "furious", "hate", "terrible", "worst", "pathetic",
    "rubbish", "horrible", "disgusting", "ridiculous", "awful", "waste",
    "fraud", "scam", "cheat", "liar", "stupid", "useless", "nonsense",
    "outrageous", "unacceptable", "disgusted", "infuriated", "mad",
}

_SADNESS_WORDS = {
    "sad", "disappointed", "broken", "upset", "depressed", "failed",
    "regret", "sorry", "unfortunate", "bad", "poor", "missed", "lost",
    "unhappy", "miserable", "hopeless", "terrible", "hurt", "grief",
    "crying", "tears", "heartbroken", "devastated", "gloomy",
}

_SURPRISE_WORDS = {
    "wow", "shocked", "unbelievable", "unexpected", "surprised",
    "suddenly", "incredible", "omg", "whoa", "really", "seriously",
    "cannot believe", "mind blown", "astonished", "stunned", "amazed",
}

_SARCASM_PATTERNS = [
    r"(oh\s+sure|yeah\s+right|oh\s+wow|so\s+helpful|oh\s+great)",
    r"(what\s+a\s+surprise|as\s+if|obviously|totally\s+amazing)",
    r"(great\s+job.{0,15}not|amazing.{0,15}not|wonderful.{0,15}not)",
    r"(thanks.{0,15}useless|just\s+what\s+i\s+needed.{0,15}broken)",
]
_SARCASM_RE = [re.compile(p, re.IGNORECASE) for p in _SARCASM_PATTERNS]

_INVERSION_POS = {"great", "amazing", "wonderful", "perfect", "excellent", "love", "best"}
_INVERSION_NEG = {"but", "however", "unfortunately", "except", "although", "despite", "not"}


def _is_sarcastic(text: str) -> bool:
    for pattern in _SARCASM_RE:
        if pattern.search(text):
            return True
    tokens = set(re.findall(r"\w+", text.lower()))
    if tokens & _INVERSION_POS and tokens & _INVERSION_NEG:
        return True
    return False


def _lexicon_emotion(text: str) -> Dict:
    if _is_sarcastic(text):
        return {"label": "Sarcasm", "score": 0.80}
    tokens = set(re.findall(r"\w+", text.lower()))
    scores = {
        "Joy":      len(tokens & _JOY_WORDS),
        "Anger":    len(tokens & _ANGER_WORDS),
        "Sadness":  len(tokens & _SADNESS_WORDS),
        "Surprise": len(tokens & _SURPRISE_WORDS),
    }
    best = max(scores, key=scores.get)
    total = sum(scores.values()) or 1
    if scores[best] == 0:
        return {"label": "Neutral", "score": 0.5}
    return {"label": best, "score": round(scores[best] / total, 2)}


def detect_emotions(texts: List[str]) -> List[Dict]:
    """
    Instant rule-based emotion detection. No downloads needed.
    Labels: Joy, Anger, Sadness, Surprise, Sarcasm, Neutral.
    """
    return [_lexicon_emotion(t) for t in texts]
