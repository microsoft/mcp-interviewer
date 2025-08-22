from collections.abc import Generator

from .base import CompositeStatistic, ServerScoreCard, Statistic, StatisticValue


class ToolCountStatistic(Statistic):
    def compute(self, server: ServerScoreCard) -> Generator[StatisticValue, None, None]:
        yield StatisticValue(self, len(server.tools))


class ResourceCountStatistic(Statistic):
    def compute(self, server: ServerScoreCard) -> Generator[StatisticValue, None, None]:
        yield StatisticValue(self, len(server.resources))


class ResourceTemplateCountStatistic(Statistic):
    def compute(self, server: ServerScoreCard) -> Generator[StatisticValue, None, None]:
        yield StatisticValue(self, len(server.resource_templates))


class PromptCountStatistic(Statistic):
    def compute(self, server: ServerScoreCard) -> Generator[StatisticValue, None, None]:
        yield StatisticValue(self, len(server.prompts))


class AllServerStatistics(CompositeStatistic):
    def __init__(self) -> None:
        super().__init__(
            ToolCountStatistic(),
            ResourceCountStatistic(),
            ResourceTemplateCountStatistic(),
            PromptCountStatistic(),
        )
