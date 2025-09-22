"""
Service class for interacting with the JSONPlaceholder API.

This module demonstrates how to use the RequestBuilder from the CAFEX framework
to interact with a public REST API.
"""

import json
import urllib3
from cafex_core.logging.logger_ import CoreLogger
from cafex_core.utils.config_utils import ConfigUtils
from cafex import CafeXAPI

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class JSONPlaceholderAPI:
    """Service class for the JSONPlaceholder API.

    This class provides methods for interacting with the JSONPlaceholder API
    using the RequestBuilder from the CAFEX framework.
    """

    def __init__(self):
        """Initialize the JSONPlaceholderAPI class."""
        # self.request_builder = RequestBuilder()
        self.logger = CoreLogger(name=__name__).get_logger()
        self.config_utils = ConfigUtils("jsonplaceholder_api.yml")
        self.base_url = "https://jsonplaceholder.typicode.com"
        self.response = None

    def get_service_config(self, service_name):
        """Get service configuration from the YML file.

        Args:
            service_name (str): The name of the service configuration to retrieve.

        Returns:
            dict: The service configuration.
        """
        try:
            # Try to get the service description from the YML file
            service_desc = self.config_utils.get_service_description(
                "jsonplaceholder_data.yml", service_name
            )
            return service_desc
        except Exception as e:
            self.logger.warning(f"Could not load service config from YML: {str(e)}")
            # Fallback to hardcoded configurations
            configs = {
                "get_post": {
                    "method": "GET",
                    "endpoint": "/posts/",
                    "headers": {"Accept": "application/json"}
                },
                "create_post": {
                    "method": "POST",
                    "endpoint": "/posts",
                    "headers": {"Content-Type": "application/json", "Accept": "application/json"}
                },
                "update_post": {
                    "method": "PATCH",
                    "endpoint": "/posts/",
                    "headers": {"Content-Type": "application/json", "Accept": "application/json"}
                },
                "delete_post": {
                    "method": "DELETE",
                    "endpoint": "/posts/",
                    "headers": {"Accept": "application/json"}
                }
            }
            return configs.get(service_name, {})

    def check_api_status(self):
        """Check if the JSONPlaceholder API is available.

        Returns:
            bool: True if the API is available, False otherwise.
        """
        try:
            url = f"{self.base_url}/posts/1"
            headers = {"Accept": "application/json"}
            response = CafeXAPI().call_request(
                method="GET",
                url=url,
                headers=headers,
                verify=False  # Important: Disable SSL verification for test purposes
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Error checking API status: {str(e)}")
            return False

    def get_post(self, post_id):
        """Retrieve a specific post by ID.

        Args:
            post_id (int): The ID of the post to retrieve.

        Returns:
            requests.Response: The response from the API.
        """
        config = self.get_service_config("get_post")
        url = f"{self.base_url}{config['endpoint']}{post_id}"
        headers = config.get("headers", {"Accept": "application/json"})

        self.response = CafeXAPI().call_request(
            method=config.get("method", "GET"),
            url=url,
            headers=headers,
            verify=False  # Disable SSL verification for test purposes
        )

        return self.response

    def send_request_to_endpoint(self, endpoint):
        """Send a GET request to a specific endpoint.

        Args:
            endpoint (str): The endpoint to send the request to.

        Returns:
            requests.Response: The response from the API.
        """
        url = f"{self.base_url}{endpoint}"
        headers = {"Accept": "application/json"}

        self.response = CafeXAPI().call_request(
            method="GET",
            url=url,
            headers=headers,
            verify=False  # Disable SSL verification for test purposes
        )

        return self.response

    def create_post(self, title, body):
        """Create a new post.

        Args:
            title (str): The title of the new post.
            body (str): The body content of the new post.

        Returns:
            requests.Response: The response from the API.
        """
        config = self.get_service_config("create_post")
        url = f"{self.base_url}{config['endpoint']}"
        headers = config.get("headers", {"Content-Type": "application/json", "Accept": "application/json"})

        payload = json.dumps({
            "title": title,
            "body": body,
            "userId": 1
        })

        self.response = CafeXAPI().call_request(
            method=config.get("method", "POST"),
            url=url,
            headers=headers,
            payload=payload,
            verify=False  # Disable SSL verification for test purposes
        )

        return self.response

    def update_post(self, post_id, title):
        """Update an existing post.

        Args:
            post_id (str): The ID of the post to update.
            title (str): The new title for the post.

        Returns:
            requests.Response: The response from the API.
        """
        config = self.get_service_config("update_post")
        url = f"{self.base_url}{config['endpoint']}{post_id}"
        headers = config.get("headers", {"Content-Type": "application/json", "Accept": "application/json"})

        payload = json.dumps({
            "title": title
        })

        self.response = CafeXAPI().call_request(
            method=config.get("method", "PATCH"),
            url=url,
            headers=headers,
            payload=payload,
            verify=False  # Disable SSL verification for test purposes
        )

        return self.response

    def delete_post(self, post_id):
        """Delete a post.

        Args:
            post_id (str): The ID of the post to delete.

        Returns:
            requests.Response: The response from the API.
        """
        config = self.get_service_config("delete_post")
        url = f"{self.base_url}{config['endpoint']}{post_id}"
        headers = config.get("headers", {"Accept": "application/json"})

        self.response = CafeXAPI().call_request(
            method=config.get("method", "DELETE"),
            url=url,
            headers=headers,
            verify=False  # Disable SSL verification for test purposes
        )

        return self.response

    def validate_response_status(self, expected_status):
        """Validate the response status code.

        Args:
            expected_status (str): The expected status code.

        Returns:
            bool: True if the status code matches, False otherwise.
        """
        if self.response is None:
            self.logger.error("No response to validate")
            return False

        actual_status = str(self.response.status_code)
        return actual_status == expected_status

    def get_response_title(self):
        """Get the title from the response.

        Returns:
            str: The title from the response, or None if not found.
        """
        if self.response is None:
            self.logger.error("No response to get title from")
            return None

        try:
            response_json = self.response.json()
            return response_json.get("title")
        except Exception as e:
            self.logger.error(f"Error getting title from response: {str(e)}")
            return None

    def has_multiple_posts(self):
        """Check if the response contains multiple posts.

        Returns:
            bool: True if the response contains multiple posts, False otherwise.
        """
        if self.response is None:
            self.logger.error("No response to check for multiple posts")
            return False

        try:
            response_json = self.response.json()
            return isinstance(response_json, list) and len(response_json) > 1
        except Exception as e:
            self.logger.error(f"Error checking for multiple posts: {str(e)}")
            return False

    def has_new_post_details(self):
        """Check if the response contains the details of a new post.

        Returns:
            bool: True if the response contains new post details, False otherwise.
        """
        if self.response is None:
            self.logger.error("No response to check for new post details")
            return False

        try:
            response_json = self.response.json()
            return all(key in response_json for key in ["id", "title", "body", "userId"])
        except Exception as e:
            self.logger.error(f"Error checking for new post details: {str(e)}")
            return False

    def has_updated_title(self, title):
        """Check if the response contains the updated title.

        Args:
            title (str): The title to check for.

        Returns:
            bool: True if the response contains the updated title, False otherwise.
        """
        if self.response is None:
            self.logger.error("No response to check for updated title")
            return False

        try:
            response_json = self.response.json()
            return response_json.get("title") == title
        except Exception as e:
            self.logger.error(f"Error checking for updated title: {str(e)}")
            return False