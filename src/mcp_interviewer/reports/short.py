from ..constraints.base import ConstraintViolation
from ..models import ServerScoreCard
from .base import BaseReport, BaseReportOptions
from .functional_test import (
    FunctionalTestReport,
)
from .interviewer import (
    ConstraintViolationsReport,
    InterviewerInfoReport,
)
from .server import (
    CapabilitiesReport,
    ServerInfoReport,
)
from .statistics import ToolCallStatisticsReport, ToolStatisticsReport


class ShortReport(BaseReport):
    """Concise report suitable for README files."""

    @classmethod
    def cli_name(cls) -> str:
        return "short"

    @classmethod
    def cli_code(cls) -> str:
        return "S"

    def __init__(
        self,
        scorecard: ServerScoreCard,
        violations: list[ConstraintViolation] = [],
        options: BaseReportOptions | None = None,
        selected_constraints: list[str] | None = None,
    ):
        """Initialize and build the short report."""
        super().__init__(scorecard, violations, options)
        self._selected_constraints = selected_constraints
        self._build()

    def _build(self):
        """Build the short report by composing submodules."""
        self.add_title("MCP Interviewer Report", 1)
        self.add_blank_line()

        self.add_report(InterviewerInfoReport(self._scorecard))

        # Metadata and basic info
        self.add_report(ServerInfoReport(self._scorecard))
        self.add_report(CapabilitiesReport(self._scorecard))

        self.add_report(ToolStatisticsReport(self._scorecard))
        self.add_report(ToolCallStatisticsReport(self._scorecard))
        self.add_report(
            FunctionalTestReport(self._scorecard, include_evaluations=False)
        )

        # Scores and violations
        self.add_report(
            ConstraintViolationsReport(
                self._scorecard, self._violations, self._selected_constraints
            )
        )
