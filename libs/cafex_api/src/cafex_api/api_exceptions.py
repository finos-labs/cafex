"""
Module providing specialized exception handling for API operations.

This module extends the core exception handling capabilities with API-specific exception types and
handling patterns.
"""

from cafex_core.utils.exceptions import CoreExceptions


class APIExceptions(CoreExceptions):
    """
    API specific exceptions that inherit from CoreExceptions.

    This class provides specialized exception handling for common API-related
    error scenarios, like null responses, invalid values, missing fields,
    and status code validation.

    All API related custom exceptions should be raised through this class.

    Examples:
        >>> import requests
        >>> import os
        >>> import json
        >>> exceptions = APIExceptions()
        >>> response = requests.get("https://example.com/api/users/1")
        >>>
        >>> # Handle missing required field
        >>> response_data = response.json()
        >>> if 'user_id' not in response_data:
        >>>     exceptions.raise_missing_required_field(
        >>>         field_name='user_id',
        >>>         fail_test=False
        >>>     )
        >>>
        >>> # Validate status code
        >>> if response.status_code != 200:
        >>>     exceptions.raise_invalid_status_code(
        >>>         status_code=response.status_code,
        >>>         expected_code=200
        >>>     )
    """

    def raise_null_response_object(
        self,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """
        Raise exception when response object is null.

        This method handles cases where an API response object is entirely null,
        different from cases where the response exists but contains null values.

        Args:
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Examples:
            >>> import requests
            >>> exceptions = APIExceptions()
            >>>
            >>> # Check if response exists
            >>> def verify_user_response():
            >>>     api_client = requests.Session()
            >>>     response = api_client.get("https://example.com/api/users/1")
            >>>     if not response:
            >>>         exceptions.raise_null_response_object(fail_test=True)
            >>>         return
            >>>
            >>>     # Process response data
            >>>     user_data = response.json()
            >>>     return user_data
        """
        message = "The response object is null"
        self.raise_generic_exception(
            message=message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_null_value(
        self,
        message: str,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """
        Raise exception when a specific value in the API response is null.

        This method handles cases where certain fields or values within an API response
        are null when they are expected to contain data.

        Args:
            message: Custom message describing which value is null
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Examples:
            >>> import requests
            >>> exceptions = APIExceptions()
            >>>
            >>> # Check for null email in user response
            >>> def validate_user_data(user_id):
            >>>     response = requests.get(f"https://example.com/api/users/{user_id}")
            >>>     user_response = response.json()
            >>>
            >>>     if user_response.get('email') is None:
            >>>         exceptions.raise_null_value(
            >>>             message="User email field is null",
            >>>             fail_test=True
            >>>         )
            >>>         return False
            >>>     return True
            >>>
            >>> # Validate API parameters
            >>> def validate_api_parameters(url, payload):
            >>>     if not url:
            >>>         exceptions.raise_null_value(
            >>>             message="API URL cannot be null",
            >>>             fail_test=False
            >>>         )
            >>>         return False
            >>>
            >>>     if not payload:
            >>>         exceptions.raise_null_value(
            >>>             message="Request payload cannot be null",
            >>>             fail_test=False
            >>>         )
            >>>         return False
            >>>
            >>>     return True
        """
        self.raise_generic_exception(
            message=message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_invalid_value(
        self,
        message: str,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """
        Raise exception when an API response contains invalid data.

        This method is used when a value in the API response is present but does not
        meet the expected format, type, or validation criteria.

        Args:
            message: Description of the invalid value and expected criteria
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Examples:
            >>> import requests
            >>> exceptions = APIExceptions()
            >>>
            >>> # Validate order status in API response
            >>> def check_order_status(order_id):
            >>>     response = requests.get(f"https://example.com/api/orders/{order_id}")
            >>>     order_response = response.json()
            >>>     valid_statuses = ['pending', 'processing', 'completed', 'cancelled']
            >>>
            >>>     if 'status' not in order_response:
            >>>         exceptions.raise_missing_required_field('status')
            >>>         return False
            >>>
            >>>     if order_response['status'] not in valid_statuses:
            >>>         exceptions.raise_invalid_value(
            >>>             message="Invalid order status",
            >>>             fail_test=False
            >>>         )
            >>>         return False
            >>>
            >>>     return True
        """
        self.raise_generic_exception(
            message=message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_file_not_found(
        self,
        file_path: str,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """
        Raise exception when a required API-related file is not found.

        This method is used when files required for API operations (like request payloads,
        response templates, or configuration files) are missing from the expected location.

        Args:
            file_path: Path of the missing file
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Examples:
            >>> import os
            >>> import json
            >>> import yaml
            >>> exceptions = APIExceptions()
            >>>
            >>> # Check for required request payload file
            >>> def load_request_payload(test_case):
            >>>     payload_path = f"payloads/{test_case}_payload.json"
            >>>
            >>>     if not os.path.exists(payload_path):
            >>>         exceptions.raise_file_not_found(
            >>>             file_path=payload_path,
            >>>             fail_test=False
            >>>         )
            >>>         return None
            >>>
            >>>     with open(payload_path, 'r', encoding='utf-8') as f:
            >>>         return json.load(f)
            >>>
            >>> # Load API configuration file
            >>> def load_api_config(environment):
            >>>     config_path = f"config/{environment}/api_config.yml"
            >>>
            >>>     if not os.path.exists(config_path):
            >>>         exceptions.raise_file_not_found(
            >>>             file_path=config_path,
            >>>             fail_test=True,
            >>>             insert_report=True
            >>>         )
            >>>         return {}
            >>>
            >>>     with open(config_path, 'r', encoding='utf-8') as f:
            >>>         return yaml.safe_load(f)
        """
        message = f"The file {file_path} is not found"
        self.raise_generic_exception(
            message=message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_invalid_status_code(
        self,
        status_code: int,
        expected_code: int,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """
        Raise exception when API response status code doesn't match expected value.

        This method handles cases where an API returns a different HTTP status code
        than what was expected for the operation, indicating potential API errors
        or unexpected behavior.

        Args:
            status_code: The actual status code received from the API
            expected_code: The status code that was expected
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Examples:
            >>> import requests
            >>> exceptions = APIExceptions()
            >>>
            >>> # Validate successful user creation (201 Created)
            >>> def verify_user_creation(user_data):
            >>>     response = requests.post("https://example.com/api/users", json=user_data)
            >>>     if response.status_code != 201:
            >>>         exceptions.raise_invalid_status_code(
            >>>             status_code=response.status_code,
            >>>             expected_code=201,
            >>>             fail_test=False
            >>>         )
            >>>         return False
            >>>
            >>>     return True
            >>>
            >>> # Validate successful GET request (200 OK)
            >>> def validate_get_response(url, allow_404=False):
            >>>     response = requests.get(url)
            >>>     if response.status_code == 200:
            >>>         return True
            >>>
            >>>     if allow_404 and response.status_code == 404:
            >>>         return False
            >>>
            >>>     exceptions.raise_invalid_status_code(
            >>>         status_code=response.status_code,
            >>>         expected_code=200,
            >>>         fail_test=False
            >>>     )
            >>>     return False
        """
        message = f"Invalid status code. Expected: {expected_code}, Got: {status_code}"
        self.raise_generic_exception(
            message=message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_invalid_response_format(
        self,
        expected_format: str,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """
        Raise exception when API response format is invalid.

        This method is used when the structure or format of the API response
        doesn't match the expected schema or data format (e.g., JSON, XML).

        Args:
            expected_format: Description of the expected response format
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Examples:
            >>> import requests
            >>> exceptions = APIExceptions()
            >>>
            >>> # Validate JSON response format
            >>> def validate_json_response(url):
            >>>     response = requests.get(url)
            >>>     try:
            >>>         response_data = response.json()
            >>>         return response_data
            >>>     except ValueError:
            >>>         exceptions.raise_invalid_response_format(
            >>>             expected_format="JSON object",
            >>>             fail_test=False
            >>>         )
            >>>         return None
            >>>
            >>> # Validate specific response structure
            >>> def validate_user_response_format(user_id):
            >>>     response = requests.get(f"https://example.com/api/users/{user_id}")
            >>>     response_data = response.json()
            >>>     required_fields = ['id', 'name', 'email', 'role']
            >>>
            >>>     if not isinstance(response_data, dict):
            >>>         exceptions.raise_invalid_response_format(
            >>>             expected_format="Dictionary containing user details",
            >>>             fail_test=False
            >>>         )
            >>>         return False
            >>>
            >>>     return True
        """

        message = f"Invalid API response format. Expected: {expected_format}"
        self.raise_generic_exception(
            message=message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_missing_required_field(
        self,
        field_name: str,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """
        Raise exception when a required field is missing from API response.

        This method handles cases where mandatory fields are absent from the API response,
        indicating potential API issues or incomplete data scenarios.

        Args:
            field_name: Name of the missing required field
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Examples:
            >>> import requests
            >>> exceptions = APIExceptions()
            >>>
            >>> # Check for required user ID field
            >>> def validate_user_profile(user_id):
            >>>     response = requests.get(f"https://example.com/api/users/{user_id}")
            >>>     profile_data = response.json()
            >>>
            >>>     if 'user_id' not in profile_data:
            >>>         exceptions.raise_missing_required_field(
            >>>             field_name='user_id',
            >>>             fail_test=True
            >>>         )
            >>>         return False
            >>>
            >>>     return True
            >>>
            >>> # Validate multiple required fields
            >>> def validate_order_data(order_id):
            >>>     response = requests.get(f"https://example.com/api/orders/{order_id}")
            >>>     order_data = response.json()
            >>>     required_fields = ['order_id', 'customer_id', 'items', 'total']
            >>>
            >>>     for field in required_fields:
            >>>         if field not in order_data:
            >>>             exceptions.raise_missing_required_field(
            >>>                 field_name=field,
            >>>                 fail_test=False
            >>>             )
            >>>             return False
            >>>
            >>>     return True
        """
        message = f"Required field missing: {field_name}"
        self.raise_generic_exception(
            message=message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )
