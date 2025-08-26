"""Base report class with utility methods."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..constraints.base import ConstraintViolation
from ..models import ServerScoreCard


@dataclass
class BaseReportOptions:
    """Options for configuring report generation."""

    use_collapsible: bool = True


class BaseReport(ABC):
    """Base class for all report builders."""

    @classmethod
    @abstractmethod
    def cli_name(cls) -> str:
        """A CLI friendly (e.g. kebab case) name for this report."""
        ...

    @classmethod
    @abstractmethod
    def cli_code(cls) -> str:
        """A single, all-caps all-letter code for this report."""
        ...

    def __init__(
        self,
        scorecard: ServerScoreCard,
        violations: list[ConstraintViolation] = [],
        options: BaseReportOptions | None = None,
    ):
        """Initialize a new Report builder."""
        self._lines: list[str] = []
        self._scorecard = scorecard
        self._violations = violations
        self._options = options or BaseReportOptions()

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
        # Propagate the options to the sub-report
        report._options = self._options
        self._lines.extend(report._lines)
        return self

    def start_collapsible(self, title: str, level: int = 2) -> "BaseReport":
        """Start a collapsible section with a title."""
        # Always add the markdown header
        prefix = "#" * level
        self._lines.append(f"{prefix} {title}")
        self._lines.append("")

        # Only add details tags if use_collapsible is True
        if self._options.use_collapsible:
            self._lines.append("<details>")
            self._lines.append("<summary>Toggle details</summary>")
            self._lines.append("")
        return self

    def end_collapsible(self) -> "BaseReport":
        """End a collapsible section."""
        if self._options.use_collapsible:
            self._lines.append("</details>")
            self._lines.append("")
        return self

    def build(self) -> str:
        """Build the final markdown string."""
        return "\n".join(self._lines)
