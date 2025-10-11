"""Configuration for the MCP Interviewer Agent."""

from pydantic import BaseModel


class AgentConfig(BaseModel):
    """Configuration for the agent workflow."""

    max_bash_output_chars: int = 50000  # ~12k tokens
    """Maximum characters allowed in bash command output."""

    max_file_read_chars: int = 100000  # ~25k tokens
    """Maximum characters allowed when reading files."""

    max_turns: int = 100
    """Maximum number of LLM turns before stopping."""

    model: str = "gpt-4o"
    """OpenAI model to use for the agent."""

    output_filename: str = "server.py"
    """Filename for the improved server (created in work_dir)."""

    work_dir: str = "./agent_workspace"
    """Working directory for the agent."""

    existing_report_file: str | None = None
    """Path to existing mcp-interview.md file (skips initial analysis if provided)."""
