# mcp-interviewer

A tool for analyzing and testing MCP (Model Context Protocol) servers and their tools.

## Quick start

Use uvx to run the tool without cloning it!

```bash
uvx --from "git+ssh://git@github.com/microsoft/mcp-interviewer.git[all]" mcp-interviewer "uvx mcp-server-fetch" --iterations 3
```

## Interview

To interview a collection of McpWorkbenches, the interviewer:

1. Iterates over each workbench i
    a. Iterates over each tool j in workbench i
        i. Generate arguments for tool j
        ii. Call tool j with generated arguments
        iii. Record success/failure of the tool call
        iv. In the same conversation context, loop to step i. 3 times (i.e. generating different arguments each time)
2. Give workbench i a score based on its average tool success.
3. Generate a qualitative analysis for workbench i based on the tool call results


### Results Structure

The interviewer returns structured results with:

- Overall score and analysis across all servers
- Per-server scores and analysis
- Per-tool scores, analysis, and error details
- Suggested improvements for poorly performing tools
- Success rates and summary statistics


## Installation

Clone this repo and then use uv to install it.

```bash
git clone git@github.com:microsoft/mcp-interviewer.git
cd mcp-interviewer
uv venv
GIT_LFS_SMUDGE_SKIP=1 uv sync --all-groups --all-extras
```

## Usage

### CLI

```bash
mcp-interviewer "uvx mcp-server-fetch" --iterations 3
```

### Python API

```python
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import McpWorkbench

from mcp_interviewer import MCPInterviewer

workbenches = [
    McpWorkbench(
        server_path="/path/to/your/mcp/server",
        server_args=["--arg1", "value1"],
        # ... other configuration
    ),
    # ... more workbenches
]

model_client = OpenAIChatCompletionClient(
    api_key="your-openai-api-key",
    model="gpt-4"
)

interviewer = MCPInterviewer(workbenches, model_client=model_client)

interview = await interviewer.interview(
    check_tools=True,  # Run tests to check if tools actually work and in what cases
    rewrite_tools=True,  # Suggest new tool names and descriptions that match real tool behavior
)

print(interview.score)  # Numerical score
print(interview.analysis)  # Natural language analysis of this server overall
print([(tool.score, tool.analysis, tool.rewritten) for tool in interview.tools])
```

