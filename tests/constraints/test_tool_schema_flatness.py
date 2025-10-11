"""Tests for ToolInputSchemaFlatnessConstraint."""

import pytest
from mcp import Tool

from mcp_interviewer.constraints.tool_schema_flatness import (
    ToolInputSchemaFlatnessConstraint,
)


def test_flat_schema_passes():
    """Test that a flat schema with no nested properties passes."""
    tool = Tool(
        name="test_tool",
        description="A test tool",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "email": {"type": "string"},
            },
        },
    )

    constraint = ToolInputSchemaFlatnessConstraint()
    violations = list(constraint.test_tool(tool))
    assert len(violations) == 0


def test_nested_properties_fails():
    """Test that a schema with nested properties fails."""
    tool = Tool(
        name="test_tool",
        description="A test tool",
        inputSchema={
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                    },
                },
            },
        },
    )

    constraint = ToolInputSchemaFlatnessConstraint()
    violations = list(constraint.test_tool(tool))
    assert len(violations) == 1
    assert "nested structures" in violations[0].message


def test_array_of_flat_objects_passes():
    """Test that an array of flat objects passes."""
    tool = Tool(
        name="test_tool",
        description="A test tool",
        inputSchema={
            "type": "object",
            "properties": {
                "users": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },
            },
        },
    )

    constraint = ToolInputSchemaFlatnessConstraint()
    violations = list(constraint.test_tool(tool))
    assert len(violations) == 0


def test_array_with_nested_properties_fails():
    """Test that an array containing items with nested properties fails."""
    tool = Tool(
        name="test_tool",
        description="A test tool",
        inputSchema={
            "type": "object",
            "properties": {
                "users": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "profile": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                },
                            },
                        },
                    },
                },
            },
        },
    )

    constraint = ToolInputSchemaFlatnessConstraint()
    violations = list(constraint.test_tool(tool))
    assert len(violations) == 1


def test_ref_to_object_with_properties_fails():
    """Test that a $ref to an object with properties is detected as nested."""
    tool = Tool(
        name="test_tool",
        description="A test tool",
        inputSchema={
            "type": "object",
            "properties": {
                "user": {"$ref": "#/definitions/User"},
            },
            "definitions": {
                "User": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                    },
                },
            },
        },
    )

    constraint = ToolInputSchemaFlatnessConstraint()
    violations = list(constraint.test_tool(tool))
    assert len(violations) == 1


def test_ref_to_primitive_passes():
    """Test that a $ref to a primitive type definition passes."""
    tool = Tool(
        name="test_tool",
        description="A test tool",
        inputSchema={
            "type": "object",
            "properties": {
                "userId": {"$ref": "#/definitions/UserId"},
                "status": {"$ref": "#/definitions/Status"},
            },
            "definitions": {
                "UserId": {"type": "string", "format": "uuid"},
                "Status": {"type": "string", "enum": ["active", "inactive"]},
            },
        },
    )

    constraint = ToolInputSchemaFlatnessConstraint()
    violations = list(constraint.test_tool(tool))
    assert len(violations) == 0


def test_ref_to_nested_definition_fails():
    """Test that a $ref to a definition with nested properties fails."""
    tool = Tool(
        name="test_tool",
        description="A test tool",
        inputSchema={
            "type": "object",
            "properties": {
                "user": {"$ref": "#/definitions/User"},
            },
            "definitions": {
                "User": {
                    "type": "object",
                    "properties": {
                        "profile": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                            },
                        },
                    },
                },
            },
        },
    )

    constraint = ToolInputSchemaFlatnessConstraint()
    violations = list(constraint.test_tool(tool))
    assert len(violations) == 1


def test_defs_keyword():
    """Test that $defs keyword (JSON Schema Draft 2019-09+) is handled."""
    tool = Tool(
        name="test_tool",
        description="A test tool",
        inputSchema={
            "type": "object",
            "properties": {
                "user": {"$ref": "#/$defs/User"},
            },
            "$defs": {
                "User": {
                    "type": "object",
                    "properties": {
                        "profile": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                            },
                        },
                    },
                },
            },
        },
    )

    constraint = ToolInputSchemaFlatnessConstraint()
    violations = list(constraint.test_tool(tool))
    assert len(violations) == 1


@pytest.mark.parametrize("union_keyword", ["oneOf", "anyOf", "allOf"])
def test_union_with_flat_schemas_passes(union_keyword):
    """Test that unions (oneOf/anyOf/allOf) with flat schemas pass."""
    tool = Tool(
        name="test_tool",
        description="A test tool",
        inputSchema={
            "type": "object",
            "properties": {
                "value": {
                    union_keyword: [
                        {"type": "string"},
                        {"type": "integer"},
                    ],
                },
            },
        },
    )

    constraint = ToolInputSchemaFlatnessConstraint()
    violations = list(constraint.test_tool(tool))
    assert len(violations) == 0


@pytest.mark.parametrize("union_keyword", ["oneOf", "anyOf", "allOf"])
def test_union_with_nested_properties_fails(union_keyword):
    """Test that unions (oneOf/anyOf/allOf) containing nested properties fail."""
    tool = Tool(
        name="test_tool",
        description="A test tool",
        inputSchema={
            "type": "object",
            "properties": {
                "value": {
                    union_keyword: [
                        {
                            "type": "object",
                            "properties": {
                                "nested": {
                                    "type": "object",
                                    "properties": {
                                        "field": {"type": "string"},
                                    },
                                },
                            },
                        },
                        {"type": "string"},
                    ],
                },
            },
        },
    )

    constraint = ToolInputSchemaFlatnessConstraint()
    violations = list(constraint.test_tool(tool))
    assert len(violations) == 1


def test_circular_ref_handled_gracefully():
    """Test that circular references are handled without infinite loops."""
    tool = Tool(
        name="test_tool",
        description="A test tool",
        inputSchema={
            "type": "object",
            "properties": {
                "node": {"$ref": "#/definitions/Node"},
            },
            "definitions": {
                "Node": {
                    "type": "object",
                    "properties": {
                        "value": {"type": "string"},
                        "next": {"$ref": "#/definitions/Node"},
                    },
                },
            },
        },
    )

    constraint = ToolInputSchemaFlatnessConstraint()
    # Should not hang or error, should detect nested properties
    violations = list(constraint.test_tool(tool))
    assert len(violations) == 1


def test_empty_schema_passes():
    """Test that an empty schema passes."""
    tool = Tool(
        name="test_tool",
        description="A test tool",
        inputSchema={},
    )

    constraint = ToolInputSchemaFlatnessConstraint()
    violations = list(constraint.test_tool(tool))
    assert len(violations) == 0


def test_no_properties_field_passes():
    """Test that a schema without properties passes."""
    tool = Tool(
        name="test_tool",
        description="A test tool",
        inputSchema={
            "type": "object",
            "additionalProperties": {"type": "string"},
        },
    )

    constraint = ToolInputSchemaFlatnessConstraint()
    violations = list(constraint.test_tool(tool))
    assert len(violations) == 0


def test_nested_arrays_fails():
    """Test that nested arrays (arrays of arrays) fail."""
    tool = Tool(
        name="test_tool",
        description="A test tool",
        inputSchema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                },
            },
        },
    )

    constraint = ToolInputSchemaFlatnessConstraint()
    violations = list(constraint.test_tool(tool))
    assert len(violations) == 1
    assert "nested structures" in violations[0].message


def test_complex_schema_with_nested_properties():
    """Test a complex real-world-like schema with nested properties."""
    tool = Tool(
        name="create_user",
        description="Create a new user",
        inputSchema={
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "metadata": {
                    "type": "object",
                    "properties": {
                        "preferences": {
                            "type": "object",
                            "properties": {
                                "theme": {"type": "string"},
                            },
                        },
                    },
                },
            },
            "required": ["username"],
        },
    )

    constraint = ToolInputSchemaFlatnessConstraint()
    violations = list(constraint.test_tool(tool))
    assert len(violations) == 1
    assert "create_user" in violations[0].message
