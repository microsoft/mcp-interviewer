import inspect
import json
import logging
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


def parse_json_completion(completion: str):
    completion = completion.strip()
    completion = completion.removeprefix("```json")
    completion = completion.strip("`")
    completion = completion.strip()
    return json.loads(completion)


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
            temperature=0,
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
