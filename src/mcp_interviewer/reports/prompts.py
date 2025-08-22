"""Prompts report generation."""

from ..models import ServerScoreCard
from .base import BaseReport


class PromptsReport(BaseReport):
    """Report for prompts information."""

    def __init__(self, scorecard: ServerScoreCard):
        """Initialize and build the prompts report."""
        super().__init__(scorecard)
        self._build()

    def _build(self):
        """Build the prompts section."""
        self.add_title("Available Prompts (🧮)", 2)

        if not self._scorecard.prompts:
            self.add_text("_No prompts available_")
            self.add_blank_line()
            return

        for i, prompt in enumerate(self._scorecard.prompts):
            # Add anchor for linking
            self.add_text(f'<a id="prompt-{i}"></a>')
            self.add_title(f"{prompt.name}", 3)

            # Prompt description
            if prompt.description:
                self.add_text(f"**Description:** {prompt.description}")
                self.add_blank_line()

            # Arguments if present
            if prompt.arguments:
                self.add_text("**Arguments:**")
                for arg in prompt.arguments:
                    self.add_text(
                        f"- **{arg.name}**: {arg.description if arg.description else 'No description'}"
                    )
                    if arg.required:
                        self.add_text("  - Required: ✅")
                    else:
                        self.add_text("  - Required: ❌")
                self.add_blank_line()
