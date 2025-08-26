"""Tools report generation."""

import json

from ...models import ServerScoreCard
from ..base import BaseReport


class ToolsReport(BaseReport):
    """Report for tools information."""

    @classmethod
    def cli_name(cls) -> str:
        return "tools"

    @classmethod
    def cli_code(cls) -> str:
        return "T"

    def __init__(self, scorecard: ServerScoreCard):
        """Initialize and build the tools report."""
        super().__init__(scorecard)
        self._build()

    def _build(self):
        """Build the tools section."""
        self.add_available_tools()

    def add_available_tools(self) -> "ToolsReport":
        """Add list of available tools with full details."""
        self.start_collapsible("Tools", 2)

        if not self._scorecard.tools:
            self.add_text("_No tools available_")
            self.add_blank_line()
            self.end_collapsible()
            return self

        for tool in self._scorecard.tools:
            # Add anchor for linking (outside collapsible)
            self.add_text(f'<a id="tool-{tool.name}"></a>')
            self.add_title(f"{tool.name}", 3)

            # Start collapsible for tool details
            if self._options.use_collapsible:
                self.add_text("<details>")
                self.add_text("<summary>Toggle tool details</summary>")
                self.add_blank_line()

            # Tool description
            if tool.description:
                self.add_text("**Description:**")
                self.add_code_block(tool.description)

            # Input schema
            self.add_text("**Input Schema:**")
            if tool.inputSchema:
                self.add_code_block(json.dumps(tool.inputSchema, indent=2), "json")
            else:
                self.add_text("_No Input Schema_")

            # Output schema
            self.add_text("**Output Schema:**")
            if tool.outputSchema:
                self.add_code_block(json.dumps(tool.outputSchema, indent=2), "json")
            else:
                self.add_text("_No Output Schema_")

            # End collapsible for tool details
            if self._options.use_collapsible:
                self.add_text("</details>")
                self.add_blank_line()

        self.end_collapsible()
        return self
