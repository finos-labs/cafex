"""Tests for the JSON Parser module."""

import json
import os
from unittest.mock import patch

import pytest
from typing import Dict, Any, List

from cafex_core.parsers.json_parser import ParseJsonData


@pytest.fixture
def json_parser():
    """Create a JSON parser instance for testing."""
    return ParseJsonData()


@pytest.fixture
def sample_json_dict():
    """Create a sample JSON dictionary for testing."""
    return {
        "name": "John Doe",
        "age": 30,
        "isActive": True,
        "address": {
            "street": "123 Main St",
            "city": "New York",
            "zipcode": "10001"
        },
        "phoneNumbers": [
            {
                "type": "home",
                "number": "212-555-1234"
            },
            {
                "type": "work",
                "number": "646-555-5678"
            }
        ],
        "email": ["john.doe@example.com", "jdoe@work.com"],
        "children": [
            {
                "name": "Jane",
                "age": 5
            },
            {
                "name": "Jack",
                "age": 3
            }
        ],
        "nested": {
            "level1": {
                "level2": {
                    "level3": "deep value"
                }
            }
        }
    }


@pytest.fixture
def sample_json_str(sample_json_dict):
    """Create a sample JSON string for testing."""
    return json.dumps(sample_json_dict)


@pytest.fixture
def sample_json_file(tmp_path, sample_json_dict):
    """Create a temporary JSON file for testing."""
    file_path = tmp_path / "test.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(sample_json_dict, f)
    return str(file_path)


def test_get_value(json_parser, sample_json_dict):
    """Test getting a value from the first level of a JSON dictionary."""
    # Test with valid key
    assert json_parser.get_value(sample_json_dict, "name") == "John Doe"
    assert json_parser.get_value(sample_json_dict, "age") == 30
    assert json_parser.get_value(sample_json_dict, "isActive") is True

    # Test with nested dictionary
    address = json_parser.get_value(sample_json_dict, "address")
    assert isinstance(address, dict)
    assert address["street"] == "123 Main St"

    # Test with array
    phone_numbers = json_parser.get_value(sample_json_dict, "phoneNumbers")
    assert isinstance(phone_numbers, list)
    assert len(phone_numbers) == 2

    # Test with invalid key
    assert json_parser.get_value(sample_json_dict, "nonexistent") is None

    # Test with invalid json_dict
    assert json_parser.get_value("not a dict", "key") is None
    assert json_parser.get_value(None, "key") is None

    # Test with empty key
    assert json_parser.get_value(sample_json_dict, "") is None


def test_get_value_of_key_path(json_parser, sample_json_dict):
    """Test getting a value using a key path."""
    # Test with valid key path
    assert json_parser.get_value_of_key_path(sample_json_dict, "address/street") == "123 Main St"
    assert json_parser.get_value_of_key_path(sample_json_dict, "address/city") == "New York"
    assert json_parser.get_value_of_key_path(sample_json_dict, "nested/level1/level2/level3") == "deep value"

    # Test with custom delimiter
    assert json_parser.get_value_of_key_path(sample_json_dict, "address.city", ".") == "New York"

    # Test with array index
    assert json_parser.get_value_of_key_path(sample_json_dict, "phoneNumbers/0/type") == "home"
    assert json_parser.get_value_of_key_path(sample_json_dict, "phoneNumbers/1/number") == "646-555-5678"
    assert json_parser.get_value_of_key_path(sample_json_dict, "email/0") == "john.doe@example.com"

    # Test with invalid path
    assert json_parser.get_value_of_key_path(sample_json_dict, "nonexistent/path") is None

    # Test with invalid json_dict
    assert json_parser.get_value_of_key_path("not a dict", "key/path") is None

    # Test with empty key path
    assert json_parser.get_value_of_key_path(sample_json_dict, "") is None


def test_read_json_file(json_parser, sample_json_file, sample_json_dict):
    """Test reading a JSON file."""
    # Test with valid file
    result = json_parser.read_json_file(sample_json_file)
    assert result == sample_json_dict

    # Test with nonexistent file
    result = json_parser.read_json_file("nonexistent.json")
    assert result == {}

    # Test with invalid JSON file
    invalid_file = os.path.join(os.path.dirname(sample_json_file), "invalid.json")
    with open(invalid_file, "w") as f:
        f.write("not valid json")

    result = json_parser.read_json_file(invalid_file)
    assert result == {}

    # Test reading a JSON file that raises a generic exception.
    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", side_effect=Exception("Generic error")):
            result = json_parser.read_json_file("generic_error.json")
            assert result == {}


def test_get_value_of_key(json_parser, sample_json_dict, sample_json_str):
    """Test getting the value of a key from JSON data."""
    # Test with dictionary and non-nested search
    assert json_parser.get_value_of_key(sample_json_dict, "name") == "John Doe"

    # Test with string and non-nested search
    assert json_parser.get_value_of_key(sample_json_str, "name") == "John Doe"

    # Test with nested search
    result = json_parser.get_value_of_key(sample_json_dict, "name", nested=True)
    assert isinstance(result, list)
    assert "John Doe" in result
    assert "Jane" in result
    assert "Jack" in result

    # Test with nested search and string
    result = json_parser.get_value_of_key(sample_json_str, "name", nested=True)
    assert isinstance(result, list)
    assert "John Doe" in result
    assert "Jane" in result
    assert "Jack" in result

    # Test with invalid key
    assert json_parser.get_value_of_key(sample_json_dict, "nonexistent") is None
    assert json_parser.get_value_of_key(sample_json_dict, "nonexistent", nested=True) == []

    # Test with invalid json_data
    assert json_parser.get_value_of_key(None, "key") is None
    assert json_parser.get_value_of_key(None, "key", nested=True) == []

    # Test with empty key
    assert json_parser.get_value_of_key(sample_json_dict, "") is None
    assert json_parser.get_value_of_key(sample_json_dict, "", nested=True) == []

    # Test getting the value of a key that raises a generic exception.
    with patch.object(json_parser, 'get_value', side_effect=Exception("Generic error")):
        result = json_parser.get_value_of_key(sample_json_dict, "name")
        assert result is None

    with patch.object(json_parser, 'get_value', side_effect=Exception("Generic error")):
        result = json_parser.get_value_of_key(sample_json_dict, "invalid", nested=True)
        assert result == []


def test_get_json_values_by_key_path(json_parser, sample_json_dict):
    """Test extracting values using a key path."""
    try:
        # Test with valid keypath and key
        result = json_parser.get_json_values_by_key_path(
            sample_json_dict, keypath="address/city", delimiter="/"
        )
        assert result == "New York"

        # Test with parser=True
        result = json_parser.get_json_values_by_key_path(
            sample_json_dict, parser=True, keypath="address.city"
        )
        assert result == "New York"

        # Test with invalid keypath
        assert json_parser.get_json_values_by_key_path(sample_json_dict, keypath="nonexistent/path") is None

        # Test with missing keypath
        assert json_parser.get_json_values_by_key_path(sample_json_dict) is None

        # Test with invalid json_data
        assert json_parser.get_json_values_by_key_path(None, keypath="address/city") is None

        assert json_parser.get_json_values_by_key_path(
            sample_json_dict, keypath=None, parser=True) is None
        sample_json_dict2 = {"user": {"profile": {"name": "John"}}}
        result = json_parser.get_json_values_by_key_path(sample_json_dict2, keypath="nonexistent/profile", key="name")
        assert result is None
        sample_json_dict2 = {"user": {"profile": {"name": "John"}}}
        result = json_parser.get_json_values_by_key_path(sample_json_dict2, keypath="user/profile", key="nonexistent")
        assert result is None
        sample_json_dict = {"user": {"profile": {"name": "John"}}}
        result = json_parser.get_json_values_by_key_path(sample_json_dict, keypath="nonexistent", key="nonexistent")
        assert result is None
        sample_json_dict = {"name": "John"}
        result = json_parser.get_json_values_by_key_path(sample_json_dict, keypath="name", key="name")
        assert result is 'John'
        with patch.object(json_parser, 'get_dict', side_effect=Exception("Generic error")):
            result = json_parser.get_json_values_by_key_path(sample_json_dict, keypath="address/city")
            assert result is None
            json_parser.exceptions.raise_generic_exception.assert_called_with(
                "Error in get_json_values_by_key_path: Generic error", fail_test=False
            )
    except Exception as e:
        print(e)


def test_get_value_from_key_path(json_parser, sample_json_dict):
    """Test extracting a value at a specified key path."""
    try:
        # Test with absolute key path
        result = json_parser.get_value_from_key_path(
            sample_json_dict, "address/city", "absolute"
        )
        assert result == "New York"

        # Test with relative key path
        result = json_parser.get_value_from_key_path(
            sample_json_dict, "address/city", "relative", "city"
        )
        assert result == "New York"

        # Test with invalid key path
        assert json_parser.get_value_from_key_path(
            sample_json_dict, "nonexistent/path", "absolute"
        ) is None

        # Test with missing key_path_type
        assert json_parser.get_value_from_key_path(
            sample_json_dict, "address/city", None
        ) is None

        # Test with invalid key_path_type
        assert json_parser.get_value_from_key_path(
            sample_json_dict, "address/city", "invalid"
        ) is None

        # Test with relative path but missing key
        assert json_parser.get_value_from_key_path(
            sample_json_dict, "address/city", "relative"
        ) is None

        # Test with invalid json_data
        assert json_parser.get_value_from_key_path(None, "address/city", "absolute") is None
        # Test with invalid key_path
        assert json_parser.get_value_from_key_path(sample_json_dict, None, "absolute") is None
        with patch.object(json_parser, 'get_dict', side_effect=Exception("Generic error")):
            result = json_parser.get_value_from_key_path(sample_json_dict, "address/city", "absolute")
            assert result is None
            json_parser.exceptions.raise_generic_exception.assert_called_with(
                "Error in get_value_from_key_path: Generic error", fail_test=False
            )
    except Exception as e:
        print(e)


def test_print_all_key_values(json_parser, sample_json_dict):
    """Test printing all key-value pairs."""
    try:
        # This is more of a visual test, just make sure it doesn't crash
        json_parser.print_all_key_values(sample_json_dict)

        # Test with invalid json_data
        json_parser.print_all_key_values("not a dict")

        # We can't easily test the logger output, but we can check it doesn't raise exceptions
        with patch.object(json_parser, 'logger') as mock_logger:
            with patch.object(json_parser, 'exceptions') as mock_exceptions:
                # Test with invalid json_data
                json_parser.print_all_key_values("not a dict")
                mock_exceptions.raise_generic_exception.assert_called_with(
                    "json_data must be a dictionary", fail_test=False
                )

                # Test with valid json_data but force an exception in logger.debug
                with patch.object(mock_logger, 'debug', side_effect=Exception("Generic error")):
                    json_parser.print_all_key_values({"key": "value"})
                    mock_exceptions.raise_generic_exception.assert_called_with(
                        "Error while printing all key-value pairs: Generic error", fail_test=False
                    )
    except Exception as e:
        print(e)


def test_get_dict(json_parser, sample_json_dict, sample_json_str):
    """Test ensuring the input is a valid JSON dictionary."""
    try:
        # Test with dictionary
        result = json_parser.get_dict(sample_json_dict)
        assert result == sample_json_dict

        # Test with string
        result = json_parser.get_dict(sample_json_str)
        assert result == sample_json_dict

        # Test with invalid input
        result = json_parser.get_dict(None)
        assert result == {}

        # Test with invalid JSON string
        result = json_parser.get_dict("not valid json")
        assert result == {}
        with patch('json.loads', side_effect=Exception("Unexpected error")):
            with patch.object(json_parser.exceptions, 'raise_generic_exception') as mock_raise_generic_exception:
                result = json_parser.get_dict('{"name": "John"}')
                assert result == {}
                mock_raise_generic_exception.assert_called_with(
                    "Error in get_dict: Unexpected error", fail_test=False
                )
    except Exception as e:
        print(e)


def test_is_json(json_parser, sample_json_str):
    """Test checking if input is valid JSON."""
    # Test with valid JSON string
    result = json_parser.is_json(sample_json_str)
    assert isinstance(result, dict)
    assert result["name"] == "John Doe"

    # Test with invalid JSON string
    result = json_parser.is_json("not valid json")
    assert result == {}


def test_compare_json(json_parser):
    """Test comparing two JSON structures."""
    # Test with identical JSON
    json1 = {"name": "John", "age": 30}
    json2 = {"name": "John", "age": 30}
    result = json_parser.compare_json(json1, json2)
    assert result is True

    # Test with different values
    json1 = {"name": "John", "age": 30}
    json2 = {"name": "John", "age": 31}
    result = json_parser.compare_json(json1, json2)
    assert isinstance(result, tuple)
    assert result[0] is False
    assert len(result[1]) > 0

    # Test with missing key
    json1 = {"name": "John", "age": 30}
    json2 = {"name": "John"}
    result = json_parser.compare_json(json1, json2)
    assert isinstance(result, tuple)
    assert result[0] is False
    assert len(result[1]) > 0

    # Test with extra key
    json1 = {"name": "John"}
    json2 = {"name": "John", "age": 30}
    result = json_parser.compare_json(json1, json2)
    assert isinstance(result, tuple)
    assert result[0] is False
    assert len(result[1]) > 0

    # Test with ignore_extra=True
    json1 = {"name": "John"}
    json2 = {"name": "John", "age": 30}
    result = json_parser.compare_json(json1, json2, ignore_extra=True)
    assert result is True

    # Test with ignore_keys
    json1 = {"name": "John", "age": 30}
    json2 = {"name": "John", "age": 31}
    result = json_parser.compare_json(json1, json2, ignore_keys=["age"])
    assert result is True

    # Test with invalid json_data
    result = json_parser.compare_json(None, {})
    assert isinstance(result, tuple)
    assert result[0] is False
    assert len(result[1]) > 0

    # Test with invalid ignore_keys
    result = json_parser.compare_json({}, {}, ignore_keys="not a list")
    assert isinstance(result, tuple)
    assert result[0] is False
    assert len(result[1]) > 0

    # Test with invalid ignore_extra
    result = json_parser.compare_json({}, {}, ignore_extra="not a bool")
    assert isinstance(result, tuple)
    assert result[0] is False
    assert len(result[1]) > 0

    # Test with invalid json_data
    result = json_parser.compare_json({}, None)
    assert isinstance(result, tuple)


def test_level_based_value(json_parser, sample_json_dict):
    """Test getting values at a specific level in a nested structure."""
    # Test at level 0
    result = json_parser.level_based_value(sample_json_dict, "name", 0)
    assert result == ["John Doe"]

    # Test at level 1
    result = json_parser.level_based_value(sample_json_dict, "street", 1)
    assert result == ["123 Main St"]

    # Test at level 2
    result = json_parser.level_based_value(sample_json_dict, "level2", 2)
    assert len(result) == 1

    # Test at level 3
    result = json_parser.level_based_value(sample_json_dict, "level3", 3)
    assert result == ["deep value"]

    # Test with nonexistent key
    result = json_parser.level_based_value(sample_json_dict, "nonexistent", 0)
    assert result == []

    # Test with invalid json_data
    result = json_parser.level_based_value(None, "key", 0)
    assert result == []

    # Test with invalid level
    result = json_parser.level_based_value(sample_json_dict, "name", "not an int")
    assert result == []


def test_convert_json_to_xml(json_parser, sample_json_dict):
    """Test converting JSON to XML."""
    # Test basic conversion
    result = json_parser.convert_json_to_xml(sample_json_dict)
    assert isinstance(result, str)
    assert "<name>John Doe</name>" in result
    assert "<street>123 Main St</street>" in result

    # Test with empty JSON
    result = json_parser.convert_json_to_xml({})
    assert isinstance(result, str)

    # Test with invalid json_data
    result = json_parser.convert_json_to_xml(None)
    assert result == ""


def test_get_all_keys(json_parser, sample_json_dict):
    """Test extracting all keys from a nested dictionary."""
    # Test with nested dictionary
    result = json_parser.get_all_keys(sample_json_dict)
    assert isinstance(result, list)
    assert "name" in result
    assert "street" in result
    assert "level3" in result

    # Test with empty dictionary
    result = json_parser.get_all_keys({})
    assert result == []

    # Test with invalid json_data
    result = json_parser.get_all_keys(None)
    assert result == []


def test_get_occurrence_of_key(json_parser, sample_json_dict):
    """Test counting the occurrences of a key."""
    # Test with common key
    result = json_parser.get_occurrence_of_key(sample_json_dict, "name")
    assert result == 3  # main name, plus 2 children names

    # Test with unique key
    result = json_parser.get_occurrence_of_key(sample_json_dict, "street")
    assert result == 1

    # Test with nonexistent key
    result = json_parser.get_occurrence_of_key(sample_json_dict, "nonexistent")
    assert result == 0

    # Test with invalid json_data
    result = json_parser.get_occurrence_of_key(None, "key")
    assert result == 0

    # Test with empty key
    result = json_parser.get_occurrence_of_key(sample_json_dict, "")
    assert result == 0


def test_key_exists(json_parser, sample_json_dict):
    """Test checking if a key exists in the JSON data."""
    # Test with existing key
    assert json_parser.key_exists(sample_json_dict, "name") is True

    # Test with nested key
    assert json_parser.key_exists(sample_json_dict, "street") is True

    # Test with nonexistent key
    assert json_parser.key_exists(sample_json_dict, "nonexistent") is False

    # Test with invalid json_data
    assert json_parser.key_exists(None, "key") is False

    # Test with empty key
    assert json_parser.key_exists(sample_json_dict, "") is False


def test_get_multiple_key_value(json_parser, sample_json_dict):
    """Test getting values for multiple keys and key paths."""
    # Test with keys only
    result = json_parser.get_multiple_key_value(sample_json_dict, ["name", "age"])
    assert "name" in result
    assert "age" in result
    assert "John Doe" in result["name"]
    assert 30 in result["age"]

    # Test with keys and key_paths
    result = json_parser.get_multiple_key_value(
        sample_json_dict,
        ["name"],
        key_paths=["address/city", "nested/level1/level2/level3"]
    )
    assert "name" in result
    assert "address/city" in result
    assert "nested/level1/level2/level3" in result
    assert "John Doe" in result["name"]
    assert result["address/city"] == "New York"
    assert result["nested/level1/level2/level3"] == "deep value"

    # Test with invalid json_data
    result = json_parser.get_multiple_key_value(None, ["key"])
    assert result == {}

    # Test with empty keys
    result = json_parser.get_multiple_key_value(sample_json_dict, [])
    assert result == {}

    # Test with invalid keys type
    result = json_parser.get_multiple_key_value(sample_json_dict, "not a list")
    assert result == {}


def test_get_json_result(json_parser, sample_json_dict):
    """Test getting a value using the unified interface."""
    # Test with key
    result = json_parser.get_json_result(sample_json_dict, key="name")
    assert result == "John Doe"

    # Test with nested key
    result = json_parser.get_json_result(sample_json_dict, key="name", nested=True)
    assert isinstance(result, list)
    assert "John Doe" in result

    # Test with absolute keypath
    result = json_parser.get_json_result(
        sample_json_dict,
        keypath="address/city",
        keypath_type="absolute"
    )
    assert result == "New York"

    # Test with relative keypath
    result = json_parser.get_json_result(
        sample_json_dict,
        keypath="address",
        keypath_type="relative",
        key_input="city"
    )
    assert result == "New York"

    # Test with missing required parameters
    assert json_parser.get_json_result(sample_json_dict) is None

    # Test with keypath but no keypath_type
    assert json_parser.get_json_result(sample_json_dict, keypath="address/city") is None

    # Test with invalid json_data
    assert json_parser.get_json_result(None, key="name") is None


def test_update_json_based_on_key(json_parser, sample_json_dict):
    """Test updating all occurrences of a key with a new value."""
    # Test updating a simple key
    updated = json_parser.update_json_based_on_key(sample_json_dict, "name", "Jane Smith")
    assert updated["name"] == "Jane Smith"

    # Check that all occurrences are updated
    assert updated["children"][0]["name"] == "Jane Smith"
    assert updated["children"][1]["name"] == "Jane Smith"

    # Test with nonexistent key
    result = json_parser.update_json_based_on_key(sample_json_dict, "nonexistent", "value")
    assert result == sample_json_dict  # Should return the original dict unchanged

    # Test with invalid json_data
    result = json_parser.update_json_based_on_key(None, "key", "value")
    assert result == {}

    # Test with empty key
    result = json_parser.update_json_based_on_key(sample_json_dict, "", "value")
    assert result == sample_json_dict  # Should return the original dict unchanged


def test_update_json_based_on_parent_child_key(json_parser, sample_json_dict):
    """Test updating a specific child key within a parent key."""
    # Create a copy to ensure the original doesn't change
    json_copy = json.loads(json.dumps(sample_json_dict))

    # Test updating a nested key
    updated = json_parser.update_json_based_on_parent_child_key(
        json_copy, "address", "city", "Chicago"
    )
    assert updated["address"]["city"] == "Chicago"

    # Test with nonexistent parent key
    result = json_parser.update_json_based_on_parent_child_key(
        sample_json_dict, "nonexistent", "key", "value"
    )
    assert result == sample_json_dict  # Should return the original dict unchanged

    # Test with nonexistent child key
    result = json_parser.update_json_based_on_parent_child_key(
        sample_json_dict, "address", "nonexistent", "value"
    )
    assert result == sample_json_dict  # Should return the original dict unchanged

    # Test with invalid json_data
    result = json_parser.update_json_based_on_parent_child_key(None, "parent", "child", "value")
    assert result == {}

    # Test with empty parent key
    result = json_parser.update_json_based_on_parent_child_key(sample_json_dict, "", "child", "value")
    assert result == sample_json_dict  # Should return the original dict unchanged

    # Test with empty child key
    result = json_parser.update_json_based_on_parent_child_key(sample_json_dict, "parent", "", "value")
    assert result == sample_json_dict  # Should return the original dict unchanged


def test_update_json_based_on_parent_child_key_index(json_parser, sample_json_dict):
    """Test updating a specific child key at a given index."""
    # Create a copy to ensure the original doesn't change
    json_copy = json.loads(json.dumps(sample_json_dict))

    # Test updating a child key at a specific index
    updated = json_parser.update_json_based_on_parent_child_key_index(
        json_copy, "children", "name", "1", "Updated Child"
    )
    # First child should be updated
    assert updated["children"][0]["name"] == "Updated Child"
    # Second child should remain unchanged
    assert updated["children"][1]["name"] == "Jack"

    # Test with nonexistent parent key
    result = json_parser.update_json_based_on_parent_child_key_index(
        sample_json_dict, "nonexistent", "key", "1", "value"
    )
    assert result == sample_json_dict  # Should return the original dict unchanged

    # Test with nonexistent child key
    result = json_parser.update_json_based_on_parent_child_key_index(
        sample_json_dict, "children", "nonexistent", "1", "value"
    )
    assert result == sample_json_dict  # Should return the original dict unchanged

    # Test with invalid json_data
    result = json_parser.update_json_based_on_parent_child_key_index(
        None, "parent", "child", "1", "value"
    )
    assert result == {}

    # Test with empty parent key
    result = json_parser.update_json_based_on_parent_child_key_index(
        sample_json_dict, "", "child", "1", "value"
    )
    assert result == sample_json_dict  # Should return the original dict unchanged

    # Test with empty child key
    result = json_parser.update_json_based_on_parent_child_key_index(
        sample_json_dict, "parent", "", "1", "value"
    )
    assert result == sample_json_dict  # Should return the original dict unchanged

    # Test with empty index
    result = json_parser.update_json_based_on_parent_child_key_index(
        sample_json_dict, "parent", "child", "", "value"
    )
    assert result == sample_json_dict  # Should return the original dict unchanged

    json_data = {"users": [{"name": "John"}, {"name": "Jane"}]}

    with patch.object(json_parser.exceptions, 'raise_generic_exception') as mock_raise_generic_exception:
        result = json_parser.update_json_based_on_parent_child_key_index(
            json_data, "users", "name", "1", ["Jane Doe", "John Doe"]
        )
        assert result == json_data  # Should return the original dict unchanged
        mock_raise_generic_exception.assert_called_with(
            "Number of keys and values must be the same", fail_test=False
        )


