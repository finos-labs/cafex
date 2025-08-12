import json
from typing import Any

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.parsers.json_parser import ParseJsonData


class ResponseParserJSON:
    """
    Description:
        Json is the response for most of the REST API requests give.
        This class provides few methods which parse and get the required details.

    """

    def __init__(self):
        self.logger = CoreLogger(name=__name__).get_logger()

    def get_key_value(self, **kwargs) -> Any:
        """Extracts the value(s) of thr key from the JSON data, optionally
        searching nested structures.

        Kwargs:
            json: The JSON data (string or dictionary).
            key: The key to retrieve the value for.
            nested: Whether to search for the key in nested structures (default: False).

        Returns:
            The value associated with the key
            The list of values if nested is True and multiple keys are found.

        Raises:
            ValueError: If required arguments are missing or invalid.
            json.JSONDecodeError: If the JSON data is invalid.

        Examples:
            # gets the first key Item. no nested search
            response_parser.get_key_value(json=dict_response, key=item)
            # searches nested keys and gets all the lists
            self.response_parser.get_key_value(json=dict_response, key=item, nested=True)
        """
        try:
            if "json" not in kwargs:
                self.logger.info("No 'json' parameter Passed")
                raise ValueError("'json' parameter is required.")
            if "key" not in kwargs:
                self.logger.info("No 'key' parameter Passed")
                raise ValueError("'key' parameter is required.")

            json_data = kwargs.get("json")
            key = kwargs.get("key")
            nested = kwargs.get("nested", False)

            if not json_data:
                raise ValueError("The 'json_data' parameter cannot be null or empty.")
            if not key:
                raise ValueError("The 'key' parameter cannot be null or empty.")
            if not isinstance(nested, bool):
                raise ValueError("The 'nested' parameter must be a boolean")

            obj_parse_data = ParseJsonData()
            return obj_parse_data.get_value_of_key(json_data, key, nested)
        except Exception as e:
            self.logger.exception("Error in extracting the value(s) of the specified key: %s", e)
            raise e

    def compare_json(
        self,
        expected_json: str | dict,
        actual_json: str | dict,
        ignore_keys: list[str] | None = None,
        ignore_extra: bool = False,
    ) -> bool | tuple[bool, list[str]]:
        """Compares two JSON structures (strings or dictionaries).

        Args:
            expected_json: The expected JSON data (string or dictionary).
            actual_json: The actual JSON data (string or dictionary).
            ignore_keys: A list of keys to ignore during comparison (default: None).
            ignore_extra: Whether to ignore extra keys in actual_json (default: False).

        Returns:
            True if the JSON structures are equal (considering ignore_keys and ignore_extra),
            otherwise a tuple containing False and a list of mismatches.

        Raises:
            ValueError: If the input JSON data is invalid.

        Examples:
            # Comparing two JSON strings
            result = compare_json('{"a": 1, "b": 2}', '{"a": 1, "b": 2}')
            assert result is True

            # Comparing two dictionaries
            result = compare_json({"a": 1, "b": 2}, {"a": 1, "b": 2})
            assert result is True

            # Ignoring specific keys
            result = compare_json('{"a": 1, "b": 2}', '{"a": 1, "b": 3}', ignore_keys=["b"])
            assert result is True

            # Ignoring extra keys
            result = compare_json('{"a": 1}', '{"a": 1, "b": 2}', ignore_extra=True)
            assert result is True

            # Mismatch example
            result = compare_json('{"c": 1}', '{"c": 2}')
            assert result == (False, ["Expected value for c is 1 but found 2"])
        """
        try:
            if not expected_json:
                raise ValueError("expected_json cannot be null or empty.")
            if not actual_json:
                raise ValueError("actual_json cannot be null or empty.")

            if ignore_keys is None:
                ignore_keys = []
            elif not isinstance(ignore_keys, list):
                raise TypeError("ignore_keys must be a list.")

            if not isinstance(ignore_extra, bool):
                raise TypeError("ignore_extra must be a boolean.")

            obj_parse_data = ParseJsonData()
            result = obj_parse_data.compare_json(
                expected_json, actual_json, ignore_keys, ignore_extra
            )
            return result

        except (ValueError, json.JSONDecodeError) as e:
            self.logger.exception("Error in comparing two JSON structures: %s", e)
            raise ValueError(f"Error comparing JSON objects: {e}") from e

    def convert_json_to_xml(self, pjson: str | dict) -> str:
        """Converts a JSON string/dict to an XML string.

        Args:
            pjson: The JSON string/dict to convert.

        Returns:
            The XML string.

        Raises:
            ValueError: If the input JSON is invalid.
        """
        if not pjson:
            raise ValueError("pjson cannot be null or empty.")
        try:
            obj_parse_data = ParseJsonData()
            return obj_parse_data.convert_json_to_xml(pjson)
        except Exception as e:
            self.logger.exception("Error in provided json to xml: %s", e)
            raise e

    def get_all_keys(self, pjson: str | dict) -> list[str]:
        """Extracts all keys from a nested JSON dictionary as a list.

        Args:
            pjson: The JSON data (string or dictionary).

        Returns:
            A list of all keys found in the JSON data.

        Raises:
            ValueError: If the input JSON data is invalid
        """
        if not pjson:
            raise ValueError("pjson cannot be null or empty.")
        try:
            obj_parse_data = ParseJsonData()
            return obj_parse_data.get_all_keys(pjson)
        except Exception as e:
            self.logger.exception("Error in extracting keys from a nested JSON dictionary: %s", e)
            raise e

    def key_exists(self, json_data: str | dict, key: str) -> bool:
        """Checks if a key exists in the JSON data.

        Args:
            json_data: The JSON data (string or dictionary).
            key: The key to check for.

        Returns:
            True if the key exists, False otherwise.

        Raises:
            ValueError: If the input JSON data is invalid or the key is empty.
        """
        if not json_data:
            raise ValueError("json_data cannot be empty.")
        if not key:
            raise ValueError("key cannot be empty.")
        try:
            obj_parse_data = ParseJsonData()
            return obj_parse_data.key_exists(json_data, key)
        except Exception as e:
            self.logger.exception("Error in checking if key exists in the JSON data: %s", e)
            raise e

    def get_occurrence_of_key(self, json_data: str | dict, key: str) -> int:
        """Counts the occurrences of a key in the JSON data.

        Args:
            json_data: The JSON data (string or dictionary).
            key: The key to count occurrences of.

        Returns:
            The number of occurrences of the key.

        Raises:
            ValueError: If the input JSON data is invalid or the key is empty.
        """
        if not json_data:
            raise ValueError("json_data cannot be empty.")
        if not key:
            raise ValueError("key cannot be empty.")
        try:
            obj_parse_data = ParseJsonData()
            return obj_parse_data.get_occurrence_of_key(json_data, key)
        except Exception as e:
            self.logger.exception("Error in finding occurrences of a key in the JSON data: %s", e)
            raise e

    def get_key_path_value(self, **kwargs: Any) -> Any:
        """Extracts the value at the specified key path from the JSON data.

        Kwargs:
            json: The JSON data (string or dictionary).
            keyPath: The path to the key, using the specified delimiter.
            keyPathType: Either "absolute" or "relative" (default: "absolute").
            delimiter: The delimiter used in the key path (default: "/").
            key: The key to retrieve the value for when using relative key paths.

        Returns:
            The value associated with the key path.

        Raises:
            ValueError: If required arguments are missing, invalid, or the key path is not found.
            json.JSONDecodeError: If the JSON data is invalid.

        Examples:
            get_key_path_value(json='json data',
                               keyPath='node1/node2/key',
                               keyPathType='absolute')
            get_key_path_value(json='json data',
                               keyPath='node1/node2',
                               keyPathType='relative',
                               key='key')
        """
        try:
            if "json" not in kwargs:
                self.logger.info("No json argument provided")
                raise ValueError("json argument is required.")
            if "keyPath" not in kwargs:
                self.logger.info("No keyPath argument provided")
                raise ValueError("keyPath argument is required.")
            if "keyPathType" not in kwargs:
                self.logger.info("No keyPathType argument provided")
                raise ValueError("keyPathType argument is required.")
            obj_parse_data = ParseJsonData()
            return obj_parse_data.get_value_from_key_path(**kwargs)
        except Exception as e:
            self.logger.exception("Error in extracting the value at the specified key path: %s", e)
            raise e
