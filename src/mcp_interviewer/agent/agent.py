"""Main agent runner for improving MCP servers."""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

from openai import BadRequestError, OpenAI
from openai.types.responses import FunctionToolParam

from ..main import amain
from ..models import StdioServerParameters, StreamableHttpServerParameters
from .config import AgentConfig
from .prompts import get_reminder_message, get_task_prompt
from .templates import get_server_template
from .tools import BashTool, FileTool, McpInterviewerTool, StopTool, TodoTool

logger = logging.getLogger(__name__)


class AgentRunner:
    """Main agent that orchestrates the MCP server improvement workflow."""

    def __init__(self, config: AgentConfig, client: OpenAI):
        """Initialize the agent runner.

        Args:
            config: Agent configuration
            client: OpenAI client
        """
        self.config = config
        self.client = client
        self.bash_tool = BashTool(config)
        self.file_tool = FileTool(config)
        self.mcp_interviewer_tool = McpInterviewerTool(config, client)
        self.stop_tool = StopTool()
        self.todo_tool = TodoTool()
        self.conversation_id: str | None = None
        self.agent_stopped = False
        self.stop_summary = ""
        self.stop_report = ""

    async def run(self, server_command: str) -> str:
        """Run the complete agent workflow.

        Args:
            server_command: Command to run the original MCP server

        Returns:
            Path to the improved server file
        """
        logger.info("=" * 60)
        logger.info("Starting MCP Interviewer Agent")
        logger.info("=" * 60)

        # Setup working directory
        work_dir = Path(self.config.work_dir)
        work_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Working directory: {work_dir}")

        # Create a conversation for the entire agent workflow
        logger.info("Creating conversation for agent workflow...")
        conversation = self.client.conversations.create()
        self.conversation_id = conversation.id
        logger.info(f"Conversation ID: {self.conversation_id}")

        # Determine report file
        if self.config.existing_report_file:
            # Use existing report
            logger.info("=" * 60)
            logger.info("Using Existing Report")
            logger.info("=" * 60)

            report_file = Path(self.config.existing_report_file)
            if not report_file.exists():
                raise RuntimeError(f"Report file does not exist: {report_file}")
            if not report_file.is_file():
                raise RuntimeError(f"Report path is not a file: {report_file}")
            if report_file.name != "mcp-interview.md":
                raise RuntimeError(
                    f"Expected mcp-interview.md but got: {report_file.name}"
                )

            logger.info(f"Using report: {report_file}")
        else:
            # Run initial mcp-interviewer on original server
            logger.info("=" * 60)
            logger.info("Running Initial Analysis of Original Server")
            logger.info("=" * 60)

            report_dir = work_dir / "original_report"
            report_dir.mkdir(parents=True, exist_ok=True)

            # Create server parameters based on command type
            if server_command.startswith(("http://", "https://")):
                # HTTP server
                params = StreamableHttpServerParameters(url=server_command)
            else:
                # Stdio server
                import shlex

                command_parts = shlex.split(server_command)
                params = StdioServerParameters(
                    command=command_parts[0],
                    args=command_parts[1:] if len(command_parts) > 1 else [],
                )

            # Run using Python API (avoids stdout capture issues)
            try:
                exit_code = await amain(
                    client=self.client,
                    model=self.config.model,
                    params=params,
                    out_dir=report_dir,
                    should_judge_tool=True,
                    should_judge_functional_test=True,
                    should_run_functional_test=True,
                    custom_reports=None,  # Full report for initial analysis
                    no_collapse=False,
                    selected_constraints=None,
                    fail_on_warnings=False,
                )

                if exit_code != 0:
                    logger.warning(
                        f"Initial analysis completed with warnings (exit code: {exit_code})"
                    )

                logger.info("Initial analysis complete")
                report_file = report_dir / "mcp-interview.md"

            except Exception as e:
                logger.error(f"Initial analysis failed: {e}")
                raise RuntimeError(f"Failed to analyze original server: {e}")

        # Pre-populate server.py with template
        logger.info("=" * 60)
        logger.info("Creating Initial Server Template")
        logger.info("=" * 60)

        server_path = work_dir / self.config.output_filename

        # Generate and write the template (auto-detects stdio vs HTTP)
        template = get_server_template(server_command)
        with open(server_path, "w") as f:
            f.write(template)

        logger.info(f"Created template at: {server_path}")
        logger.info(f"Server command: {server_command}")

        # Initialize todo list with a required task
        self.todo_tool.add_todo(
            "Run mcp_interviewer tool with test=true, judge_tools=true, and judge_test=true at least once"
        )
        logger.info(
            "Initialized todo list with requirement to run comprehensive testing"
        )

        # Give the agent its task
        logger.info("=" * 60)
        logger.info("Starting Agent Workflow")
        logger.info("=" * 60)

        # Generate the task prompt
        initial_message = get_task_prompt(
            self.config.output_filename, server_command, str(report_file)
        )

        # Run the agent until it stops itself or hits max turns
        await self._run_until_complete(initial_message)

        # Final output
        logger.info("\n" + "=" * 60)
        logger.info("Agent Complete!")
        logger.info("=" * 60)

        if self.agent_stopped:
            logger.info(f"\nSummary: {self.stop_summary}")
            logger.info(f"\nFinal Report:\n{self.stop_report}")

        final_server_path = work_dir / self.config.output_filename
        return str(final_server_path)

    async def _run_until_complete(self, initial_message: str) -> None:
        """Run the agent until it calls stop or hits max turns.

        Args:
            initial_message: Initial task message for the agent
        """
        response = await self._call_llm_with_tools(initial_message)

        # The agent is now running and will continue until it stops itself
        logger.info("\nAgent workflow complete")
        logger.info(f"Total turns processed: {response.id}")

    async def _call_llm_with_tools(self, user_message: str) -> Any:
        """Call the LLM using Responses API with tools enabled.

        Args:
            user_message: The user's message

        Returns:
            The response object
        """
        # Initial call (no system instructions - everything is in the user message)
        response = self.client.responses.create(
            model=self.config.model,
            input=[{"role": "user", "content": user_message}],
            conversation=self.conversation_id,
            tools=self._get_tool_definitions(),
            max_output_tokens=16000,
        )

        # Handle tool calls in a loop until agent stops or max turns reached
        turn_count = 0

        while turn_count < self.config.max_turns:
            # Check if agent called stop
            if self.agent_stopped:
                logger.info("Agent called stop tool, ending workflow")
                break

            # Check if response has tool calls
            has_tool_calls = any(
                hasattr(item, "type") and item.type == "function_call"
                for item in response.output
            )

            # Log any text output from the model (its "thinking") - always, even with tool calls
            for item in response.output:
                if hasattr(item, "type") and item.type == "message":
                    for content in item.content:
                        if hasattr(content, "type") and content.type == "output_text":
                            if content.text.strip():
                                logger.info(f"  Agent: {content.text}")

            if not has_tool_calls:
                # No tool calls - remind the agent to either continue or call stop
                logger.info("No tool calls detected, sending reminder to agent...")

                # Wait a moment for the conversation to be fully processed
                await asyncio.sleep(1)

                # Get current todo status and generate reminder
                todo_status = self.todo_tool.get_status()
                reminder_message = get_reminder_message(todo_status)
                # Retry logic for conversation lock
                max_retries = 3
                for retry in range(max_retries):
                    try:
                        response = self.client.responses.create(
                            model=self.config.model,
                            conversation=self.conversation_id,
                            input=[{"role": "user", "content": reminder_message}],
                            tools=self._get_tool_definitions(),
                            max_output_tokens=16000,
                        )
                        break
                    except BadRequestError as e:
                        if "conversation_locked" in str(e) and retry < max_retries - 1:
                            wait_time = 2**retry  # Exponential backoff: 1s, 2s, 4s
                            logger.info(
                                f"Conversation locked, waiting {wait_time}s before retry {retry + 1}/{max_retries}..."
                            )
                            await asyncio.sleep(wait_time)
                        else:
                            raise
                continue

            turn_count += 1
            logger.info(f"Turn {turn_count}/{self.config.max_turns}")

            # Build input with tool outputs
            new_input = []

            for item in response.output:
                if hasattr(item, "type") and item.type == "function_call":
                    tool_name = item.name

                    # Try to parse arguments
                    try:
                        tool_args = json.loads(item.arguments)
                    except json.JSONDecodeError as e:
                        # Pass the JSON error back to the model
                        error_msg = (
                            f"Error: Failed to parse tool arguments as JSON: {e}"
                        )
                        logger.warning(f"    JSON parse error: {e}")
                        new_input.append(
                            {
                                "type": "function_call_output",
                                "call_id": item.call_id,
                                "output": error_msg,
                            }
                        )
                        continue

                    # Log tool call with context-specific details
                    if tool_name == "bash_command":
                        logger.info(
                            f"  Calling tool: {tool_name}: {tool_args.get('command', 'N/A')}"
                        )
                    elif tool_name == "readlines":
                        path = tool_args.get("path", "N/A")
                        offset = tool_args.get("offset")
                        limit = tool_args.get("limit")
                        if offset is not None or limit is not None:
                            start = offset if offset else 1
                            end = (start + limit - 1) if limit else "EOF"
                            logger.info(
                                f"  Calling tool: {tool_name}: {path} (lines {start}-{end})"
                            )
                        else:
                            logger.info(
                                f"  Calling tool: {tool_name}: {path} (full file)"
                            )
                    elif tool_name == "writelines":
                        path = tool_args.get("path", "N/A")
                        content = tool_args.get("content", "")
                        start_line = tool_args.get("start_line")
                        end_line = tool_args.get("end_line")
                        chars = len(content)
                        lines = content.count("\n") + (
                            1 if content and not content.endswith("\n") else 0
                        )

                        if start_line is not None and end_line is not None:
                            logger.info(
                                f"  Calling tool: {tool_name}: {path} (replacing lines {start_line}-{end_line}, {lines} lines, {chars} chars)"
                            )
                        else:
                            logger.info(
                                f"  Calling tool: {tool_name}: {path} (full overwrite, {lines} lines, {chars} chars)"
                            )
                    elif tool_name == "findlines":
                        path = tool_args.get("path", "N/A")
                        pattern = tool_args.get("pattern", "N/A")
                        offset = tool_args.get("offset")
                        limit = tool_args.get("limit")
                        extra = ""
                        if offset is not None or limit is not None:
                            extra = f", offset={offset or 0}, limit={limit or 'all'}"
                        logger.info(
                            f"  Calling tool: {tool_name}: {path} (pattern: {pattern}{extra})"
                        )
                    elif tool_name in ["add_todo", "complete_todo", "remove_todo"]:
                        task = tool_args.get("task", "N/A")
                        logger.info(f"  Calling tool: {tool_name}: {task}")
                    else:
                        logger.info(f"  Calling tool: {tool_name}")

                    if tool_name != "stop":  # Don't log stop args
                        logger.debug(f"    Args: {tool_args}")

                    # Execute the tool
                    tool_result = await self._execute_tool(tool_name, tool_args)

                    # Log result (truncated)
                    if len(tool_result) > 500:
                        logger.debug(
                            f"    Result: {tool_result[:500]}... ({len(tool_result)} chars)"
                        )
                    else:
                        logger.debug(f"    Result: {tool_result}")

                    # Add tool output to input
                    new_input.append(
                        {
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": tool_result,
                        }
                    )

            # If agent called stop, don't continue
            if self.agent_stopped:
                break

            # Continue conversation with tool results
            response = self.client.responses.create(
                model=self.config.model,
                conversation=self.conversation_id,
                input=new_input,
                tools=self._get_tool_definitions(),
                max_output_tokens=16000,
            )

        if turn_count >= self.config.max_turns:
            logger.warning(
                f"Reached maximum turns ({self.config.max_turns}), stopping agent"
            )

        return response

    def _get_tool_definitions(self) -> list[FunctionToolParam]:
        """Get tool definitions for the LLM."""
        return [
            BashTool.get_tool_definition(),
            FileTool.get_readlines_tool_definition(),
            FileTool.get_writelines_tool_definition(),
            FileTool.get_findlines_tool_definition(),
            McpInterviewerTool.get_tool_definition(),
            TodoTool.get_add_todo_definition(),
            TodoTool.get_complete_todo_definition(),
            TodoTool.get_remove_todo_definition(),
            TodoTool.get_clear_todos_definition(),
            TodoTool.get_list_todos_definition(),
            StopTool.get_tool_definition(),
        ]

    async def _execute_tool(self, tool_name: str, tool_args: dict[str, Any]) -> str:
        """Execute a tool call and return the result.

        Args:
            tool_name: Name of the tool to execute
            tool_args: Arguments for the tool

        Returns:
            Tool execution result as string
        """
        if tool_name == "bash_command":
            return self.bash_tool.execute(tool_args["command"])
        elif tool_name == "readlines":
            return self.file_tool.readlines(**tool_args)
        elif tool_name == "writelines":
            return self.file_tool.writelines(**tool_args)
        elif tool_name == "findlines":
            return self.file_tool.findlines(**tool_args)
        elif tool_name == "mcp_interviewer":
            return await self.mcp_interviewer_tool.execute(
                tool_args["server_path"],
                tool_args.get("test", False),
                tool_args.get("judge_tools", False),
                tool_args.get("judge_test", False),
            )
        elif tool_name == "add_todo":
            result = self.todo_tool.add_todo(**tool_args)
            # Also log the current status
            return result + "\n\n" + self.todo_tool.get_status()
        elif tool_name == "complete_todo":
            result = self.todo_tool.complete_todo(**tool_args)
            return result + "\n\n" + self.todo_tool.get_status()
        elif tool_name == "remove_todo":
            result = self.todo_tool.remove_todo(**tool_args)
            return result + "\n\n" + self.todo_tool.get_status()
        elif tool_name == "clear_todos":
            return self.todo_tool.clear_todos()
        elif tool_name == "list_todos":
            return self.todo_tool.list_todos()
        elif tool_name == "stop":
            # Check if there are pending todos
            pending_todos = [
                t["task"] for t in self.todo_tool.todos if t["status"] == "pending"
            ]

            if pending_todos:
                # Reject stop - still have pending todos
                pending_list = "\n".join(f"  - {task}" for task in pending_todos)
                return f"""Error: Cannot stop - you have {len(pending_todos)} pending todos:

{pending_list}

Complete or remove these todos before calling stop. Use complete_todo(task) or remove_todo(task).
"""

            # Mark agent as stopped and save the summary/report
            self.agent_stopped = True
            self.stop_summary = tool_args["summary"]
            self.stop_report = tool_args["final_report"]
            return self.stop_tool.execute(**tool_args)
        else:
            return f"Error: Unknown tool '{tool_name}'"
