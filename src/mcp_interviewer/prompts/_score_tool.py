from mcp import Tool
from openai.types.chat import ChatCompletionUserMessageParam

from ..models import Client, ToolScoreCard
from .utils import create_typed_completion


async def judge_tool(client: Client, model: str, tool: Tool):
    prompt = f"""
You are tasked with evaluating the quality of an MCP (Model Context Protocol) tool based on its name, description, and JSON schema. Analyze the provided tool information and return your evaluation as a structured JSON object.

### Tool:

```json
{tool.model_dump_json(exclude_none=True)}
```

### Instructions:

Fill out the following rubric and return your evaluation as a JSON object:

```json
{ToolScoreCard.model_json_schema()}
```
""".strip()

    messages = [ChatCompletionUserMessageParam(role="user", content=prompt)]

    return await create_typed_completion(client, model, messages, ToolScoreCard)
