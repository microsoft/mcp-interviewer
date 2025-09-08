"""Tool output analysis report generation."""

from collections import defaultdict

from mcp.types import TextResourceContents
from tiktoken import encoding_for_model

from ...models import ServerScoreCard
from ..base import BaseReport


class ToolCallStatisticsReport(BaseReport):
    """Report for analyzing tool call outputs."""

    @classmethod
    def cli_name(cls) -> str:
        return "tool-call-stats"

    @classmethod
    def cli_code(cls) -> str:
        return "TCS"

    def __init__(self, scorecard: ServerScoreCard):
        """Initialize and build the tool output analysis report."""
        super().__init__(scorecard)
        if (
            self._scorecard.functional_test_scorecard
            and self._scorecard.functional_test_scorecard.steps
        ):
            self._build()

    def add_stats_table_row(
        self,
        label: str,
        values: list[float],
        show_total=True,
        show_avg=True,
        show_min=True,
        show_max=True,
    ) -> None:
        """Add a statistics table row with total, average, min, and max."""
        if not values:
            return

        total = sum(values)
        if total == 0:
            return

        avg = total / len(values)
        min_val = min(values)
        max_val = max(values)

        self.add_table_row(
            [
                label,
                f"{total:,}" if show_total else "",
                f"{avg:.1f}" if show_avg else "",
                f"{min_val:,}" if show_min else "",
                f"{max_val:,}" if show_max else "",
            ]
        )

    def _build(self):
        """Build the tool output analysis section."""
        functional_test_scorecard = self._scorecard.functional_test_scorecard
        if functional_test_scorecard is None:
            return

        tokenizer = encoding_for_model("gpt-4o")

        # Never collapse this section - always show the statistics
        self.add_title("Tool Call Statistics", 2)
        self.add_table_header(["Metric", "Total", "Average", "Min", "Max"])

        steps = functional_test_scorecard.steps

        # Analyze tool calls
        total_attempted = len(steps)
        calls_with_output = 0
        calls_with_error = 0
        calls_with_exception = 0

        # MCP request counts
        sampling_requests_per_step = []
        elicitation_requests_per_step = []
        list_roots_requests_per_step = []
        logging_requests_per_step = []

        text_tokens_per_output = []
        content_types_per_output = []

        for step in steps:
            if step.exception:
                calls_with_exception += 1

            # Collect MCP request counts per step
            sampling_requests_per_step.append(step.sampling_requests)
            elicitation_requests_per_step.append(step.elicitation_requests)
            list_roots_requests_per_step.append(step.list_roots_requests)
            logging_requests_per_step.append(step.logging_requests)

            if step.tool_output:
                calls_with_output += 1

                # Check if it's an error
                if step.tool_output.isError:
                    calls_with_error += 1

                content_types = defaultdict(int)
                text_content = ""
                # Analyze content types and collect text
                for content in step.tool_output.content:
                    content_types[content.type] += 1

                    # Collect text for token counting
                    if content.type == "text" and content.text:
                        text_content += content.text
                    elif (
                        content.type == "resource"
                        and isinstance(content.resource, TextResourceContents)
                        and content.resource.text
                    ):
                        text_content += content.resource.text

                if text_content:
                    text_token_count = len(tokenizer.encode(text_content))
                    text_tokens_per_output.append(text_token_count)

                if content_types:
                    content_types_per_output.append(content_types)

        self.add_table_row(["Tool calls attempted", str(total_attempted), "", "", ""])
        self.add_table_row(
            ["Tool calls returned output", str(calls_with_output), "", "", ""]
        )
        self.add_table_row(
            [
                "Tool call outputs with no error",
                str(calls_with_output - calls_with_error),
                "",
                "",
                "",
            ]
        )
        self.add_table_row(
            ["Tool call outputs with error", str(calls_with_error), "", "", ""]
        )
        self.add_table_row(
            ["Exceptions calling tools", str(calls_with_exception), "", "", ""]
        )

        # Output size analysis
        if text_tokens_per_output:
            self.add_stats_table_row(
                "Tool call output lengths (gpt-4o text tokens)", text_tokens_per_output
            )

        # Content type distribution
        if content_types_per_output:
            merged_content_types = defaultdict(int)
            for content_types in content_types_per_output:
                for key, value in content_types.items():
                    merged_content_types[key] += value

            # Sort by count descending
            for content_type, count in sorted(
                merged_content_types.items(), key=lambda x: x[1], reverse=True
            ):
                self.add_table_row(
                    [
                        f"{content_type.title()} output content blocks",
                        str(count),
                        f"{count / len(merged_content_types):.1f}",
                        f"{min(c[content_type] for c in content_types_per_output)}",
                        f"{max(c[content_type] for c in content_types_per_output)}",
                    ]
                )

        # MCP Request counts
        self.add_stats_table_row("Sampling requests", sampling_requests_per_step)
        self.add_stats_table_row("Elicitation requests", elicitation_requests_per_step)
        self.add_stats_table_row("List roots requests", list_roots_requests_per_step)
        self.add_stats_table_row("Logging requests", logging_requests_per_step)

        # No end_collapsible since we never start one
