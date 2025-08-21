import re
from collections.abc import Generator

from mcp.types import CallToolResult, Tool

from .base import (
    Constraint,
    ConstraintViolation,
    ServerScoreCard,
    Severity,
    ToolConstraint,
    ToolResultConstraint,
)


class OpenAIToolCountConstraint(Constraint):
    def test(
        self, server: ServerScoreCard
    ) -> Generator[ConstraintViolation, None, None]:
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
    def test_tool(self, tool: Tool) -> Generator[ConstraintViolation, None, None]:
        if len(tool.name) > 64:
            yield ConstraintViolation(
                self, "name must be at most 64 characters.", severity=Severity.CRITICAL
            )


class OpenAIToolNamePatternConstraint(ToolConstraint):
    pattern = re.compile(r"^[a-zA-Z_]+[a-zA-Z0-9_]$")

    def test_tool(self, tool: Tool) -> Generator[ConstraintViolation, None, None]:
        if not self.pattern.fullmatch(tool.name):
            yield ConstraintViolation(
                self,
                "name must be a valid python identifier.",
                severity=Severity.CRITICAL,
            )


class OpenAIToolResultTokenLengthConstraint(ToolResultConstraint):
    def test_tool_result(
        self, result: CallToolResult
    ) -> Generator[ConstraintViolation, None, None]:
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
    def __init__(self):
        self.constraints: list[Constraint] = [
            OpenAIToolCountConstraint(),
            OpenAIToolNameLengthConstraint(),
            OpenAIToolNamePatternConstraint(),
            OpenAIToolResultTokenLengthConstraint(),
        ]

    def test(
        self, server: ServerScoreCard
    ) -> Generator[ConstraintViolation, None, None]:
        for constraint in self.constraints:
            yield from constraint.test(server)
