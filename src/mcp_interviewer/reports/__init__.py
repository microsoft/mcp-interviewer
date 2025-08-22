"""Report generation for MCP Server evaluation."""

from ..constraints.base import ConstraintViolation
from ..models import ServerScoreCard
from .base import BaseReport
from .capabilities import CapabilitiesReport
from .constraint_violations import ConstraintViolationsReport
from .emoji_legend import EmojiLegendReport
from .failed_tests import FailedTestsReport
from .functional_tests import FunctionalTestReport
from .model_info import ModelInfoReport
from .prompts import PromptsReport
from .resource_templates import ResourceTemplatesReport
from .resources import ResourcesReport
from .score_summary import ScoreSummaryReport
from .server_info import ServerInfoReport
from .tool_scorecards import ToolScorecardsReport
from .tools import ToolsReport
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
        self.add_title("📊 MCP Server Score Card", 1)
        self.add_blank_line()

        self.add_report(EmojiLegendReport(self._scorecard))
        self.add_report(ModelInfoReport(self._scorecard))
        self.add_report(ServerInfoReport(self._scorecard))
        self.add_report(CapabilitiesReport(self._scorecard))
        self.add_report(ScoreSummaryReport(self._scorecard, detailed=True))
        self.add_report(ConstraintViolationsReport(self._scorecard, self._violations))
        self.add_report(FailedTestsReport(self._scorecard, detailed=False))


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
        self.add_title("MCP Server Full Evaluation Report", 1)
        self.add_blank_line()

        # Metadata and basic info
        self.add_report(EmojiLegendReport(self._scorecard))
        self.add_report(ModelInfoReport(self._scorecard))
        self.add_report(ServerInfoReport(self._scorecard))
        self.add_report(CapabilitiesReport(self._scorecard))

        # Scores and violations
        self.add_report(ScoreSummaryReport(self._scorecard, detailed=True))
        self.add_report(ConstraintViolationsReport(self._scorecard, self._violations))
        self.add_report(FailedTestsReport(self._scorecard, detailed=True))

        # Available features (factual data)
        self.add_report(ToolsReport(self._scorecard))
        self.add_report(ResourcesReport(self._scorecard))
        self.add_report(ResourceTemplatesReport(self._scorecard))
        self.add_report(PromptsReport(self._scorecard))

        # Evaluations (AI-generated)
        self.add_report(ToolScorecardsReport(self._scorecard))
        self.add_report(FunctionalTestReport(self._scorecard))


# Re-export for backward compatibility
__all__ = [
    "BaseReport",
    "ShortReport",
    "FullReport",
    "format_score",
    "count_scores",
    "get_server_info",
]
