import inspect
import json
import logging
import re
from collections.abc import Sequence
from typing import TypeVar

import pydantic
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionUserMessageParam,
)
from pydantic import BaseModel

from ..models import Client

logger = logging.getLogger(__name__)

json_start_chars = re.compile(r"[{\[\"]")  # Match { or [ or "
json_end_chars = re.compile(r"[}\]\"]")  # Match } or ] or "


def parse_json_completion(completion: str):
    """Extract and parse JSON from a completion string.

    Finds the first occurrence of { or [ and the last occurrence of } or ],
    then parses the substring as JSON.

    Args:
        completion: String potentially containing JSON

    Returns:
        Parsed JSON object or array

    Raises:
        ValueError: If no JSON markers found
        json.JSONDecodeError: If JSON is invalid
    """
    match = json_start_chars.search(completion)
    if not match:
        raise ValueError("No JSON start character found")

    first_json_char = match.start()

    # Find last closing character (get all matches, take the last one)
    end_matches = list(json_end_chars.finditer(completion))
    if not end_matches:
        raise ValueError("No JSON end character found")

    last_json_char = end_matches[-1].end()

    # Extract JSON substring
    json_str = completion[first_json_char:last_json_char]
    return json.loads(json_str)


TResponseModel = TypeVar("TResponseModel", bound=BaseModel)


async def create_typed_completion(
    client: Client,
    model: str,
    initial_messages: Sequence[ChatCompletionMessageParam],
    response_model: type[TResponseModel],
    max_retries: int = 2,
):
    max_retries = max(0, max_retries)
    messages = list(initial_messages)

    for _ in range(max_retries + 1):
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
        )

        if inspect.isawaitable(completion):
            completion = await completion

        content = completion.choices[0].message.content
        messages.append(
            ChatCompletionAssistantMessageParam(role="assistant", content=content)
        )

        if not content:
            raise ValueError("chat completion content was None")

        try:
            response = parse_json_completion(content)
            response = response_model.model_validate(response)
            return response
        except (json.decoder.JSONDecodeError, pydantic.ValidationError) as e:
            print(content)
            logger.exception("Error parsing json")
            import traceback

            tb_str = traceback.format_exc()
            messages.append(
                ChatCompletionUserMessageParam(
                    role="user",
                    content=f"Error parsing json: {e}\nTraceback:\n{tb_str}",
                )
            )
    raise Exception("Exceeded maximum retries")
