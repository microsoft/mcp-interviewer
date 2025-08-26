"""Capabilities and feature counts report generation."""

from ...models import ServerScoreCard
from ..base import BaseReport


class CapabilitiesReport(BaseReport):
    """Report for server capabilities and feature counts."""

    @classmethod
    def cli_name(cls) -> str:
        return "capabilities"

    @classmethod
    def cli_code(cls) -> str:
        return "CAP"

    def __init__(self, scorecard: ServerScoreCard):
        """Initialize and build the capabilities report."""
        super().__init__(scorecard)
        self._build()

    def _build(self):
        """Build the capabilities section."""
        self.add_capabilities_table()

    def add_capabilities_table(self) -> "CapabilitiesReport":
        """Add capabilities summary table with counts."""
        # Never collapse this section - always show the table
        self.add_title("Server Capabilities", 2)

        capabilities = self._scorecard.initialize_result.capabilities

        self.add_table_header(["Feature", "Supported", "Count", "Additional Features"])

        # Tools capability
        if capabilities.tools:
            details = []
            if capabilities.tools.listChanged:
                details.append("listChanged")
            details_str = ", ".join(details) if details else ""
            self.add_table_row(
                ["Tools", "✅", str(len(self._scorecard.tools)), details_str]
            )
        else:
            self.add_table_row(["Tools", "❌", str(len(self._scorecard.tools)), ""])

        # Resources capability
        if capabilities.resources:
            details = []
            if capabilities.resources.subscribe:
                details.append("subscribe")
            if capabilities.resources.listChanged:
                details.append("listChanged")
            details_str = ", ".join(details) if details else ""
            self.add_table_row(
                ["Resources", "✅", str(len(self._scorecard.resources)), details_str]
            )
            self.add_table_row(
                [
                    "Resource Templates",
                    "✅",
                    str(len(self._scorecard.resource_templates)),
                    "",
                ]
            )
        else:
            self.add_table_row(
                ["Resources", "❌", str(len(self._scorecard.resources)), ""]
            )
            self.add_table_row(
                [
                    "Resource Templates",
                    "❌",
                    str(len(self._scorecard.resource_templates)),
                    "",
                ]
            )

        # Prompts capability
        if capabilities.prompts:
            details = []
            if capabilities.prompts.listChanged:
                details.append("listChanged")
            details_str = ", ".join(details) if details else ""
            self.add_table_row(
                ["Prompts", "✅", str(len(self._scorecard.prompts)), details_str]
            )
        else:
            self.add_table_row(["Prompts", "❌", str(len(self._scorecard.prompts)), ""])

        # Logging capability
        if capabilities.logging:
            self.add_table_row(["Logging", "✅", "", ""])
        else:
            self.add_table_row(["Logging", "❌", "", ""])

        # Experimental features
        if capabilities.experimental:
            for feature, additional_features in capabilities.experimental.items():
                details_str = (
                    ", ".join(additional_features.values())
                    if additional_features
                    else ""
                )
                self.add_table_row([f"{feature} (experimental)", "✅", "", details_str])

        self.add_blank_line()
        # No end_collapsible since we never start one
        return self
