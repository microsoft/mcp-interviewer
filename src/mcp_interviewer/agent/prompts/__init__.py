"""Prompts and instructions for the MCP Interviewer Agent."""

from .prompt import get_task_prompt
from .reminder import get_reminder_message

__all__ = ["get_task_prompt", "get_reminder_message"]
