# MCP Interviewer Agent

An agent that automatically improves your MCP server tools.

Given an MCP Server, the MCP Interviewer Agent will produce a FastMCP proxy server (written in Python) that exposes your original server's tools through a more agent-ergonomic interface with improved names, descriptions, and schemas.

## Usage

```bash
# Creates an improved server.py in ./agent_workspace/
mcp-interviewer-agent <your mcp-server command>

# With custom output path (parent directory becomes the working directory)
mcp-interviewer-agent "npx @org/mcp-server-foo" \
  --output ./my_project/improved_server.py \
  --max-turns 50

# Run your improved server:
python ./agent_workspace/server.py
```

## How it works

1. **Initial Analysis**: Runs mcp-interviewer with --test and --judge flags on your original server
2. **Continuous Improvement**: The agent autonomously:
   - Reads the analysis reports (mcp-interview.md and .json)
   - Identifies constraint violations and quality issues
   - Writes a FastMCP proxy server.py that wraps your original tools
   - Tests the proxy with mcp-interviewer
   - Refines the SAME server.py file based on test results
   - Repeats until all issues are resolved
3. **Completion**: Agent calls the 'stop' tool when satisfied, or stops at max turns

The agent works continuously in a single directory, iteratively improving one server.py file until it passes all constraints and quality checks.