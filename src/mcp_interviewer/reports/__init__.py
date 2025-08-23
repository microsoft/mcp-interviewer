"""Report generation for MCP Server evaluation."""

from ..constraints.base import ConstraintViolation
from ..models import ServerScoreCard
from .base import BaseReport
from .functional_test import (
    FunctionalTestReport,
    ScoreSummaryReport,
    ToolScorecardsReport,
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
from .utils import count_scores, format_score, get_server_info


class ShortReport(BaseReport):
    """Concise report suitable for README files."""

    def __init__(
        self,
        scorecard: ServerScoreCard,
        violations: list[ConstraintViolation] = [],
    ):
        """Initialize and build the short report."""
        super().__init__(scorecard, violations)
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
        self.add_report(ConstraintViolationsReport(self._scorecard, self._violations))


class FullReport(BaseReport):
    """Complete detailed report with all information."""

    def __init__(
        self,
        scorecard: ServerScoreCard,
        violations: list[ConstraintViolation] | None = None,
    ):
        """Initialize and build the full report."""
        super().__init__(scorecard)
        self._violations = violations
        self._build()

    def _build(self):
        """Build the full report by composing submodules."""
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
        self.add_report(ConstraintViolationsReport(self._scorecard, self._violations))

        self.add_report(ToolsReport(self._scorecard))
        self.add_report(ResourcesReport(self._scorecard))
        self.add_report(ResourceTemplatesReport(self._scorecard))
        self.add_report(PromptsReport(self._scorecard))
        self.add_report(EmojiLegendReport(self._scorecard))


class AIReport(BaseReport):
    """Complete detailed report with all information."""

    def __init__(
        self,
        scorecard: ServerScoreCard,
        violations: list[ConstraintViolation] | None = None,
    ):
        """Initialize and build the full report."""
        super().__init__(scorecard)
        self._violations = violations
        self._build()

    def _build(self):
        """Build the full report by composing submodules."""
        self.add_title("MCP Interviewer Report", 1)
        self.add_blank_line()

        self.add_report(InterviewerInfoReport(self._scorecard))

        # Metadata and basic info
        self.add_report(ServerInfoReport(self._scorecard))
        self.add_report(CapabilitiesReport(self._scorecard))

        # Stats
        self.add_report(ToolStatisticsReport(self._scorecard))
        self.add_report(ToolCallStatisticsReport(self._scorecard))

        # AI evaluations
        self.add_report(ScoreSummaryReport(self._scorecard, detailed=True))
        self.add_report(ToolScorecardsReport(self._scorecard))
        self.add_report(FunctionalTestReport(self._scorecard, include_evaluations=True))

        # Scores and violations
        self.add_report(ConstraintViolationsReport(self._scorecard, self._violations))

        # More info
        self.add_report(ToolsReport(self._scorecard))
        self.add_report(ResourcesReport(self._scorecard))
        self.add_report(ResourceTemplatesReport(self._scorecard))
        self.add_report(PromptsReport(self._scorecard))
        self.add_report(EmojiLegendReport(self._scorecard))


# Re-export for backward compatibility
__all__ = [
    "BaseReport",
    "ShortReport",
    "FullReport",
    "format_score",
    "count_scores",
    "get_server_info",
]
