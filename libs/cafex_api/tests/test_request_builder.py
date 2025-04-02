"""
Test module for the RequestBuilder class in the CAFEX framework.

This module provides comprehensive test coverage for the URI building and HTTP request
capabilities in the cafex_api.request_builder module.
"""

import json
import pytest
import requests
from unittest.mock import MagicMock, patch
from requests.cookies import RequestsCookieJar
from requests.structures import CaseInsensitiveDict

from cafex_api.request_builder import RequestBuilder


class TestRequestBuilder:
    """Test suite for RequestBuilder class."""

    @pytest.fixture
    def request_builder(self):
        """Fixture to create a RequestBuilder instance for tests."""
        return RequestBuilder()

    def test_init(self, request_builder):
        """Test RequestBuilder initialization."""
        assert request_builder is not None
        assert request_builder.logger is not None
        assert request_builder.security is not None
        assert request_builder._RequestBuilder__exceptions_generic is not None
        assert request_builder._RequestBuilder__exceptions_services is not None

    def test_get_base_url_from_uri(self, request_builder):
        """Test extracting base URL from URI."""
        # Valid URL
        url = "https://www.samplesite.com/param1/param2?name=abc&id=123"
        base_url = request_builder.get_base_url_from_uri(url)
        assert base_url == "https://www.samplesite.com"

        # URL with port
        url = "https://api.example.com:8080/v1/users?active=true"
        base_url = request_builder.get_base_url_from_uri(url)
        assert base_url == "https://api.example.com:8080"

        # Empty URL
        with pytest.raises(Exception):
            request_builder.get_base_url_from_uri("")

        # URL without scheme
        with pytest.raises(Exception):
            request_builder.get_base_url_from_uri("www.example.com/test")

        # URL without path
        with pytest.raises(Exception):
            request_builder.get_base_url_from_uri("https://www.example.com")

    def test_generate_headers_from_string(self, request_builder):
        """Test converting a header string into a dictionary."""
        # Simple header
        header_string = "Content-Type: application/json"
        headers = request_builder.generate_headers_from_string(header_string)
        assert headers == {"Content-Type": "application/json"}

        # Multiple headers
        header_string = "Content-Type: application/json, Accept: application/json, Authorization: Bearer token123"
        headers = request_builder.generate_headers_from_string(header_string)
        assert headers == {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer token123"
        }

        # Custom delimiters
        header_string = "Content-Type=application/json|Accept=application/json"
        headers = request_builder.generate_headers_from_string(header_string, headers_delimiter="|", values_delimiter="=")
        assert headers == {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Empty header string
        with pytest.raises(ValueError):
            request_builder.generate_headers_from_string("")

        # Same delimiters
        with pytest.raises(ValueError):
            request_builder.generate_headers_from_string("Content-Type: application/json", headers_delimiter=":", values_delimiter=":")

        # Invalid format
        with pytest.raises(ValueError):
            request_builder.generate_headers_from_string("Content-Type application/json")

    def test_add_path_parameters(self, request_builder):
        """Test adding path parameters to base URL."""
        # Simple path parameter
        url = "https://api.example.com"
        path_params = "users"
        result = request_builder.add_path_parameters(url, path_params)
        assert result == "https://api.example.com/users"

        # Multiple path parameters
        url = "https://api.example.com"
        path_params = "users/123/profile"
        result = request_builder.add_path_parameters(url, path_params)
        assert result == "https://api.example.com/users/123/profile"

        # URL with trailing slash
        url = "https://api.example.com/"
        path_params = "users"
        result = request_builder.add_path_parameters(url, path_params)
        assert result == "https://api.example.com/users"

        # Path parameters with leading slash
        url = "https://api.example.com"
        path_params = "/users"
        result = request_builder.add_path_parameters(url, path_params)
        assert result == "https://api.example.com/users"

        # With encoding
        url = "https://api.example.com"
        path_params = "users/John Doe/profile"
        result = request_builder.add_path_parameters(url, path_params, encode=True)
        assert result == "https://api.example.com/users/John%20Doe/profile"

        # Replace parameters
        url = "https://api.example.com/old/path"
        path_params = "new/path"
        result = request_builder.add_path_parameters(url, path_params, replace_params=True)
        assert result == "https://api.example.com/new/path"

        # Empty URL
        with pytest.raises(ValueError):
            request_builder.add_path_parameters("", "users")

        # Invalid parameter types
        with pytest.raises(ValueError):
            request_builder.add_path_parameters(url, path_params, encode="not_a_bool")

        with pytest.raises(ValueError):
            request_builder.add_path_parameters(url, path_params, replace_params="not_a_bool")

    def test_overwrite_path_parameters(self, request_builder):
        """Test overwriting path parameters in the URI."""
        # Replace all parameters
        url = "https://www.samplesite.com/param1/param2"
        result = request_builder.overwrite_path_parameters(
            url, "param1,param2", "newparam1,newparam2"
        )
        assert result == "https://www.samplesite.com/newparam1/newparam2"

        # Replace one parameter
        url = "https://www.samplesite.com/param1/param2"
        result = request_builder.overwrite_path_parameters(
            url, "param2", "newparam2"
        )
        assert result == "https://www.samplesite.com/param1/newparam2"

        # Custom delimiter
        url = "https://www.samplesite.com/param1/param2"
        result = request_builder.overwrite_path_parameters(
            url, "param1#param2", "newparam1#newparam2", delimiter="#"
        )
        assert result == "https://www.samplesite.com/newparam1/newparam2"

        # With encoding
        url = "https://www.samplesite.com/param1/param2"
        result = request_builder.overwrite_path_parameters(
            url, "param1,param2", "new param1,new param2", encode=True
        )
        assert result == "https://www.samplesite.com/new%20param1/new%20param2"

        # Empty URL
        with pytest.raises(ValueError):
            request_builder.overwrite_path_parameters("", "param", "newparam")

        # Empty current parameters
        with pytest.raises(ValueError):
            request_builder.overwrite_path_parameters(url, "", "newparam")

        # Mismatched parameter lists length
        with pytest.raises(ValueError):
            request_builder.overwrite_path_parameters(
                url, "param1,param2", "newparam1,newparam2,newparam3"
            )

        # Parameter not in URL
        with pytest.raises(ValueError):
            request_builder.overwrite_path_parameters(
                url, "nonexistent", "newparam"
            )

    def test_add_query_parameters(self, request_builder):
        """Test adding query parameters to the URL."""
        # Add query parameters to URL without any
        url = "https://www.samplesite.com/param1/param2"
        params = {"name": "abc", "id": "123"}
        result = request_builder.add_query_parameters(url, params)
        assert result == "https://www.samplesite.com/param1/param2?name=abc&id=123"

        # Add query parameters to URL with existing ones
        url = "https://www.samplesite.com/param1/param2?existing=value"
        params = {"name": "abc", "id": "123"}
        result = request_builder.add_query_parameters(url, params)
        assert "existing=value" in result
        assert "name=abc" in result
        assert "id=123" in result

        # With encoding
        url = "https://www.samplesite.com/param1/param2"
        params = {"name": "John Doe", "id": "123"}
        result = request_builder.add_query_parameters(url, params, encode=True)
        assert "name=John%20Doe" in result

        # Without encoding
        url = "https://www.samplesite.com/param1/param2"
        params = {"name": "John Doe", "id": "123"}
        result = request_builder.add_query_parameters(url, params, encode=False)
        assert "name=John Doe" in result

        # Empty URL
        with pytest.raises(ValueError):
            request_builder.add_query_parameters("", params)

        # Invalid encode parameter
        with pytest.raises(ValueError):
            request_builder.add_query_parameters(url, params, encode="not_a_bool")

        # Invalid params parameter
        with pytest.raises(ValueError):
            request_builder.add_query_parameters(url, "not_a_dict")

    def test_fetch_path_parameters_from_url(self, request_builder):
        """Test fetching path parameters from URL."""
        # Simple URL
        url = "https://www.samplesite.com/param1/param2"
        result = request_builder.fetch_path_parameters_from_url(url)
        assert result == "/param1/param2"

        # URL with query parameters
        url = "https://www.samplesite.com/param1/param2?name=abc&id=123"
        result = request_builder.fetch_path_parameters_from_url(url)
        assert result == "/param1/param2"

        # URL with just domain
        url = "https://www.samplesite.com"
        result = request_builder.fetch_path_parameters_from_url(url)
        assert result == ""

        # Empty URL
        with pytest.raises(ValueError):
            request_builder.fetch_path_parameters_from_url("")

    def test_fetch_query_parameters_from_url(self, request_builder):
        """Test fetching query parameters from URL."""
        # URL with query parameters, text return
        url = "https://www.samplesite.com/param1/param2?name=abc&id=123"
        result = request_builder.fetch_query_parameters_from_url(url, return_type="text")
        assert result == "name=abc&id=123"

        # URL with query parameters, dict return
        url = "https://www.samplesite.com/param1/param2?name=abc&id=123"
        result = request_builder.fetch_query_parameters_from_url(url, return_type="dict")
        assert result == {"name": "abc", "id": "123"}

        # URL without query parameters
        url = "https://www.samplesite.com/param1/param2"
        result = request_builder.fetch_query_parameters_from_url(url, return_type="dict")
        assert result == {}

        # Empty URL
        with pytest.raises(ValueError):
            request_builder.fetch_query_parameters_from_url("", return_type="text")

        # Invalid return type
        with pytest.raises(ValueError):
            request_builder.fetch_query_parameters_from_url(url, return_type="invalid")

    def test_modify_payload(self, request_builder):
        """Test adding, updating, or modifying a JSON payload."""
        # String payloads
        template = '{"name":"SPG","year":"1900"}'
        modifications = '{"HQ":"New York"}'
        result = request_builder.modify_payload(template, modifications)
        assert result == {"name": "SPG", "year": "1900", "HQ": "New York"}

        # Overwrite existing key
        template = '{"name":"SPG","year":"1900"}'
        modifications = '{"HQ":"New York", "year":"2000"}'
        result = request_builder.modify_payload(template, modifications)
        assert result == {"name": "SPG", "year": "2000", "HQ": "New York"}

        # Dictionary payloads
        template = {"name": "SPG", "year": "1900"}
        modifications = {"HQ": "New York"}
        result = request_builder.modify_payload(template, modifications)
        assert result == {"name": "SPG", "year": "1900", "HQ": "New York"}

        # Mixed payloads (string and dict)
        template = '{"name":"SPG","year":"1900"}'
        modifications = {"HQ": "New York"}
        result = request_builder.modify_payload(template, modifications)
        assert result == {"name": "SPG", "year": "1900", "HQ": "New York"}

        # Invalid inputs
        with pytest.raises(Exception):
            request_builder.modify_payload("not_valid_json", modifications)

        with pytest.raises(Exception):
            request_builder.modify_payload(template, "not_valid_json")

        with pytest.raises(Exception):
            request_builder.modify_payload([1, 2, 3], modifications)

        with pytest.raises(Exception):
            request_builder.modify_payload(template, [1, 2, 3])

    @patch('builtins.open', MagicMock())
    def test_get_value_from_yaml(self, request_builder):
        """Test fetching values from YAML files."""
        # Mock the yaml.safe_load to return a test dictionary
        with patch('yaml.safe_load', return_value={"key1": "value1", "key2": "value2"}):
            value = RequestBuilder.get_value_from_yaml("test.yaml", "key1")
            assert value == "value1"

        # Test non-existent key
        with patch('yaml.safe_load', return_value={"key1": "value1"}):
            with pytest.raises(KeyError):
                RequestBuilder.get_value_from_yaml("test.yaml", "nonexistent")

        # Test empty key
        with pytest.raises(ValueError):
            RequestBuilder.get_value_from_yaml("test.yaml", "")

        # Test file not found
        with patch('builtins.open', side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                RequestBuilder.get_value_from_yaml("nonexistent.yaml", "key")

        # Test invalid YAML
        with patch('yaml.safe_load', side_effect=Exception("Invalid YAML")):
            with pytest.raises(ValueError):
                RequestBuilder.get_value_from_yaml("invalid.yaml", "key")

    @patch('builtins.open', MagicMock())
    def test_get_value_from_json(self, request_builder):
        """Test fetching values from JSON files."""
        # Mock the json.load to return a test dictionary
        with patch('json.load', return_value={"key1": "value1", "key2": "value2"}):
            value = RequestBuilder.get_value_from_json("test.json", "key1")
            assert value == "value1"

        # Test non-existent key
        with patch('json.load', return_value={"key1": "value1"}):
            with pytest.raises(KeyError):
                RequestBuilder.get_value_from_json("test.json", "nonexistent")

        # Test empty key
        with pytest.raises(ValueError):
            RequestBuilder.get_value_from_json("test.json", "")

        # Test file not found
        with patch('builtins.open', side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                RequestBuilder.get_value_from_json("nonexistent.json", "key")

        # Test invalid JSON
        with patch('json.load', side_effect=json.JSONDecodeError("Invalid JSON", "", 0)):
            with pytest.raises(ValueError):
                RequestBuilder.get_value_from_json("invalid.json", "key")

    def test_get_response_cookies(self, request_builder):
        """Test getting cookies from response object."""
        # Create a mock response with cookies
        mock_response = MagicMock(spec=requests.Response)
        mock_cookies = RequestsCookieJar()
        mock_cookies.set("session", "abc123")
        mock_response.cookies = mock_cookies

        cookies = request_builder.get_response_cookies(mock_response)
        assert cookies == mock_cookies
        assert "session" in cookies

        # Test with invalid response object
        with pytest.raises(ValueError):
            request_builder.get_response_cookies("not_a_response")

        # Test with None
        with pytest.raises(ValueError):
            request_builder.get_response_cookies(None)

    def test_get_response_contenttype(self, request_builder):
        """Test getting content type from response object."""
        # Create a mock response with content type header
        mock_response = MagicMock(spec=requests.Response)
        mock_response.headers = {"Content-Type": "application/json"}

        content_type = request_builder.get_response_contenttype(mock_response)
        assert content_type == "application/json"

        # Response without content type
        mock_response.headers = {}
        content_type = request_builder.get_response_contenttype(mock_response)
        assert content_type is None

        # Test with None
        with pytest.raises(ValueError):
            request_builder.get_response_contenttype(None)

    def test_encode_url(self, request_builder):
        """Test URL encoding."""
        # URL with spaces and special characters
        url = "https://example.com/path with spaces/special?param=value&other=test"
        encoded_url = request_builder.encode_url(url)
        assert "%20" in encoded_url  # Space encoded
        assert "%3F" in encoded_url  # ? encoded
        assert "%3D" in encoded_url  # = encoded
        assert "%26" in encoded_url  # & encoded

        # Empty URL
        with pytest.raises(ValueError):
            request_builder.encode_url("")

    def test_decode_url(self, request_builder):
        """Test URL decoding."""
        # Encoded URL
        encoded_url = "https%3A%2F%2Fexample.com%2Fpath%20with%20spaces"
        decoded_url = request_builder.decode_url(encoded_url)
        assert decoded_url == "https://example.com/path with spaces"

        # Empty URL
        with pytest.raises(ValueError):
            request_builder.decode_url("")

    def test_soap_add_wsdl_endpoint(self, request_builder):
        """Test adding WSDL endpoint to base URL."""
        # Simple case
        base_url = "https://api.example.com"
        wsdl_endpoint = "service?wsdl"
        result = request_builder.soap_add_wsdl_endpoint(base_url, wsdl_endpoint)
        assert result == "https://api.example.com/service?wsdl"

        # With special characters
        base_url = "https://api.example.com"
        wsdl_endpoint = "service with spaces?wsdl"
        result = request_builder.soap_add_wsdl_endpoint(base_url, wsdl_endpoint)
        assert result == "https://api.example.com/service%20with%20spaces%3Fwsdl"

        # Empty base URL
        with pytest.raises(ValueError):
            request_builder.soap_add_wsdl_endpoint("", wsdl_endpoint)

        # Empty endpoint
        with pytest.raises(ValueError):
            request_builder.soap_add_wsdl_endpoint(base_url, "")

    def test_compress_data_with_gzip(self, request_builder):
        """Test compressing data with GZIP."""
        # Simple compression
        data = "This is a test string for compression."
        compressed = RequestBuilder.compress_data_with_gzip(data)
        assert isinstance(compressed, bytes)
        assert len(compressed) < len(data.encode('utf-8'))

        # With custom compression level
        compressed_level_1 = RequestBuilder.compress_data_with_gzip(data, compress_level=1)
        compressed_level_9 = RequestBuilder.compress_data_with_gzip(data, compress_level=9)
        # Level 1 should produce larger output than level 9
        assert len(compressed_level_1) >= len(compressed_level_9)

        # Invalid compression level
        with pytest.raises(ValueError):
            RequestBuilder.compress_data_with_gzip(data, compress_level=10)

        with pytest.raises(ValueError):
            RequestBuilder.compress_data_with_gzip(data, compress_level=-1)

    def test_decompress_data_with_gzip(self, request_builder):
        """Test decompressing GZIP data."""
        # Compress and then decompress
        original = "This is a test string for compression and decompression."
        compressed = RequestBuilder.compress_data_with_gzip(original)
        decompressed = RequestBuilder.decompress_data_with_gzip(compressed)
        assert decompressed == original

        # Invalid compressed data
        with pytest.raises(ValueError):
            RequestBuilder.decompress_data_with_gzip(b'not_gzipped_data')

    @patch('requests.get')
    @patch('requests.post')
    @patch('requests.put')
    @patch('requests.patch')
    @patch('requests.delete')
    def test_call_request(self, mock_delete, mock_patch, mock_put, mock_post, mock_get, request_builder):
        """Test making HTTP requests with various methods."""
        # Mock the Security.get_auth_string method to avoid dependency
        request_builder.security.get_auth_string = MagicMock(return_value=("user", "pass"))

        # Common test parameters
        url = "https://api.example.com/test"
        headers = {"Content-Type": "application/json"}
        payload = '{"key": "value"}'

        # GET request
        mock_response = MagicMock(spec=requests.Response)
        mock_get.return_value = mock_response
        response = request_builder.call_request("GET", url, headers)
        assert response == mock_response
        mock_get.assert_called_once()

        # POST request
        mock_response = MagicMock(spec=requests.Response)
        mock_post.return_value = mock_response
        response = request_builder.call_request("POST", url, headers, pstr_payload=payload)
        assert response == mock_response
        mock_post.assert_called_once()

        # POST without payload
        with pytest.raises(Exception):
            request_builder.call_request("POST", url, headers)

        # PUT request
        mock_response = MagicMock(spec=requests.Response)
        mock_put.return_value = mock_response
        response = request_builder.call_request("PUT", url, headers, pstr_payload=payload)
        assert response == mock_response
        mock_put.assert_called_once()

        # PUT without payload
        with pytest.raises(Exception):
            request_builder.call_request("PUT", url, headers)

        # PATCH request
        mock_response = MagicMock(spec=requests.Response)
        mock_patch.return_value = mock_response
        response = request_builder.call_request("PATCH", url, headers, pstr_payload=payload)
        assert response == mock_response
        mock_patch.assert_called_once()

        # PATCH without payload
        with pytest.raises(Exception):
            request_builder.call_request("PATCH", url, headers)

        # DELETE request
        mock_response = MagicMock(spec=requests.Response)
        mock_delete.return_value = mock_response
        response = request_builder.call_request("DELETE", url, headers)
        assert response == mock_response
        mock_delete.assert_called_once()

        # Invalid method
        with pytest.raises(ValueError):
            request_builder.call_request("INVALID", url, headers)

        # Empty URL
        with pytest.raises(ValueError):
            request_builder.call_request("GET", "", headers)

    def test_get_response_statuscode(self, request_builder):
        """Test getting status code from response object."""
        # Create a mock response with status code
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200

        status_code = request_builder.get_response_statuscode(mock_response)
        assert status_code == 200

        # Test with None
        with pytest.raises(ValueError):
            request_builder.get_response_statuscode(None)

    def test_get_response_headers(self, request_builder):
        """Test getting headers from response object."""
        # Create a mock response with headers
        mock_response = MagicMock(spec=requests.Response)
        mock_headers = CaseInsensitiveDict({"Content-Type": "application/json", "X-Custom": "value"})
        mock_response.headers = mock_headers

        headers = request_builder.get_response_headers(mock_response)
        assert headers == mock_headers
        assert headers["content-type"] == "application/json"
        assert headers["X-Custom"] == "value"

        # Test with None
        with pytest.raises(ValueError):
            request_builder.get_response_headers(None)

    def test_get_response_time(self, request_builder):
        """Test getting response time in various formats."""
        from datetime import timedelta

        # Create a mock response with elapsed time
        mock_response = MagicMock(spec=requests.Response)
        mock_response.elapsed = timedelta(seconds=1, microseconds=500000)  # 1.5 seconds

        # Default format (%s.%S)
        response_time = request_builder.get_response_time(mock_response)
        assert response_time == "1.500"

        # Seconds with microseconds format
        response_time = request_builder.get_response_time(mock_response, desired_format="%s.%f")
        assert response_time == 1.5

        # Minutes format
        response_time = request_builder.get_response_time(mock_response, desired_format="%M.%s")
        assert float(response_time) == 0.025  # 1.5 seconds = 0.025 minutes

        # Invalid format
        with pytest.raises(ValueError):
            request_builder.get_response_time(mock_response, desired_format="invalid")

        # Test with None
        with pytest.raises(ValueError):
            request_builder.get_response_time(None)