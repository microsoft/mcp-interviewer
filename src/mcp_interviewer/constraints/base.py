"""Base classes and interfaces for MCP server constraints.

This module provides the foundational classes for defining and enforcing
constraints on MCP (Model Context Protocol) servers. Constraints can be
applied to validate server behavior, tool definitions, and tool results.
"""

from abc import ABC, abstractmethod
from collections.abc import Generator
from enum import StrEnum
from typing import Any

from mcp.types import CallToolResult, Tool

from ..models import ServerScoreCard


class Severity(StrEnum):
    """Severity levels for constraint violations.

    Attributes:
        WARNING: Non-critical issues that should be addressed
        CRITICAL: Critical issues that indicate serious problems
    """

    WARNING = "warning"
    CRITICAL = "critical"


class ConstraintViolation:
    """Represents a constraint violation detected during server evaluation.

    Attributes:
        constraint: The constraint that was violated
        message: Human-readable description of the violation
        severity: The severity level of the violation
    """

    def __init__(
        self,
        constraint: "Constraint",
        message: str,
        severity: Severity = Severity.WARNING,
    ):
        """Initialize a constraint violation.

        Args:
            constraint: The constraint that was violated
            message: Description of the violation
            severity: Severity level (defaults to WARNING)
        """
        self.constraint = constraint
        self.message = message
        self.severity = severity


class Constraint(ABC):
    """Abstract base class for all MCP server constraints.

    Subclasses must implement the test method to define specific
    constraint validation logic.
    """

    @abstractmethod
    def test(
        self, server: ServerScoreCard
    ) -> Generator[ConstraintViolation, None, None]:
        """Test the constraint against a server scorecard.

        Args:
            server: The server scorecard to validate

        Yields:
            ConstraintViolation: Any violations found during testing
        """
        ...


class CompositeConstraint(Constraint):
    """Composite constraint that aggregates multiple constraints.

    Allows combining multiple constraints into a single constraint
    that tests all of them sequentially.
    """

    def __init__(self, *constraints: Constraint):
        """Initialize with multiple constraints.

        Args:
            *constraints: Variable number of constraints to aggregate
        """
        self._constraints = list(constraints)

    def test(
        self, server: ServerScoreCard
    ) -> Generator[ConstraintViolation, None, None]:
        """Test all aggregated constraints against the server.

        Args:
            server: The server scorecard to validate

        Yields:
            ConstraintViolation: Violations from all child constraints
        """
        for constraint in self._constraints:
            yield from constraint.test(server)


class ToolConstraint(Constraint, ABC):
    """Abstract base class for constraints that validate individual tools."""

    @abstractmethod
    def test_tool(self, tool: Tool) -> Generator[ConstraintViolation, None, None]:
        """Test the constraint against a single tool.

        Args:
            tool: The tool to validate

        Yields:
            ConstraintViolation: Any violations found for this tool
        """
        ...

    def test(
        self, server: ServerScoreCard
    ) -> Generator[ConstraintViolation, None, None]:
        """Test the constraint against all server tools.

        Args:
            server: The server scorecard containing tools to validate

        Yields:
            ConstraintViolation: Violations from all tools
        """
        for tool in server.tools:
            yield from self.test_tool(tool)


class ToolResultConstraint(Constraint, ABC):
    """Abstract base class for constraints that validate tool execution results."""

    @abstractmethod
    def test_tool_result(
        self, result: Any
    ) -> Generator[ConstraintViolation, None, None]:
        """Test the constraint against a tool execution result.

        Args:
            result: The tool execution result to validate

        Yields:
            ConstraintViolation: Any violations found in the result
        """
        ...

    def test(
        self, server: ServerScoreCard
    ) -> Generator[ConstraintViolation, None, None]:
        """Test the constraint against all tool execution results.

        Args:
            server: The server scorecard containing test results

        Yields:
            ConstraintViolation: Violations from all tool results
        """
        for step in server.functional_test_scorecard.steps:
            if isinstance(step.tool_output, CallToolResult):
                yield from self.test_tool_result(step.tool_output)
