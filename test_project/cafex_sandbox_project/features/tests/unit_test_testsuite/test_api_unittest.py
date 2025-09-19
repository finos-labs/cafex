"""
Unit tests for the JSONPlaceholderAPI class that uses RequestBuilder.

This module contains unit tests that verify the functionality of individual methods
in the JSONPlaceholderAPI class, which uses the RequestBuilder to interact with
the JSONPlaceholder API.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

import pytest
from cafex_core.reporting_.step_decorator import step
from requests import Response

from test_project.cafex_sandbox_project.features.services.jsonplaceholder_api import JSONPlaceholderAPI


class TestJSONPlaceholderAPIUnit(unittest.TestCase):
    """Unit test suite for JSONPlaceholderAPI class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.api_service = JSONPlaceholderAPI()
        self.api_service.request_builder = MagicMock()
        self.mock_response = MagicMock(spec=Response)
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = {
            "id": 1,
            "title": "Test Title",
            "body": "Test Body",
            "userId": 1
        }
        self.api_service.request_builder.call_request.return_value = self.mock_response

    def test_check_api_status(self):
        """Test the check_api_status method."""

        @step("When I check the API status")
        def check_api_status():
            result = self.api_service.check_api_status()
            assert result is True, "API status check should return True"

        @step("Then the request_builder.call_request should be called correctly")
        def verify_call_request():
            self.api_service.request_builder.call_request.assert_called_once_with(
                method="GET",
                url="https://jsonplaceholder.typicode.com/posts/1",
                headers={"Accept": "application/json"},
                verify=False
            )

        # Execute the steps
        check_api_status()
        verify_call_request()

    def test_check_api_status_error(self):
        """Test the check_api_status method when an error occurs."""

        @step("Given the request_builder.call_request raises an exception")
        def setup_exception():
            self.api_service.request_builder.call_request.side_effect = Exception("Test error")

        @step("When I check the API status")
        def check_api_status():
            result = self.api_service.check_api_status()
            assert result is False, "API status check should return False on error"

        # Execute the steps
        setup_exception()
        check_api_status()

    def test_get_post(self):
        """Test the get_post method."""

        @step("When I call get_post with ID 1")
        def call_get_post():
            response = self.api_service.get_post(1)
            assert response == self.mock_response, "get_post should return the response"

        @step("Then the request_builder.call_request should be called with correct parameters")
        def verify_call_request():
            # Assuming get_service_config returns default values
            self.api_service.request_builder.call_request.assert_called_once()
            call_args = self.api_service.request_builder.call_request.call_args[1]
            assert call_args['method'] == "GET"
            assert call_args['url'] == "https://jsonplaceholder.typicode.com/posts/1"
            assert "Accept" in call_args['headers']
            assert call_args['verify'] is False

        # Execute the steps
        call_get_post()
        verify_call_request()

    def test_send_request_to_endpoint(self):
        """Test the send_request_to_endpoint method."""

        @step("When I call send_request_to_endpoint with '/posts/1'")
        def call_send_request():
            response = self.api_service.send_request_to_endpoint("/posts/1")
            assert response == self.mock_response, "send_request_to_endpoint should return the response"

        @step("Then the request_builder.call_request should be called with correct parameters")
        def verify_call_request():
            self.api_service.request_builder.call_request.assert_called_once_with(
                method="GET",
                url="https://jsonplaceholder.typicode.com/posts/1",
                headers={"Accept": "application/json"},
                verify=False
            )

        # Execute the steps
        call_send_request()
        verify_call_request()

    def test_create_post(self):
        """Test the create_post method."""

        @step("When I call create_post with title and body")
        def call_create_post():
            response = self.api_service.create_post("Test Title", "Test Body")
            assert response == self.mock_response, "create_post should return the response"

        @step("Then the request_builder.call_request should be called with correct parameters")
        def verify_call_request():
            self.api_service.request_builder.call_request.assert_called_once()
            call_args = self.api_service.request_builder.call_request.call_args[1]
            assert call_args['method'] == "POST"
            assert call_args['url'].endswith("/posts")
            assert "Content-Type" in call_args['headers']
            assert call_args['verify'] is False

            # Verify payload
            payload = json.loads(call_args['payload'])
            assert payload['title'] == "Test Title"
            assert payload['body'] == "Test Body"
            assert payload['userId'] == 1

        # Execute the steps
        call_create_post()
        verify_call_request()

    def test_update_post(self):
        """Test the update_post method."""

        @step("When I call update_post with ID and title")
        def call_update_post():
            response = self.api_service.update_post("1", "Updated Title")
            assert response == self.mock_response, "update_post should return the response"

        @step("Then the request_builder.call_request should be called with correct parameters")
        def verify_call_request():
            self.api_service.request_builder.call_request.assert_called_once()
            call_args = self.api_service.request_builder.call_request.call_args[1]
            assert call_args['method'] == "PATCH"
            assert call_args['url'].endswith("/posts/1")
            assert "Content-Type" in call_args['headers']
            assert call_args['verify'] is False

            # Verify payload
            payload = json.loads(call_args['payload'])
            assert payload['title'] == "Updated Title"

        # Execute the steps
        call_update_post()
        verify_call_request()

    def test_delete_post(self):
        """Test the delete_post method."""

        @step("When I call delete_post with ID 1")
        def call_delete_post():
            response = self.api_service.delete_post("1")
            assert response == self.mock_response, "delete_post should return the response"

        @step("Then the request_builder.call_request should be called with correct parameters")
        def verify_call_request():
            self.api_service.request_builder.call_request.assert_called_once()
            call_args = self.api_service.request_builder.call_request.call_args[1]
            assert call_args['method'] == "DELETE"
            assert call_args['url'].endswith("/posts/1")
            assert call_args['verify'] is False

        # Execute the steps
        call_delete_post()
        verify_call_request()

    def test_validate_response_status(self):
        """Test the validate_response_status method."""

        @step("Given a response with status code 200")
        def setup_response():
            self.api_service.response = self.mock_response
            self.mock_response.status_code = 200

        @step("When I call validate_response_status with '200'")
        def call_validate_response_status():
            result = self.api_service.validate_response_status("200")
            assert result is True, "validate_response_status should return True for matching status"

        @step("When I call validate_response_status with '404'")
        def call_validate_response_status_not_matching():
            result = self.api_service.validate_response_status("404")
            assert result is False, "validate_response_status should return False for non-matching status"

        @step("When I call validate_response_status with None response")
        def call_validate_response_status_none():
            self.api_service.response = None
            result = self.api_service.validate_response_status("200")
            assert result is False, "validate_response_status should return False with None response"

        # Execute the steps
        setup_response()
        call_validate_response_status()
        call_validate_response_status_not_matching()
        call_validate_response_status_none()

    def test_get_response_title(self):
        """Test the get_response_title method."""

        @step("Given a response with a title")
        def setup_response():
            self.api_service.response = self.mock_response
            self.mock_response.json.return_value = {"title": "Test Title"}

        @step("When I call get_response_title")
        def call_get_response_title():
            title = self.api_service.get_response_title()
            assert title == "Test Title", "get_response_title should return the title from the response"

        @step("Given a response without a title")
        def setup_response_no_title():
            self.mock_response.json.return_value = {"notTitle": "Something else"}

        @step("When I call get_response_title with no title in response")
        def call_get_response_title_no_title():
            title = self.api_service.get_response_title()
            assert title is None, "get_response_title should return None when title is not in response"

        @step("Given a response that raises an exception on json()")
        def setup_response_exception():
            self.mock_response.json.side_effect = Exception("Test error")

        @step("When I call get_response_title with exception")
        def call_get_response_title_exception():
            title = self.api_service.get_response_title()
            assert title is None, "get_response_title should return None on exception"

        @step("Given a None response")
        def setup_none_response():
            self.api_service.response = None

        @step("When I call get_response_title with None response")
        def call_get_response_title_none():
            title = self.api_service.get_response_title()
            assert title is None, "get_response_title should return None with None response"

        # Execute the steps
        setup_response()
        call_get_response_title()
        setup_response_no_title()
        call_get_response_title_no_title()
        setup_response_exception()
        call_get_response_title_exception()
        setup_none_response()
        call_get_response_title_none()

    def test_has_multiple_posts(self):
        """Test the has_multiple_posts method."""

        @step("Given a response with multiple posts")
        def setup_response_multiple():
            self.api_service.response = self.mock_response
            self.mock_response.json.return_value = [
                {"id": 1, "title": "Post 1"},
                {"id": 2, "title": "Post 2"}
            ]

        @step("When I call has_multiple_posts with multiple posts")
        def call_has_multiple_posts_multiple():
            result = self.api_service.has_multiple_posts()
            assert result is True, "has_multiple_posts should return True with multiple posts"

        @step("Given a response with a single post")
        def setup_response_single():
            self.mock_response.json.return_value = [{"id": 1, "title": "Post 1"}]

        @step("When I call has_multiple_posts with a single post")
        def call_has_multiple_posts_single():
            result = self.api_service.has_multiple_posts()
            assert result is False, "has_multiple_posts should return False with single post"

        @step("Given a response with a non-list result")
        def setup_response_non_list():
            self.mock_response.json.return_value = {"id": 1, "title": "Post 1"}

        @step("When I call has_multiple_posts with non-list result")
        def call_has_multiple_posts_non_list():
            result = self.api_service.has_multiple_posts()
            assert result is False, "has_multiple_posts should return False with non-list result"

        @step("Given a response that raises an exception on json()")
        def setup_response_exception():
            self.mock_response.json.side_effect = Exception("Test error")

        @step("When I call has_multiple_posts with exception")
        def call_has_multiple_posts_exception():
            result = self.api_service.has_multiple_posts()
            assert result is False, "has_multiple_posts should return False on exception"

        @step("Given a None response")
        def setup_none_response():
            self.api_service.response = None

        @step("When I call has_multiple_posts with None response")
        def call_has_multiple_posts_none():
            result = self.api_service.has_multiple_posts()
            assert result is False, "has_multiple_posts should return False with None response"

        # Execute the steps
        setup_response_multiple()
        call_has_multiple_posts_multiple()
        setup_response_single()
        call_has_multiple_posts_single()
        setup_response_non_list()
        call_has_multiple_posts_non_list()
        setup_response_exception()
        call_has_multiple_posts_exception()
        setup_none_response()
        call_has_multiple_posts_none()

    def test_has_new_post_details(self):
        """Test the has_new_post_details method."""

        @step("Given a response with complete post details")
        def setup_response_complete():
            self.api_service.response = self.mock_response
            self.mock_response.json.return_value = {
                "id": 1,
                "title": "Test Title",
                "body": "Test Body",
                "userId": 1
            }

        @step("When I call has_new_post_details with complete details")
        def call_has_new_post_details_complete():
            result = self.api_service.has_new_post_details()
            assert result is True, "has_new_post_details should return True with complete details"

        @step("Given a response with incomplete post details")
        def setup_response_incomplete():
            self.mock_response.json.return_value = {
                "id": 1,
                "title": "Test Title"
                # Missing body and userId
            }

        @step("When I call has_new_post_details with incomplete details")
        def call_has_new_post_details_incomplete():
            result = self.api_service.has_new_post_details()
            assert result is False, "has_new_post_details should return False with incomplete details"

        @step("Given a response that raises an exception on json()")
        def setup_response_exception():
            self.mock_response.json.side_effect = Exception("Test error")

        @step("When I call has_new_post_details with exception")
        def call_has_new_post_details_exception():
            result = self.api_service.has_new_post_details()
            assert result is False, "has_new_post_details should return False on exception"

        @step("Given a None response")
        def setup_none_response():
            self.api_service.response = None

        @step("When I call has_new_post_details with None response")
        def call_has_new_post_details_none():
            result = self.api_service.has_new_post_details()
            assert result is False, "has_new_post_details should return False with None response"

        # Execute the steps
        setup_response_complete()
        call_has_new_post_details_complete()
        setup_response_incomplete()
        call_has_new_post_details_incomplete()
        setup_response_exception()
        call_has_new_post_details_exception()
        setup_none_response()
        call_has_new_post_details_none()

    def test_has_updated_title(self):
        """Test the has_updated_title method."""

        @step("Given a response with matching title")
        def setup_response_matching():
            self.api_service.response = self.mock_response
            self.mock_response.json.return_value = {"title": "Test Title"}

        @step("When I call has_updated_title with matching title")
        def call_has_updated_title_matching():
            result = self.api_service.has_updated_title("Test Title")
            assert result is True, "has_updated_title should return True with matching title"

        @step("When I call has_updated_title with non-matching title")
        def call_has_updated_title_non_matching():
            result = self.api_service.has_updated_title("Different Title")
            assert result is False, "has_updated_title should return False with non-matching title"

        @step("Given a response without a title")
        def setup_response_no_title():
            self.mock_response.json.return_value = {"notTitle": "Something else"}

        @step("When I call has_updated_title with no title in response")
        def call_has_updated_title_no_title():
            result = self.api_service.has_updated_title("Test Title")
            assert result is False, "has_updated_title should return False when title is not in response"

        @step("Given a response that raises an exception on json()")
        def setup_response_exception():
            self.mock_response.json.side_effect = Exception("Test error")

        @step("When I call has_updated_title with exception")
        def call_has_updated_title_exception():
            result = self.api_service.has_updated_title("Test Title")
            assert result is False, "has_updated_title should return False on exception"

        @step("Given a None response")
        def setup_none_response():
            self.api_service.response = None

        @step("When I call has_updated_title with None response")
        def call_has_updated_title_none():
            result = self.api_service.has_updated_title("Test Title")
            assert result is False, "has_updated_title should return False with None response"

        # Execute the steps
        setup_response_matching()
        call_has_updated_title_matching()
        call_has_updated_title_non_matching()
        setup_response_no_title()
        call_has_updated_title_no_title()
        setup_response_exception()
        call_has_updated_title_exception()
        setup_none_response()
        call_has_updated_title_none()


class TestGetServiceConfig:
    """Unit tests for the get_service_config method using pytest."""

    @pytest.fixture
    def api_service(self):
        """Fixture to create a JSONPlaceholderAPI instance."""
        return JSONPlaceholderAPI()

    @patch('features.services.jsonplaceholder_api.ConfigUtils')
    def test_get_service_config_success(self, mock_config_utils, api_service):
        """Test get_service_config when config loading succeeds."""

        @step("Given a mocked ConfigUtils that returns a valid service description")
        def setup_mock():
            # Mock the ConfigUtils instance
            mock_config_instance = mock_config_utils.return_value
            # Mock the get_service_description method
            mock_config_instance.get_service_description.return_value = {
                "method": "GET",
                "endpoint": "/test-endpoint",
                "headers": {"Custom-Header": "Value"}
            }

        @step("When I call get_service_config")
        def call_get_service_config():
            result = api_service.get_service_config("test_service")
            assert result["method"] == "GET"
            assert result["endpoint"] == "/test-endpoint"
            assert result["headers"]["Custom-Header"] == "Value"

        @step("Then ConfigUtils.get_service_description should be called correctly")
        def verify_mock_called():
            mock_config_instance = mock_config_utils.return_value
            mock_config_instance.get_service_description.assert_called_once_with(
                "jsonplaceholder_data.yml", "test_service"
            )

        # Execute the steps
        setup_mock()
        call_get_service_config()
        verify_mock_called()

    @patch('features.services.jsonplaceholder_api.ConfigUtils')
    def test_get_service_config_fallback(self, mock_config_utils, api_service):
        """Test get_service_config when config loading fails."""

        @step("Given a mocked ConfigUtils that raises an exception")
        def setup_mock():
            # Mock the ConfigUtils instance
            mock_config_instance = mock_config_utils.return_value
            # Make get_service_description raise an exception
            mock_config_instance.get_service_description.side_effect = Exception("Config error")

        @step("When I call get_service_config for 'get_post'")
        def call_get_service_config():
            result = api_service.get_service_config("get_post")
            assert result["method"] == "GET"
            assert result["endpoint"] == "/posts/"
            assert "Accept" in result["headers"]

        @step("When I call get_service_config for an unknown service")
        def call_get_service_config_unknown():
            result = api_service.get_service_config("unknown_service")
            assert result == {}

        # Execute the steps
        setup_mock()
        call_get_service_config()
        call_get_service_config_unknown()