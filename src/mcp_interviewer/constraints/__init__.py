"""Constraints package for MCP server validation.

This package provides a framework for defining and enforcing constraints
on MCP (Model Context Protocol) servers to ensure compatibility with
various AI providers and best practices.
"""

from .base import CompositeConstraint
from .openai import OpenAIConstraints


class AllConstraints(CompositeConstraint):
    """Aggregates all available constraints for comprehensive validation.

    This class combines all provider-specific and general constraints
    to provide a complete validation suite for MCP servers.
    """

    def __init__(self):
        """Initialize with all available constraint sets."""
        super().__init__(
            OpenAIConstraints(),
        )
