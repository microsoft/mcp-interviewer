"""Stop tool for agent to signal completion."""

from openai.types.responses import FunctionToolParam


class StopTool:
    """Tool that allows the agent to signal it has completed its work."""

    @staticmethod
    def get_tool_definition() -> FunctionToolParam:
        """Get the stop tool definition for the LLM."""
        return {
            "type": "function",
            "name": "stop",
            "description": "Call this when you have successfully completed the task and the improved server.py passes all tests. Include a summary of what was accomplished.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "A brief summary of the improvements made",
                    },
                    "final_report": {
                        "type": "string",
                        "description": "Key metrics and improvements (constraint violations fixed, tool quality improvements, etc.)",
                    },
                },
                "required": ["summary", "final_report"],
            },
            "strict": None,
        }

    @staticmethod
    def execute(summary: str, final_report: str) -> str:
        """Execute the stop tool.

        Args:
            summary: Summary of improvements
            final_report: Final report details

        Returns:
            Confirmation message
        """
        return f"Agent stopping. Summary: {summary}\n\nFinal Report:\n{final_report}"
