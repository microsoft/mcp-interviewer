"""Base template components for FastMCP proxy servers."""


def get_base_template(lifespan_code: str, proxy_context_fields: list[str]) -> str:
    """Get the base template with lifespan code injected.

    Args:
        lifespan_code: The proxy_lifespan function implementation
        proxy_context_fields: List of field declarations for ProxyContext (without indentation)

    Returns:
        Complete server template
    """
    # Format fields with proper indentation
    formatted_fields = "\n".join(f"    {field}" for field in proxy_context_fields)

    return f'''"""Improved MCP Server - FastMCP Proxy

This server wraps the original MCP server with improved tool names,
descriptions, and schemas for better agent ergonomics.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp import ClientSession, ServerSession
from mcp.server.fastmcp import Context, FastMCP


# Define lifespan context to store the original server connection
@dataclass
class ProxyContext:
    """Context holding the persistent connection to the original MCP server."""

    session: ClientSession
{formatted_fields}


{lifespan_code}


# Create the MCP server with the lifespan
mcp = FastMCP("Improved MCP Server", lifespan=proxy_lifespan)


async def proxy_call_tool(tool_name: str, **kwargs):
    """Helper to call tools on the original server.

    Args:
        tool_name: The tool name in the original server
        **kwargs: The key-value arguments for the tool

    Returns:
        The original server's tool call result
    """
    context: Context[ServerSession, ProxyContext] = mcp.get_context()
    proxy_ctx = context.request_context.lifespan_context
    return await proxy_ctx.session.call_tool(tool_name, kwargs)


# >>> START WRITING TOOLS ON THIS LINE
# >>> END WRITING TOOLS ON THIS LINE


if __name__ == "__main__":
    mcp.run()
'''
