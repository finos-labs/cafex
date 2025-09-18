"""This module contains the PytestBDDStepError class for custom error reporting
and logging in pytest-bdd tests."""

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.reporting_.screenshot_utils import (
    add_screenshot_to_report,
    capture_screenshot,
)
from cafex_core.singletons_.request_ import RequestSingleton
from cafex_core.singletons_.session_ import SessionStore
from cafex_core.utils.date_time_utils import DateTimeActions


class PytestBDDStepError:
    """A class that handles the logging of test run reports in Pytest.

    Attributes:
        logger (Logger): The logger object.
        session_store (SessionStore): The session store object.
         step (pytest_bdd.parser.Step): The step that failed.
    Methods:
        __init__: Initializes the PytestBDDStepError class.
        bdd_step_error: step status and logging of failure.
    """

    def __init__(self, step):
        """Initialize the PytestBDDStepError class."""

        self.logger = CoreLogger(name=__name__).get_logger()
        self.date_time_util = DateTimeActions()
        self.session_store = SessionStore()
        self.session_context = self.session_store.context
        self.metadata = self.session_context.metadata
        self.reporting = self.session_context.reporting
        self.test_context = self.session_context.test
        self.request_ = RequestSingleton().request
        self.step = step

    def bdd_step_error(self):
        """This hook is called when a step fails.

        We use it to attach rich information to report.json and Allure
        reports.
        """
        node_id = self.request_.node.nodeid
        try:
            self.logger.error(f"error in BDD step for node: {node_id}")
            if f"{node_id}_current_scenario_id" in self.metadata.globals:
                step_details = self.test_context.current_step_details
                self.capture_screenshot_for_step_error(step_details)
                step_details["stepEndTime"] = self.date_time_util.get_current_date_time()

                duration_seconds = self.date_time_util.get_time_difference_seconds(
                    step_details["stepEndTime"], step_details["stepStartTime"]
                )

                step_details["stepDurationSeconds"] = duration_seconds
                step_details["stepDuration"] = self.date_time_util.seconds_to_human_readable(
                    duration_seconds
                )

                step_details["stepStatus"] = "F"
                self.metadata.globals[f"{node_id}_current_scenario_failed"] = "Yes"

                test_data = self.reporting["tests"].get(node_id, {})
                test_data.setdefault("steps", []).append(step_details)
                self.reporting["tests"][node_id] = test_data

        except Exception as e:
            self.logger.error(f"Error in bdd step error hook: {e}")
        finally:
            self.test_context.current_step = None
            self.test_context.current_step_details = None

    def capture_screenshot_for_step_error(self, step_details):
        """Takes a screenshot for a failed step and updates the evidence in
        step_details."""
        try:
            screenshot_path = capture_screenshot(self.step.name, error=True)
            add_screenshot_to_report(step_details, screenshot_path)
        except Exception as e:
            self.logger.error(f"Error while saving screenshot: {e}")
            raise
