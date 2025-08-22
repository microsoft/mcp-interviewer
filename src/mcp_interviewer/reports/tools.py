"""Tools report generation."""

import json

from ..models import ServerScoreCard
from .base import BaseReport


class ToolsReport(BaseReport):
    """Report for tools information."""

    def __init__(self, scorecard: ServerScoreCard):
        """Initialize and build the tools report."""
        super().__init__(scorecard)
        self._build()

    def _build(self):
        """Build the tools section."""
        self.add_available_tools()

    def add_available_tools(self) -> "ToolsReport":
        """Add list of available tools with full details."""
        self.add_title("Available Tools (🧮)", 2)

        if not self._scorecard.tools:
            self.add_text("_No tools available_")
            self.add_blank_line()
            return self

        for i, tool in enumerate(self._scorecard.tools):
            # Add anchor for linking
            self.add_text(f'<a id="tool-{i}"></a>')
            self.add_title(f"{tool.name}", 3)

            # Link to scorecard
            self.add_text(f"[→ View evaluation scorecard](#tool-scorecard-{i})")
            self.add_blank_line()

            # Tool description
            if tool.description:
                self.add_text(f"**Description:** {tool.description}")
                self.add_blank_line()

            # Input schema
            if tool.inputSchema:
                self.add_text("**Input Schema:**")
                self.add_code_block(json.dumps(tool.inputSchema, indent=2), "json")

            # Output schema
            if tool.outputSchema:
                self.add_text("**Output Schema:**")
                self.add_code_block(json.dumps(tool.outputSchema, indent=2), "json")

        return self
