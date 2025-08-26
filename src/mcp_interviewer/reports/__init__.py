"""Report generation for MCP Server evaluation."""

from .base import BaseReport
from .full import FullReport
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
from .utils import count_scores, format_score, get_server_info

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


def get_available_reports() -> list[str]:
    """Get list of available report names for CLI help."""
    return sorted(REPORT_MAPPING.keys())


def get_shorthand_codes() -> dict[str, str]:
    """Get mapping of shorthand codes to report names."""
    return SHORTHAND_REPORT_MAPPING


__all__ = [
    "BaseReport",
    "FullReport",
    "format_score",
    "count_scores",
    "get_server_info",
    "REPORT_CLASSES",
    "REPORT_MAPPING",
    "SHORTHAND_REPORT_MAPPING",
    "get_available_reports",
    "get_shorthand_codes",
]
