"""Failed tests report generation."""

from ..models import ServerScoreCard
from .base import BaseReport
from .test_step import TestStepReport


class FailedTestsReport(BaseReport):
    """Report for failed test steps."""

    def __init__(self, scorecard: ServerScoreCard, detailed: bool = False):
        """Initialize and build the failed tests report."""
        super().__init__(scorecard)
        self.detailed = detailed
        if self._has_failed_tests():
            self._build()

    def _has_failed_tests(self) -> bool:
        """Check if there are any failed tests."""
        if not self._scorecard.functional_test_scorecard:
            return False

        for step in self._scorecard.functional_test_scorecard.steps:
            # Check if any evaluation criteria failed
            for field_name in step.model_fields_set:
                field_value = getattr(step, field_name)
                if hasattr(field_value, "score") and field_value.score == "fail":
                    return True
        return False

    def _build(self):
        """Build the failed tests section."""
        if self.detailed:
            self._add_detailed_failed_test_steps()
        else:
            self._add_failed_test_steps()

    def _add_failed_test_steps(self) -> "FailedTestsReport":
        """Add a summary of failed test steps."""
        self.add_title("Failed Test Steps (🤖)", 2)

        for i, step in enumerate(self._scorecard.functional_test_scorecard.steps):
            has_failure = False
            failures = []

            # Check each evaluation criteria
            for field_name in step.model_fields_set:
                field_value = getattr(step, field_name)
                if hasattr(field_value, "score") and field_value.score == "fail":
                    has_failure = True
                    failures.append(field_name.replace("_", " ").title())

            if has_failure:
                self.add_text(
                    f"**Step {i + 1}: {step.tool_name}** - Failed: {', '.join(failures)}"
                )

        self.add_blank_line()
        return self

    def _add_detailed_failed_test_steps(self) -> "FailedTestsReport":
        """Add detailed information about failed test steps."""
        self.add_title("Failed Test Steps (🤖)", 2)

        for i, step in enumerate(self._scorecard.functional_test_scorecard.steps):
            # Use TestStepReport with show_only_failures=True
            # This will only build the report if the step has failures
            step_report = TestStepReport(
                self._scorecard, step, i, show_only_failures=True
            )

            # Only add if the step has failures (the report will have content)
            if step_report.has_failures:
                self.add_report(step_report)

        return self
