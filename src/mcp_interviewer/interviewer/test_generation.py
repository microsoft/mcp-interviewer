"""Functional test generation functionality."""

import logging

from .. import prompts
from ..models import Client, FunctionalTest, Server

logger = logging.getLogger(__name__)


async def generate_functional_test(
    client: Client, model: str, server: Server
) -> FunctionalTest:
    """Generate a functional test plan for the server's tools.

    Creates a comprehensive test plan with multiple steps to evaluate the server's
    functionality, including edge cases and error handling.

    Args:
        client: OpenAI client (sync or async) for LLM-based evaluation
        model: Model name to use for evaluation
        server: The Server object containing tools and capabilities to test

    Returns:
        FunctionalTest containing a test plan and steps to execute

    Raises:
        Exception: If test generation fails
    """
    try:
        logger.debug(f"Generating functional test for {len(server.tools)} tools")
        test = await prompts.generate_functional_test(client, model, server)
        logger.info(f"Generated test plan with {len(test.steps)} steps")
        logger.debug(f"Test plan: {test.plan}")
        return test
    except Exception as e:
        logger.error(f"Failed to generate functional test: {e}", exc_info=True)
        raise
