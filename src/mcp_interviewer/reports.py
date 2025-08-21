"""Markdown report generation for MCP Server evaluation results."""

import json
from typing import Any

from pydantic import BaseModel

from .constraints.base import ConstraintViolation, Severity
from .models import PassFailScoreCard, ServerScoreCard


def format_score(score: str) -> str:
    """Format a score with appropriate emoji."""
    if score == "pass":
        return "✅ Pass"
    elif score == "fail":
        return "❌ Fail"
    elif score == "N/A":
        return "⚪ N/A"
    else:
        return score


def count_scores(obj: Any, path: str = "") -> tuple[int, int]:
    """Recursively count pass/fail scores. Returns (passes, total)."""
    passes = 0
    total = 0

    if isinstance(obj, PassFailScoreCard):
        if obj.score != "N/A":
            total += 1
            if obj.score == "pass":
                passes += 1
    elif isinstance(obj, BaseModel):
        for field_name in obj.model_fields_set:
            field_value = getattr(obj, field_name)
            p, t = count_scores(field_value, f"{path}.{field_name}")
            passes += p
            total += t
    elif isinstance(obj, dict):
        for key, value in obj.items():
            p, t = count_scores(value, f"{path}.{key}")
            passes += p
            total += t
    elif isinstance(obj, list):
        for item in obj:
            p, t = count_scores(item, path)
            passes += p
            total += t

    return passes, total


def get_server_info(scorecard: ServerScoreCard) -> dict[str, str | None]:
    """Extract server information from scorecard."""
    info: dict[str, str | None] = {
        "title": None,
        "name": None,
        "version": None,
        "protocol_version": None,
        "instructions": None,
    }

    if (
        hasattr(scorecard.initialize_result, "serverInfo")
        and scorecard.initialize_result.serverInfo
    ):
        server_info = scorecard.initialize_result.serverInfo
        info["title"] = getattr(server_info, "title", None)
        info["name"] = getattr(server_info, "name", None)
        info["version"] = getattr(server_info, "version", None)

    # Fallback title from parameters if not found
    if not info["title"] and hasattr(scorecard, "parameters"):
        if hasattr(scorecard.parameters, "command"):
            info["title"] = str(scorecard.parameters.command)
            if hasattr(scorecard.parameters, "args") and scorecard.parameters.args:
                info["title"] += " " + " ".join(
                    str(arg) for arg in scorecard.parameters.args
                )

    if hasattr(scorecard.initialize_result, "protocolVersion"):
        info["protocol_version"] = str(scorecard.initialize_result.protocolVersion)

    if hasattr(scorecard.initialize_result, "instructions"):
        info["instructions"] = scorecard.initialize_result.instructions

    return info


class Report:
    """Builder class for generating markdown reports."""

    def __init__(self, scorecard: ServerScoreCard):
        """Initialize a new Report builder."""
        self._lines: list[str] = []
        self._scorecard = scorecard

    def add_title(self, title: str, level: int = 1) -> "Report":
        """Add a title to the report."""
        prefix = "#" * level
        self._lines.append(f"{prefix} {title}")
        self._lines.append("")
        return self

    def add_text(self, text: str) -> "Report":
        """Add text content to the report."""
        self._lines.append(text)
        return self

    def add_blank_line(self) -> "Report":
        """Add a blank line to the report."""
        self._lines.append("")
        # self._lines.append("")
        return self

    def add_code_block(self, code: str, language: str = "") -> "Report":
        """Add a code block to the report."""
        self._lines.append(f"```{language}")
        self._lines.append(code)
        self._lines.append("```")
        return self

    def add_table_header(self, columns: list[str]) -> "Report":
        """Add a table header to the report."""
        self._lines.append("| " + " | ".join(columns) + " |")
        self._lines.append("|" + "|".join(["---" for _ in columns]) + "|")
        return self

    def add_table_row(self, values: list[str]) -> "Report":
        """Add a table row to the report."""
        self._lines.append("| " + " | ".join(values) + " |")
        return self

    def add_server_info(self) -> "Report":
        """Add server information section to the report."""
        if not self._scorecard:
            raise ValueError("Scorecard must be set before adding server info")

        info = get_server_info(self._scorecard)

        self.add_title("Server Information (🧮)", 2)
        self.add_blank_line()
        self.add_text(f"**Title:** {info.get('title') or 'No title found'}")
        self.add_blank_line()
        self.add_text(f"**Name:** {info.get('name') or 'No name found'}")
        self.add_blank_line()
        self.add_text(f"**Version:** {info.get('version') or 'No version found'}")
        self.add_blank_line()
        self.add_text(
            f"**Protocol Version:** {info.get('protocol_version') or 'No protocol version found'}"
        )
        self.add_blank_line()
        self.add_text(
            f"**Instructions:** {info.get('instructions') or 'No instructions found'}"
        )
        self.add_blank_line()

        return self

    def add_launch_parameters(self) -> "Report":
        """Add launch parameters section to the report."""
        if not self._scorecard:
            raise ValueError("Scorecard must be set before adding launch parameters")

        self.add_title("Launch Parameters (🧮)", 3)
        self.add_blank_line()

        params = []
        if hasattr(self._scorecard.parameters, "command"):
            params.append(f'"command": "{self._scorecard.parameters.command}"')
        if (
            hasattr(self._scorecard.parameters, "args")
            and self._scorecard.parameters.args
        ):
            args_str = ", ".join(f'"{arg}"' for arg in self._scorecard.parameters.args)
            params.append(f'"args": [{args_str}]')
        if (
            hasattr(self._scorecard.parameters, "env")
            and self._scorecard.parameters.env
        ):
            params.append(f'"env": {self._scorecard.parameters.env}')

        self.add_code_block("\n".join(params), "json")
        self.add_blank_line()

        return self

    def add_capabilities_table(self) -> "Report":
        """Add capabilities table to the report."""
        if not self._scorecard:
            raise ValueError("Scorecard must be set before adding capabilities")

        self.add_title("Capabilities (🧮)", 2)
        self.add_blank_line()

        caps = (
            self._scorecard.initialize_result.capabilities
            if hasattr(self._scorecard.initialize_result, "capabilities")
            else None
        )

        self.add_table_header(["Feature", "Supported"])

        # Check logging capability
        logging_supported = (
            "✅" if caps and getattr(caps, "logging", None) is not None else "❌"
        )
        self.add_table_row(["Logging", logging_supported])

        # Check prompts capabilities
        prompts_cap = getattr(caps, "prompts", None) if caps else None
        prompts_supported = "✅" if prompts_cap else "❌"
        self.add_table_row(["Prompts", prompts_supported])

        prompts_list_changed = (
            "✅" if prompts_cap and getattr(prompts_cap, "listChanged", False) else "❌"
        )
        self.add_table_row(["Prompts List Changed", prompts_list_changed])

        # Check resources capabilities
        resources_cap = getattr(caps, "resources", None) if caps else None
        resources_supported = "✅" if resources_cap else "❌"
        self.add_table_row(["Resources", resources_supported])

        resources_subscribe = (
            "✅"
            if resources_cap and getattr(resources_cap, "subscribe", False)
            else "❌"
        )
        self.add_table_row(["Resources Subscribe", resources_subscribe])

        resources_list_changed = (
            "✅"
            if resources_cap and getattr(resources_cap, "listChanged", False)
            else "❌"
        )
        self.add_table_row(["Resources List Changed", resources_list_changed])

        # Check tools capabilities
        tools_cap = getattr(caps, "tools", None) if caps else None
        tools_supported = "✅" if tools_cap else "❌"
        self.add_table_row(["Tools", tools_supported])

        tools_list_changed = (
            "✅" if tools_cap and getattr(tools_cap, "listChanged", False) else "❌"
        )
        self.add_table_row(["Tools List Changed", tools_list_changed])

        self.add_blank_line()

        return self

    def add_feature_counts(self) -> "Report":
        """Add feature counts table to the report."""
        if not self._scorecard:
            raise ValueError("Scorecard must be set before adding feature counts")

        self.add_title("Feature Summary (🧮)", 2)
        self.add_blank_line()

        self.add_table_header(["Feature", "Count"])
        self.add_table_row(["Tools", str(len(self._scorecard.tools))])
        self.add_table_row(["Prompts", str(len(self._scorecard.prompts))])
        self.add_table_row(["Resources", str(len(self._scorecard.resources))])
        self.add_table_row(
            ["Resource Templates", str(len(self._scorecard.resource_templates))]
        )

        self.add_blank_line()

        return self

    def add_score_summary(self, detailed: bool = False) -> "Report":
        """Add score summary section to the report."""
        if not self._scorecard:
            raise ValueError("Scorecard must be set before adding score summary")

        self.add_title("Score Summary (🤖)", 2)
        self.add_blank_line()

        tool_passes, tool_total = count_scores(self._scorecard.tool_scorecards)
        func_passes, func_total = count_scores(
            self._scorecard.functional_test_scorecard
        )
        total_passes = tool_passes + func_passes
        total_tests = tool_total + func_total
        percentage = (total_passes / total_tests * 100) if total_tests > 0 else 0

        if detailed:
            self.add_table_header(["Category", "Passed", "Total", "Percentage"])
            self.add_table_row(
                [
                    "Tool Quality",
                    str(tool_passes),
                    str(tool_total),
                    f"{(tool_passes / tool_total * 100) if tool_total > 0 else 0:.1f}%",
                ]
            )
            self.add_table_row(
                [
                    "Functional Tests",
                    str(func_passes),
                    str(func_total),
                    f"{(func_passes / func_total * 100) if func_total > 0 else 0:.1f}%",
                ]
            )
            self.add_table_row(
                [
                    "**Overall**",
                    f"**{total_passes}**",
                    f"**{total_tests}**",
                    f"**{percentage:.1f}%**",
                ]
            )
        else:
            # Overall score with visual indicator
            score_emoji = (
                "✅" if percentage >= 80 else "⚠️" if percentage >= 60 else "❌"
            )
            score_text = f"{score_emoji} **{percentage:.1f}%** ({total_passes}/{total_tests} passed)"
            self.add_text(f"**Overall Score:** {score_text}")

            if self._scorecard.tool_scorecards:
                self.add_blank_line()
                self.add_text(
                    f"**Tools Evaluated:** {len(self._scorecard.tool_scorecards)}"
                )
                tool_percentage = (
                    (tool_passes / tool_total * 100) if tool_total > 0 else 0
                )
                self.add_text(
                    f"- Tool Quality: {tool_percentage:.0f}% ({tool_passes}/{tool_total})"
                )

            self.add_blank_line()

            # Functional test summary
            func_test_status = (
                "✅ Passed"
                if self._scorecard.functional_test_scorecard.meets_expectations.score
                == "pass"
                else "❌ Failed"
            )
            self.add_text(f"**Functional Test:** {func_test_status}")
            self.add_blank_line()

            if self._scorecard.functional_test_scorecard.error_type.score != "N/A":
                self.add_text(
                    f"- Error Type: {self._scorecard.functional_test_scorecard.error_type.score}"
                )
                self.add_blank_line()

            func_percentage = (func_passes / func_total * 100) if func_total > 0 else 0
            self.add_text(
                f"- Test Coverage: {func_percentage:.0f}% ({func_passes}/{func_total})"
            )

        self.add_blank_line()

        return self

    def add_tool_scorecard(self, tool_index: int) -> "Report":
        """Add a single tool scorecard section to the report."""
        if not self._scorecard:
            raise ValueError("Scorecard must be set before adding tool scorecard")

        tool_scorecard = self._scorecard.tool_scorecards[tool_index]
        tool_name = (
            self._scorecard.tools[tool_index].name
            if tool_index < len(self._scorecard.tools)
            else f"Tool {tool_index + 1}"
        )

        self.add_title(f"Tool: `{tool_name}`", 3)
        self.add_blank_line()

        # Tool Name Assessment
        self.add_title("Naming Quality (🤖)", 4)
        self.add_blank_line()
        self.add_table_header(["Aspect", "Score", "Justification"])

        name_sc = tool_scorecard.tool_name
        self.add_table_row(
            ["Length", format_score(name_sc.length.score), name_sc.length.justification]
        )
        self.add_table_row(
            [
                "Uniqueness",
                format_score(name_sc.uniqueness.score),
                name_sc.uniqueness.justification,
            ]
        )
        self.add_table_row(
            [
                "Descriptiveness",
                format_score(name_sc.descriptiveness.score),
                name_sc.descriptiveness.justification,
            ]
        )
        self.add_blank_line()

        # Tool Description Assessment
        self.add_title("Description Quality (🤖)", 4)
        self.add_blank_line()
        self.add_table_header(["Aspect", "Score", "Justification"])

        desc_sc = tool_scorecard.tool_description
        self.add_table_row(
            ["Length", format_score(desc_sc.length.score), desc_sc.length.justification]
        )
        self.add_table_row(
            [
                "Parameters",
                format_score(desc_sc.parameters.score),
                desc_sc.parameters.justification,
            ]
        )
        self.add_table_row(
            [
                "Examples",
                format_score(desc_sc.examples.score),
                desc_sc.examples.justification,
            ]
        )
        self.add_blank_line()

        # Tool Schema Assessment (Input)
        self.add_title("Input Schema Quality (🤖)", 4)
        self.add_blank_line()
        self.add_table_header(["Aspect", "Score", "Justification"])

        schema_sc = tool_scorecard.tool_input_schema
        self.add_table_row(
            [
                "Complexity",
                format_score(schema_sc.complexity.score),
                schema_sc.complexity.justification,
            ]
        )
        self.add_table_row(
            [
                "Parameters",
                format_score(schema_sc.parameters.score),
                schema_sc.parameters.justification,
            ]
        )
        self.add_table_row(
            [
                "Optionals",
                format_score(schema_sc.optionals.score),
                schema_sc.optionals.justification,
            ]
        )
        self.add_table_row(
            [
                "Constraints",
                format_score(schema_sc.constraints.score),
                schema_sc.constraints.justification,
            ]
        )

        # Tool Schema Assessment (Output) if exists
        if hasattr(tool_scorecard, "tool_output_schema"):
            self.add_blank_line()
            self.add_title("Output Schema Quality (🤖)", 4)
            self.add_blank_line()
            self.add_table_header(["Aspect", "Score", "Justification"])

            output_sc = tool_scorecard.tool_output_schema
            self.add_table_row(
                [
                    "Complexity",
                    format_score(output_sc.complexity.score),
                    output_sc.complexity.justification,
                ]
            )
            self.add_table_row(
                [
                    "Parameters",
                    format_score(output_sc.parameters.score),
                    output_sc.parameters.justification,
                ]
            )
            self.add_table_row(
                [
                    "Optionals",
                    format_score(output_sc.optionals.score),
                    output_sc.optionals.justification,
                ]
            )
            self.add_table_row(
                [
                    "Constraints",
                    format_score(output_sc.constraints.score),
                    output_sc.constraints.justification,
                ]
            )

        self.add_blank_line()

        return self

    def add_failed_test_steps(self) -> "Report":
        """Add failed test steps section if any."""
        if not self._scorecard:
            raise ValueError("Scorecard must be set before adding failed test steps")

        failed_steps = []
        if (
            hasattr(self._scorecard, "functional_test_scorecard")
            and self._scorecard.functional_test_scorecard.steps
        ):
            for i, step in enumerate(
                self._scorecard.functional_test_scorecard.steps, 1
            ):
                if (
                    hasattr(step, "meets_expectations")
                    and step.meets_expectations.score == "fail"
                ):
                    failed_steps.append((i, step.tool_name, step.tool_arguments))

        if failed_steps:
            self.add_title("⚠️ Failed Test Steps (🤖)", 3)
            self.add_blank_line()
            for step_num, tool_name, tool_args in failed_steps:
                self.add_text(
                    f"- **Step {step_num}**: `{tool_name}` with arguments: `{json.dumps(tool_args, separators=(',', ':'))}`"
                )
            self.add_blank_line()

        return self

    def add_model_info(self) -> "Report":
        """Add model information if available."""
        if not self._scorecard:
            raise ValueError("Scorecard must be set before adding model info")

        if hasattr(self._scorecard, "model") and self._scorecard.model:
            self.add_text(f"**Evaluation Model:** {self._scorecard.model}")
            self.add_blank_line()

        return self

    def build(self) -> str:
        """Build and return the final markdown report."""
        return "\n".join(self._lines)

    def reset(self) -> "Report":
        """Reset the report builder."""
        self._lines = []
        self._scorecard = None
        return self

    def add_available_tools(self) -> "Report":
        """Add available tools section to the report."""
        if not self._scorecard:
            raise ValueError("Scorecard must be set before adding available tools")

        if self._scorecard.tools:
            self.add_title("Available Tools (🧮)", 2)
            self.add_blank_line()
            for tool in self._scorecard.tools:
                self.add_title(f"`{tool.name}`", 3)
                self.add_blank_line()
                if tool.description:
                    self.add_text(f"**Description:** {tool.description}")
                self.add_blank_line()

        return self

    def add_all_tool_scorecards(self) -> "Report":
        """Add all tool scorecards to the report."""
        if not self._scorecard:
            raise ValueError("Scorecard must be set before adding tool scorecards")

        if self._scorecard.tool_scorecards:
            self.add_title("Tool Quality Assessment (🤖)", 2)
            self.add_blank_line()

            for i in range(len(self._scorecard.tool_scorecards)):
                self.add_tool_scorecard(i)

        return self

    def add_functional_test_results(self) -> "Report":
        """Add functional test results section to the report."""
        if not self._scorecard:
            raise ValueError(
                "Scorecard must be set before adding functional test results"
            )

        self.add_title("Functional Test Results (🤖)", 2)
        self.add_blank_line()

        if self._scorecard.functional_test_scorecard.plan:
            self.add_title("Test Plan (🤖)", 3)
            self.add_blank_line()
            self.add_text(self._scorecard.functional_test_scorecard.plan)
            self.add_blank_line()

        self.add_title("Overall Test Result (🤖)", 3)
        self.add_blank_line()
        meets_exp = self._scorecard.functional_test_scorecard.meets_expectations
        self.add_text(f"**Status:** {format_score(meets_exp.score)}")
        self.add_blank_line()
        self.add_text(f"**Justification:** {meets_exp.justification}")
        self.add_blank_line()

        if self._scorecard.functional_test_scorecard.error_type.score != "N/A":
            self.add_text(
                f"**Error Type:** {self._scorecard.functional_test_scorecard.error_type.score}"
            )
            self.add_blank_line()
            self.add_text(
                f"**Error Justification:** {self._scorecard.functional_test_scorecard.error_type.justification}"
            )
            self.add_blank_line()

        # Individual Test Steps
        if self._scorecard.functional_test_scorecard.steps:
            self.add_title("Test Steps", 3)
            self.add_blank_line()

            for i, step in enumerate(
                self._scorecard.functional_test_scorecard.steps, 1
            ):
                # Add pass/fail indicator to step title
                status_icon = "✅" if step.meets_expectations.score == "pass" else "❌"
                self.add_title(f"{status_icon} Step {i}: {step.tool_name}", 4)
                self.add_blank_line()

                self.add_text(f"**Justification: (🤖)** {step.justification}")
                self.add_blank_line()

                self.add_text(f"**Expected Output: (🤖)** {step.expected_output}")
                self.add_blank_line()

                self.add_text("**Arguments: (🤖)**")
                self.add_blank_line()
                self.add_code_block(json.dumps(step.tool_arguments, indent=2), "json")
                self.add_blank_line()

                # Add tool output if available
                tool_output = step.tool_output or step.exception
                if tool_output is not None:
                    self.add_text("**Tool Output (🧮):**")
                    self.add_blank_line()
                    # Format and truncate tool output
                    if isinstance(tool_output, str):
                        output_type = ""
                        output_str = tool_output
                    else:
                        output_type = "json"
                        output_str = tool_output.model_dump_json(indent=2)

                    if len(output_str) > 500:
                        output_str = (
                            output_str[:500]
                            + f"... ({len(output_str) - 500} chars truncated)"
                        )

                    self.add_code_block(output_str, output_type)
                    self.add_blank_line()

                # Request tracking
                self.add_text("**Request Tracking (🧮):**")
                self.add_blank_line()
                self.add_text(
                    f"- Sampling Requests: {getattr(step, 'sampling_requests', 0)}"
                )
                self.add_blank_line()
                self.add_text(
                    f"- Elicitation Requests: {getattr(step, 'elicitation_requests', 0)}"
                )
                self.add_blank_line()
                self.add_text(
                    f"- List Roots Requests: {getattr(step, 'list_roots_requests', 0)}"
                )
                self.add_blank_line()
                self.add_text(
                    f"- Logging Requests: {getattr(step, 'logging_requests', 0)}"
                )
                self.add_blank_line()

                # Test Results
                self.add_text("**Results: (🤖)**")
                self.add_blank_line()
                self.add_table_header(["Criterion", "Score", "Justification"])

                self.add_table_row(
                    [
                        "Error Handling",
                        format_score(step.error_handling.score),
                        step.error_handling.justification,
                    ]
                )

                if step.error_type.score != "N/A":
                    self.add_table_row(
                        [
                            "Error Type",
                            step.error_type.score,
                            step.error_type.justification,
                        ]
                    )

                if hasattr(step, "no_silent_error"):
                    self.add_table_row(
                        [
                            "No Silent Error",
                            format_score(step.no_silent_error.score),
                            step.no_silent_error.justification,
                        ]
                    )

                self.add_table_row(
                    [
                        "Output Relevance",
                        format_score(step.output_relevance.score),
                        step.output_relevance.justification,
                    ]
                )
                self.add_table_row(
                    [
                        "Output Quality",
                        format_score(step.output_quality.score),
                        step.output_quality.justification,
                    ]
                )
                self.add_table_row(
                    [
                        "Schema Compliance",
                        format_score(step.schema_compliance.score),
                        step.schema_compliance.justification,
                    ]
                )
                self.add_table_row(
                    [
                        "Meets Expectations",
                        format_score(step.meets_expectations.score),
                        step.meets_expectations.justification,
                    ]
                )
                self.add_blank_line()

        return self

    def add_detailed_failed_test_steps(self) -> "Report":
        """Add detailed failed test steps section."""
        if not self._scorecard:
            raise ValueError(
                "Scorecard must be set before adding detailed failed test steps"
            )

        failed_steps = []
        if (
            hasattr(self._scorecard, "functional_test_scorecard")
            and self._scorecard.functional_test_scorecard.steps
        ):
            for i, step in enumerate(
                self._scorecard.functional_test_scorecard.steps, 1
            ):
                if (
                    hasattr(step, "meets_expectations")
                    and step.meets_expectations.score == "fail"
                ):
                    failed_steps.append(
                        (
                            i,
                            step.tool_name,
                            step.tool_arguments,
                            step.meets_expectations.justification,
                            getattr(step, "tool_output", None),
                        )
                    )

        if failed_steps:
            self.add_title("⚠️ Failed Test Steps (🤖)", 2)
            self.add_blank_line()
            self.add_text("The following test steps did not meet expectations:")
            self.add_blank_line()

            for (
                step_num,
                tool_name,
                tool_args,
                justification,
                tool_output,
            ) in failed_steps:
                self.add_title(f"❌ Step {step_num}: `{tool_name}`", 3)
                self.add_blank_line()
                self.add_text(f"**Failure Reason:** {justification}")
                self.add_blank_line()
                self.add_text("**Arguments (🤖):**")
                self.add_code_block(json.dumps(tool_args, indent=2), "json")
                self.add_blank_line()
                if tool_output is not None:
                    self.add_text("**Tool Output (🧮):**")
                    # Format tool output based on its type
                    if isinstance(tool_output, Exception):
                        self.add_code_block(str(tool_output), "")
                    elif isinstance(tool_output, str):
                        self.add_code_block(tool_output, "json")
                    else:
                        try:
                            self.add_code_block(
                                json.dumps(tool_output, indent=2), "json"
                            )
                        except:
                            self.add_code_block(str(tool_output), "")
                    self.add_blank_line()

        return self

    def add_emoji_legend(self) -> "Report":
        """Add emoji legend to the report."""
        self.add_text("**Legend:**")
        self.add_blank_line()
        self.add_text("- (🤖) = AI-generated content")
        self.add_blank_line()
        self.add_text("- (🧮) = Computed metrics and data")
        self.add_blank_line()
        self.add_text("---")
        self.add_blank_line()
        return self

    def add_constraint_violations(
        self, violations: list[ConstraintViolation] | None
    ) -> "Report":
        """Add constraint violations section to the report."""
        if not violations:
            self.add_title("✅ Constraint Violations (🧮)", 2)
            self.add_text("No constraint violations found.")
            self.add_blank_line()
            return self

        # Separate by severity
        critical_violations = [v for v in violations if v.severity == Severity.CRITICAL]
        warning_violations = [v for v in violations if v.severity == Severity.WARNING]

        if critical_violations or warning_violations:
            self.add_title("⚠️ Constraint Violations (🧮)", 2)
            self.add_blank_line()

        if critical_violations:
            self.add_title("🚨 Critical Issues (🧮)", 3)
            self.add_blank_line()
            for violation in critical_violations:
                constraint_name = violation.constraint.__class__.__name__
                self.add_text(f"- **{constraint_name}:** {violation.message}")
            self.add_blank_line()

        if warning_violations:
            self.add_title("⚠️ Warnings (🧮)", 3)
            self.add_blank_line()
            for violation in warning_violations:
                constraint_name = violation.constraint.__class__.__name__
                self.add_text(f"- **{constraint_name}:** {violation.message}")
            self.add_blank_line()

        return self


def generate_summary_markdown(
    scorecard: ServerScoreCard, violations: list[ConstraintViolation] | None = None
) -> str:
    """Generate a concise Markdown summary suitable for a README."""
    report = Report(scorecard)

    report.add_title("📊 MCP Server Score Card", 2)
    report.add_blank_line()
    report.add_emoji_legend()
    report.add_model_info()
    report.add_server_info()
    report.add_launch_parameters()
    report.add_capabilities_table()
    report.add_feature_counts()
    report.add_score_summary(detailed=True)
    report.add_constraint_violations(violations)
    report.add_failed_test_steps()

    return report.build()


def generate_full_markdown(
    scorecard: ServerScoreCard, violations: list[ConstraintViolation] | None = None
) -> str:
    """Generate a complete detailed Markdown report."""
    report = Report(scorecard)

    report.add_title("MCP Server Full Evaluation Report", 1)
    report.add_blank_line()
    report.add_emoji_legend()
    report.add_model_info()
    report.add_server_info()
    report.add_launch_parameters()
    report.add_capabilities_table()
    report.add_feature_counts()
    report.add_score_summary(detailed=True)
    report.add_constraint_violations(violations)
    report.add_detailed_failed_test_steps()
    report.add_available_tools()
    report.add_all_tool_scorecards()
    report.add_functional_test_results()

    return report.build()
