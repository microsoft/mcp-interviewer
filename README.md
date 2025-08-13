# mcp-interviewer

A tool for performing automatic LLM-as-a-judge analysis and functional testing of MCP (Model Context Protocol) servers.

## Quick start

Use uvx to run the tool without cloning it!

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

## Installation

Clone this repo and then use uv to install it.

```bash
git clone git@github.com:microsoft/mcp-interviewer.git
cd mcp-interviewer
uv venv
uv sync --all-extras --all-groups
```

## Usage

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

