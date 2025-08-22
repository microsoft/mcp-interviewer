"""Functional test results report generation."""

from ..models import ServerScoreCard
from .base import BaseReport
from .test_step import TestStepReport
from .utils import count_scores, format_score


class FunctionalTestReport(BaseReport):
    """Report for functional test results."""

    def __init__(self, scorecard: ServerScoreCard):
        """Initialize and build the functional test report."""
        super().__init__(scorecard)
        if self._scorecard.functional_test_scorecard:
            self._build()

    def _build(self):
        """Build the functional test results section."""
        self.add_title("Functional Test Results (🤖)", 2)

        test = self._scorecard.functional_test_scorecard

        # Test plan
        if test.plan:
            self.add_text("**Test Plan (🤖):**")
            self.add_text(f"> {test.plan}")
            self.add_blank_line()

        # Overall results
        passes, total = count_scores(test)
        if total > 0:
            percentage = (passes / total) * 100
            self.add_text(
                f"**Overall Results:** {passes}/{total} checks passed ({percentage:.1f}%)"
            )
        else:
            self.add_text("**Overall Results:** No test results available")

        # Request counts
        self.add_blank_line()
        self.add_text("**MCP Request Counts (🧮):**")
        self.add_text(f"- Sampling requests: {test.sampling_requests}")
        self.add_text(f"- Prompt elicitation requests: {test.elicitation_requests}")
        self.add_text(f"- List roots requests: {test.list_roots_requests}")
        self.add_text(f"- Logging requests: {test.logging_requests}")
        self.add_blank_line()

        # Overall evaluation
        if test.meets_expectations:
            self.add_text("**Overall Evaluation (🤖):**")
            self.add_text(
                f"- {format_score(test.meets_expectations.score)} **Meets Expectations**: {test.meets_expectations.justification}"
            )
        if test.error_type:
            self.add_text(
                f"- **Error Type**: {test.error_type.score} - {test.error_type.justification}"
            )

        self.add_blank_line()

        # Individual test steps
        if test.steps:
            self.add_title("Test Steps", 3)

            for i, step in enumerate(test.steps):
                step_report = TestStepReport(
                    self._scorecard, step, i, show_only_failures=False
                )
                self.add_report(step_report)
