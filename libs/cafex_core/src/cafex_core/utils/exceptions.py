"""Module for handling exceptions in the cafex framework.

Provides exception handling with reporting integration.
"""

import os
import sys
import traceback

import pytest
from cafex_core.logging.logger_ import CoreLogger
from cafex_core.reporting_.reporting import Reporting
from cafex_core.singletons_.session_ import SessionStore


class CoreExceptions:
    """Handles custom exceptions with reporting integration.

    This class provides methods to:
    - Raise and handle custom exceptions
    - Create detailed stack traces
    - Integrate with the reporting system
    - Control test execution flow
    """

    def __init__(self):
        """Initialize the Exceptions class."""
        self.logger = CoreLogger(name=__name__).get_logger()
        self.reporting = Reporting()
        self.session_store = SessionStore()
        self.exception_message_prefix = "CAFEX Exception -->"
        self.cafex_packages = [
            "cafex_api",
            "cafex_ui",
            "cafex_core",
            "cafex_db",
            "cafex",
            "features",
        ]
        self.exclude_files = [f"{os.sep}exceptions.py"]  # Files to exclude from stack trace
        self.is_custom_exception = False  # Flag to track custom exceptions

    def _log_and_raise_exception(self, message: str) -> None:
        """Log and raise an exception with detailed context.

        Args:
            message: Initial exception message

        Raises:
            Exception: Enhanced exception with context and stack trace
        """
        exc_type, exc_value, exc_tb = sys.exc_info()

        # Ensure message always starts with prefix
        if not message.startswith(self.exception_message_prefix):
            message = f"{self.exception_message_prefix} {message}"

        # If no active exception, create default values with context
        if exc_type is None:
            exc_type = Exception
            self.is_custom_exception = True  # Set flag for custom exception

            # Get the call stack
            stack = traceback.extract_stack(limit=1000)
            all_frames = []
            trimmed_frames = []

            # Find all relevant cafex files in the stack
            for frame in reversed(stack):
                filename = frame.filename
                is_relevant = any(pkg in filename for pkg in self.cafex_packages)
                if is_relevant:
                    frame_str = f"at {filename}:{frame.lineno} in {frame.name}"
                    all_frames.append(frame_str)

                    # For trimmed frames, exclude exceptions.py
                    if not filename.endswith(f"{os.sep}utils{os.sep}exceptions.py"):
                        trimmed_frames.append(frame_str)

            # Store frames for custom exception
            self.session_store.all_frames = all_frames
            self.session_store.trimmed_frames = trimmed_frames

            cafex_context = "\n".join(all_frames) if all_frames else "Unknown origin"
            exc_value = f"Cafex Custom Exception\n{cafex_context}"
        else:
            self.is_custom_exception = False  # Reset flag for system exception

        final_message = self.__build_exception_message(message, exc_type, exc_value)

        # Log the exception
        self.logger.error(final_message)

        # Store for report generation
        self.session_store.exception_type = exc_type.__name__
        self.session_store.exception_message = final_message

        # Raise with original traceback
        if exc_tb:
            raise Exception(final_message).with_traceback(exc_tb)
        raise Exception(final_message)

    def _run_log_actions(
            self,
            message: str,
            insert_report: bool = True,
            trim_log: bool = True,
            log_local: bool = True,
            fail_test: bool = True,
    ) -> None:
        """Process exception for reporting and test control.

        Args:
            message: Exception message
            insert_report: Whether to generate report
            trim_log: Use trimmed stack trace if True
            log_local: Enable local logging
            fail_test: Mark test as failed
        """
        try:
            if insert_report:
                # Get stack traces
                trace = None
                if log_local:
                    if self.is_custom_exception:
                        # Use stored frames for custom exception
                        trace = (
                            "\n".join(
                                ["Cafex Stack Trace:", "\n".join(self.session_store.trimmed_frames)]
                            )
                            if trim_log
                            else "\n".join(
                                ["Cafex Stack Trace:", "\n".join(self.session_store.all_frames)]
                            )
                        )
                    else:
                        # Use traceback for system exception
                        trace = (
                            self.__get_trim_stack_trace()
                            if trim_log
                            else self.__get_complete_stack_trace()
                        )

                # Get stored exception info
                stored_exc = {
                    "type": self.session_store.storage.get("exception_type", "Exception"),
                    "message": self.session_store.storage.get("exception_message", message),
                }

                # Clean and format the message
                final_message = self.__clean_message_for_report(stored_exc["message"])

                # Report exception
                self.reporting.report_exception(
                    message=final_message,
                    exception_type=stored_exc["type"],
                    trace=trace,
                    context=self.__get_context_info(),
                    fail_test=fail_test,
                )

            if fail_test:
                pytest.fail(message, pytrace=False)
        finally:
            # Clean up session store
            keys_to_clean = ["exception_type", "exception_message"]
            for key in keys_to_clean:
                if key in self.session_store.storage:
                    del self.session_store.storage[key]

    @staticmethod
    def __clean_message_for_report(message: str) -> str:
        """Clean exception message for reporting.

        Args:
            message: Raw exception message

        Returns:
            str: Cleaned message suitable for reporting
        """
        # Get user's custom message and error details
        error_details = None

        # Extract custom message (everything before Exception Type)
        if "Exception Type:" in message:
            custom_message = message.split("Exception Type:", 1)[0].strip().rstrip(":")
        else:
            custom_message = message.strip().rstrip(":")

        # Extract error details (actual error message after Exception Details)
        if "Exception Details:" in message:
            details_section = message.split("Exception Details:", 1)[1].strip()
            # Get first meaningful line
            for line in details_section.split("\n"):
                if line.strip() and not any(
                        x in line for x in ["Stacktrace:", "Message:", "at ", "Exception Type:"]
                ):
                    error_details = line.strip()
                    break

        # Build final message based on what we have
        if custom_message == "CAFEX Exception -->":
            return custom_message + " " + (error_details if error_details else "")

        custom_message = custom_message.rstrip(":").strip()  # Remove trailing colon if exists
        return f"{custom_message} : {error_details}" if error_details else custom_message

    def __get_trim_stack_trace(self) -> str:
        """Get trimmed stack trace with just cafex frames. Provides a concise
        view focusing on application-specific code.

        Returns:
            str: Formatted stack trace with cafex frames
        """
        try:
            exc_type, exc_value, exc_tb = sys.exc_info()
            frames = self.__get_stack_frames(exc_tb)

            if not frames:
                return "No Cafex stack trace available"

            return "\n".join(["Cafex Stack Trace:", "\n".join(frames)])

        except Exception as e:
            self.logger.error(f"Error in get_trim_stack_trace: {str(e)}")
            return "Exception occurred"

    def __get_complete_stack_trace(self) -> str:
        """Get complete stack trace including both cafex and external frames.
        Provides comprehensive view of the error chain.

        Returns:
            str: Complete formatted stack trace
        """
        try:
            exc_type, exc_value, exc_tb = sys.exc_info()

            # Extract stacktrace if present
            external_trace = None
            if exc_value and "Stacktrace:" in str(exc_value):
                external_trace = str(exc_value).split("Stacktrace:", 1)[1].strip()

            # Build comprehensive trace
            stack_parts = []

            # Add Cafex frames
            frames = self.__get_stack_frames(exc_tb)

            if frames:
                stack_parts.extend(["Cafex Stack Trace:", "\n".join(frames)])

            # Add external trace if available
            if external_trace:
                stack_parts.extend(["\nExternal Stack Trace:", external_trace])

            if not stack_parts:
                return "No stack trace available"

            return "\n".join(stack_parts)

        except Exception as e:
            self.logger.error(f"Error in get_complete_stack_trace: {str(e)}")
            return str(traceback.format_exc())

    def __build_exception_message(self, user_message: str, exc_type=None, exc_value=None) -> str:
        """Build formatted exception message with context.

        Args:
            user_message: Initial user message
            exc_type: Exception type
            exc_value: Exception value

        Returns:
            str: Formatted exception message
        """
        if not exc_type or not exc_value:
            return user_message.strip()

        exc_message = str(exc_value).strip()
        exc_name = exc_type.__name__

        # Remove duplicate information
        if exc_message in user_message:
            user_message = user_message.replace(exc_message, "").strip()

        # Get context information
        context = self.__get_context_info()
        context_info = []
        if context["current_step"]:
            context_info.append(f"Step: {context['current_step']}")
        if context["current_test"]:
            context_info.append(f"Test: {context['current_test']}")

        # Build final message
        message_parts = [
            user_message.strip() if user_message else "",
            f"Exception Type: {exc_name}",
            "\n".join(context_info) if context_info else "",
            f"Exception Details: \n{exc_message}",
        ]

        return "\n".join(filter(None, message_parts))

    def __get_stack_frames(self, tb) -> list:
        """Extract and format relevant stack frames.

        Args:
            tb: Traceback object

        Returns:
            list: Formatted frame strings for cafex and feature code
        """
        frames = []
        while tb is not None:
            filename = tb.tb_frame.f_code.co_filename
            cafex_packages = self.cafex_packages

            is_relevant = any(pkg in filename for pkg in cafex_packages) and not any(
                filename.endswith(exclude) for exclude in self.exclude_files
            )

            if is_relevant:
                frame = f"at {filename}:{tb.tb_lineno}"

                # Add class and method context if available
                if tb.tb_frame.f_locals.get("self"):
                    frame += (
                        f" in {tb.tb_frame.f_code.co_name} "
                        f"[{tb.tb_frame.f_locals['self'].__class__.__name__}]"
                    )
                else:
                    frame += f" in {tb.tb_frame.f_code.co_name}"

                frames.append(frame)

            tb = tb.tb_next
        return frames

    def __get_context_info(self) -> dict:
        """Get current test and step context.

        Returns:
            Dictionary containing context information
        """
        return {
            "current_test": self.session_store.current_test,
            "current_step": self.session_store.current_step,
        }

    def raise_generic_exception(
            self,
            message: str,
            insert_report: bool = True,
            trim_log: bool = True,
            log_local: bool = True,
            fail_test: bool = True,
    ) -> None:
        """Raise and handle a generic exception with comprehensive error
        reporting.

        This method provides centralized exception handling with flexible reporting options.
        It captures stack traces, adds context information, and can optionally fail the test.

        Args:
            message: The exception message to log and report
            insert_report: Whether to add exception details to the test report
            trim_log: If True, includes only application frames in stack trace
            log_local: Whether to enable local logging of the exception
            fail_test: If True, marks the current test as failed

        Examples:
            Basic API test error handling:
                # In your API test class
                def test_api_endpoint(self):
                    try:
                        response = self.client.get("/api/data")
                    except Exception as e:
                        self.exceptions.raise_generic_exception(
                            f"API request failed: {str(e)}"
                        )

            UI element interaction error:
                # In your UI test class
                def verify_element_visible(self, locator: str) -> bool:
                    try:
                        self.driver.find_element(locator)
                        return True
                    except Exception as e:
                        error_msg = f"Element not visible: '{locator}'"
                        self.exceptions.raise_generic_exception(
                            message=error_msg,
                            fail_test=False
                        )
                        return False

            Database operation error:
                # In your DB test class
                def execute_query(self, query: str) -> None:
                    try:
                        self.cursor.execute(query)
                    except Exception as e:
                        self.exceptions.raise_generic_exception(
                            message=f"Query execution failed: {str(e)}",
                            trim_log=True,
                            fail_test=False
                        )

        Note:
            - Uses session store to maintain exception context
            - Integrates with the reporting system for test results
            - Supports both BDD and non-BDD test frameworks
            - Handles nested exceptions and maintains original stack traces
        """
        try:
            self._log_and_raise_exception(message)
        except Exception as raised_exception:
            # Only handle the exception we raised
            if isinstance(raised_exception, Exception) and str(raised_exception).startswith(
                    self.exception_message_prefix
            ):
                self._run_log_actions(
                    str(raised_exception),
                    insert_report=insert_report,
                    trim_log=trim_log,
                    log_local=log_local,
                    fail_test=fail_test,
                )
            else:
                # Re-raise if it's not our exception
                raise
