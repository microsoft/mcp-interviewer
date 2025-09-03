# mcp-interviewer

The MCP Interviewer is a Python CLI tool that helps you ***catch MCP server issues before your agents do.***

It does this via the following features:

### 🔎 Constraint checking

The MCP Interviewer helps you make sure you aren't violating providers' hard constraints and warns you when you're not following recommended guidance.

<details>

<summary>View all supported constraints</summary>

Use `--constraints [CODE ...]` to customize output.

| Constraint Code | Description |
|------------|-------------|
| `OTC` | OpenAI tool count limit (≤128 tools) |
| `ONL` | OpenAI name length (≤64 chars) |
| `ONP` | OpenAI name pattern (a-zA-Z0-9_-) |
| `OTL` | OpenAI token length limit |
| `OA` | All OpenAI constraints |

</details>

### 🛠️ Functional testing

MCP servers are intended to be used by LLM agents, so we test them with an LLM agent. Using your specified LLM, the interviewer generates a test plan based on the MCP server's capabilities and then executes that plan (e.g. by calling tools), collecting statistics about observed tool behavior.

### 🧪 LLM evaluation

***Note: this is an experimental feature. All LLM generated evaluations should be manually inspected for errors.***

The interviewer can also use your specified LLM to provide structured and natural language evaluations of the server's features.


### 📋 Reports

The interviewer generates a Markdown report (and accompanying `.json` file with raw data) summarizing the interview results.

<details>
<summary>View all supported reports</summary>

Use `--reports [CODE ...]` to customize output.

| Report Code | Description |
|-------------|-------------|
| `II` | Interviewer Info (model, parameters) |
| `SI` | Server Info (name, version, capabilities) |
| `CAP` | Capabilities (supported features) |
| `TS` | Tool Statistics (counts, patterns) |
| `TCS` | Tool Call Statistics (performance metrics) |
| `FT` | Functional Tests (tool execution results) |
| `CV` | Constraint Violations |
| `T` | Tools |
| `R` | Resources |
| `RT` | Resource Templates |
| `P` | Prompts |


</details>


## Quick Start

```bash
# Test any MCP server with one command
uvx --from "git+ssh://git@github.com/microsoft/mcp-interviewer.git" mcp-interviewer \
  --model gpt-4o "npx -y @modelcontextprotocol/server-everything"
```

Generates `mcp-interview.md` and `mcp-interview.json` with a full evaluation report.

## Example

To interview the MCP reference server, you can run the following command:

```bash
mcp-interviewer --model gpt-4o "npx -y @@modelcontextprotocol/server-everything"
```

Which will generate a report like (this)[./mcp-interview.md].

## Installation

```bash
pip install git+ssh://git@github.com/microsoft/mcp-interviewer.git
```

## Usage

### CLI

```bash
# Constraint checking, functional testing, default report generation
mcp-interviewer --model gpt-4o "uvx mcp-server-fetch"

# Constraint checking, functional testing, LLM evaluation, default report generation
mcp-interviewer --model gpt-4o --judge "uvx mcp-server-fetch"

# Constraint checking, functional testing, custom report generation
mcp-interviewer --model gpt-4o --reports SI TS FT CV "uvx mcp-server-fetch"

# Custom constraint checking, functional testing, report generation
mcp-interviewer --model gpt-4o --select OTC ONL "uvx mcp-server-fetch"

# Test remote servers
mcp-interviewer --model gpt-4o "https://my-mcp-server.com/sse"
```

### Python

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