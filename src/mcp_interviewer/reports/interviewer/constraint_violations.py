"""Constraint violations report generation."""

from ...constraints import get_selected_constraints
from ...constraints.base import Constraint, ConstraintViolation, Severity
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
        self.selected_constraints = get_selected_constraints(selected_constraints)
        self._build()

    def _build(self):
        """Build the constraint violations section."""
        # Add title
        self.add_title("Constraint Violations", 2)

        # Group by constraint for consistent ordering
        constraint_to_violations: dict[type[Constraint], list[ConstraintViolation]] = {
            constraint: [] for constraint in self.selected_constraints
        }

        errors = 0
        warnings = 0
        for violation in self.violations:
            if violation.severity == Severity.CRITICAL:
                errors += 1
            elif violation.severity == Severity.WARNING:
                warnings += 1
            constraint_to_violations[type(violation.constraint)].append(violation)

        passes = sum(1 for v in constraint_to_violations.values() if not v)

        self.add_table_header(["❌ Errors", "⚠️ Warnings", "✅ Passes"])
        self.add_table_row(list(map(str, (errors, warnings, passes))))
        self.add_blank_line()

        self.start_collapsible("Details")

        for constraint, violations in sorted(
            constraint_to_violations.items(), key=lambda item: item[0].cli_code()
        ):
            constraint_str = f"{constraint.cli_name()} ({constraint.cli_code()})"
            if violations:
                for violation in violations:
                    if violation.severity == Severity.CRITICAL:
                        self.add_text(f"❌ {constraint_str}: {violation.message}")
                    elif violation.severity == Severity.WARNING:
                        self.add_text(f"⚠️ {constraint_str}: {violation.message}")

                    self.add_blank_line()
            else:
                self.add_text(f"✅ {constraint_str}")
                self.add_blank_line()

        self.end_collapsible()
