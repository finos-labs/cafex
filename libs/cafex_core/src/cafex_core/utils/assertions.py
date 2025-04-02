"""
This module provides assertion methods for test validation.

It integrates with the Reporting class for comprehensive test result logging.
"""
import ast
from typing import Any

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.reporting_.reporting import Reporting
from cafex_core.singletons_.session_ import SessionStore


class Assertions:
    """Provides assertion methods for test validation.

    Integrates with Reporting class for comprehensive test result
    logging.
    """

    def __init__(self):
        self.reporting = Reporting()
        self.session_store = SessionStore()
        self.logger = CoreLogger(name=__name__).get_logger()

    def _handle_assertion(
            self,
            expected_message: str,
            actual_message: str,
            assertion_type: str = "assert",
            condition: Any = None,
    ) -> bool:
        """Handles assertion logic and reporting.

        Args:
            expected_message: Expected result message
            actual_message: Actual result message
            assertion_type: Type of assertion ('assert' or 'verify')
            condition: Optional condition to evaluate (string condition or boolean)

        Returns:
            bool: Result of the assertion

        Raises:
            AssertionError: If assertion fails and type is 'assert'
        """
        try:
            result = self._evaluate_condition(condition)
            status = "pass" if result else "fail"
            exception_detail = None

            if result:
                if assertion_type == "assert":
                    self.logger.info("Assertion passed: %s", expected_message)
                else:
                    self.logger.info("Verification passed: %s", expected_message)
            else:
                exception_detail = f"Assertion failed: {expected_message}"
                if assertion_type == "assert":
                    self.logger.error("Assertion failed: %s", expected_message)
                else:
                    self.logger.warning("Verification failed: %s", expected_message)

            self.reporting.insert_step(
                expected_message=expected_message,
                actual_message=actual_message,
                status=status,
                step_type=assertion_type,
                exception_detail=exception_detail,
            )

            if not result:
                if assertion_type == "assert":
                    raise AssertionError(f"Assertion failed: {expected_message}")

            return result

        except Exception as e:
            if not isinstance(e, AssertionError):
                self.reporting.insert_step(
                    expected_message=expected_message,
                    actual_message=actual_message,
                    status="fail",
                    step_type=assertion_type,
                    exception_detail=str(e),
                )

            if assertion_type == "assert":
                raise
            return False

    def _evaluate_condition(self, condition):
        """Evaluates a condition for assertions.

        Args:
            condition: Can be None, bool, str, or any value that can be converted to bool

        Returns:
            bool: The evaluated condition result
        """
        if condition is None:
            return True

        if isinstance(condition, bool):
            return condition

        if isinstance(condition, str):
            if condition.strip() == "":
                return True
            try:
                return bool(ast.literal_eval(condition))
            except (SyntaxError, NameError, TypeError, ValueError) as e:
                self.logger.warning("Could not evaluate condition %s: %s", condition, str(e))
                return False

        try:
            return bool(condition)
        except (TypeError, ValueError) as e:
            self.logger.warning("Could not convert condition to bool: %s", str(e))
            return False

    def assert_true(
            self, expected_message: str, actual_message: str, condition: Any = None
    ) -> None:
        """When condition is passed, asserts that the condition is True. When
        condition is not passed, asserts True.

        Args:
            expected_message: Expected result message
            actual_message: Actual result message
            condition: Optional condition to evaluate

        Raises:
            AssertionError: If assertion fails

        Examples:
            # With condition
            assert_true("Expected value is 100", "Actual value is 100", "value == 100")

            # Without condition
            assert_true("Value should be available", "Value is available")
        """
        self._handle_assertion(
            expected_message,
            actual_message,
            "assert",
            condition,
        )

    def verify_true(
            self, expected_message: str, actual_message: str, condition: Any = None
    ) -> bool:
        """When condition is passed, verifies that the condition is True. When
        condition is not passed, verifies True. Does not raise an exception on
        failure.

        Args:
            expected_message: Expected result message
            actual_message: Actual result message
            condition: Optional condition to evaluate

        Returns:
            bool: True if verification passes, False otherwise

        Examples:
            # With condition
            verify_true("Expected value is 100", "Actual value is 100", "value == 100")

            # Without condition
            verify_true("Value should be available", "Value is available")
        """
        return self._handle_assertion(expected_message, actual_message, "verify", condition)

    def assert_false(
            self, expected_message: str, actual_message: str, condition: Any = None
    ) -> None:
        """When condition is passed, asserts that the condition is False. When
        condition is not passed, asserts False.

        Args:
            expected_message: Expected result message
            actual_message: Actual result message
            condition: Optional condition to evaluate

        Raises:
            AssertionError: If assertion fails

        Examples:
            # With condition
            assert_false("Value should not be negative", "Value is positive", "value < 0")

            # Without condition
            assert_false("Value should not be present", "Value is not present")
        """
        inverted_condition = (
            None
            if condition is None
            else (f"not ({condition})" if isinstance(condition, str) else not condition)
        )
        self._handle_assertion(expected_message, actual_message, "assert", inverted_condition)

    def verify_false(
            self, expected_message: str, actual_message: str, condition: Any = None
    ) -> bool:
        """When condition is passed, verifies that the condition is False. When
        condition is not passed, verifies False. Does not raise an exception on
        failure.

        Args:
            expected_message: Expected result message
            actual_message: Actual result message
            condition: Optional condition to evaluate

        Returns:
            bool: True if verification passes, False otherwise

        Examples:
            # With condition
            verify_false("Value should not be negative", "Value is positive", "value < 0")

            # Without condition
            verify_false("Value should not be present", "Value is not present")
        """
        inverted_condition = (
            None
            if condition is None
            else (f"not ({condition})" if isinstance(condition, str) else not condition)
        )
        return self._handle_assertion(
            expected_message, actual_message, "verify", inverted_condition
        )

    def assert_equal(
            self,
            actual: Any,
            expected: Any,
            expected_message: str = None,
            actual_message: str = None,
            actual_message_on_pass: str = None,
            actual_message_on_fail: str = None,
    ) -> None:
        """Asserts that two values are equal. Values must be of the same type.

        Args:
            actual: The actual value
            expected: The expected value
            expected_message: Optional message describing what was expected
            (default: generated from expected value)
            actual_message: Optional default message for actual result
            (default: generated from actual value)
            actual_message_on_pass: Optional custom message to show when assertion passes
            actual_message_on_fail: Optional custom message to show when assertion fails

        Raises:
            AssertionError: If assertion fails or if types don't match

        Examples:
            # With default messages
            assert_equal(value, expected)

            # With custom messages
            assert_equal(
                page.get_notification_message(),
                "Success",
                expected_message="Notification should be displayed",
                actual_message="Notification is NOT displayed",
                actual_message_on_pass="Notification is displayed correctly",
                actual_message_on_fail="Notification text does not match"
        )
        """
        message_expected = expected_message or f"Expected value: {expected}"
        message_actual = actual_message or f"Actual value: {actual}"
        try:
            # Check types first
            if type(expected) is not type(actual):
                error_msg = (
                    "Error: Cannot compare values of different types. "
                    f"Expected type: {type(expected)}, Actual type: {type(actual)}"
                )
                self.reporting.insert_step(
                    expected_message=message_expected,
                    actual_message="Type mismatch in assertion",
                    status="fail",
                    step_type="assert",
                    exception_detail=error_msg,
                )
                raise AssertionError(error_msg)

            # If types match, proceed with value comparison
            result = expected == actual
            final_actual_message = (
                actual_message_on_pass
                if result and actual_message_on_pass is not None
                else (
                    actual_message_on_fail
                    if not result and actual_message_on_fail is not None
                    else message_actual
                )
            )

            self._handle_assertion(
                message_expected, final_actual_message, "assert", condition=result
            )

        except Exception as e:
            if not isinstance(e, AssertionError):
                error_msg = f"Unexpected error during comparison: {str(e)}"
                self.reporting.insert_step(
                    expected_message=message_expected,
                    actual_message="Error in assertion",
                    status="fail",
                    step_type="assert",
                    exception_detail=error_msg,
                )
                raise AssertionError(error_msg)
            raise

    def verify_equal(
            self,
            actual: Any,
            expected: Any,
            expected_message: str = None,
            actual_message: str = None,
            actual_message_on_pass: str = None,
            actual_message_on_fail: str = None,
    ) -> bool:
        """Verifies that two values are equal. Values must be of the same type.
        Does not raise an exception on failure.

        Args:
            actual: The actual value
            expected: The expected value
            expected_message: Optional message describing what was expected
            (default: generated from expected value)
            actual_message: Optional default message for actual result
            (default: generated from actual value)
            actual_message_on_pass: Optional custom message to show when verification passes
            actual_message_on_fail: Optional custom message to show when verification fails

        Returns:
            bool: True if verification passes, False otherwise

        Examples:
            # With default messages
            verify_equal(value, expected)

            # With custom messages
            verify_equal(
                page.get_notification_message(),
                "Success",
                expected_message="Notification should be displayed",
                actual_message="Notification is NOT displayed",
                actual_message_on_pass="Notification is displayed correctly",
                actual_message_on_fail="Notification text does not match"
        )
        """
        message_expected = expected_message or f"Expected value: {expected}"
        message_actual = actual_message or f"Actual value: {actual}"
        try:
            # Check types first
            if type(expected) is not type(actual):
                error_msg = (
                    "Error: Cannot compare values of different types. "
                    f"Expected type: {type(expected)}, Actual type: {type(actual)}"
                )
                self.reporting.insert_step(
                    expected_message=message_expected,
                    actual_message="Type mismatch in verification",
                    status="fail",
                    step_type="verify",
                    exception_detail=error_msg,
                )
                return False

            # If types match, proceed with value comparison
            result = expected == actual
            final_actual_message = (
                actual_message_on_pass
                if result and actual_message_on_pass is not None
                else (
                    actual_message_on_fail
                    if not result and actual_message_on_fail is not None
                    else message_actual
                )
            )

            return self._handle_assertion(
                message_expected, final_actual_message, "verify", condition=result
            )

        except Exception as e:  # Catch any unexpected errors
            error_msg = f"Unexpected error during comparison: {str(e)}"
            self.reporting.insert_step(
                expected_message=message_expected,
                actual_message="Error in verification",
                status="fail",
                step_type="verify",
                exception_detail=error_msg,
            )
            return False

    def assert_not_equal(
            self,
            actual: Any,
            expected: Any,
            expected_message: str = None,
            actual_message: str = None,
            actual_message_on_pass: str = None,
            actual_message_on_fail: str = None,
    ) -> None:
        """Asserts that two values are not equal. Values must be of the same
        type.

        Args:
            actual: The actual value
            expected: The value that should not match
            expected_message: Optional message describing what was expected
            (default: generated from expected value)
            actual_message: Optional default message for actual result
            (default: generated from actual value)
            actual_message_on_pass: Optional custom message to show when assertion passes
            actual_message_on_fail: Optional custom message to show when assertion fails

        Raises:
            AssertionError: If assertion fails or if types don't match

        Examples:
            # With default messages
            assert_not_equal(value, not_expected)

            # With custom messages
            assert_not_equal(
                page.get_status(),
                "Error",
                expected_message="Status should not be Error",
                actual_message="Status is Error",
                actual_message_on_pass="Status is not Error as expected",
                actual_message_on_fail="Status is Error which is not expected"
        )
        """
        message_expected = expected_message or f"Values should not be equal: {expected}"
        message_actual = actual_message or f"Actual value: {actual}"
        try:
            # Check types first
            if type(expected) is not type(actual):
                error_msg = (
                    "Error: Cannot compare values of different types. "
                    f"Expected type: {type(expected)}, Actual type: {type(actual)}"
                )
                self.reporting.insert_step(
                    expected_message=message_expected,
                    actual_message="Type mismatch in assertion",
                    status="fail",
                    step_type="assert",
                    exception_detail=error_msg,
                )
                raise AssertionError(error_msg)

            # If types match, proceed with value comparison
            result = expected != actual
            final_actual_message = (
                actual_message_on_pass
                if result and actual_message_on_pass is not None
                else (
                    actual_message_on_fail
                    if not result and actual_message_on_fail is not None
                    else message_actual
                )
            )

            self._handle_assertion(
                message_expected, final_actual_message, "assert", condition=result
            )

        except Exception as e:
            if not isinstance(e, AssertionError):
                error_msg = f"Unexpected error during comparison: {str(e)}"
                self.reporting.insert_step(
                    expected_message=message_expected,
                    actual_message="Error in assertion",
                    status="fail",
                    step_type="assert",
                    exception_detail=error_msg,
                )
                raise AssertionError(error_msg)
            raise

    def verify_not_equal(
            self,
            actual: Any,
            expected: Any,
            expected_message: str = None,
            actual_message: str = None,
            actual_message_on_pass: str = None,
            actual_message_on_fail: str = None,
    ) -> bool:
        """Verifies that two values are not equal. Values must be of the same
        type. Does not raise an exception on failure.

        Args:
            actual: The actual value
            expected: The value that should not match
            expected_message: Optional message describing what was expected
            (default: generated from expected value)
            actual_message: Optional default message for actual result
            (default: generated from actual value)
            actual_message_on_pass: Optional custom message to show when verification passes
            actual_message_on_fail: Optional custom message to show when verification fails

        Returns:
            bool: True if verification passes, False otherwise

        Examples:
            # With default messages
            verify_not_equal(value, not_expected)

            # With custom messages
            verify_not_equal(
                page.get_status(),
                "Error",
                expected_message="Status should not be Error",
                actual_message="Status is Error",
                actual_message_on_pass="Status is not Error as expected",
                actual_message_on_fail="Status is Error which is not expected"
        )
        """
        message_expected = expected_message or f"Values should not be equal: {expected}"
        message_actual = actual_message or f"Actual value: {actual}"
        try:
            # Check types first
            if type(expected) is not type(actual):
                error_msg = (
                    "Error: Cannot compare values of different types. "
                    f"Expected type: {type(expected)}, Actual type: {type(actual)}"
                )
                self.reporting.insert_step(
                    expected_message=message_expected,
                    actual_message="Type mismatch in verification",
                    status="fail",
                    step_type="verify",
                    exception_detail=error_msg,
                )
                return False

            # If types match, proceed with value comparison
            result = expected != actual
            final_actual_message = (
                actual_message_on_pass
                if result and actual_message_on_pass is not None
                else (
                    actual_message_on_fail
                    if not result and actual_message_on_fail is not None
                    else message_actual
                )
            )

            return self._handle_assertion(
                message_expected, final_actual_message, "verify", condition=result
            )

        except Exception as e:
            error_msg = f"Unexpected error during comparison: {str(e)}"
            self.reporting.insert_step(
                expected_message=message_expected,
                actual_message="Error in verification",
                status="fail",
                step_type="verify",
                exception_detail=error_msg,
            )
            return False
