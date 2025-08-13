from openai.types.chat import ChatCompletionUserMessageParam

from ..models import Client, FunctionalTestOutput, FunctionalTestScoreCard
from .utils import create_typed_completion


async def score_functional_test_output(
    client: Client, model: str, test: FunctionalTestOutput
):
    prompt = f"""
You are creating an overall evaluation report for an MCP (Model Context Protocol) server based on the results of an executed evaluation plan. Analyze the evaluation steps and their execution results to provide a comprehensive assessment.

### Input:

Evaluation Plan:
```json
{test.model_dump_json()}
```

### Analysis Guidelines:

- **PRIORITIZE EXECUTION SUCCESS**: Focus primarily on whether tools actually executed successfully
- The evaluation.steps array contains tool call execution results with these key fields:
  - actualOutput: The actual result returned by the tool call (or error object)
  - evaluation.error_type.value: "Unauthorized", "Bad Request", "Internal Error", "MCP Error", "Other Error", or "No Error"
  - evaluation.overall_assessment.score for each tool call execution (1-3)
- Determine status based on execution patterns: if most tools executed without errors, lean toward "Met Expectations"
- Authentication/Connection errors should override other considerations for status classification
- Count successful vs failed executions to determine overall server health

Base your assessment on the actual evaluation data provided, considering both tool quality metrics and execution results.

### Instructions:

Fill out the following rubric and return your evaluation as a JSON object:

```json
{FunctionalTestScoreCard.model_json_schema()}
```
""".strip()

    messages = [ChatCompletionUserMessageParam(role="user", content=prompt)]

    return await create_typed_completion(
        client, model, messages, FunctionalTestScoreCard
    )
