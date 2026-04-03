"""
Module 8: Summary Generation
Produces a detailed summary including:
- Overall sentiment breakdown
- Emotion analysis
- Sarcasm detection
- Analysis reliability
- Key takeaway
- Plain English meaning of each comment
"""

from typing import List, Dict
from collections import Counter
import re


def _explain_comment(text: str, sentiment: str, emotion: str, language: str) -> str:
    """Generate a plain English explanation of what a comment means."""

    text_lower = text.lower()

    # Sentiment phrase
    sentiment_phrase = {
        "Positive": "This is a positive comment",
        "Negative": "This is a negative comment",
        "Neutral":  "This is a neutral comment",
    }.get(sentiment, "This comment")

    # Emotion phrase
    emotion_phrase = {
        "Joy":      "The reviewer is happy and satisfied",
        "Anger":    "The reviewer is angry or strongly frustrated",
        "Sadness":  "The reviewer is disappointed or sad",
        "Surprise": "The reviewer is surprised — either pleasantly or unpleasantly",
        "Sarcasm":  "The reviewer is being sarcastic — positive words may actually mean the opposite",
        "Neutral":  "The reviewer expresses no strong emotion",
    }.get(emotion, "")

    # Language note
    lang_note = ""
    if "code-mixed" in language.lower() or "+" in language:
        lang_note = f"Written in {language}, mixing two languages in the same sentence. "

    # Content meaning
    meaning = ""

    # Negative patterns
    if sentiment == "Negative":
        if re.search(r"not\s+working|doesn'?t\s+work|stop\w*\s+work", text_lower):
            meaning = "The reviewer is saying the product does not work or stopped functioning."
        elif re.search(r"fake|fraud|scam|cheat", text_lower):
            meaning = "The reviewer is accusing the product or seller of being fake or fraudulent."
        elif re.search(r"late|delay|never\s+arriv|not\s+arriv", text_lower):
            meaning = "The reviewer is complaining about late or missing delivery."
        elif re.search(r"broke|broken|damage|defect|fault", text_lower):
            meaning = "The reviewer received a broken or defective product."
        elif re.search(r"waste|not\s+worth|overpriced|expensive", text_lower):
            meaning = "The reviewer feels the product is not worth the money spent."
        elif re.search(r"wrong|incorrect|not\s+as\s+describ|different", text_lower):
            meaning = "The reviewer received the wrong or a different product than expected."
        elif re.search(r"disappoint|expect\w+\s+better|expected\s+more", text_lower):
            meaning = "The reviewer expected better quality but was let down."
        else:
            meaning = "The reviewer is expressing general dissatisfaction with the product or experience."

    # Positive patterns
    elif sentiment == "Positive":
        if re.search(r"fast|quick|speed|on\s+time|early", text_lower):
            meaning = "The reviewer is happy about the fast delivery or quick service."
        elif re.search(r"quality|build|material|premium|solid|durable", text_lower):
            meaning = "The reviewer is impressed with the quality and build of the product."
        elif re.search(r"price|value|worth|affordable|cheap|reasonable", text_lower):
            meaning = "The reviewer finds the product to be good value for money."
        elif re.search(r"bagundi|chala|super", text_lower):
            meaning = "The reviewer is saying the product is very good (expressed in Telugu)."
        elif re.search(r"recommend|must\s+buy|buy\s+again|will\s+buy", text_lower):
            meaning = "The reviewer is recommending this product to others."
        elif re.search(r"exact|original|genuine|authentic", text_lower):
            meaning = "The reviewer confirms the product is genuine and as described."
        else:
            meaning = "The reviewer is expressing general satisfaction and happiness with the product."

    # Neutral patterns
    else:
        if re.search(r"average|okay|ok|decent|fine|alright", text_lower):
            meaning = "The reviewer finds the product average — not great, not bad."
        elif re.search(r"nothing\s+special|does\s+the\s+job|works", text_lower):
            meaning = "The reviewer says the product works but is nothing extraordinary."
        else:
            meaning = "The reviewer is stating a fact without expressing a strong positive or negative opinion."

    # Sarcasm override
    if emotion == "Sarcasm":
        meaning = (
            "⚠️ This comment appears sarcastic. "
            "The reviewer may be using positive words to actually express strong dissatisfaction. "
            "Read carefully — the true meaning is likely negative."
        )

    return f"{lang_note}{sentiment_phrase}. {emotion_phrase}. {meaning}"


def generate_summary(
    sentiments: List[Dict],
    emotions: List[Dict],
    aspects: Dict,
    platform: str,
    texts: List[str] = None,
    languages: List[str] = None,
) -> str:
    total = len(sentiments)
    if total == 0:
        return "No reviews were analysed."

    # ── Sentiment breakdown ───────────────────────────────────────────────────
    sent_counter = Counter(s["label"] for s in sentiments)
    pos = sent_counter["Positive"]
    neg = sent_counter["Negative"]
    neu = sent_counter["Neutral"]
    pos_pct = round(pos / total * 100)
    neg_pct = round(neg / total * 100)
    neu_pct = round(neu / total * 100)

    # ── Emotion breakdown ─────────────────────────────────────────────────────
    emo_counter      = Counter(e["label"] for e in emotions)
    dominant_emotion = emo_counter.most_common(1)[0][0] if emo_counter else "Neutral"
    sarcasm_count    = emo_counter.get("Sarcasm", 0)
    joy_count        = emo_counter.get("Joy", 0)
    anger_count      = emo_counter.get("Anger", 0)
    sadness_count    = emo_counter.get("Sadness", 0)
    surprise_count   = emo_counter.get("Surprise", 0)

    # ── Confidence ────────────────────────────────────────────────────────────
    avg_confidence = round(sum(s["score"] for s in sentiments) / total * 100, 1)
    high_conf      = sum(1 for s in sentiments if s["score"] >= 0.75)
    low_conf       = sum(1 for s in sentiments if s["score"] < 0.55)

    # ── Overall verdict ───────────────────────────────────────────────────────
    if pos_pct >= 70:
        verdict = "overwhelmingly positive"
    elif pos_pct >= 55:
        verdict = "mostly positive"
    elif neg_pct >= 60:
        verdict = "predominantly negative"
    elif neg_pct >= 40:
        verdict = "mixed to negative"
    elif neu_pct >= 50:
        verdict = "largely neutral"
    else:
        verdict = "mixed"

    lines = []

    # ── Section 1: Overview ───────────────────────────────────────────────────
    lines.append("### 📊 Overall Analysis")
    lines.append(
        f"A total of **{total} reviews** were analysed. "
        f"The overall sentiment is **{verdict}** — "
        f"**{pos_pct}% Positive**, **{neg_pct}% Negative**, and **{neu_pct}% Neutral**."
    )

    # ── Section 2: Sentiment detail ───────────────────────────────────────────
    lines.append("\n### 😊 Sentiment Insights")
    if pos > neg:
        lines.append(
            f"The majority of reviews (**{pos} out of {total}**) express a positive opinion. "
            f"This suggests that most reviewers are satisfied overall."
        )
    elif neg > pos:
        lines.append(
            f"A significant portion of reviews (**{neg} out of {total}**) are negative. "
            f"This indicates dissatisfaction among a large group of reviewers."
        )
    else:
        lines.append(
            f"Positive and negative reviews are nearly equal (**{pos} positive, {neg} negative**), "
            f"indicating divided opinions."
        )
    if neu > 0:
        lines.append(f"**{neu} neutral** reviews were detected — these are factual or indecisive in tone.")

    # ── Section 3: Emotion detail ─────────────────────────────────────────────
    lines.append("\n### 💬 Emotion Insights")
    lines.append(f"The dominant emotion across all reviews is **{dominant_emotion}**.")
    emotion_details = []
    if joy_count:
        emotion_details.append(f"**{joy_count} reviews** express **Joy** — showing happiness and satisfaction")
    if anger_count:
        emotion_details.append(f"**{anger_count} reviews** express **Anger** — indicating strong frustration")
    if sadness_count:
        emotion_details.append(f"**{sadness_count} reviews** express **Sadness** — reflecting disappointment")
    if surprise_count:
        emotion_details.append(f"**{surprise_count} reviews** express **Surprise** — either positively or negatively")
    if emotion_details:
        lines.append("\n".join(f"- {d}" for d in emotion_details))

    # ── Section 4: Sarcasm ────────────────────────────────────────────────────
    if sarcasm_count > 0:
        sarcasm_pct = round(sarcasm_count / total * 100)
        lines.append("\n### 🙄 Sarcasm Detection")
        lines.append(
            f"**{sarcasm_count} reviews ({sarcasm_pct}%)** appear to be **sarcastic**. "
            f"These reviews use positive words but carry a negative meaning. "
            f"Interpret their sentiment carefully."
        )

    # ── Section 5: Reliability ────────────────────────────────────────────────
    lines.append("\n### 🎯 Analysis Reliability")
    lines.append(
        f"Average confidence: **{avg_confidence}%**. "
        f"**{high_conf} reviews** classified with high confidence (≥75%). "
        f"**{low_conf} reviews** had lower confidence (<55%) and may need manual review."
    )

    # ── Section 6: Key takeaway ───────────────────────────────────────────────
    lines.append("\n### 💡 Key Takeaway")
    if pos_pct >= 60 and sarcasm_count == 0:
        lines.append(
            "The reviews are largely genuine and positive. "
            "The feedback reflects strong satisfaction with minimal negative experiences."
        )
    elif neg_pct >= 50:
        lines.append(
            "The reviews reveal significant dissatisfaction. "
            "Recurring negative emotions suggest serious issues that need attention."
        )
    elif sarcasm_count >= total * 0.2:
        lines.append(
            "A notable level of sarcasm was detected. "
            "Surface-level positive language may mask underlying negative opinions."
        )
    else:
        lines.append(
            "The reviews show a mixed response. "
            "While some reviewers are satisfied, others express concern — indicating an inconsistent experience."
        )

    # ── Section 7: Comment-by-comment meaning ────────────────────────────────
    if texts and languages:
        lines.append("\n### 🔍 What Each Comment Means")
        for i, (text, sent, emo, lang) in enumerate(
            zip(texts, sentiments, emotions, languages), 1
        ):
            explanation = _explain_comment(
                text, sent["label"], emo["label"], lang
            )
            sentiment_emoji = {"Positive": "😊", "Negative": "😞", "Neutral": "😐"}.get(sent["label"], "")
            lines.append(
                f"**{i}. {sentiment_emoji} \"{text[:80]}{'...' if len(text) > 80 else ''}\"**\n"
                f"→ {explanation}"
            )

    return "\n\n".join(lines)
