import gzip
import json
import re
from typing import Any
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
from cafex_api.api_exceptions import APIExceptions
from cafex_core.logging.logger_ import CoreLogger
from cafex_core.utils.core_security import Security
from cafex_core.utils.exceptions import CoreExceptions
from requests.cookies import RequestsCookieJar
from requests.structures import CaseInsensitiveDict


class RequestBuilder:
    """
    Description:
        |  This class provides methods to build a URI using base_url, path params and query params.
        |  This class allows user to modify path params and query params existing in URI
        |  This class also lets user call a web service request.

    """

    def __init__(self):
        self.logger = CoreLogger(name=__name__).get_logger()
        self.security = Security()
        self.__exceptions_generic = CoreExceptions()
        self.__exceptions_services = APIExceptions()

    def get_base_url_from_uri(self, url: str) -> str:
        """Fetches the base URL from a URI.

        Args:
            url: The URL string.

        Returns:
            The base URL.

        Raises:
            Exception: If the URL is invalid or missing scheme or path.

        Examples:
        Input: https://www.samplesite.com/param1/param2?name=abc&id=123
        Output: https://www.samplesite.com
        """
        try:
            if not url:
                self.__exceptions_services.raise_null_value("URL cannot be null")
            dict_url_parts = urlsplit(url)
            if not dict_url_parts.scheme:
                self.__exceptions_services.raise_null_value(
                    f"URL {url} must have a scheme (http or https)"
                )
            if not dict_url_parts.path:
                self.__exceptions_services.raise_null_value(f"URL {url} must have a path")
            str_base_url = dict_url_parts.scheme + "://" + dict_url_parts.netloc
            return str_base_url
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error in fetching base URL: {str(e)}"
            )

    def generate_headers_from_string(
        self, header_string: str, headers_delimiter: str = ",", values_delimiter: str = ":"
    ) -> dict[str, str]:
        """Converts a header string into a dictionary.

        Args:
            header_string: The header string (e.g., "Content-Type: application/json").
            headers_delimiter: Delimiter between headers (default: ",").
            values_delimiter: Delimiter between key and value (default: ":").

        Returns:
            A dictionary of headers.

        Raises:
            Exception: If the header string is invalid or delimiters are the same.
        """
        try:
            if not header_string:
                raise ValueError("Header string cannot be null")
            if headers_delimiter == values_delimiter:
                raise ValueError("Header and value delimiters must be different")

            headers = {}
            for header in header_string.replace("\\'", "").split(headers_delimiter):
                if len(header.split(values_delimiter)) == 2:
                    key, value = header.split(values_delimiter, 1)
                    headers[key.strip()] = value.strip()
                else:
                    raise ValueError(
                        f"Incorrect delimiter ({headers_delimiter}) used between Header Key and Value"
                    )

            return headers
        except Exception as e:
            self.logger.exception("Error in generating headers: %s", e)
            raise e

    def add_path_parameters(
        self, url: str, path_parameters: str, encode: bool = False, replace_params: bool = False
    ) -> str:
        """Adds path parameters to the base URL.

        Args:
            url: The base URL.
            path_parameters: The path parameters to add.
            encode: Whether to encode the parameters.
            replace_params: Whether to replace existing parameters.

        Returns:
            The URL with path parameters added.

        Raises:
            Exception: If the URL or parameters are invalid.
        """
        try:
            if not url:
                raise ValueError("URL cannot be null")

            if not isinstance(replace_params, bool):
                raise ValueError("replace_params must be a boolean")

            if not isinstance(encode, bool):
                raise ValueError("encode must be a boolean")

            if replace_params:
                if url.endswith("/"):
                    url = url[:-1]
            else:
                if not url.endswith("/"):
                    url = url + "/"
                if path_parameters.startswith("/"):
                    path_parameters = path_parameters[1:]

            encoded_params = quote(path_parameters) if encode else path_parameters
            url_with_params = urljoin(url, encoded_params)
            self.logger.info("URL with parameters is: %s", url_with_params)
            return url_with_params
        except Exception as e:
            self.logger.exception("Error in adding path parameters to the base URL: %s", e)
            raise e

    def overwrite_path_parameters(
        self,
        url: str,
        current_params: str,
        new_params: str,
        delimiter: str = ",",
        encode: bool = False,
    ) -> str:
        """Overwrites path parameters in the URI.

        Args:
            url: The URL with path parameters.
            current_params: The current path parameters (comma-separated).
            new_params: The new path parameters (comma-separated).
            delimiter: The delimiter used to separate parameters.
            encode: Whether to encode the parameters.

        Returns:
            The URL with overwritten path parameters.

        Raises:
            Exception: If the URL or parameters are invalid.

        Examples:
            overwrite_path_parameters("https://www.samplesite.com/param1/param2",
                                       "param1,param2",
                                       "param11,param22")
            returns https://www.samplesite.com/param11/param22

            overwrite_path_parameters("https://www.samplesite.com/param1/param2",
                                       "param2",
                                       "param22")
            returns https://www.samplesite.com/param1/param22

            overwrite_path_parameters("https://www.samplesite.com/param1/param2",
                                      "param1#param2",
                                      "param11#param22",
                                      delimiter='#')
            returns https://www.samplesite.com/param11/param22
        """
        try:
            if not url:
                raise ValueError("URL cannot be null")
            if not current_params:
                raise ValueError("Current path parameters cannot be null")
            current_params_list = current_params.split(delimiter)
            new_params_list = new_params.split(delimiter)

            if len(current_params_list) != len(new_params_list):
                raise ValueError(
                    "Current and new path parameters must have the same number of parameters"
                )

            for i, param in enumerate(current_params_list):
                if f"/{param}" not in url:
                    raise ValueError(f"Parameter {param} isn't present in URL {url}")

            for i, param in enumerate(current_params_list):
                url = re.sub(f"/{param}/", f"/{new_params_list[i]}/", url)
                url = re.sub(f"/{param}$", f"/{new_params_list[i]}", url)

            base_url = self.get_base_url_from_uri(url)
            path_params = self.fetch_path_parameters_from_url(url)

            encoded_params = quote(path_params) if encode else path_params

            url_with_params = urljoin(base_url, encoded_params)
            self.logger.info("URL with parameters is: %s", url_with_params)
            return url_with_params
        except Exception as e:
            self.logger.exception("Error in overwriting path parameters: %s", e)
            raise e

    def add_query_parameters(self, url: str, params: dict[str, Any], encode: bool = False) -> str:
        """Adds query parameters to the base URL.

        Args:
            url: The base URL.
            params: A dictionary of query parameters.
            encode: Whether to encode the parameters.

        Returns:
            The URL with query parameters added.

        Raises:
            Exception: If the URL or parameters are invalid.

        Examples:
            add_query_parameters(“https://www.samplesite.com/param1/param2”)
            returns https://www.samplesite.com/param1/param2

            add_query_parameters(“https://www.samplesite.com/param1/param2”,
                                  {“name”:”abc”,”id”:”123”})
            returns https://www.samplesite.com/param1/param2?name=abc&id=123

            add_query_parameters(“https://www.samplesite.com”,
                                  {“name”:”abc”,”id”:”123”})
            returns https://www.samplesite.com/?name=abc&id=123

        .. note::
            |  encode (bool) –
            |  False will add the parameters as it is
            |  True replaces special characters in the url using
            |  %xx escape. Letters, digits and characters ‘_._’
            |  are never quoted
        """
        try:
            if not url:
                raise ValueError("URL cannot be null")

            if not isinstance(encode, bool):
                raise ValueError("encode must be a boolean")

            if not isinstance(params, dict):
                raise ValueError("Query parameters must be a dictionary")

            parsed_url = urlparse(url)
            current_params = dict(parse_qsl(parsed_url.query))
            current_params.update(params)

            if not encode:
                query_string = unquote(urlencode(current_params))
            else:
                query_string = urlencode(current_params)

            url_parts = list(parsed_url)
            url_parts[4] = query_string
            url_with_params = urlunparse(url_parts)
            return url_with_params
        except Exception as e:
            self.logger.exception("Error in adding query parameters to the base URL: %s", e)
            raise e

    def fetch_path_parameters_from_url(self, url: str) -> str:
        """Returns the path parameters/endpoint from a URL.

        Args:
            url: The URL string.

        Returns:
            The path parameters/endpoint.

        Raises:
            Exception: If the URL is invalid.
        """
        try:
            if not url:
                raise ValueError("URL cannot be null")
            parsed_url = urlparse(url)
            str_path_params = parsed_url[2]  # This fetches path parameters from a URL
            return str_path_params
        except Exception as e:
            self.logger.exception("Error in fetching path parameters from URL: %s", e)
            raise e

    def fetch_query_parameters_from_url(
        self, url: str, return_type: str = "text"
    ) -> str | dict[str, str]:
        """Returns the query parameters from the given URL.

        Args:
            url: The URL to extract query parameters from.
            return_type: The desired return type ("text" or "dict").

        Returns:
            The query parameters as a string (if return_type is "text")
            or a dictionary (if return_type is "dict").

        Raises:
            ValueError: If the URL is invalid or return_type is not supported.
        """
        if not url:
            raise ValueError("URL cannot be null")
        return_type = return_type.lower()
        if return_type not in ("text", "dict"):
            raise ValueError(
                f"Invalid return type: {return_type}. Valid options are: text and dict"
            )
        try:
            parsed_uri = urlparse(url)
            if return_type == "text":
                return urlencode(parse_qsl(parsed_uri.query))
            if return_type == "dict":
                return dict(parse_qsl(parsed_uri.query))
        except Exception as e:
            self.logger.exception("Error in fetching query parameters from URL: %s", e)
            raise e

    def modify_payload(
        self,
        template_payload: str | dict[str, Any],
        payload_to_modify: str | dict[str, Any],
    ) -> dict[str, Any]:
        """Adds, updates, or modifies a JSON payload.

        Args:
            template_payload: The base payload (JSON string or dictionary).
            payload_to_modify: The modifications to apply (JSON string or dictionary).

        Returns:
            The modified payload as a dictionary.

        Raises:
            ValueError: If the input payloads are not valid JSON or dictionaries.

        Examples:
            modify_payload('{"name":"SPG","year":"1900"}', '{"HQ":"New York"}')
            returns {"name":"SPG","year":"1900","HQ":"New York"}

            modify_payload('{"name":"SPG","year":"1900"}', '{"HQ":"New York", "year":"2000"}')
            returns {"name":"SPG","year":"2000","HQ":"New York"}
        """
        try:
            if isinstance(template_payload, str):
                template_payload = json.loads(template_payload)
            if not isinstance(template_payload, dict):
                raise ValueError("template_payload must be a JSON string or dictionary.")

            if isinstance(payload_to_modify, str):
                payload_to_modify = json.loads(payload_to_modify)
            if not isinstance(payload_to_modify, dict):
                raise ValueError("payload_to_modify must be a JSON string or dictionary.")

            final_payload = template_payload.copy()
            final_payload.update(payload_to_modify)

            return final_payload
        except Exception as e:
            self.logger.exception("Error in modifying payload: %s", e)
            raise e

    @staticmethod
    def get_value_from_yaml(file_path: str, key: str) -> Any:
        """Fetches the value of the specified key from a YAML file.

        Args:
            file_path: The path to the YAML file.
            key: The key to retrieve the value for.

        Returns:
            The value associated with the key in the YAML file.

        Raises:
            FileNotFoundError: If the YAML file is not found.
            KeyError: If the key is not present in the YAML file.
        """
        if not key:
            raise ValueError("key cannot be null")
        try:
            with open(file_path) as yaml_file:
                yaml_data = yaml.safe_load(yaml_file)
                return yaml_data[key]

        except FileNotFoundError as exc:
            raise FileNotFoundError(f"File Path: '{file_path}' not found.") from exc

        except KeyError as e:
            raise KeyError(f"Key '{key}' not in YAML file '{file_path}'.") from e

        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in file '{file_path}': {e}") from e

    @staticmethod
    def get_value_from_json(file_path: str, key: str) -> Any:
        """Fetches the value of the specified key from a JSON file.

        Args:
            file_path: The path to the JSON file.
            key: The key to retrieve the value for.

        Returns:
            The value associated with the key in the JSON file.

        Raises:
            FileNotFoundError: If the JSON file is not found.
            KeyError: If the key is not present in the JSON file.
            ValueError: If the JSON file contains invalid JSON.
        """
        if not key:
            raise ValueError("key cannot be null")
        try:
            with open(file_path) as json_file:
                json_data = json.load(json_file)
                return json_data[key]

        except FileNotFoundError as exc:
            raise FileNotFoundError(f"File Path: '{file_path}' not found.") from exc

        except KeyError as e:
            raise KeyError(f"Key '{key}' not in JSON file '{file_path}'.") from e

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in file '{file_path}': {e}") from e

    def get_response_cookies(self, response_obj: requests.Response) -> RequestsCookieJar:
        """Returns the cookies of the response object as a dictionary.

        Args:
            response_obj: The requests.Response object.

        Returns:
            A dictionary containing the cookie key-value pairs.

        Raises:
            ValueError: If the response object is not a requests.Response instance.
        """
        try:
            if not isinstance(response_obj, requests.Response):
                raise ValueError("response_obj must be a requests.Response instance.")
            if response_obj is None:
                raise ValueError("response_obj cannot be null")
            return response_obj.cookies
        except Exception as e:
            self.logger.exception("Error in getting response cookies: %s", e)
            raise e

    def get_response_contenttype(self, response_obj: requests.Response) -> str | None:
        """Returns the content type of the response object.

        Args:
            response_obj: The requests.Response object.

        Returns:
            The content type as a string, or None if not found.
        """
        try:
            if response_obj is None:
                raise ValueError("response_obj cannot be null")
            return response_obj.headers.get("Content-Type", None)
        except Exception as e:
            self.logger.exception("Error in getting response content type: %s", e)
            raise e

    def encode_url(self, url: str) -> str:
        """Encodes the URL, replacing special characters with %xx escape
        sequences.

        Args:
            url: The URL to encode.

        Returns:
            The encoded URL.
        """
        try:
            if not url:
                raise ValueError("URL cannot be null")
            return quote(url)
        except Exception as e:
            self.logger.exception("Error in encoding URL: %s", e)
            raise e

    def decode_url(self, url: str) -> str:
        """Decodes the URL, replacing %xx escape sequences with their
        corresponding characters.

        Args:
            url: The URL to decode.

        Returns:
            The decoded URL.
        """
        try:
            if not url:
                raise ValueError("URL cannot be null")
            return unquote(url)
        except Exception as e:
            self.logger.exception("Error in decoding URL: %s", e)
            raise e

    def soap_add_wsdl_endpoint(self, base_url: str, wsdl_endpoint: str) -> str:
        """Adds a WSDL endpoint to the base URL and returns the final URL.

        Args:
            base_url: The base URL.
            wsdl_endpoint: The WSDL endpoint to add.

        Returns:
            The URL with the WSDL endpoint added.

        Raises:
            ValueError: If the base URL or WSDL endpoint is empty.
        """
        try:
            if not base_url:
                raise ValueError("base_url cannot be null")
            if not wsdl_endpoint:
                raise ValueError("wsdl_endpoint cannot be null")
            return self.add_path_parameters(base_url, wsdl_endpoint, True)
        except Exception as e:
            self.logger.exception("Error in adding WSDL endpoint to the base URL: %s", e)
            raise e

    @staticmethod
    def compress_data_with_gzip(data: str, compress_level: int = 9) -> bytes:
        """Compresses string data into GZIP bytes.

        Args:
            data: The uncompressed string data.
            compress_level: The compression level (0-9, default: 9).

        Returns:
            The compressed data as bytes.

        Raises:
            ValueError: If the compression level is outside the valid range.
        """

        if not 0 <= compress_level <= 9:
            raise ValueError("compress_level must be in the range 0-9.")

        return gzip.compress(data.encode("utf-8"), compress_level)

    @staticmethod
    def decompress_data_with_gzip(compressed_data: bytes) -> str:
        """Decompresses GZIP bytes into a string.

        Args:
            compressed_data: The compressed data as bytes.

        Returns:
            The decompressed string.

        Raises:
            ValueError: If the input data is not valid GZIP data.
        """

        try:
            return gzip.decompress(compressed_data).decode()
        except OSError as e:
            raise ValueError(f"Invalid GZIP data: {e}") from e

    def call_request(
        self, method: str, url: str, headers: dict[str, str], **kwargs: Any
    ) -> requests.Response:
        """Performs various HTTP requests (GET, POST, PUT, PATCH, DELETE) with
        flexible parameters.

        This method allows you to make HTTP requests using the specified method, URL, and headers.
        It also accepts additional keyword arguments (kwargs) to customize the request further.

        Args:
            method (str): The HTTP method (e.g., 'GET', 'POST').
            url (str): The request URL.
            headers (dict): A dictionary of request headers.
             **kwargs: Additional keyword arguments to customize the request. These include:
                * pstr_json (str): JSON data for the request body.
                * pstr_payload (dict): Data for the request body.
                * pdict_cookies (dict): Cookies for the request.
                * pbln_allow_redirects (bool): Allow or disallow redirects.
                * pstr_files (str): File path for file uploads.
                * pbln_verify (bool): Verify SSL certificates.
                * pstr_auth_type (str): Authentication type (e.g., "basic", "digest").
                * pstr_auth_username (str): Username for authentication.
                * pstr_auth_password (str): Password for authentication.
                * ptimeout (float or tuple): Timeout in seconds for the request.
                * pdict_proxies (dict): Proxy configuration.

        Returns:
            requests.Response: The response object from the request.

        Examples:
            call_request("GET", "https://www.samplesite.com/param1/param2", headers={"Accept":
            "application/json"})
            call_request("POST", "https://www.samplesite.com/param1/param2", headers={"Accept":
            "application/json"}, pstr_payload='{"KOU": "123456"}', pbln_allow_redirects=True)
        """
        if not url:
            raise ValueError("url cannot be empty or None")
        method = method.upper()
        if method not in ("GET", "POST", "PUT", "PATCH", "DELETE"):
            raise ValueError(
                f"Invalid HTTP method: {method}. Valid options are: GET, POST, PUT, PATCH, DELETE"
            )
        try:

            request_json = kwargs.get("pstr_json", None)
            payload = kwargs.get("pstr_payload", None)
            cookies = kwargs.get("pdict_cookies", {})
            allow_redirects = kwargs.get("pbln_allow_redirects", False)
            files = kwargs.get("pstr_files", None)
            verify = kwargs.get("pbln_verify", False)
            auth_type = kwargs.get("pstr_auth_type", None)
            auth_username = kwargs.get("pstr_auth_username", None)
            auth_password = kwargs.get("pstr_auth_password", None)
            timeout = kwargs.get("ptimeout", None)
            proxies = kwargs.get("pdict_proxies", None)

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
                    json=request_json,
                    timeout=timeout,
                    proxies=proxies,
                )
            if method == "POST":
                if payload is not None:
                    return requests.post(
                        url,
                        headers=headers,
                        data=payload,
                        json=request_json,
                        verify=verify,
                        allow_redirects=allow_redirects,
                        cookies=cookies,
                        files=files,
                        auth=str_auth_string,
                        timeout=timeout,
                        proxies=proxies,
                    )
                raise Exception("Error-->Payload is missing")
            if method == "PUT":
                if payload is not None:
                    return requests.put(
                        url,
                        headers=headers,
                        data=payload,
                        verify=verify,
                        allow_redirects=allow_redirects,
                        cookies=cookies,
                        files=files,
                        auth=str_auth_string,
                        timeout=timeout,
                        proxies=proxies,
                    )
                raise Exception("Error-->Payload is missing")
            if method == "PATCH":
                if payload is not None:
                    return requests.patch(
                        url,
                        headers=headers,
                        data=payload,
                        verify=verify,
                        allow_redirects=allow_redirects,
                        cookies=cookies,
                        files=files,
                        auth=str_auth_string,
                        timeout=timeout,
                        proxies=proxies,
                    )
                raise Exception("Error-->Payload is missing")
            if method == "DELETE":
                return requests.delete(
                    url,
                    headers=headers,
                    verify=verify,
                    allow_redirects=allow_redirects,
                    cookies=cookies,
                    auth=str_auth_string,
                    data=payload,
                    json=request_json,
                    timeout=timeout,
                    proxies=proxies,
                )
        except Exception as e:
            self.logger.exception("Error in API Request: %s", e)
            raise e

    def get_response_statuscode(self, response_obj: requests.Response) -> int:
        """Returns the status code of the response object.

        Args:
            response_obj: The requests.Response object.

        Returns:
            The status code as an integer.

        Raises:
            Exception: If the response object is None.
        """
        try:
            if response_obj is None:
                raise ValueError("response_obj cannot be None")
            return response_obj.status_code
        except Exception as e:
            self.logger.exception("Error in fetching status code of the response object: %s", e)
            raise e

    def get_response_headers(self, response_obj: requests.Response) -> CaseInsensitiveDict[str]:
        """Returns the headers of the response object as a dictionary.

        Args:
            response_obj: The requests.Response object.

        Returns:
            The headers as a dictionary.

        Raises:
            Exception: If the response object is None.
        """
        try:
            if response_obj is None:
                raise ValueError("response_obj cannot be None")
            return response_obj.headers
        except Exception as e:
            self.logger.exception("Error in fetching headers of the response object: %s", e)
            raise e

    def get_response_time(
        self, response_obj: requests.Response, desired_format: str = "%s.%S"
    ) -> float | str:
        """Returns the response time in the specified format.

        Args:
            response_obj: The requests.Response object.
            desired_format: The desired time format (e.g., "%s.%f", "%s.%S", "%M.%s").

        Returns:
            The response time as a float or string, depending on the format.

        Raises:
            Exception: If the response object is None or the format is invalid.
        """
        try:
            if response_obj is None:
                raise ValueError("response_obj cannot be None")
            if desired_format not in ("%s.%f", "%s.%S", "%M.%s"):
                raise ValueError(f"Invalid time format: {desired_format}")

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
            self.logger.exception("Error in fetching response time: %s", e)
            raise e
