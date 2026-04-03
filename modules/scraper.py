"""
Module 2: Data Extraction
Scrapes reviews from Amazon, Flipkart, and YouTube.
"""

import re
import time
import random
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple

HEADERS_LIST = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.google.com/",
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
        "Accept-Language": "en-GB,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.google.co.in/",
    },
    {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "en-IN,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.amazon.in/",
    },
]

DEMO_REVIEWS = [
    {"text": "Absolutely love this product! The quality is outstanding and delivery was super fast.", "rating": 5, "timestamp": "2024-01-01"},
    {"text": "Worst purchase ever. Broke after 2 days. Total waste of money.", "rating": 1, "timestamp": "2024-01-02"},
    {"text": "Average product. Nothing special but does the job.", "rating": 3, "timestamp": "2024-01-03"},
    {"text": "chala bagundi! delivery kuda fast ga vachindi. price kuda reasonable ga undi.", "rating": 5, "timestamp": "2024-01-04"},
    {"text": "Oh great, the package arrived damaged. So helpful indeed. NOT.", "rating": 1, "timestamp": "2024-01-05"},
    {"text": "Very happy with the purchase. Excellent build quality and worth every rupee.", "rating": 5, "timestamp": "2024-01-06"},
    {"text": "Product looks cheap and flimsy. Not worth the price at all.", "rating": 2, "timestamp": "2024-01-07"},
    {"text": "Delivery was delayed by 5 days. Customer support did not help either.", "rating": 2, "timestamp": "2024-01-08"},
    {"text": "Amazing product! Exceeded my expectations. Will definitely buy again.", "rating": 5, "timestamp": "2024-01-09"},
    {"text": "idi chinda product. paise waste chesanu. never buying again.", "rating": 1, "timestamp": "2024-01-10"},
    {"text": "Good value for money. Packaging was nice and product works well.", "rating": 4, "timestamp": "2024-01-11"},
    {"text": "Yeah right, the best product ever said no one. Totally disappointed.", "rating": 1, "timestamp": "2024-01-12"},
    {"text": "Superb quality! The material feels premium and looks exactly like the photos.", "rating": 5, "timestamp": "2024-01-13"},
    {"text": "Okay product. Price is a bit high for what you get.", "rating": 3, "timestamp": "2024-01-14"},
    {"text": "Fast shipping and well packaged. Product quality is decent.", "rating": 4, "timestamp": "2024-01-15"},
    {"text": "Stopped working after a week. Very disappointed with the quality.", "rating": 1, "timestamp": "2024-01-16"},
    {"text": "Best product in this price range. Highly recommend to everyone!", "rating": 5, "timestamp": "2024-01-17"},
    {"text": "Not as described. Color is different and size is wrong.", "rating": 2, "timestamp": "2024-01-18"},
    {"text": "Happy with the purchase overall. Minor issues but nothing major.", "rating": 4, "timestamp": "2024-01-19"},
    {"text": "Product is genuine and works perfectly. Great deal!", "rating": 5, "timestamp": "2024-01-20"},
    {"text": "Terrible customer service. Product is bad and return process is painful.", "rating": 1, "timestamp": "2024-01-21"},
    {"text": "Nice product, arrived on time. Would buy again.", "rating": 4, "timestamp": "2024-01-22"},
    {"text": "Overpriced for the quality. Can find better options elsewhere.", "rating": 2, "timestamp": "2024-01-23"},
    {"text": "Excellent! Fast delivery, great quality, perfect packaging. 10/10!", "rating": 5, "timestamp": "2024-01-24"},
    {"text": "So sad, the product I received was completely different from what was shown.", "rating": 1, "timestamp": "2024-01-25"},
    {"text": "Decent product for daily use. Not the best but affordable.", "rating": 3, "timestamp": "2024-01-26"},
    {"text": "Very angry about the delivery. Took 15 days and arrived broken.", "rating": 1, "timestamp": "2024-01-27"},
    {"text": "Surprised by the quality! Did not expect it to be this good at this price.", "rating": 5, "timestamp": "2024-01-28"},
    {"text": "Works as expected. Nothing extraordinary but does the job fine.", "rating": 3, "timestamp": "2024-01-29"},
    {"text": "Good product, fast delivery. Very satisfied with the purchase.", "rating": 5, "timestamp": "2024-01-30"},
]


def detect_platform(url: str) -> str:
    u = url.lower().strip()
    if u == "demo":
        return "Demo"
    if "amazon" in u:
        return "Amazon"
    if "flipkart" in u:
        return "Flipkart"
    if "youtube.com" in u or "youtu.be" in u:
        return "YouTube"
    return "Unknown"


def scrape_reviews(url: str, max_reviews: int = 50) -> Tuple[List[Dict], str]:
    platform = detect_platform(url.strip())

    if platform == "Demo" or platform == "Unknown":
        return DEMO_REVIEWS[:max_reviews], "Demo"

    if platform == "Amazon":
        reviews = _scrape_amazon(url, max_reviews)
        if reviews:
            return reviews, "Amazon"
        return DEMO_REVIEWS[:max_reviews], "Demo (Amazon blocked scraper — showing sample data)"

    if platform == "Flipkart":
        reviews = _scrape_flipkart(url, max_reviews)
        if reviews:
            return reviews, "Flipkart"
        return DEMO_REVIEWS[:max_reviews], "Demo (Flipkart blocked scraper — showing sample data)"

    if platform == "YouTube":
        reviews = _scrape_youtube(url, max_reviews)
        if reviews:
            return reviews, "YouTube"
        return DEMO_REVIEWS[:max_reviews], "Demo (YouTube failed — showing sample data)"

    return DEMO_REVIEWS[:max_reviews], "Demo"


# ── Amazon ────────────────────────────────────────────────────────────────────

def _get_amazon_asin(url: str):
    match = re.search(r"/dp/([A-Z0-9]{10})", url)
    return match.group(1) if match else None


def _scrape_amazon(url: str, max_reviews: int) -> List[Dict]:
    reviews = []
    asin = _get_amazon_asin(url)
    if not asin:
        return reviews

    # Try both .in and .com domains
    domains = ["https://www.amazon.in", "https://www.amazon.com"]

    for domain in domains:
        if reviews:
            break
        base_url = f"{domain}/product-reviews/{asin}"

        for attempt in range(3):  # retry 3 times
            headers = random.choice(HEADERS_LIST)
            session = requests.Session()
            session.headers.update(headers)

            try:
                # First visit homepage to get cookies
                session.get(f"{domain}", timeout=10)
                time.sleep(random.uniform(1, 2))

                page = 1
                while len(reviews) < max_reviews:
                    params = {
                        "pageNumber": page,
                        "reviewerType": "all_reviews",
                        "sortBy": "recent",
                        "formatType": "current_format",
                    }
                    resp = session.get(base_url, params=params, timeout=15)

                    if resp.status_code == 503 or resp.status_code == 403:
                        break

                    if resp.status_code != 200:
                        break

                    soup = BeautifulSoup(resp.text, "html.parser")

                    # Check if blocked
                    if "Enter the characters you see below" in resp.text:
                        break
                    if "robot" in resp.text.lower() and len(resp.text) < 5000:
                        break

                    review_divs = soup.select("div[data-hook='review']")
                    if not review_divs:
                        break

                    for div in review_divs:
                        text_el   = div.select_one("span[data-hook='review-body'] span")
                        rating_el = div.select_one("i[data-hook='review-star-rating'] span")
                        date_el   = div.select_one("span[data-hook='review-date']")

                        text = text_el.get_text(strip=True) if text_el else ""
                        if len(text) < 10:
                            continue

                        rating = None
                        if rating_el:
                            m = re.search(r"(\d+\.?\d*)", rating_el.get_text())
                            if m:
                                rating = float(m.group(1))

                        reviews.append({
                            "text": text,
                            "rating": rating,
                            "timestamp": date_el.get_text(strip=True) if date_el else None,
                        })
                        if len(reviews) >= max_reviews:
                            break

                    page += 1
                    time.sleep(random.uniform(2, 4))

                if reviews:
                    break

            except requests.RequestException:
                time.sleep(2)
                continue

    return reviews


# ── Flipkart ──────────────────────────────────────────────────────────────────

def _scrape_flipkart(url: str, max_reviews: int) -> List[Dict]:
    reviews = []

    # Build review URL
    review_url = re.sub(r"\?.*", "", url)
    if "/p/" in review_url:
        review_url = review_url.replace("/p/", "/product-reviews/")

    for attempt in range(3):
        headers = random.choice(HEADERS_LIST)
        session = requests.Session()
        session.headers.update(headers)

        try:
            page = 1
            while len(reviews) < max_reviews:
                resp = session.get(review_url, params={"page": page}, timeout=15)

                if resp.status_code != 200:
                    break

                soup = BeautifulSoup(resp.text, "html.parser")

                # Try multiple CSS selectors (Flipkart changes them often)
                containers = (
                    soup.select("div.EPCmJX") or
                    soup.select("div.col.EPCmJX") or
                    soup.select("div._27M-vq") or
                    soup.select("div.t-ZTKy") or
                    soup.select("div[class*='review']")
                )

                if not containers:
                    break

                for c in containers:
                    text_el = (
                        c.select_one("div.ZmyHeo") or
                        c.select_one("div.t-ZTKy div") or
                        c.select_one("p.z9E0IG") or
                        c.select_one("p")
                    )
                    text = text_el.get_text(strip=True) if text_el else c.get_text(strip=True)
                    if len(text) < 10:
                        continue

                    rating_el = c.select_one("div._3LWZlK") or c.select_one("div[class*='star']")
                    rating = None
                    if rating_el:
                        try:
                            rating = float(rating_el.get_text(strip=True))
                        except ValueError:
                            pass

                    reviews.append({"text": text, "rating": rating, "timestamp": None})
                    if len(reviews) >= max_reviews:
                        break

                page += 1
                time.sleep(random.uniform(1, 3))

            if reviews:
                break

        except requests.RequestException:
            time.sleep(2)
            continue

    return reviews


# ── YouTube ───────────────────────────────────────────────────────────────────

def _extract_video_id(url: str):
    for p in [r"v=([A-Za-z0-9_-]{11})", r"youtu\.be/([A-Za-z0-9_-]{11})"]:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


def _scrape_youtube(url: str, max_reviews: int) -> List[Dict]:
    try:
        from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_RECENT
        downloader = YoutubeCommentDownloader()
        video_id = _extract_video_id(url)
        if not video_id:
            return []
        comments = []
        for comment in downloader.get_comments_from_url(
            f"https://www.youtube.com/watch?v={video_id}",
            sort_by=SORT_BY_RECENT,
        ):
            text = comment.get("text", "").strip()
            if len(text) >= 5:
                comments.append({
                    "text": text,
                    "rating": None,
                    "timestamp": comment.get("time", None),
                })
            if len(comments) >= max_reviews:
                break
        return comments
    except Exception:
        return []
