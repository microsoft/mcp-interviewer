"""Constraints package for MCP server validation.

This package provides a framework for defining and enforcing constraints
on MCP (Model Context Protocol) servers to ensure compatibility with
various AI providers and best practices.
"""

from .base import CompositeConstraint, Constraint
from .openai import (
    OpenAIConstraints,
    OpenAIToolCountConstraint,
    OpenAIToolNameLengthConstraint,
    OpenAIToolNamePatternConstraint,
    OpenAIToolResultTokenLengthConstraint,
)
from .tool_schema_flatness import ToolInputSchemaFlatnessConstraint


class AllConstraints(CompositeConstraint):
    """Aggregates all available constraints for comprehensive validation.

    This class combines all provider-specific and general constraints
    to provide a complete validation suite for MCP servers.
    """

    def __init__(self):
        """Initialize with all available constraint sets."""
        super().__init__(
            OpenAIConstraints(),
            ToolInputSchemaFlatnessConstraint(),
        )


# All available constraint classes
ALL_CONSTRAINT_CLASSES = [
    OpenAIToolCountConstraint,
    OpenAIToolNameLengthConstraint,
    OpenAIToolNamePatternConstraint,
    OpenAIToolResultTokenLengthConstraint,
    ToolInputSchemaFlatnessConstraint,
]

# Create mappings for names and codes
CONSTRAINT_MAPPING = {cls.cli_name(): cls for cls in ALL_CONSTRAINT_CLASSES}
SHORTHAND_MAPPING = {cls.cli_code(): cls.cli_name() for cls in ALL_CONSTRAINT_CLASSES}

# Also add the composite constraint
CONSTRAINT_MAPPING[OpenAIConstraints.cli_name()] = OpenAIConstraints
SHORTHAND_MAPPING[OpenAIConstraints.cli_code()] = OpenAIConstraints.cli_name()


def get_selected_constraints(
    selected: list[str] | None = None,
) -> list[type[Constraint]]:
    """Get list of constraint classes based on selection.

    Args:
        selected: List of constraint names or codes to include (all if None)

    Returns:
        List of constraint classes to use
    """
    if not selected:
        # Default to all individual constraints (not the composite)
        return ALL_CONSTRAINT_CLASSES

    result = []
    for item in selected:
        # Check if it's a shorthand code
        if item in SHORTHAND_MAPPING:
            constraint_name = SHORTHAND_MAPPING[item]
        else:
            constraint_name = item

        if constraint_name in CONSTRAINT_MAPPING:
            constraint_class = CONSTRAINT_MAPPING[constraint_name]
            if constraint_class == OpenAIConstraints:
                # If OpenAIConstraints is selected, add all OpenAI constraints
                result.extend(ALL_CONSTRAINT_CLASSES)
            else:
                result.append(constraint_class)

    # Remove duplicates while preserving order
    seen = set()
    unique_result = []
    for cls in result:
        if cls not in seen:
            seen.add(cls)
            unique_result.append(cls)

    return unique_result
