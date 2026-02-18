import json
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

IN_PATH = "/Users/siyakamboj/Downloads/Group137_WI26/data/00-raw/nvda_news_may2023_plus.json"

with open(IN_PATH, "r", encoding="utf-8") as f:
    items = json.load(f)

# Extract timestamps
dates = [x.get("published_utc") for x in items if x.get("published_utc")]

# Convert to pandas datetime
dt = pd.to_datetime(dates, utc=True)

# Count per month
counts = dt.to_series().dt.to_period("M").value_counts().sort_index()

print(counts)

# # Plot
# counts.plot(kind="bar")
# plt.title("NVDA News Articles per Month")
# plt.xlabel("Month")
# plt.ylabel("Number of Articles")
# plt.show()


with open(IN_PATH, "r", encoding="utf-8") as f:
    items = json.load(f)

publishers = [x.get("source") for x in items if x.get("source")]

counts = Counter(publishers)

# Print top publishers
for name, count in counts.most_common(20):
    print(f"{name}: {count}")


#filter and re-save
CLUSTER_MAP = {
    # Opinion / Retail Analysis
    "The Motley Fool": "Opinion_Retail",
    "Seeking Alpha": "Opinion_Retail",

    # Quant / Analyst
    "Zacks Investment Research": "Quant_Analyst",

    # Real-Time News
    "MarketWatch": "RealTime_News",
    "Benzinga": "RealTime_News",
    "Investing.com": "RealTime_News",
}
filtered_items = []

for item in items:
    src = item.get("source")
    cluster = CLUSTER_MAP.get(src)

    if cluster is not None:   # keeps only chosen groups
        item["publisher_cluster"] = cluster
        filtered_items.append(item)

print("Remaining articles:", len(filtered_items))


counts = Counter(x["publisher_cluster"] for x in filtered_items)

for k, v in counts.items():
    print(f"{k}: {v}")

import json

with open("nvda_news_clustered.json", "w", encoding="utf-8") as f:
    json.dump(filtered_items, f, indent=2, ensure_ascii=False)


