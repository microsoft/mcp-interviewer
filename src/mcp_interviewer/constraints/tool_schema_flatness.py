from collections.abc import Generator
from typing import Any

from mcp import Tool
from pydantic import HttpUrl
from referencing import Registry
from referencing.jsonschema import DRAFT202012

from mcp_interviewer.constraints.base import ConstraintViolation, Severity

from .base import SourceUrl, ToolConstraint


class ToolInputSchemaFlatnessConstraint(ToolConstraint):
    """Validates that tool input schemas are flat (no nested objects or arrays).

    Nested structures in tool schemas can make them difficult to understand and use.
    This constraint ensures that the inputSchema doesn't contain:
    - Nested "properties" fields (objects within objects)
    - Nested arrays (arrays of arrays)

    A flat schema has all parameters at the top level. Arrays of primitives and
    unions (oneOf/anyOf/allOf) are allowed.
    """

    @classmethod
    def cli_name(cls) -> str:
        """Return the CLI-friendly name for this constraint."""
        return "tool-schema-flatness"

    @classmethod
    def cli_code(cls) -> str:
        """Return the shorthand code for this constraint."""
        return "TSF"

    @classmethod
    def sources(cls) -> list[SourceUrl]:
        return [HttpUrl("https://composio.dev/blog/gpt-4-function-calling-example")]

    def test_tool(self, tool: Tool) -> Generator[ConstraintViolation, None, None]:
        """Test if the tool's inputSchema has nested properties fields.

        Args:
            tool: The tool to validate

        Yields:
            ConstraintViolation: Warning if inputSchema contains nested "properties" fields
        """
        # Create a registry for handling $ref references using the new referencing library
        # Explicitly use DRAFT202012 specification
        resource = DRAFT202012.create_resource(tool.inputSchema)
        registry = Registry().with_resource(uri="", resource=resource)

        def has_nested_structure(
            obj: Any,
            registry: Any,
            depth: int = 0,
            inside_array: bool = False,
            visited: set[str] | None = None,
        ) -> bool:
            """Check if an object contains nested "properties" fields or nested arrays.

            Args:
                obj: The object to check
                resolver: JSON Schema reference resolver
                depth: Current depth (0 = top level properties)
                inside_array: Whether we're currently inside an array's items
                visited: Set of visited $ref URLs to prevent infinite loops

            Returns:
                True if nested structures found, False otherwise
            """
            if not isinstance(obj, dict):
                return False

            if visited is None:
                visited = set()

            # If we're already inside a property definition and we find another "properties" field
            if depth > 0 and "properties" in obj:
                return True

            # If we're inside an array and we find another array type
            if inside_array and obj.get("type") == "array":
                return True

            # Check $ref
            if "$ref" in obj:
                ref_url = obj["$ref"]
                # Prevent infinite loops from circular references
                if ref_url in visited:
                    return False
                visited.add(ref_url)

                try:
                    # Use the new referencing API
                    resolver = registry.resolver()
                    resolved = resolver.lookup(ref_url).contents
                    if isinstance(resolved, dict) and has_nested_structure(
                        resolved, registry, depth, inside_array, visited
                    ):
                        return True
                except Exception:
                    # If resolution fails, skip this ref
                    pass

            # Recursively check all values in the current object
            for key, value in obj.items():
                if key == "properties" and depth == 0:
                    # This is the top-level properties, check its children at depth 1
                    if isinstance(value, dict):
                        for prop_value in value.values():
                            if has_nested_structure(
                                prop_value, registry, depth + 1, inside_array, visited
                            ):
                                return True
                elif key == "items":
                    # Check array items - set inside_array=True
                    if isinstance(value, dict):
                        if has_nested_structure(value, registry, depth, True, visited):
                            return True
                elif isinstance(value, dict):
                    # Check nested structures (like oneOf, anyOf, allOf, etc.)
                    if has_nested_structure(
                        value, registry, depth, inside_array, visited
                    ):
                        return True
                elif isinstance(value, list):
                    # Check each item in arrays (like oneOf, anyOf, allOf)
                    for item in value:
                        if isinstance(item, dict) and has_nested_structure(
                            item, registry, depth, inside_array, visited
                        ):
                            return True

            return False

        if has_nested_structure(tool.inputSchema, registry):
            yield ConstraintViolation(
                self,
                f"Tool '{tool.name}': inputSchema contains nested structures (nested objects or arrays). Tool parameters should be flat.",
                severity=Severity.WARNING,
            )
