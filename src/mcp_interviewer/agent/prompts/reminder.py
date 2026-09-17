"""Reminder message for when agent stops making tool calls."""


def get_reminder_message(todo_status: str) -> str:
    """Generate reminder message for the agent.

    Args:
        todo_status: Current status of the todo list

    Returns:
        Reminder message string
    """
    return f"""
Remember: You CANNOT contact the user. You must operate autonomously and independently.

IMPORTANT: You must implement ALL tools from the original server. Every tool in the original
mcp-interview report must have a corresponding @mcp.tool() in your improved server. Do not skip any tools.

**CURRENT TODO STATUS:**
{todo_status}

If you have:
1. Implemented ALL tools from the original server
2. Fixed all critical constraint violations
3. Improved tool names, descriptions, and schemas
4. Verified with mcp_interviewer testing
5. Completed ALL pending todos

Then call the 'stop' tool with a summary of your improvements.

If there is more work to do, continue using the available tools to improve the server.
"""
