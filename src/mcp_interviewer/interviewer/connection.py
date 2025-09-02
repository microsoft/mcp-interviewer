"""MCP client connection management."""

from contextlib import asynccontextmanager

from mcp import stdio_client
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client

from ..models import ServerParameters


@asynccontextmanager
async def mcp_client(params: ServerParameters):
    """Create an MCP client based on the server connection type.

    Args:
        params: ServerParameters specifying the connection type and configuration

    Yields:
        Tuple of (read_stream, write_stream) for the MCP client connection
    """
    if params.connection_type == "stdio":
        async with stdio_client(params) as (read, write):
            yield read, write
    elif params.connection_type == "sse":
        async with sse_client(
            params.url,
            headers=params.headers,
            timeout=params.timeout,
            sse_read_timeout=params.sse_read_timeout,
        ) as (read, write):
            yield read, write
    elif params.connection_type == "streamable_http":
        async with streamablehttp_client(
            params.url,
            headers=params.headers,
            timeout=params.timeout,
            sse_read_timeout=params.sse_read_timeout,
        ) as (read, write, _):
            yield read, write
    else:
        raise ValueError(f"Unknown connection type: {params.connection_type}")
