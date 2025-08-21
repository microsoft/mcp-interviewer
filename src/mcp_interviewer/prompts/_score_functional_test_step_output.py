from openai.types.chat import ChatCompletionUserMessageParam

from ..models import (
    Client,
    FunctionalTestStep,
    FunctionalTestStepEvaluationRubric,
    FunctionalTestStepOutput,
    FunctionalTestStepScoreCard,
)
from .utils import create_typed_completion


async def score_functional_test_step_output(
    client: Client,
    model: str,
    step: FunctionalTestStep,
    output: FunctionalTestStepOutput,
):
    prompt = f"""
You are tasked with evaluating the quality of Model Context Protocol (MCP) tool call results. Analyze the provided tool call information and return your evaluation as a structured JSON object.

### Input:

Tool Name: {step.tool_name}

Input Parameters: {step.tool_arguments}

Expected Output: {step.expected_output}

Actual Output: {output.tool_output}

### Instructions:

Fill out the following rubric and return your evaluation as a JSON object. ONLY return the JSON, nothing else!

```json
{FunctionalTestStepEvaluationRubric.model_json_schema()}
```
""".strip()

    messages = [ChatCompletionUserMessageParam(role="user", content=prompt)]

    evaluation = await create_typed_completion(
        client, model, messages, FunctionalTestStepEvaluationRubric
    )

    return FunctionalTestStepScoreCard(
        **{**step.model_dump(), **output.model_dump(), **evaluation.model_dump()}
    )
