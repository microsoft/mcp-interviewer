<div align="center">

<h1>MCP Interviewer</h1>
<div>
<i>
A Python CLI tool that helps you catch MCP server issues before your agents do.
</i>
</div>
<a href="./README.md#installation">PyPi (coming soon!)</a> | <a href="./README.md">Blog</a> | <a href="./mcp-interview.md">Example</a>
</div>

---

## Table of Contents

- [How it works](#how-it-works)
  - [🔎 Constraint checking](#-constraint-checking)
  - [🛠️ Functional testing](#️-functional-testing)
  - [🤖 LLM evaluation](#-llm-evaluation)
  - [📋 Report generation](#-report-generation)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Example](#example)
- [Usage](#usage)
  - [CLI](#cli)
  - [Bring Your Own Models](#bring-your-own-models)
  - [Python](#python)
- [Limitations](#limitations)
- [Contributing](#contributing)
- [Trademarks](#trademarks)

## How it works

### 🔎 Constraint checking

The MCP Interviewer helps avoid violating providers' hard constraints and warns you when you're not following recommended guidance.

For example, OpenAI does not allow more than 128 tools in a single chat completion request, and recommends at most 20 tools.

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

MCP servers are intended to be used by LLM agents, so the interviewer can optionally test them with an LLM agent. When enabled with the `--test` flag, the interviewer uses your specified LLM to generate a test plan based on the MCP server's capabilities and then executes that plan (e.g. by calling tools), collecting statistics about observed tool behavior.

### 🤖 LLM evaluation

***Note: this is an experimental feature. All LLM generated evaluations should be manually inspected for errors.***

The interviewer can also use your specified LLM to provide structured and natural language evaluations of the server's features.


### 📋 Report generation

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

## Installation

### As a CLI tool

The easiest way to install `mcp-interviewer` is as a `uv` tool. Follow [these instructions](https://docs.astral.sh/uv/getting-started/installation/) to install uv.

```bash
uv tool install --from "git+ssh://git@github.com/microsoft/mcp-interviewer.git" mcp-interviewer

# Then,
mcp-interviewer ...
```

Read more about [CLI usage](./README.md#cli).

### As a dependency

Via `uv`

```bash
uv add git+ssh://git@github.com/microsoft/mcp-interviewer.git
```

Via `pip`

```bash
pip install git+ssh://git@github.com/microsoft/mcp-interviewer.git
```

Read more about [Python usage](./README.md#python).

## Quick Start

⚠️ ***mcp-interviewer arbitrarily executes the provided MCP server command in a child process. Whenever possible, run your server in a container like in the examples below to isolate the server from your host system.***

First, [install](./README.md#as-a-cli-tool) `mcp-interviewer` as a CLI tool.

```bash
# Command to run npx safely inside a Docker container
NPX_CONTAINER="docker run -i --rm node:lts npx"

# Interview the MCP reference server
mcp-interviewer \
  "$NPX_CONTAINER -y @modelcontextprotocol/server-everything"
```

Generates a report Markdown `mcp-interview.md` and corresponding JSON data `mcp-interview.json`.

## Example

To interview the MCP reference server with constraint checking and functional testing you can run the following command:

```bash
NPX_CONTAINER="docker run -i --rm node:lts npx"

mcp-interviewer --test --model gpt-4.1 "$NPX_CONTAINER -y @modelcontextprotocol/server-everything"
```

Which will generate a report like [this](./mcp-interview.md).

## Usage

### CLI

**Key Flags:**

- `--constraints [CODE ...]`: Customize which constraints to check
- `--reports [CODE ...]`: Customize which report sections to include



- `--test`: Enable functional testing. 🚨 ***This option causes mcp-interviewer to invoke the server's tools. Be careful to limit the server's access to your host system, sensitive data, etc before using these options.***
- `--judge-tools`: Enable experimental LLM evaluation of tools
- `--judge-test`: Enable experimental LLM evaluation of functional tests (requires `--test`)
- `--judge`: Enable all LLM evaluation (equivalent to `--judge-tools --judge-test`)

```bash
# Docker command to run uvx inside a container
UVX_CONTAINER="docker run -i --rm ghcr.io/astral-sh/uv:python3.12-alpine uvx"

# Basic constraint checking, server inspection, and report generation (no --model needed)
mcp-interviewer "$UVX_CONTAINER mcp-server-fetch"

# Add functional testing with --test (requires --model)
mcp-interviewer --model gpt-4.1 --test "$UVX_CONTAINER mcp-server-fetch"

# Add LLM tool evaluation with --judge-tools (requires --model)
mcp-interviewer --model gpt-4.1 --judge-tools "$UVX_CONTAINER mcp-server-fetch"

# Add LLM test evaluation with --judge-test (requires --model and --test)
mcp-interviewer --model gpt-4.1 --test --judge-test "$UVX_CONTAINER mcp-server-fetch"

# Add all LLM evaluation with --judge (requires --model and --test)
mcp-interviewer --model gpt-4.1 --test --judge "$UVX_CONTAINER mcp-server-fetch"

# Customize report sections with --reports
mcp-interviewer --model gpt-4.1 --test --reports SI TS FT CV "$UVX_CONTAINER mcp-server-fetch"

# Customize constraint checking with --constraints
mcp-interviewer --constraints OTC ONL "$UVX_CONTAINER mcp-server-fetch"

# Fail on constraint warnings for CI/CD pipelines
mcp-interviewer --fail-on-warnings "$UVX_CONTAINER mcp-server-fetch"

# Test remote servers
mcp-interviewer "https://my-mcp-server.com/sse"
```

### Bring Your Own Models

MCP Interviewer can use any Python object that mimics the chat completions API of the OpenAI Python SDK's `OpenAI` client.

The CLI provides two ways of customizing your model client:

1. `openai.OpenAI` keyword arguments

    You can provide keyword arguments to the OpenAI client constructor via the "--client-kwargs" CLI option. For example, to connect to gpt-oss:20b running locally via Ollama for LLM features:

    ```bash
    mcp-interviewer \
      --client-kwargs \
      "base_url=http://localhost:11434/v1" \
      "api_key=ollama" \
      --model "gpt-oss:20b" \
      --test \
      "docker run -i --rm node:lts npx -y @modelcontextprotocol/server-everything"
    ```

1. Import custom `openai.OpenAI`-compatible type

    Define a parameterless callable the returns an OpenAI compatible type, then specify it's import path via the "--client" option:
    ```python
    # my_client.py
    from openai import AzureOpenAI

    def azure_client():
      return AzureOpenAI(azure_endpoint=..., azure_ad_token_provider=...)
    ```

    ```bash
    mcp-interviewer \
      --client "my_client.azure_client" \
      --model "gpt-4.1_2024-11-20" \
      --test \
      "docker run -i --rm node:lts npx -y @modelcontextprotocol/server-everything"
    ```


### Python

**Basic usage (constraint checking and server inspection only):**

```python
from mcp_interviewer import MCPInterviewer, StdioServerParameters

params = StdioServerParameters(
    command="docker",
    args=["run", "-i", "--rm", "node:lts", "npx", "-y", "@modelcontextprotocol/server-everything"]
)

# No client or model needed for basic functionality
interviewer = MCPInterviewer(None, None)
interview = await interviewer.interview_server(params)
```

**With LLM features (functional testing and evaluation):**

```python
from openai import OpenAI
from mcp_interviewer import MCPInterviewer, StdioServerParameters

# Any object following the OpenAI chat completions API will work
client = OpenAI()
params = StdioServerParameters(
    command="docker",
    args=["run", "-i", "--rm", "node:lts", "npx", "-y", "@modelcontextprotocol/server-everything"]
)

interviewer = MCPInterviewer(client, "gpt-4.1", should_run_functional_test=True)
interview = await interviewer.interview_server(params)
```

**Using the main function directly (includes constraint checking and report generation):**

```python
from mcp_interviewer import main, StdioServerParameters

params = StdioServerParameters(
    command="docker",
    args=["run", "-i", "--rm", "node:lts", "npx", "-y", "@modelcontextprotocol/server-everything"]
)

# Basic usage - no client or model needed
exit_code = main(None, None, params)

# With LLM features
from openai import OpenAI
client = OpenAI()
exit_code = main(client, "gpt-4.1", params, should_run_functional_test=True)
```

## Limitations

MCP Interviewer was developed for research and experimental purposes. Further testing and validation are needed before considering its application in commercial or real-world scenarios. 

The MCP Python SDK executes arbitrary commands on the host machine, so users should run server commands in isolated containers and use external security tools to validate MCP server safety before running MCP Interviewer. 

Additionally, MCP Servers may have malicious or misleading tool metadata that may cause inaccurate MCP Interviewer outputs. Users should manually examine MCP Interviewer outputs for signs of malicious manipulation.

See [TRANSPARENCY.md](./TRANSPARENCY.md) for more information.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding new statistics, constraints, and reports.

## Trademarks 

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos is subject to and must follow Microsoft’s Trademark & Brand Guidelines. Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship. Any use of third-party trademarks or logos are subject to those third-party’s policies.