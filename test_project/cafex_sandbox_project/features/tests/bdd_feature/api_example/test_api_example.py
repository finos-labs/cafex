"""
Step definitions for the JSONPlaceholder API test scenarios.

This module contains the pytest-bdd step definitions for the JSONPlaceholder API test scenarios.
"""

from pytest_bdd import (
    given,
    scenario,
    then,
    when,
    parsers,
)

from test_project.cafex_sandbox_project.features.services.jsonplaceholder_api import JSONPlaceholderAPI

# Initialize the API service
api_service = JSONPlaceholderAPI()


# Scenario functions
@scenario('api_example.feature', 'Retrieve post details from JSONPlaceholder')
def test_retrieve_post_details():
    """Test retrieving post details from JSONPlaceholder API."""
    pass


@scenario('api_example.feature', 'Retrieve non-existent post')
def test_retrieve_non_existent_post():
    """Test retrieving a non-existent post."""
    pass


@scenario('api_example.feature', 'Retrieve posts with query parameters')
def test_retrieve_posts_with_query_parameters():
    """Test retrieving posts with query parameters."""
    pass


@scenario('api_example.feature', 'Create a new post')
def test_create_new_post():
    """Test creating a new post."""
    pass


@scenario('api_example.feature', 'Update an existing post')
def test_update_existing_post():
    """Test updating an existing post."""
    pass


@scenario('api_example.feature', 'Delete a post')
def test_delete_post():
    """Test deleting a post."""
    pass


# Given steps
@given("the JSONPlaceholder API is available")
def the_json_placeholder_api_is_available():
    """Check if the JSONPlaceholder API is available."""
    assert api_service.check_api_status(), "JSONPlaceholder API is not available"


# When steps
@when(parsers.parse("I send a GET request to retrieve post {post_id:d}"))
def send_get_request_to_retrieve_post(post_id):
    """Send a GET request to retrieve a specific post."""
    api_service.get_post(post_id)


@when(parsers.parse('I send a GET request to endpoint "{endpoint}"'))
def send_get_request_to_endpoint(endpoint):
    """Send a GET request to a specific endpoint."""
    api_service.send_request_to_endpoint(endpoint)


@when(parsers.parse('I create a new post with title "{title}" and body "{body}"'))
def create_new_post(title, body):
    """Create a new post with the given title and body."""
    api_service.create_post(title, body)


@when(parsers.parse('I update post "{post_id}" with title "{title}"'))
def update_post(post_id, title):
    """Update a post with the given ID and title."""
    api_service.update_post(post_id, title)


@when(parsers.parse('I delete post "{post_id}"'))
def delete_post(post_id):
    """Delete a post with the given ID."""
    api_service.delete_post(post_id)


# Then steps
@then(parsers.parse('the response status code should be "{status_code}"'))
def verify_response_status_code(status_code):
    """Verify the response status code."""
    assert api_service.validate_response_status(status_code), \
        f"Expected status code {status_code}, but got {api_service.response.status_code}"


@then("the response should contain the post title")
def verify_response_contains_post_title():
    """Verify the response contains the post title."""
    title = api_service.get_response_title()
    assert title is not None, "Response does not contain a title"
    assert isinstance(title, str) and len(title) > 0, "Title is empty or not a string"


@then("the response should contain multiple posts")
def verify_response_contains_multiple_posts():
    """Verify the response contains multiple posts."""
    assert api_service.has_multiple_posts(), "Response does not contain multiple posts"


@then("the response should contain the new post details")
def verify_response_contains_new_post_details():
    """Verify the response contains the new post details."""
    assert api_service.has_new_post_details(), "Response does not contain new post details"


@then("the response should contain the updated title")
def verify_response_contains_updated_title():
    """Verify the response contains the updated title."""
    assert api_service.has_updated_title("Updated Title"), \
        "Response does not contain the updated title"