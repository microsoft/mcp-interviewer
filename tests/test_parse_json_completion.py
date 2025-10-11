"""Unit tests for parse_json_completion utility."""

import json

import pytest

from mcp_interviewer.prompts.utils import parse_json_completion


def test_parse_json_object_plain():
    """Test parsing a plain JSON object."""
    completion = '{"name": "test", "value": 42}'
    result = parse_json_completion(completion)
    assert result == {"name": "test", "value": 42}


def test_parse_json_object_with_prefix():
    """Test parsing JSON object with text prefix."""
    completion = 'Here is the result: {"name": "test", "value": 42}'
    result = parse_json_completion(completion)
    assert result == {"name": "test", "value": 42}


def test_parse_json_object_with_suffix():
    """Test parsing JSON object with text suffix."""
    completion = '{"name": "test", "value": 42} and that is the answer.'
    result = parse_json_completion(completion)
    assert result == {"name": "test", "value": 42}


def test_parse_json_object_with_prefix_and_suffix():
    """Test parsing JSON object wrapped in text."""
    completion = 'The result is: {"name": "test", "value": 42} as requested.'
    result = parse_json_completion(completion)
    assert result == {"name": "test", "value": 42}


def test_parse_json_array_plain():
    """Test parsing a plain JSON array."""
    completion = '[1, 2, 3, 4, 5]'
    result = parse_json_completion(completion)
    assert result == [1, 2, 3, 4, 5]


def test_parse_json_array_with_text():
    """Test parsing JSON array wrapped in text."""
    completion = 'Here are the numbers: [1, 2, 3, 4, 5] in order.'
    result = parse_json_completion(completion)
    assert result == [1, 2, 3, 4, 5]


def test_parse_json_with_markdown_code_block():
    """Test parsing JSON inside markdown code block."""
    completion = '''```json
{"name": "test", "value": 42}
```'''
    result = parse_json_completion(completion)
    assert result == {"name": "test", "value": 42}


def test_parse_json_with_nested_objects():
    """Test parsing JSON with nested objects."""
    completion = '''{"outer": {"inner": {"value": 123}}, "list": [1, 2, 3]}'''
    result = parse_json_completion(completion)
    assert result == {"outer": {"inner": {"value": 123}}, "list": [1, 2, 3]}


def test_parse_json_with_arrays_in_objects():
    """Test parsing JSON object containing arrays."""
    completion = '{"items": [{"id": 1}, {"id": 2}], "total": 2}'
    result = parse_json_completion(completion)
    assert result == {"items": [{"id": 1}, {"id": 2}], "total": 2}


def test_parse_json_empty_object():
    """Test parsing empty JSON object."""
    completion = '{}'
    result = parse_json_completion(completion)
    assert result == {}


def test_parse_json_empty_array():
    """Test parsing empty JSON array."""
    completion = '[]'
    result = parse_json_completion(completion)
    assert result == []


def test_parse_json_with_strings_containing_braces():
    """Test parsing JSON with strings that contain braces."""
    completion = '{"message": "This {has} [braces] in it", "value": 1}'
    result = parse_json_completion(completion)
    assert result == {"message": "This {has} [braces] in it", "value": 1}


def test_parse_json_multiline():
    """Test parsing multiline JSON."""
    completion = '''{
    "name": "test",
    "value": 42,
    "nested": {
        "deep": true
    }
}'''
    result = parse_json_completion(completion)
    assert result == {"name": "test", "value": 42, "nested": {"deep": True}}


def test_parse_json_with_llm_preamble():
    """Test parsing JSON from LLM response with typical preamble."""
    completion = """Sure! Here's the JSON you requested:

```json
{
    "tool_name": "echo",
    "description": "Echoes input",
    "parameters": ["message"]
}
```

Let me know if you need anything else!"""
    result = parse_json_completion(completion)
    assert result == {
        "tool_name": "echo",
        "description": "Echoes input",
        "parameters": ["message"],
    }


def test_parse_json_array_of_objects():
    """Test parsing array of objects."""
    completion = '[{"id": 1, "name": "first"}, {"id": 2, "name": "second"}]'
    result = parse_json_completion(completion)
    assert result == [{"id": 1, "name": "first"}, {"id": 2, "name": "second"}]


def test_parse_json_with_escaped_characters():
    """Test parsing JSON with escaped characters."""
    completion = r'{"message": "Line 1\nLine 2\tTabbed", "path": "C:\\Users\\test"}'
    result = parse_json_completion(completion)
    assert result == {"message": "Line 1\nLine 2\tTabbed", "path": "C:\\Users\\test"}


def test_parse_json_with_unicode():
    """Test parsing JSON with unicode characters."""
    completion = '{"emoji": "🎉", "chinese": "你好", "value": 42}'
    result = parse_json_completion(completion)
    assert result == {"emoji": "🎉", "chinese": "你好", "value": 42}


def test_parse_invalid_json_raises_error():
    """Test that invalid JSON raises an appropriate error."""
    completion = '{"name": "test", invalid}'
    with pytest.raises(json.JSONDecodeError):
        parse_json_completion(completion)


def test_parse_no_json_raises_error():
    """Test that text without JSON raises an error."""
    completion = "This is just plain text without any JSON"
    with pytest.raises(ValueError, match="No JSON start character found"):
        parse_json_completion(completion)


def test_parse_json_with_only_opening_brace():
    """Test that incomplete JSON raises an error."""
    completion = '{"name": "test"'
    with pytest.raises((ValueError, json.JSONDecodeError)):
        # Should fail when trying to find closing brace or parsing invalid JSON
        parse_json_completion(completion)
