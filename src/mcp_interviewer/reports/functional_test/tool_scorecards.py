"""Tool scorecards report generation."""

from ...models import ServerScoreCard
from ..base import BaseReport
from ..utils import count_scores, format_score


class ToolScorecardsReport(BaseReport):
    """Report for tool evaluation scorecards."""

    @classmethod
    def cli_name(cls) -> str:
        return "tool-scorecards"

    @classmethod
    def cli_code(cls) -> str:
        return "TSC"

    def __init__(self, scorecard: ServerScoreCard):
        """Initialize and build the tool scorecards report."""
        super().__init__(scorecard)
        self._build()

    def _build(self):
        """Build the tool scorecards section."""
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
            self.start_collapsible("Tool Scorecards", 2)
            self.add_text(
                "_Experimental tool judging disabled - no evaluations generated_"
            )
            self.add_blank_line()
            self.end_collapsible()
            return
        else:
            self.start_collapsible("Tool Scorecards (🤖)", 2)

        if not self._scorecard.tool_scorecards:
            self.add_text("_No tool evaluations available_")
            self.add_blank_line()
            self.end_collapsible()
            return

        for i in range(len(self._scorecard.tool_scorecards)):
            self.add_tool_scorecard(i)

        self.end_collapsible()

    def add_tool_scorecard(self, tool_index: int) -> "ToolScorecardsReport":
        """Add a detailed scorecard for a specific tool."""
        tool = self._scorecard.tools[tool_index]
        scorecard = self._scorecard.tool_scorecards[tool_index]

        # Calculate score for display in content
        passes, total = count_scores(scorecard)
        percentage = (passes / total * 100) if total > 0 else 0

        # Add title for the tool scorecard
        self.add_title(f"{tool.name}", 3)

        # Show score
        self.add_text(f"**Score:** {passes}/{total} ({percentage:.0f}%)")
        self.add_blank_line()

        # Link to tool details
        self.add_text(f"[→ View tool details](#tool-{tool.name})")
        self.add_blank_line()

        # Start collapsible section for scorecard details
        if self._options.use_collapsible:
            self.add_text("<details>")
            self.add_text("<summary>Toggle scorecard details</summary>")
            self.add_blank_line()

        # Tool Name Evaluation
        if self._options.use_collapsible:
            self.add_text("<details>")
            self.add_text("<summary>Tool Name (🤖)</summary>")
            self.add_blank_line()
        else:
            self.add_text("**Tool Name (🤖):**")
            self.add_blank_line()
        self.add_table_header(["Aspect", "Score", "Justification"])
        self.add_table_row(
            [
                "Length",
                format_score(scorecard.tool_name.length.score),
                scorecard.tool_name.length.justification,
            ]
        )
        self.add_table_row(
            [
                "Uniqueness",
                format_score(scorecard.tool_name.uniqueness.score),
                scorecard.tool_name.uniqueness.justification,
            ]
        )
        self.add_table_row(
            [
                "Descriptiveness",
                format_score(scorecard.tool_name.descriptiveness.score),
                scorecard.tool_name.descriptiveness.justification,
            ]
        )
        self.add_blank_line()

        # End collapsible for Tool Name
        if self._options.use_collapsible:
            self.add_text("</details>")
            self.add_blank_line()

        # Tool Description Evaluation
        if self._options.use_collapsible:
            self.add_text("<details>")
            self.add_text("<summary>Tool Description (🤖)</summary>")
            self.add_blank_line()
        else:
            self.add_text("**Tool Description (🤖):**")
            self.add_blank_line()
        self.add_table_header(["Aspect", "Score", "Justification"])
        self.add_table_row(
            [
                "Length",
                format_score(scorecard.tool_description.length.score),
                scorecard.tool_description.length.justification,
            ]
        )
        self.add_table_row(
            [
                "Parameters",
                format_score(scorecard.tool_description.parameters.score),
                scorecard.tool_description.parameters.justification,
            ]
        )
        self.add_table_row(
            [
                "Examples",
                format_score(scorecard.tool_description.examples.score),
                scorecard.tool_description.examples.justification,
            ]
        )
        self.add_blank_line()

        # End collapsible for Tool Description
        if self._options.use_collapsible:
            self.add_text("</details>")
            self.add_blank_line()

        # Input Schema Evaluation
        if self._options.use_collapsible:
            self.add_text("<details>")
            self.add_text("<summary>Input Schema (🤖)</summary>")
            self.add_blank_line()
        else:
            self.add_text("**Input Schema (🤖):**")
            self.add_blank_line()
        self.add_table_header(["Aspect", "Score", "Justification"])
        self.add_table_row(
            [
                "Complexity",
                format_score(scorecard.tool_input_schema.complexity.score),
                scorecard.tool_input_schema.complexity.justification,
            ]
        )
        self.add_table_row(
            [
                "Parameters",
                format_score(scorecard.tool_input_schema.parameters.score),
                scorecard.tool_input_schema.parameters.justification,
            ]
        )
        self.add_table_row(
            [
                "Optionals",
                format_score(scorecard.tool_input_schema.optionals.score),
                scorecard.tool_input_schema.optionals.justification,
            ]
        )
        self.add_table_row(
            [
                "Constraints",
                format_score(scorecard.tool_input_schema.constraints.score),
                scorecard.tool_input_schema.constraints.justification,
            ]
        )
        self.add_blank_line()

        # End collapsible for Input Schema
        if self._options.use_collapsible:
            self.add_text("</details>")
            self.add_blank_line()

        # Output Schema Evaluation (if exists)
        if scorecard.tool_output_schema:
            if self._options.use_collapsible:
                self.add_text("<details>")
                self.add_text("<summary>Output Schema (🤖)</summary>")
                self.add_blank_line()
            else:
                self.add_text("**Output Schema (🤖):**")
                self.add_blank_line()
            self.add_table_header(["Aspect", "Score", "Justification"])
            self.add_table_row(
                [
                    "Complexity",
                    format_score(scorecard.tool_output_schema.complexity.score),
                    scorecard.tool_output_schema.complexity.justification,
                ]
            )
            self.add_table_row(
                [
                    "Parameters",
                    format_score(scorecard.tool_output_schema.parameters.score),
                    scorecard.tool_output_schema.parameters.justification,
                ]
            )
            self.add_table_row(
                [
                    "Optionals",
                    format_score(scorecard.tool_output_schema.optionals.score),
                    scorecard.tool_output_schema.optionals.justification,
                ]
            )
            self.add_table_row(
                [
                    "Constraints",
                    format_score(scorecard.tool_output_schema.constraints.score),
                    scorecard.tool_output_schema.constraints.justification,
                ]
            )
            self.add_blank_line()

            # End collapsible for Output Schema
            if self._options.use_collapsible:
                self.add_text("</details>")
                self.add_blank_line()

        # End collapsible section for entire scorecard
        if self._options.use_collapsible:
            self.add_text("</details>")
            self.add_blank_line()

        return self
