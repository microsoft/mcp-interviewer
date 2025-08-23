"""Resources report generation."""

import json

from ...models import ServerScoreCard
from ..base import BaseReport


class ResourcesReport(BaseReport):
    """Report for resources information."""

    def __init__(self, scorecard: ServerScoreCard):
        """Initialize and build the resources report."""
        super().__init__(scorecard)
        self._build()

    def _build(self):
        """Build the resources section."""
        self.add_title("Resources", 2)

        if not self._scorecard.resources:
            self.add_text("_No resources available_")
            self.add_blank_line()
            return

        for i, resource in enumerate(self._scorecard.resources):
            # Add anchor for linking
            self.add_text(f'<a id="resource-{i}"></a>')
            self.add_title(f"{resource.name}", 3)

            # Resource URI
            self.add_text(f"**URI:** `{resource.uri}`")
            self.add_blank_line()

            # Resource description
            if resource.description:
                self.add_text(f"**Description:** {resource.description}")
                self.add_blank_line()

            # Resource mime type
            if resource.mimeType:
                self.add_text(f"**MIME Type:** {resource.mimeType}")
                self.add_blank_line()

            # Annotations if present
            if hasattr(resource, "annotations") and resource.annotations:
                self.add_text("**Annotations:**")
                self.add_code_block(json.dumps(resource.annotations, indent=2), "json")
                self.add_blank_line()
