from abc import ABC, abstractmethod
from collections.abc import Generator
from enum import StrEnum
from typing import Any

from mcp.types import CallToolResult, Tool

from ..models import ServerScoreCard


class Severity(StrEnum):
    WARNING = "warning"
    CRITICAL = "critical"


class ConstraintViolation:
    def __init__(
        self,
        constraint: "Constraint",
        message: str,
        severity: Severity = Severity.WARNING,
    ):
        self.constraint = constraint
        self.message = message
        self.severity = severity


class Constraint(ABC):
    @abstractmethod
    def test(
        self, server: ServerScoreCard
    ) -> Generator[ConstraintViolation, None, None]: ...


class CompositeConstraint(Constraint):
    def __init__(self, *constraints: Constraint):
        self._constraints = list(constraints)

    def test(
        self, server: ServerScoreCard
    ) -> Generator[ConstraintViolation, None, None]:
        for constraint in self._constraints:
            yield from constraint.test(server)


class ToolConstraint(Constraint, ABC):
    @abstractmethod
    def test_tool(self, tool: Tool) -> Generator[ConstraintViolation, None, None]: ...

    def test(
        self, server: ServerScoreCard
    ) -> Generator[ConstraintViolation, None, None]:
        for tool in server.tools:
            yield from self.test_tool(tool)


class ToolResultConstraint(Constraint, ABC):
    @abstractmethod
    def test_tool_result(
        self, result: Any
    ) -> Generator[ConstraintViolation, None, None]: ...

    def test(
        self, server: ServerScoreCard
    ) -> Generator[ConstraintViolation, None, None]:
        for step in server.functional_test_scorecard.steps:
            if isinstance(step.tool_output, CallToolResult):
                yield from self.test_tool_result(step.tool_output)
