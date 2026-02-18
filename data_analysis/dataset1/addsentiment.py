import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

IN_PATH = "/Users/siyakamboj/Downloads/Group137_WI26/data/00-raw/dataset1/clustered.json"   # your current file
OUT_PATH = "/Users/siyakamboj/Downloads/Group137_WI26/data/00-raw/dataset1/clustered_with_sentiment.json"

analyzer = SentimentIntensityAnalyzer()

def article_text(item: dict) -> str:
    title = (item.get("title") or "").strip()
    desc = (item.get("description") or "").strip()
    # VADER works better with a little context; title alone can be noisy
    if desc:
        return f"{title}. {desc}"
    return title

def vader_sentiment(text: str) -> dict:
    if not text.strip():
        return {
            "sentiment_model": "vader",
            "sentiment_label": "neutral",
            "sentiment_score": 0.0,
            "sentiment_detail": {"pos": 0.0, "neu": 1.0, "neg": 0.0, "compound": 0.0},
        }
    scores = analyzer.polarity_scores(text)
    compound = float(scores["compound"])  # [-1, 1]
    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"
    return {
        "sentiment_model": "vader",
        "sentiment_label": label,
        "sentiment_score": compound,
        "sentiment_detail": scores,
    }

with open(IN_PATH, "r", encoding="utf-8") as f:
    items = json.load(f)

for item in items:
    text = article_text(item)
    item.update(vader_sentiment(text))

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(items, f, indent=2, ensure_ascii=False)

print(f"Saved {len(items)} items with sentiment to {OUT_PATH}")
