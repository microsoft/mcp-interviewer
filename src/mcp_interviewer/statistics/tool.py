import json
from abc import ABC, abstractmethod
from collections.abc import Generator

from mcp.types import Tool
from tiktoken import encoding_for_model

from .base import CompositeStatistic, ServerScoreCard, Statistic, StatisticValue


class ToolStatistic(Statistic, ABC):
    @abstractmethod
    def compute_tool(self, tool: Tool) -> Generator[StatisticValue, None, None]: ...

    def compute(self, server: ServerScoreCard) -> Generator[StatisticValue, None, None]:
        for tool in server.tools:
            yield from self.compute_tool(tool)


class ToolInputSchemaTokenCount(ToolStatistic):
    def compute_tool(self, tool: Tool) -> Generator[StatisticValue, None, None]:
        input_schema = json.dumps(tool.inputSchema)
        tokenizer = encoding_for_model("gpt-4o")
        token_count = len(tokenizer.encode(input_schema))
        yield StatisticValue(self, token_count)


class AllToolStatistics(CompositeStatistic):
    def __init__(self) -> None:
        super().__init__(
            ToolInputSchemaTokenCount(),
        )
