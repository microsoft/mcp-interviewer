import asyncio
import logging
from typing import Any

from mcp import ClientSession
from mcp.shared.context import RequestContext
from mcp.types import (
    CreateMessageRequestParams,
    CreateMessageResult,
    ElicitRequestParams,
    ElicitResult,
    ListRootsResult,
    LoggingMessageNotificationParams,
    Tool,
)

from ..models import (
    Client,
    FunctionalTest,
    FunctionalTestOutput,
    FunctionalTestScoreCard,
    FunctionalTestStep,
    FunctionalTestStepOutput,
    FunctionalTestStepScoreCard,
    Server,
    ServerParameters,
    ServerScoreCard,
    ToolScoreCard,
)
from .callbacks import (
    create_request_counters,
    elicitation_callback,
    list_roots_callback,
    logging_callback,
    sampling_callback,
)
from .connection import mcp_client
from .inspection import inspect_server
from .test_execution import execute_functional_test, execute_functional_test_step
from .test_generation import generate_functional_test
from .test_judging import (
    judge_functional_test as _judge_functional_test,
)
from .test_judging import (
    judge_functional_test_step as _judge_functional_test_step,
)
from .tool_judging import judge_tool as _judge_tool

logger = logging.getLogger(__name__)


class MCPInterviewer:
    """Main class for evaluating MCP servers.

    The MCPInterviewer orchestrates the complete evaluation process for MCP servers,
    including server inspection, tool quality assessment, and functional testing.
    It uses an LLM to generate tests and score the server's capabilities.
    """

    def __init__(
        self,
        client: Client,
        model: str,
        should_run_functional_test: bool = False,
        should_judge_tool: bool = False,
        should_judge_functional_test: bool = False,
    ):
        """Initialize the MCP Interviewer.

        Args:
            client: OpenAI client (sync or async) for LLM-based evaluation
            model: Model name to use for evaluation (e.g., "gpt-4o")
            should_judge_tool: Whether to perform expensive experimental LLM judging of tools (default: False)
            should_judge_functional_test: Whether to perform expensive experimental LLM judging of functional tests (default: False)
        """
        self._client = client
        self._model = model
        self._should_run_functional_test = should_run_functional_test
        self._should_judge_tool = should_judge_tool
        self._should_judge_functional_test = should_judge_functional_test
        self._request_counters = create_request_counters()

    async def judge_tool(self, tool: Tool) -> ToolScoreCard:
        """Judge a single tool based on its name, description, and schema quality.

        Args:
            tool: The Tool object to evaluate

        Returns:
            ToolScoreCard containing scores for tool name, description, and schema quality

        Raises:
            Exception: If tool judging fails
        """
        return await _judge_tool(
            self._client, self._model, tool, self._should_judge_tool
        )

    async def generate_functional_test(self, server: Server) -> FunctionalTest:
        """Generate a functional test plan for the server's tools.

        Creates a comprehensive test plan with multiple steps to evaluate the server's
        functionality, including edge cases and error handling.

        Args:
            server: The Server object containing tools and capabilities to test

        Returns:
            FunctionalTest containing a test plan and steps to execute

        Raises:
            Exception: If test generation fails
        """
        return await generate_functional_test(self._client, self._model, server)

    async def execute_functional_test_step(
        self, session: ClientSession, step: FunctionalTestStep
    ) -> FunctionalTestStepOutput:
        """Execute a single step of a functional test.

        Calls the specified tool with the given arguments and tracks request counts
        for sampling, elicitation, list_roots, and logging operations.

        Args:
            session: The MCP ClientSession to use for tool calls
            step: The FunctionalTestStep containing tool name and arguments

        Returns:
            FunctionalTestStepOutput with the tool output and request tracking data
        """
        return await execute_functional_test_step(session, step, self._request_counters)

    async def execute_functional_test(
        self, session: ClientSession, test: FunctionalTest
    ) -> tuple[FunctionalTestOutput, list[FunctionalTestStepOutput]]:
        """Execute all steps of a functional test.

        Runs through all test steps sequentially, collecting outputs and tracking
        the total number of requests made during the test execution.

        Args:
            session: The MCP ClientSession to use for tool calls
            test: The FunctionalTest containing all test steps to execute

        Returns:
            Tuple of (FunctionalTestOutput with aggregate request counts, list of step outputs)

        Raises:
            Exception: If any test step fails critically
        """
        return await execute_functional_test(session, test, self._request_counters)

    async def judge_functional_test_step(
        self, step: FunctionalTestStep, output: FunctionalTestStepOutput
    ) -> FunctionalTestStepScoreCard:
        """Judge a single functional test step output.

        Evaluates the step based on error handling, output relevance, quality,
        schema compliance, and whether it meets expectations.

        Args:
            step: The FunctionalTestStep to evaluate
            output: The FunctionalTestStepOutput to evaluate

        Returns:
            FunctionalTestStepScoreCard with detailed judging for the step

        Raises:
            Exception: If step judging fails
        """
        return await _judge_functional_test_step(
            self._client,
            self._model,
            step,
            output,
            self._should_judge_functional_test,
        )

    async def judge_functional_test(
        self,
        test: FunctionalTest,
        output: FunctionalTestOutput,
        step_outputs: list[FunctionalTestStepOutput],
    ) -> FunctionalTestScoreCard:
        """Judge the entire functional test output.

        Evaluates the overall test execution, including all individual steps,
        to determine if the server meets functional expectations.

        Args:
            test: The FunctionalTest containing test plan and steps
            output: The FunctionalTestOutput containing all step results
            step_outputs: List of individual step outputs

        Returns:
            FunctionalTestScoreCard with overall test judging and individual step scores

        Raises:
            Exception: If test judging fails
        """
        return await _judge_functional_test(
            self._client,
            self._model,
            test,
            output,
            step_outputs,
            self._should_judge_functional_test,
        )

    async def inspect_server(
        self, server: ServerParameters, session: ClientSession
    ) -> Server:
        """Inspect an MCP server to discover its capabilities and features.

        Initializes the server connection and retrieves all available tools,
        resources, resource templates, and prompts based on the server's
        advertised capabilities.

        Args:
            server: ServerParameters for launching the server
            session: The MCP ClientSession to use for inspection

        Returns:
            Server object containing all discovered features and capabilities
        """
        return await inspect_server(server, session)

    async def sampling_callback(
        self,
        context: RequestContext["ClientSession", Any],
        params: CreateMessageRequestParams,
    ) -> CreateMessageResult:
        """Callback for handling sampling requests from the server.

        Tracks the number of sampling requests and returns a dummy response.

        Args:
            context: The request context from the MCP session
            params: Parameters for the message creation request

        Returns:
            CreateMessageResult with dummy content
        """
        return await sampling_callback(self._request_counters, context, params)

    async def elicitation_callback(
        self,
        context: RequestContext["ClientSession", Any],
        params: ElicitRequestParams,
    ) -> ElicitResult:
        """Callback for handling elicitation requests from the server.

        Tracks the number of elicitation requests and cancels them.

        Args:
            context: The request context from the MCP session
            params: Parameters for the elicitation request

        Returns:
            ElicitResult with cancel action
        """
        return await elicitation_callback(self._request_counters, context, params)

    async def list_roots_callback(
        self,
        context: RequestContext["ClientSession", Any],
    ) -> ListRootsResult:
        """Callback for handling list roots requests from the server.

        Tracks the number of list roots requests and returns a dummy root.

        Args:
            context: The request context from the MCP session

        Returns:
            ListRootsResult with a dummy file root
        """
        return await list_roots_callback(self._request_counters, context)

    async def logging_callback(
        self,
        params: LoggingMessageNotificationParams,
    ) -> None:
        """Callback for handling logging notifications from the server.

        Tracks the number of logging requests received.

        Args:
            params: Parameters containing the logging message
        """
        return await logging_callback(self._request_counters, params)

    # Properties for backward compatibility with request counter attributes
    @property
    def sampling_requests(self) -> int:
        """Get the current number of sampling requests."""
        return self._request_counters["sampling"]

    @property
    def elicitation_requests(self) -> int:
        """Get the current number of elicitation requests."""
        return self._request_counters["elicitation"]

    @property
    def list_roots_requests(self) -> int:
        """Get the current number of list roots requests."""
        return self._request_counters["list_roots"]

    @property
    def logging_requests(self) -> int:
        """Get the current number of logging requests."""
        return self._request_counters["logging"]

    async def interview_server(self, params: ServerParameters) -> ServerScoreCard:
        """Perform a complete evaluation of an MCP server.

        This is the main entry point that orchestrates the entire evaluation process:
        1. Server inspection to discover capabilities
        2. Tool quality assessment for all discovered tools
        3. Functional testing to verify server behavior
        4. Compilation of results into a comprehensive scorecard

        Args:
            params: ServerParameters for launching and connecting to the server

        Returns:
            ServerScoreCard containing complete evaluation results including:
            - Server information and capabilities
            - Individual tool scorecards
            - Functional test results
            - Overall scoring metrics

        Raises:
            Exception: If server evaluation fails at any stage
        """
        logger.info("=" * 60)
        if params.connection_type == "stdio":
            logger.info(f"Starting MCP Server Evaluation: {params.command}")
        else:
            logger.info(f"Starting MCP Server Evaluation: {params.url}")
        logger.info("=" * 60)

        try:
            async with mcp_client(params) as (read, write):
                async with ClientSession(
                    read,
                    write,
                    sampling_callback=self.sampling_callback,
                    elicitation_callback=self.elicitation_callback,
                    list_roots_callback=self.list_roots_callback,
                    logging_callback=self.logging_callback,
                ) as session:
                    # Phase 1: Server Inspection
                    logger.info("=" * 60)
                    logger.info("PHASE 1: Server Inspection")
                    logger.info("=" * 60)
                    server = await self.inspect_server(params, session)

                    # Phase 2: Tool Scoring
                    logger.info("=" * 60)
                    logger.info("PHASE 2: Tool Quality Assessment")
                    logger.info("=" * 60)
                    if server.tools:
                        logger.info(f"Evaluating {len(server.tools)} tools")
                        tool_scorecards = await asyncio.gather(
                            *[self.judge_tool(tool) for tool in server.tools],
                            return_exceptions=True,
                        )

                        # Log any errors from tool judging
                        successful_scorecards = []
                        for i, scorecard in enumerate(tool_scorecards):
                            if isinstance(scorecard, Exception):
                                logger.error(
                                    f"Tool {server.tools[i].name} judging failed: {scorecard}"
                                )
                            else:
                                successful_scorecards.append(scorecard)

                        tool_scorecards = successful_scorecards
                    else:
                        logger.info("No tools found")
                        tool_scorecards = []

                    # Phase 3: Functional Testing
                    if self._should_run_functional_test:
                        logger.info("=" * 60)
                        logger.info("PHASE 3: Functional Testing")
                        logger.info("=" * 60)

                        functional_test = await self.generate_functional_test(server)

                        (
                            functional_test_output,
                            functional_test_step_outputs,
                        ) = await self.execute_functional_test(session, functional_test)

                        # Judge functional test
                        functional_test_scorecard = await self.judge_functional_test(
                            functional_test,
                            functional_test_output,
                            functional_test_step_outputs,
                        )
                    else:
                        logger.info("=" * 60)
                        logger.info("PHASE 3: Functional Testing - SKIPPED")
                        logger.info("=" * 60)
                        functional_test_scorecard = None

                    # Create final scorecard
                    logger.info("Creating final server scorecard")
                    scorecard = ServerScoreCard(
                        **server.model_dump(),
                        model=self._model,
                        tool_scorecards=tool_scorecards,
                        functional_test_scorecard=functional_test_scorecard,
                    )

                    logger.info("=" * 60)
                    logger.info("Evaluation Complete")
                    logger.info("=" * 60)

                    return scorecard
        except Exception as e:
            logger.error(f"Evaluation failed: {e}", exc_info=True)
            logger.error("=" * 60)
            raise
