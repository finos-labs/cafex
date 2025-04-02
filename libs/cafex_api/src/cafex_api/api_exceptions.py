from cafex_core.utils.exceptions import CoreExceptions


class APIExceptions(CoreExceptions):
    """API specific exceptions that inherit from CoreExceptions.

    All API related custom exceptions should be raised through this
    class.
    """

    def __init__(self):
        super().__init__()

    def raise_null_response_object(
        self,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """Raise exception when response object is null.

        This method handles cases where an API response object is entirely null,
        different from cases where the response exists but contains null values.

        Args:
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Example:
            # In your API test class
            def verify_user_response(self):
                response = self.api_client.get_user_details()
                if not response:
                    self.exceptions.raise_null_response_object(fail_test=True)

        Note:
            Use raise_null_response() for modern implementations.
            This method is maintained for backward compatibility.
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
        """Raise exception when a specific value in the API response is null.

        This method handles cases where certain fields or values within an API response
        are null when they are expected to contain data.

        Args:
            message: Custom message describing which value is null
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Example:
            # In your API response validation
            def validate_user_data(self, user_response):
                if user_response.get('email') is None:
                    self.exceptions.raise_null_value(
                        message="User email field is null",
                        fail_test=True
                    )
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
        """Raise exception when an API response contains invalid data.

        This method is used when a value in the API response is present but does not
        meet the expected format, type, or validation criteria.

        Args:
            message: Description of the invalid value and expected criteria
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Example:
            # Validating status in response
            def check_order_status(self, order_response):
                valid_statuses = ['pending', 'completed', 'cancelled']
                if order_response.status not in valid_statuses:
                    self.exceptions.raise_invalid_value(
                        message=f"Invalid order status: {order_response.status}. Expected one of {valid_statuses}",
                        fail_test=False
                    )
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
        """Raise exception when a required API-related file is not found.

        This method is used when files required for API operations (like request payloads,
        response templates, or configuration files) are missing from the expected location.

        Args:
            file_path: Path of the missing file
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Example:
            # Checking for required request payload file
            def load_request_payload(self, test_case):
                payload_path = f"payloads/{test_case}_payload.json"
                if not os.path.exists(payload_path):
                    self.exceptions.raise_file_not_found(
                        file_path=payload_path,
                        fail_test=True
                    )
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
        """Raise exception when API response status code doesn't match expected
        value.

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

        Example:
            # Validating API response status
            def verify_user_creation(self, response):
                if response.status_code != 201:
                    self.exceptions.raise_invalid_status_code(
                        status_code=response.status_code,
                        expected_code=201,
                        fail_test=True
                    )
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
        """Raise exception when API response format is invalid.

        This method is used when the structure or format of the API response
        doesn't match the expected schema or data format (e.g., JSON, XML).

        Args:
            expected_format: Description of the expected response format
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Example:
            # Validating response format
            def validate_response_format(self, response):
                try:
                    response_data = response.json()
                except ValueError:
                    self.exceptions.raise_invalid_response_format(
                        expected_format="JSON object with user details",
                        fail_test=True
                    )
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
        """Raise exception when a required field is missing from API response.

        This method handles cases where mandatory fields are absent from the API response,
        indicating potential API issues or incomplete data scenarios.

        Args:
            field_name: Name of the missing required field
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Example:
            # Checking required fields in user profile response
            def validate_user_profile(self, profile_data):
                if 'user_id' not in profile_data:
                    self.exceptions.raise_missing_required_field(
                        field_name='user_id',
                        fail_test=True
                    )
        """
        message = f"Required field missing in API response: {field_name}"
        self.raise_generic_exception(
            message=message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )
