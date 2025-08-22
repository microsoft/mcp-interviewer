"""Test step report generation."""

import json

from ..models import FunctionalTestStepScoreCard, ServerScoreCard
from .base import BaseReport
from .utils import count_scores, format_score


class TestStepReport(BaseReport):
    """Report for a single test step."""

    def __init__(
        self,
        scorecard: ServerScoreCard,
        step: FunctionalTestStepScoreCard,
        step_index: int,
        show_only_failures: bool = False,
    ):
        """Initialize and build the test step report."""
        super().__init__(scorecard)
        self.step = step
        self.step_index = step_index
        self.show_only_failures = show_only_failures

        # Check if this step has failures
        self.has_failures = self._check_for_failures()

        # Only build if not filtering or if has failures
        if not show_only_failures or self.has_failures:
            self._build()

    def _check_for_failures(self) -> bool:
        """Check if this step has any failures."""
        for field_name in self.step.model_fields_set:
            field_value = getattr(self.step, field_name)
            if hasattr(field_value, "score") and field_value.score == "fail":
                return True
        return False

    def _build(self):
        """Build the test step report."""
        passes, total = count_scores(self.step)
        percentage = (passes / total * 100) if total > 0 else 0

        self.add_title(
            f"Step {self.step_index + 1}: {self.step.tool_name} ({passes}/{total} - {percentage:.0f}%)",
            4,
        )

        # Find the tool index for linking
        tool_index = None
        for i, tool in enumerate(self._scorecard.tools):
            if tool.name == self.step.tool_name:
                tool_index = i
                break

        # Link to tool details and scorecard if found
        if tool_index is not None:
            self.add_text(
                f"[→ View tool details](#tool-{tool_index}) | [→ View scorecard](#tool-scorecard-{tool_index})"
            )
            self.add_blank_line()

        # Justification
        if self.step.justification:
            self.add_text(f"**Purpose (🤖):** {self.step.justification}")
            self.add_blank_line()

        # Tool call
        self.add_text("**Tool Call (🤖):**")
        self.add_code_block(json.dumps(self.step.tool_arguments, indent=2), "json")

        # Expected output
        if self.step.expected_output:
            self.add_text(f"**Expected (🤖):** {self.step.expected_output}")
            self.add_blank_line()

        # Actual output
        if self.step.tool_output:
            self.add_text("**Actual Output (🧮):**")
            if self.step.tool_output.isError:
                self.add_text("⚠️ **Error Response**")

            self._add_tool_output(self.step.tool_output)

        # Exception if any
        if self.step.exception:
            self.add_text("**Exception:**")
            self.add_code_block(self.step.exception)

        # Request counts for this step
        if any(
            [
                self.step.sampling_requests,
                self.step.elicitation_requests,
                self.step.list_roots_requests,
                self.step.logging_requests,
            ]
        ):
            self.add_text("**MCP Requests (🧮):**")
            if self.step.sampling_requests:
                self.add_text(f"- Sampling: {self.step.sampling_requests}")
            if self.step.elicitation_requests:
                self.add_text(f"- Elicitation: {self.step.elicitation_requests}")
            if self.step.list_roots_requests:
                self.add_text(f"- List roots: {self.step.list_roots_requests}")
            if self.step.logging_requests:
                self.add_text(f"- Logging: {self.step.logging_requests}")
            self.add_blank_line()

        # Evaluation results
        self.add_text("**Evaluation (🤖):**")

        # Show all evaluations or just failures based on context
        evaluation_fields = [
            "error_handling",
            "error_type",
            "no_silent_error",
            "output_relevance",
            "output_quality",
            "schema_compliance",
            "meets_expectations",
        ]

        for field_name in evaluation_fields:
            field_value = getattr(self.step, field_name, None)
            if field_value and hasattr(field_value, "score"):
                # Show all scores in full report, only failures in failed test section
                if not self.show_only_failures or field_value.score == "fail":
                    self.add_text(
                        f"- {format_score(field_value.score)} **{field_name.replace('_', ' ').title()}**: {field_value.justification}"
                    )

        self.add_blank_line()

    def _add_tool_output(self, tool_output) -> None:
        """Add formatted tool output with truncation."""
        for content in tool_output.content:
            if content.type == "text":
                if content.text:
                    output_str = content.text
                    language = ""

                    # Try to parse as JSON for better formatting
                    try:
                        parsed = json.loads(content.text)
                        output_str = json.dumps(parsed, indent=2)
                        language = "json"
                    except:
                        pass

                    # Truncate if too long
                    if len(output_str) > 500:
                        truncated_chars = len(output_str) - 500
                        output_str = (
                            output_str[:500]
                            + f"\n... ({truncated_chars} chars truncated)"
                        )

                    self.add_code_block(output_str, language)
            elif content.type == "image":
                self.add_text(f"[Image: {content.mimeType or 'unknown type'}]")
            elif content.type == "resource":
                self.add_text(f"[Resource: {content.resource.uri}]")
