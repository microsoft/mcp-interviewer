"""Interviewer information report generation."""

from datetime import datetime

from ... import __version__
from ...models import ServerScoreCard
from ..base import BaseReport


class InterviewerInfoReport(BaseReport):
    """Report for MCP Interviewer information including model, server launch params, date and version."""

    def __init__(self, scorecard: ServerScoreCard):
        """Initialize and build the interviewer info report."""
        super().__init__(scorecard)
        self._build()

    def _build(self):
        """Build the interviewer info section."""
        self.add_title("Interviewer Parameters", 2)

        self.add_title("Metadata", 4)
        # Add date and version
        self.add_text(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")
        self.add_blank_line()
        self.add_text(f"**mcp-interviewer Version:** {__version__}")
        self.add_blank_line()

        # Add model info
        self.add_text(f"**Evaluation Model:** {self._scorecard.model}")
        self.add_blank_line()

        # Add server launch parameters
        self.add_launch_parameters()

    def add_launch_parameters(self) -> "InterviewerInfoReport":
        """Add launch parameters section."""
        self.add_title("Server Launch Parameters", 4)

        params = self._scorecard.parameters
        if params.connection_type == "stdio":
            self.add_text(f"**Command:** `{params.command}`")
            self.add_blank_line()
            if params.args:
                self.add_text(
                    f"**Arguments:** `{' '.join(str(arg) for arg in params.args)}`"
                )
                self.add_blank_line()
            if params.env:
                self.add_text(f"**Environment Variables:** {params.env}")
                self.add_blank_line()
        else:
            # For SSE and StreamableHttp
            self.add_text(f"**URL:** `{params.url}`")
            self.add_blank_line()
            self.add_text(f"**Connection Type:** {params.connection_type}")
            self.add_blank_line()
            if params.headers:
                self.add_text(f"**Headers:** {params.headers}")
                self.add_blank_line()
            self.add_text(f"**Timeout:** {params.timeout}s")
            self.add_blank_line()
            self.add_text(f"**SSE Read Timeout:** {params.sse_read_timeout}s")
            self.add_blank_line()

        return self
