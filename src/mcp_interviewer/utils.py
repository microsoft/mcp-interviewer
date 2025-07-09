"""Utility functions for the MCP Interviewer package."""

from typing import Any

from loguru import logger


def validate_tool_schema(tool_schema: dict[str, Any]) -> bool:
    """Validate that a tool schema has required fields."""
    required_fields = ["name"]

    for field in required_fields:
        if field not in tool_schema:
            logger.warning(f"Tool schema missing required field: {field}")
            return False

    return True


def calculate_weighted_score(scores: list[float], weights: list[float] | None = None) -> float:
    """Calculate weighted average score."""
    if not scores:
        return 0.0

    if weights is None:
        weights = [1.0] * len(scores)

    if len(scores) != len(weights):
        raise ValueError("Scores and weights must have the same length")

    total_weight = sum(weights)
    if total_weight == 0:
        return 0.0

    weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
    return weighted_sum / total_weight
