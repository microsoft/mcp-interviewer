"""Score summary report generation."""

from ...models import ServerScoreCard
from ..base import BaseReport
from ..utils import count_scores


class ScoreSummaryReport(BaseReport):
    """Report for score summaries."""

    @classmethod
    def cli_name(cls) -> str:
        return "score-summary"

    @classmethod
    def cli_code(cls) -> str:
        return "SCORE"

    def __init__(self, scorecard: ServerScoreCard, detailed: bool = False):
        """Initialize and build the score summary report."""
        super().__init__(scorecard)
        self.detailed = detailed
        self._build()

    def _build(self):
        """Build the score summary section."""
        # Check if scoring was disabled
        scoring_disabled = False
        if self._scorecard.tool_scorecards:
            first_scorecard = self._scorecard.tool_scorecards[0]
            # Check if all scores are N/A (indicating scoring was disabled)
            sample_score = first_scorecard.tool_name.length.score
            if (
                sample_score == "N/A"
                and "No score generated"
                in first_scorecard.tool_name.length.justification
            ):
                scoring_disabled = True

        if scoring_disabled:
            self.add_title("Score Summary", 2)
            self.add_text("**Overall Score:** _Scoring disabled_")
            self.add_blank_line()
            return

        self.add_title("Score Summary (🤖)", 2)

        # Calculate overall score first
        total_passes, total_tests = count_scores(self._scorecard)
        if total_tests > 0:
            percentage = (total_passes / total_tests) * 100
            self.add_text(
                f"**Overall Score:** {total_passes}/{total_tests} tests passed ({percentage:.1f}%)"
            )
        else:
            self.add_text("**Overall Score:** No tests available")

        self.add_blank_line()

        # Summary table
        self.add_table_header(["Category", "Score", "Details"])

        # Tools scores
        if self._scorecard.tool_scorecards:
            for i, tool_scorecard in enumerate(self._scorecard.tool_scorecards):
                tool = self._scorecard.tools[i]
                passes, total = count_scores(tool_scorecard)
                if total > 0:
                    score_text = f"{passes}/{total}"
                    self.add_table_row(
                        [
                            f"Tool: {tool.name}",
                            score_text,
                            "Tool definition quality",
                        ]
                    )

                    if self.detailed:
                        # Add subcategory breakdowns
                        for category in [
                            "tool_name",
                            "tool_description",
                            "tool_input_schema",
                            "tool_output_schema",
                        ]:
                            category_obj = getattr(tool_scorecard, category)
                            cat_passes, cat_total = count_scores(category_obj)
                            if cat_total > 0:
                                self.add_table_row(
                                    [
                                        f"  └─ {category.replace('_', ' ').title()}",
                                        f"{cat_passes}/{cat_total}",
                                        "",
                                    ]
                                )

        # Functional test scores
        if self._scorecard.functional_test_scorecard:
            passes, total = count_scores(self._scorecard.functional_test_scorecard)
            if total > 0:
                score_text = f"{passes}/{total}"
                self.add_table_row(
                    [
                        "Functional Tests",
                        score_text,
                        "End-to-end testing",
                    ]
                )

                if self.detailed and self._scorecard.functional_test_scorecard.steps:
                    # Show individual test steps
                    for i, step in enumerate(
                        self._scorecard.functional_test_scorecard.steps
                    ):
                        step_passes, step_total = count_scores(step)
                        if step_total > 0:
                            tool_name = step.tool_name if step.tool_name else "Unknown"
                            self.add_table_row(
                                [
                                    f"  └─ Step {i + 1}: {tool_name}",
                                    f"{step_passes}/{step_total}",
                                    "",
                                ]
                            )

        self.add_blank_line()
