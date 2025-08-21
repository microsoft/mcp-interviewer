from typing import Any, Generic, Literal, TypeVar

from mcp.client.stdio import StdioServerParameters
from mcp.types import (
    CallToolResult,
    InitializeResult,
    Prompt,
    Resource,
    ResourceTemplate,
    Tool,
)
from openai import AsyncOpenAI, OpenAI
from pydantic import BaseModel

Client = OpenAI | AsyncOpenAI

TScore = TypeVar("TScore")


class ScoreCard(BaseModel, Generic[TScore]):
    justification: str
    """A brief justification of the assigned score."""
    score: TScore
    """The score for this feature."""


PassFailNA = Literal["pass", "fail", "N/A"]


class PassFailScoreCard(ScoreCard[PassFailNA]): ...


class ToolNameScoreCard(BaseModel):
    length: PassFailScoreCard
    """Fail = Too short or excessively long (e.g., "q" or "retrieve_information_about_weather_forecast_and_historical_data_analysis") | Pass = Optimal length for comprehension (e.g., "getWeatherForecast")"""
    uniqueness: PassFailScoreCard
    """Fail = Generic or duplicate names (e.g., multiple tools named "search" or "get_data") | Pass = Clearly unique across the server (e.g., "fetchGoogleSearchResults" and "queryMySQLDatabase")"""
    descriptiveness: PassFailScoreCard
    """Fail = Unclear functionality from name (e.g., "process" or "handle") | Pass = Function immediately clear from name (e.g., "convertJsonToCsv")"""


class ToolDescriptionScoreCard(BaseModel):
    length: PassFailScoreCard
    """Fail = Too brief or verbose (e.g., "Gets data" or three paragraphs explaining a simple concept) | Pass = Adequate information (e.g., "Retrieves current weather data for specified location") | Comprehensive yet concise (e.g., "Retrieves current weather data for any global location using either city name or coordinates. Returns temperature, conditions, and forecasts.")"""
    parameters: PassFailScoreCard
    """Fail = Missing parameter explanations (e.g., "location: string") | Pass = Clear explanation of all parameters (e.g., "location: (string) City name (e.g., 'New York') or coordinates (e.g., '40.7,-74.0'). Required.")"""
    examples: PassFailScoreCard
    """Fail = No examples provided | Basic examples (e.g., `{"city": "London"}`) | Pass = Helpful, realistic examples (e.g., `{"location": "Tokyo"}` returns current conditions in Tokyo. `{"location": "48.8566,2.3522", "format": "daily"}` returns daily forecast for Paris.)"""


class ToolSchemaScoreCard(BaseModel):
    complexity: PassFailScoreCard
    """Fail = Overly complex, deeply nested (e.g., input requires 5+ levels of nesting) | Pass = Simple, intuitive structure (e.g., flat structure with clear property names)"""
    parameters: PassFailScoreCard
    """Fail = Too many parameters (e.g., 10+ parameters for a simple function) | Pass = Minimal necessary parameters (e.g., 1-3 core parameters)"""
    optionals: PassFailScoreCard
    """Fail = Too many optional fields (e.g., most parameters are optional with unclear defaults) | Pass = Well-balanced required vs. optional (e.g., core parameters required, enhancement parameters optional)"""
    constraints: PassFailScoreCard
    """Fail = Missing constraints (e.g., no validation info for parameters) | Pass = Clear, helpful constraints (e.g., `"date": {"type": "string", "format": "date"}`)"""


class ToolScoreCard(BaseModel):
    tool_name: ToolNameScoreCard
    tool_description: ToolDescriptionScoreCard
    tool_input_schema: ToolSchemaScoreCard
    """ScoreCard for the tool's inputSchema"""
    tool_output_schema: ToolSchemaScoreCard
    """ScoreCard for the tool's outputSchema (if it exists, otherwise set all scores to N/A)"""


class FunctionalTestStep(BaseModel):
    justification: str
    """Why this step is a good test for this tool"""
    expected_output: str
    """The expected output from the tool call"""
    tool_name: str
    """The name of the tool to call"""
    tool_arguments: dict[str, Any]
    """Realistic arguments to call the tool with"""


class FunctionalTestStepOutput(BaseModel):
    tool_output: CallToolResult | None
    exception: str | None
    sampling_requests: int = 0
    elicitation_requests: int = 0
    list_roots_requests: int = 0
    logging_requests: int = 0

    # @field_serializer("tool_output")
    # def serialize_tool_output(self, tool_output):
    #     try:
    #         return to_json(tool_output).decode()
    #     except Exception:
    #         return str(tool_output)


class FunctionalTestStepEvaluationRubric(BaseModel):
    error_handling: PassFailScoreCard
    """N/A = No error occurred | Fail = No error message or uninformative (e.g., "Error occurred") | Pass = Detailed, actionable error message (e.g., "Invalid city name 'Lond@n'. City names must contain only letters, spaces, and hyphens.")"""
    error_type: ScoreCard[
        Literal[
            "Authorization Error",
            "Connection Error",
            "Internal Server Error",
            "Bad Request",
            "N/A",
        ]
    ]
    """N/A = No error occurred | Fail = Does the output content indicate an error? For example, an 'Unauthorized' error might look like "Missing API key" and an 'Connection Error' might look like "Connection/Transport closed"."""
    no_silent_error: PassFailScoreCard
    """N/A = No error occurred | Fail = isError is false but the content of the output clearly indicates an error | Pass = isError is true"""
    output_relevance: PassFailScoreCard
    """Fail = Output unrelated to input (e.g., asking for weather but getting stock prices) | Pass = Output directly addresses input (e.g., returning exactly the weather data requested in the format specified)"""
    output_quality: PassFailScoreCard
    """Fail = Incorrect or misleading (e.g., wrong temperature units or outdated information) | Pass = Comprehensive, accurate, and helpful (e.g., complete weather data with all requested details and helpful context)"""
    schema_compliance: PassFailScoreCard
    """Fail = Output doesn't match schema (e.g., missing required fields or incorrect data types) | Pass = Output perfectly matches schema (e.g., all fields present with correct types and formats)"""
    meets_expectations: PassFailScoreCard
    """Fail = Output differs significantly from expected results (e.g., calendar tool returning appointments in wrong timezone) | Pass = Output perfectly matches expected behavior (e.g., all appointments returned with complete details in the correct timezone)"""


class FunctionalTestStepScoreCard(
    FunctionalTestStep, FunctionalTestStepOutput, FunctionalTestStepEvaluationRubric
): ...


TFunctionalTestStep = TypeVar("TFunctionalTestStep", bound=FunctionalTestStep)


class FunctionalTest(BaseModel, Generic[TFunctionalTestStep]):
    """A plan for how to perform a functional test on the MCP Server."""

    plan: str
    """2-3 sentence overview of your testing approach and strategy"""
    steps: list[TFunctionalTestStep]
    """The steps of this plan"""


class FunctionalTestOutput(BaseModel):
    sampling_requests: int = 0
    elicitation_requests: int = 0
    list_roots_requests: int = 0
    logging_requests: int = 0


class FunctionalTestEvaluationRubric(BaseModel):
    meets_expectations: PassFailScoreCard
    error_type: ScoreCard[
        Literal[
            "Authorization Error",
            "Connection Error",
            "Internal Server Error",
            "Bad Request",
            "N/A",
        ]
    ]


class FunctionalTestScoreCard(
    FunctionalTest[FunctionalTestStepScoreCard],
    FunctionalTestOutput,
    FunctionalTestEvaluationRubric,
): ...


# TODO: Add models for SSE and StreamableHTTP
ServerParameters = StdioServerParameters


class Server(BaseModel):
    parameters: ServerParameters
    initialize_result: InitializeResult
    tools: list[Tool]
    resources: list[Resource]
    resource_templates: list[ResourceTemplate]
    prompts: list[Prompt]


class ServerScoreCard(Server):
    model: str
    tool_scorecards: list[ToolScoreCard]
    functional_test_scorecard: FunctionalTestScoreCard
