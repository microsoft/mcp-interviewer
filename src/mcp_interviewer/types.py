"""Data models for MCP interviewer results."""

from typing import Any

from pydantic import BaseModel


class ToolAnalysis(BaseModel):
    """Analysis results for a single MCP tool."""

    name: str
    score: float  # 0.0 to 1.0
    analysis: str  # Natural language analysis
    rewritten: dict[str, Any] | None = None  # Suggested rewritten tool definition
    errors: list[str] | None = None  # Any errors encountered during testing
    test_results: dict[str, Any] | None = None  # Detailed test results

    def model_post_init(self, __context: Any) -> None:
        if self.errors is None:
            self.errors = []


class ServerAnalysis(BaseModel):
    """Analysis results for an entire MCP server.

    The metadata field may contain:
    - initialize_result: The MCP initialization result from the server
    - Other server-specific metadata collected during analysis
    """

    name: str
    score: float  # Overall score 0.0 to 1.0
    analysis: str  # Natural language analysis of the server overall
    tools: list[ToolAnalysis]  # Analysis for each tool
    metadata: dict[str, Any] | None = None  # Additional server metadata including initialize_result

    @property
    def tool_count(self) -> int:
        """Number of tools analyzed."""
        return len(self.tools)

    @property
    def average_tool_score(self) -> float:
        """Average score across all tools."""
        if not self.tools:
            return 0.0
        return sum(tool.score for tool in self.tools) / len(self.tools)

    @property
    def initialize_result(self) -> Any | None:
        """Get the MCP initialize result from metadata if available."""
        if self.metadata:
            return self.metadata.get("initialize_result")
        return None


class InterviewResults(BaseModel):
    """Complete results from an MCP interview session.

    Note: For best results, create McpWorkbenches with a model_client parameter
    to enable server sampling capabilities in the patched autogen_ext.tools.mcp.
    """

    score: float  # Overall score across all servers
    analysis: str  # High-level analysis
    servers: list[ServerAnalysis]  # Per-server analysis
    total_tools: int = 0
    successful_tools: int = 0

    def model_post_init(self, __context: Any) -> None:
        # Calculate totals
        self.total_tools = sum(server.tool_count for server in self.servers)
        self.successful_tools = sum(
            len([tool for tool in server.tools if tool.score > 0.5]) for server in self.servers
        )

    @property
    def success_rate(self) -> float:
        """Percentage of tools that scored above 0.5."""
        if self.total_tools == 0:
            return 0.0
        return self.successful_tools / self.total_tools
