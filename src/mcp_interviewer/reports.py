"""Markdown report generation for MCP Server evaluation results."""

import json
from typing import Any

from pydantic import BaseModel

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


def generate_capabilities_table(scorecard: ServerScoreCard) -> list[str]:
    """Generate capabilities table markdown lines."""
    lines = []

    caps = (
        scorecard.initialize_result.capabilities
        if hasattr(scorecard.initialize_result, "capabilities")
        else None
    )

    lines.append("| Feature | Supported |")
    lines.append("|---------|-----------|")

    # Check logging capability
    logging_supported = (
        "✅" if caps and getattr(caps, "logging", None) is not None else "❌"
    )
    lines.append(f"| Logging | {logging_supported} |")

    # Check prompts capabilities
    prompts_cap = getattr(caps, "prompts", None) if caps else None
    prompts_supported = "✅" if prompts_cap else "❌"
    lines.append(f"| Prompts | {prompts_supported} |")

    prompts_list_changed = (
        "✅" if prompts_cap and getattr(prompts_cap, "listChanged", False) else "❌"
    )
    lines.append(f"| Prompts List Changed | {prompts_list_changed} |")

    # Check resources capabilities
    resources_cap = getattr(caps, "resources", None) if caps else None
    resources_supported = "✅" if resources_cap else "❌"
    lines.append(f"| Resources | {resources_supported} |")

    resources_subscribe = (
        "✅" if resources_cap and getattr(resources_cap, "subscribe", False) else "❌"
    )
    lines.append(f"| Resources Subscribe | {resources_subscribe} |")

    resources_list_changed = (
        "✅" if resources_cap and getattr(resources_cap, "listChanged", False) else "❌"
    )
    lines.append(f"| Resources List Changed | {resources_list_changed} |")

    # Check tools capabilities
    tools_cap = getattr(caps, "tools", None) if caps else None
    tools_supported = "✅" if tools_cap else "❌"
    lines.append(f"| Tools | {tools_supported} |")

    tools_list_changed = (
        "✅" if tools_cap and getattr(tools_cap, "listChanged", False) else "❌"
    )
    lines.append(f"| Tools List Changed | {tools_list_changed} |")

    return lines


def generate_feature_counts_table(scorecard: ServerScoreCard) -> list[str]:
    """Generate feature counts table markdown lines."""
    lines = []
    lines.append("| Feature | Count |")
    lines.append("|---------|-------|")
    lines.append(f"| Tools | {len(scorecard.tools)} |")
    lines.append(f"| Prompts | {len(scorecard.prompts)} |")
    lines.append(f"| Resources | {len(scorecard.resources)} |")
    lines.append(f"| Resource Templates | {len(scorecard.resource_templates)} |")
    return lines


def generate_score_summary(
    scorecard: ServerScoreCard, detailed: bool = False
) -> list[str]:
    """Generate score summary section."""
    lines = []

    tool_passes, tool_total = count_scores(scorecard.tool_scorecards)
    func_passes, func_total = count_scores(scorecard.functional_test_scorecard)
    total_passes = tool_passes + func_passes
    total_tests = tool_total + func_total
    percentage = (total_passes / total_tests * 100) if total_tests > 0 else 0

    if detailed:
        lines.append("| Category | Passed | Total | Percentage |")
        lines.append("|----------|--------|-------|------------|")
        lines.append(
            f"| Tool Quality | {tool_passes} | {tool_total} | "
            f"{(tool_passes / tool_total * 100) if tool_total > 0 else 0:.1f}% |"
        )
        lines.append(
            f"| Functional Tests | {func_passes} | {func_total} | "
            f"{(func_passes / func_total * 100) if func_total > 0 else 0:.1f}% |"
        )
        lines.append(
            f"| **Overall** | **{total_passes}** | **{total_tests}** | **{percentage:.1f}%** |"
        )
    else:
        # Overall score with visual indicator
        score_emoji = "✅" if percentage >= 80 else "⚠️" if percentage >= 60 else "❌"
        score_text = (
            f"{score_emoji} **{percentage:.1f}%** ({total_passes}/{total_tests} passed)"
        )
        lines.append(f"**Overall Score:** {score_text}")

        if scorecard.tool_scorecards:
            lines.append("")
            lines.append("")
            lines.append(f"**Tools Evaluated:** {len(scorecard.tool_scorecards)}")
            tool_percentage = (tool_passes / tool_total * 100) if tool_total > 0 else 0
            lines.append(
                f"- Tool Quality: {tool_percentage:.0f}% ({tool_passes}/{tool_total})"
            )

        lines.append("")
        lines.append("")

        # Functional test summary
        func_test_status = (
            "✅ Passed"
            if scorecard.functional_test_scorecard.meets_expectations.score == "pass"
            else "❌ Failed"
        )
        lines.append(f"**Functional Test:** {func_test_status}")
        lines.append("")

        if scorecard.functional_test_scorecard.error_type.score != "N/A":
            lines.append(
                f"- Error Type: {scorecard.functional_test_scorecard.error_type.score}"
            )
            lines.append("")

        func_percentage = (func_passes / func_total * 100) if func_total > 0 else 0
        lines.append(
            f"- Test Coverage: {func_percentage:.0f}% ({func_passes}/{func_total})"
        )

    return lines


def generate_tool_scorecard_section(
    scorecard: ServerScoreCard, tool_index: int
) -> list[str]:
    """Generate markdown for a single tool scorecard."""
    lines = []
    tool_scorecard = scorecard.tool_scorecards[tool_index]
    tool_name = (
        scorecard.tools[tool_index].name
        if tool_index < len(scorecard.tools)
        else f"Tool {tool_index + 1}"
    )

    lines.append(f"### Tool: `{tool_name}`")
    lines.append("")
    lines.append("")

    # Tool Name Assessment
    lines.append("#### Naming Quality")
    lines.append("")
    lines.append("")
    lines.append("| Aspect | Score | Justification |")
    lines.append("|--------|-------|---------------|")

    name_sc = tool_scorecard.tool_name
    lines.append(
        f"| Length | {format_score(name_sc.length.score)} | "
        f"{name_sc.length.justification} |"
    )
    lines.append(
        f"| Uniqueness | {format_score(name_sc.uniqueness.score)} | "
        f"{name_sc.uniqueness.justification} |"
    )
    lines.append(
        f"| Descriptiveness | {format_score(name_sc.descriptiveness.score)} | "
        f"{name_sc.descriptiveness.justification} |"
    )
    lines.append("")
    lines.append("")

    # Tool Description Assessment
    lines.append("#### Description Quality")
    lines.append("")
    lines.append("")
    lines.append("| Aspect | Score | Justification |")
    lines.append("|--------|-------|---------------|")

    desc_sc = tool_scorecard.tool_description
    lines.append(
        f"| Length | {format_score(desc_sc.length.score)} | "
        f"{desc_sc.length.justification} |"
    )
    lines.append(
        f"| Parameters | {format_score(desc_sc.parameters.score)} | "
        f"{desc_sc.parameters.justification} |"
    )
    lines.append(
        f"| Examples | {format_score(desc_sc.examples.score)} | "
        f"{desc_sc.examples.justification} |"
    )
    lines.append("")
    lines.append("")

    # Tool Schema Assessment (Input)
    lines.append("#### Input Schema Quality")
    lines.append("")
    lines.append("")
    lines.append("| Aspect | Score | Justification |")
    lines.append("|--------|-------|---------------|")

    schema_sc = tool_scorecard.tool_input_schema
    lines.append(
        f"| Complexity | {format_score(schema_sc.complexity.score)} | "
        f"{schema_sc.complexity.justification} |"
    )
    lines.append(
        f"| Parameters | {format_score(schema_sc.parameters.score)} | "
        f"{schema_sc.parameters.justification} |"
    )
    lines.append(
        f"| Optionals | {format_score(schema_sc.optionals.score)} | "
        f"{schema_sc.optionals.justification} |"
    )
    lines.append(
        f"| Constraints | {format_score(schema_sc.constraints.score)} | "
        f"{schema_sc.constraints.justification} |"
    )

    # Tool Schema Assessment (Output) if exists
    if hasattr(tool_scorecard, "tool_output_schema"):
        lines.append("")
        lines.append("")
        lines.append("#### Output Schema Quality")
        lines.append("")
        lines.append("")
        lines.append("| Aspect | Score | Justification |")
        lines.append("|--------|-------|---------------|")

        output_sc = tool_scorecard.tool_output_schema
        lines.append(
            f"| Complexity | {format_score(output_sc.complexity.score)} | "
            f"{output_sc.complexity.justification} |"
        )
        lines.append(
            f"| Parameters | {format_score(output_sc.parameters.score)} | "
            f"{output_sc.parameters.justification} |"
        )
        lines.append(
            f"| Optionals | {format_score(output_sc.optionals.score)} | "
            f"{output_sc.optionals.justification} |"
        )
        lines.append(
            f"| Constraints | {format_score(output_sc.constraints.score)} | "
            f"{output_sc.constraints.justification} |"
        )

    lines.append("")
    lines.append("")

    return lines


def generate_summary_markdown(scorecard: ServerScoreCard) -> str:
    """Generate a concise Markdown summary suitable for a README."""
    lines = []
    lines.append("## 📊 MCP Server Score Card")
    lines.append("")
    lines.append("")

    # Model used for evaluation
    if hasattr(scorecard, "model") and scorecard.model:
        lines.append(f"**Evaluation Model:** {scorecard.model}")
        lines.append("")
        lines.append("")

    # Server Information
    lines.append("## Server Information")
    lines.append("")
    lines.append("")

    server_info = get_server_info(scorecard)
    lines.append(f"**Title:** {server_info.get('title') or 'No title found'}")
    lines.append(f"**Name:** {server_info.get('name') or 'No name found'}")
    lines.append(f"**Version:** {server_info.get('version') or 'No version found'}")
    lines.append(
        f"**Protocol Version:** {server_info.get('protocol_version') or 'No protocol version found'}"
    )
    lines.append(
        f"**Instructions:** {server_info.get('instructions') or 'No instructions found'}"
    )

    lines.append("")
    lines.append("")

    # Launch Parameters
    lines.append("### Launch Parameters")
    lines.append("")
    lines.append("")
    lines.append("```json")
    if hasattr(scorecard.parameters, "command"):
        lines.append(f'"command": "{scorecard.parameters.command}"')
    if hasattr(scorecard.parameters, "args") and scorecard.parameters.args:
        args_str = ", ".join(f'"{arg}"' for arg in scorecard.parameters.args)
        lines.append(f'"args": [{args_str}]')
    if hasattr(scorecard.parameters, "env") and scorecard.parameters.env:
        lines.append(f'"env": {scorecard.parameters.env}')
    lines.append("```")
    lines.append("")
    lines.append("")

    # Capabilities
    lines.append("## Capabilities")
    lines.append("")
    lines.append("")
    lines.extend(generate_capabilities_table(scorecard))
    lines.append("")
    lines.append("")

    # Feature Summary
    lines.append("## Feature Summary")
    lines.append("")
    lines.append("")
    lines.extend(generate_feature_counts_table(scorecard))
    lines.append("")
    lines.append("")

    # Score Summary
    lines.append("## Score Summary")
    lines.append("")
    lines.append("")
    lines.extend(generate_score_summary(scorecard, detailed=True))

    return "\n".join(lines)


def generate_full_markdown(scorecard: ServerScoreCard) -> str:
    """Generate a complete detailed Markdown report."""
    lines = []

    # Header
    lines.append("# MCP Server Full Evaluation Report")
    lines.append("")
    lines.append("")

    # Model used for evaluation
    if hasattr(scorecard, "model") and scorecard.model:
        lines.append(f"**Evaluation Model:** {scorecard.model}")
        lines.append("")
        lines.append("")

    # Server Information
    lines.append("## Server Information")
    lines.append("")
    lines.append("")

    server_info = get_server_info(scorecard)
    lines.append(f"**Title:** {server_info.get('title') or 'No title found'}")
    lines.append(f"**Name:** {server_info.get('name') or 'No name found'}")
    lines.append(f"**Version:** {server_info.get('version') or 'No version found'}")
    lines.append(
        f"**Protocol Version:** {server_info.get('protocol_version') or 'No protocol version found'}"
    )
    lines.append(
        f"**Instructions:** {server_info.get('instructions') or 'No instructions found'}"
    )

    lines.append("")
    lines.append("")

    # Launch Parameters
    lines.append("### Launch Parameters")
    lines.append("")
    lines.append("")
    lines.append("```json")
    if hasattr(scorecard.parameters, "command"):
        lines.append(f'"command": "{scorecard.parameters.command}"')
    if hasattr(scorecard.parameters, "args") and scorecard.parameters.args:
        args_str = ", ".join(f'"{arg}"' for arg in scorecard.parameters.args)
        lines.append(f'"args": [{args_str}]')
    if hasattr(scorecard.parameters, "env") and scorecard.parameters.env:
        lines.append(f'"env": {scorecard.parameters.env}')
    lines.append("```")
    lines.append("")
    lines.append("")

    # Capabilities
    lines.append("## Capabilities")
    lines.append("")
    lines.append("")
    lines.extend(generate_capabilities_table(scorecard))
    lines.append("")
    lines.append("")

    # Feature Summary
    lines.append("## Feature Summary")
    lines.append("")
    lines.append("")
    lines.extend(generate_feature_counts_table(scorecard))
    lines.append("")
    lines.append("")

    # Score Summary
    lines.append("## Score Summary")
    lines.append("")
    lines.append("")
    lines.extend(generate_score_summary(scorecard, detailed=True))

    # Tools Details
    if scorecard.tools:
        lines.append("## Available Tools")
        lines.append("")
        lines.append("")
        for tool in scorecard.tools:
            lines.append(f"### `{tool.name}`")
            lines.append("")
            if tool.description:
                lines.append(f"**Description:** {tool.description}")
            lines.append("")
            lines.append("")

    # Tool Scorecards
    if scorecard.tool_scorecards:
        lines.append("## Tool Quality Assessment")
        lines.append("")
        lines.append("")

        for i in range(len(scorecard.tool_scorecards)):
            lines.extend(generate_tool_scorecard_section(scorecard, i))

    # Functional Test Results
    lines.append("## Functional Test Results")
    lines.append("")
    lines.append("")

    if scorecard.functional_test_scorecard.plan:
        lines.append("### Test Plan")
        lines.append("")
        lines.append("")
        lines.append(scorecard.functional_test_scorecard.plan)
        lines.append("")
        lines.append("")

    lines.append("### Overall Test Result")
    lines.append("")
    lines.append("")
    meets_exp = scorecard.functional_test_scorecard.meets_expectations
    lines.append(f"**Status:** {format_score(meets_exp.score)}")
    lines.append(f"**Justification:** {meets_exp.justification}")
    lines.append("")
    lines.append("")

    if scorecard.functional_test_scorecard.error_type.score != "N/A":
        lines.append(
            f"**Error Type:** {scorecard.functional_test_scorecard.error_type.score}"
        )
        lines.append(
            f"**Error Justification:** {scorecard.functional_test_scorecard.error_type.justification}"
        )
        lines.append("")
        lines.append("")

    # Individual Test Steps
    if scorecard.functional_test_scorecard.steps:
        lines.append("### Test Steps")
        lines.append("")
        lines.append("")

        for i, step in enumerate(scorecard.functional_test_scorecard.steps, 1):
            lines.append(f"#### Step {i}: {step.tool_name}")
            lines.append("")
            lines.append("")

            lines.append(f"**Justification:** {step.justification}")
            lines.append("")
            lines.append("")

            lines.append(f"**Expected Output:** {step.expected_output}")
            lines.append("")
            lines.append("")

            lines.append("**Arguments:**")
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(step.tool_arguments, indent=2))
            lines.append("```")
            lines.append("")
            lines.append("")

            # Request tracking (if available)
            if any(
                hasattr(step, field)
                for field in [
                    "sampling_requests",
                    "elicitation_requests",
                    "list_roots_requests",
                    "logging_requests",
                ]
            ):
                lines.append("**Request Tracking:**")
                lines.append("")
                if hasattr(step, "sampling_requests"):
                    lines.append(f"- Sampling Requests: {step.sampling_requests}")
                if hasattr(step, "elicitation_requests"):
                    lines.append(f"- Elicitation Requests: {step.elicitation_requests}")
                if hasattr(step, "list_roots_requests"):
                    lines.append(f"- List Roots Requests: {step.list_roots_requests}")
                if hasattr(step, "logging_requests"):
                    lines.append(f"- Logging Requests: {step.logging_requests}")
                lines.append("")
                lines.append("")

            # Test Results
            lines.append("**Results:**")
            lines.append("")
            lines.append("")
            lines.append("| Criterion | Score | Justification |")
            lines.append("|-----------|-------|---------------|")

            lines.append(
                f"| Error Handling | {format_score(step.error_handling.score)} | "
                f"{step.error_handling.justification} |"
            )

            if step.error_type.score != "N/A":
                lines.append(
                    f"| Error Type | {step.error_type.score} | "
                    f"{step.error_type.justification} |"
                )

            if hasattr(step, "no_silent_error"):
                lines.append(
                    f"| No Silent Error | {format_score(step.no_silent_error.score)} | "
                    f"{step.no_silent_error.justification} |"
                )

            lines.append(
                f"| Output Relevance | {format_score(step.output_relevance.score)} | "
                f"{step.output_relevance.justification} |"
            )
            lines.append(
                f"| Output Quality | {format_score(step.output_quality.score)} | "
                f"{step.output_quality.justification} |"
            )
            lines.append(
                f"| Schema Compliance | {format_score(step.schema_compliance.score)} | "
                f"{step.schema_compliance.justification} |"
            )
            lines.append(
                f"| Meets Expectations | {format_score(step.meets_expectations.score)} | "
                f"{step.meets_expectations.justification} |"
            )
            lines.append("")
            lines.append("")

    return "\n".join(lines)
