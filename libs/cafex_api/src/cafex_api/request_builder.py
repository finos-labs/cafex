"""
Module providing request building and API interaction capabilities for the CAFEX framework.

This module provides a robust RequestBuilder class with methods to construct and manipulate URIs,
handle headers, manage payloads, and execute HTTP requests. It supports various HTTP methods and
provides utilities for URL manipulation.
"""

import gzip
import json
import re
from typing import Any, Dict, Optional, Tuple, Union
from urllib.parse import (
    parse_qsl,
    quote,
    unquote,
    urlencode,
    urljoin,
    urlparse,
    urlsplit,
    urlunparse,
)

import requests
import yaml
from requests.cookies import RequestsCookieJar
from requests.structures import CaseInsensitiveDict

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.utils.core_security import Security
from cafex_core.utils.exceptions import CoreExceptions

from .api_exceptions import APIExceptions


class RequestBuilder:
    """
    A comprehensive request builder for API testing and interaction.

    This class provides methods to build and manipulate URIs, handle headers and payloads, and
    execute HTTP requests with various options. It includes functionality for parameter encoding,
    URL manipulation, and response analysis.
    """

    def __init__(self):
        """Initialize the RequestBuilder with logging and exception handling."""
        self.logger = CoreLogger(name=__name__).get_logger()
        self.security = Security()
        self.__exceptions_generic = CoreExceptions()
        self.__exceptions_services = APIExceptions()

    def get_base_url_from_uri(self, url: str) -> Optional[str]:
        """
        Extract the base URL from a URI.

        Extracts the scheme and domain part of a URL, removing paths and query parameters.

        Args:
            url: The URL string to extract the base from

        Returns:
            The base URL (scheme + domain) or None if extraction fails

        Examples:
            >>> builder = RequestBuilder()
            >>> builder.get_base_url_from_uri("https://www.example.com/api/users?id=123")
            'https://www.example.com'
            >>> builder.get_base_url_from_uri("https://api.service.org/v1/data")
            'https://api.service.org'
        """
        try:
            if not url:
                self.__exceptions_services.raise_null_value("URL cannot be null", fail_test=False)
                return None

            dict_url_parts = urlsplit(url)
            if not dict_url_parts.scheme:
                self.__exceptions_services.raise_null_value(
                    f"URL {url} must have a scheme (http or https)", fail_test=False
                )
                return None

            if not dict_url_parts.path:
                self.__exceptions_services.raise_null_value(
                    f"URL {url} must have a path", fail_test=False
                )
                return None

            str_base_url = dict_url_parts.scheme + "://" + dict_url_parts.netloc
            return str_base_url
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error in fetching base URL: {str(e)}", fail_test=False
            )
            return None

    def generate_headers_from_string(
        self, header_string: str, headers_delimiter: str = ",", values_delimiter: str = ":"
    ) -> Dict[str, str]:
        """
        Convert a header string into a dictionary.

        Parses a string of headers into a dictionary format suitable for HTTP requests.

        Args:
            header_string: The header string (e.g., "Content-Type: application/json")
            headers_delimiter: Delimiter between headers (default: ",")
            values_delimiter: Delimiter between key and value (default: ":")

        Returns:
            A dictionary of headers with keys and values, or empty dict if parsing fails

        Examples:
            >>> builder = RequestBuilder()
            >>> builder.generate_headers_from_string("Content-Type: application/json, Auth: token123")
            {'Content-Type': 'application/json', 'Auth': 'token123'}
            >>> builder.generate_headers_from_string("Accept: text/html|Cache-Control: no-cache", "|", ":")
            {'Accept': 'text/html', 'Cache-Control': 'no-cache'}
        """
        try:
            if not header_string:
                self.__exceptions_services.raise_null_value(
                    "Header string cannot be null", fail_test=False
                )
                return {}

            if headers_delimiter == values_delimiter:
                self.__exceptions_services.raise_invalid_value(
                    "Header and value delimiters must be different", fail_test=False
                )
                return {}

            headers = {}
            for header in header_string.replace("\\'", "").split(headers_delimiter):
                if len(header.split(values_delimiter)) == 2:
                    key, value = header.split(values_delimiter, 1)
                    headers[key.strip()] = value.strip()
                else:
                    self.__exceptions_services.raise_invalid_value(
                        f"Incorrect delimiter ({headers_delimiter}) used between Header Key and Value",
                        fail_test=False,
                    )
                    return {}

            return headers
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error in generating headers: {str(e)}", fail_test=False
            )
            return {}

    def add_path_parameters(
        self, url: str, path_parameters: str, encode: bool = False, replace_params: bool = False
    ) -> Optional[str]:
        """
        Add path parameters to a base URL.

        Adds path components to a URL, with options for encoding and replacement.

        Args:
            url: The base URL
            path_parameters: The path parameters to add
            encode: Whether to encode the parameters
            replace_params: Whether to replace existing parameters

        Returns:
            The URL with path parameters added, or None if operation fails

        Examples:
            >>> builder = RequestBuilder()
            >>> # Add path keeping existing structure
            >>> builder.add_path_parameters("https://api.example.com", "users/123")
            'https://api.example.com/users/123'
            >>> # Replace existing path
            >>> builder.add_path_parameters("https://api.example.com/v1", "users/123", replace_params=True)
            'https://api.example.com/users/123'
            >>> # Add with encoding
            >>> builder.add_path_parameters("https://api.example.com", "users/John Doe", encode=True)
            'https://api.example.com/users/John%20Doe'
        """
        try:
            if not url:
                self.__exceptions_services.raise_null_value("URL cannot be null", fail_test=False)
                return None

            if not isinstance(replace_params, bool):
                self.__exceptions_services.raise_invalid_value(
                    "replace_params must be a boolean", fail_test=False
                )
                return None

            if not isinstance(encode, bool):
                self.__exceptions_services.raise_invalid_value(
                    "encode must be a boolean", fail_test=False
                )
                return None

            # Parse URL to separate base and path
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

            # Handle path parameters
            if replace_params:
                # Handle trailing slash in base_url
                if base_url.endswith("/"):
                    base_url = base_url[:-1]

                # If path_parameters doesn't start with slash, add it
                if not path_parameters.startswith("/"):
                    path_parameters = "/" + path_parameters

                # For true replacement behavior, ignore existing path
                path = path_parameters
            else:
                # Get existing path
                path = parsed_url.path

                # Ensure path has trailing slash for joining
                if not path.endswith("/"):
                    path = path + "/"

                # Remove leading slash from path_parameters if present
                if path_parameters.startswith("/"):
                    path_parameters = path_parameters[1:]

                # Join paths
                path = path + path_parameters

            # Encode if requested
            if encode:
                # Only encode the new portion, not the whole path
                path = path.replace(" ", "%20")

            result = base_url + path

            self.logger.info("URL with parameters is: %s", result)
            return result
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error in adding path parameters to the base URL: {str(e)}", fail_test=False
            )
            return None

    def overwrite_path_parameters(
        self,
        url: str,
        current_params: str,
        new_params: str,
        delimiter: str = ",",
        encode: bool = False,
    ) -> Optional[str]:
        """
        Overwrite path parameters in a URI.

        Replaces specific path components in a URL with new values.

        Args:
            url: The URL with path parameters
            current_params: The current path parameters (delimiter-separated)
            new_params: The new path parameters (delimiter-separated)
            delimiter: The delimiter used to separate parameters
            encode: Whether to encode the parameters

        Returns:
            The URL with overwritten path parameters, or None if operation fails

        Examples:
            >>> builder = RequestBuilder()
            >>> # Replace path parameters
            >>> builder.overwrite_path_parameters(
            ...     "https://www.example.com/param1/param2",
            ...     "param1,param2",
            ...     "param11,param22"
            ... )
            'https://www.example.com/param11/param22'
            >>> # Replace single parameter
            >>> builder.overwrite_path_parameters(
            ...     "https://www.example.com/param1/param2",
            ...     "param2",
            ...     "param22"
            ... )
            'https://www.example.com/param1/param22'
            >>> # Custom delimiter
            >>> builder.overwrite_path_parameters(
            ...     "https://www.example.com/param1/param2",
            ...     "param1#param2",
            ...     "param11#param22",
            ...     delimiter='#'
            ... )
            'https://www.example.com/param11/param22'
        """
        try:
            if not url:
                self.__exceptions_services.raise_null_value("URL cannot be null", fail_test=False)
                return None

            if not current_params:
                self.__exceptions_services.raise_null_value(
                    "Current path parameters cannot be null", fail_test=False
                )
                return None

            current_params_list = current_params.split(delimiter)
            new_params_list = new_params.split(delimiter)

            if len(current_params_list) != len(new_params_list):
                self.__exceptions_services.raise_invalid_value(
                    "Current and new path parameters must have the same number of parameters",
                    fail_test=False,
                )
                return None

            for i, param in enumerate(current_params_list):
                if f"/{param}" not in url:
                    self.__exceptions_services.raise_invalid_value(
                        f"Parameter {param} isn't present in URL {url}", fail_test=False
                    )
                    return None

            for i, param in enumerate(current_params_list):
                url = re.sub(f"/{param}/", f"/{new_params_list[i]}/", url)
                url = re.sub(f"/{param}$", f"/{new_params_list[i]}", url)

            base_url = self.get_base_url_from_uri(url)
            if not base_url:
                return None

            path_params = self.fetch_path_parameters_from_url(url)
            if not path_params:
                return None

            encoded_params = quote(path_params) if encode else path_params

            url_with_params = urljoin(base_url, encoded_params)
            self.logger.info("URL with parameters is: %s", url_with_params)
            return url_with_params
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error in overwriting path parameters: {str(e)}", fail_test=False
            )
            return None

    def add_query_parameters(
        self, url: str, params: Dict[str, Any], encode: bool = False
    ) -> Optional[str]:
        """
        Add query parameters to a URL.

        Appends or updates query parameters in a URL.

        Args:
            url: The base URL
            params: A dictionary of query parameters
            encode: Whether to encode the parameters

        Returns:
            The URL with query parameters added, or None if operation fails

        Examples:
            >>> builder = RequestBuilder()
            >>> # Add parameters to URL without existing parameters
            >>> builder.add_query_parameters(
            ...     "https://www.example.com/api",
            ...     {"page": "1", "limit": "10"}
            ... )
            'https://www.example.com/api?page=1&limit=10'
            >>> # Add parameters to URL with existing parameters
            >>> builder.add_query_parameters(
            ...     "https://www.example.com/api?format=json",
            ...     {"page": "1", "limit": "10"}
            ... )
            'https://www.example.com/api?format=json&page=1&limit=10'
            >>> # Add with encoding
            >>> builder.add_query_parameters(
            ...     "https://www.example.com/search",
            ...     {"q": "test query", "lang": "en"},
            ...     encode=True
            ... )
            'https://www.example.com/search?q=test%20query&lang=en'
        """
        try:
            if not url:
                self.__exceptions_services.raise_null_value("URL cannot be null", fail_test=False)
                return None

            if not isinstance(encode, bool):
                self.__exceptions_services.raise_invalid_value(
                    "encode must be a boolean", fail_test=False
                )
                return None

            if not isinstance(params, dict):
                self.__exceptions_services.raise_invalid_value(
                    "Query parameters must be a dictionary", fail_test=False
                )
                return None

            parsed_url = urlparse(url)
            current_params = dict(parse_qsl(parsed_url.query))
            current_params.update(params)

            if not encode:
                query_string = unquote(urlencode(current_params))
            else:
                query_string = urlencode(current_params).replace("+", "%20")

            url_parts = list(parsed_url)
            url_parts[4] = query_string
            url_with_params = urlunparse(url_parts)
            return url_with_params
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error in adding query parameters to the base URL: {str(e)}", fail_test=False
            )
            return None

    def fetch_path_parameters_from_url(self, url: str) -> Optional[str]:
        """
        Extract the path parameters from a URL.

        Gets the path component from a URL, excluding domain and query parameters.

        Args:
            url: The URL string

        Returns:
            The path parameters/endpoint, or None if extraction fails

        Examples:
            >>> builder = RequestBuilder()
            >>> builder.fetch_path_parameters_from_url("https://www.example.com/api/users/123")
            '/api/users/123'
            >>> builder.fetch_path_parameters_from_url("https://api.service.com/v1/data?format=json")
            '/v1/data'
        """
        try:
            if not url:
                self.__exceptions_services.raise_null_value("URL cannot be null", fail_test=False)
                return None

            parsed_url = urlparse(url)
            str_path_params = parsed_url[2]  # This fetches path parameters from a URL
            return str_path_params
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error in fetching path parameters from URL: {str(e)}", fail_test=False
            )
            return None

    def fetch_query_parameters_from_url(
        self, url: str, return_type: str = "text"
    ) -> Union[str, Dict[str, str], None]:
        """
        Extract query parameters from a URL.

        Gets the query parameters from a URL, returning them as text or dictionary.

        Args:
            url: The URL to extract query parameters from
            return_type: The desired return type ("text" or "dict")

        Returns:
            The query parameters as a string or dictionary, or None if extraction fails

        Examples:
            >>> builder = RequestBuilder()
            >>> # Get parameters as text
            >>> builder.fetch_query_parameters_from_url(
            ...     "https://www.example.com/api?page=1&limit=10"
            ... )
            'page=1&limit=10'
            >>> # Get parameters as dictionary
            >>> builder.fetch_query_parameters_from_url(
            ...     "https://www.example.com/api?page=1&limit=10",
            ...     return_type="dict"
            ... )
            {'page': '1', 'limit': '10'}
        """
        try:
            if not url:
                self.__exceptions_services.raise_null_value("URL cannot be null", fail_test=False)
                return None

            return_type = return_type.lower()
            if return_type not in ("text", "dict"):
                self.__exceptions_services.raise_invalid_value(
                    f"Invalid return type: {return_type}. Valid options are: text and dict",
                    fail_test=False,
                )
                return None

            parsed_uri = urlparse(url)
            if return_type == "text":
                return urlencode(parse_qsl(parsed_uri.query))
            if return_type == "dict":
                return dict(parse_qsl(parsed_uri.query))
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error in fetching query parameters from URL: {str(e)}", fail_test=False
            )
            return None if return_type == "dict" else ""

    def modify_payload(
        self,
        template_payload: Union[str, Dict[str, Any]],
        payload_to_modify: Union[str, Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """
        Add, update, or modify a JSON payload.

        Combines two JSON payloads, with the second overriding any duplicate keys.

        Args:
            template_payload: The base payload (JSON string or dictionary)
            payload_to_modify: The modifications to apply (JSON string or dictionary)

        Returns:
            The modified payload as a dictionary, or None if operation fails

        Examples:
            >>> builder = RequestBuilder()
            >>> # Combine payloads
            >>> builder.modify_payload(
            ...     '{"name":"SPG","year":"1900"}',
            ...     '{"HQ":"New York"}'
            ... )
            {'name': 'SPG', 'year': '1900', 'HQ': 'New York'}
            >>> # Override value
            >>> builder.modify_payload(
            ...     '{"name":"SPG","year":"1900"}',
            ...     '{"HQ":"New York", "year":"2000"}'
            ... )
            {'name': 'SPG', 'year': '2000', 'HQ': 'New York'}
        """
        try:
            if isinstance(template_payload, str):
                template_payload = json.loads(template_payload)
            if not isinstance(template_payload, dict):
                self.__exceptions_services.raise_invalid_value(
                    "template_payload must be a JSON string or dictionary.", fail_test=False
                )
                return None

            if isinstance(payload_to_modify, str):
                payload_to_modify = json.loads(payload_to_modify)
            if not isinstance(payload_to_modify, dict):
                self.__exceptions_services.raise_invalid_value(
                    "payload_to_modify must be a JSON string or dictionary.", fail_test=False
                )
                return None

            final_payload = template_payload.copy()
            final_payload.update(payload_to_modify)

            return final_payload
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error in modifying payload: {str(e)}", fail_test=False
            )
            return None

    def get_value_from_yaml(self, file_path: str, key: str) -> Optional[Any]:
        """
        Fetch a value from a YAML file by key.

        Reads a YAML file and returns the value for the specified key.

        Args:
            file_path: The path to the YAML file
            key: The key to retrieve the value for

        Returns:
            The value associated with the key in the YAML file, or None if operation fails

        Examples:
            >>> # Given a YAML file "config.yml" with content:
            >>> # api_url: https://api.example.com
            >>> # timeout: 30
            >>> builder = RequestBuilder()
            >>> builder.get_value_from_yaml("config.yml", "api_url")
            'https://api.example.com'
            >>> builder.get_value_from_yaml("config.yml", "timeout")
            30
        """
        try:
            if not key:
                self.__exceptions_services.raise_null_value("key cannot be null", fail_test=False)
                return None

            with open(file_path, "r", encoding="utf-8") as yaml_file:
                yaml_data = yaml.safe_load(yaml_file)
                return yaml_data[key]

        except FileNotFoundError:
            self.__exceptions_services.raise_file_not_found(file_path, fail_test=False)
            return None
        except KeyError:
            self.__exceptions_services.raise_missing_required_field(key, fail_test=False)
            return None
        except yaml.YAMLError as e:
            self.__exceptions_services.raise_invalid_value(
                f"Invalid YAML in file '{file_path}': {e}", fail_test=False
            )
            return None
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error reading YAML file: {str(e)}", fail_test=False
            )
            return None

    def get_value_from_json(self, file_path: str, key: str) -> Optional[Any]:
        """
        Fetch a value from a JSON file by key.

        Reads a JSON file and returns the value for the specified key.

        Args:
            file_path: The path to the JSON file
            key: The key to retrieve the value for

        Returns:
            The value associated with the key in the JSON file, or None if operation fails

        Examples:
            >>> # Given a JSON file "config.json" with content:
            >>> # {"api_url": "https://api.example.com", "timeout": 30}
            >>> builder = RequestBuilder()
            >>> builder.get_value_from_json("config.json", "api_url")
            'https://api.example.com'
            >>> builder.get_value_from_json("config.json", "timeout")
            30
        """
        try:
            if not key:
                self.__exceptions_services.raise_null_value("key cannot be null", fail_test=False)
                return None

            with open(file_path, "r", encoding="utf-8") as json_file:
                json_data = json.load(json_file)
                return json_data[key]

        except FileNotFoundError:
            self.__exceptions_services.raise_file_not_found(file_path, fail_test=False)
            return None
        except KeyError:
            self.__exceptions_services.raise_missing_required_field(key, fail_test=False)
            return None
        except json.JSONDecodeError as e:
            self.__exceptions_services.raise_invalid_value(
                f"Invalid JSON in file '{file_path}': {e}", fail_test=False
            )
            return None
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error reading JSON file: {str(e)}", fail_test=False
            )
            return None

    def get_response_cookies(self, response_obj: requests.Response) -> Optional[RequestsCookieJar]:
        """
        Get cookies from a response object.

        Extracts cookies from an HTTP response object.

        Args:
            response_obj: The requests.Response object

        Returns:
            A RequestsCookieJar containing the cookie key-value pairs, or None if operation fails

        Examples:
            >>> builder = RequestBuilder()
            >>> response = requests.get("https://example.com")
            >>> cookies = builder.get_response_cookies(response)
            >>> session_id = cookies.get("session_id")
        """
        try:
            if not isinstance(response_obj, requests.Response):
                self.__exceptions_services.raise_invalid_value(
                    "response_obj must be a requests.Response instance.", fail_test=False
                )
                return None

            if response_obj is None:
                self.__exceptions_services.raise_null_response_object(fail_test=False)
                return None

            return response_obj.cookies
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error in getting response cookies: {str(e)}", fail_test=False
            )
            return None

    def get_response_contenttype(self, response_obj: requests.Response) -> Optional[str]:
        """
        Get content type from a response object.

        Extracts the Content-Type header from an HTTP response object.

        Args:
            response_obj: The requests.Response object

        Returns:
            The content type as a string, or None if not found or if operation fails

        Examples:
            >>> builder = RequestBuilder()
            >>> response = requests.get("https://example.com/api/data")
            >>> content_type = builder.get_response_contenttype(response)
            >>> if "application/json" in content_type:
            ...     # Process JSON response
            ...     pass
        """
        try:
            if response_obj is None:
                self.__exceptions_services.raise_null_response_object(fail_test=False)
                return None

            return response_obj.headers.get("Content-Type", None)
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error in getting response content type: {str(e)}", fail_test=False
            )
            return None

    def encode_url(self, url: str) -> Optional[str]:
        """
        Encode a URL string.

        Replaces special characters with %xx escape sequences in a URL.

        Args:
            url: The URL to encode

        Returns:
            The encoded URL, or None if operation fails

        Examples:
            >>> builder = RequestBuilder()
            >>> builder.encode_url("https://example.com/search?q=test query")
            'https%3A//example.com/search%3Fq%3Dtest%20query'
        """
        try:
            if not url:
                self.__exceptions_services.raise_null_value("URL cannot be null", fail_test=False)
                return None

            return quote(url)
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error in encoding URL: {str(e)}", fail_test=False
            )
            return None

    def decode_url(self, url: str) -> Optional[str]:
        """
        Decode a URL string.

        Replaces %xx escape sequences with their corresponding characters in a URL.

        Args:
            url: The URL to decode

        Returns:
            The decoded URL, or None if operation fails

        Examples:
            >>> builder = RequestBuilder()
            >>> builder.decode_url("https%3A//example.com/search%3Fq%3Dtest%20query")
            'https://example.com/search?q=test query'
        """
        try:
            if not url:
                self.__exceptions_services.raise_null_value("URL cannot be null", fail_test=False)
                return None

            return unquote(url)
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error in decoding URL: {str(e)}", fail_test=False
            )
            return None

    def soap_add_wsdl_endpoint(self, base_url: str, wsdl_endpoint: str) -> Optional[str]:
        """
        Add a WSDL endpoint to a base URL.

        Combines a base URL with a WSDL endpoint for SOAP API operations.

        Args:
            base_url: The base URL
            wsdl_endpoint: The WSDL endpoint to add

        Returns:
            The complete WSDL URL, or None if operation fails

        Examples:
            >>> builder = RequestBuilder()
            >>> builder.soap_add_wsdl_endpoint("https://api.example.com", "service?wsdl")
            'https://api.example.com/service?wsdl'
            >>> builder.soap_add_wsdl_endpoint("https://api.example.com/v1", "/services/user/user.wsdl")
            'https://api.example.com/v1/services/user/user.wsdl'
        """
        try:
            if not base_url:
                self.__exceptions_services.raise_null_value(
                    "base_url cannot be null", fail_test=False
                )
                return None

            if not wsdl_endpoint:
                self.__exceptions_services.raise_null_value(
                    "wsdl_endpoint cannot be null", fail_test=False
                )
                return None

            return self.add_path_parameters(base_url, wsdl_endpoint, True)
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error in adding WSDL endpoint to the base URL: {str(e)}", fail_test=False
            )
            return None

    def compress_data_with_gzip(self, data: str, compress_level: int = 9) -> Optional[bytes]:
        """
        Compress string data into GZIP bytes.

        Compresses text data to GZIP format with configurable compression level.

        Args:
            data: The uncompressed string data
            compress_level: The compression level (0-9, default: 9)

        Returns:
            The compressed data as bytes, or None if compression fails

        Examples:
            >>> builder = RequestBuilder()
            >>> compressed = builder.compress_data_with_gzip("example data")
            >>> # For a specific compression level
            >>> light_compression = builder.compress_data_with_gzip("example data", compress_level=1)
        """
        try:
            if not 0 <= compress_level <= 9:
                self.__exceptions_services.raise_invalid_value(
                    "compress_level must be in the range 0-9.", fail_test=False
                )
                return None

            return gzip.compress(data.encode("utf-8"), compress_level)
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error compressing data: {str(e)}", fail_test=False
            )
            return None

    def decompress_data_with_gzip(self, compressed_data: bytes) -> Optional[str]:
        """
        Decompress GZIP bytes into a string.

        Decompresses GZIP-formatted binary data back to a UTF-8 string.

        Args:
            compressed_data: The compressed data as bytes

        Returns:
            The decompressed string, or None if decompression fails

        Examples:
            >>> builder = RequestBuilder()
            >>> original_text = "example data"
            >>> compressed = builder.compress_data_with_gzip(original_text)
            >>> decompressed = builder.decompress_data_with_gzip(compressed)
            >>> assert original_text == decompressed
        """
        try:
            return gzip.decompress(compressed_data).decode()
        except OSError as e:
            self.__exceptions_services.raise_invalid_value(
                f"Invalid GZIP data: {e}", fail_test=False
            )
            return None
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error decompressing data: {str(e)}", fail_test=False
            )
            return None

    def call_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str] = None,
        json_data: Any = None,
        payload: Any = None,
        cookies: Dict[str, str] = None,
        allow_redirects: bool = False,
        files: Any = None,
        verify: bool = False,
        auth_type: Optional[str] = None,
        auth_username: Optional[str] = None,
        auth_password: Optional[str] = None,
        timeout: Optional[Union[float, Tuple[float, float]]] = None,
        proxies: Optional[Dict[str, str]] = None,
    ) -> Optional[requests.Response]:
        """
        Perform an HTTP request with configurable parameters.

        Makes HTTP requests using the specified method, URL, and parameters.

        Args:
            method: The HTTP method (GET, POST, PUT, PATCH, DELETE)
            url: The request URL
            headers: Request headers (default: None)
            json_data: JSON data for the request body (default: None)
            payload: Data for the request body (default: None)
            cookies: Cookies for the request (default: None)
            allow_redirects: Whether to follow redirects (default: False)
            files: File path for file uploads (default: None)
            verify: Whether to verify SSL certificates (default: False)
            auth_type: Authentication type (e.g., "basic", "digest") (default: None)
            auth_username: Username for authentication (default: None)
            auth_password: Password for authentication (default: None)
            timeout: Timeout in seconds for the request (default: None)
            proxies: Proxy configuration (default: None)

        Returns:
            The response object from the request, or None if the request fails

        Examples:
            >>> builder = RequestBuilder()
            >>> # GET request
            >>> get_response = builder.call_request(
            ...     "GET",
            ...     "https://api.example.com/users",
            ...     headers={"Accept": "application/json"}
            ... )
            >>> # POST request
            >>> post_response = builder.call_request(
            ...     "POST",
            ...     "https://api.example.com/users",
            ...     headers={"Content-Type": "application/json"},
            ...     payload='{"name": "John", "email": "john@example.com"}'
            ... )
        """
        try:
            if not url:
                self.__exceptions_services.raise_null_value(
                    "url cannot be empty or None", fail_test=False
                )
                return None

            if headers is None:
                headers = {}

            if cookies is None:
                cookies = {}

            method = method.upper()
            if method not in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                self.__exceptions_services.raise_invalid_value(
                    f"Invalid HTTP method: {method}. Valid options are: GET, POST, PUT, PATCH, DELETE",
                    fail_test=False,
                )
                return None

            str_auth_string = ""
            if auth_type is not None:
                str_auth_string = self.security.get_auth_string(
                    auth_type, auth_username, auth_password
                )

            if method == "GET":
                return requests.get(
                    url,
                    headers=headers,
                    verify=verify,
                    allow_redirects=allow_redirects,
                    cookies=cookies,
                    auth=str_auth_string,
                    data=payload,
                    json=json_data,
                    timeout=timeout,
                    proxies=proxies,
                )
            if method == "POST":
                if payload is not None or json_data is not None:
                    return requests.post(
                        url,
                        headers=headers,
                        data=payload,
                        json=json_data,
                        verify=verify,
                        allow_redirects=allow_redirects,
                        cookies=cookies,
                        files=files,
                        auth=str_auth_string,
                        timeout=timeout,
                        proxies=proxies,
                    )
                self.__exceptions_services.raise_null_value(
                    "POST request requires payload or json_data", fail_test=False
                )
                return None
            if method == "PUT":
                if payload is not None or json_data is not None:
                    return requests.put(
                        url,
                        headers=headers,
                        data=payload,
                        json=json_data,
                        verify=verify,
                        allow_redirects=allow_redirects,
                        cookies=cookies,
                        files=files,
                        auth=str_auth_string,
                        timeout=timeout,
                        proxies=proxies,
                    )
                self.__exceptions_services.raise_null_value(
                    "PUT request requires payload or json_data", fail_test=False
                )
                return None
            if method == "PATCH":
                if payload is not None or json_data is not None:
                    return requests.patch(
                        url,
                        headers=headers,
                        data=payload,
                        json=json_data,
                        verify=verify,
                        allow_redirects=allow_redirects,
                        cookies=cookies,
                        files=files,
                        auth=str_auth_string,
                        timeout=timeout,
                        proxies=proxies,
                    )
                self.__exceptions_services.raise_null_value(
                    "PATCH request requires payload or json_data", fail_test=False
                )
                return None

            if method == "DELETE":
                return requests.delete(
                    url,
                    headers=headers,
                    verify=verify,
                    allow_redirects=allow_redirects,
                    cookies=cookies,
                    auth=str_auth_string,
                    data=payload,
                    json=json_data,
                    timeout=timeout,
                    proxies=proxies,
                )
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error in API Request: {str(e)}", fail_test=False
            )
            return None

    def get_response_statuscode(self, response_obj: requests.Response) -> Optional[int]:
        """
        Get status code from a response object.

        Extracts the HTTP status code from a response object.

        Args:
            response_obj: The requests.Response object

        Returns:
            The status code as an integer, or None if operation fails

        Examples:
            >>> builder = RequestBuilder()
            >>> response = requests.get("https://example.com")
            >>> status_code = builder.get_response_statuscode(response)
            >>> assert status_code == 200
        """
        try:
            if response_obj is None:
                self.__exceptions_services.raise_null_response_object(fail_test=False)
                return None

            return response_obj.status_code
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error in fetching status code of the response object: {str(e)}", fail_test=False
            )
            return None

    def get_response_headers(
        self, response_obj: requests.Response
    ) -> Optional[CaseInsensitiveDict[str]]:
        """
        Get headers from a response object.

        Extracts HTTP headers from a response object.

        Args:
            response_obj: The requests.Response object

        Returns:
            The headers as a case-insensitive dictionary, or None if operation fails

        Examples:
            >>> builder = RequestBuilder()
            >>> response = requests.get("https://example.com")
            >>> headers = builder.get_response_headers(response)
            >>> content_type = headers.get("Content-Type")
        """
        try:
            if response_obj is None:
                self.__exceptions_services.raise_null_response_object(fail_test=False)
                return None

            return response_obj.headers
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error in fetching headers of the response object: {str(e)}", fail_test=False
            )
            return None

    def get_response_time(
        self, response_obj: requests.Response, desired_format: str = "%s.%S"
    ) -> Union[float, str, None]:
        """
        Get response time in the specified format.

        Calculates and formats the response time from a response object.

        Args:
            response_obj: The requests.Response object
            desired_format: The desired time format ("%s.%f", "%s.%S", or "%M.%s")

        Returns:
            The response time as a float or string, depending on the format, or None if operation fails

        Examples:
            >>> builder = RequestBuilder()
            >>> response = requests.get("https://example.com")
            >>> # Get time in seconds with milliseconds
            >>> time_ms = builder.get_response_time(response, "%s.%S")
            >>> # Get time in seconds with microseconds
            >>> time_us = builder.get_response_time(response, "%s.%f")
            >>> # Get time in minutes
            >>> time_min = builder.get_response_time(response, "%M.%s")
        """

        try:
            if response_obj is None:
                self.__exceptions_services.raise_null_response_object(fail_test=False)
                return None

            if desired_format not in ("%s.%f", "%s.%S", "%M.%s"):
                self.__exceptions_services.raise_invalid_value(
                    f"Invalid time format: {desired_format}", fail_test=False
                )
                return None

            elapsed_seconds = response_obj.elapsed.total_seconds()
            if desired_format == "%s.%f":
                return elapsed_seconds

            elapsed_microseconds = response_obj.elapsed.microseconds
            elapsed_milliseconds = elapsed_microseconds // 1000
            if desired_format == "%s.%S":
                return f"{int(elapsed_seconds)}.{elapsed_milliseconds}"

            elapsed_minutes = round(elapsed_seconds / 60, 4)
            return f"{elapsed_minutes}"
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error in fetching response time: {str(e)}", fail_test=False
            )
            return None
