from openai.types.chat import ChatCompletionUserMessageParam

from ..models import Client, FunctionalTest, Server
from .utils import create_typed_completion


async def generate_functional_test(client: Client, model: str, server: Server):
    tools_list = [
        f"""
{i}. **{tool.name}**
```json
{tool.model_dump_json(exclude_none=True, exclude={"name"})}
```
""".strip()
        for i, tool in enumerate(server.tools)
    ]

    tools_list = "\n\n".join(tools_list)

    prompt = f"""
You are creating a comprehensive testing plan for an MCP (Model Context Protocol) server. 
Your goal is to systematically test all tools to understand their functionality, dependencies, and overall quality.

Available Tools ({len(server.tools)} total):

{tools_list}

Your task is to create a strategic testing plan that:

1. **Identifies Dependencies**: Determine if any tools depend on others (e.g., a "delete_file" tool might depend on "create_file" being called first)

2. **Orders Tool Calls**: Arrange tools in a logical sequence that respects dependencies and builds understanding progressively

3. **Generates Realistic Arguments**: For each tool call, provide realistic, varied arguments that would thoroughly test the tool's capabilities

4. **Anticipates Results**: Predict what each tool should return given the arguments

5. **Considers Edge Cases**: Include tests for boundary conditions, error scenarios, and edge cases where appropriate

Guidelines:
- Start with simpler, foundational tools before complex ones
- Use realistic, varied data that makes sense for the tool's purpose
- If tools seem related, test them in a logical workflow sequence
- Focus on positive test cases (expected to succeed).
- Consider the tool descriptions and schemas carefully when generating arguments
- For tools that might modify state, plan tests that can verify the modifications
- If a tool requires external resources (files, URLs, etc.), use realistic examples

Respond with a JSON object following this schema:
```json
{FunctionalTest.model_json_schema()}
```


Make the plan comprehensive but minimal - you can call tools multiple times but only if necessary to test something.
""".strip()

    messages = [ChatCompletionUserMessageParam(role="user", content=prompt)]

    return await create_typed_completion(client, model, messages, FunctionalTest)
