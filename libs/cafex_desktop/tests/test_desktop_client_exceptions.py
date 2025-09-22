import unittest
from unittest.mock import MagicMock

from cafex_desktop.desktop_client.desktop_client_exceptions import DesktopClientExceptions


class TestDesktopClientExceptions(unittest.TestCase):
    def setUp(self):
        # Create an instance of DesktopClientExceptions and mock the raise_generic_exception method
        self.exceptions = DesktopClientExceptions()
        self.exceptions.raise_generic_exception = MagicMock()

    def test_raise_connect_to_app_failed_default_args(self):
        # Test with default arguments
        self.exceptions.raise_connect_to_app_failed()
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="At least one criterion should be provided to connect with the existing app",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=True,
        )

    def test_raise_connect_to_app_failed_no_fail_test(self):
        # Test with fail_test set to False
        self.exceptions.raise_connect_to_app_failed(fail_test=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="At least one criterion should be provided to connect with the existing app",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False,
        )

    def test_raise_connect_to_app_failed_no_local_log(self):
        # Test with log_local set to False
        self.exceptions.raise_connect_to_app_failed(log_local=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="At least one criterion should be provided to connect with the existing app",
            insert_report=True,
            trim_log=True,
            log_local=False,
            fail_test=True,
        )

    def test_raise_connect_to_app_failed_no_trim_log(self):
        # Test with trim_log set to False
        self.exceptions.raise_connect_to_app_failed(trim_log=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="At least one criterion should be provided to connect with the existing app",
            insert_report=True,
            trim_log=False,
            log_local=True,
            fail_test=True,
        )

    def test_raise_connect_to_app_failed_no_insert_report(self):
        # Test with insert_report set to False
        self.exceptions.raise_connect_to_app_failed(insert_report=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="At least one criterion should be provided to connect with the existing app",
            insert_report=False,
            trim_log=True,
            log_local=True,
            fail_test=True,
        )

    def test_raise_element_not_found_default_args(self):
        # Test with default arguments
        self.exceptions.raise_element_not_found()
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Element not found",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=True,
        )

    def test_raise_element_not_found_no_fail_test(self):
        # Test with fail_test set to False
        self.exceptions.raise_element_not_found(fail_test=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Element not found",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False,
        )

    def test_raise_element_not_found_no_local_log(self):
        # Test with log_local set to False
        self.exceptions.raise_element_not_found(log_local=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Element not found",
            insert_report=True,
            trim_log=True,
            log_local=False,
            fail_test=True,
        )

    def test_raise_element_not_found_no_trim_log(self):
        # Test with trim_log set to False
        self.exceptions.raise_element_not_found(trim_log=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Element not found",
            insert_report=True,
            trim_log=False,
            log_local=True,
            fail_test=True,
        )

    def test_raise_element_not_found_no_insert_report(self):
        # Test with insert_report set to False
        self.exceptions.raise_element_not_found(insert_report=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Element not found",
            insert_report=False,
            trim_log=True,
            log_local=True,
            fail_test=True,
        )

    def test_raise_incorrect_locator_entered_default_args(self):
        # Test with default arguments
        self.exceptions.raise_incorrect_locator_entered()
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Invalid Locator Strategy: Enter locator_type as title/autoid/class_name/title_re/control_type",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=True,
        )

    def test_raise_incorrect_locator_entered_no_fail_test(self):
        # Test with fail_test set to False
        self.exceptions.raise_incorrect_locator_entered(fail_test=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Invalid Locator Strategy: Enter locator_type as title/autoid/class_name/title_re/control_type",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False,
        )

    def test_raise_incorrect_locator_entered_no_local_log(self):
        # Test with log_local set to False
        self.exceptions.raise_incorrect_locator_entered(log_local=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Invalid Locator Strategy: Enter locator_type as title/autoid/class_name/title_re/control_type",
            insert_report=True,
            trim_log=True,
            log_local=False,
            fail_test=True,
        )

    def test_raise_incorrect_locator_entered_no_trim_log(self):
        # Test with trim_log set to False
        self.exceptions.raise_incorrect_locator_entered(trim_log=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Invalid Locator Strategy: Enter locator_type as title/autoid/class_name/title_re/control_type",
            insert_report=True,
            trim_log=False,
            log_local=True,
            fail_test=True,
        )

    def test_raise_incorrect_locator_entered_no_insert_report(self):
        # Test with insert_report set to False
        self.exceptions.raise_incorrect_locator_entered(insert_report=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Invalid Locator Strategy: Enter locator_type as title/autoid/class_name/title_re/control_type",
            insert_report=False,
            trim_log=True,
            log_local=True,
            fail_test=True,
        )
    def test_raise_window_not_found_default_args(self):
        # Test with default arguments
        self.exceptions.raise_window_not_found()
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Unable to locate window",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=True,
        )

    def test_raise_window_not_found_no_fail_test(self):
        # Test with fail_test set to False
        self.exceptions.raise_window_not_found(fail_test=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Unable to locate window",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False,
        )

    def test_raise_window_not_found_no_local_log(self):
        # Test with log_local set to False
        self.exceptions.raise_window_not_found(log_local=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Unable to locate window",
            insert_report=True,
            trim_log=True,
            log_local=False,
            fail_test=True,
        )

    def test_raise_window_not_found_no_trim_log(self):
        # Test with trim_log set to False
        self.exceptions.raise_window_not_found(trim_log=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Unable to locate window",
            insert_report=True,
            trim_log=False,
            log_local=True,
            fail_test=True,
        )

    def test_raise_window_not_found_no_insert_report(self):
        # Test with insert_report set to False
        self.exceptions.raise_window_not_found(insert_report=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Unable to locate window",
            insert_report=False,
            trim_log=True,
            log_local=True,
            fail_test=True,
        )
    def test_raise_invalid_parameters_default_args(self):
        # Test with default arguments
        self.exceptions.raise_invalid_parameters()
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Invalid Parameters. Make sure that your parameters and their values are correct",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=True,
        )

    def test_raise_invalid_parameters_no_fail_test(self):
        # Test with fail_test set to False
        self.exceptions.raise_invalid_parameters(fail_test=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Invalid Parameters. Make sure that your parameters and their values are correct",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False,
        )

    def test_raise_invalid_parameters_no_local_log(self):
        # Test with log_local set to False
        self.exceptions.raise_invalid_parameters(log_local=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Invalid Parameters. Make sure that your parameters and their values are correct",
            insert_report=True,
            trim_log=True,
            log_local=False,
            fail_test=True,
        )

    def test_raise_invalid_parameters_no_trim_log(self):
        # Test with trim_log set to False
        self.exceptions.raise_invalid_parameters(trim_log=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Invalid Parameters. Make sure that your parameters and their values are correct",
            insert_report=True,
            trim_log=False,
            log_local=True,
            fail_test=True,
        )

    def test_raise_invalid_parameters_no_insert_report(self):
        # Test with insert_report set to False
        self.exceptions.raise_invalid_parameters(insert_report=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Invalid Parameters. Make sure that your parameters and their values are correct",
            insert_report=False,
            trim_log=True,
            log_local=True,
            fail_test=True,
        )
    def test_raise_image_not_found_default_args(self):
        # Test with default arguments
        self.exceptions.raise_image_not_found()
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Unable to locate specified Image",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=True,
        )

    def test_raise_image_not_found_no_fail_test(self):
        # Test with fail_test set to False
        self.exceptions.raise_image_not_found(fail_test=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Unable to locate specified Image",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False,
        )

    def test_raise_image_not_found_no_local_log(self):
        # Test with log_local set to False
        self.exceptions.raise_image_not_found(log_local=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Unable to locate specified Image",
            insert_report=True,
            trim_log=True,
            log_local=False,
            fail_test=True,
        )

    def test_raise_image_not_found_no_trim_log(self):
        # Test with trim_log set to False
        self.exceptions.raise_image_not_found(trim_log=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Unable to locate specified Image",
            insert_report=True,
            trim_log=False,
            log_local=True,
            fail_test=True,
        )

    def test_raise_image_not_found_no_insert_report(self):
        # Test with insert_report set to False
        self.exceptions.raise_image_not_found(insert_report=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Unable to locate specified Image",
            insert_report=False,
            trim_log=True,
            log_local=True,
            fail_test=True,
        )
    def test_raise_element_property_not_found_default_args(self):
        # Test with default arguments
        self.exceptions.raise_element_property_not_found()
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Unable to find element property",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=True,
        )

    def test_raise_element_property_not_found_no_fail_test(self):
        # Test with fail_test set to False
        self.exceptions.raise_element_property_not_found(fail_test=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Unable to find element property",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False,
        )

    def test_raise_element_property_not_found_no_local_log(self):
        # Test with log_local set to False
        self.exceptions.raise_element_property_not_found(log_local=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Unable to find element property",
            insert_report=True,
            trim_log=True,
            log_local=False,
            fail_test=True,
        )

    def test_raise_element_property_not_found_no_trim_log(self):
        # Test with trim_log set to False
        self.exceptions.raise_element_property_not_found(trim_log=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Unable to find element property",
            insert_report=True,
            trim_log=False,
            log_local=True,
            fail_test=True,
        )

    def test_raise_element_property_not_found_no_insert_report(self):
        # Test with insert_report set to False
        self.exceptions.raise_element_property_not_found(insert_report=False)
        self.exceptions.raise_generic_exception.assert_called_once_with(
            message="Unable to find element property",
            insert_report=False,
            trim_log=True,
            log_local=True,
            fail_test=True,
        )


if __name__ == "__main__":
    unittest.main()
