"""Main MCPInterviewer class for analyzing MCP workbenches."""

import asyncio

from autogen_core.models import ChatCompletionClient
from autogen_core.tools import ToolSchema
from autogen_ext.tools.mcp import McpWorkbench
from loguru import logger

# Import patched MCP classes to ensure we get extended functionality
from .prompts import generate_overall_analysis_prompt, generate_server_analysis_prompt
from .tester import ToolTester
from .types import InterviewResults, ServerAnalysis, ToolAnalysis


class MCPInterviewer:
    """Main class for interviewing and analyzing MCP servers."""

    def __init__(
        self,
        workbenches: list[McpWorkbench],
        model_client: ChatCompletionClient | None = None,
        tool_timeout: float = 30.0,
        server_timeout: float = 300.0,
        analysis_timeout: float = 60.0,
        iterations_per_tool: int = 3,
    ):
        """Initialize the interviewer with workbenches and a model client.

        Args:
            workbenches: List of MCP workbenches to analyze. For best results with the
                patched autogen_ext.tools.mcp, create workbenches with a model_client
                parameter to enable server sampling capabilities:
                    workbench = McpWorkbench(server_params, model_client=your_model_client)
            model_client: Chat completion client for LLM-based analysis
            tool_timeout: Timeout in seconds for individual tool testing (default: 30s)
            server_timeout: Timeout in seconds for analyzing a complete server (default: 5m)
            analysis_timeout: Timeout in seconds for LLM analysis generation (default: 60s)
            iterations_per_tool: Number of test iterations to run per tool (default: 3)
        """
        self.workbenches = workbenches
        if model_client is None:
            try:
                from trapi.autogen import TrapiChatCompletionClient
            except ImportError:
                raise ImportError(
                    "trapi not found. Please install optional dependency group 'trapi'"
                )
            model_client = TrapiChatCompletionClient("gpt-4o")

        assert isinstance(model_client, ChatCompletionClient)
        self.model_client = model_client
        self.tester = ToolTester(model_client, analysis_timeout)
        self.tool_timeout = tool_timeout
        self.server_timeout = server_timeout
        self.analysis_timeout = analysis_timeout
        self.iterations_per_tool = iterations_per_tool

    async def interview(
        self,
    ) -> InterviewResults:
        """Conduct a full interview of all workbenches following iterative testing logic.

        For each workbench:
        1. Iterates over each tool in the workbench
        2. For each tool, runs multiple test iterations (configurable)
           - Generates arguments for the tool
           - Calls the tool with generated arguments
           - Records success/failure of each tool call
        3. Scores the workbench based on average tool success rate
        4. Generates qualitative analysis for the workbench

        Finally generates overall qualitative analysis across all workbenches.

        Args:
            check_tools: Whether to run tests to check if tools actually work
            rewrite_tools: Whether to suggest new tool names and descriptions

        Returns:
            Complete interview results with scores and analysis
        """
        server_analyses = []
        failed_servers = 0

        for i, workbench in enumerate(self.workbenches):
            logger.info(f"Analyzing workbench {i + 1}/{len(self.workbenches)}")
            server_name = getattr(workbench, "name", f"Server {i + 1}")

            try:
                # Apply server-level timeout to prevent hanging
                server_analysis = await asyncio.wait_for(
                    self._analyze_server(workbench, server_name),
                    timeout=self.server_timeout,
                )
                server_analyses.append(server_analysis)
            except TimeoutError:
                logger.error(
                    f"Server '{server_name}' analysis timed out after {self.server_timeout}s"
                )
                failed_servers += 1
                server_analyses.append(
                    ServerAnalysis(
                        name=server_name,
                        score=0.0,
                        analysis=f"Server analysis timed out after {self.server_timeout} seconds",
                        tools=[],
                    )
                )
            except Exception as e:
                logger.exception(f"Unexpected error analyzing server '{server_name}': {e}")
                failed_servers += 1
                server_analyses.append(
                    ServerAnalysis(
                        name=server_name,
                        score=0.0,
                        analysis=f"Server analysis failed: {str(e)}",
                        tools=[],
                    )
                )

        # Calculate overall score and analysis
        overall_score = self._calculate_overall_score(server_analyses)

        try:
            overall_analysis = await asyncio.wait_for(
                self._generate_overall_analysis(server_analyses), timeout=self.analysis_timeout
            )
        except TimeoutError:
            logger.error("Overall analysis generation timed out")
            overall_analysis = (
                f"Analysis completed with {failed_servers} failed servers. "
                f"Overall analysis generation timed out after {self.analysis_timeout}s."
            )
        except Exception as e:
            logger.exception(f"Error generating overall analysis: {e}")
            overall_analysis = (
                f"Analysis completed with {failed_servers} failed servers. "
                f"Error generating analysis: {str(e)}"
            )

        return InterviewResults(
            score=overall_score, analysis=overall_analysis, servers=server_analyses
        )

    async def _analyze_server(
        self,
        workbench: McpWorkbench,
        server_name: str,
    ) -> ServerAnalysis:
        """Analyze a single MCP server."""
        await workbench.start()

        try:
            # Collect initialize result if available (after workbench is started)
            initialize_result = None
            try:
                # Check if this is our patched workbench with initialize_result property
                if (
                    hasattr(workbench, "_actor")
                    and workbench._actor
                    and hasattr(workbench._actor, "initalize_result")
                ):
                    # Use getattr to avoid type checking issues
                    initialize_result = getattr(workbench._actor, "initalize_result", None)
                    logger.debug(
                        f"Collected initialize_result for server '{server_name}': "
                        f"{initialize_result}"
                    )
            except Exception as e:
                logger.debug(f"Could not collect initialize_result for server '{server_name}': {e}")

            # List all tools with timeout and retry
            try:
                tools = await asyncio.wait_for(
                    self._retry_operation(workbench.list_tools), timeout=30.0
                )
            except TimeoutError:
                logger.error(f"Timeout listing tools for server '{server_name}'")
                metadata = {"initialize_result": initialize_result} if initialize_result else None
                return ServerAnalysis(
                    name=server_name,
                    score=0.0,
                    analysis="Failed to list tools: operation timed out",
                    tools=[],
                    metadata=metadata,
                )
            except Exception as e:
                logger.exception(f"Error listing tools for server '{server_name}': {e}")
                metadata = {"initialize_result": initialize_result} if initialize_result else None
                return ServerAnalysis(
                    name=server_name,
                    score=0.0,
                    analysis=f"Failed to list tools: {str(e)}",
                    tools=[],
                    metadata=metadata,
                )

            tool_analyses = []
            failed_tools = 0

            # Ensure we have a valid tools list
            if not tools:
                logger.warning(f"No tools found for server '{server_name}'")
                metadata = {"initialize_result": initialize_result} if initialize_result else None
                return ServerAnalysis(
                    name=server_name,
                    score=0.0,
                    analysis="No tools found in server",
                    tools=[],
                    metadata=metadata,
                )

            # Analyze each tool with multiple iterations
            for tool in tools:
                try:
                    # Run multiple iterations for each tool
                    tool_analysis = await asyncio.wait_for(
                        self._test_tool_with_iterations(workbench, tool, self.iterations_per_tool),
                        timeout=self.tool_timeout * self.iterations_per_tool,
                    )

                    tool_analyses.append(tool_analysis)

                except TimeoutError:
                    logger.error(f"Timeout testing tool '{tool['name']}' in server '{server_name}'")
                    failed_tools += 1
                    timeout_duration = self.tool_timeout * self.iterations_per_tool
                    tool_analyses.append(
                        ToolAnalysis(
                            name=tool["name"],
                            score=0.0,
                            analysis=f"Tool testing timed out after {timeout_duration} seconds",
                            errors=["Timeout during testing"],
                        )
                    )
                except Exception as e:
                    logger.exception(f"Error testing tool '{tool['name']}': {e}")
                    failed_tools += 1
                    tool_analyses.append(
                        ToolAnalysis(
                            name=tool["name"],
                            score=0.0,
                            analysis=f"Tool testing failed: {str(e)}",
                            errors=[str(e)],
                        )
                    )

            # Calculate server score and generate analysis
            server_score = self._calculate_server_score(tool_analyses)

            try:
                server_analysis_text = await asyncio.wait_for(
                    self._generate_server_analysis(server_name, tool_analyses),
                    timeout=self.analysis_timeout,
                )
            except TimeoutError:
                logger.error(f"Timeout generating analysis for server '{server_name}'")
                server_analysis_text = (
                    f"Server '{server_name}' has {len(tool_analyses)} tools. "
                    f"Analysis generation timed out. {failed_tools} tools failed testing."
                )
            except Exception as e:
                logger.exception(f"Error generating analysis for server '{server_name}': {e}")
                server_analysis_text = (
                    f"Server '{server_name}' has {len(tool_analyses)} tools. "
                    f"Error generating analysis: {str(e)}. {failed_tools} tools failed testing."
                )

            # Prepare metadata
            metadata = {"initialize_result": initialize_result} if initialize_result else None

            return ServerAnalysis(
                name=server_name,
                score=server_score,
                analysis=server_analysis_text,
                tools=tool_analyses,
                metadata=metadata,
            )

        except Exception as e:
            logger.exception(f"Unexpected error analyzing server '{server_name}': {e}")
            # Try to get initialize_result even in error case
            error_initialize_result = None
            try:
                if (
                    hasattr(workbench, "_actor")
                    and workbench._actor
                    and hasattr(workbench._actor, "initalize_result")
                ):
                    error_initialize_result = getattr(workbench._actor, "initalize_result", None)
            except Exception:
                pass  # Ignore errors when trying to get initialize_result

            error_metadata = (
                {"initialize_result": error_initialize_result} if error_initialize_result else None
            )
            return ServerAnalysis(
                name=server_name,
                score=0.0,
                analysis=f"Failed to analyze server: {str(e)}",
                tools=[],
                metadata=error_metadata,
            )

    async def _test_tool_with_iterations(
        self, workbench: McpWorkbench, tool: ToolSchema, iterations: int
    ) -> ToolAnalysis:
        """Test a tool multiple times with generated arguments and calculate success rate."""
        tool_name = tool["name"]
        logger.info(f"Testing tool '{tool_name}' with {iterations} iterations")

        successful_calls = 0
        failed_calls = 0
        errors = []
        messages = []  # Maintain message history across iterations

        for iteration in range(iterations):
            try:
                logger.debug(f"Testing tool '{tool_name}' - iteration {iteration + 1}/{iterations}")

                # Generate arguments for this tool call, using accumulated message history
                args = await self.tester._generate_mock_args_with_llm(tool, messages)

                # Call the tool with generated arguments
                result = await workbench.call_tool(tool_name, args)

                # Check if the call was successful
                if result and not getattr(result, "isError", False):
                    successful_calls += 1
                    logger.debug(f"Tool '{tool_name}' iteration {iteration + 1} succeeded")

                    # Add the successful call to message history to encourage variation
                    from autogen_core.models import AssistantMessage

                    messages.append(
                        AssistantMessage(
                            content=f"Successfully called {tool_name} with args: {args}",
                            source="assistant",
                        )
                    )
                else:
                    failed_calls += 1
                    error_msg = getattr(result, "content", "Unknown error")
                    errors.append(f"Iteration {iteration + 1}: {error_msg}")
                    logger.debug(
                        f"Tool '{tool_name}' iteration {iteration + 1} failed: {error_msg}"
                    )

                    # Add the failed call to message history to learn from failures
                    from autogen_core.models import AssistantMessage

                    messages.append(
                        AssistantMessage(
                            content=f"Failed to call {tool_name} with args: {args}. Error: {error_msg}",
                            source="assistant",
                        )
                    )

            except Exception as e:
                failed_calls += 1
                error_msg = str(e)
                errors.append(f"Iteration {iteration + 1}: {error_msg}")
                logger.debug(
                    f"Tool '{tool_name}' iteration {iteration + 1} failed with exception: {e}"
                )

                # Add the exception to message history
                from autogen_core.models import AssistantMessage

                messages.append(
                    AssistantMessage(
                        content=f"Exception calling {tool_name}: {error_msg}", source="assistant"
                    )
                )

        # Calculate success rate as score
        total_calls = successful_calls + failed_calls
        success_rate = successful_calls / total_calls if total_calls > 0 else 0.0

        # Generate analysis text
        if success_rate == 1.0:
            analysis = f"Tool works perfectly ({successful_calls}/{total_calls} successful calls)"
        elif success_rate >= 0.8:
            analysis = f"Tool works well ({successful_calls}/{total_calls} successful calls)"
        elif success_rate >= 0.5:
            analysis = f"Tool has mixed results ({successful_calls}/{total_calls} successful calls)"
        elif success_rate > 0:
            analysis = f"Tool mostly fails ({successful_calls}/{total_calls} successful calls)"
        else:
            analysis = f"Tool completely fails (0/{total_calls} successful calls)"

        return ToolAnalysis(
            name=tool_name, score=success_rate, analysis=analysis, errors=errors if errors else None
        )

    def _calculate_server_score(self, tool_analyses: list[ToolAnalysis]) -> float:
        """Calculate overall score for a server based on average tool success rate."""
        if not tool_analyses:
            return 0.0

        total_score = sum(tool.score for tool in tool_analyses)
        return total_score / len(tool_analyses)

    def _calculate_overall_score(self, server_analyses: list[ServerAnalysis]) -> float:
        """Calculate overall score across all servers."""
        if not server_analyses:
            return 0.0

        # Weight by number of tools in each server
        total_weighted_score = 0.0
        total_tools = 0

        for server in server_analyses:
            tool_count = len(server.tools)
            if tool_count > 0:
                total_weighted_score += server.score * tool_count
                total_tools += tool_count

        return total_weighted_score / total_tools if total_tools > 0 else 0.0

    async def _generate_server_analysis(
        self, server_name: str, tool_analyses: list[ToolAnalysis]
    ) -> str:
        """Generate LLM-based analysis for a server."""
        if not tool_analyses:
            return f"Server '{server_name}' has no tools to analyze."

        prompt = generate_server_analysis_prompt(server_name, tool_analyses)

        try:
            from autogen_core.models import UserMessage

            messages = [UserMessage(source="user", content=prompt)]
            response = await asyncio.wait_for(
                self.model_client.create(messages=messages),
                timeout=self.analysis_timeout,
            )

            if hasattr(response, "content") and response.content:
                if isinstance(response.content, str):
                    return response.content.strip()
                elif isinstance(response.content, list) and len(response.content) > 0:
                    return str(response.content[0]).strip()

            # Fallback to template-based analysis
            return self._fallback_server_analysis(server_name, tool_analyses)

        except Exception as e:
            logger.warning(f"Failed to generate LLM analysis for server '{server_name}': {e}")
            return self._fallback_server_analysis(server_name, tool_analyses)

    def _fallback_server_analysis(self, server_name: str, tool_analyses: list[ToolAnalysis]) -> str:
        """Fallback template-based server analysis."""
        working_tools = len([t for t in tool_analyses if t.score > 0.5])
        total_tools = len(tool_analyses)
        avg_score = sum(t.score for t in tool_analyses) / len(tool_analyses)

        analysis = (
            f"Server '{server_name}' has {total_tools} tools with an average success rate of "
            f"{avg_score:.2%}. {working_tools} of {total_tools} tools are working reliably "
            f"(>50% success rate)."
        )

        if avg_score >= 0.9:
            analysis += " Excellent performance across all tools."
        elif avg_score >= 0.7:
            analysis += " Good overall performance with room for minor improvements."
        elif avg_score >= 0.5:
            analysis += " Mixed performance - some tools need attention."
        elif avg_score >= 0.2:
            analysis += " Poor performance - most tools have significant issues."
        else:
            analysis += " Very poor performance - server needs major fixes."

        # Add specific issues
        common_issues = []
        for tool in tool_analyses:
            common_issues.extend(tool.errors or [])

        if common_issues:
            unique_issues = list(set(common_issues))
            analysis += f" Common issues: {', '.join(unique_issues[:3])}"

        return analysis

    async def _generate_overall_analysis(self, server_analyses: list[ServerAnalysis]) -> str:
        """Generate LLM-based overall analysis across all servers."""
        if not server_analyses:
            return "No servers analyzed."

        prompt = generate_overall_analysis_prompt(server_analyses)

        try:
            from autogen_core.models import UserMessage

            messages = [UserMessage(source="user", content=prompt)]
            response = await asyncio.wait_for(
                self.model_client.create(messages=messages),
                timeout=self.analysis_timeout,
            )

            if hasattr(response, "content") and response.content:
                if isinstance(response.content, str):
                    return response.content.strip()
                elif isinstance(response.content, list) and len(response.content) > 0:
                    return str(response.content[0]).strip()

            # Fallback to template-based analysis
            return self._fallback_overall_analysis(server_analyses)

        except Exception as e:
            logger.warning(f"Failed to generate LLM overall analysis: {e}")
            return self._fallback_overall_analysis(server_analyses)

    def _fallback_overall_analysis(self, server_analyses: list[ServerAnalysis]) -> str:
        """Fallback template-based overall analysis."""
        total_servers = len(server_analyses)
        total_tools = sum(len(server.tools) for server in server_analyses)
        working_servers = len([s for s in server_analyses if s.score > 0.7])

        # Calculate overall success rate
        if total_tools > 0:
            total_score = sum(server.score * len(server.tools) for server in server_analyses)
            overall_success_rate = total_score / total_tools
        else:
            overall_success_rate = 0.0

        analysis = (
            f"Analyzed {total_servers} servers with {total_tools} total tools across "
            f"multiple test iterations. Overall success rate: {overall_success_rate:.2%}. "
            f"{working_servers} servers are performing well (>70% success rate)."
        )

        if overall_success_rate >= 0.9:
            analysis += " Excellent performance across the entire MCP ecosystem."
        elif overall_success_rate >= 0.7:
            analysis += " Good overall ecosystem health with minor issues to address."
        elif overall_success_rate >= 0.5:
            analysis += " Mixed ecosystem performance - several areas need improvement."
        elif overall_success_rate >= 0.2:
            analysis += " Poor ecosystem health - significant improvements needed across servers."
        else:
            analysis += " Critical ecosystem issues - major overhaul required for most servers."

        return analysis

    async def _retry_operation(self, operation, max_retries: int = 3, delay: float = 1.0):
        """Retry an operation with exponential backoff."""
        for attempt in range(max_retries):
            try:
                result = operation()
                if asyncio.iscoroutine(result):
                    return await result
                else:
                    return result
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    raise e

                wait_time = delay * (2**attempt)  # Exponential backoff
                logger.warning(
                    f"Operation failed (attempt {attempt + 1}/{max_retries}), "
                    f"retrying in {wait_time}s: {e}"
                )
                await asyncio.sleep(wait_time)
