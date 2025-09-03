"""Test step report generation."""

import json
from collections import defaultdict

from mcp.types import TextResourceContents
from tiktoken import encoding_for_model

from ...models import FunctionalTestStepScoreCard, ServerScoreCard
from ..base import BaseReport
from ..utils import count_scores, format_score


class TestStepReport(BaseReport):
    """Report for a single test step."""

    @classmethod
    def cli_name(cls) -> str:
        return "test-step"

    @classmethod
    def cli_code(cls) -> str:
        return "TSTEP"

    def __init__(
        self,
        scorecard: ServerScoreCard,
        step: FunctionalTestStepScoreCard,
        step_index: int,
        show_only_failures: bool = False,
        include_evaluations: bool = True,
    ):
        """Initialize and build the test step report."""
        super().__init__(scorecard)
        self.step = step
        self.step_index = step_index
        self.show_only_failures = show_only_failures
        self.include_evaluations = include_evaluations

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

    def _add_statistics(self):
        """Compute statistics for this test step."""
        stats = {}

        if self.step.tool_output:
            # Token count
            tool_output_text = ""
            for content in self.step.tool_output.content:
                if content.type == "text" and content.text:
                    tool_output_text += content.text
                elif (
                    content.type == "resource"
                    and isinstance(content.resource, TextResourceContents)
                    and content.resource.text
                ):
                    tool_output_text += content.resource.text

            if tool_output_text:
                try:
                    tokenizer = encoding_for_model("gpt-4o")
                    token_count = len(tokenizer.encode(tool_output_text))
                    stats["token_count"] = token_count
                except:
                    pass

            # Content type distribution
            distribution = defaultdict(int)
            for content in self.step.tool_output.content:
                distribution[content.type] += 1
            stats["content_types"] = dict(distribution)

        if stats and "token_count" in stats or "content_types" in stats:
            self.add_text("**Output Statistics:**")
            self.add_blank_line()

            self.add_table_header(["Metric", "Value"])

            if "token_count" in stats:
                self.add_table_row(["Text token count", f"{stats['token_count']:,}"])

            if "content_types" in stats:
                for content_type, count in stats["content_types"].items():
                    # Format content type name
                    type_display = {
                        "text": "Text blocks",
                        "image": "Image blocks",
                        "audio": "Audio blocks",
                        "resource_link": "Resource link blocks",
                        "embedded_resource": "Embedded resource blocks",
                    }.get(content_type, f"{content_type.replace('_', ' ').title()}")

                    self.add_table_row([type_display, str(count)])
            self.add_blank_line()

    def _build(self):
        """Build the test step report."""
        # Create a collapsible section for each step
        step_title = f"Step {self.step_index + 1}: {self.step.tool_name}"
        if self.step.exception is not None:
            step_title += " ❌"
        elif self.step.tool_output is not None and self.step.tool_output.isError:
            step_title += " ⚠️"
        else:
            step_title += " ✅"

        # Add the title first
        self.add_title(step_title, 4)

        # Start collapsible section if enabled
        if self._options.use_collapsible:
            self.add_text("<details>")
            self.add_text("<summary>Toggle step details</summary>")
            self.add_blank_line()

        if self.include_evaluations:
            passes, total = count_scores(self.step)
            if total > 0:
                self.add_text(f"Score (🤖): {passes}/{total}")
                self.add_blank_line()

        # Link to tool details using tool name
        self.add_text(f"[→ View tool details](#tool-{self.step.tool_name})")
        self.add_blank_line()

        # Justification
        if self.step.justification:
            self.add_text(f"**Reasoning (🤖):** {self.step.justification}")
            self.add_blank_line()

        # Tool call
        self.add_text("**Tool Call (🤖):**")
        self.add_code_block(json.dumps(self.step.tool_arguments, indent=2), "json")

        # Expected output
        if self.step.expected_output:
            self.add_text(f"**Expected Output (🤖):** {self.step.expected_output}")
            self.add_blank_line()

        # Actual output
        if self.step.tool_output:
            self.add_text(
                f"**Actual Output ({len(self.step.tool_output.content)} blocks):**"
            )
            self.add_blank_line()
            self._add_tool_output(self.step.tool_output)

        # Exception if any
        if self.step.exception:
            self.add_text("**Exception:**")
            self.add_code_block(self.step.exception)
            self.add_blank_line()

        # Add statistics
        self._add_statistics()

        # Request counts for this step - display as a table
        if any(
            [
                self.step.sampling_requests,
                self.step.elicitation_requests,
                self.step.list_roots_requests,
                self.step.logging_requests,
            ]
        ):
            self.add_text("**MCP Requests:**")
            self.add_blank_line()

            self.add_table_header(["Request Type", "Count"])

            if self.step.sampling_requests:
                self.add_table_row(["Sampling", str(self.step.sampling_requests)])
            if self.step.elicitation_requests:
                self.add_table_row(["Elicitation", str(self.step.elicitation_requests)])
            if self.step.list_roots_requests:
                self.add_table_row(["List roots", str(self.step.list_roots_requests)])
            if self.step.logging_requests:
                self.add_table_row(["Logging", str(self.step.logging_requests)])

            self.add_blank_line()

        if self.include_evaluations:
            # Check if scoring was disabled
            scoring_disabled = False
            if (
                self.step.meets_expectations
                and self.step.meets_expectations.score == "N/A"
            ):
                if "No score generated" in self.step.meets_expectations.justification:
                    scoring_disabled = True

            if not scoring_disabled:
                # Evaluation results
                self.add_text("**Evaluation (🤖):**")

                # Show all evaluations or just failures based on context
                evaluation_fields = [
                    "meets_expectations",
                    "output_quality",
                    "output_relevance",
                    "schema_compliance",
                    "error_type",
                    "no_silent_error",
                    "error_handling",
                ]

                for field_name in evaluation_fields:
                    field_value = getattr(self.step, field_name, None)
                    if field_value and hasattr(field_value, "score"):
                        # Show all scores in full report, only failures in failed test section
                        if not self.show_only_failures or field_value.score == "fail":
                            self.add_text(
                                f"- {format_score(field_value.score)} **{field_name.replace('_', ' ').title()}**: {field_value.justification}"
                            )

        # End collapsible section if enabled
        if self._options.use_collapsible:
            self.add_text("</details>")

        self.add_blank_line()

    def _add_tool_output(self, tool_output) -> None:
        """Add formatted tool output with truncation."""
        if tool_output.isError:
            self.add_text("⚠️ **Error Response**")
        else:
            self.add_text("✅ **No Error**")

        self.add_blank_line()

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
                text = f"[Image: {content.mimeType}]"
                if hasattr(content, "data") and content.data:
                    text += f"\n\tSize: {len(content.data)} bytes (base64)"
                self.add_code_block(text)
            elif content.type == "audio":
                text = f"[Audio: {content.mimeType}]"
                if hasattr(content, "data") and content.data:
                    text += f"\n\tSize: {len(content.data)} bytes (base64)"
                self.add_code_block(text)
            elif content.type == "resource_link":
                text = f"[Resource Link: {content.uri}]"
                if content.mimeType:
                    text += f"\n\tMIME type: {content.mimeType}"
                if content.description:
                    text += f"\n\tDescription: {content.description}"
                self.add_code_block(text)
            elif content.type == "resource":
                # EmbeddedResource type
                resource = content.resource
                text = f"[Embedded Resource: {resource.uri}]"
                if resource.mimeType:
                    text += f"\n\tMIME type: {resource.mimeType}"

                # Handle text vs blob resource contents
                if hasattr(resource, "text"):
                    # TextResourceContents
                    text += "\n\n" + resource.text

                elif hasattr(resource, "blob"):
                    # BlobResourceContents
                    text += f"\n\tBlob size: {len(resource.blob)} bytes (base64)"

                if len(text) > 500:
                    truncated_chars = len(text) - 500
                    text = text[:500] + f"\n... ({truncated_chars} chars truncated)"

                self.add_code_block(text)
