"""Tool summary report generation."""

from ...models import ServerScoreCard
from ...statistics.tool import (
    ToolInputSchemaMaxDepthCount,
    ToolInputSchemaOptionalParametersCount,
    ToolInputSchemaRequiredParametersCount,
    ToolInputSchemaTokenCount,
    ToolInputSchemaTotalParametersCount,
)
from ..base import BaseReport
from ..utils import count_scores


class ToolStatisticsReport(BaseReport):
    """Report showing aggregate tool statistics."""

    @classmethod
    def cli_name(cls) -> str:
        return "tool-stats"

    @classmethod
    def cli_code(cls) -> str:
        return "TS"

    def __init__(self, scorecard: ServerScoreCard):
        """Initialize and build the tool summary report."""
        super().__init__(scorecard)
        self._build()

    def _build(self):
        """Build the tool summary section."""
        # Never collapse this section - always show the statistics
        self.add_title("Tool Statistics", 2)

        self.add_table_header(["Metric", "Total", "Average", "Min", "Max"])
        if self._scorecard.tools:
            # Compute statistics
            token_stat = ToolInputSchemaTokenCount()
            total_params_stat = ToolInputSchemaTotalParametersCount()
            required_params_stat = ToolInputSchemaRequiredParametersCount()
            optional_params_stat = ToolInputSchemaOptionalParametersCount()
            max_depth_stat = ToolInputSchemaMaxDepthCount()

            token_counts = list(token_stat.compute(self._scorecard))
            total_params = list(total_params_stat.compute(self._scorecard))
            required_params = list(required_params_stat.compute(self._scorecard))
            optional_params = list(optional_params_stat.compute(self._scorecard))
            max_depths = list(max_depth_stat.compute(self._scorecard))

            # Token counts
            if token_counts:
                values = [v.value for v in token_counts]
                self.add_table_row(
                    [
                        "Input schema lengths (gpt-4o tokens)",
                        f"{sum(values):,}",
                        f"{sum(values) / len(values):.1f}",
                        f"{min(values):,}",
                        f"{max(values):,}",
                    ]
                )

            # Total parameters
            if total_params:
                values = [v.value for v in total_params]
                self.add_table_row(
                    [
                        "Input schemas parameter count",
                        "",
                        f"{sum(values) / len(values):.1f}",
                        str(min(values)),
                        str(max(values)),
                    ]
                )

            # Required parameters
            if required_params:
                values = [v.value for v in required_params]
                self.add_table_row(
                    [
                        "Input schemas required parameter count",
                        "",
                        f"{sum(values) / len(values):.1f}",
                        str(min(values)),
                        str(max(values)),
                    ]
                )

            # Optional parameters
            if optional_params:
                values = [v.value for v in optional_params]
                self.add_table_row(
                    [
                        "Input schemas optional parameter count",
                        "",
                        f"{sum(values) / len(values):.1f}",
                        str(min(values)),
                        str(max(values)),
                    ]
                )

            # Max depth
            if max_depths:
                values = [v.value for v in max_depths]
                self.add_table_row(
                    [
                        "Input schema max depth",
                        "",
                        f"{sum(values) / len(values):.1f}",
                        str(min(values)),
                        str(max(values)),
                    ]
                )

        # Tool scorecard statistics
        if self._scorecard.tool_scorecards and len(self._scorecard.tool_scorecards) > 0:
            # Count passing scores for tool names and descriptions
            tools_with_passing_names = 0
            tools_with_name_scores = 0
            tools_with_passing_descriptions = 0
            tools_with_description_scores = 0

            for tool_scorecard in self._scorecard.tool_scorecards:
                # Check tool name scores
                name_passes, name_total = count_scores(tool_scorecard.tool_name)

                if name_total > 0:
                    tools_with_name_scores += 1
                    if name_passes == name_total:
                        tools_with_passing_names += 1

                desc_passes, desc_total = count_scores(tool_scorecard.tool_description)

                if desc_total > 0:
                    tools_with_description_scores += 1
                    if desc_passes == desc_total:
                        tools_with_passing_descriptions += 1

            if tools_with_passing_names + tools_with_passing_descriptions > 0:
                self.add_table_row(
                    [
                        "Tool names passing eval (🤖)",
                        f"{tools_with_passing_names}/{tools_with_name_scores}",
                        "",
                        "",
                        "",
                    ]
                )

                self.add_table_row(
                    [
                        "Tool descriptions passing eval (🤖)",
                        f"{tools_with_passing_descriptions}/{tools_with_passing_descriptions}",
                        "",
                        "",
                        "",
                    ]
                )

                self.add_blank_line()

        # No end_collapsible since we never start one
