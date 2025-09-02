"""Test judging functionality."""

import logging

from .. import prompts
from ..models import (
    Client,
    FunctionalTest,
    FunctionalTestOutput,
    FunctionalTestScoreCard,
    FunctionalTestStep,
    FunctionalTestStepOutput,
    FunctionalTestStepScoreCard,
)

logger = logging.getLogger(__name__)


async def judge_functional_test_step(
    client: Client,
    model: str,
    step: FunctionalTestStep,
    output: FunctionalTestStepOutput,
    should_judge: bool = False,
) -> FunctionalTestStepScoreCard:
    """Judge a single functional test step output.

    Evaluates the step based on error handling, output relevance, quality,
    schema compliance, and whether it meets expectations.

    Args:
        client: OpenAI client (sync or async) for LLM-based evaluation
        model: Model name to use for evaluation
        step: The FunctionalTestStep to evaluate
        output: The FunctionalTestStepOutput to evaluate
        should_judge: Whether to perform expensive experimental LLM judging

    Returns:
        FunctionalTestStepScoreCard with detailed judging for the step

    Raises:
        Exception: If step judging fails
    """
    if not should_judge:
        logger.info(
            f"Skipping judging for test step '{step.tool_name}' (judging disabled)"
        )
        from ..models import ErrorType, PassFailScoreCard, ScoreCard

        na_scorecard = PassFailScoreCard(
            justification="No score generated", score="N/A"
        )

        # Create error type scorecard with the correct literal type
        na_error_type = ScoreCard[ErrorType](
            justification="No score generated", score="N/A"
        )

        return FunctionalTestStepScoreCard(
            # Include the step data
            justification=step.justification,
            expected_output=step.expected_output,
            tool_name=step.tool_name,
            tool_arguments=step.tool_arguments,
            # Include the output data
            tool_output=output.tool_output,
            exception=output.exception,
            sampling_requests=output.sampling_requests,
            elicitation_requests=output.elicitation_requests,
            list_roots_requests=output.list_roots_requests,
            logging_requests=output.logging_requests,
            # Add the evaluation rubric with N/A scores
            error_handling=na_scorecard,
            error_type=na_error_type,
            no_silent_error=na_scorecard,
            output_relevance=na_scorecard,
            output_quality=na_scorecard,
            schema_compliance=na_scorecard,
            meets_expectations=na_scorecard,
        )

    try:
        logger.debug(f"Judging step '{step.tool_name}'")
        scorecard = await prompts.score_functional_test_step_output(
            client, model, step, output
        )
        logger.debug(f"Step scorecard: {scorecard}")
        return scorecard
    except Exception as e:
        logger.error(
            f"Failed to judge test step '{step.tool_name}': {e}", exc_info=True
        )
        raise


async def judge_functional_test(
    client: Client,
    model: str,
    test: FunctionalTest,
    output: FunctionalTestOutput,
    step_outputs: list[FunctionalTestStepOutput],
    should_judge: bool = False,
) -> FunctionalTestScoreCard:
    """Judge the entire functional test output.

    Evaluates the overall test execution, including all individual steps,
    to determine if the server meets functional expectations.

    Args:
        client: OpenAI client (sync or async) for LLM-based evaluation
        model: Model name to use for evaluation
        test: The FunctionalTest containing test plan and steps
        output: The FunctionalTestOutput containing all step results
        step_outputs: List of individual step outputs
        should_judge: Whether to perform expensive experimental LLM judging

    Returns:
        FunctionalTestScoreCard with overall test judging and individual step scores

    Raises:
        Exception: If test judging fails
    """

    step_scorecards: list[FunctionalTestStepScoreCard] = []
    for step, step_output in zip(test.steps, step_outputs):
        step_scorecard = await judge_functional_test_step(
            client, model, step, step_output, should_judge
        )
        step_scorecards.append(step_scorecard)

    if not should_judge:
        logger.debug("Skipping overall functional test judging (judging disabled)")
        # Return a scorecard with N/A values for the overall test
        from ..models import ErrorType, PassFailScoreCard, ScoreCard

        na_scorecard = PassFailScoreCard(
            justification="No score generated", score="N/A"
        )

        na_error_type = ScoreCard[ErrorType](
            justification="No score generated", score="N/A"
        )

        return FunctionalTestScoreCard(
            # Include the test plan and steps
            plan=test.plan,
            steps=step_scorecards,
            # Include the output data
            sampling_requests=output.sampling_requests,
            elicitation_requests=output.elicitation_requests,
            list_roots_requests=output.list_roots_requests,
            logging_requests=output.logging_requests,
            # Add the evaluation rubric with N/A scores
            meets_expectations=na_scorecard,
            error_type=na_error_type,
        )

    try:
        logger.debug(f"Judging test with {len(test.steps)} steps")
        scorecard = await prompts.judge_functional_test_output(
            client,
            model,
            test,
            output,
            step_scorecards,
        )
        logger.debug(f"Test scorecard: {scorecard}")
        return scorecard
    except Exception as e:
        logger.error(f"Failed to judge functional test: {e}", exc_info=True)
        raise
