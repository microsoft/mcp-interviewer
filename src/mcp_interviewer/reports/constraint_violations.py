"""Constraint violations report generation."""

from ..constraints.base import ConstraintViolation, Severity
from ..models import ServerScoreCard
from .base import BaseReport


class ConstraintViolationsReport(BaseReport):
    """Report for constraint violations."""

    def __init__(
        self,
        scorecard: ServerScoreCard,
        violations: list[ConstraintViolation] | None = None,
    ):
        """Initialize and build the constraint violations report."""
        super().__init__(scorecard)
        self.violations = violations or []
        self._build()

    def _build(self):
        """Build the constraint violations section."""
        self.add_title("Constraint Violations (🧮)", 2)

        if not self.violations:
            self.add_text("✅ **No constraint violations found**")
            self.add_blank_line()
            return

        # Group by severity
        errors = [v for v in self.violations if v.severity == Severity.CRITICAL]
        warnings = [v for v in self.violations if v.severity == Severity.WARNING]

        if errors:
            self.add_text(f"**Errors ({len(errors)}):**")
            self.add_blank_line()
            for violation in errors:
                self.add_text(f"- ❌ {violation.message}")
            self.add_blank_line()

        if warnings:
            self.add_text(f"**Warnings ({len(warnings)}):**")
            self.add_blank_line()
            for violation in warnings:
                self.add_text(f"- ⚠️ {violation.message}")
            self.add_blank_line()
