# mcp-interviewer

A CLI tool for Model Context Protocol (MCP) Server developers to evaluate their servers' readiness for agentic use-cases. Collects server statistics and performs LLM-as-a-judge functional testing of MCP (Model Context Protocol) servers.

## Quick Start

Easy one-liner with `uvx`:

```bash
uvx --from "git+ssh://git@github.com/microsoft/mcp-interviewer.git" mcp-interviewer --model gpt-4.1 "npx -y @modelcontextprotocol/server-everything"
```

The command will save three files:

```
./mcp-scorecard.md
./mcp-scorecard-short.md
./mcp-scorecard.json
```

Open the `mcp-scorecard.md` to read the report on your MCP server.

## Developer Installation

```bash
git clone git@github.com:microsoft/mcp-interviewer.git
cd mcp-interviewer

uv venv
uv sync --all-extras --all-groups

pre-commit install
```

## Detailed Usage

### CLI

```bash
usage: mcp-interviewer [-h] --model MODEL [--client CLIENT] [--out-dir OUT_DIR]
                       [--log-level {DEBUG,INFO,WARN,ERROR}]
                       server_params
```

```bash
mcp-interviewer --model gpt-4.1 "uvx mcp-server-fetch"
```

### Python API

```python
from openai import OpenAI
from mcp_interviewer import MCPInterviewer, ServerParameters

client = OpenAI()
model = "gpt-4.1"
params = ServerParameters(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-everything"]
)

interviewer = MCPInterviewer(client, model)
scorecard = await interviewer.score_server(params)
```

### Example Output