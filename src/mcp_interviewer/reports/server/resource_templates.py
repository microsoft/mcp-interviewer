"""Resource templates report generation."""

import json

from ...models import ServerScoreCard
from ..base import BaseReport


class ResourceTemplatesReport(BaseReport):
    """Report for resource templates information."""

    @classmethod
    def cli_name(cls) -> str:
        return "resource-templates"

    @classmethod
    def cli_code(cls) -> str:
        return "RT"

    def __init__(self, scorecard: ServerScoreCard):
        """Initialize and build the resource templates report."""
        super().__init__(scorecard)
        self._build()

    def _build(self):
        """Build the resource templates section."""
        self.add_title("Resource Templates", 2)
        self.start_collapsible("Toggle details")

        if not self._scorecard.resource_templates:
            self.add_text("_No resource templates available_")
            self.add_blank_line()
            self.end_collapsible()
            return

        for template in self._scorecard.resource_templates:
            # Add anchor for linking (outside collapsible)
            self.add_text(f'<a id="resource-template-{template.name}"></a>')
            self.add_title(f"{template.name}", 3)

            # Start collapsible for template details
            if self._options.use_collapsible:
                self.add_text("<details>")
                self.add_text("<summary>Toggle template details</summary>")
                self.add_blank_line()

            # Template URI pattern
            self.add_text(f"**URI Template:** `{template.uriTemplate}`")
            self.add_blank_line()

            # Template description
            if template.description:
                self.add_text(f"**Description:** {template.description}")
                self.add_blank_line()

            # MIME type
            if template.mimeType:
                self.add_text(f"**MIME Type:** {template.mimeType}")
                self.add_blank_line()

            # Annotations if present
            if hasattr(template, "annotations") and template.annotations:
                self.add_text("**Annotations:**")
                self.add_code_block(json.dumps(template.annotations, indent=2), "json")
                self.add_blank_line()

            # End collapsible for template details
            if self._options.use_collapsible:
                self.add_text("</details>")
                self.add_blank_line()

        self.end_collapsible()
