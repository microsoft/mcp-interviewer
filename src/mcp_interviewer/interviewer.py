import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any

from mcp import ClientSession, stdio_client
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client
from mcp.shared.context import RequestContext
from mcp.types import (
    CreateMessageRequestParams,
    CreateMessageResult,
    ElicitRequestParams,
    ElicitResult,
    ListRootsResult,
    LoggingMessageNotificationParams,
    Root,
    TextContent,
    Tool,
)
from pydantic import FileUrl

from . import prompts
from .models import (
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

logger = logging.getLogger(__name__)


@asynccontextmanager
async def mcp_client(params: ServerParameters):
    """Create an MCP client based on the server connection type.

    Args:
        params: ServerParameters specifying the connection type and configuration

    Yields:
        Tuple of (read_stream, write_stream) for the MCP client connection
    """
    if params.connection_type == "stdio":
        async with stdio_client(params) as (read, write):
            yield read, write
    elif params.connection_type == "sse":
        async with sse_client(
            params.url,
            headers=params.headers,
            timeout=params.timeout,
            sse_read_timeout=params.sse_read_timeout,
        ) as (read, write):
            yield read, write
    elif params.connection_type == "streamable_http":
        async with streamablehttp_client(
            params.url,
            headers=params.headers,
            timeout=params.timeout,
            sse_read_timeout=params.sse_read_timeout,
        ) as (read, write, _):
            yield read, write
    else:
        raise ValueError(f"Unknown connection type: {params.connection_type}")


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
        should_score_tool: bool = True,
        should_score_functional_test: bool = True,
    ):
        """Initialize the MCP Interviewer.

        Args:
            client: OpenAI client (sync or async) for LLM-based evaluation
            model: Model name to use for evaluation (e.g., "gpt-4", "gpt-3.5-turbo")
            should_score_tool: Whether to perform expensive LLM scoring of tools (default: True)
            should_score_functional_test: Whether to perform expensive LLM scoring of functional tests (default: True)
        """
        self._client = client
        self._model = model
        self._should_score_tool = should_score_tool
        self._should_score_functional_test = should_score_functional_test

    async def score_tool(self, tool: Tool) -> ToolScoreCard:
        """Score a single tool based on its name, description, and schema quality.

        Args:
            tool: The Tool object to evaluate

        Returns:
            ToolScoreCard containing scores for tool name, description, and schema quality

        Raises:
            Exception: If tool scoring fails
        """
        if not self._should_score_tool:
            logger.info(f"Skipping scoring for tool '{tool.name}' (scoring disabled)")
            # Return a scorecard with N/A values
            from .models import (
                PassFailScoreCard,
                ToolDescriptionScoreCard,
                ToolNameScoreCard,
                ToolSchemaScoreCard,
            )

            na_scorecard = PassFailScoreCard(
                justification="No score generated", score="N/A"
            )

            return ToolScoreCard(
                tool_name=ToolNameScoreCard(
                    length=na_scorecard,
                    uniqueness=na_scorecard,
                    descriptiveness=na_scorecard,
                ),
                tool_description=ToolDescriptionScoreCard(
                    length=na_scorecard,
                    parameters=na_scorecard,
                    examples=na_scorecard,
                ),
                tool_input_schema=ToolSchemaScoreCard(
                    complexity=na_scorecard,
                    parameters=na_scorecard,
                    optionals=na_scorecard,
                    constraints=na_scorecard,
                ),
                tool_output_schema=ToolSchemaScoreCard(
                    complexity=na_scorecard,
                    parameters=na_scorecard,
                    optionals=na_scorecard,
                    constraints=na_scorecard,
                ),
            )

        try:
            logger.debug(f"Scoring tool '{tool.name}'")
            scorecard = await prompts.score_tool(self._client, self._model, tool)
            logger.debug(f"Tool scorecard for '{tool.name}': {scorecard}")
            return scorecard
        except Exception as e:
            logger.error(f"Failed to score tool '{tool.name}': {e}", exc_info=True)
            raise

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
        try:
            logger.debug(f"Generating functional test for {len(server.tools)} tools")
            test = await prompts.generate_functional_test(
                self._client, self._model, server
            )
            logger.info(f"Generated test plan with {len(test.steps)} steps")
            logger.debug(f"Test plan: {test.plan}")
            return test
        except Exception as e:
            logger.error(f"Failed to generate functional test: {e}", exc_info=True)
            raise

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
        start_sampling_requests = self.sampling_requests
        start_elicitation_requests = self.elicitation_requests
        start_list_roots_requests = self.list_roots_requests
        start_logging_requests = self.logging_requests
        exception = None
        try:
            logger.debug(f"Calling tool '{step.tool_name}'")
            result = await session.call_tool(step.tool_name, step.tool_arguments)
        except Exception as e:
            logger.error(
                f"Failed to execute test step '{step.tool_name}': {e}", exc_info=True
            )
            result = None
            exception = str(e)

        logger.debug(f"Tool output: {result}")
        return FunctionalTestStepOutput(
            tool_output=result,
            exception=exception,
            sampling_requests=self.sampling_requests - start_sampling_requests,
            elicitation_requests=self.elicitation_requests - start_elicitation_requests,
            list_roots_requests=self.list_roots_requests - start_list_roots_requests,
            logging_requests=self.logging_requests - start_logging_requests,
        )

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
            FunctionalTestOutput with all step outputs and aggregate request counts

        Raises:
            Exception: If any test step fails critically
        """
        logger.debug(f"Starting test execution with {len(test.steps)} steps")

        self.sampling_requests = 0
        self.elicitation_requests = 0
        self.list_roots_requests = 0
        self.logging_requests = 0

        step_outputs = []
        for i, step in enumerate(test.steps, 1):
            logger.info(f"Step {i}/{len(test.steps)}: {step.tool_name}")
            try:
                output = await self.execute_functional_test_step(session, step)
                step_outputs.append(output)
            except Exception as e:
                logger.error(f"Step {i}/{len(test.steps)} failed: {e}")
                raise

        return FunctionalTestOutput(
            sampling_requests=self.sampling_requests,
            elicitation_requests=self.elicitation_requests,
            list_roots_requests=self.list_roots_requests,
            logging_requests=self.logging_requests,
        ), step_outputs

    async def score_functional_test_step(
        self, step: FunctionalTestStep, output: FunctionalTestStepOutput
    ) -> FunctionalTestStepScoreCard:
        """Score a single functional test step output.

        Evaluates the step based on error handling, output relevance, quality,
        schema compliance, and whether it meets expectations.

        Args:
            step: The FunctionalTestStepOutput to evaluate

        Returns:
            FunctionalTestStepScoreCard with detailed scoring for the step

        Raises:
            Exception: If step scoring fails
        """
        if not self._should_score_functional_test:
            logger.info(
                f"Skipping scoring for test step '{step.tool_name}' (scoring disabled)"
            )
            from .models import ErrorType, PassFailScoreCard, ScoreCard

            na_scorecard = PassFailScoreCard(
                justification="No score generated", score="N/A"
            )

            # Create error type scorecard with the correct literal type
            na_error_type = ScoreCard[ErrorType](
                justification="No score generated", score="N/A"
            )

            return FunctionalTestStepScoreCard(
                # Include the step data
                justification=step.justification,
                expected_output=step.expected_output,
                tool_name=step.tool_name,
                tool_arguments=step.tool_arguments,
                # Include the output data
                tool_output=output.tool_output,
                exception=output.exception,
                sampling_requests=output.sampling_requests,
                elicitation_requests=output.elicitation_requests,
                list_roots_requests=output.list_roots_requests,
                logging_requests=output.logging_requests,
                # Add the evaluation rubric with N/A scores
                error_handling=na_scorecard,
                error_type=na_error_type,
                no_silent_error=na_scorecard,
                output_relevance=na_scorecard,
                output_quality=na_scorecard,
                schema_compliance=na_scorecard,
                meets_expectations=na_scorecard,
            )

        try:
            logger.debug(f"Scoring step '{step.tool_name}'")
            scorecard = await prompts.score_functional_test_step_output(
                self._client, self._model, step, output
            )
            logger.debug(f"Step scorecard: {scorecard}")
            return scorecard
        except Exception as e:
            logger.error(
                f"Failed to score test step '{step.tool_name}': {e}", exc_info=True
            )
            raise

    async def score_functional_test(
        self,
        test: FunctionalTest,
        output: FunctionalTestOutput,
        step_outputs: list[FunctionalTestStepOutput],
    ) -> FunctionalTestScoreCard:
        """Score the entire functional test output.

        Evaluates the overall test execution, including all individual steps,
        to determine if the server meets functional expectations.

        Args:
            test: The FunctionalTestOutput containing all step results

        Returns:
            FunctionalTestScoreCard with overall test scoring and individual step scores

        Raises:
            Exception: If test scoring fails
        """

        step_scorecards: list[FunctionalTestStepScoreCard] = []
        for step, step_output in zip(test.steps, step_outputs):
            step_scorecard = await self.score_functional_test_step(step, step_output)
            step_scorecards.append(step_scorecard)

        if not self._should_score_functional_test:
            logger.debug("Skipping overall functional test scoring (scoring disabled)")
            # Return a scorecard with N/A values for the overall test
            from .models import ErrorType, PassFailScoreCard, ScoreCard

            na_scorecard = PassFailScoreCard(
                justification="No score generated", score="N/A"
            )

            na_error_type = ScoreCard[ErrorType](
                justification="No score generated", score="N/A"
            )

            return FunctionalTestScoreCard(
                # Include the test plan and steps
                plan=test.plan,
                steps=step_scorecards,
                # Include the output data
                sampling_requests=output.sampling_requests,
                elicitation_requests=output.elicitation_requests,
                list_roots_requests=output.list_roots_requests,
                logging_requests=output.logging_requests,
                # Add the evaluation rubric with N/A scores
                meets_expectations=na_scorecard,
                error_type=na_error_type,
            )

        try:
            logger.debug(f"Scoring test with {len(test.steps)} steps")
            scorecard = await prompts.score_functional_test_output(
                self._client,
                self._model,
                test,
                output,
                step_scorecards,
            )
            logger.debug(f"Test scorecard: {scorecard}")
            return scorecard
        except Exception as e:
            logger.error(f"Failed to score functional test: {e}", exc_info=True)
            raise

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
        if server.connection_type == "stdio":
            logger.info(
                f"Starting server inspection for: {server.command} {' '.join(server.args or [])}"
            )
        else:
            logger.info(f"Starting server inspection for: {server.url}")
        logger.debug(f"Server parameters: {server}")

        logger.info("Initializing client session...")
        initialize_result = await session.initialize()
        await asyncio.sleep(0.2)
        logger.info("Client session initialized successfully")
        logger.debug(f"Server capabilities: {initialize_result.capabilities}")
        tools = []
        resources = []
        resource_templates = []
        prompts = []

        if initialize_result.capabilities.tools is not None:
            logger.info("Server supports tools capability - fetching tools")
            try:
                result = await session.list_tools()
                logger.debug(f"Initial tools batch: {len(result.tools)} tools")

                while result.nextCursor:
                    tools.extend(result.tools)
                    logger.debug(
                        f"Fetching next batch of tools with cursor: {result.nextCursor}"
                    )
                    result = await session.list_tools(result.nextCursor)
                    logger.debug(f"Retrieved {len(result.tools)} more tools")

                tools.extend(result.tools)
                logger.info(f"Successfully fetched {len(tools)} total tools")
                for tool in tools:
                    logger.debug(f"Tool found: {tool.name}")
            except Exception as e:
                logger.warning(f"Failed to list tools: {e}", exc_info=True)
        else:
            logger.info("Server does not support tools capability")

        if initialize_result.capabilities.resources is not None:
            logger.info("Server supports resources capability - fetching resources")
            try:
                result = await session.list_resources()
                logger.debug(
                    f"Initial resources batch: {len(result.resources)} resources"
                )

                while result.nextCursor:
                    resources.extend(result.resources)
                    logger.debug(
                        f"Fetching next batch of resources with cursor: {result.nextCursor}"
                    )
                    result = await session.list_resources(result.nextCursor)
                    logger.debug(f"Retrieved {len(result.resources)} more resources")

                resources.extend(result.resources)
                logger.info(f"Successfully fetched {len(resources)} total resources")
                for resource in resources:
                    logger.debug(
                        f"Resource found: {resource.name if hasattr(resource, 'name') else resource}"
                    )
            except Exception as e:
                logger.warning(f"Failed to list resources: {e}", exc_info=True)

            logger.info("Fetching resource templates")

            try:
                result = await session.list_resource_templates()
                logger.debug(
                    f"Initial resource templates batch: {len(result.resourceTemplates)} templates"
                )

                while result.nextCursor:
                    resource_templates.extend(result.resourceTemplates)
                    logger.debug(
                        f"Fetching next batch of resource templates with cursor: {result.nextCursor}"
                    )
                    result = await session.list_resource_templates(result.nextCursor)
                    logger.debug(
                        f"Retrieved {len(result.resourceTemplates)} more templates"
                    )

                resource_templates.extend(result.resourceTemplates)
                logger.info(
                    f"Successfully fetched {len(resource_templates)} total resource templates"
                )
                for template in resource_templates:
                    logger.debug(
                        f"Resource template found: {template.name if hasattr(template, 'name') else template}"
                    )
            except Exception as e:
                logger.warning(f"Failed to list resource templates: {e}", exc_info=True)
        else:
            logger.info("Server does not support resources capability")

        if initialize_result.capabilities.prompts is not None:
            logger.info("Server supports prompts capability - fetching prompts")
            try:
                result = await session.list_prompts()
                logger.debug(f"Initial prompts batch: {len(result.prompts)} prompts")

                while result.nextCursor:
                    prompts.extend(result.prompts)
                    logger.debug(
                        f"Fetching next batch of prompts with cursor: {result.nextCursor}"
                    )
                    result = await session.list_prompts(result.nextCursor)
                    logger.debug(f"Retrieved {len(result.prompts)} more prompts")

                prompts.extend(result.prompts)
                logger.info(f"Successfully fetched {len(prompts)} total prompts")
                for prompt in prompts:
                    logger.debug(
                        f"Prompt found: {prompt.name if hasattr(prompt, 'name') else prompt}"
                    )
            except Exception as e:
                logger.warning(f"Failed to list prompts: {e}", exc_info=True)
        else:
            logger.info("Server does not support prompts capability")

        logger.info("Server inspection completed successfully")
        logger.info(
            f"Server summary: {len(tools)} tools, {len(resources)} resources, "
            f"{len(resource_templates)} resource templates, {len(prompts)} prompts"
        )

        server_obj = Server(
            parameters=server,
            initialize_result=initialize_result,
            tools=tools,
            resources=resources,
            resource_templates=resource_templates,
            prompts=prompts,
        )
        logger.debug(f"Created Server object: {server_obj}")
        return server_obj

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
        self.sampling_requests += 1
        return CreateMessageResult(
            role="assistant",
            content=TextContent(type="text", text="Dummy content"),
            model="dummy",
        )

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
        self.elicitation_requests += 1
        return ElicitResult(action="cancel")

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
        self.list_roots_requests += 1
        return ListRootsResult(roots=[Root(uri=FileUrl("file://dummy.txt"))])

    async def logging_callback(
        self,
        params: LoggingMessageNotificationParams,
    ) -> None:
        """Callback for handling logging notifications from the server.

        Tracks the number of logging requests received.

        Args:
            params: Parameters containing the logging message
        """
        self.logging_requests += 1
        pass

    async def score_server(self, params: ServerParameters) -> ServerScoreCard:
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
                            *[self.score_tool(tool) for tool in server.tools],
                            return_exceptions=True,
                        )

                        # Log any errors from tool scoring
                        successful_scorecards = []
                        for i, scorecard in enumerate(tool_scorecards):
                            if isinstance(scorecard, Exception):
                                logger.error(
                                    f"Tool {server.tools[i].name} scoring failed: {scorecard}"
                                )
                            else:
                                successful_scorecards.append(scorecard)

                        tool_scorecards = successful_scorecards
                    else:
                        logger.info("No tools found")
                        tool_scorecards = []

                    # Phase 3: Functional Testing
                    logger.info("=" * 60)
                    logger.info("PHASE 3: Functional Testing")
                    logger.info("=" * 60)
                    functional_test = await self.generate_functional_test(server)

                    (
                        functional_test_output,
                        functional_test_step_outputs,
                    ) = await self.execute_functional_test(session, functional_test)

                    # Score functional test
                    functional_test_scorecard = await self.score_functional_test(
                        functional_test,
                        functional_test_output,
                        functional_test_step_outputs,
                    )

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
