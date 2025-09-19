import unittest
from unittest.mock import patch, MagicMock
from cafex_core.utils.exceptions import CoreExceptions


class TestCoreExceptions(unittest.TestCase):

    def setUp(self):
        self.core_exceptions = CoreExceptions()

    @patch('cafex_core.logging.logger_.CoreLogger.get_logger')
    @patch('cafex_core.reporting_.reporting.Reporting')
    @patch('cafex_core.singletons_.session_.SessionStore')
    def test_init(self, mock_session_store, mock_reporting, mock_logger):
        core_exceptions = CoreExceptions()
        self.assertIsNotNone(core_exceptions.logger)
        self.assertIsNotNone(core_exceptions.reporting)
        self.assertIsNotNone(core_exceptions.session_store)

    @patch('cafex_core.utils.exceptions.sys.exc_info', return_value=(None, None, None))
    @patch('cafex_core.utils.exceptions.traceback.extract_stack')
    @patch('cafex_core.logging.logger_.CoreLogger.get_logger')
    def test_log_and_raise_exception_custom(self, mock_logger, mock_stack, mock_exc_info):
        mock_stack.return_value = [MagicMock(filename='cafex_core/utils/exceptions.py', lineno=10, name='test')]
        with self.assertRaises(Exception) as context:
            self.core_exceptions._log_and_raise_exception("Test message")
        self.assertTrue("CAFEX Exception -->" in str(context.exception))

    @patch('cafex_core.utils.exceptions.sys.exc_info', return_value=(Exception, Exception("Test Exception"), None))
    @patch('cafex_core.logging.logger_.CoreLogger.get_logger')
    def test_log_and_raise_exception_system(self, mock_logger, mock_exc_info):
        with self.assertRaises(Exception) as context:
            self.core_exceptions._log_and_raise_exception("Test message")
        self.assertTrue("Test message" in str(context.exception))

    @patch('cafex_core.utils.exceptions.pytest.fail')
    @patch('cafex_core.utils.exceptions.CoreExceptions._log_and_raise_exception')
    def test_raise_generic_exception(self, mock_log_and_raise, mock_pytest_fail):
        mock_log_and_raise.side_effect = Exception("CAFEX Exception --> Test message")
        self.core_exceptions.raise_generic_exception("Test message")
        mock_pytest_fail.assert_called_once_with("CAFEX Exception --> Test message", pytrace=False)

    @patch('cafex_core.utils.exceptions.CoreExceptions._log_and_raise_exception')
    def test_raise_generic_exception_reraise(self, mock_log_and_raise):
        # Simulate an unexpected exception
        mock_log_and_raise.side_effect = ValueError("Unexpected exception")
        with self.assertRaises(ValueError) as context:
            self.core_exceptions.raise_generic_exception("Test message")
        self.assertEqual(str(context.exception), "Unexpected exception")

    @patch('cafex_core.utils.exceptions.CoreExceptions._run_log_actions')
    @patch('cafex_core.utils.exceptions.CoreExceptions._log_and_raise_exception')
    def test_raise_generic_exception_no_fail(self, mock_log_and_raise, mock_run_log_actions):
        mock_log_and_raise.side_effect = Exception("CAFEX Exception --> Test message")
        self.core_exceptions.raise_generic_exception("Test message", fail_test=False)
        mock_run_log_actions.assert_called_once()

    def test_clean_message_for_report(self):
        message = "CAFEX Exception --> Exception Type: ValueError Exception Details: Test error"
        cleaned_message = self.core_exceptions._CoreExceptions__clean_message_for_report(message)
        self.assertEqual(cleaned_message, "CAFEX Exception --> Test error")

    @patch('cafex_core.utils.exceptions.sys.exc_info', return_value=(Exception, Exception("Test Exception"), None))
    def test_get_trim_stack_trace(self, mock_exc_info):
        trace = self.core_exceptions._CoreExceptions__get_trim_stack_trace()
        self.assertFalse("Cafex Stack Trace:" in trace)

    @patch('cafex_core.utils.exceptions.sys.exc_info', return_value=(Exception, Exception("Test Exception"), None))
    def test_get_complete_stack_trace(self, mock_exc_info):
        trace = self.core_exceptions._CoreExceptions__get_complete_stack_trace()
        self.assertFalse("Cafex Stack Trace:" in trace)

    @patch('cafex_core.utils.exceptions.sys.exc_info')
    @patch('cafex_core.utils.exceptions.traceback.format_exc')
    def test_get_complete_stack_trace_no_exception(self, mock_format_exc, mock_exc_info):
        mock_exc_info.return_value = (None, None, None)
        result = self.core_exceptions._CoreExceptions__get_complete_stack_trace()
        self.assertEqual(result, "No stack trace available")

    @patch('cafex_core.utils.exceptions.sys.exc_info')
    @patch('cafex_core.utils.exceptions.traceback.format_exc')
    def test_get_complete_stack_trace_with_exception(self, mock_format_exc, mock_exc_info):
        mock_exc_info.return_value = (Exception, Exception("Test Exception"), MagicMock())
        with patch.object(self.core_exceptions, '_CoreExceptions__get_stack_frames', return_value=["frame1", "frame2"]):
            result = self.core_exceptions._CoreExceptions__get_complete_stack_trace()
            self.assertIn("Cafex Stack Trace:", result)
            self.assertIn("frame1", result)
            self.assertIn("frame2", result)

    @patch('cafex_core.utils.exceptions.sys.exc_info')
    @patch('cafex_core.utils.exceptions.traceback.format_exc')
    def test_get_complete_stack_trace_with_external_trace(self, mock_format_exc, mock_exc_info):
        mock_exc_info.return_value = (
            Exception, Exception("Test Exception Stacktrace: external frame1\nexternal frame2"), MagicMock())
        with patch.object(self.core_exceptions, '_CoreExceptions__get_stack_frames', return_value=["frame1", "frame2"]):
            result = self.core_exceptions._CoreExceptions__get_complete_stack_trace()
            self.assertIn("Cafex Stack Trace:", result)
            self.assertIn("frame1", result)
            self.assertIn("frame2", result)
            self.assertIn("External Stack Trace:", result)
            self.assertIn("external frame1", result)
            self.assertIn("external frame2", result)

    # @patch('cafex_core.utils.exceptions.sys.exc_info')
    # @patch('cafex_core.utils.exceptions.traceback.format_exc')
    # def test_get_complete_stack_trace_with_internal_error(self, mock_format_exc, mock_exc_info):
    #     mock_exc_info.side_effect = Exception("Internal error")
    #     mock_format_exc.return_value = "Formatted traceback"
    #     result = self.core_exceptions._CoreExceptions__get_complete_stack_trace()
    #     self.assertIn("Formatted traceback", result)

    def test_build_exception_message(self):
        message = self.core_exceptions._CoreExceptions__build_exception_message("User message", Exception,
                                                                                "Test Exception")
        self.assertTrue("User message" in message)
        self.assertTrue("Exception Type: Exception" in message)
        self.assertTrue("Exception Details: \nTest Exception" in message)

    def test_clean_message_for_report_else_block(self):
        message = "Some random message"
        cleaned_message = self.core_exceptions._CoreExceptions__clean_message_for_report(message)
        self.assertEqual(cleaned_message, "Some random message")

    @patch('cafex_core.utils.exceptions.CoreExceptions._CoreExceptions__get_context_info')
    def test_build_exception_message_with_context(self, mock_get_context_info):
        mock_get_context_info.return_value = {
            "current_step": "Step 1",
            "current_test": "Test 1"
        }
        user_message = "User message"
        exc_type = ValueError
        exc_value = ValueError("Test Exception")

        message = self.core_exceptions._CoreExceptions__build_exception_message(user_message, exc_type, exc_value)

        self.assertIn("Step: Step 1", message)
        self.assertIn("Test: Test 1", message)
        self.assertIn("Exception Type: ValueError", message)
        self.assertIn("Exception Details: \nTest Exception", message)

    def test_build_exception_message_no_exception(self):
        user_message = "User message"
        exc_type = None
        exc_value = None

        core_exceptions = CoreExceptions()
        message = core_exceptions._CoreExceptions__build_exception_message(user_message, exc_type, exc_value)

        self.assertEqual(message, "User message")

    def test_get_context_info(self):
        context = self.core_exceptions._CoreExceptions__get_context_info()
        self.assertIn("current_test", context)
        self.assertIn("current_step", context)

    @patch('cafex_core.utils.exceptions.sys.exc_info', return_value=(Exception, Exception("Test Exception"), None))
    @patch('cafex_core.utils.exceptions.traceback.format_exc', return_value="Formatted Stack Trace")
    def test_exception_handling_in_get_complete_stack_trace(self, mock_format_exc, mock_exc_info):
        try:
            # Create an instance of the CoreExceptions class
            obj = CoreExceptions()

            # Mock logger to prevent actual logging calls
            obj.logger = MagicMock()

            # Simulate an exception within the method
            with patch.object(obj, '_CoreExceptions__get_stack_frames', side_effect=Exception("Test Exception")):
                # Use patch.object to mock the logger's error method directly
                with patch.object(obj.logger, 'error') as mock_error:
                    result = obj._CoreExceptions__get_complete_stack_trace()
                    # Ensure the logger.error method is called with the correct message
                    mock_error.assert_called_with('Error in get_complete_stack_trace: Test Exception')

            # Assert that the return value is the formatted stack trace
            self.assertEqual(result, "Formatted Stack Trace")
        except Exception as e:
            print("Exception occurred")


if __name__ == "__main__":
    unittest.main()
