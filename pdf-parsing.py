import pymupdf
import json
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()


class ArgumentPair(BaseModel):
    point: str
    counterpoint: str


class DebateTopic(BaseModel):
    topic: str
    arguments: list[ArgumentPair]


with open("data/debatabase_book_toc.json") as f:
    table_of_contents = json.load(f)

# PDF page 10 = book page 1, and make zero-indexed
table_of_contents_adjusted = {
    title: page + 8 for title, page in table_of_contents.items()
}

range_zip = zip(
    table_of_contents_adjusted.values(), list(table_of_contents_adjusted.values())[1:]
)
ranges = list(range_zip)[1:]  # ignore Introduction

uploaded_files = []

with pymupdf.open("data/Association and Trapp - 2008 - Debatabase Book.pdf") as doc:
    for a, b in list(ranges):
        with pymupdf.open() as excerpted_pages:
            excerpted_pages.insert_pdf(doc, from_page=a, to_page=b)
            pdf_bytes = excerpted_pages.tobytes()
            uploaded = client.files.create(
                file=(f"excerpt-{a}-{b}.pdf", pdf_bytes, "application/pdf"),
                purpose="user_data",
                expires_after={"anchor": "created_at", "seconds": 3600},
            )
            uploaded_files.append(uploaded)

system_prompt = """
You extract structured data.
You will be given unstructured text from a book and should convert it into the given structure.
Do not infer missing fields; use empty strings if absent. Preserve quoted text verbatim.
"""

user_prompt = """
Extract the debate topic and its PRO/CON argument pairs.
Focus only on the fully included topic, ignoring extraneous data before or after.
"""

parsed_topics = []
n = 1
for uploaded in uploaded_files:
    response = client.responses.parse(
        model="gpt-5.5",
        reasoning={"effort": "medium"},
        input=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": [
                    {"type": "input_file", "file_id": uploaded.id},
                    {"type": "input_text", "text": user_prompt},
                ],
            },
        ],
        text_format=DebateTopic,
    )

    parsed_topic = response.output_parsed
    if parsed_topic is None:
        print(f"parsed_topic is None; skipping. Response:\n{response}")
        continue
    parsed_topics.append(parsed_topic)

    with open(f"data/topics/{parsed_topic.topic}.json", "w") as f:
        json.dump(parsed_topic.model_dump(), f, indent=4)

    print(f"Successfully parsed topic {n}/{len(ranges)}")
    n += 1

with open("data/parsed-remaining.json", "w") as f:
    json.dump([topic.model_dump() for topic in parsed_topics], f, indent=4)
