from cafex_core.utils.exceptions import CoreExceptions


class DesktopClientExceptions(CoreExceptions):
    """
    A class for handling exceptions specific to desktop applications.

    This class provides methods to raise and handle various exceptions encountered during the
    operation of desktop applications.
    """

    def raise_connect_to_app_failed(
        self,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """
        Raise exception when unable to connect to the application.

        This method is used when the application fails to connect due to
        missing or invalid connection criteria.

        Args:
            insert_report: Whether to add exception details to the test report.
            trim_log: If True, includes only application frames in the stack trace.
            log_local: Whether to enable local logging of the exception.
            fail_test: If True, marks the current test as failed.

        Examples:
            1. When no valid connection criteria are provided:
                >>> exceptions = DesktopClientExceptions()
                >>> exceptions.raise_connect_to_app_failed()

            2. When connection fails but the test should not fail:
                >>> exceptions = DesktopClientExceptions()
                >>> exceptions.raise_connect_to_app_failed(fail_test=False)
        """
        exception_message = (
            "At least one criterion should be provided to connect with the existing app"
        )
        self.raise_generic_exception(
            message=exception_message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_element_not_found(
        self,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """
        Raise exception when an element is not found.

        This method is used when a UI element cannot be located in the application.

        Args:
            insert_report: Whether to add exception details to the test report.
            trim_log: If True, includes only application frames in the stack trace.
            log_local: Whether to enable local logging of the exception.
            fail_test: If True, marks the current test as failed.

        Examples:
            1. When an element is missing during a UI test:
                >>> exceptions = DesktopClientExceptions()
                >>> exceptions.raise_element_not_found()

            2. When logging the issue locally without failing the test:
                >>> exceptions = DesktopClientExceptions()
                >>> exceptions.raise_element_not_found(log_local=True, fail_test=False)
        """
        exception_message = "Element not found"
        self.raise_generic_exception(
            message=exception_message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_incorrect_locator_entered(
        self,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """
        Raise exception for an invalid locator strategy.

        This method is used when an invalid locator type is provided for locating UI elements.

        Args:
            insert_report: Whether to add exception details to the test report.
            trim_log: If True, includes only application frames in the stack trace.
            log_local: Whether to enable local logging of the exception.
            fail_test: If True, marks the current test as failed.

        Examples:
            1. When an invalid locator type is used:
                >>> exceptions = DesktopClientExceptions()
                >>> exceptions.raise_incorrect_locator_entered()

            2. When the test should continue despite the invalid locator:
                >>> exceptions = DesktopClientExceptions()
                >>> exceptions.raise_incorrect_locator_entered(fail_test=False)
        """
        exception_message = "Invalid Locator Strategy: Enter locator_type as title/autoid/class_name/title_re/control_type"
        self.raise_generic_exception(
            message=exception_message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_window_not_found(
        self,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """
        Raise exception when a window is not found.

        This method is used when the application fails to locate a specific window.

        Args:
            insert_report: Whether to add exception details to the test report.
            trim_log: If True, includes only application frames in the stack trace.
            log_local: Whether to enable local logging of the exception.
            fail_test: If True, marks the current test as failed.

        Examples:
            1. When a window is missing during a test:
                >>> exceptions = DesktopClientExceptions()
                >>> exceptions.raise_window_not_found()

            2. When logging the issue locally without failing the test:
                >>> exceptions = DesktopClientExceptions()
                >>> exceptions.raise_window_not_found(log_local=True, fail_test=False)
        """
        exception_message = "Unable to locate window"
        self.raise_generic_exception(
            message=exception_message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_invalid_parameters(
        self,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """
        Raise exception for invalid parameters.

        This method is used when invalid or incorrect parameters are provided to a function or method.

        Args:
            insert_report: Whether to add exception details to the test report.
            trim_log: If True, includes only application frames in the stack trace.
            log_local: Whether to enable local logging of the exception.
            fail_test: If True, marks the current test as failed.

        Examples:
            1. When invalid parameters are passed to a function:
                >>> exceptions = DesktopClientExceptions()
                >>> exceptions.raise_invalid_parameters()

            2. When the test should continue despite invalid parameters:
                >>> exceptions = DesktopClientExceptions()
                >>> exceptions.raise_invalid_parameters(fail_test=False)
        """
        exception_message = (
            "Invalid Parameters. Make sure that your parameters and their values are correct"
        )
        self.raise_generic_exception(
            message=exception_message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_image_not_found(
        self,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """
        Raise exception when an image is not found.

        This method is used when the application fails to locate a specific image.

        Args:
            insert_report: Whether to add exception details to the test report.
            trim_log: If True, includes only application frames in the stack trace.
            log_local: Whether to enable local logging of the exception.
            fail_test: If True, marks the current test as failed.

        Examples:
            1. When an image is missing during a test:
                >>> exceptions = DesktopClientExceptions()
                >>> exceptions.raise_image_not_found()

            2. When logging the issue locally without failing the test:
                >>> exceptions = DesktopClientExceptions()
                >>> exceptions.raise_image_not_found(log_local=True, fail_test=False)
        """
        exception_message = "Unable to locate specified Image"
        self.raise_generic_exception(
            message=exception_message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )

    def raise_element_property_not_found(
        self,
        insert_report: bool = True,
        trim_log: bool = True,
        log_local: bool = True,
        fail_test: bool = True,
    ) -> None:
        """
        Raise exception when an element property is not found.

        This method is used when a specific property of a UI element cannot be located.

        Args:
            insert_report: Whether to add exception details to the test report.
            trim_log: If True, includes only application frames in the stack trace.
            log_local: Whether to enable local logging of the exception.
            fail_test: If True, marks the current test as failed.

        Examples:
            1. When a property of an element is missing:
                >>> exceptions = DesktopClientExceptions()
                >>> exceptions.raise_element_property_not_found()

            2. When logging the issue locally without failing the test:
                >>> exceptions = DesktopClientExceptions()
                >>> exceptions.raise_element_property_not_found(log_local=True, fail_test=False)
        """
        exception_message = "Unable to find element property"
        self.raise_generic_exception(
            message=exception_message,
            insert_report=insert_report,
            trim_log=trim_log,
            log_local=log_local,
            fail_test=fail_test,
        )
