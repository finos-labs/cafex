class SessionStore:
    """A singleton class for storing variables throughout a session."""

    _instance = None

    def __new__(cls):
        """Ensures only one instance of SessionStore exists.

        Returns:
            SessionStore: The singleton instance.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.storage = {}
            cls._instance.reporting = {"tests": {}}
            cls._instance.current_test = None
            cls._instance.current_step = None
            cls._instance.failed_tests = set()
            cls._instance.error_messages = {}
            cls._instance.base_config = None
        return cls._instance

    def __setattr__(self, name, value):
        """Sets an attribute (session variable) on the SessionStore instance.

        Args:
            name (str): The name of the attribute (variable).
            value: The value to store.
        """
        if name == "storage":  # Protect the internal storage dictionary
            super().__setattr__(name, value)
        else:
            self.storage[name] = value

    def __getattr__(self, name):
        """Retrieves the value of an attribute (session variable).

        Args:
            name (str): The name of the attribute (variable).

        Returns:
            The value of the attribute.

        Raises:
            AttributeError: If the attribute does not exist.
        """
        return self.storage[name]

    def add_error_message(self, error_info: dict) -> None:
        """Add error message for current test.

        Args:
            error_info: Dictionary containing error details
                {
                    'message': str,  # Error message
                    'type': str,     # 'step' or 'assert'
                    'name': str,     # Step or assertion name
                    'phase': str     # test phase when error occurred
                }
        """
        if self.current_test:
            if self.current_test not in self.error_messages:
                self.error_messages[self.current_test] = []
            self.error_messages[self.current_test].append(error_info)

    def get_error_messages(self, test_id: str) -> list:
        """Get all error messages for a test."""
        return self.error_messages.get(test_id, [])

    def clear_error_messages(self, test_id: str) -> None:
        """Clear error messages for a test."""
        if test_id in self.error_messages:
            del self.error_messages[test_id]

    def mark_test_failed(self):
        """Mark current test as failed."""
        if self.current_test:
            self.failed_tests.add(self.current_test)

    def is_current_test_failed(self) -> bool:
        """Check if current test has failed."""
        return self.current_test in self.failed_tests

    def clear_current_test_status(self):
        """Clear the failure status of current test."""
        if self.current_test:
            self.failed_tests.discard(self.current_test)
