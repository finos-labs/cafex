"""
Module providing JSON parsing capabilities for the CAFEX framework.

This module provides robust JSON parsing and manipulation functionality including:
- Reading and validating JSON data
- Extracting values using keys or key paths
- Comparing JSON structures
- Converting JSON to XML
- Updating JSON data based on keys
"""

import json
import os
from functools import reduce
from typing import Any, Dict, List, Optional, Tuple, Union

import dicttoxml
import objectpath
from nested_lookup import (
    get_all_keys,
    get_occurrence_of_key,
    nested_lookup,
    nested_update,
)

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.utils.exceptions import CoreExceptions

# Global variables for the parser (to be refactored as instance variables)
int_keys_counter = 1
int_node_counter = 1
bln_flag = True
bln_parent_key_status = False
bln_child_key_status = False


class ParseJsonData:
    """
    A modern JSON parser for extracting, comparing, and manipulating JSON data.

    This class provides methods to parse JSON content and extract data using various techniques
    including key lookup, path-based access, and nested searches. It also supports comparison,
    validation, and manipulation of JSON data.

    Features:
        - JSON file and string parsing
        - Key and path-based value extraction
        - Nested structure traversal
        - JSON comparison functionality
        - JSON to XML conversion
        - JSON validation
        - JSON manipulation and updating

    Attributes:
        logger: Logger instance for debug/error logging
        exceptions: Exception handler for standardized error handling

    Example:
        >>> parser = ParseJsonData()
        >>> json_data = parser.read_json_file("config.json")
        >>> value = parser.get_value(json_data, "api_key")
    """

    def __init__(self):
        self.logger = CoreLogger(name=__name__).get_logger()
        self.exceptions = CoreExceptions()

    def get_value(self, json_dict: Dict[str, Any], key: str) -> Any:
        """
        Gets the value of a key from the first level of a JSON dictionary.

        Args:
            json_dict (dict): The JSON dictionary to search.
            key (str): The key to retrieve the value for.

        Returns:
            The value associated with the key, or None if not found.

        Raises:
            ValueError: If json_dict is not a dictionary or the key is not found.

        Examples:
            >>> parser = ParseJsonData()
            >>> data = {"name": "John", "age": 30}
            >>> parser.get_value(data, "name")
            'John'
        """
        if not isinstance(json_dict, dict):
            self.exceptions.raise_generic_exception(
                "json_dict must be a dictionary", fail_test=False
            )
            return None

        if not key:
            self.exceptions.raise_generic_exception("key cannot be null or empty", fail_test=False)
            return None

        try:
            return json_dict[key]
        except KeyError:
            self.exceptions.raise_generic_exception(
                f"Key '{key}' not in the JSON dictionary", fail_test=False
            )
            return None

    def get_value_of_key_path(
        self, json_dict: Dict[str, Any], key_path: str, delimiter: str = "/"
    ) -> Any:
        """
        Gets the value of a key from a nested JSON dictionary using the provided key path.

        Args:
            json_dict (dict): The JSON dictionary to search.
            key_path (str): The path to the key, using the specified delimiter.
            delimiter (str, optional): The delimiter used in the key path (default: "/").

        Returns:
            Any: The value associated with the key path, or None if not found.

        Raises:
            ValueError: If json_dict is not a dictionary or the key path is not found.

        Examples:
            >>> parser = ParseJsonData()
            >>> data = {"user": {"profile": {"name": "John"}}}
            >>> parser.get_value_of_key_path(data, "user/profile/name")
            'John'
            >>> parser.get_value_of_key_path(data, "user.profile.name", ".")
            'John'
        """
        try:
            if not isinstance(json_dict, dict):
                self.exceptions.raise_generic_exception(
                    "json_dict must be a dictionary", fail_test=False
                )
                return None

            if not key_path:
                self.exceptions.raise_generic_exception(
                    "key_path cannot be null or empty", fail_test=False
                )
                return None
            # Split the key path into segments
            key_list = key_path.split(delimiter)

            def get_item(obj, key):
                if isinstance(obj, list) and key.isdigit():
                    # Convert string index to integer for list access
                    return obj[int(key)]
                return obj[key]

            return reduce(get_item, key_list, json_dict)
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error in fetching key value using the provided key path: {str(e)}",
                fail_test=False,
            )
            return None

    def read_json_file(self, file_path: str) -> Dict[str, Any]:
        """
        Reads a JSON file and returns the parsed dictionary.

        Args:
            file_path: The path to the JSON file.

        Returns:
            The parsed JSON dictionary.

        Raises:
            FileNotFoundError: If the JSON file is not found.
            ValueError: If the JSON file contains invalid JSON.

        Examples:
            >>> parser = ParseJsonData()
            >>> data = parser.read_json_file("config.json")
            >>> print(data["version"])
            '1.0'
        """
        try:
            if not os.path.exists(file_path):
                self.exceptions.raise_generic_exception(
                    f"JSON file not found: {file_path}", fail_test=False
                )
                return {}

            with open(file_path, "r", encoding="utf-8") as json_file:
                return json.load(json_file)
        except json.JSONDecodeError as e:
            self.exceptions.raise_generic_exception(
                f"Error parsing JSON file: {str(e)}", fail_test=False
            )
            return {}
        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error reading JSON file: {str(e)}", fail_test=False
            )
            return {}

    def get_value_of_key(
        self, json_data: Union[str, Dict[str, Any]], key: str, nested: bool = False
    ) -> Any:
        """
        Gets the value of a key from the JSON data, optionally searching nested structures.

        Args:
            json_data: The JSON data to parse (either a string or a dictionary).
            key: The key to retrieve the value for.
            nested: Whether to search for the key in nested structures (default: False).

        Returns:
            The value associated with the key, or a list of values if nested is True and multiple keys are found.

        Raises:
            ValueError: If json_data is not a dictionary or the key is not found.

        Examples:
            >>> parser = ParseJsonData()
            >>> data = {"user": {"name": "John"}, "admin": {"name": "Admin"}}
            >>> parser.get_value_of_key(data, "user", False)
            {'name': 'John'}
            >>> parser.get_value_of_key(data, "name", True)
            ['John', 'Admin']
        """
        try:
            if not json_data:
                self.exceptions.raise_generic_exception(
                    "json_data cannot be null or empty", fail_test=False
                )
                return None if not nested else []

            if not key:
                self.exceptions.raise_generic_exception(
                    "key cannot be null or empty", fail_test=False
                )
                return None if not nested else []

            json_dict = self.get_dict(json_data)

            if nested:
                return nested_lookup(key, json_dict)

            return self.get_value(json_dict, key)

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error getting value of key: {str(e)}", fail_test=False
            )
            return None if not nested else []

    def get_json_values_by_key_path(
        self,
        json_data: Union[str, Dict[str, Any]],
        delimiter: str = "/",
        keypath: Optional[str] = None,
        key: Optional[str] = None,
        parser: bool = False,
    ) -> Any:
        """
        Extracts values from a JSON dictionary using a key path.

        Args:
            json_data: The JSON data (string or dictionary)
            delimiter: The delimiter used in the key path
            keypath: The key path to extract values from
            key: The specific sub-child key to retrieve the value for
            parser: If True, parses the json_data as a JSON string before processing

        Returns:
            Any: The value(s) associated with the key path.

        Raises:
            ValueError: If json_data or keypath is null or empty, or if key is not found
            in the nested dictionary

        Examples:
            >>> json_parser = ParseJsonData()
            >>> data = {"users": {"admin": {"name": "Admin", "role": "admin"}}}
            >>> json_parser.get_json_values_by_key_path(data, keypath="users/admin", key="name")
            'Admin'
        """
        try:
            if not json_data:
                self.exceptions.raise_generic_exception("json_data cannot be null", fail_test=False)
                return None

            json_dict = self.get_dict(json_data)

            if parser:
                if not keypath:
                    self.exceptions.raise_generic_exception(
                        "keypath cannot be null when parser is True", fail_test=False
                    )
                    return None

                modified_keypath = keypath.replace("/", ".") if delimiter == "/" else keypath
                json_tree = objectpath.Tree(json_dict)
                return json_tree.execute("$." + modified_keypath)

            if keypath:
                root_parent = keypath.split(delimiter)

                if len(root_parent) == 1:
                    root = root_parent[0]
                    if root not in json_dict:
                        self.exceptions.raise_generic_exception(
                            f"Key '{root}' not found in JSON data", fail_test=False
                        )
                        return None

                    result = json_dict[root]
                    # If we're looking for a specific subkey within this result
                    if key is not None and isinstance(result, dict):
                        return result.get(key)
                    return result

                root = root_parent[0]
                parent = root_parent[1]

                if root not in json_dict:
                    self.exceptions.raise_generic_exception(
                        f"Root key '{root}' not found in JSON data", fail_test=False
                    )
                    return None

                json_tree = objectpath.Tree(json_dict[root])
                result_list = list(json_tree.execute("$.." + parent))

                for result in result_list:
                    if key is not None and isinstance(result, dict):
                        return result.get(key)
                    return result

            self.exceptions.raise_generic_exception(
                "Invalid arguments for get_json_values_by_key_path", fail_test=False
            )
            return None

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error in get_json_values_by_key_path: {str(e)}", fail_test=False
            )
        return None

    def get_value_from_key_path(
        self,
        json_data: Union[str, Dict[str, Any]],
        key_path: str,
        key_path_type: str,
        key: Optional[str] = None,
        delimiter: str = "/",
    ) -> Any:
        """
        Extract the value at the specified key path from the JSON data.

        Args:
            json_data: The JSON data (string or dictionary)
            key_path: The path to the key, using the specified delimiter
            key_path_type: Either "absolute" or "relative"
            key: The key to retrieve the value for when using relative key paths
            delimiter: The delimiter used in the key path

        Returns:
            The value associated with the key path

        Raises:
            ValueError: If required arguments are missing, invalid, or the key path is not found

        Examples:
            >>> parser = ParseJsonData()
            >>> data = {"users": {"admin": {"name": "Admin", "role": "admin"}}}
            >>> parser.get_value_from_key_path(
            ...     data, "users/admin", "absolute"
            ... )
            {'name': 'Admin', 'role': 'admin'}
            >>> parser.get_value_from_key_path(
            ...     data, "users/admin", "relative", "name"
            ... )
            'Admin'
        """
        try:
            if not json_data:
                self.exceptions.raise_generic_exception("json_data cannot be null", fail_test=False)
                return None

            if not key_path:
                self.exceptions.raise_generic_exception("key_path cannot be null", fail_test=False)
                return None

            if not key_path_type:
                self.exceptions.raise_generic_exception(
                    "key_path_type cannot be null", fail_test=False
                )
                return None

            json_dict = self.get_dict(json_data)

            key_path_type = key_path_type.lower()

            if key_path_type == "absolute":
                return self.get_value_of_key_path(json_dict, key_path, delimiter)
            if key_path_type == "relative":
                if key is None:
                    self.exceptions.raise_generic_exception(
                        "key argument is required if key_path_type is relative", fail_test=False
                    )
                    return None

                return self.get_json_values_by_key_path(
                    json_dict, delimiter, keypath=key_path, key=key
                )

            self.exceptions.raise_generic_exception(
                "Invalid key_path_type. Use 'absolute' or 'relative'", fail_test=False
            )
            return None

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error in get_value_from_key_path: {str(e)}", fail_test=False
            )
            return None

    def print_all_key_values(self, json_data: Dict[str, Any]) -> None:
        """
        Print all key-value pairs in a nested dictionary structure.

        Args:
            json_data: The nested dictionary to print

        Raises:
            ValueError: If json_data is not a dictionary

        Examples:
            >>> parser = ParseJsonData()
            >>> data = {"user": {"name": "John", "age": 30}}
            >>> parser.print_all_key_values(data)
            user:
              name: John
              age: 30
        """
        try:
            if not isinstance(json_data, dict):
                self.exceptions.raise_generic_exception(
                    "json_data must be a dictionary", fail_test=False
                )
                return

            def _print_nested(data: Dict[str, Any], indent: int = 0) -> None:
                for key, value in data.items():
                    if isinstance(value, dict):
                        self.logger.debug("%s%s:", " " * indent, key)
                        _print_nested(value, indent + 2)
                    else:
                        self.logger.debug("%s%s: %s", " " * indent, key, value)

            _print_nested(json_data)

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error while printing all key-value pairs: {str(e)}", fail_test=False
            )

    def get_dict(self, json_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Ensure the input is a valid JSON dictionary.

        Args:
            json_data: The input data, which can be either a JSON string or a dictionary

        Returns:
            The parsed JSON dictionary

        Raises:
            ValueError: If the input data is not a valid JSON string or dictionary

        Examples:
            >>> parser = ParseJsonData()
            >>> parser.get_dict('{"name": "John"}')
            {'name': 'John'}
            >>> parser.get_dict({"name": "John"})
            {'name': 'John'}
        """
        try:
            if isinstance(json_data, dict):
                return json_data

            if isinstance(json_data, str):
                return json.loads(json_data)

            self.exceptions.raise_generic_exception(
                "Input must be a JSON string or dictionary", fail_test=False
            )
            return {}

        except json.JSONDecodeError as e:
            self.exceptions.raise_generic_exception(f"Invalid JSON data: {str(e)}", fail_test=False)
            return {}
        except Exception as e:
            self.exceptions.raise_generic_exception(f"Error in get_dict: {str(e)}", fail_test=False)
            return {}

    def is_json(self, json_data: str) -> Dict[str, Any]:
        """
        Check if the input is a valid JSON string and return the parsed dictionary.

        Args:
            json_data: The input data to be checked

        Returns:
            The parsed JSON dictionary if json_data is valid JSON

        Raises:
            ValueError: If the input data is not valid JSON

        Examples:
            >>> parser = ParseJsonData()
            >>> parser.is_json('{"name": "John"}')
            {'name': 'John'}
            >>> parser.is_json('invalid')
            Traceback (most recent call last):
            ...
            ValueError: Invalid JSON data: ...
        """

        try:
            return json.loads(json_data)
        except json.JSONDecodeError as e:
            self.exceptions.raise_generic_exception(f"Invalid JSON data: {str(e)}", fail_test=False)
            return {}

    def compare_json(
        self,
        expected_json: Union[str, Dict[str, Any]],
        actual_json: Union[str, Dict[str, Any]],
        ignore_keys: Optional[List[str]] = None,
        ignore_extra: bool = False,
    ) -> Union[bool, Tuple[bool, List[str]]]:
        """
        Compare two JSON structures (strings or dictionaries).

        Args:
            expected_json: The expected JSON data (string or dictionary)
            actual_json: The actual JSON data (string or dictionary)
            ignore_keys: A list of keys to ignore during comparison
            ignore_extra: Whether to ignore extra keys in actual_json

        Returns:
            True if the JSON structures are equal (considering ignore_keys and ignore_extra),
            otherwise a tuple containing False and a list of mismatches

        Raises:
            ValueError: If the input JSON data is invalid

        Examples:
            >>> parser = ParseJsonData()
            >>> parser.compare_json(
            ...     {"name": "John", "age": 30},
            ...     {"name": "John", "age": 30, "role": "admin"},
            ...     ignore_extra=True
            ... )
            True
            >>> result = parser.compare_json(
            ...     {"name": "John", "age": 30},
            ...     {"name": "John", "age": 25}
            ... )
            >>> isinstance(result, tuple) and not result[0]
            True
        """

        try:
            if ignore_keys is None:
                ignore_keys = []

            if expected_json is None:
                self.exceptions.raise_generic_exception(
                    "expected_json can not be None", fail_test=False
                )
                return False, ["expected_json can not be None"]

            if actual_json is None:
                self.exceptions.raise_generic_exception(
                    "actual_json can not be None", fail_test=False
                )
                return False, ["actual_json can not be None"]

            if not isinstance(ignore_keys, list):
                self.exceptions.raise_generic_exception(
                    "ignore_keys must be a list", fail_test=False
                )
                return False, ["ignore_keys must be a list"]

            if not isinstance(ignore_extra, bool):
                self.exceptions.raise_generic_exception(
                    "ignore_extra must be a boolean", fail_test=False
                )
                return False, ["ignore_extra must be a boolean"]

            expected_dict = self.get_dict(expected_json)
            actual_dict = self.get_dict(actual_json)

            error_list = []

            def compare_dicts(
                expected: Dict[str, Any], actual: Dict[str, Any], path: str = ""
            ) -> None:
                for key, expected_value in expected.items():
                    if key in ignore_keys:
                        continue

                    if key not in actual:
                        error_list.append(f"Key '{path}{key}' does not exist in actual JSON")
                        continue

                    actual_value = actual[key]

                    if isinstance(expected_value, dict) and isinstance(actual_value, dict):
                        compare_dicts(expected_value, actual_value, f"{path}{key}.")
                    elif isinstance(expected_value, list) and isinstance(actual_value, list):
                        if len(expected_value) != len(actual_value):
                            error_list.append(
                                f"List length mismatch for '{path}{key}': "
                                f"expected {len(expected_value)}, got {len(actual_value)}"
                            )
                        else:
                            for i, (exp_item, act_item) in enumerate(
                                zip(expected_value, actual_value)
                            ):
                                if isinstance(exp_item, dict) and isinstance(act_item, dict):
                                    compare_dicts(exp_item, act_item, f"{path}{key}[{i}].")
                                elif exp_item != act_item:
                                    error_list.append(
                                        f"Value mismatch at '{path}{key}[{i}]': "
                                        f"expected {exp_item}, got {act_item}"
                                    )
                    elif expected_value != actual_value:
                        error_list.append(
                            f"Value mismatch for '{path}{key}': "
                            f"expected {expected_value}, got {actual_value}"
                        )

                if not ignore_extra:
                    for key in set(actual.keys()) - set(expected.keys()):
                        if key not in ignore_keys:
                            error_list.append(f"Unexpected key in actual JSON: '{path}{key}'")

            compare_dicts(expected_dict, actual_dict)

            if error_list:
                return False, error_list

            return True

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error comparing JSON objects: {str(e)}", fail_test=False
            )
            return False, [f"Error comparing JSON objects: {str(e)}"]

    def level_based_value(
        self, json_data: Union[str, Dict[str, Any]], key: str, level: int = 0
    ) -> List[Any]:
        """
        Get values for a key at a specific level in a nested JSON structure.

        Args:
            json_data: The JSON data (string or dictionary)
            key: The key to search for
            level: The level in the JSON hierarchy to search (0-based)

        Returns:
            A list of values found for the key at the specified level

        Raises:
            ValueError: If json_data or key is null or empty, or if level is not an integer

        Examples:
            >>> parser = ParseJsonData()
            >>> data = {
            ...     "level0": "value0",
            ...     "nested": {
            ...         "level1": "value1",
            ...         "more": {
            ...             "level2": "value2"
            ...         }
            ...     }
            ... }
            >>> parser.level_based_value(data, "level0", 0)
            ['value0']
            >>> parser.level_based_value(data, "level1", 1)
            ['value1']
            >>> parser.level_based_value(data, "level2", 2)
            ['value2']
        """
        try:
            if not json_data:
                self.exceptions.raise_generic_exception(
                    "json_data cannot be null or empty", fail_test=False
                )
                return []

            if not key:
                self.exceptions.raise_generic_exception(
                    "key cannot be null or empty", fail_test=False
                )
                return []

            if not isinstance(level, int):
                self.exceptions.raise_generic_exception("level must be an integer", fail_test=False)
                return []

            json_dict = self.get_dict(json_data)

            def search_at_level(
                data: Any, search_key: str, current_level: int, target_level: int
            ) -> List[Any]:
                results = []

                if isinstance(data, dict):
                    for k, v in data.items():
                        if k == search_key and current_level == target_level:
                            results.append(v)

                        if isinstance(v, (dict, list)) and current_level < target_level:
                            results.extend(
                                search_at_level(v, search_key, current_level + 1, target_level)
                            )
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, (dict, list)):
                            results.extend(
                                search_at_level(item, search_key, current_level, target_level)
                            )

                return results

            return search_at_level(json_dict, key, 0, level)

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error in level_based_value: {str(e)}", fail_test=False
            )
            return []

    def convert_json_to_xml(self, json_data: Union[str, Dict[str, Any]]) -> str:
        """
        Convert a JSON string/dict to an XML string.

        Args:
            json_data: The JSON string/dict to convert

        Returns:
            The XML string

        Raises:
            ValueError: If the input JSON is invalid

        Examples:
            >>> parser = ParseJsonData()
            >>> xml = parser.convert_json_to_xml({"name": "John", "age": 30})
            >>> "<name>John</name>" in xml and "<age>30</age>" in xml
            True
        """
        try:
            if not json_data:
                self.exceptions.raise_generic_exception(
                    "json_data cannot be null or empty", fail_test=False
                )
                return ""

            json_dict = self.get_dict(json_data)
            xml_str = dicttoxml.dicttoxml(json_dict, custom_root="all", attr_type=False)
            return xml_str.decode()

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error converting JSON to XML: {str(e)}", fail_test=False
            )
            return ""

    def get_all_keys(self, json_data: Union[str, Dict[str, Any]]) -> List[str]:
        """
        Extract all keys from a nested JSON dictionary as a list.

        Args:
            json_data: The JSON data (string or dictionary)

        Returns:
            A list of all keys found in the JSON data

        Raises:
            ValueError: If the input JSON data is invalid

        Examples:
            >>> parser = ParseJsonData()
            >>> keys = parser.get_all_keys({"user": {"name": "John", "age": 30}})
            >>> sorted(keys)
            ['age', 'name', 'user']
        """
        try:
            if not json_data:
                self.exceptions.raise_generic_exception(
                    "json_data cannot be null or empty", fail_test=False
                )
                return []

            json_dict = self.get_dict(json_data)
            return get_all_keys(json_dict)

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error getting all keys: {str(e)}", fail_test=False
            )
            return []

    def get_occurrence_of_key(self, json_data: Union[str, Dict[str, Any]], key: str) -> int:
        """
        Count the occurrences of a key in the JSON data.

        Args:
            json_data: The JSON data (string or dictionary)
            key: The key to count occurrences of

        Returns:
            The number of occurrences of the key

        Raises:
            ValueError: If the input JSON data is invalid or the key is empty

        Examples:
            >>> parser = ParseJsonData()
            >>> data = {"name": "John", "address": {"name": "Home", "street": "Main St"}}
            >>> parser.get_occurrence_of_key(data, "name")
            2
        """
        try:
            if not json_data:
                self.exceptions.raise_generic_exception(
                    "json_data cannot be null or empty", fail_test=False
                )
                return 0

            if not key:
                self.exceptions.raise_generic_exception(
                    "key cannot be null or empty", fail_test=False
                )
                return 0

            json_dict = self.get_dict(json_data)
            return get_occurrence_of_key(json_dict, key)

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error getting occurrence of key: {str(e)}", fail_test=False
            )
            return 0

    def key_exists(self, json_data: Union[str, Dict[str, Any]], key: str) -> bool:
        """
        Check if a key exists in the JSON data.

        Args:
            json_data: The JSON data (string or dictionary)
            key: The key to check for

        Returns:
            True if the key exists, False otherwise

        Raises:
            ValueError: If the input JSON data is invalid or the key is empty

        Examples:
            >>> parser = ParseJsonData()
            >>> data = {"name": "John", "age": 30}
            >>> parser.key_exists(data, "name")
            True
            >>> parser.key_exists(data, "email")
            False
        """
        try:
            if not json_data:
                self.exceptions.raise_generic_exception(
                    "json_data cannot be null or empty", fail_test=False
                )
                return False

            if not key:
                self.exceptions.raise_generic_exception(
                    "key cannot be null or empty", fail_test=False
                )
                return False

            all_keys = self.get_all_keys(json_data)
            return key in all_keys

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error checking if key exists: {str(e)}", fail_test=False
            )
            return False

    def get_multiple_key_value(
        self,
        json_data: Union[str, Dict[str, Any]],
        keys: List[str],
        key_paths: Optional[List[str]] = None,
        delimiter: str = "/",
    ) -> Dict[str, Any]:
        """
        Get values for multiple keys and key paths from the JSON data.

        Args:
            json_data: The JSON data (string or dictionary)
            keys: List of keys for which to fetch values
            key_paths: Optional list of key paths for which to fetch values
            delimiter: The delimiter used in the key paths

        Returns:
            A dictionary mapping keys and key paths to their values

        Raises:
            ValueError: If json_data or keys is null or keys is not a list

        Examples:
            >>> parser = ParseJsonData()
            >>> data = {"user": {"profile": {"name": "John", "age": 30}}}
            >>> results = parser.get_multiple_key_value(
            ...     data, ["user"], key_paths=["user/profile", "user/profile/name"]
            ... )
            >>> "user" in results and "user/profile" in results and "user/profile/name" in results
            True
        """
        try:
            if not json_data:
                self.exceptions.raise_generic_exception(
                    "json_data cannot be null or empty", fail_test=False
                )
                return {}

            if not keys:
                self.exceptions.raise_generic_exception(
                    "keys cannot be null or empty", fail_test=False
                )
                return {}

            if not isinstance(keys, list):
                self.exceptions.raise_generic_exception("keys must be a list", fail_test=False)
                return {}

            result = {}
            json_dict = self.get_dict(json_data)

            # Get values for keys
            for key in keys:
                result[key] = nested_lookup(key, json_dict)

            # Get values for key paths
            if key_paths:
                for key_path in key_paths:
                    try:
                        result[key_path] = self.get_value_of_key_path(
                            json_dict, key_path, delimiter
                        )
                    except Exception as e:
                        self.logger.warning(
                            "Error getting value for key path '%s': %s", key_path, str(e)
                        )
                        result[key_path] = None

            return result

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error getting multiple key values: {str(e)}", fail_test=False
            )
            return {}

    def get_json_result(
        self,
        json_data: Union[str, Dict[str, Any]],
        key: Optional[str] = None,
        nested: bool = False,
        keypath: Optional[str] = None,
        keypath_type: Optional[str] = None,
        key_input: Optional[str] = None,
        delimiter: str = "/",
    ) -> Any:
        """
        Get a value from JSON data based on key or key path.

        This method is a convenience wrapper that provides a unified interface to retrieve
        values using either simple keys or complex key paths.

        Args:
            json_data: The JSON data (string or dictionary)
            key: The key to retrieve the value for (for simple key lookups)
            nested: Whether to search for the key in nested structures (when using key)
            keypath: The path to the key, using the specified delimiter (for path-based lookups)
            keypath_type: Either "absolute" or "relative" (required when using keypath)
            key_input: The specific sub-child key to retrieve the value for (when using relative keypath)
            delimiter: The delimiter used in the key path (default: "/")

        Returns:
            The value associated with the key or key path

        Raises:
            ValueError: If required parameters are missing or invalid

        Examples:
            >>> parser = ParseJsonData()
            >>> data = {"user": {"profile": {"name": "John"}}}
            >>> # Simple key lookup
            >>> parser.get_json_result(data, key="user")
            {'profile': {'name': 'John'}}
            >>> # Nested key lookup
            >>> parser.get_json_result(data, key="name", nested=True)
            ['John']
            >>> # Absolute key path lookup
            >>> parser.get_json_result(
            ...     data,
            ...     keypath="user/profile/name",
            ...     keypath_type="absolute"
            ... )
            'John'
            >>> # Relative key path lookup
            >>> parser.get_json_result(
            ...     data,
            ...     keypath="user/profile",
            ...     keypath_type="relative",
            ...     key_input="name"
            ... )
            'John'
        """
        try:
            if not json_data:
                self.exceptions.raise_generic_exception(
                    "json_data cannot be null or empty", fail_test=False
                )
                return None

            # Simple key lookup
            if key is not None:
                return self.get_value_of_key(json_data, key, nested)

            # Key path lookup
            if keypath is not None:
                if not keypath_type:
                    self.exceptions.raise_generic_exception(
                        "keypath_type is required when using keypath", fail_test=False
                    )
                    return None

                return self.get_value_from_key_path(
                    json_data=json_data,
                    key_path=keypath,
                    key_path_type=keypath_type,
                    key=key_input,
                    delimiter=delimiter,
                )

            self.exceptions.raise_generic_exception(
                "Either key or keypath must be provided", fail_test=False
            )
            return None

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error in get_json_result: {str(e)}", fail_test=False
            )
            return None

    def update_json_based_on_key(
        self, json_data: Union[str, Dict[str, Any]], key: str, updated_value: Any
    ) -> Dict[str, Any]:
        """
        Update all occurrences of a key in the JSON data with a new value.

        Args:
            json_data: The JSON data (string or dictionary)
            key: The key to update
            updated_value: The new value for the key

        Returns:
            The updated JSON dictionary
            The same JSON dictionary if key is empty or key doesn't exist in the JSON data

        Raises:
            ValueError: If json_data is invalid

        Examples:
            >>> parser = ParseJsonData()
            >>> data = {"name": "John", "user": {"name": "John"}}
            >>> updated = parser.update_json_based_on_key(data, "name", "Jane")
            >>> updated["name"] == "Jane" and updated["user"]["name"] == "Jane"
            True
        """
        try:
            if not json_data:
                self.exceptions.raise_generic_exception(
                    "json_data cannot be null or empty", fail_test=False
                )
                return {}

            json_dict = self.get_dict(json_data)

            if not key:
                self.exceptions.raise_generic_exception(
                    "key cannot be null or empty", fail_test=False
                )
                return json_dict

            if not self.key_exists(json_dict, key):
                self.exceptions.raise_generic_exception(
                    f"Key '{key}' not found in JSON data", fail_test=False
                )
                return json_dict

            return nested_update(json_dict, key, updated_value)

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error updating JSON based on key: {str(e)}", fail_test=False
            )
            return self.get_dict(json_data)

    def update_json_based_on_parent_child_key(
        self,
        json_data: Union[str, Dict[str, Any]],
        parent_key: str,
        child_key: str,
        updated_value: Any,
    ) -> Dict[str, Any]:
        """
        Update a specific child key within a parent key in the JSON data.

        Args:
            json_data: The JSON data (string or dictionary)
            parent_key: The parent key
            child_key: The child key to update
            updated_value: The new value for the child key

        Returns:
            The updated JSON dictionary
            The same JSON dictionary if parent_key or child_key is empty or doesn't exist

        Raises:
            ValueError: If json_data is invalid

        Examples:
            >>> parser = ParseJsonData()
            >>> data = {"user": {"name": "John", "age": 30}}
            >>> updated = parser.update_json_based_on_parent_child_key(
            ...     data, "user", "name", "Jane"
            ... )
            >>> updated["user"]["name"]
            'Jane'
        """
        try:
            if not json_data:
                self.exceptions.raise_generic_exception(
                    "json_data cannot be null or empty", fail_test=False
                )
                return {}

            json_dict = self.get_dict(json_data)

            if not parent_key:
                self.exceptions.raise_generic_exception(
                    "parent_key cannot be null or empty", fail_test=False
                )
                return json_dict

            if not child_key:
                self.exceptions.raise_generic_exception(
                    "child_key cannot be null or empty", fail_test=False
                )
                return json_dict

            if not self.key_exists(json_dict, parent_key):
                self.exceptions.raise_generic_exception(
                    f"Parent key '{parent_key}' not found in JSON data", fail_test=False
                )
                return json_dict

            if not self.key_exists(json_dict, child_key):
                self.exceptions.raise_generic_exception(
                    f"Child key '{child_key}' not found in JSON data", fail_test=False
                )
                return json_dict

            # Combine parent and child keys using the special format for __parse_json_with_parent_key
            combined_key = f"{parent_key}->{child_key}"

            global bln_flag, bln_parent_key_status, bln_child_key_status, int_node_counter
            bln_flag = True
            bln_parent_key_status = False
            bln_child_key_status = False
            int_node_counter = 1

            return self.__parse_json_with_parent_key([combined_key], [updated_value], json_dict)

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error updating JSON based on parent-child key: {str(e)}", fail_test=False
            )
            return self.get_dict(json_data)

    def update_json_based_on_parent_child_key_index(
        self,
        json_data: Union[str, Dict[str, Any]],
        parent_key: str,
        child_key: str,
        index: str,
        updated_value: Any,
    ) -> Dict[str, Any]:
        """
        Update a specific child key at a given index within a parent key in the JSON data.

        Args:
            json_data: The JSON data (string or dictionary)
            parent_key: The parent key
            child_key: The child key to update
            index: The index of the child key if multiple instances exist
            updated_value: The new value for the child key

        Returns:
            The updated JSON dictionary
            The same JSON dictionary if parent_key or child_key is empty or doesn't exist
            The same JSON dictionary if index is empty

        Raises:
            ValueError: If json_data is invalid

        Examples:
            >>> parser = ParseJsonData()
            >>> data = {"users": [{"name": "John"}, {"name": "Jane"}]}
            >>> updated = parser.update_json_based_on_parent_child_key_index(
            ...     data, "users", "name", "2", "Jane Doe"
            ... )
            >>> updated["users"][1]["name"]  # Index 2 points to the second element (0-indexed)
            'Jane Doe'
        """
        try:
            if not json_data:
                self.exceptions.raise_generic_exception(
                    "json_data cannot be null or empty", fail_test=False
                )
                return {}

            json_dict = self.get_dict(json_data)

            if not parent_key:
                self.exceptions.raise_generic_exception(
                    "parent_key cannot be null or empty", fail_test=False
                )
                return json_dict

            if not child_key:
                self.exceptions.raise_generic_exception(
                    "child_key cannot be null or empty", fail_test=False
                )
                return json_dict

            if not index:
                self.exceptions.raise_generic_exception(
                    "index cannot be null or empty", fail_test=False
                )
                return json_dict

            if not self.key_exists(json_dict, parent_key):
                self.exceptions.raise_generic_exception(
                    f"Parent key '{parent_key}' not found in JSON data", fail_test=False
                )
                return json_dict

            if not self.key_exists(json_dict, child_key):
                self.exceptions.raise_generic_exception(
                    f"Child key '{child_key}' not found in JSON data", fail_test=False
                )
                return json_dict

            # Combine parent, child keys, and index using the special format for __parse_json_with_parent_key
            combined_key = f"{parent_key}->{child_key}${index}"

            global bln_flag, bln_parent_key_status, bln_child_key_status, int_node_counter
            bln_flag = True
            bln_parent_key_status = False
            bln_child_key_status = False
            int_node_counter = 1

            return self.__parse_json_with_parent_key([combined_key], [updated_value], json_dict)

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error updating JSON based on parent-child key with index: {str(e)}",
                fail_test=False,
            )
            return self.get_dict(json_data)

    def __update_portion_json(self, json_data: Any, key: str, value: Any) -> Any:
        """
        Update a portion of the JSON data based on the specified key and value.

        Args:
            json_data: The JSON data to update
            key: The key to update, possibly with an index
            value: The new value for the key

        Returns:
            The updated JSON data

        Note:
            This is an internal helper method used by update_json_based_on_parent_child_key
            and update_json_based_on_parent_child_key_index.
        """
        try:
            if not json_data:
                self.exceptions.raise_generic_exception("json_data cannot be null", fail_test=False)
                return json_data

            if not key:
                self.exceptions.raise_generic_exception("key cannot be null", fail_test=False)
                return json_data

            global bln_child_key_status, int_node_counter

            # Split the key if it contains an index
            key_parts = key.split("$")
            target_key = key_parts[0]
            target_index = int(key_parts[1]) if len(key_parts) > 1 else None

            if isinstance(json_data, dict):
                for json_key, json_value in json_data.items():
                    if target_key == json_key:
                        if target_index is not None and int_node_counter == target_index:
                            # Update value at the specified index
                            json_data[json_key] = value
                            bln_child_key_status = True
                        elif target_index is None:
                            # Update all occurrences if no index is specified
                            json_data[json_key] = value
                            bln_child_key_status = True

                        int_node_counter += 1
                    elif isinstance(json_value, (dict, list)):
                        # Recursively update nested structures
                        self.__update_portion_json(json_value, key, value)
            elif isinstance(json_data, list):
                for item in json_data:
                    if isinstance(item, (dict, list)):
                        # Recursively update items in the list
                        self.__update_portion_json(item, key, value)

            return json_data

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error in __update_portion_json: {str(e)}", fail_test=False
            )
            return json_data

    def __parse_update_json(self, json_data: Any, keys: List[str], value: Any) -> Any:
        """
        Parse and update the JSON data based on the specified keys and value.

        Args:
            json_data: The JSON data to update
            keys: The list of keys representing the path to the target key
            value: The new value for the target key

        Returns:
            The updated JSON data

        Note:
            This is an internal helper method used by __parse_json_with_parent_key.
        """
        try:
            global int_keys_counter, bln_flag, bln_parent_key_status

            if bln_flag:
                if isinstance(json_data, dict):
                    for json_key, json_value in json_data.items():
                        if keys[int_keys_counter - 1] == json_key:
                            # Found the parent key, now look for the child key
                            self.__update_portion_json(json_value, keys[int_keys_counter], value)
                            bln_parent_key_status = True
                            bln_flag = False
                            break
                        if isinstance(json_value, (dict, list)):
                            # Recursively search for the parent key
                            self.__parse_update_json(json_value, keys, value)
                elif isinstance(json_data, list):
                    for item in json_data:
                        if isinstance(item, (dict, list)):
                            # Recursively search for the parent key in list items
                            self.__parse_update_json(item, keys, value)

            return json_data

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error in __parse_update_json: {str(e)}", fail_test=False
            )
            return json_data

    def __parse_json_with_parent_key(
        self, keys: List[str], values: List[Any], json_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse and update the JSON data based on the specified parent-child keys and values.

        Args:
            keys: The list of parent-child keys
            values: The list of new values corresponding to the keys
            json_data: The JSON data to update

        Returns:
            The updated JSON data

        Note:
            This is an internal helper method used by update_json_based_on_parent_child_key
            and update_json_based_on_parent_child_key_index.
        """
        try:
            if len(keys) != len(values):
                self.exceptions.raise_generic_exception(
                    "Number of keys and values must be the same", fail_test=False
                )
                return json_data

            global bln_flag, bln_parent_key_status, bln_child_key_status, int_node_counter, int_keys_counter

            for i, key in enumerate(keys):
                # Split the key into parent and child parts
                key_parts = key.split("->")

                bln_flag = True
                bln_parent_key_status = False
                bln_child_key_status = False
                int_node_counter = 1
                int_keys_counter = 1

                # Update the JSON data with the current key-value pair
                json_data = self.__parse_update_json(json_data, key_parts, values[i])

                if not bln_parent_key_status or not bln_child_key_status:
                    self.exceptions.raise_generic_exception(
                        f"Key '{key}' not found in JSON data", fail_test=False
                    )
                    return json_data

            return json_data

        except Exception as e:
            self.exceptions.raise_generic_exception(
                f"Error in __parse_json_with_parent_key: {str(e)}", fail_test=False
            )
            return json_data
