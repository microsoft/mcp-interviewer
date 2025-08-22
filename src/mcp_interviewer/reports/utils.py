"""Utility functions for report generation."""

from typing import Any

from pydantic import BaseModel

from ..models import PassFailScoreCard, ServerScoreCard


def format_score(score: str) -> str:
    """Format a score with appropriate emoji."""
    if score == "pass":
        return "✅"
    elif score == "fail":
        return "❌"
    elif score == "N/A":
        return "⚪"
    else:
        return score


def count_scores(obj: Any, path: str = "") -> tuple[int, int]:
    """Recursively count pass/fail scores. Returns (passes, total)."""
    passes = 0
    total = 0

    if isinstance(obj, PassFailScoreCard):
        if obj.score != "N/A":
            total += 1
            if obj.score == "pass":
                passes += 1
    elif isinstance(obj, BaseModel):
        for field_name in obj.model_fields_set:
            field_value = getattr(obj, field_name)
            p, t = count_scores(field_value, f"{path}.{field_name}")
            passes += p
            total += t
    elif isinstance(obj, dict):
        for key, value in obj.items():
            p, t = count_scores(value, f"{path}.{key}")
            passes += p
            total += t
    elif isinstance(obj, list):
        for item in obj:
            p, t = count_scores(item, path)
            passes += p
            total += t

    return passes, total


def get_server_info(scorecard: ServerScoreCard) -> dict[str, str | None]:
    """Extract server information from scorecard."""
    info: dict[str, str | None] = {
        "title": None,
        "name": None,
        "version": None,
        "protocol_version": None,
        "instructions": None,
    }

    if scorecard.initialize_result.serverInfo:
        server_info = scorecard.initialize_result.serverInfo
        info["title"] = server_info.title
        info["name"] = server_info.name
        info["version"] = server_info.version

    # Fallback title from parameters if not found
    if not info["title"]:
        if scorecard.parameters.connection_type == "stdio":
            info["title"] = str(scorecard.parameters.command)
            if scorecard.parameters.args:
                info["title"] += " " + " ".join(
                    str(arg) for arg in scorecard.parameters.args
                )
        else:
            # For SSE and StreamableHttp, use the URL as title
            info["title"] = str(scorecard.parameters.url)

    info["protocol_version"] = str(scorecard.initialize_result.protocolVersion)
    info["instructions"] = scorecard.initialize_result.instructions

    return info
