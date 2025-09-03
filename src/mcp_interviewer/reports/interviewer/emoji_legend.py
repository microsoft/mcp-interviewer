"""Emoji legend report generation."""

from ...models import ServerScoreCard
from ..base import BaseReport


class EmojiLegendReport(BaseReport):
    """Report for emoji legend."""

    @classmethod
    def cli_name(cls) -> str:
        return "emoji-legend"

    @classmethod
    def cli_code(cls) -> str:
        return "EMOJI"

    def __init__(self, scorecard: ServerScoreCard):
        """Initialize and build the emoji legend report."""
        super().__init__(scorecard)
        self._build()

    def _build(self):
        """Build the emoji legend section."""
        self.add_title("Legend", 2)
        # self.add_text("- ✅: Feature meets requirements")
        # self.add_text("- ❌: Feature does not meet requirements")
        self.add_text("- ⚪: Feature not applicable or not tested")
        self.add_text("- 🤖: AI-generated content")
        # self.add_text("- 🧮: Computed metrics and data")
        self.add_blank_line()
