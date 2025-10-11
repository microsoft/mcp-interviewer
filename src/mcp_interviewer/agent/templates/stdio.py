"""Template for stdio-based FastMCP proxy servers."""

from .base import get_base_template


def get_stdio_template(original_command: str, original_args: list[str]) -> str:
    """Get the template for a stdio-based FastMCP proxy server.

    Args:
        original_command: Command to run the original server (e.g., 'npx', 'python')
        original_args: Arguments for the original server command

    Returns:
        Python code template with stdio connection and lifespan setup
    """
    # Format args as a Python list string
    args_str = "[" + ", ".join(f'"{arg}"' for arg in original_args) + "]"

    # ProxyContext fields specific to stdio
    proxy_context_fields = [
        "original_command: str",
        "original_args: list[str]",
    ]

    # Lifespan code specific to stdio
    lifespan_code = f'''# Lifespan: connect to original server once on startup
@asynccontextmanager
async def proxy_lifespan(server: FastMCP) -> AsyncIterator[ProxyContext]:
    """Manage the lifecycle of the proxy server.

    Connects to the original MCP server on startup and maintains the
    connection throughout the server's lifetime.
    """
    # Additional imports needed for stdio
    from mcp.client.stdio import StdioServerParameters, stdio_client

    # Startup: Connect to original server via stdio
    params = StdioServerParameters(command="{original_command}", args={args_str})
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            # Yield the context with the session
            yield ProxyContext(
                session=session,
                original_command="{original_command}",
                original_args={args_str},
            )
    # Shutdown: Connection automatically closed by context managers'''

    return get_base_template(lifespan_code, proxy_context_fields)
