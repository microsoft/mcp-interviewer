"""Server information report generation."""

from ..models import ServerScoreCard
from .base import BaseReport
from .utils import get_server_info


class ServerInfoReport(BaseReport):
    """Report for server information and metadata."""

    def __init__(self, scorecard: ServerScoreCard):
        """Initialize and build the server info report."""
        super().__init__(scorecard)
        self._build()

    def _build(self):
        """Build the server info section."""
        self.add_server_info()
        self.add_launch_parameters()

    def add_server_info(self) -> "ServerInfoReport":
        """Add server information section."""
        info = get_server_info(self._scorecard)

        self.add_title("Server Information (🧮)", 2)

        if info["name"]:
            self.add_text(f"**Name:** {info['name']}")
            self.add_blank_line()
        if info["version"]:
            self.add_text(f"**Version:** {info['version']}")
            self.add_blank_line()
        self.add_text(f"**Protocol Version:** {info['protocol_version']}")
        self.add_blank_line()

        if info["instructions"]:
            self.add_text("**Instructions:**")
            self.add_blank_line()
            self.add_text(f"> {info['instructions']}")
            self.add_blank_line()

        return self

    def add_launch_parameters(self) -> "ServerInfoReport":
        """Add launch parameters section."""
        self.add_title("Launch Parameters (🧮)", 2)

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
