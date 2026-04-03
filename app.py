"""
Multi-Lingual Sentiment & Emotion Analyzer
Streamlit Frontend — Final Version with URL + Text Input
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from modules.scraper import scrape_reviews
from modules.preprocessor import preprocess_reviews
from modules.language_detector import detect_language
from modules.sentiment import analyze_sentiment
from modules.emotion import detect_emotions
from modules.summarizer import generate_summary

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Lingual Sentiment & Emotion Analyzer",
    page_icon="🧠",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px; border-radius: 12px; color: white; text-align: center;
        margin: 8px 0;
    }
    .metric-card h2 { margin: 0; font-size: 2em; }
    .metric-card p  { margin: 0; font-size: 0.9em; opacity: 0.85; }
    .review-card {
        border-left: 4px solid #667eea; background: #f8f9fa;
        padding: 12px 16px; border-radius: 6px; margin: 8px 0;
    }
    .positive { border-color: #28a745; }
    .negative { border-color: #dc3545; }
    .neutral  { border-color: #ffc107; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🧠 Multi-Lingual Sentiment & Emotion Analyzer")
st.markdown("*Supports English, Telugu, Hindi and Code-Mixed languages*")
st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Options")
    max_reviews = st.slider("Max Reviews to Fetch (URL mode)", 10, 100, 30, step=10)
    show_raw = st.checkbox("Show Raw Data Table", value=False)
    st.divider()
    st.markdown("**Supported Platforms**")
    st.markdown("• 🛒 Amazon\n• 🛒 Flipkart\n• 📺 YouTube")
    st.divider()
    st.markdown("**Supported Languages**")
    st.markdown("• English\n• Telugu\n• Telugu + English (Code-Mixed)\n• Hindi\n• Tamil\n• And more…")
    st.divider()
    st.markdown("**Detected Emotions**")
    st.markdown("• 😄 Joy\n• 😠 Anger\n• 😢 Sadness\n• 😲 Surprise\n• 🙄 Sarcasm\n• 😐 Neutral")

# ── Input Mode ────────────────────────────────────────────────────────────────
st.subheader("📝 Input")
input_mode = st.radio(
    "Choose Input Mode",
    ["🔗 URL (Amazon / Flipkart / YouTube)", "✏️ Type / Paste Reviews", "📂 Upload .txt File"],
    horizontal=True,
)

reviews_input = []
platform_name = "Text Input"

# ── URL Mode ──────────────────────────────────────────────────────────────────
if input_mode == "🔗 URL (Amazon / Flipkart / YouTube)":
    url = st.text_input(
        "Enter URL",
        placeholder="https://www.amazon.in/dp/...  or  https://www.youtube.com/watch?v=...",
    )
    st.caption("💡 Tip: YouTube URLs work best. Amazon/Flipkart may be blocked — will auto fallback to demo data.")

    if url.strip():
        if st.button("🚀 Fetch & Analyze", type="primary", use_container_width=True):
            with st.spinner("Fetching reviews from URL…"):
                reviews_raw, platform_name = scrape_reviews(url.strip(), max_reviews)
                reviews_input = reviews_raw
                st.session_state["reviews_input"]  = reviews_input
                st.session_state["platform_name"]  = platform_name
                st.session_state["trigger_analyze"] = True
    else:
        st.button("🚀 Fetch & Analyze", type="primary", use_container_width=True, disabled=True)

# ── Text Mode ─────────────────────────────────────────────────────────────────
elif input_mode == "✏️ Type / Paste Reviews":
    st.markdown("Enter one review per line:")
    text_input = st.text_area(
        "Reviews",
        height=200,
        placeholder="This product is amazing!\nchala bagundi, delivery fast ga vachindi\nTerrible quality, waste of money\nNot working at all very disappointed",
    )
    if text_input.strip():
        reviews_input = [
            {"text": line.strip(), "rating": None, "timestamp": None}
            for line in text_input.strip().split("\n")
            if line.strip()
        ]
        st.caption(f"📋 {len(reviews_input)} review(s) ready to analyze")

    if st.button("🚀 Analyze", type="primary", use_container_width=True):
        st.session_state["reviews_input"]   = reviews_input
        st.session_state["platform_name"]   = "Text Input"
        st.session_state["trigger_analyze"] = True

# ── File Upload Mode ──────────────────────────────────────────────────────────
else:
    uploaded_file = st.file_uploader("Upload a .txt file (one review per line)", type=["txt"])
    if uploaded_file:
        content = uploaded_file.read().decode("utf-8")
        reviews_input = [
            {"text": line.strip(), "rating": None, "timestamp": None}
            for line in content.strip().split("\n")
            if line.strip()
        ]
        st.success(f"✅ Loaded {len(reviews_input)} reviews from file")

    if st.button("🚀 Analyze", type="primary", use_container_width=True):
        st.session_state["reviews_input"]   = reviews_input
        st.session_state["platform_name"]   = "File Upload"
        st.session_state["trigger_analyze"] = True

# ── Analysis Pipeline ─────────────────────────────────────────────────────────
if st.session_state.get("trigger_analyze"):
    st.session_state["trigger_analyze"] = False
    reviews_input = st.session_state.get("reviews_input", [])
    platform_name = st.session_state.get("platform_name", "Text Input")

    if not reviews_input:
        st.warning("No reviews found. Please enter reviews or a valid URL.")
        st.stop()

    with st.status("🔍 Analyzing reviews…", expanded=True) as status:
        st.write(f"Processing **{len(reviews_input)}** reviews from **{platform_name}**…")

        # Preprocess
        reviews_clean = preprocess_reviews(reviews_input)
        if not reviews_clean:
            reviews_clean = reviews_input  # fallback to raw

        texts = [r["text"] for r in reviews_clean]

        # Language detection
        st.write("Detecting languages…")
        lang_labels = [detect_language(t) for t in texts]

        # Sentiment
        st.write("Running sentiment analysis…")
        sentiments = analyze_sentiment(texts)

        # Emotion
        st.write("Detecting emotions…")
        emotions = detect_emotions(texts)

        # Summary
        st.write("Generating summary…")
        summary = generate_summary(
            sentiments, emotions,
            {"price":    {"positive": 0, "negative": 0, "neutral": 1},
             "quality":  {"positive": 0, "negative": 0, "neutral": 1},
             "delivery": {"positive": 0, "negative": 0, "neutral": 1}},
            platform_name,
            texts=texts,
            languages=lang_labels,
        )

        status.update(label="✅ Analysis complete!", state="complete")

    # ── Build DataFrame ───────────────────────────────────────────────────────
    df = pd.DataFrame(reviews_clean)
    df["language"]   = lang_labels
    df["sentiment"]  = [s["label"] for s in sentiments]
    df["confidence"] = [round(s["score"] * 100, 1) for s in sentiments]
    df["emotion"]    = [e["label"] for e in emotions]

    total   = len(df)
    pos_pct = round(len(df[df.sentiment == "Positive"]) / total * 100) if total > 0 else 0
    neg_pct = round(len(df[df.sentiment == "Negative"]) / total * 100) if total > 0 else 0
    neu_pct = 100 - pos_pct - neg_pct

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("📊 Overview")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <p>Total Reviews</p><h2>{total}</h2></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card" style="background:linear-gradient(135deg,#28a745,#20c997)">
            <p>Positive</p><h2>{pos_pct}%</h2></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card" style="background:linear-gradient(135deg,#dc3545,#fd7e14)">
            <p>Negative</p><h2>{neg_pct}%</h2></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card" style="background:linear-gradient(135deg,#ffc107,#fd7e14)">
            <p>Neutral</p><h2>{neu_pct}%</h2></div>""", unsafe_allow_html=True)

    st.divider()

    # ── Summary ───────────────────────────────────────────────────────────────
    st.subheader("📝 Summary")
    st.info(summary)

    st.divider()

    # ── Charts ────────────────────────────────────────────────────────────────
    st.subheader("📈 Visual Insights")
    col1, col2 = st.columns(2)

    with col1:
        sent_counts = df["sentiment"].value_counts().reset_index()
        sent_counts.columns = ["Sentiment", "Count"]
        fig_pie = px.pie(
            sent_counts, names="Sentiment", values="Count",
            title="Sentiment Distribution",
            color="Sentiment",
            color_discrete_map={"Positive": "#28a745", "Negative": "#dc3545", "Neutral": "#ffc107"},
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        emo_counts = df["emotion"].value_counts().reset_index()
        emo_counts.columns = ["Emotion", "Count"]
        fig_bar = px.bar(
            emo_counts, x="Emotion", y="Count",
            title="Emotion Distribution",
            color="Emotion",
            color_discrete_sequence=px.colors.qualitative.Vivid,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    lang_counts = df["language"].value_counts().reset_index()
    lang_counts.columns = ["Language", "Count"]
    fig_lang = px.bar(
        lang_counts, x="Language", y="Count",
        title="Language Distribution",
        color="Count",
        color_continuous_scale="Viridis",
    )
    st.plotly_chart(fig_lang, use_container_width=True)

    st.divider()

    # ── Review Cards ──────────────────────────────────────────────────────────
    st.subheader("💬 Review Results")
    filter_sent = st.multiselect(
        "Filter by Sentiment",
        ["Positive", "Negative", "Neutral"],
        default=["Positive", "Negative", "Neutral"],
    )
    filtered = df[df["sentiment"].isin(filter_sent)]

    for _, row in filtered.iterrows():
        css_cls         = row["sentiment"].lower()
        sentiment_emoji = {"Positive": "😊", "Negative": "😞", "Neutral": "😐"}.get(row["sentiment"], "")
        emotion_emoji   = {
            "Joy": "😄", "Anger": "😠", "Sadness": "😢",
            "Surprise": "😲", "Sarcasm": "🙄", "Neutral": "😐",
        }.get(row["emotion"], "")
        st.markdown(f"""
        <div class="review-card {css_cls}">
            <strong>{sentiment_emoji} {row['sentiment']}</strong> &nbsp;|&nbsp;
            {emotion_emoji} {row['emotion']} &nbsp;|&nbsp;
            🌐 {row['language']} &nbsp;|&nbsp;
            🎯 {row['confidence']}% confidence
            <br><br>{row['text']}
        </div>
        """, unsafe_allow_html=True)

    if show_raw:
        st.subheader("📋 Raw Data")
        st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Results as CSV", csv, "sentiment_results.csv", "text/csv")