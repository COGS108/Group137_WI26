import json
import time
from urllib.parse import urljoin
import requests
BASE_URL = "https://api.massive.com"
ENDPOINT = "/v2/reference/news"

TICKER = "NVDA"
START_DATE = "2023-05-01"     # May 2023 and after
TARGET_ROWS = 1000
PAGE_LIMIT = 1000             # request up to 1000 per call (2 calls to reach ~1500)

# Free tier is 5 req/min -> ~12s between requests; use a buffer.
POLITE_SLEEP_SECONDS = 13

def fetch_json(url, params=None, session=None, max_retries=8):
    s = session or requests.Session()
    backoff = 5  # seconds (will grow)
    for attempt in range(max_retries):
        resp = s.get(url, params=params, timeout=30)

        if resp.status_code == 200:
            return resp.json(), resp.headers

        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After")
            if retry_after is not None:
                wait = max(POLITE_SLEEP_SECONDS, int(float(retry_after)))
            else:
                wait = max(POLITE_SLEEP_SECONDS, backoff)

            print(f"429 rate-limited. Sleeping {wait}s...")
            time.sleep(wait)
            backoff = min(backoff * 2, 300)  # cap at 5 minutes
            continue

        # For other errors, raise with context
        resp.raise_for_status()

    raise RuntimeError("Too many 429s / retries; try increasing POLITE_SLEEP_SECONDS or reducing TARGET_ROWS.")

def main():
    session = requests.Session()

    url = urljoin(BASE_URL, ENDPOINT)
    params = {
        "ticker": TICKER,
        "published_utc.gte": START_DATE,
        "sort": "published_utc",
        "order": "asc",
        "limit": PAGE_LIMIT,
        "apiKey": API_KEY,
    }

    items = []
    seen_urls = set()

    while url and len(items) < TARGET_ROWS:
        data, headers = fetch_json(url, params=params, session=session)

        results = data.get("results", []) or []
        for item in results:
            # If the API already returns JSON objects, keep them as-is / lightly normalize
            publisher = item.get("publisher")

            items.append({
                "published_utc": item.get("published_utc"),
                "publisher": publisher,                         # full publisher object
                "title": item.get("title"),
                "description": item.get("description"),
                "article_url": item.get("article_url"),
                "source": (publisher or {}).get("name"),       # convenience string
                "insights": item.get("insights"),                   # may be empty list
            })

            if len(items) >= TARGET_ROWS:
                break

        # Prepare next page
        next_url = data.get("next_url")
        if next_url:
            # next_url is often relative; make it absolute
            url = urljoin(BASE_URL, next_url)
            params = None  # next_url usually already contains the cursor + apiKey in query
        else:
            url = None

        # Polite throttle even if not rate-limited
        if url and len(items) < TARGET_ROWS:
            time.sleep(POLITE_SLEEP_SECONDS)

        # Optional: avoid accidental loops if API repeats next_url
        if url:
            if url in seen_urls:
                print("Detected repeated next_url; stopping to avoid loop.")
                break
            seen_urls.add(url)

    out_path = "nvda_news_may2023_plus.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(items)} rows to {out_path}")

if __name__ == "__main__":
    main()
