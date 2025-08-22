from .base import CompositeStatistic
from .server import AllServerStatistics
from .tool import AllToolStatistics


class AllStatistics(CompositeStatistic):
    def __init__(self) -> None:
        super().__init__(
            AllServerStatistics(),
            AllToolStatistics(),
        )
