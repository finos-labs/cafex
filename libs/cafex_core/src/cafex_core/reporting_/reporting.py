from cafex_core.logging.logger_ import CoreLogger
from cafex_core.reporting_.screenshot_utils import (
    add_screenshot_to_report,
    capture_screenshot,
)
from cafex_core.singletons_.session_ import SessionStore
from cafex_core.utils.date_time_utils import DateTimeActions
from cafex_core.utils.regex_constants import TRACE_ORIGIN_PATTERN


class Reporting:
    """Handles reporting functionality for test execution, including step and
    assertion tracking."""

    def __init__(self):
        self.session_store = SessionStore()
        self.datetime_util = DateTimeActions()
        self.logger = CoreLogger(name=__name__).get_logger()

    def _create_assertion_data(
        self,
        name: str,
        expected_message: str,
        actual_message: str,
        status: str,
        step_type: str,
        current_time: str,
        screenshot_path: str = None,
        api_response: dict = None,
        exception_detail: str = None,
    ) -> dict:
        """Creates assertion data structure with consistent format."""
        assertion_data = {
            "name": name,
            "expected": expected_message,
            "actual": actual_message,
            "status": status,
            "type": step_type,
            "timestamp": current_time,
        }

        if screenshot_path:
            assertion_data["screenshot"] = screenshot_path

        if api_response:
            assertion_data["apiResponse"] = api_response

        if exception_detail:
            assertion_data["exceptionDetail"] = exception_detail

        if status == "F":
            # Mark the test as failed
            self.session_store.mark_test_failed()

            error_info = {
                "name": name,
                "message": exception_detail if exception_detail else f"Failed: {expected_message}",
                "type": step_type,
                "timestamp": current_time,
                "phase": "test",
                "details": {
                    "expected": expected_message,
                    "actual": actual_message,
                },
            }
            self.session_store.add_error_message(error_info)

        return assertion_data

    @staticmethod
    def _normalize_status(status: str) -> str:
        """
        Normalizes the status to one of the valid values: 'F', 'P', or 'IC'.
        """
        status = status.lower()
        if status == "fail":
            return "F"
        if status == "pass":
            return "P"
        return "IC"

    def insert_step(
        self,
        expected_message: str,
        actual_message: str,
        status: str = "IC",
        step_name: str = None,
        step_type: str = "step",
        exception_detail: str = None,
        take_screenshot: bool = True,
        api_response: dict = None,
        trim_exception_detail: bool = False,
    ) -> None:
        """Inserts a step or assertion into the test report.

        If called within an existing step (i.e., current_step is set in session_store),
        adds data as an assertion to that step. Otherwise, creates a new step in the test report.

        Args:
            expected_message (str): Expected result or condition
            actual_message (str): Actual result or condition
            status (str, optional): Step/assertion status ("Pass", "Fail", or "IC"). Defaults to "IC".
            step_name (str, optional): Custom name for the step. If not provided,
                constructs name from expected and actual messages.
            step_type (str, optional): Type of step ("step", "verify", "assert", etc.). Defaults to "step".
            exception_detail (str, optional): Details of any exception that occurred.
            take_screenshot (bool, optional): Whether to capture a screenshot. Defaults to True.
            api_response (dict, optional): API response data to include in the report.
            trim_exception_detail (bool, optional): Whether to trim exception detail to 3990 chars.
                Defaults to False.

        Examples:
            1. Basic step with pass status:
            ```python
            reporting.insert_step(
                "Login button should be enabled",
                "Login button is enabled",
                "Pass"
            )
            ```

            2. Failed step with custom name and exception:
            ```python
            reporting.insert_step(
                "User should be logged in",
                "Login failed",
                "Fail",
                step_name="Login Verification",
                exception_detail="InvalidCredentialsError: Username or password incorrect"
            )
            ```

            3. API test step with response data:
            ```python
            api_response = {
                "status_code": 200,
                "body": {"user_id": 123, "status": "active"}
            }
            reporting.insert_step(
                "API should return 200",
                f"API returned {api_response['status_code']}",
                "Pass",
                step_type="api",
                api_response=api_response
            )
            ```

            4. Step within another step (adds as assertion):
            ```python
            # In a test using @step decorator or within a BDD step
            reporting.insert_step(
                "Element should be visible",
                "Element is visible",
                "Pass",
                step_type="verify"
            )
            ```

            5. Disable screenshot for performance:
            ```python
            reporting.insert_step(
                "Database should be connected",
                "Connected successfully",
                "Pass",
                take_screenshot=False
            )
            ```

            6. Handle long exception details:
            ```python
            reporting.insert_step(
                "Parse large file",
                "Parsing failed",
                "Fail",
                exception_detail=long_stack_trace,
                trim_exception_detail=True
            )
            ```

        Notes:
            - The method automatically captures screenshots unless disabled
            - For failed steps (status="Fail"), it marks the test as failed in session_store
            - When used within a step (e.g., in BDD steps), adds the data as an assertion
            - Screenshots and API responses are stored in the step's evidence
        """
        try:
            current_test = self.session_store.current_test
            current_time = self.datetime_util.get_current_date_time()
            normalized_status = self._normalize_status(status)

            # Handle exception detail trimming if requested
            if trim_exception_detail and exception_detail:
                exception_detail = (
                    exception_detail[:3990] if len(exception_detail) > 3990 else exception_detail
                )

            if not current_test:
                self.logger.warning("No current test set in SessionStore")
                return

            # If within a step, add as assertion
            if self.session_store.current_step:
                step_data = self.session_store.current_step_details
                name = f"Assert {step_data['stepName']}: {expected_message}: {actual_message}"[:200]
                screenshot_path = None

                if take_screenshot:
                    screenshot_path = capture_screenshot(name, error=normalized_status == "F")
                    if screenshot_path:
                        add_screenshot_to_report(step_data, screenshot_path)

                assertion_data = self._create_assertion_data(
                    name=name,
                    expected_message=expected_message,
                    actual_message=actual_message,
                    status=normalized_status,
                    step_type=step_type,
                    current_time=current_time,
                    screenshot_path=screenshot_path,
                    api_response=api_response,
                    exception_detail=exception_detail,
                )

                step_data.setdefault("asserts", []).append(assertion_data)

                if normalized_status == "F":
                    step_data["stepStatus"] = "F"
                    # Add error message to step evidence
                    if exception_detail:
                        if "errorMessages" not in step_data["evidence"]:
                            step_data["evidence"]["errorMessages"] = []
                        step_data["evidence"]["errorMessages"].append(exception_detail)

                # Add API response if provided
                if api_response:
                    if "apiResponse" not in step_data["evidence"]:
                        step_data["evidence"]["apiResponse"] = {}
                    step_data["evidence"]["apiResponse"].update(api_response)

                return

            name = step_name or f"Assert {expected_message}: {actual_message}"[:200]
            screenshot_path = None

            if take_screenshot:
                screenshot_path = capture_screenshot(name, error=normalized_status == "F")

            assertion_data = self._create_assertion_data(
                name=name,
                expected_message=expected_message,
                actual_message=actual_message,
                status=normalized_status,
                step_type=step_type,
                current_time=current_time,
                screenshot_path=screenshot_path,
                api_response=api_response,
                exception_detail=exception_detail,
            )

            step_data = {
                "stepName": name,
                "stepStatus": normalized_status,
                "stepStartTime": current_time,
                "stepEndTime": current_time,
                "stepDurationSeconds": 0,
                "stepDuration": "0 seconds",
                "screenshot": None,
                "asserts": [assertion_data],
                "evidence": {},
            }

            if screenshot_path:
                add_screenshot_to_report(step_data, screenshot_path)

            if exception_detail:
                if "errorMessages" not in step_data["evidence"]:
                    step_data["evidence"]["errorMessages"] = []
                step_data["evidence"]["errorMessages"].append(exception_detail)

            if api_response:
                if "apiResponse" not in step_data["evidence"]:
                    step_data["evidence"]["apiResponse"] = {}
                step_data["evidence"]["apiResponse"].update(api_response)

            test_data = self.session_store.reporting["tests"].get(current_test, {})
            test_data.setdefault("steps", []).append(step_data)

            self.session_store.reporting["tests"][current_test] = test_data

        except Exception as e:
            self.logger.error(f"Error in insert_step: {str(e)}")

    def report_exception(
        self,
        message: str,
        exception_type: str = None,
        trace: str = None,
        context: dict = None,
        fail_test: bool = True,
    ) -> None:
        """Report an exception to result.json with screenshots if available.

        Args:
            message: Exception message
            exception_type: Type of exception
            trace: Stack trace info
            context: test context
            fail_test: Mark test as failed
        """
        if not self.session_store.current_test:
            return

        current_time = self.datetime_util.get_current_date_time()

        # Check if we have a driver available
        has_driver = (
            self.session_store.driver is not None or self.session_store.mobile_driver is not None
        )

        screenshot_path = None
        if has_driver:
            # Create meaningful screenshot name
            if self.session_store.current_step:
                screenshot_name = f"Exception_{exception_type}_{self.session_store.current_step}"
            else:
                # Extract origin from trace if available
                origin = None
                if trace and trace != "No Cafex stack trace available":
                    match = TRACE_ORIGIN_PATTERN.search(trace)
                    if match:
                        method, class_name = match.groups()
                        origin = f"{class_name}_{method}"
                    else:
                        # Fallback to just the last line of trace
                        last_frame = trace.strip().split("\n")[-1]
                        if "in" in last_frame:
                            origin = last_frame.split("in ")[-1].strip()

                # If no origin found from trace, get from context or use default
                if not origin:
                    if context and context.get("current_test"):
                        # Extract meaningful part from test path
                        test_path = context["current_test"]
                        test_name = test_path.split("::")[-1] if "::" in test_path else test_path
                        origin = f"Test_{test_name}"
                    else:
                        origin = "Custom_Exception"

                screenshot_name = (
                    f"Exception_{exception_type}_{origin}"
                    if exception_type != "Exception"
                    else f"Exception_{origin}"
                )

            # Capture screenshot
            screenshot_path = capture_screenshot(name=screenshot_name, error=True)

        # Prepare error info
        error_info = {
            "message": message,
            "type": exception_type,
            "timestamp": current_time,
            "phase": "step" if self.session_store.current_step else "test",
            "stackTrace": trace,
            "context": context,
            "screenshot": screenshot_path,
        }

        # Add to test data
        test_data = self.session_store.reporting["tests"].get(self.session_store.current_test, {})

        # Add exception to evidence.exceptions
        test_data["evidence"]["exceptions"].append(error_info)

        # Update test status to failed
        if fail_test:
            test_data["testStatus"] = "F"

        # Add screenshot to test evidence.screenshots
        if screenshot_path:
            test_data["evidence"]["screenshots"].append(screenshot_path)

        if self.session_store.current_step:
            step_data = self.session_store.current_step_details
            if "exceptions" not in step_data["evidence"]:
                step_data["evidence"]["exceptions"] = []

            # Add simplified exception info to step
            step_exception = {
                "message": message,
                "type": exception_type,
                "timestamp": current_time,
                "stackTrace": trace,
                "screenshot": screenshot_path,
            }
            step_data["evidence"]["exceptions"].append(step_exception)

            if fail_test:
                step_data["stepStatus"] = "F"
                step_data["stepEndTime"] = current_time
                duration_seconds = self.datetime_util.get_time_difference_seconds(
                    step_data["stepEndTime"], step_data["stepStartTime"]
                )
                step_data["stepDurationSeconds"] = duration_seconds
                step_data["stepDuration"] = self.datetime_util.seconds_to_human_readable(
                    duration_seconds
                )

                # Add step to test data
                test_data.setdefault("steps", []).append(step_data)

        self.session_store.reporting["tests"][self.session_store.current_test] = test_data
