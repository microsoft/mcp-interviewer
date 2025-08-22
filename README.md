# mcp-interviewer

A CLI tool to evaluate an Model Context Protocol (MCP) servers' readiness for agentic use-cases. Inspects server capabilities and statistics, performs LLM-as-a-judge functional testing of tools, and generates a report.

## How is this for?

### Server Developers

If you are an MCP Server Developer, the `mcp-interviewer` can help you validate the functionality of your server and alert you to any potential issues for downstream clients consuming your server.

### Users

Before using an MCP Server, you can interview it to see how it behaves with your LLM.

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

Open the `mcp-scorecard.md` to read the report on the MCP server.

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

## Trademarks 

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos is subject to and must follow Microsoft’s Trademark & Brand Guidelines. Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship. Any use of third-party trademarks or logos are subject to those third-party’s policies.