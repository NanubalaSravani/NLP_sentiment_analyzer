import sys
import modules.scraper as scraper

url = sys.argv[1]
print(f"Testing URL: {url}")
reviews, platform = scraper.scrape_reviews(url, 10)
print(f"Platform: {platform}")
print(f"Extracted {len(reviews)} reviews.")
if len(reviews) > 0 and platform != "Demo" and "Demo" not in platform:
    print(reviews[0])
