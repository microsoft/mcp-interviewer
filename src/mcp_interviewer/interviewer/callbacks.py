"""MCP session callback functions."""

from typing import Any

from mcp.client.session import ClientSession
from mcp.shared.context import RequestContext
from mcp.types import (
    CreateMessageRequestParams,
    CreateMessageResult,
    ElicitRequestParams,
    ElicitResult,
    ListRootsResult,
    LoggingMessageNotificationParams,
    Root,
    TextContent,
)
from pydantic import FileUrl


def create_request_counters() -> dict[str, int]:
    """Create a new request counters dictionary."""
    return {
        "sampling": 0,
        "elicitation": 0,
        "list_roots": 0,
        "logging": 0,
    }


async def sampling_callback(
    request_counters: dict[str, int],
    context: RequestContext[ClientSession, Any],
    params: CreateMessageRequestParams,
) -> CreateMessageResult:
    """Callback for handling sampling requests from the server.

    Tracks the number of sampling requests and returns a dummy response.

    Args:
        request_counters: Dict containing request counters for tracking
        context: The request context from the MCP session
        params: Parameters for the message creation request

    Returns:
        CreateMessageResult with dummy content
    """
    request_counters["sampling"] += 1
    return CreateMessageResult(
        role="assistant",
        content=TextContent(type="text", text="Dummy content"),
        model="dummy",
    )


async def elicitation_callback(
    request_counters: dict[str, int],
    context: RequestContext[ClientSession, Any],
    params: ElicitRequestParams,
) -> ElicitResult:
    """Callback for handling elicitation requests from the server.

    Tracks the number of elicitation requests and cancels them.

    Args:
        request_counters: Dict containing request counters for tracking
        context: The request context from the MCP session
        params: Parameters for the elicitation request

    Returns:
        ElicitResult with cancel action
    """
    request_counters["elicitation"] += 1
    return ElicitResult(action="cancel")


async def list_roots_callback(
    request_counters: dict[str, int],
    context: RequestContext[ClientSession, Any],
) -> ListRootsResult:
    """Callback for handling list roots requests from the server.

    Tracks the number of list roots requests and returns a dummy root.

    Args:
        request_counters: Dict containing request counters for tracking
        context: The request context from the MCP session

    Returns:
        ListRootsResult with a dummy file root
    """
    request_counters["list_roots"] += 1
    return ListRootsResult(roots=[Root(uri=FileUrl("file://dummy.txt"))])


async def logging_callback(
    request_counters: dict[str, int],
    params: LoggingMessageNotificationParams,
) -> None:
    """Callback for handling logging notifications from the server.

    Tracks the number of logging requests received.

    Args:
        request_counters: Dict containing request counters for tracking
        params: Parameters containing the logging message
    """
    request_counters["logging"] += 1
