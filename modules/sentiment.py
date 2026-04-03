"""
Module 5: Sentiment Analysis
Improved rule-based sentiment - accurately detects negative reviews.
"""

import re
from typing import List, Dict

# ── Expanded word banks ───────────────────────────────────────────────────────

POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing", "awesome", "best", "love",
    "perfect", "happy", "satisfied", "recommend", "fantastic", "wonderful",
    "superb", "nice", "brilliant", "outstanding", "quality", "fast",
    "quick", "genuine", "value", "worth", "beautiful", "reliable", "solid",
    "durable", "premium", "authentic", "pleased", "glad", "enjoy", "smooth",
    "comfortable", "easy", "useful", "helpful", "fresh", "clean", "strong",
    "bagundi", "super", "top", "impressive", "loved", "works", "working",
    "delivered", "accurate", "correct", "original", "affordable", "cheap",
    "reasonable", "neat", "clear", "bright", "cool", "wow", "yay",
    "satisfied", "happy", "thankful", "grateful", "excited",
}

NEGATIVE_WORDS = {
    # Quality issues
    "bad", "worst", "terrible", "awful", "horrible", "poor", "pathetic",
    "useless", "inferior", "fake", "cheap", "flimsy", "fragile", "broken",
    "defective", "damaged", "dirty", "ugly", "dull", "blurry", "faulty",
    # Experience issues
    "disappointed", "disappointing", "frustrating", "frustrated", "annoyed",
    "annoying", "angry", "upset", "unhappy", "dissatisfied", "regret",
    "regretted", "mistake", "wrong", "incorrect", "misleading", "deceived",
    # Action issues
    "waste", "wasted", "returned", "refund", "returning", "complaint",
    "complaining", "complained", "fraud", "scam", "cheated", "lied",
    # Delivery issues
    "late", "delayed", "delay", "missing", "lost", "damaged", "broken",
    "slow", "never", "arrived", "cancelled",
    # Strong negatives
    "hate", "hated", "horrible", "disgusting", "ridiculous", "pathetic",
    "nonsense", "useless", "worthless", "overpriced", "expensive",
    # Telugu negative words
    "chinda", "ledu", "kaadu", "waste",
    # Phrases treated as single tokens
    "not working", "doesnt work", "not worth", "do not buy", "dont buy",
    "not recommended", "not good", "not great", "not happy", "not satisfied",
    "stop working", "stopped working", "fell apart", "broke down",
}

STRONG_NEGATIVE_PHRASES = [
    r"not\s+working",
    r"doesn'?t\s+work",
    r"don'?t\s+buy",
    r"do\s+not\s+buy",
    r"waste\s+of\s+money",
    r"total\s+waste",
    r"not\s+worth",
    r"very\s+bad",
    r"very\s+poor",
    r"really\s+bad",
    r"not\s+good",
    r"not\s+recommended",
    r"not\s+happy",
    r"not\s+satisfied",
    r"not\s+working",
    r"stopped\s+working",
    r"broke\s+after",
    r"broke\s+down",
    r"fell\s+apart",
    r"poor\s+quality",
    r"bad\s+quality",
    r"worst\s+ever",
    r"never\s+buy",
    r"return\s+this",
    r"sent\s+wrong",
    r"wrong\s+product",
    r"not\s+as\s+described",
    r"completely\s+useless",
    r"total\s+fraud",
    r"it\s+is\s+bad",
    r"it'?s\s+bad",
    r"this\s+is\s+bad",
    r"definitely\s+negative",
    r"definit\w+\s+negative",
    r"not\s+at\s+all",
    r"not\s+even\s+close",
    r"absolute\s+garbage",
    r"complete\s+garbage",
    r"utter\s+disappointment",
]

STRONG_POSITIVE_PHRASES = [
    r"very\s+good",
    r"very\s+happy",
    r"really\s+good",
    r"highly\s+recommend",
    r"must\s+buy",
    r"great\s+product",
    r"love\s+it",
    r"loved\s+it",
    r"best\s+ever",
    r"works\s+perfectly",
    r"works\s+great",
    r"absolutely\s+love",
    r"totally\s+worth",
    r"great\s+value",
    r"worth\s+every",
    r"exceeded\s+expectations",
    r"chala\s+bagundi",
    r"super\s+fast",
    r"super\s+good",
]

NEGATIONS = {
    "not", "no", "never", "don't", "doesn't", "didn't",
    "isn't", "wasn't", "hardly", "barely", "neither", "nor",
    "cant", "cannot", "won't", "wouldn't", "shouldn't",
}


def _check_phrases(text: str):
    """Check for strong positive/negative phrases first."""
    text_lower = text.lower()
    neg_hits = sum(1 for p in STRONG_NEGATIVE_PHRASES if re.search(p, text_lower))
    pos_hits = sum(1 for p in STRONG_POSITIVE_PHRASES if re.search(p, text_lower))
    return pos_hits, neg_hits


def _rule_based_sentiment(text: str) -> Dict:
    text_lower = text.lower()

    # 1. Check strong phrases first — these are very reliable
    pos_phrase, neg_phrase = _check_phrases(text_lower)

    # 2. Token-level scoring with negation
    tokens = re.findall(r"\w+", text_lower)
    pos = neg = 0
    negate = False

    for i, tok in enumerate(tokens):
        if tok in NEGATIONS:
            negate = True
            continue
        if tok in POSITIVE_WORDS:
            if negate:
                neg += 2  # negated positive = stronger negative signal
            else:
                pos += 1
        elif tok in NEGATIVE_WORDS:
            if negate:
                pos += 1
            else:
                neg += 2  # negative words weighted higher
        # Reset negation after 2 tokens
        if negate and tok not in NEGATIONS:
            negate = False

    # 3. Combine phrase score + token score
    total_pos = pos + (pos_phrase * 3)
    total_neg = neg + (neg_phrase * 3)

    total = total_pos + total_neg or 1

    # 4. Decision with bias toward non-neutral
    # If any strong negative phrase found → definitely negative
    if neg_phrase > 0 and neg_phrase >= pos_phrase:
        score = min(0.95, 0.7 + (neg_phrase * 0.1))
        return {"label": "Negative", "score": round(score, 2)}

    # If any strong positive phrase found → definitely positive
    if pos_phrase > 0 and pos_phrase > neg_phrase:
        score = min(0.95, 0.7 + (pos_phrase * 0.1))
        return {"label": "Positive", "score": round(score, 2)}

    # Token-level decision
    if total_pos > total_neg:
        score = round(total_pos / total, 2)
        return {"label": "Positive", "score": min(score, 0.95)}
    elif total_neg > total_pos:
        score = round(total_neg / total, 2)
        return {"label": "Negative", "score": min(score, 0.95)}

    # Only mark Neutral if truly no signal
    return {"label": "Neutral", "score": 0.5}


def analyze_sentiment(texts: List[str], model_key: str = "xlm-roberta-base") -> List[Dict]:
    """
    Accurate rule-based sentiment analysis. No downloads needed.
    Returns list of {"label": "Positive"|"Negative"|"Neutral", "score": float}
    """
    return [_rule_based_sentiment(t) for t in texts]
