import unittest
from unittest.mock import MagicMock, patch
from cafex_core.utils.assertions import Assertions


class TestHandleAssertion(unittest.TestCase):
    def setUp(self):
        self.assertions = Assertions()
        self.assertions.logger = MagicMock()
        self.assertions.reporting = MagicMock()

    @patch.object(Assertions, '_evaluate_condition', return_value=True)
    def test_assertion_pass(self, mock_evaluate_condition):
        result = self.assertions._handle_assertion(
            expected_message="Expected condition is True",
            actual_message="Condition is True",
            assertion_type="assert",
            condition=True
        )
        self.assertTrue(result)
        # Adjust the assertion to match the actual call with placeholders
        self.assertions.logger.info.assert_called_with("Assertion passed: %s", "Expected condition is True")
        self.assertions.reporting.insert_step.assert_called_once()

    @patch.object(Assertions, '_evaluate_condition', return_value=False)
    def test_assertion_fail(self, mock_evaluate_condition):
        with self.assertRaises(AssertionError):
            self.assertions._handle_assertion(
                expected_message="Expected condition is True",
                actual_message="Condition is False",
                assertion_type="assert",
                condition=False
            )
        self.assertions.logger.error.assert_called_with('Assertion failed: %s', 'Expected condition is True')
        self.assertions.reporting.insert_step.assert_called_once()

    @patch.object(Assertions, '_evaluate_condition', return_value=True)
    def test_verification_pass(self, mock_evaluate_condition):
        result = self.assertions._handle_assertion(
            expected_message="Expected condition is True",
            actual_message="Condition is True",
            assertion_type="verify",
            condition=True
        )
        self.assertTrue(result)
        self.assertions.logger.info.assert_called_with('Verification passed: %s', 'Expected condition is True')
        self.assertions.reporting.insert_step.assert_called_once()

    @patch.object(Assertions, '_evaluate_condition', return_value=False)
    def test_verification_fail(self, mock_evaluate_condition):
        result = self.assertions._handle_assertion(
            expected_message="Expected condition is True",
            actual_message="Condition is False",
            assertion_type="verify",
            condition=False
        )
        self.assertFalse(result)
        self.assertions.logger.warning.assert_called_with('Verification failed: %s', 'Expected condition is True')
        self.assertions.reporting.insert_step.assert_called_once()

    @patch.object(Assertions, '_evaluate_condition', side_effect=Exception("Evaluation error"))
    def test_exception_handling_in_assertion(self, mock_evaluate_condition):
        with self.assertRaises(Exception) as context:
            self.assertions._handle_assertion(
                expected_message="Expected condition is True",
                actual_message="Condition is False",
                assertion_type="assert",
                condition="invalid_condition"
            )
        self.assertEqual(str(context.exception), "Evaluation error")
        self.assertions.reporting.insert_step.assert_called_once()

    @patch.object(Assertions, '_evaluate_condition', side_effect=Exception("Evaluation error"))
    def test_exception_handling_in_verification(self, mock_evaluate_condition):
        result = self.assertions._handle_assertion(
            expected_message="Expected condition is True",
            actual_message="Condition is False",
            assertion_type="verify",
            condition="invalid_condition"
        )
        self.assertFalse(result)
        self.assertions.reporting.insert_step.assert_called_once()

    def test_condition_none(self):
        # Test when condition is None
        result = self.assertions._evaluate_condition(None)
        self.assertTrue(result)

    def test_condition_boolean_true(self):
        # Test when condition is a boolean True
        result = self.assertions._evaluate_condition(True)
        self.assertTrue(result)

    def test_condition_boolean_false(self):
        # Test when condition is a boolean False
        result = self.assertions._evaluate_condition(False)
        self.assertFalse(result)

    def test_condition_empty_string(self):
        # Test when condition is an empty string
        result = self.assertions._evaluate_condition("")
        self.assertTrue(result)

    def test_condition_invalid_string(self):
        # Test when condition is an invalid string
        result = self.assertions._evaluate_condition("invalid_condition")
        self.assertFalse(result)
        self.assertions.logger.warning.assert_called_with(
            "Could not evaluate condition %s: %s", "invalid_condition", unittest.mock.ANY
        )

    def test_condition_non_string(self):
        # Test when condition is a non-string, non-boolean value
        result = self.assertions._evaluate_condition(10)
        self.assertTrue(result)

    def test_condition_raises_type_error(self):
        # Test when condition raises a TypeError during bool conversion
        class RaisesTypeError:
            def __bool__(self):
                raise TypeError("Cannot convert to bool")

        result = self.assertions._evaluate_condition(RaisesTypeError())
        self.assertFalse(result)
        self.assertions.logger.warning.assert_called_with(
            "Could not convert condition to bool: %s", unittest.mock.ANY
        )

    def test_assert_true_with_condition(self):
        # Test when a condition is passed
        with patch.object(self.assertions, '_handle_assertion') as mock_handle_assertion:
            self.assertions.assert_true(
                expected_message="Expected value is 100",
                actual_message="Actual value is 100",
                condition="1 == 1"
            )
            mock_handle_assertion.assert_called_once_with(
                "Expected value is 100",
                "Actual value is 100",
                "assert",
                "1 == 1"
            )

    def test_assert_true_without_condition(self):
        # Test when no condition is passed
        with patch.object(self.assertions, '_handle_assertion') as mock_handle_assertion:
            self.assertions.assert_true(
                expected_message="Value should be available",
                actual_message="Value is available"
            )
            mock_handle_assertion.assert_called_once_with(
                "Value should be available",
                "Value is available",
                "assert",
                None
            )

    def test_verify_true_with_condition(self):
        # Test when a condition is passed
        with patch.object(self.assertions, '_handle_assertion', return_value=True) as mock_handle_assertion:
            result = self.assertions.verify_true(
                expected_message="Expected value is 100",
                actual_message="Actual value is 100",
                condition="1 == 1"
            )
            self.assertTrue(result)
            mock_handle_assertion.assert_called_once_with(
                "Expected value is 100",
                "Actual value is 100",
                "verify",
                "1 == 1"
            )

    def test_verify_true_without_condition(self):
        # Test when no condition is passed
        with patch.object(self.assertions, '_handle_assertion', return_value=True) as mock_handle_assertion:
            result = self.assertions.verify_true(
                expected_message="Value should be available",
                actual_message="Value is available"
            )
            self.assertTrue(result)
            mock_handle_assertion.assert_called_once_with(
                "Value should be available",
                "Value is available",
                "verify",
                None
            )

    def test_assert_false_with_condition(self):
        # Test when a condition is passed
        with patch.object(self.assertions, '_handle_assertion') as mock_handle_assertion:
            self.assertions.assert_false(
                expected_message="Value should not be negative",
                actual_message="Value is positive",
                condition="value < 0"
            )
            mock_handle_assertion.assert_called_once_with(
                "Value should not be negative",
                "Value is positive",
                "assert",
                "not (value < 0)"
            )

    def test_assert_false_without_condition(self):
        # Test when no condition is passed
        with patch.object(self.assertions, '_handle_assertion') as mock_handle_assertion:
            self.assertions.assert_false(
                expected_message="Value should not be present",
                actual_message="Value is not present"
            )
            mock_handle_assertion.assert_called_once_with(
                "Value should not be present",
                "Value is not present",
                "assert",
                None
            )

    def test_verify_false_with_condition(self):
        # Test when a condition is passed
        with patch.object(self.assertions, '_handle_assertion', return_value=True) as mock_handle_assertion:
            result = self.assertions.verify_false(
                expected_message="Value should not be negative",
                actual_message="Value is positive",
                condition="value < 0"
            )
            self.assertTrue(result)
            mock_handle_assertion.assert_called_once_with(
                "Value should not be negative",
                "Value is positive",
                "verify",
                "not (value < 0)"
            )

    def test_verify_false_without_condition(self):
        # Test when no condition is passed
        with patch.object(self.assertions, '_handle_assertion', return_value=True) as mock_handle_assertion:
            result = self.assertions.verify_false(
                expected_message="Value should not be present",
                actual_message="Value is not present"
            )
            self.assertTrue(result)
            mock_handle_assertion.assert_called_once_with(
                "Value should not be present",
                "Value is not present",
                "verify",
                None
            )

    @patch.object(Assertions, '_handle_assertion')
    def test_assert_equal_pass(self, mock_handle_assertion):
        # Test when values are equal
        self.assertions.assert_equal(
            actual=100,
            expected=100,
            expected_message="Values should be equal",
            actual_message_on_pass="Values are equal as expected"
        )
        mock_handle_assertion.assert_called_once_with(
            "Values should be equal",
            "Values are equal as expected",
            "assert",
            condition=True
        )

    @patch.object(Assertions, '_handle_assertion', side_effect=AssertionError("Values are not equal"))
    def test_assert_equal_fail(self, mock_handle_assertion):
        # Test when values are not equal
        with self.assertRaises(AssertionError):
            self.assertions.assert_equal(
                actual=100,
                expected=200,
                expected_message="Values should be equal",
                actual_message_on_fail="Values are not equal"
            )
        mock_handle_assertion.assert_called_once_with(
            "Values should be equal",
            "Values are not equal",
            "assert",
            condition=False
        )

    def test_assert_equal_type_mismatch(self):
        # Test when types of values are different
        with self.assertRaises(AssertionError) as context:
            self.assertions.assert_equal(
                actual=100,
                expected="100",
                expected_message="Values should be equal"
            )
        self.assertIn("Cannot compare values of different types", str(context.exception))
        self.assertions.reporting.insert_step.assert_called_once_with(
            expected_message="Values should be equal",
            actual_message="Type mismatch in assertion",
            status="fail",
            step_type="assert",
            exception_detail=unittest.mock.ANY
        )

    @patch.object(Assertions, '_handle_assertion')
    def test_assert_equal_with_default_messages(self, mock_handle_assertion):
        # Test with default messages
        self.assertions.assert_equal(
            actual=42,
            expected=42
        )
        mock_handle_assertion.assert_called_once_with(
            "Expected value: 42",
            "Actual value: 42",
            "assert",
            condition=True
        )

    @patch.object(Assertions, '_handle_assertion', return_value=True)
    def test_verify_equal_pass(self, mock_handle_assertion):
        # Test when values are equal
        result = self.assertions.verify_equal(
            actual=100,
            expected=100,
            expected_message="Values should be equal",
            actual_message_on_pass="Values are equal as expected"
        )
        self.assertTrue(result)
        mock_handle_assertion.assert_called_once_with(
            "Values should be equal",
            "Values are equal as expected",
            "verify",
            condition=True
        )

    @patch.object(Assertions, '_handle_assertion', return_value=False)
    def test_verify_equal_fail(self, mock_handle_assertion):
        # Test when values are not equal
        result = self.assertions.verify_equal(
            actual=100,
            expected=200,
            expected_message="Values should be equal",
            actual_message_on_fail="Values are not equal"
        )
        self.assertFalse(result)
        mock_handle_assertion.assert_called_once_with(
            "Values should be equal",
            "Values are not equal",
            "verify",
            condition=False
        )

    def test_verify_equal_type_mismatch(self):
        # Test when types of values are different
        result = self.assertions.verify_equal(
            actual=100,
            expected="100",
            expected_message="Values should be equal"
        )
        self.assertFalse(result)
        self.assertions.reporting.insert_step.assert_called_once_with(
            expected_message="Values should be equal",
            actual_message="Type mismatch in verification",
            status="fail",
            step_type="verify",
            exception_detail=unittest.mock.ANY
        )

    @patch.object(Assertions, '_handle_assertion', return_value=True)
    def test_verify_equal_with_default_messages(self, mock_handle_assertion):
        # Test with default messages
        result = self.assertions.verify_equal(
            actual=42,
            expected=42
        )
        self.assertTrue(result)
        mock_handle_assertion.assert_called_once_with(
            "Expected value: 42",
            "Actual value: 42",
            "verify",
            condition=True
        )

    @patch.object(Assertions, '_handle_assertion')
    def test_assert_not_equal_pass(self, mock_handle_assertion):
        # Test when values are not equal
        self.assertions.assert_not_equal(
            actual=100,
            expected=200,
            expected_message="Values should not be equal",
            actual_message_on_pass="Values are not equal as expected"
        )
        mock_handle_assertion.assert_called_once_with(
            "Values should not be equal",
            "Values are not equal as expected",
            "assert",
            condition=True
        )

    @patch.object(Assertions, '_handle_assertion', side_effect=AssertionError("Values are equal"))
    def test_assert_not_equal_fail(self, mock_handle_assertion):
        # Test when values are equal
        with self.assertRaises(AssertionError):
            self.assertions.assert_not_equal(
                actual=100,
                expected=100,
                expected_message="Values should not be equal",
                actual_message_on_fail="Values are equal which is not expected"
            )
        mock_handle_assertion.assert_called_once_with(
            "Values should not be equal",
            "Values are equal which is not expected",
            "assert",
            condition=False
        )

    def test_assert_not_equal_type_mismatch(self):
        # Test when types of values are different
        with self.assertRaises(AssertionError) as context:
            self.assertions.assert_not_equal(
                actual=100,
                expected="100",
                expected_message="Values should not be equal"
            )
        self.assertIn("Cannot compare values of different types", str(context.exception))
        self.assertions.reporting.insert_step.assert_called_once_with(
            expected_message="Values should not be equal",
            actual_message="Type mismatch in assertion",
            status="fail",
            step_type="assert",
            exception_detail=unittest.mock.ANY
        )

    @patch.object(Assertions, '_handle_assertion')
    def test_assert_not_equal_with_default_messages(self, mock_handle_assertion):
        # Test with default messages
        self.assertions.assert_not_equal(
            actual=42,
            expected=100
        )
        mock_handle_assertion.assert_called_once_with(
            "Values should not be equal: 100",
            "Actual value: 42",
            "assert",
            condition=True
        )
    @patch.object(Assertions, '_handle_assertion', return_value=True)
    def test_verify_not_equal_pass(self, mock_handle_assertion):
        # Test when values are not equal
        result = self.assertions.verify_not_equal(
            actual=100,
            expected=200,
            expected_message="Values should not be equal",
            actual_message_on_pass="Values are not equal as expected"
        )
        self.assertTrue(result)
        mock_handle_assertion.assert_called_once_with(
            "Values should not be equal",
            "Values are not equal as expected",
            "verify",
            condition=True
        )

    @patch.object(Assertions, '_handle_assertion', return_value=False)
    def test_verify_not_equal_fail(self, mock_handle_assertion):
        # Test when values are equal
        result = self.assertions.verify_not_equal(
            actual=100,
            expected=100,
            expected_message="Values should not be equal",
            actual_message_on_fail="Values are equal which is not expected"
        )
        self.assertFalse(result)
        mock_handle_assertion.assert_called_once_with(
            "Values should not be equal",
            "Values are equal which is not expected",
            "verify",
            condition=False
        )

    def test_verify_not_equal_type_mismatch(self):
        # Test when types of values are different
        result = self.assertions.verify_not_equal(
            actual=100,
            expected="100",
            expected_message="Values should not be equal"
        )
        self.assertFalse(result)
        self.assertions.reporting.insert_step.assert_called_once_with(
            expected_message="Values should not be equal",
            actual_message="Type mismatch in verification",
            status="fail",
            step_type="verify",
            exception_detail=unittest.mock.ANY
        )

    @patch.object(Assertions, '_handle_assertion', return_value=True)
    def test_verify_not_equal_with_default_messages(self, mock_handle_assertion):
        # Test with default messages
        result = self.assertions.verify_not_equal(
            actual=42,
            expected=100
        )
        self.assertTrue(result)
        mock_handle_assertion.assert_called_once_with(
            "Values should not be equal: 100",
            "Actual value: 42",
            "verify",
            condition=True
        )

    @patch.object(Assertions, '_handle_assertion', side_effect=Exception("Unexpected error"))
    def test_verify_not_equal_unexpected_exception(self, mock_handle_assertion):
        # Test when an unexpected exception occurs
        result = self.assertions.verify_not_equal(
            actual=100,
            expected=200,
            expected_message="Values should not be equal"
        )
        self.assertFalse(result)
        self.assertions.reporting.insert_step.assert_called_once_with(
            expected_message="Values should not be equal",
            actual_message="Error in verification",
            status="fail",
            step_type="verify",
            exception_detail="Unexpected error during comparison: Unexpected error"
        )

    @patch.object(Assertions, '_handle_assertion', side_effect=Exception("Unexpected error"))
    def test_assert_not_equal_unexpected_exception(self, mock_handle_assertion):
        # Test when an unexpected exception occurs
        with self.assertRaises(AssertionError) as context:
            self.assertions.assert_not_equal(
                actual=100,
                expected=200,
                expected_message="Values should not be equal"
            )
        self.assertIn("Unexpected error during comparison", str(context.exception))
        self.assertions.reporting.insert_step.assert_called_once_with(
            expected_message="Values should not be equal",
            actual_message="Error in assertion",
            status="fail",
            step_type="assert",
            exception_detail="Unexpected error during comparison: Unexpected error"
        )

    @patch.object(Assertions, '_handle_assertion', side_effect=Exception("Unexpected error"))
    def test_verify_equal_unexpected_exception(self, mock_handle_assertion):
        # Test when an unexpected exception occurs in verify_equal
        result = self.assertions.verify_equal(
            actual=100,
            expected=200,
            expected_message="Values should be equal"
        )
        self.assertFalse(result)
        self.assertions.reporting.insert_step.assert_called_once_with(
            expected_message="Values should be equal",
            actual_message="Error in verification",
            status="fail",
            step_type="verify",
            exception_detail="Unexpected error during comparison: Unexpected error"
        )

    @patch.object(Assertions, '_handle_assertion', side_effect=Exception("Unexpected error"))
    def test_assert_not_equal_unexpected_exception(self, mock_handle_assertion):
        # Test when an unexpected exception occurs
        with self.assertRaises(AssertionError) as context:
            self.assertions.assert_not_equal(
                actual=100,
                expected=200,
                expected_message="Values should not be equal"
            )
        self.assertIn("Unexpected error during comparison", str(context.exception))
        self.assertions.reporting.insert_step.assert_called_once_with(
            expected_message="Values should not be equal",
            actual_message="Error in assertion",
            status="fail",
            step_type="assert",
            exception_detail="Unexpected error during comparison: Unexpected error"
        )

    @patch.object(Assertions, '_handle_assertion', side_effect=Exception("Unexpected error"))
    def test_assert_not_equal_unexpected_exception(self, mock_handle_assertion):
        # Test when an unexpected exception occurs
        with self.assertRaises(AssertionError) as context:
            self.assertions.assert_not_equal(
                actual=100,
                expected=200,
                expected_message="Values should not be equal"
            )
        self.assertIn("Unexpected error during comparison", str(context.exception))
        self.assertions.reporting.insert_step.assert_called_once_with(
            expected_message="Values should not be equal",
            actual_message="Error in assertion",
            status="fail",
            step_type="assert",
            exception_detail="Unexpected error during comparison: Unexpected error"
        )

    @patch.object(Assertions, '_handle_assertion', side_effect=Exception("Unexpected error"))
    def test_assert_equal_unexpected_exception(self, mock_handle_assertion):
        # Test when an unexpected exception occurs
        with self.assertRaises(AssertionError) as context:
            self.assertions.assert_equal(
                actual=100,
                expected=100,
                expected_message="Values should be equal"
            )
        self.assertIn("Unexpected error during comparison", str(context.exception))
        self.assertions.reporting.insert_step.assert_called_once_with(
            expected_message="Values should be equal",
            actual_message="Error in assertion",
            status="fail",
            step_type="assert",
            exception_detail="Unexpected error during comparison: Unexpected error"
        )


if __name__ == '__main__':
    unittest.main()
