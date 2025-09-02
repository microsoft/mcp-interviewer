# mcp-interviewer

LLM-driven testing for MCP servers: generates functional tests, executes tool calls, and validates server design best practices.

The MCP Interviewer generates a Markdown report capturing the following information:

- Server capabilities (e.g resource subscriptions, prompt lists changing)
- Schemas of server tools, resources, resource templates, and prompts
- Schema statistics (e.g. tool name lengths, tool input schema depths)
- LLM-generated functional test plan and outputs
- Functional test output statistics (e.g. tool call result lengths)
- Warnings and errors for common constraints (e.g. context window lengths, number of tools)
- LLM-as-a-judge evaluation of functional test outputs
- LLM-as-a-judge evaluation of static tool schemas



## Quick Start

```bash
# Test any MCP server with one command
uvx --from "git+ssh://git@github.com/microsoft/mcp-interviewer.git" mcp-interviewer \
  --model gpt-4o "npx -y @modelcontextprotocol/server-everything"
```

Generates `mcp-interview.md` and `mcp-interview.json` with a full evaluation report.

See an example report for the "@modelcontextprotocol/server-everything" reference server [here](./mcp-interview.md).

## Installation

```bash
pip install git+ssh://git@github.com/microsoft/mcp-interviewer.git
```

## Common Examples

```bash
# Basic evaluation (fast, no experimental LLM judging)
mcp-interviewer --model gpt-4o "uvx mcp-server-fetch"

# Full evaluation with experimental LLM judging (detailed but slower)
mcp-interviewer --model gpt-4o --judge "uvx mcp-server-fetch"

# Quick summary report
mcp-interviewer --model gpt-4o --short "uvx mcp-server-fetch"

# Custom report with specific sections
mcp-interviewer --model gpt-4o --reports SI TS FT CV "uvx mcp-server-fetch"

# Check only specific constraints
mcp-interviewer --model gpt-4o --select OTC ONL "uvx mcp-server-fetch"

# Test remote servers
mcp-interviewer --model gpt-4o "https://my-mcp-server.com/sse"
```

## Report Sections

Use `--reports` to customize output. Available sections:

- `II` - Interviewer Info (model, parameters)
- `SI` - Server Info (name, version, capabilities)  
- `CAP` - Capabilities (supported features)
- `TS` - Tool Statistics (counts, patterns)
- `TCS` - Tool Call Statistics (performance metrics)
- `FT` - Functional Tests (tool execution results)
- `CV` - Constraint Violations
- `T` - Tools
- `R` - Resources
- `RT` - Resource Templates
- `P` - Prompts

## Constraint Validation

Use `--select` to check specific constraints:

- `OTC` - OpenAI tool count limit (≤128 tools)
- `ONL` - OpenAI name length (≤64 chars)
- `ONP` - OpenAI name pattern (a-zA-Z0-9_-)
- `OTL` - OpenAI token length limit
- `OA` - All OpenAI constraints

## Python API

```python
from openai import OpenAI
from mcp_interviewer import MCPInterviewer, StdioServerParameters

client = OpenAI()
params = StdioServerParameters(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-everything"]
)

interviewer = MCPInterviewer(client, "gpt-4o")
interview = await interviewer.score_server(params)
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding new statistics, constraints, and reports.

## Trademarks 

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos is subject to and must follow Microsoft’s Trademark & Brand Guidelines. Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship. Any use of third-party trademarks or logos are subject to those third-party’s policies.