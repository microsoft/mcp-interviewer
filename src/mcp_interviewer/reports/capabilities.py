"""Capabilities and feature counts report generation."""

from ..models import ServerScoreCard
from .base import BaseReport


class CapabilitiesReport(BaseReport):
    """Report for server capabilities and feature counts."""

    def __init__(self, scorecard: ServerScoreCard):
        """Initialize and build the capabilities report."""
        super().__init__(scorecard)
        self._build()

    def _build(self):
        """Build the capabilities sections."""
        self.add_capabilities_table()
        self.add_feature_counts()

    def add_capabilities_table(self) -> "CapabilitiesReport":
        """Add capabilities summary table."""
        self.add_title("Capabilities (🧮)", 2)

        capabilities = self._scorecard.initialize_result.capabilities

        self.add_table_header(["Feature", "Status", "Additional Features"])

        # Tools capability
        if capabilities.tools:
            details = []
            if capabilities.tools.listChanged:
                details.append("listChanged")
            details_str = ", ".join(details) if details else ""
            self.add_table_row(["Tools", "✅", details_str])
        else:
            self.add_table_row(["Tools", "❌", ""])

        # Resources capability
        if capabilities.resources:
            details = []
            if capabilities.resources.subscribe:
                details.append("subscribe")
            if capabilities.resources.listChanged:
                details.append("listChanged")
            details_str = ", ".join(details) if details else ""
            self.add_table_row(["Resources", "✅", details_str])
        else:
            self.add_table_row(["Resources", "❌", ""])

        # Prompts capability
        if capabilities.prompts:
            details = []
            if capabilities.prompts.listChanged:
                details.append("listChanged")
            details_str = ", ".join(details) if details else ""
            self.add_table_row(["Prompts", "✅", details_str])
        else:
            self.add_table_row(["Prompts", "❌", ""])

        # Logging capability
        if capabilities.logging:
            self.add_table_row(["Logging", "✅", ""])
        else:
            self.add_table_row(["Logging", "❌", ""])

        # Experimental features
        if capabilities.experimental:
            for feature, additional_features in capabilities.experimental.items():
                details_str = (
                    ", ".join(additional_features.values())
                    if additional_features
                    else ""
                )
                self.add_table_row([f"{feature} (experimental)", "✅", details_str])

        self.add_blank_line()
        return self

    def add_feature_counts(self) -> "CapabilitiesReport":
        """Add feature counts section."""
        self.add_title("Feature Counts (🧮)", 2)

        self.add_table_header(["Feature", "Count"])
        self.add_table_row(["Tools", str(len(self._scorecard.tools))])
        self.add_table_row(["Resources", str(len(self._scorecard.resources))])
        self.add_table_row(
            ["Resource Templates", str(len(self._scorecard.resource_templates))]
        )
        self.add_table_row(["Prompts", str(len(self._scorecard.prompts))])

        self.add_blank_line()
        return self
