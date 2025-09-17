import logging
from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import cast

import tiktoken
from mcp.types import Tool
from openai.types.chat import ChatCompletionTool
from openai.types.shared import FunctionDefinition

from .base import CompositeStatistic, ServerScoreCard, Statistic, StatisticValue

logger = logging.getLogger(__name__)


def num_tokens_for_tool(tool: ChatCompletionTool, model):
    """From https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb"""

    # Initialize function settings to 0
    func_init = 0
    prop_init = 0
    prop_key = 0
    enum_init = 0
    enum_item = 0
    func_end = 0

    if model in ["gpt-3.5-turbo", "gpt-4"]:
        # Set function settings for the above models
        func_init = 10
        prop_init = 3
        prop_key = 3
        enum_init = -3
        enum_item = 3
        func_end = 12
    else:
        if model not in ["gpt-4o", "gpt-4o-mini"]:
            logger.warning(
                f"""Unrecognized model {model}, defaulting to gpt-4o tokenizer settings."""
            )

        # Set function settings for the above models
        func_init = 7
        prop_init = 3
        prop_key = 3
        enum_init = -3
        enum_item = 3
        func_end = 12

    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        logger.warning(f"model {model} not found. Using o200k_base encoding.")
        encoding = tiktoken.get_encoding("o200k_base")

    func_token_count = 0
    func_token_count += func_init  # Add tokens for start of each function
    function = tool.function
    f_name = function.name
    f_desc = function.description or ""
    if f_desc.endswith("."):
        f_desc = f_desc[:-1]
    line = f_name + ":" + f_desc
    func_token_count += len(
        encoding.encode(line)
    )  # Add tokens for set name and description

    properties = {}
    if function.parameters is not None and "properties" in function.parameters:
        properties = cast(dict, function.parameters["properties"])

    if len(properties) > 0:
        func_token_count += prop_init  # Add tokens for start of each property
        for key in list(properties.keys()):
            func_token_count += prop_key  # Add tokens for each set property
            p_name = key
            p_type = properties[key].get("type", "")
            p_desc = properties[key].get("description", "")

            if "enum" in properties[key].keys():
                func_token_count += enum_init  # Add tokens if property has enum list
                for item in properties[key]["enum"]:
                    func_token_count += enum_item
                    func_token_count += len(encoding.encode(item))
            if p_desc.endswith("."):
                p_desc = p_desc[:-1]
            line = f"{p_name}:{p_type}:{p_desc}"
            func_token_count += len(encoding.encode(line))
    func_token_count += func_end

    return func_token_count


class ToolStatistic(Statistic, ABC):
    @abstractmethod
    def compute_tool(self, tool: Tool) -> Generator[StatisticValue, None, None]: ...

    def compute(self, server: ServerScoreCard) -> Generator[StatisticValue, None, None]:
        for tool in server.tools:
            yield from self.compute_tool(tool)


class ToolInputSchemaTokenCount(ToolStatistic):
    def compute_tool(self, tool: Tool) -> Generator[StatisticValue, None, None]:
        oai_tool = ChatCompletionTool(
            type="function",
            function=FunctionDefinition(
                name=tool.name,
                description=tool.description,
                parameters=tool.inputSchema,
            ),
        )
        token_count = num_tokens_for_tool(oai_tool, "gpt-4o")
        yield StatisticValue(self, token_count)


class ToolInputSchemaTotalParametersCount(ToolStatistic):
    def compute_tool(self, tool: Tool) -> Generator[StatisticValue, None, None]:
        yield StatisticValue(self, len(tool.inputSchema.get("properties", {})))


class ToolInputSchemaRequiredParametersCount(ToolStatistic):
    def compute_tool(self, tool: Tool) -> Generator[StatisticValue, None, None]:
        yield StatisticValue(self, len(tool.inputSchema.get("required", [])))


class ToolInputSchemaOptionalParametersCount(ToolStatistic):
    def compute_tool(self, tool: Tool) -> Generator[StatisticValue, None, None]:
        yield StatisticValue(
            self,
            len(tool.inputSchema.get("properties", {}))
            - len(tool.inputSchema.get("required", [])),
        )


class ToolInputSchemaMaxDepthCount(ToolStatistic):
    def compute_tool(self, tool: Tool) -> Generator[StatisticValue, None, None]:
        def get_max_depth(o, depth=0):
            max_depth = depth
            if isinstance(o, list | tuple):
                for item in o:
                    max_depth = max(get_max_depth(item, depth + 1), max_depth)
            elif isinstance(o, dict):
                for value in o.values():
                    max_depth = max(get_max_depth(value, depth + 1), max_depth)
            return max_depth

        yield StatisticValue(
            self, get_max_depth(tool.inputSchema.get("properties", {}))
        )


class AllToolStatistics(CompositeStatistic):
    def __init__(self) -> None:
        super().__init__(
            ToolInputSchemaTokenCount(),
        )
