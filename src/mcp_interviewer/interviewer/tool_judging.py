"""Tool evaluation functionality."""

import logging

from mcp.types import Tool

from .. import prompts
from ..models import Client, ToolScoreCard

logger = logging.getLogger(__name__)


async def judge_tool(
    client: Client, model: str, tool: Tool, should_judge: bool = False
) -> ToolScoreCard:
    """Judge a single tool based on its name, description, and schema quality.

    Args:
        client: OpenAI client (sync or async) for LLM-based evaluation
        model: Model name to use for evaluation
        tool: The Tool object to evaluate
        should_judge: Whether to perform expensive experimental LLM judging

    Returns:
        ToolScoreCard containing scores for tool name, description, and schema quality

    Raises:
        Exception: If tool judging fails
    """
    if not should_judge:
        logger.info(f"Skipping judging for tool '{tool.name}' (judging disabled)")
        # Return a scorecard with N/A values
        from ..models import (
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
        logger.debug(f"Judging tool '{tool.name}'")
        scorecard = await prompts.judge_tool(client, model, tool)
        logger.debug(f"Tool scorecard for '{tool.name}': {scorecard}")
        return scorecard
    except Exception as e:
        logger.error(f"Failed to judge tool '{tool.name}': {e}", exc_info=True)
        raise
