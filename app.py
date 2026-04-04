"""
Multi-Lingual Sentiment & Emotion Analyzer
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import markdown
from modules.scraper import scrape_reviews
from modules.preprocessor import preprocess_reviews
from modules.language_detector import detect_language
from modules.sentiment import analyze_sentiment
from modules.emotion import detect_emotions
from modules.summarizer import generate_summary

st.set_page_config(
    page_title="SentiLens · NLP Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── FULL CUSTOM CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&family=DM+Mono&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: #F5F2ED !important;
    font-family: 'DM Sans', sans-serif;
    color: #1a1a1a;
}

[data-testid="stAppViewContainer"] > .main {
    background-color: #F5F2ED !important;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { background: #EDE9E2 !important; }

.block-container {
    padding: 0 2rem 4rem 2rem !important;
    max-width: 1200px;
    margin: 0 auto;
}

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Navbar ── */
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.4rem 0 1rem 0;
    border-bottom: 1px solid #D9D4CB;
    margin-bottom: 3rem;
}
.navbar-brand {
    font-family: 'DM Mono', monospace;
    font-size: 1rem;
    color: #1a1a1a;
    letter-spacing: -0.02em;
}
.navbar-brand span { color: #4A7C6F; }
.navbar-links {
    display: flex;
    gap: 2rem;
    font-size: 0.85rem;
    color: #666;
    font-weight: 400;
}

/* ── Hero Section ── */
.hero {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4rem;
    align-items: center;
    padding: 2rem 0 4rem 0;
}
.hero-tag {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #4A7C6F;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.2rem;
}
.hero-tag::before {
    content: '';
    width: 2rem;
    height: 1.5px;
    background: #4A7C6F;
    display: inline-block;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.8rem;
    font-weight: 900;
    line-height: 1.05;
    color: #1a1a1a;
    margin-bottom: 0.2rem;
}
.hero-title-accent {
    font-family: 'Playfair Display', serif;
    font-size: 3.8rem;
    font-weight: 700;
    font-style: italic;
    color: #4A7C6F;
    line-height: 1.05;
    margin-bottom: 1.5rem;
    display: block;
}
.hero-sub {
    font-size: 0.95rem;
    color: #555;
    font-weight: 400;
    margin-bottom: 1.5rem;
    line-height: 1.7;
}
.lang-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 2rem;
}
.lang-tag {
    background: #EDE9E2;
    border: 1px solid #D9D4CB;
    border-radius: 100px;
    padding: 0.3rem 0.9rem;
    font-size: 0.78rem;
    color: #555;
    font-weight: 500;
}

/* ── Profile Card ── */
.profile-card {
    background: #fff;
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 2px 20px rgba(0,0,0,0.06);
}
.profile-card-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.2rem;
}
.profile-avatar {
    width: 52px;
    height: 52px;
    border-radius: 50%;
    background: linear-gradient(135deg, #C5D5CB, #A8C4BB);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'DM Mono', monospace;
    font-size: 0.85rem;
    color: #4A7C6F;
    font-weight: 600;
    flex-shrink: 0;
}
.profile-name {
    font-weight: 600;
    font-size: 1rem;
    color: #1a1a1a;
}
.profile-badge {
    display: inline-block;
    background: #EDF7F4;
    border: 1px solid #B8DDD5;
    color: #4A7C6F;
    font-size: 0.75rem;
    padding: 0.3rem 0.85rem;
    border-radius: 100px;
    font-family: 'DM Mono', monospace;
    margin-bottom: 1.2rem;
}
.profile-badge::before { content: '● '; font-size: 0.6rem; }
.stats-row {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 0.5rem;
    margin-bottom: 1.2rem;
}
.stat-box {
    background: #F9F7F4;
    border-radius: 10px;
    padding: 0.8rem 0.5rem;
    text-align: center;
}
.stat-num {
    font-weight: 700;
    font-size: 1.3rem;
    color: #1a1a1a;
}
.stat-label {
    font-size: 0.7rem;
    color: #888;
    margin-top: 0.1rem;
}
.skill-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
}
.skill-tag {
    background: #F0EDE8;
    border-radius: 100px;
    padding: 0.25rem 0.75rem;
    font-size: 0.75rem;
    color: #555;
    font-weight: 500;
}

/* ── Input Section ── */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #4A7C6F;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 0.5rem;
}
.section-sub {
    font-size: 0.88rem;
    color: #777;
    margin-bottom: 2rem;
}

/* ── Streamlit widget overrides ── */
.stTextArea textarea {
    background: #fff !important;
    border: 1.5px solid #D9D4CB !important;
    border-radius: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    color: #1a1a1a !important;
    padding: 1rem !important;
    transition: border-color 0.2s !important;
}
.stTextArea textarea:focus {
    border-color: #4A7C6F !important;
    box-shadow: 0 0 0 3px rgba(74,124,111,0.1) !important;
}

/* ── FIX 1: Textarea placeholder visible ── */
.stTextArea textarea::placeholder {
    color: #999 !important;
    opacity: 1 !important;
}

.stTextInput input {
    background: #FFFFFF !important;
    border: 1.5px solid #D9D4CB !important;
    border-radius: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.75rem 1rem !important;
    color: #1a1a1a !important;
    opacity: 1 !important;
}
.stTextInput input:focus {
    border-color: #4A7C6F !important;
    box-shadow: 0 0 0 3px rgba(74,124,111,0.1) !important;
}
.stTextInput input::placeholder {
    color: #888 !important;
    opacity: 1 !important;
}

/* ── Analyze + Download buttons — warm sage default, deeper teal on hover ── */
.stButton > button,
[data-testid="stDownloadButton"] > button {
    background: #5C8C7D !important;
    color: #F5F2ED !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.75rem 2rem !important;
    transition: all 0.2s !important;
    letter-spacing: 0.01em !important;
    cursor: pointer !important;
}
.stButton > button:hover,
[data-testid="stDownloadButton"] > button:hover {
    background: #3D6B5E !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(74,124,111,0.35) !important;
}

.stRadio > div { gap: 1rem !important; }

/* ── RADIO BUTTON FIX ── */
div[role="radiogroup"] {
    display: flex !important;
    gap: 14px !important;
    flex-wrap: wrap !important;
}
div[role="radiogroup"] label {
    background: #FFFFFF !important;
    border: 1.5px solid #D9D4CB !important;
    border-radius: 12px !important;
    padding: 10px 16px !important;
    min-height: 44px !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    color: #1a1a1a !important;
    opacity: 1 !important;
    cursor: pointer !important;
}
div[role="radiogroup"] label p {
    margin: 0 !important;
    color: #1a1a1a !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    opacity: 1 !important;
}
div[role="radiogroup"] input[type="radio"] {
    accent-color: #4A7C6F !important;
}

/* ── Multiselect Styling ── */
[data-baseweb="select"] > div {
    background: #F9F7F4 !important;
    border-radius: 10px !important;
    border: 1.5px solid #D9D4CB !important;
    min-height: 48px !important;
}
[data-baseweb="tag"] {
    background: #EDF7F4 !important;
    color: #4A7C6F !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
[data-baseweb="tag"] svg {
    color: #4A7C6F !important;
}
[data-baseweb="popover"] {
    background: #fff !important;
    border-radius: 10px !important;
}
[data-baseweb="menu"] {
    background: #fff !important;
}
[data-baseweb="menu"] div:hover {
    background: #EDF7F4 !important;
}

/* ── KPI Cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 2rem 0;
}
.kpi-card {
    background: #fff;
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    border: 1px solid #EDE9E2;
}
.kpi-card.total    { border-top: 3px solid #1a1a1a; }
.kpi-card.positive { border-top: 3px solid #4A7C6F; }
.kpi-card.negative { border-top: 3px solid #C4705A; }
.kpi-card.neutral  { border-top: 3px solid #C4A25A; }
.kpi-num {
    font-family: 'Playfair Display', serif;
    font-size: 2.5rem;
    font-weight: 700;
    color: #1a1a1a;
    line-height: 1;
}
.kpi-label {
    font-size: 0.78rem;
    color: #888;
    margin-top: 0.4rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ── Summary Card ── */
.summary-card {
    background: #fff;
    border-radius: 16px;
    padding: 1.2rem;
    border-left: 4px solid #4A7C6F;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    margin: 1.5rem 0;
}
.ai-summary-content {
    background: #EDF7F4;
    border-radius: 14px;
    padding: 1.3rem 1.4rem;
    color: #2f4f46;
}
.ai-summary-content h1,
.ai-summary-content h2,
.ai-summary-content h3,
.ai-summary-content h4 {
    font-size: 1.2rem;
    font-weight: 800;
    color: #4A7C6F;
    margin-top: 1.3rem;
    margin-bottom: 0.8rem;
    line-height: 1.35;
}
.ai-summary-content h1:first-child,
.ai-summary-content h2:first-child,
.ai-summary-content h3:first-child,
.ai-summary-content h4:first-child {
    margin-top: 0;
}
.ai-summary-content p {
    font-size: 1rem;
    line-height: 1.85;
    color: #2f4f46;
    margin-bottom: 1rem;
}
.ai-summary-content ul,
.ai-summary-content ol {
    margin: 0.4rem 0 1rem 1.6rem;
    padding-left: 1rem;
}
.ai-summary-content li {
    font-size: 1rem;
    line-height: 1.8;
    color: #2f4f46;
    margin-bottom: 0.45rem;
}
.ai-summary-content strong {
    font-weight: 800;
    color: #4A7C6F;
}
.ai-summary-content em { font-style: normal; }
.ai-summary-content code {
    background: rgba(74, 124, 111, 0.1);
    padding: 0.1rem 0.35rem;
    border-radius: 6px;
}
.ai-summary-content hr {
    border: none;
    border-top: 1px solid #CFE5DE;
    margin: 1rem 0;
}

/* ── Review Cards ── */
.review-card {
    background: #fff;
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    margin: 0.75rem 0;
    border: 1px solid #EDE9E2;
    box-shadow: 0 1px 6px rgba(0,0,0,0.04);
    transition: transform 0.15s;
}
.review-card:hover { transform: translateY(-2px); }
.review-card.positive { border-left: 4px solid #4A7C6F; }
.review-card.negative { border-left: 4px solid #C4705A; }
.review-card.neutral  { border-left: 4px solid #C4A25A; }

.review-meta {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-bottom: 0.6rem;
}
.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.2rem 0.7rem;
    border-radius: 100px;
    font-size: 0.72rem;
    font-weight: 600;
}
.badge.positive { background: #EDF7F4; color: #4A7C6F; }
.badge.negative { background: #FBF0ED; color: #C4705A; }
.badge.neutral  { background: #FBF6ED; color: #C4A25A; }
.badge.emotion  { background: #F0EDE8; color: #666; }
.badge.lang     { background: #F0EDE8; color: #888; }
.badge.conf     { background: #F0EDE8; color: #888; }

.review-text {
    font-size: 0.88rem;
    color: #444;
    line-height: 1.6;
}

/* ── Divider ── */
.soft-divider {
    height: 1px;
    background: #D9D4CB;
    margin: 2.5rem 0;
}

/* ── Info box override ── */
.stAlert {
    background: #fff !important;
    border: 1px solid #D9D4CB !important;
    border-radius: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── FIX FILE UPLOADER (REMOVE BLACK BAR) ── */

/* Outer container */
[data-testid="stFileUploader"] {
    background: transparent !important;
}

/* Main upload box */
[data-testid="stFileUploader"] section {
    background: #FFFFFF !important;
    border: 1.5px solid #D9D4CB !important;
    border-radius: 14px !important;
    padding: 0.8rem 1rem !important;
}

/* Dropzone (big black area) */
[data-testid="stFileUploaderDropzone"] {
    background: #FFFFFF !important;
    border: 2px dashed #D9D4CB !important;
    border-radius: 12px !important;
    padding: 1.2rem !important;
}



/* Force white again (important override) */
[data-testid="stFileUploaderDropzone"] {
    background-color: #FFFFFF !important;
}

/* Upload button inside */
[data-testid="stFileUploaderDropzone"] button {
    background: #EDF7F4 !important;
    color: #4A7C6F !important;
    border: 1px solid #B8DDD5 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

/* Hover */
[data-testid="stFileUploaderDropzone"] button:hover {
    background: #4A7C6F !important;
    color: white !important;
}

/* Text inside uploader */
[data-testid="stFileUploaderDropzone"] div {
    color: #555 !important;
}
</style>
""", unsafe_allow_html=True)

# ── NAVBAR ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
    <div class="navbar-brand">&lt;<span>sentilens</span>/&gt;</div>
    <div class="navbar-links">
        <span>Sentiment</span>
        <span>Emotions</span>
        <span>Languages</span>
        <span>Summary</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── HERO ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-left">
        <div class="hero-tag">NLP · Multilingual Analysis · Code-Mixed</div>
        <div class="hero-title">Sentiment</div>
        <span class="hero-title-accent">& Emotion Lens</span>
        <p class="hero-sub">
            Analyze reviews in English, Telugu, Hindi and code-mixed languages.<br>
            Detect sentiment, emotions, sarcasm and get detailed AI insights — instantly.
        </p>
        <div class="lang-tags">
            <span class="lang-tag">Speaks:</span>
            <span class="lang-tag">Telugu</span>
            <span class="lang-tag">English</span>
            <span class="lang-tag">Hindi</span>
            <span class="lang-tag">Code-Mixed</span>
        </div>
    </div>
    <div class="hero-right">
        <div class="profile-card">
            <div class="profile-card-header">
                <div class="profile-avatar">SN</div>
                <div>
                    <div class="profile-name">AI-Powered Sentiment Analysis System</div>
                </div>
            </div>
            <div class="profile-badge">Multilingual NLP • Emotion Detection • Code-Mixed Analysis</div>
            <div class="stats-row">
                <div class="stat-box"><div class="stat-num">3+</div><div class="stat-label">Modules</div></div>
                <div class="stat-box"><div class="stat-num">5</div><div class="stat-label">Emotions</div></div>
                <div class="stat-box"><div class="stat-num">10+</div><div class="stat-label">Languages</div></div>
            </div>
            <div class="skill-tags">
                <span class="skill-tag">Python</span>
                <span class="skill-tag">NLP</span>
                <span class="skill-tag">XLM-RoBERTa</span>
                <span class="skill-tag">mBERT</span>
                <span class="skill-tag">Streamlit</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)

# ── INPUT SECTION ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-label">Step 01</div>
<div class="section-title">Enter Your Reviews</div>
<div class="section-sub">Paste reviews, type them in, upload a file, or use a URL to fetch reviews automatically.</div>
""", unsafe_allow_html=True)

col_mode, _ = st.columns([3, 1])
with col_mode:
    input_mode = st.radio(
        "Input Mode",
        ["🔗 URL", "✏️ Type / Paste", "📂 Upload .txt"],
        horizontal=True,
        label_visibility="collapsed",
    )

reviews_input = []
platform_name = "Text Input"

if input_mode == "🔗 URL":
    url_input = st.text_input(
        "URL",
        placeholder="https://www.amazon.in/dp/...  or  https://www.youtube.com/watch?v=...",
        label_visibility="collapsed",
    )
    st.caption("💡 YouTube works best. Amazon/Flipkart may be blocked — falls back to demo data automatically.")

    if "url_reviews" in st.session_state and st.session_state.get("url_loaded"):
        reviews_input = st.session_state["url_reviews"]
        platform_name = st.session_state.get("url_platform", "URL")
        st.caption(f"✅ Loaded {len(reviews_input)} reviews from {platform_name}")

    if st.button("Fetch Reviews", key="fetch_btn"):
        if url_input.strip():
            with st.spinner("Fetching reviews…"):
                reviews_raw, plat = scrape_reviews(url_input.strip(), 50)
                st.session_state["url_reviews"] = reviews_raw
                st.session_state["url_platform"] = plat
                st.session_state["url_loaded"] = True
                reviews_input = reviews_raw
                platform_name = plat
                st.caption(f"✅ Fetched {len(reviews_raw)} reviews from {plat}")

elif input_mode == "✏️ Type / Paste":
    text_input = st.text_area(
        "Reviews",
        height=180,
        placeholder="Enter one review per line...\n\nThis product is amazing!\nchala bagundi, delivery fast ga vachindi\nTerrible quality, waste of money\nNot working at all very disappointed",
        label_visibility="collapsed",
    )
    if text_input.strip():
        reviews_input = [
            {"text": line.strip(), "rating": None, "timestamp": None}
            for line in text_input.strip().split("\n")
            if line.strip()
        ]
        st.caption(f"📋 {len(reviews_input)} review(s) ready")

else:
    uploaded = st.file_uploader("Upload .txt file", type=["txt"], label_visibility="collapsed")
    if uploaded:
        content = uploaded.read().decode("utf-8")
        reviews_input = [
            {"text": line.strip(), "rating": None, "timestamp": None}
            for line in content.strip().split("\n")
            if line.strip()
        ]
        st.caption(f"✅ Loaded {len(reviews_input)} reviews from file")

st.markdown("<br>", unsafe_allow_html=True)
analyze_btn = st.button("🔍 Analyze Reviews", type="primary", use_container_width=False)

# ── ANALYSIS ────────────────────────────────────────────────────────────────────
if analyze_btn:
    if not reviews_input:
        st.warning("Please enter at least one review before analyzing.")
        st.stop()

    with st.status("Analyzing…", expanded=True) as status:
        st.write(f"Processing **{len(reviews_input)}** reviews…")

        reviews_clean = preprocess_reviews(reviews_input)
        if not reviews_clean:
            reviews_clean = reviews_input

        texts = [r["text"] for r in reviews_clean]

        st.write("Detecting languages…")
        lang_labels = [detect_language(text) for text in texts]

        st.write("Running sentiment analysis…")
        sentiments = analyze_sentiment(texts)

        st.write("Detecting emotions…")
        emotions = detect_emotions(texts)

        st.write("Generating summary…")
        summary = generate_summary(
            sentiments,
            emotions,
            {
                "price": {"positive": 0, "negative": 0, "neutral": 1},
                "quality": {"positive": 0, "negative": 0, "neutral": 1},
                "delivery": {"positive": 0, "negative": 0, "neutral": 1},
            },
            platform_name,
            texts=texts,
            languages=lang_labels,
        )

        status.update(label="✅ Analysis complete!", state="complete")

    df = pd.DataFrame(reviews_clean)
    df["language"] = lang_labels
    df["sentiment"] = [s["label"] for s in sentiments]
    df["confidence"] = [round(s["score"] * 100, 1) for s in sentiments]
    df["emotion"] = [e["label"] for e in emotions]

    total = len(df)
    pos_pct = round(len(df[df.sentiment == "Positive"]) / total * 100) if total > 0 else 0
    neg_pct = round(len(df[df.sentiment == "Negative"]) / total * 100) if total > 0 else 0
    neu_pct = 100 - pos_pct - neg_pct

    st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)

    # ── KPI ─────────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-label">Step 02</div>
    <div class="section-title">Overview</div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card total">
            <div class="kpi-num">{total}</div>
            <div class="kpi-label">Total Reviews</div>
        </div>
        <div class="kpi-card positive">
            <div class="kpi-num">{pos_pct}%</div>
            <div class="kpi-label">Positive</div>
        </div>
        <div class="kpi-card negative">
            <div class="kpi-num">{neg_pct}%</div>
            <div class="kpi-label">Negative</div>
        </div>
        <div class="kpi-card neutral">
            <div class="kpi-num">{neu_pct}%</div>
            <div class="kpi-label">Neutral</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)

    # ── CHARTS ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-label">Step 03</div>
    <div class="section-title">Visual Insights</div>
    """, unsafe_allow_html=True)

    BG_CARD = "#FFFFFF"
    GRID    = "#E8E3DA"
    TEXT    = "#2F3E39"
    SUBTLE  = "#6B7C76"

    sentiment_colors = {
        "Positive": "#4A7C6F",
        "Negative": "#C4705A",
        "Neutral":  "#C4A25A"
    }
    emotion_color_map = {
        "Joy":      "#4A7C6F",
        "Anger":    "#C4705A",
        "Sadness":  "#7C8FA6",
        "Surprise": "#A67C6F",
        "Sarcasm":  "#6F7CA6",
        "Neutral":  "#C4A25A"
    }

    sent_counts = df["sentiment"].value_counts().reset_index()
    sent_counts.columns = ["Sentiment", "Count"]

    emo_counts = df["emotion"].value_counts().reset_index()
    emo_counts.columns = ["Emotion", "Count"]

    lang_counts = df["language"].value_counts().reset_index()
    lang_counts.columns = ["Language", "Count"]

    col1, col2 = st.columns(2)

    with col1:
        fig_pie = px.pie(
            sent_counts,
            names="Sentiment",
            values="Count",
            hole=0.58,
            color="Sentiment",
            color_discrete_map=sentiment_colors,
        )
        fig_pie.update_traces(
            textinfo="percent+label",
            textfont_size=14,
            marker=dict(line=dict(color=BG_CARD, width=4)),
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>"
        )
        fig_pie.update_layout(
            title=dict(text="Sentiment Distribution", x=0.02, xanchor="left", font=dict(size=18, color=TEXT)),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans", color=TEXT),
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center", font=dict(size=12, color=SUBTLE)),
            margin=dict(t=60, b=60, l=20, r=20),
            height=380
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        fig_emo = px.bar(
            emo_counts,
            x="Emotion",
            y="Count",
            color="Emotion",
            color_discrete_map=emotion_color_map,
            text="Count"
        )
        fig_emo.update_traces(
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>"
        )
        fig_emo.update_layout(
            title=dict(text="Emotion Distribution", x=0.02, xanchor="left", font=dict(size=18, color=TEXT)),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor=BG_CARD,
            font=dict(family="DM Sans", color=TEXT),
            showlegend=False,
            margin=dict(t=60, b=40, l=40, r=20),
            height=380,
            xaxis=dict(title="Emotion", title_font=dict(color=SUBTLE), tickfont=dict(color=TEXT), showgrid=False, zeroline=False),
            yaxis=dict(title="Count",   title_font=dict(color=SUBTLE), tickfont=dict(color=TEXT), gridcolor=GRID, zeroline=False)
        )
        st.plotly_chart(fig_emo, use_container_width=True)

    fig_lang = px.bar(
        lang_counts,
        x="Language",
        y="Count",
        color="Language",
        text="Count",
        color_discrete_sequence=["#8EACA3", "#4A7C6F", "#C5D5CB", "#A8C4BB"]
    )
    fig_lang.update_traces(
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>"
    )
    fig_lang.update_layout(
        title=dict(text="Language Distribution", x=0.02, xanchor="left", font=dict(size=18, color=TEXT)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=BG_CARD,
        font=dict(family="DM Sans", color=TEXT),
        showlegend=False,
        margin=dict(t=60, b=40, l=40, r=20),
        height=360,
        xaxis=dict(title="Language", title_font=dict(color=SUBTLE), tickfont=dict(color=TEXT), showgrid=False, zeroline=False),
        yaxis=dict(title="Count",    title_font=dict(color=SUBTLE), tickfont=dict(color=TEXT), gridcolor=GRID, zeroline=False)
    )
    st.plotly_chart(fig_lang, use_container_width=True)

    st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)

    # ── SUMMARY ─────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-label">Step 04</div>
    <div class="section-title">AI Summary</div>
    """, unsafe_allow_html=True)

    html_summary = markdown.markdown(summary, extensions=["extra", "sane_lists"])

    st.markdown(f"""
    <div class="summary-card">
        <div class="ai-summary-content">
            {html_summary}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)

    # ── REVIEW CARDS ────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-label">Step 05</div>
    <div class="section-title">Review Results</div>
    """, unsafe_allow_html=True)

    filter_col, _ = st.columns([2, 3])
    with filter_col:
        filter_sent = st.multiselect(
            "Filter by Sentiment",
            ["Positive", "Negative", "Neutral"],
            default=["Positive", "Negative", "Neutral"],
        )

    filtered = df[df["sentiment"].isin(filter_sent)]

    for _, row in filtered.iterrows():
        css_cls = row["sentiment"].lower()
        s_emoji = {"Positive": "😊", "Negative": "😞", "Neutral": "😐"}.get(row["sentiment"], "")
        e_emoji = {
            "Joy": "😄", "Anger": "😠", "Sadness": "😢",
            "Surprise": "😲", "Sarcasm": "🙄", "Neutral": "😐"
        }.get(row["emotion"], "")

        st.markdown(f"""
        <div class="review-card {css_cls}">
            <div class="review-meta">
                <span class="badge {css_cls}">{s_emoji} {row['sentiment']}</span>
                <span class="badge emotion">{e_emoji} {row['emotion']}</span>
                <span class="badge lang">🌐 {row['language']}</span>
                <span class="badge conf">🎯 {row['confidence']}%</span>
            </div>
            <div class="review-text">{row['text']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)

    # ── DOWNLOAD ────────────────────────────────────────────────────────────────
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Results as CSV",
        csv,
        "sentiment_results.csv",
        "text/csv",
    )
