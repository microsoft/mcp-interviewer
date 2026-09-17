"""Main task prompt for the MCP Interviewer Agent."""


def get_task_prompt(output_filename: str, server_command: str, report_file: str) -> str:
    """Generate the task prompt for the agent.

    Args:
        output_filename: Name of the output server file
        server_command: Original server command
        report_file: Path to mcp-interview.md report

    Returns:
        Task prompt string
    """
    return f"""
Improve the MCP server `{server_command}` by creating a FastMCP proxy server.

**FILES:**
- Read original analysis from: `{report_file}`
- Write improved proxy to: `{output_filename}` (template already created with markers)

**CONSTRAINTS:**
- Work autonomously - NO user contact
- Implement ALL tools from the original server as proxies
- Use ONLY the tools provided to complete this task
- Call `stop(summary, final_report)` when completely finished

---

## STEP 1: UNDERSTAND THE ORIGINAL SERVER

Read `{report_file}` to find:
- How many tools exist (in the "## Tools" section)
- What each tool's name, parameters, and description are
- Any constraint violations or quality issues

Create todos for each tool you need to implement.

---

## STEP 2: LOCATE WHERE TO WRITE

The file `{output_filename}` contains two marker lines. Find them:

```
findlines(path="{output_filename}", pattern=">>> START WRITING TOOLS")
findlines(path="{output_filename}", pattern=">>> END WRITING TOOLS")
```

These will give you line numbers N and M. You'll replace these lines with your tool code.

---

## STEP 3: WRITE TOOLS (CRITICAL - READ CAREFULLY)

Replace lines N-M with improved tool definitions. Each tool MUST follow this EXACT format:

**CRITICAL: Return Type Hints**
- In FastMCP, the function's return type hint becomes the OUTPUT SCHEMA
- ONLY add a return type hint if the original tool has an outputSchema in the report
- If NO outputSchema exists, do NOT add a return type hint - just return the proxy_call_tool result directly

**Format for tools WITHOUT outputSchema (MOST TOOLS):**

```python
@mcp.tool()  # ← EMPTY! Do NOT pass any arguments!
async def tool_name(param1: str, param2: int = 10):  # ← NO return type hint!
    \"\"\"Brief one-line description.

    Detailed explanation of what this tool does and when to use it.

    Args:
        param1: What param1 is (type, purpose, constraints)
        param2: What param2 is (type, purpose, default value)

    Returns:
        What this returns (describe it in text, but no type hint!)

    Examples:
        tool_name("test", 5) → "expected output"
    \"\"\"
    return await proxy_call_tool("original_tool_name", param1=param1, param2=param2)
```

**Format for tools WITH outputSchema (RARE - check the report!):**

```python
from pydantic import BaseModel, Field

class WeatherOutput(BaseModel):
    \"\"\"Weather data structure.\"\"\"
    temperature: float = Field(description="Temperature in celsius")
    conditions: str = Field(description="Weather conditions")
    humidity: float = Field(description="Humidity percentage")

@mcp.tool()
async def get_weather(location: str) -> WeatherOutput:  # ← HAS return type from outputSchema
    \"\"\"Get weather for a location.

    Returns temperature, conditions, and humidity for the specified location.

    Args:
        location: City name or zip code

    Returns:
        Structured weather data with temperature, conditions, and humidity

    Examples:
        get_weather("Paris") → {{"temperature": 18, "conditions": "Cloudy", "humidity": 65}}
    \"\"\"
    result = await proxy_call_tool("structuredContent", location=location)
    validated = WeatherOutput.model_validate(result.structuredContent)
    return validated
```

**CRITICAL RULES:**

1. **@mcp.tool()** must be EMPTY - do not pass name, description, or parameters!
2. **Docstring is MANDATORY** - this is what the LLM sees as the tool description
3. **Must be async def** - always use `async def`
4. **NO return type hint** - unless original tool has outputSchema (check the report!)
5. **Return directly** - `return await proxy_call_tool(...)` for tools without outputSchema
6. **Validate with model_validate** - for tools WITH outputSchema: `return Model.model_validate(result.structuredContent)`
7. **Must have sections** - Args, Returns, Examples in docstring

**DO NOT:**
- Pass arguments to @mcp.tool()
- Add return type hints unless original has outputSchema
- Parse `.content[0].text` - this is wrong!
- Skip Pydantic docstrings and Field descriptions when using BaseModel
- Skip the tool docstring
- Forget to call the original tool

**FOR outputSchema tools:**
- Create Pydantic BaseModel with docstring and Field descriptions
- Add return type hint matching the BaseModel
- Validate result with `Model.model_validate(result.structuredContent)` before returning

**EXAMPLE FOR REFERENCE:**

Original tool "echo" with parameter "message" (NO outputSchema):

```python
@mcp.tool()
async def echo_message(message: str):  # ← NO return type hint!
    \"\"\"Echoes the input message back unchanged.

    Takes any text and returns it exactly as provided. Useful for testing.

    Args:
        message: Text to echo (any string)

    Returns:
        The exact same text that was input

    Examples:
        echo_message("hello") → "hello"
    \"\"\"
    return await proxy_call_tool("echo", message=message)  # Return directly!
```

---

## STEP 4: WRITE ALL TOOLS AT ONCE

Use `writelines`:

```python
writelines(
    path="{output_filename}",
    content="<all your @mcp.tool() definitions here>",
    start_line=N,
    end_line=M
)
```

---

## STEP 5: TEST

```python
mcp_interviewer(server_path="{output_filename}", test=true, judge_tools=true)
```

Read the new report. If there are still issues, refine the tools and test again.

---

## STEP 6: FINISH

When all constraint violations are fixed, all tools are implemented correctly as proxies, and quality is good:

```python
stop(
    summary="Implemented X tools with improved names/descriptions",
    final_report="Fixed: <list issues>. Improved: <list improvements>"
)
```

---

## YOUR AVAILABLE TOOLS:

- `readlines(path, offset?, limit?)` - read files
- `writelines(path, content, start_line, end_line)` - replace lines (must read first)
- `findlines(path, pattern)` - search files
- `bash_command(cmd)` - run shell commands
- `mcp_interviewer(server_path, test?, judge_tools?, judge_test?)` - test your server
- `add_todo(task)`, `complete_todo(task)`, `remove_todo(task)`, `list_todos()` - track progress
- `stop(summary, final_report)` - signal done

**START NOW.** Begin by reading the report to understand the original server.
"""
