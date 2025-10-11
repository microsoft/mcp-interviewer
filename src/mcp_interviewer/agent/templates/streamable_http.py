"""Template for HTTP-based FastMCP proxy servers."""

from .base import get_base_template


def get_streamable_http_template(
    url: str, headers: dict[str, str] | None = None
) -> str:
    """Get the template for an HTTP-based FastMCP proxy server.

    Args:
        url: URL of the original MCP server
        headers: Optional HTTP headers for the connection

    Returns:
        Python code template with streamable HTTP connection and lifespan setup
    """
    # Format headers as a Python dict string
    if headers:
        headers_str = (
            "{\n        "
            + ",\n        ".join(f'"{k}": "{v}"' for k, v in headers.items())
            + "\n    }"
        )
    else:
        headers_str = "None"

    # ProxyContext fields specific to HTTP
    proxy_context_fields = [
        "original_url: str",
    ]

    # Lifespan code specific to HTTP
    lifespan_code = f'''# Lifespan: connect to original server once on startup
@asynccontextmanager
async def proxy_lifespan(server: FastMCP) -> AsyncIterator[ProxyContext]:
    """Manage the lifecycle of the proxy server.

    Connects to the original MCP server on startup and maintains the
    connection throughout the server's lifetime.
    """
    # Additional imports needed for HTTP
    from mcp.client.streamable_http import streamablehttp_client

    # Startup: Connect to original server via HTTP
    async with streamablehttp_client(
        "{url}",
        headers={headers_str},
        timeout=5,
        sse_read_timeout=300,
    ) as (read, write, _):
        async with ClientSession(read, write) as session:
            # Yield the context with the session
            yield ProxyContext(
                session=session,
                original_url="{url}",
            )
    # Shutdown: Connection automatically closed by context managers'''

    return get_base_template(lifespan_code, proxy_context_fields)
