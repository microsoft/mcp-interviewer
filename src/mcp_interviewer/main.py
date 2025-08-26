import asyncio
import logging
from pathlib import Path

from openai import OpenAI

from .constraints.base import Constraint, Severity
from .constraints.openai import (
    OpenAIConstraints,
    OpenAIToolCountConstraint,
    OpenAIToolNameLengthConstraint,
    OpenAIToolNamePatternConstraint,
    OpenAIToolResultTokenLengthConstraint,
)
from .interviewer import MCPInterviewer
from .models import ServerParameters
from .reports import FullReport, ShortReport
from .reports.base import BaseReportOptions
from .reports.custom import CustomReport

logger = logging.getLogger(__name__)


def get_selected_constraints(
    selected: list[str] | None = None,
) -> list[type[Constraint]]:
    """Get list of constraint classes based on selection.

    Args:
        selected: List of constraint names or codes to include (all if None)

    Returns:
        List of constraint classes to use
    """
    # All available constraint classes
    ALL_CONSTRAINT_CLASSES = [
        OpenAIToolCountConstraint,
        OpenAIToolNameLengthConstraint,
        OpenAIToolNamePatternConstraint,
        OpenAIToolResultTokenLengthConstraint,
    ]

    # Create mappings for names and codes
    CONSTRAINT_MAPPING = {cls.cli_name(): cls for cls in ALL_CONSTRAINT_CLASSES}
    SHORTHAND_MAPPING = {
        cls.cli_code(): cls.cli_name() for cls in ALL_CONSTRAINT_CLASSES
    }

    # Also add the composite constraint
    CONSTRAINT_MAPPING[OpenAIConstraints.cli_name()] = OpenAIConstraints
    SHORTHAND_MAPPING[OpenAIConstraints.cli_code()] = OpenAIConstraints.cli_name()

    if not selected:
        # Default to all individual constraints (not the composite)
        return ALL_CONSTRAINT_CLASSES

    result = []
    for item in selected:
        # Check if it's a shorthand code
        if item in SHORTHAND_MAPPING:
            constraint_name = SHORTHAND_MAPPING[item]
        else:
            constraint_name = item

        if constraint_name in CONSTRAINT_MAPPING:
            constraint_class = CONSTRAINT_MAPPING[constraint_name]
            if constraint_class == OpenAIConstraints:
                # If OpenAIConstraints is selected, add all OpenAI constraints
                result.extend(ALL_CONSTRAINT_CLASSES)
            else:
                result.append(constraint_class)
        else:
            logger.warning(f"Unknown constraint: {item}")

    # Remove duplicates while preserving order
    seen = set()
    unique_result = []
    for cls in result:
        if cls not in seen:
            seen.add(cls)
            unique_result.append(cls)

    return unique_result


async def amain(
    client: OpenAI,
    model: str,
    params: ServerParameters,
    out_dir=Path("."),
    should_score_tool: bool = False,
    should_score_functional_test: bool = False,
    short_report: bool = False,
    custom_reports: list[str] | None = None,
    no_collapse: bool = False,
    selected_constraints: list[str] | None = None,
):
    """Asynchronous main function to evaluate an MCP server and generate reports.

    Performs a complete server evaluation and saves the results in multiple formats:
    - Full markdown report (mcp-scorecard.md) or short report based on options
    - Raw JSON data (mcp-scorecard.json)

    Args:
        client: OpenAI client for LLM-based evaluation
        model: Model name to use for evaluation (e.g., "gpt-4")
        params: ServerParameters for the MCP server to evaluate
        out_dir: Directory to save output files (default: current directory)
        should_score_tool: Whether to perform expensive LLM scoring of tools (default: False)
        should_score_functional_test: Whether to perform expensive LLM scoring of functional tests (default: False)
        short_report: If True, generate short report instead of full report (default: False)
        custom_reports: List of specific report names to include (overrides short_report)
        no_collapse: If True, don't use collapsible sections in the report (default: False)
        selected_constraints: List of constraint names or codes to check (all if None)
    """
    interviewer = MCPInterviewer(
        client, model, should_score_tool, should_score_functional_test
    )
    scorecard = await interviewer.score_server(params)

    # Get constraint violations based on selected constraints
    violations = []
    constraint_classes = get_selected_constraints(selected_constraints)
    for constraint_class in constraint_classes:
        constraint = constraint_class()
        violations.extend(list(constraint.test(scorecard)))

    for violation in violations:
        if violation.severity == Severity.WARNING:
            logger.warning(
                f"{type(violation.constraint).__name__}: {violation.message}"
            )
        elif violation.severity == Severity.CRITICAL:
            logger.critical(
                f"{type(violation.constraint).__name__}: {violation.message}"
            )

    # Create report options
    options = BaseReportOptions(use_collapsible=not no_collapse)

    # Generate the appropriate report based on options
    if custom_reports:
        # Custom report with selected components
        path = out_dir / Path("mcp-scorecard.md")
        logger.info(
            f"Saving custom scorecard with reports: {', '.join(custom_reports)} to {path}"
        )
        with open(path, "w") as fd:
            report = CustomReport(
                scorecard, custom_reports, violations, options, selected_constraints
            )
            fd.write(report.build())
    elif short_report:
        # Short report only
        path = out_dir / Path("mcp-scorecard.md")
        logger.info(f"Saving short scorecard to {path}")
        with open(path, "w") as fd:
            report = ShortReport(scorecard, violations, options, selected_constraints)
            fd.write(report.build())
    else:
        # Full report (default)
        path = out_dir / Path("mcp-scorecard.md")
        logger.info(f"Saving full scorecard to {path}")
        with open(path, "w") as fd:
            report = FullReport(scorecard, violations, options, selected_constraints)
            fd.write(report.build())

    path = out_dir / Path("mcp-scorecard.json")
    logger.info(f"Saving scorecard json data to {path}")
    with open(path, "w") as fd:
        fd.write(scorecard.model_dump_json(indent=2))


def main(
    client: OpenAI,
    model: str,
    params: ServerParameters,
    out_dir=Path("."),
    should_score_tool: bool = False,
    should_score_functional_test: bool = False,
    short_report: bool = False,
    custom_reports: list[str] | None = None,
    no_collapse: bool = False,
    selected_constraints: list[str] | None = None,
):
    """Synchronous wrapper for the main evaluation function.

    Args:
        client: OpenAI client for LLM-based evaluation
        model: Model name to use for evaluation (e.g., "gpt-4")
        params: ServerParameters for the MCP server to evaluate
        out_dir: Directory to save output files (default: current directory)
        should_score_tool: Whether to perform expensive LLM scoring of tools (default: False)
        should_score_functional_test: Whether to perform expensive LLM scoring of functional tests (default: False)
        short_report: If True, generate short report instead of full report (default: False)
        custom_reports: List of specific report names to include (overrides short_report)
        no_collapse: If True, don't use collapsible sections in the report (default: False)
        selected_constraints: List of constraint names or codes to check (all if None)
    """
    asyncio.run(
        amain(
            client,
            model,
            params,
            out_dir,
            should_score_tool,
            should_score_functional_test,
            short_report,
            custom_reports,
            no_collapse,
            selected_constraints,
        )
    )
