import os
import logging
import polars as pl
from openai import OpenAI
from dotenv import load_dotenv

DATASET_URI = "hf://datasets/ibm-research/debate_speeches/opening_speeches/train-00000-of-00001.parquet"
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"), base_url=os.environ.get("OPENAI_BASE_URL")
)

# We'll use text written either by a human expert or Project Debater,
# and need topics with at least 2 relevant texts so we can have them compared.
df = pl.read_parquet(DATASET_URI)

expert_or_project_debator_rows = df.filter(
    pl.col("source").is_in(["Human expert", "Project Debater"])
    & (pl.len().over("topic_id") >= 2)
)

position_str_to_int = {"for": 1, "against": -1, "inconclusive": 0}


def classify_position_from_row(row, client):
    claim = row["topic"]
    text = row["text"]

    system_prompt = """
You classify debate speeches as either "for", "against", or "inconclusive" on the position '{claim}'.
You will be given unstructured text from a speech and return only the corresponding one-word position label.
"""

    try:
        response = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
        )
        position_str = response.choices[0].message.content
    except Exception:
        logger.exception("Failed to classify position for topic=%r", claim)
        return 0

    if position_str not in position_str_to_int:
        logger.warning("Invalid position %r for topic=%r", position, claim)
        return 0

    logger.info(
        "Classified text with topic_id=%r as '%r'", row["topic_id"], position_str
    )

    return position_str_to_int[position_str]


# To ensure that the multiple texts within a topic are actually on opposing sides of the issue,
# we introduce classification not present in the original dataset.
with_position_classification = expert_or_project_debator_rows.with_columns(
    pl.struct(expert_or_project_debator_rows.columns)
    .map_elements(
        lambda row: classify_position_from_row(row, client),
        return_dtype=pl.Int64,
    )
    .alias("position")
)

with_position_classification.write_csv("data/with_position_classification.csv")
