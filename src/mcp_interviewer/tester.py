"""Tool testing and analysis functionality."""

import asyncio
import json
from typing import Any

from autogen_core.models import ChatCompletionClient, LLMMessage, UserMessage
from autogen_core.tools import ToolSchema
from autogen_ext.tools.mcp import McpWorkbench
from loguru import logger

from .prompts import generate_mock_args_prompt, generate_tool_analysis_prompt
from .types import ToolAnalysis


def _generate_fallback_mock_args(tool: ToolSchema) -> dict[str, Any]:
    """Generate fallback mock arguments based on a JSON schema."""
    mock_args = {}
    parameters = tool.get("parameters", {})
    properties = parameters.get("properties", {})
    required = parameters.get("required", [])

    for prop_name, prop_def in properties.items():
        prop_type = prop_def.get("type", "string")

        # Generate appropriate mock values based on type
        if prop_type == "string":
            mock_args[prop_name] = "test_string"
        elif prop_type == "number":
            mock_args[prop_name] = 42
        elif prop_type == "integer":
            mock_args[prop_name] = 42
        elif prop_type == "boolean":
            mock_args[prop_name] = True
        elif prop_type == "array":
            # Create a simple array with one mock item
            items_schema = prop_def.get("items", {})
            if items_schema.get("type") == "string":
                mock_args[prop_name] = ["test_item"]
            elif items_schema.get("type") == "number":
                mock_args[prop_name] = [1]
            else:
                mock_args[prop_name] = ["test_item"]
        elif prop_type == "object":
            # Recursively generate mock object
            mock_args[prop_name] = _generate_fallback_mock_args(prop_def)
        else:
            # Default fallback
            mock_args[prop_name] = "test_value"

    # Only include required properties to test minimal valid input
    if required:
        return {k: v for k, v in mock_args.items() if k in required}

    return mock_args


class ToolTester:
    """Tests MCP tools to determine if they work correctly."""

    def __init__(self, model_client: ChatCompletionClient, llm_timeout: float = 30.0):
        self.model_client = model_client
        self.llm_timeout = llm_timeout

    async def _generate_mock_args_with_llm(
        self, tool: ToolSchema, messages: list[LLMMessage] | None = None
    ) -> dict[str, Any]:
        """Use LLM to generate realistic mock arguments for a tool."""
        # Create a prompt for the LLM to understand the tool's purpose
        prompt = generate_mock_args_prompt(
            tool_name=tool["name"],
            tool_description=tool.get("description", ""),
            tool_schema=json.dumps(tool.get("parameters", {}), indent=2),
        )
        try:
            if not messages:
                messages = []

            messages.append(UserMessage(source="user", content=prompt))

            response = await asyncio.wait_for(
                self.model_client.create(
                    messages=messages,
                    tools=[tool],
                    extra_create_args={"tool_choice": "required"},
                ),
                timeout=self.llm_timeout,
            )

            if isinstance(response.content, list):
                for function_call in response.content:
                    return json.loads(function_call.arguments)
        except TimeoutError:
            logger.warning(
                f"LLM timeout generating mock args for tool '{tool['name']}', "
                "falling back to static generation"
            )
        except Exception:
            logger.exception(
                "Failed to generate mock args from LLM, fallback to static generation."
            )

        # Fallback to schema-based generation
        return _generate_fallback_mock_args(tool)

    async def _generate_llm_analysis(
        self,
        tool: ToolSchema,
        mock_args: dict[str, Any],
        test_results: dict[str, Any],
        errors: list[str],
    ) -> str:
        """Use LLM to generate a comprehensive analysis of the tool test results."""
        prompt = generate_tool_analysis_prompt(
            tool_name=tool["name"],
            tool_description=tool.get("description", "No description provided"),
            tool_schema=json.dumps(tool.get("parameters", {}), indent=2),
            mock_args=json.dumps(mock_args, indent=2),
            test_results=json.dumps(test_results, indent=2),
            errors=errors,
        )

        try:
            messages = [UserMessage(source="user", content=prompt)]
            response = await asyncio.wait_for(
                self.model_client.create(messages=messages),
                timeout=self.llm_timeout,
            )

            if hasattr(response, "content") and response.content:
                if isinstance(response.content, str):
                    return response.content.strip()
                elif isinstance(response.content, list) and len(response.content) > 0:
                    # Handle case where content is a list
                    return str(response.content[0]).strip()

            return "LLM analysis not available"

        except TimeoutError:
            logger.warning(f"LLM timeout generating analysis for tool '{tool['name']}'")
            return "Analysis generation timed out"
        except Exception as e:
            logger.error(f"Failed to generate LLM analysis: {e}")
            return f"Analysis generation failed: {str(e)}"

    async def test_tool(self, workbench: McpWorkbench, tool: ToolSchema) -> ToolAnalysis:
        """Test a single tool and return analysis."""
        try:
            # Basic validation tests
            score = 0.0
            errors = []
            test_results = {}
            mock_args = {}

            # Test 1: Tool definition completeness
            if tool.get("description", None):
                score += 0.3
                test_results["has_description"] = True
            else:
                errors.append("Missing description")
                test_results["has_description"] = False

            # Test 2: Parameter validation
            if tool.get("parameters", None):
                score += 0.2
                test_results["has_schema"] = True
            else:
                errors.append("Missing or incomplete input schema")
                test_results["has_schema"] = False

            # Test 3: Try to call the tool with LLM-generated or schema-based mock arguments
            try:
                # Try to use LLM to generate mock arguments, fall back to schema-based generation
                mock_args = await self._generate_mock_args_with_llm(tool)
                test_results["mock_args_generated"] = True

                logger.debug(f"Testing tool {tool['name']} with mock args: {mock_args}")
                # Add timeout to tool call to prevent hanging
                tool_result = await asyncio.wait_for(
                    workbench.call_tool(tool["name"], mock_args),
                    timeout=15.0,  # 15 second timeout for individual tool calls
                )
                score += 0.5
                test_results["tool_call_success"] = True
                test_results["tool_result"] = str(tool_result)[:200]  # Truncate for brevity
            except TimeoutError:
                logger.debug(f"Tool call timed out for {tool['name']}")
                score += 0.1  # Tool exists but times out
                test_results["tool_call_success"] = False
                test_results["error_type"] = "timeout"
            except Exception as e:
                # Tool call failed, but we can still provide analysis
                logger.debug(f"Tool call failed with generated args: {e}")
                test_results["tool_call_success"] = False
                test_results["error_message"] = str(e)

                # Check if it's a validation error vs other error
                if "required" in str(e).lower() or "missing" in str(e).lower():
                    score += 0.2  # Schema validation issue
                    test_results["error_type"] = "validation"
                else:
                    score += 0.3  # Tool exists but may have runtime issues
                    test_results["error_type"] = "runtime"

            # Generate LLM-based analysis
            analysis = await self._generate_llm_analysis(tool, mock_args, test_results, errors)

            return ToolAnalysis(
                name=tool["name"],
                score=min(score, 1.0),
                analysis=analysis,
                errors=errors,
            )

        except Exception as e:
            logger.error(f"Error testing tool {tool['name']}: {e}")
            return ToolAnalysis(
                name=tool["name"],
                score=0.0,
                analysis=f"Failed to test tool: {str(e)}",
                errors=[str(e)],
            )
