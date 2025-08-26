"""Custom report generation based on CLI selections."""

from ..constraints.base import ConstraintViolation
from ..models import ServerScoreCard
from .base import BaseReport, BaseReportOptions
from .functional_test import FunctionalTestReport
from .interviewer import (
    ConstraintViolationsReport,
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

# Available report classes
REPORT_CLASSES = [
    InterviewerInfoReport,
    ServerInfoReport,
    CapabilitiesReport,
    ToolStatisticsReport,
    ToolCallStatisticsReport,
    FunctionalTestReport,
    ConstraintViolationsReport,
    ToolsReport,
    ResourcesReport,
    ResourceTemplatesReport,
    PromptsReport,
]

# Build mappings from class methods - no instantiation needed!
REPORT_MAPPING = {cls.cli_name(): cls for cls in REPORT_CLASSES}
SHORTHAND_REPORT_MAPPING = {cls.cli_code(): cls.cli_name() for cls in REPORT_CLASSES}


class CustomReport(BaseReport):
    """Custom report based on user-selected components."""

    @classmethod
    def cli_name(cls) -> str:
        return "custom"

    @classmethod
    def cli_code(cls) -> str:
        return "CUSTOM"

    def __init__(
        self,
        scorecard: ServerScoreCard,
        report_names: list[str],
        violations: list[ConstraintViolation] | None = None,
        options: BaseReportOptions | None = None,
        selected_constraints: list[str] | None = None,
    ):
        """Initialize and build the custom report.

        Args:
            scorecard: The server scorecard to report on
            report_names: List of CLI-friendly report names or codes to include
            violations: List of constraint violations (optional)
            options: Report generation options
            selected_constraints: List of selected constraint names/codes (optional)
        """
        super().__init__(scorecard, violations or [], options)
        self.report_names = self._resolve_report_names(report_names)
        self._selected_constraints = selected_constraints
        self._build()

    def _resolve_report_names(self, names: list[str]) -> list[str]:
        """Resolve report names, converting shorthand codes to full names."""
        resolved = []
        for name in names:
            # Check if it's a shorthand code (uppercase)
            if name.upper() in SHORTHAND_REPORT_MAPPING:
                resolved.append(SHORTHAND_REPORT_MAPPING[name.upper()])
            # Check if it's already a full name
            elif name.lower() in REPORT_MAPPING:
                resolved.append(name.lower())
            # Skip unknown names
        return resolved

    def _build(self):
        """Build the custom report by composing selected submodules."""
        self.add_title("MCP Interviewer Report", 1)
        self.add_blank_line()

        for report_name in self.report_names:
            if report_name not in REPORT_MAPPING:
                # Skip unknown report names
                continue

            report_class = REPORT_MAPPING[report_name]

            # Special handling for reports that need violations
            if report_class == ConstraintViolationsReport:
                self.add_report(
                    report_class(
                        self._scorecard, self._violations, self._selected_constraints
                    )
                )
            # Special handling for FunctionalTestReport
            elif report_class == FunctionalTestReport:
                self.add_report(report_class(self._scorecard, include_evaluations=True))
            else:
                self.add_report(report_class(self._scorecard))


def get_available_reports() -> list[str]:
    """Get list of available report names for CLI help."""
    return sorted(REPORT_MAPPING.keys())


def get_shorthand_codes() -> dict[str, str]:
    """Get mapping of shorthand codes to report names."""
    return SHORTHAND_REPORT_MAPPING
