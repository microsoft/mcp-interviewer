"""MCP Interviewer tool for running analysis on MCP servers."""

from pathlib import Path

from openai import OpenAI
from openai.types.responses import FunctionToolParam

from ...main import amain
from ...models import StdioServerParameters
from ..config import AgentConfig


class McpInterviewerTool:
    """Tool for running mcp-interviewer with standard options."""

    def __init__(self, config: AgentConfig, client: OpenAI):
        """Initialize the mcp-interviewer tool.

        Args:
            config: Agent configuration
            client: OpenAI client for analysis
        """
        self.config = config
        self.client = client

    @staticmethod
    def get_tool_definition() -> FunctionToolParam:
        """Get the mcp_interviewer tool definition for the LLM."""
        return {
            "type": "function",
            "name": "mcp_interviewer",
            "description": "Run mcp-interviewer analysis on a Python MCP server file. Always includes --accept-risk and --reports with tool-focused sections (CV TS T). Uses the configured model. The server will be run with 'python {server_path}'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "server_path": {
                        "type": "string",
                        "description": "Path to the Python server file to analyze (e.g., 'server.py' or './workspace/server.py')",
                    },
                    "test": {
                        "type": "boolean",
                        "description": "Enable functional testing of the server (default: false). When enabled, mcp-interviewer will actually call the server's tools to test functionality.",
                    },
                    "judge_tools": {
                        "type": "boolean",
                        "description": "Enable experimental LLM judging of tools (default: false). Generates evaluation scores for tool names, descriptions, and schemas.",
                    },
                    "judge_test": {
                        "type": "boolean",
                        "description": "Enable experimental LLM judging of functional tests (default: false). Generates evaluation scores for test outputs. Requires 'test' to be true.",
                    },
                },
                "required": ["server_path"],
            },
            "strict": None,
        }

    async def execute(
        self,
        server_path: str,
        test: bool = False,
        judge_tools: bool = False,
        judge_test: bool = False,
    ) -> str:
        """Execute mcp-interviewer with options using Python API.

        Args:
            server_path: Path to the Python server file to analyze
            test: Enable functional testing
            judge_tools: Enable LLM judging of tools
            judge_test: Enable LLM judging of functional tests

        Returns:
            Success message or error
        """
        try:
            # Auto-generate output directory based on server path
            server_file = Path(server_path).resolve()
            output_dir = server_file.parent / f"{server_file.stem}_report"

            # Ensure output directory exists (create parent directories if needed)
            output_dir.mkdir(parents=True, exist_ok=True)

            import logging

            logger = logging.getLogger(__name__)
            logger.info(f"Running mcp-interviewer on: {server_file}")
            logger.info(f"Output directory: {output_dir}")

            # Create server parameters for stdio connection
            params = StdioServerParameters(command="python", args=[str(server_file)])

            # Build reports list based on what's enabled
            reports = ["CV", "TS", "T"]  # Constraint Violations, Tool Statistics, Tools
            if test:
                reports.extend(["TCS", "FT"])  # Tool Call Statistics, Functional Tests

            # Run mcp-interviewer using Python API (await since we're already async)
            exit_code = await amain(
                client=self.client,
                model=self.config.model,
                params=params,
                out_dir=output_dir,
                should_judge_tool=judge_tools,
                should_judge_functional_test=judge_test,
                should_run_functional_test=test,
                custom_reports=reports,
                no_collapse=False,
                selected_constraints=None,
                fail_on_warnings=False,
            )

            if exit_code == 0:
                return f"Analysis complete. Reports saved to: {output_dir}/mcp-interview.md"
            else:
                return f"Analysis completed with warnings/errors (exit code: {exit_code}). Check: {output_dir}/mcp-interview.md"

        except Exception as e:
            import traceback

            error_details = traceback.format_exc()
            return f"Error running mcp-interviewer: {str(e)}\n\nFull traceback:\n{error_details}"
