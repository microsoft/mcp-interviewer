"""Functional test results report generation."""

from ...models import ServerScoreCard
from ..base import BaseReport
from ..utils import format_score
from .test_step import TestStepReport


class FunctionalTestReport(BaseReport):
    """Report for functional test results."""

    @classmethod
    def cli_name(cls) -> str:
        return "functional-tests"

    @classmethod
    def cli_code(cls) -> str:
        return "FT"

    def __init__(self, scorecard: ServerScoreCard, include_evaluations: bool = True):
        """Initialize and build the functional test report.

        Args:
            scorecard: The server scorecard to report on
            include_evaluations: If False, hide AI-generated fields except tool call arguments
        """
        super().__init__(scorecard)
        self.include_evaluations = include_evaluations
        if self._scorecard.functional_test_scorecard:
            self._build()

    def _build(self):
        """Build the functional test results section."""
        # functional_test_scorecard is guaranteed to be non-None when _build() is called
        assert self._scorecard.functional_test_scorecard is not None

        # Check if scoring was disabled
        self.start_collapsible("Functional Test Results", 2)

        test = self._scorecard.functional_test_scorecard

        # Test plan
        if self.include_evaluations and test.plan:
            self.add_text("**Test Plan (🤖):**")
            self.add_code_block(test.plan)
            self.add_blank_line()

        # Overall evaluation
        if self.include_evaluations:
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
        self.add_title("Test Steps", 3)

        if test.steps:
            for i, step in enumerate(test.steps):
                step_report = TestStepReport(
                    self._scorecard,
                    step,
                    i,
                    show_only_failures=False,
                    include_evaluations=self.include_evaluations,
                )
                self.add_report(step_report)
        else:
            self.add_text("_No test steps available_")
            self.add_blank_line()

        self.end_collapsible()
