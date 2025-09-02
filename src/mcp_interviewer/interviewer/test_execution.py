"""Test execution functionality."""

import logging

from mcp import ClientSession

from ..models import (
    FunctionalTest,
    FunctionalTestOutput,
    FunctionalTestStep,
    FunctionalTestStepOutput,
)

logger = logging.getLogger(__name__)


async def execute_functional_test_step(
    session: ClientSession,
    step: FunctionalTestStep,
    request_counters: dict[str, int],
) -> FunctionalTestStepOutput:
    """Execute a single step of a functional test.

    Calls the specified tool with the given arguments and tracks request counts
    for sampling, elicitation, list_roots, and logging operations.

    Args:
        session: The MCP ClientSession to use for tool calls
        step: The FunctionalTestStep containing tool name and arguments
        request_counters: Dict containing request counters for tracking

    Returns:
        FunctionalTestStepOutput with the tool output and request tracking data
    """
    start_sampling_requests = request_counters["sampling"]
    start_elicitation_requests = request_counters["elicitation"]
    start_list_roots_requests = request_counters["list_roots"]
    start_logging_requests = request_counters["logging"]
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
        sampling_requests=request_counters["sampling"] - start_sampling_requests,
        elicitation_requests=request_counters["elicitation"]
        - start_elicitation_requests,
        list_roots_requests=request_counters["list_roots"] - start_list_roots_requests,
        logging_requests=request_counters["logging"] - start_logging_requests,
    )


async def execute_functional_test(
    session: ClientSession,
    test: FunctionalTest,
    request_counters: dict[str, int],
) -> tuple[FunctionalTestOutput, list[FunctionalTestStepOutput]]:
    """Execute all steps of a functional test.

    Runs through all test steps sequentially, collecting outputs and tracking
    the total number of requests made during the test execution.

    Args:
        session: The MCP ClientSession to use for tool calls
        test: The FunctionalTest containing all test steps to execute
        request_counters: Dict containing request counters for tracking

    Returns:
        Tuple of (FunctionalTestOutput with aggregate request counts, list of step outputs)

    Raises:
        Exception: If any test step fails critically
    """
    logger.debug(f"Starting test execution with {len(test.steps)} steps")

    # Reset counters
    request_counters.update(
        {
            "sampling": 0,
            "elicitation": 0,
            "list_roots": 0,
            "logging": 0,
        }
    )

    step_outputs = []
    for i, step in enumerate(test.steps, 1):
        logger.info(f"Step {i}/{len(test.steps)}: {step.tool_name}")
        try:
            output = await execute_functional_test_step(session, step, request_counters)
            step_outputs.append(output)
        except Exception as e:
            logger.error(f"Step {i}/{len(test.steps)} failed: {e}")
            raise

    return FunctionalTestOutput(
        sampling_requests=request_counters["sampling"],
        elicitation_requests=request_counters["elicitation"],
        list_roots_requests=request_counters["list_roots"],
        logging_requests=request_counters["logging"],
    ), step_outputs
