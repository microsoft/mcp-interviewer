"""Model information report generation."""

from ...models import ServerScoreCard
from ..base import BaseReport


class ModelInfoReport(BaseReport):
    """Report for model information."""

    @classmethod
    def cli_name(cls) -> str:
        return "model-info"

    @classmethod
    def cli_code(cls) -> str:
        return "MI"

    def __init__(self, scorecard: ServerScoreCard):
        """Initialize and build the model info report."""
        super().__init__(scorecard)
        self._build()

    def _build(self):
        """Build the model info section."""
        self.add_title("Evaluation Model Information", 2)
        self.add_text(f"**Model:** {self._scorecard.model}")
        self.add_blank_line()
