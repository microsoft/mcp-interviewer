"""Base report class with utility methods."""

from abc import ABC

from ..constraints.base import ConstraintViolation
from ..models import ServerScoreCard


class BaseReport(ABC):
    """Base class for all report builders."""

    def __init__(
        self, scorecard: ServerScoreCard, violations: list[ConstraintViolation] = []
    ):
        """Initialize a new Report builder."""
        self._lines: list[str] = []
        self._scorecard = scorecard
        self._violations = violations

    def add_title(self, title: str, level: int = 1) -> "BaseReport":
        """Add a title to the report."""
        prefix = "#" * level
        self.add_text(f"{prefix} {title}")
        self.add_blank_line()
        return self

    def add_text(self, text: str) -> "BaseReport":
        """Add a line of text to the report."""
        self._lines.append(text)
        return self

    def add_blank_line(self) -> "BaseReport":
        """Add a blank line to the report."""
        self._lines.append("")
        return self

    def add_code_block(self, code: str, language: str = "") -> "BaseReport":
        """Add a code block to the report."""
        self._lines.append(f"```{language}")
        self._lines.append(code)
        self._lines.append("```")
        return self

    def add_table_header(self, columns: list[str]) -> "BaseReport":
        """Add a table header to the report."""
        self._lines.append("| " + " | ".join(columns) + " |")
        self._lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
        return self

    def add_table_row(self, values: list[str]) -> "BaseReport":
        """Add a table row to the report."""
        self._lines.append("| " + " | ".join(values) + " |")
        return self

    def add_report(self, report: "BaseReport") -> "BaseReport":
        """Merge another report into this one."""
        self._lines.extend(report._lines)
        return self

    def build(self) -> str:
        """Build the final markdown string."""
        return "\n".join(self._lines)
