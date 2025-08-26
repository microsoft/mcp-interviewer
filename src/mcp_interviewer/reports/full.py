from mcp_interviewer.reports.functional_test.tool_scorecards import ToolScorecardsReport

from ..constraints.base import ConstraintViolation
from ..models import ServerScoreCard
from .base import BaseReport, BaseReportOptions
from .functional_test import (
    FunctionalTestReport,
)
from .interviewer import (
    ConstraintViolationsReport,
    EmojiLegendReport,
    InterviewerInfoReport,
)
from .server import (
    CapabilitiesReport,
    PromptsReport,
    ResourcesReport,
    ResourceTemplatesReport,
    ServerInfoReport,
    ToolsReport,
)
from .statistics import ToolCallStatisticsReport, ToolStatisticsReport


class FullReport(BaseReport):
    """Complete detailed report with all information."""

    @classmethod
    def cli_name(cls) -> str:
        return "full"

    @classmethod
    def cli_code(cls) -> str:
        return "F"

    def __init__(
        self,
        scorecard: ServerScoreCard,
        violations: list[ConstraintViolation] | None = None,
        options: BaseReportOptions | None = None,
        selected_constraints: list[str] | None = None,
    ):
        """Initialize and build the full report."""
        super().__init__(scorecard, [], options)
        self._violations = violations
        self._selected_constraints = selected_constraints
        self._build()

    def _build(self):
        """Build the full report by composing submodules."""
        self.add_title("MCP Interviewer Report", 1)
        self.add_blank_line()

        self.add_report(ServerInfoReport(self._scorecard))
        self.add_report(InterviewerInfoReport(self._scorecard))
        self.add_report(CapabilitiesReport(self._scorecard))

        self.add_report(ToolStatisticsReport(self._scorecard))
        self.add_report(ToolCallStatisticsReport(self._scorecard))

        self.add_report(
            ConstraintViolationsReport(
                self._scorecard, self._violations, self._selected_constraints
            )
        )

        if self._options.score_tools:
            self.add_report(ToolScorecardsReport(scorecard=self._scorecard))

        self.add_report(
            FunctionalTestReport(
                self._scorecard, include_evaluations=self._options.score_functional_test
            )
        )

        self.add_report(ToolsReport(self._scorecard))
        self.add_report(ResourcesReport(self._scorecard))
        self.add_report(ResourceTemplatesReport(self._scorecard))
        self.add_report(PromptsReport(self._scorecard))
        self.add_report(EmojiLegendReport(self._scorecard))
