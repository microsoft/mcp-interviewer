from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Generator

from mcp.types import TextResourceContents
from tiktoken import encoding_for_model

from ..models import FunctionalTestStepScoreCard
from .base import CompositeStatistic, ServerScoreCard, Statistic, StatisticValue


class FunctionalTestStepStatistic(Statistic, ABC):
    @abstractmethod
    def compute_test_step(
        self, step: FunctionalTestStepScoreCard
    ) -> Generator[StatisticValue, None, None]: ...

    def compute(self, server: ServerScoreCard) -> Generator[StatisticValue, None, None]:
        for step in server.functional_test_scorecard.steps:
            yield from self.compute_test_step(step)


class ToolCallOutputTokenCount(FunctionalTestStepStatistic):
    def compute_test_step(
        self, step: FunctionalTestStepScoreCard
    ) -> Generator[StatisticValue, None, None]:
        if step.tool_output:
            tool_output_text = ""
            for content in step.tool_output.content:
                if content.type == "text" and content.text:
                    tool_output_text += content.text
                elif (
                    content.type == "resource"
                    and isinstance(content.resource, TextResourceContents)
                    and content.resource.text
                ):
                    tool_output_text += content.resource.text
            tokenizer = encoding_for_model("gpt-4o")
            token_count = len(tokenizer.encode(tool_output_text))
            yield StatisticValue(self, token_count)


class ToolCallOutputContentTypeDistribution(FunctionalTestStepStatistic):
    def merge_distributions(self, *distributions: dict[str, int]):
        merged = defaultdict(int)
        for dist in distributions:
            for key, value in dist.items():
                merged[key] += value
        return merged

    def compute_test_step(
        self, step: FunctionalTestStepScoreCard
    ) -> Generator[StatisticValue, None, None]:
        if step.tool_output:
            distribution = defaultdict(int)
            for content in step.tool_output.content:
                distribution[content.type] += 1

            yield StatisticValue(self, distribution)


class ToolCallHasOutputStatistic(FunctionalTestStepStatistic):
    def compute_test_step(
        self, step: FunctionalTestStepScoreCard
    ) -> Generator[StatisticValue, None, None]:
        yield StatisticValue(self, 1 if step.tool_output else 0)


class ToolCallOutputIsErrorStatistic(FunctionalTestStepStatistic):
    def compute_test_step(
        self, step: FunctionalTestStepScoreCard
    ) -> Generator[StatisticValue, None, None]:
        yield StatisticValue(
            self, 1 if (step.tool_output and step.tool_output.isError) else 0
        )


class ToolCallHasExceptionStatistic(FunctionalTestStepStatistic):
    def compute_test_step(
        self, step: FunctionalTestStepScoreCard
    ) -> Generator[StatisticValue, None, None]:
        yield StatisticValue(self, 1 if step.exception else 0)


class AllFunctionalTestStepStatistics(CompositeStatistic):
    def __init__(self) -> None:
        super().__init__(
            ToolCallOutputTokenCount(),
            ToolCallOutputContentTypeDistribution(),
        )
