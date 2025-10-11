"""OpenAI-specific constraints for MCP server validation.

This module implements constraints based on OpenAI's requirements
and recommendations for tools that will be used with OpenAI models.
These constraints help ensure MCP servers are compatible with
OpenAI's API limits and best practices.
"""

import re
from collections.abc import Generator

from mcp.types import CallToolResult, Tool
from pydantic import HttpUrl

from .base import (
    Constraint,
    ConstraintViolation,
    ServerScoreCard,
    Severity,
    SourceUrl,
    ToolConstraint,
    ToolResultConstraint,
)


class OpenAIToolCountConstraint(Constraint):
    """Validates the total number of tools exposed by the server.

    OpenAI has limits on the number of tools that can be used:
    - Hard limit: 128 tools maximum
    - Recommended: Less than 20 tools for optimal performance
    """

    @classmethod
    def cli_name(cls) -> str:
        """Return the CLI-friendly name for this constraint."""
        return "openai-tool-count"

    @classmethod
    def cli_code(cls) -> str:
        """Return the shorthand code for this constraint."""
        return "OTC"

    @classmethod
    def sources(cls) -> list[SourceUrl]:
        return [
            HttpUrl(
                "https://platform.openai.com/docs/guides/function-calling#best-practices-for-defining-functions"
            )
        ]

    def test(
        self, server: ServerScoreCard
    ) -> Generator[ConstraintViolation, None, None]:
        """Test if the server has an acceptable number of tools.

        Args:
            server: The server scorecard to validate

        Yields:
            ConstraintViolation: Critical if > 128 tools, warning if >= 20 tools
        """
        if len(server.tools) > 128:
            yield ConstraintViolation(
                self,
                "server must contain at most 128 tools.",
                severity=Severity.CRITICAL,
            )
        elif len(server.tools) >= 20:
            yield ConstraintViolation(
                self,
                "server should contain less than 20 tools.",
                severity=Severity.WARNING,
            )


class OpenAIToolNameLengthConstraint(ToolConstraint):
    """Validates that tool names meet OpenAI's length requirements.

    OpenAI requires tool names to be at most 64 characters long.
    """

    @classmethod
    def cli_name(cls) -> str:
        """Return the CLI-friendly name for this constraint."""
        return "openai-name-length"

    @classmethod
    def cli_code(cls) -> str:
        """Return the shorthand code for this constraint."""
        return "ONL"

    @classmethod
    def sources(cls) -> list[SourceUrl]:
        return [
            HttpUrl(
                "https://github.com/openai/openai-python/blob/e5f93f5daee9f3fc7646833ac235b1693f192a56/src/openai/types/shared_params/function_definition.py#L17-L18"
            )
        ]

    def test_tool(self, tool: Tool) -> Generator[ConstraintViolation, None, None]:
        """Test if the tool name meets length requirements.

        Args:
            tool: The tool to validate

        Yields:
            ConstraintViolation: Critical if name exceeds 64 characters
        """
        if len(tool.name) > 64:
            yield ConstraintViolation(
                self, "name must be at most 64 characters.", severity=Severity.CRITICAL
            )


class OpenAIToolNamePatternConstraint(ToolConstraint):
    """Validates that tool names follow OpenAI's naming pattern requirements.

    OpenAI requires tool names to be valid Python identifiers:
    - Must start with a letter or underscore
    - Can contain letters, numbers, and underscores
    - Must be at least 1 character long
    """

    @classmethod
    def cli_name(cls) -> str:
        """Return the CLI-friendly name for this constraint."""
        return "openai-name-pattern"

    @classmethod
    def cli_code(cls) -> str:
        """Return the shorthand code for this constraint."""
        return "ONP"

    @classmethod
    def sources(cls) -> list[SourceUrl]:
        return [
            HttpUrl(
                "https://github.com/openai/openai-python/blob/e5f93f5daee9f3fc7646833ac235b1693f192a56/src/openai/types/shared_params/function_definition.py#L17-L18"
            )
        ]

    pattern = re.compile(r"^[a-zA-Z_]+[a-zA-Z0-9_]*$")

    def test_tool(self, tool: Tool) -> Generator[ConstraintViolation, None, None]:
        """Test if the tool name follows the required pattern.

        Args:
            tool: The tool to validate

        Yields:
            ConstraintViolation: Critical if name doesn't match pattern
        """
        if not self.pattern.fullmatch(tool.name):
            yield ConstraintViolation(
                self,
                "name must be a valid python identifier.",
                severity=Severity.CRITICAL,
            )


class OpenAIToolResultTokenLengthConstraint(ToolResultConstraint):
    """Validates that tool results don't exceed token limits for OpenAI models.

    Different OpenAI models have different context window limits.
    This constraint checks that tool results fit within these limits
    for various model families.
    """

    @classmethod
    def cli_name(cls) -> str:
        """Return the CLI-friendly name for this constraint."""
        return "openai-token-length"

    @classmethod
    def cli_code(cls) -> str:
        """Return the shorthand code for this constraint."""
        return "OTL"

    @classmethod
    def sources(cls) -> list[SourceUrl]:
        return [HttpUrl("https://platform.openai.com/docs/models/compare")]

    def test_tool_result(
        self, result: CallToolResult
    ) -> Generator[ConstraintViolation, None, None]:
        """Test if tool result fits within token limits for OpenAI models.

        Args:
            result: The tool execution result to validate

        Yields:
            ConstraintViolation: Critical if result exceeds any model's token limit
        """
        from tiktoken import encoding_for_model

        # TODO: Correctly stringify CallToolResult
        result_str = str(result)

        for model, max_length in [
            ("gpt-4.1", 1_000_000),
            ("gpt-4o", 128_000),
            ("o1", 200_000),
            ("o3", 200_000),
            ("o4-mini", 200_000),
        ]:
            encoding = encoding_for_model(model)
            tokens = encoding.encode(result_str)
            if len(tokens) > max_length:
                yield ConstraintViolation(
                    self,
                    f"tool call result exceeds max token length {max_length} for model family {model}",
                    severity=Severity.CRITICAL,
                )


class OpenAIConstraints(Constraint):
    """Composite constraint that aggregates all OpenAI-specific constraints.

    This class provides a convenient way to apply all OpenAI-related
    constraints at once when validating an MCP server for OpenAI compatibility.
    """

    @classmethod
    def cli_name(cls) -> str:
        """Return the CLI-friendly name for all OpenAI constraints."""
        return "openai-all"

    @classmethod
    def cli_code(cls) -> str:
        """Return the shorthand code for all OpenAI constraints."""
        return "OA"

    def __init__(self):
        """Initialize with all OpenAI-specific constraints."""
        self.constraints: list[Constraint] = [
            OpenAIToolCountConstraint(),
            OpenAIToolNameLengthConstraint(),
            OpenAIToolNamePatternConstraint(),
            OpenAIToolResultTokenLengthConstraint(),
        ]

    def test(
        self, server: ServerScoreCard
    ) -> Generator[ConstraintViolation, None, None]:
        """Test all OpenAI constraints against the server.

        Args:
            server: The server scorecard to validate

        Yields:
            ConstraintViolation: Any violations from all OpenAI constraints
        """
        for constraint in self.constraints:
            yield from constraint.test(server)
