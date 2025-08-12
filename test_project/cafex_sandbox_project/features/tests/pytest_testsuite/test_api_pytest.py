"""
Pytest test suite for testing the RequestBuilder functionality with the JSONPlaceholder API.

This module contains pytest tests that use the JSONPlaceholderAPI class to demonstrate
the capabilities of the RequestBuilder module.
"""

import pytest
from cafex_core.reporting_.step_decorator import step
from test_project.cafex_sandbox_project.features.services.jsonplaceholder_api import JSONPlaceholderAPI


class TestJSONPlaceholderAPI:
    """Test suite for JSONPlaceholder API using RequestBuilder."""

    @pytest.fixture(scope="function")
    def api_service(self):
        """Fixture to create a JSONPlaceholderAPI instance for tests."""
        return JSONPlaceholderAPI()

    def test_retrieve_post(self, api_service):
        """Test retrieving a post from JSONPlaceholder API."""

        @step("Given the JSONPlaceholder API is available")
        def verify_api_available():
            assert api_service.check_api_status(), "JSONPlaceholder API is not available"

        @step("When I send a GET request to retrieve post 1")
        def retrieve_post():
            api_service.get_post(1)

        @step("Then the response status code should be 200")
        def verify_status_code():
            assert api_service.validate_response_status("200"), \
                f"Expected status code 200, but got {api_service.response.status_code}"

        @step("And the response should contain the post title")
        def verify_post_title():
            title = api_service.get_response_title()
            assert title is not None, "Response does not contain a title"
            assert isinstance(title, str) and len(title) > 0, "Title is empty or not a string"

        # Execute the steps
        verify_api_available()
        retrieve_post()
        verify_status_code()
        verify_post_title()

    def test_retrieve_non_existent_post(self, api_service):
        """Test retrieving a non-existent post."""

        @step("Given the JSONPlaceholder API is available")
        def verify_api_available():
            assert api_service.check_api_status(), "JSONPlaceholder API is not available"

        @step("When I send a GET request to endpoint /posts/999")
        def retrieve_non_existent_post():
            api_service.send_request_to_endpoint("/posts/999")

        @step("Then the response status code should be 404")
        def verify_status_code():
            assert api_service.validate_response_status("404"), \
                f"Expected status code 404, but got {api_service.response.status_code}"

        # Execute the steps
        verify_api_available()
        retrieve_non_existent_post()
        verify_status_code()

    def test_retrieve_posts_with_query_params(self, api_service):
        """Test retrieving posts with query parameters."""

        @step("Given the JSONPlaceholder API is available")
        def verify_api_available():
            assert api_service.check_api_status(), "JSONPlaceholder API is not available"

        @step("When I send a GET request to endpoint /posts?userId=1")
        def retrieve_posts_with_query():
            api_service.send_request_to_endpoint("/posts?userId=1")

        @step("Then the response status code should be 200")
        def verify_status_code():
            assert api_service.validate_response_status("200"), \
                f"Expected status code 200, but got {api_service.response.status_code}"

        @step("And the response should contain multiple posts")
        def verify_multiple_posts():
            assert api_service.has_multiple_posts(), "Response does not contain multiple posts"

        # Execute the steps
        verify_api_available()
        retrieve_posts_with_query()
        verify_status_code()
        verify_multiple_posts()

    def test_create_new_post(self, api_service):
        """Test creating a new post."""

        @step("Given the JSONPlaceholder API is available")
        def verify_api_available():
            assert api_service.check_api_status(), "JSONPlaceholder API is not available"

        @step("When I create a new post with title 'Test Post' and body 'This is a test post'")
        def create_post():
            api_service.create_post("Test Post", "This is a test post")

        @step("Then the response status code should be 201")
        def verify_status_code():
            assert api_service.validate_response_status("201"), \
                f"Expected status code 201, but got {api_service.response.status_code}"

        @step("And the response should contain the new post details")
        def verify_new_post_details():
            assert api_service.has_new_post_details(), "Response does not contain new post details"
            title = api_service.get_response_title()
            assert title == "Test Post", f"Expected title 'Test Post', but got '{title}'"

        # Execute the steps
        verify_api_available()
        create_post()
        verify_status_code()
        verify_new_post_details()

    def test_update_existing_post(self, api_service):
        """Test updating an existing post."""

        @step("Given the JSONPlaceholder API is available")
        def verify_api_available():
            assert api_service.check_api_status(), "JSONPlaceholder API is not available"

        @step("When I update post 1 with title 'Updated Title'")
        def update_post():
            api_service.update_post("1", "Updated Title")

        @step("Then the response status code should be 200")
        def verify_status_code():
            assert api_service.validate_response_status("200"), \
                f"Expected status code 200, but got {api_service.response.status_code}"

        @step("And the response should contain the updated title")
        def verify_updated_title():
            assert api_service.has_updated_title("Updated Title"), \
                "Response does not contain the updated title"

        # Execute the steps
        verify_api_available()
        update_post()
        verify_status_code()
        verify_updated_title()

    def test_delete_post(self, api_service):
        """Test deleting a post."""

        @step("Given the JSONPlaceholder API is available")
        def verify_api_available():
            assert api_service.check_api_status(), "JSONPlaceholder API is not available"

        @step("When I delete post 1")
        def delete_post():
            api_service.delete_post("1")

        @step("Then the response status code should be 200")
        def verify_status_code():
            assert api_service.validate_response_status("200"), \
                f"Expected status code 200, but got {api_service.response.status_code}"

        # Execute the steps
        verify_api_available()
        delete_post()
        verify_status_code()


class TestRequestBuilderAdvanced:
    """Advanced test cases for RequestBuilder functionality."""

    @pytest.fixture(scope="function")
    def api_service(self):
        """Fixture to create a JSONPlaceholderAPI instance for tests."""
        return JSONPlaceholderAPI()

    def test_multiple_endpoints(self, api_service):
        """Test accessing multiple different endpoints."""

        endpoints = [
            "/posts/1",
            "/comments/1",
            "/users/1"
        ]

        @step("Given the JSONPlaceholder API is available")
        def verify_api_available():
            assert api_service.check_api_status(), "JSONPlaceholder API is not available"

        @step("When I send requests to multiple endpoints")
        def access_multiple_endpoints():
            for endpoint in endpoints:
                api_service.send_request_to_endpoint(endpoint)
                assert api_service.validate_response_status("200"), \
                    f"Expected status code 200 for endpoint {endpoint}, but got {api_service.response.status_code}"

        # Execute the steps
        verify_api_available()
        access_multiple_endpoints()

    def test_error_handling_invalid_url(self, api_service):
        """Test error handling with an invalid URL."""

        @step("Given the JSONPlaceholder API is available")
        def verify_api_available():
            assert api_service.check_api_status(), "JSONPlaceholder API is not available"

        @step("When I send a request to an invalid endpoint")
        def send_to_invalid_endpoint():
            api_service.send_request_to_endpoint("/nonexistent/endpoint")

        @step("Then the response status code should be 404")
        def verify_status_code():
            assert api_service.validate_response_status("404"), \
                f"Expected status code 404, but got {api_service.response.status_code}"

        # Execute the steps
        verify_api_available()
        send_to_invalid_endpoint()
        verify_status_code()