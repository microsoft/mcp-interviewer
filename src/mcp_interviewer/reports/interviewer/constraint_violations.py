"""Constraint violations report generation."""

from ...constraints.base import ConstraintViolation, Severity
from ...models import ServerScoreCard
from ..base import BaseReport


class ConstraintViolationsReport(BaseReport):
    """Report for constraint violations."""

    @classmethod
    def cli_name(cls) -> str:
        return "constraint-violations"

    @classmethod
    def cli_code(cls) -> str:
        return "CV"

    def __init__(
        self,
        scorecard: ServerScoreCard,
        violations: list[ConstraintViolation] | None = None,
        selected_constraints: list[str] | None = None,
    ):
        """Initialize and build the constraint violations report."""
        super().__init__(scorecard)
        self.violations = violations or []
        self.selected_constraints = selected_constraints
        self._build()

    def _build(self):
        """Build the constraint violations section."""
        # Add title
        self.add_title("Constraint Violations", 2)

        # Always show summary message first
        if not self.violations:
            self.add_text("✅ **No constraint violations found**")
            self.add_blank_line()
        else:
            # Group by severity
            errors = [v for v in self.violations if v.severity == Severity.CRITICAL]
            warnings = [v for v in self.violations if v.severity == Severity.WARNING]

            # Show summary counts
            summary_parts = []
            if errors:
                summary_parts.append(
                    f"❌ {len(errors)} error{'s' if len(errors) > 1 else ''}"
                )
            if warnings:
                summary_parts.append(
                    f"⚠️ {len(warnings)} warning{'s' if len(warnings) > 1 else ''}"
                )

            self.add_text(f"**Found:** {', '.join(summary_parts)}")
            self.add_blank_line()

        # Put checked constraints in collapsible section
        if self._options.use_collapsible:
            self.add_text("<details>")
            self.add_text("<summary>Checked constraints</summary>")
            self.add_blank_line()

        if self.selected_constraints:
            self.add_text(
                f"**Constraints checked:** {', '.join(self.selected_constraints)}"
            )
        else:
            self.add_text("**Constraints checked:** All available constraints")
        self.add_blank_line()

        if self._options.use_collapsible:
            self.add_text("</details>")
            self.add_blank_line()

        # Return early if no violations
        if not self.violations:
            return

        # Put violation details in collapsible section
        errors = [v for v in self.violations if v.severity == Severity.CRITICAL]
        warnings = [v for v in self.violations if v.severity == Severity.WARNING]
        if self._options.use_collapsible:
            self.add_text("<details>")
            self.add_text("<summary>Violation details</summary>")
            self.add_blank_line()

        if errors:
            self.add_text(f"**Errors ({len(errors)}):**")
            self.add_blank_line()
            for violation in errors:
                cli_code = (
                    violation.constraint.cli_code()
                    if hasattr(violation.constraint, "cli_code")
                    else ""
                )
                if cli_code:
                    self.add_text(f"- ❌ [{cli_code}] {violation.message}")
                else:
                    self.add_text(f"- ❌ {violation.message}")
            self.add_blank_line()

        if warnings:
            self.add_text(f"**Warnings ({len(warnings)}):**")
            self.add_blank_line()
            for violation in warnings:
                cli_code = (
                    violation.constraint.cli_code()
                    if hasattr(violation.constraint, "cli_code")
                    else ""
                )
                if cli_code:
                    self.add_text(f"- ⚠️ [{cli_code}] {violation.message}")
                else:
                    self.add_text(f"- ⚠️ {violation.message}")
            self.add_blank_line()

        if self._options.use_collapsible:
            self.add_text("</details>")
            self.add_blank_line()
