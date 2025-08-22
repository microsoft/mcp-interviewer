from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import Any

from ..models import ServerScoreCard


class StatisticValue:
    def __init__(self, statistic: "Statistic", value: Any) -> None:
        self.statistic = statistic
        self.value = value


class Statistic(ABC):
    @abstractmethod
    def compute(
        self, server: ServerScoreCard
    ) -> Generator[StatisticValue, None, None]: ...


class CompositeStatistic(Statistic):
    def __init__(self, *statistics: Statistic) -> None:
        self.statistics = list(statistics)

    def compute(self, server: ServerScoreCard) -> Generator[StatisticValue, None, None]:
        for statistic in self.statistics:
            yield from statistic.compute(server)
