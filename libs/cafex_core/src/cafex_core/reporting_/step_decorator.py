from functools import wraps

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.reporting_.screenshot_utils import (
    add_screenshot_to_report,
    capture_screenshot,
)
from cafex_core.singletons_.session_ import SessionStore
from cafex_core.utils.date_time_utils import DateTimeActions


def step(description: str):
    """Decorator to create structured steps in pytest and unittest test cases.

    This decorator provides BDD-style organization by:
    - Creating a named step in the test report
    - Tracking step execution time
    - Capturing screenshots
    - Collecting evidence (assertions, exceptions)

    Args:
        description (str): Description of the step that will appear in the report

    Note:
        - Only for use with pytest and unittest test cases
        - Do not use with pytest-bdd tests (which handle steps automatically)
        - Must be used within a test method

    Example:
        ```python
        class TestLoginPytest:
            def test_login_flow(self):
                @step("User is on login page")
                def verify_login_page():
                    # This becomes a step in the report
                    assert login_page.is_displayed()

                @step("User enters credentials")
                def enter_credentials():
                    # Another step with its own timing and evidence
                    login_page.enter_username("user")
                    login_page.enter_password("pass")

                # Execute the steps
                verify_login_page()
                enter_credentials()
        ```

    The above will create a report with:
    - Two named steps
    - Start and end time for each step
    - Screenshots taken at step completion
    - Any assertions or exceptions that occurred
    - All evidence collected during step execution
    """

    def decorator(func):
        """Internal decorator that wraps the test function.

        Args:
            func: The function to be wrapped

        Returns:
            wrapper: The wrapped function with step tracking
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            """Wrapper that handles step execution and reporting.

            This wrapper:
            1. Creates step data structure
            2. Executes the wrapped function
            3. Captures evidence (screenshots, assertions)
            4. Records timing information
            5. Handles exceptions
            6. Updates the test report

            Returns:
                Result of the wrapped function

            Raises:
                ValueError: If current_test is not set in SessionStore
                AssertionError: If any assertions fail in the step
            """
            logger = CoreLogger(name=__name__).get_logger()
            logger.info(f"Executing step: {description}")
            session_store = SessionStore()
            date_time_util = DateTimeActions()

            if session_store.current_test is None:
                raise ValueError("current_test is not set in SessionStore")

            test_data = session_store.reporting["tests"][session_store.current_test]
            step_data = {
                "stepName": description,
                "stepStatus": "P",
                "stepStartTime": date_time_util.get_current_date_time(),
                "stepEndTime": None,
                "stepDurationSeconds": None,
                "stepDuration": None,
                "screenshot": None,
                "asserts": [],
                "evidence": {},
            }

            session_store.current_step = description
            session_store.current_step_details = step_data

            try:
                result = func(*args, **kwargs)
                screenshot_path = capture_screenshot(description)
                add_screenshot_to_report(step_data, screenshot_path)
                logger.info("Step Execution Complete")
                return result
            except AssertionError as e:
                step_data["stepStatus"] = "F"
                screenshot_path = capture_screenshot(description, error=True)
                add_screenshot_to_report(step_data, screenshot_path)
                logger.error(f"error in custom step for node: {session_store.current_test}")
                raise e
            finally:
                step_data["stepEndTime"] = date_time_util.get_current_date_time()

                duration_seconds = date_time_util.get_time_difference_seconds(
                    step_data["stepEndTime"], step_data["stepStartTime"]
                )
                step_data["stepDurationSeconds"] = duration_seconds
                step_data["stepDuration"] = date_time_util.seconds_to_human_readable(
                    duration_seconds
                )
                test_data["steps"].append(step_data)
                session_store.current_step = None
                session_store.current_step_details = None

        return wrapper

    return decorator
