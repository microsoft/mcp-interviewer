"""Bash command execution tool with output size protection."""

import subprocess

from openai.types.responses import FunctionToolParam

from ..config import AgentConfig


class BashTool:
    """Tool for executing bash commands with output size limits."""

    def __init__(self, config: AgentConfig):
        """Initialize the bash tool.

        Args:
            config: Agent configuration with output limits
        """
        self.max_output_chars = config.max_bash_output_chars

    @staticmethod
    def get_tool_definition() -> FunctionToolParam:
        """Get the tool definition for the LLM."""
        return {
            "type": "function",
            "name": "bash_command",
            "description": "Execute a bash command and return output. Use this for running mcp-interviewer, grep, jq, python, and other CLI tools.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The bash command to execute",
                    }
                },
                "required": ["command"],
            },
            "strict": None,
        }

    def execute(self, command: str, timeout: int | None = 120) -> str:
        """Execute a bash command and return stdout/stderr.

        Args:
            command: The bash command to execute
            timeout: Command timeout in seconds (default: 120)

        Returns:
            Combined stdout and stderr output, or error message if too large
        """
        try:
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            # Combine stdout and stderr
            output = result.stdout
            if result.stderr:
                output += "\n" + result.stderr

            # Check output size
            if len(output) > self.max_output_chars:
                actual_chars = len(output)
                return (
                    f"Error: Command output exceeded maximum length "
                    f"({actual_chars} chars > {self.max_output_chars} limit). "
                    f"Try using head, tail, grep, or other filtering commands to "
                    f"reduce output. For example: 'cat big_file.txt | head -n 100' "
                    f"or 'grep pattern file.txt'"
                )

            return output

        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {timeout} seconds"
        except Exception as e:
            return f"Error executing command: {str(e)}"
