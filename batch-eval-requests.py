import pandas as pd
from pydantic import BaseModel
from openai import OpenAI

client = OpenAI()

N_ARGUMENT_PAIRS = 5

# TODO: Helpful assistant, approximating normal behavior
ASSISTANT_SYSTEM_PROMPT = """
"""

# TODO: Strict impartial judge, demonstrates potential bias mitigation through intstruction-following
STRICT_JUDGE_SYSTEM_PROMPT = """
"""


class ResponsesBody(BaseModel):
    model: str
    instructions: str
    input: str


class ResponsesBatchRequest(BaseModel):
    custom_id: str
    method: str = "POST"
    url: str = "/v1/responses"
    body: ResponsesBody


def create_input(topic: str, left_argument: str, right_argument: str) -> str:
    # TODO: Form blind, id=A, and id=B framing conditions
    pass


def input_to_batch_line(input_str: str) -> ResponsesBatchRequest:
    # TODO: Given prompt, output a batch call JSON line
    batch_req = ResponsesBatchRequest(
        custom_id=f"{topic_to_id(topic)}-{user_identified_as}-{is_swapped}",
        body=ResponsesBody(
            model="gpt-5.5", instructions=ASSISTANT_SYSTEM_PROMPT, input=input_str
        ),
    )
    return batch_req


arguments = pd.read_parquet("data/debatabase-book-arguments.parquet")
arguments = arguments.head(N_ARGUMENT_PAIRS)

batch_lines = []
for topic, pro, con in arguments[["topic", "pro", "con"]].itertuples(
    index=False, name=None
):
    # Form pro/con and con/pro permutations
    pro_con_input = create_input(topic, pro, con)
    con_pro_input = create_input(topic, con, pro)

    batch_lines.append(input_to_batch_line(pro_con_input))
    batch_lines.append(input_to_batch_line(con_pro_input))

# TODO: output from batch_lines to file


## Separate below stuff out, just output batch OAI jsonl

# TODO: call judge to score argument
# potentially on: relevance clarity reasoning support objections proportionality
# look to literature for scoring frameworks

# TODO: calculate biases
# score_margin(User identified as A) - score_margin(Blind)
# score_margin(Blind) - score_margin(User identified as B)
