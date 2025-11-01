"""Templates for generating FastMCP proxy servers."""

from .stdio import get_stdio_template
from .streamable_http import get_streamable_http_template


def get_server_template(server_command: str) -> str:
    """Get the appropriate template based on the server command.

    Args:
        server_command: Command or URL to run the original server

    Returns:
        Python code template with appropriate connection setup
    """
    # Check if it's a URL (HTTP-based server)
    if server_command.startswith(("http://", "https://")):
        # HTTP-based server
        # Parse headers if needed (for now, no headers)
        return get_streamable_http_template(server_command, headers=None)
    else:
        # Command-based server (stdio)
        import shlex

        command_parts = shlex.split(server_command)
        original_command = command_parts[0] if command_parts else ""
        original_args = command_parts[1:] if len(command_parts) > 1 else []
        return get_stdio_template(original_command, original_args)


__all__ = ["get_server_template", "get_stdio_template", "get_streamable_http_template"]
