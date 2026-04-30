import json
import pandas as pd

with open("data/parsed-all.json") as f:
    topics = json.load(f)

# shape
# entry_id | topic_id | topic | pro | con

rows = []

topic_id = 1
entry_id = 1
for topic in topics:
    for argument in topic["arguments"]:
        rows.append(
            {
                "entry_id": entry_id,
                "topic_id": topic_id,
                "topic": topic["topic"],
                "pro": argument["point"],
                "con": argument["counterpoint"],
            }
        )
        entry_id += 1
    topic_id += 1

df = pd.DataFrame(rows)
df.to_parquet("data/debatabase-book-arguments.parquet", index=False)
