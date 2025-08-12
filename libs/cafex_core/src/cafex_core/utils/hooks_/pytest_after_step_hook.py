from cafex_core.logging.logger_ import CoreLogger
from cafex_core.reporting_.screenshot_utils import (
    add_screenshot_to_report,
    capture_screenshot,
)
from cafex_core.singletons_.request_ import RequestSingleton
from cafex_core.singletons_.session_ import SessionStore
from cafex_core.utils.date_time_utils import DateTimeActions


class PytestBddAfterStep:
    def __init__(self, step):
        self.logger = CoreLogger(name=__name__).get_logger()
        self.date_time_util = DateTimeActions()
        self.session_store = SessionStore()
        self.request_ = RequestSingleton().request
        self.step = step
        self.step_details = None

    def after_step_hook(self):
        try:
            self.logger.info("Step Execution Complete")
            self.after_step_dash_auto_config()
        except Exception as e:
            self.logger.error(f"Error in after_step_hook: {e}")

    def after_step_dash_auto_config(self):
        node_id = self.request_.node.nodeid
        try:
            if f"{node_id}_current_scenario_id" in self.session_store.globals:
                self.step_details = self.session_store.current_step_details

                self.capture_screenshot_for_step()

                self.step_details["stepStatus"] = self.get_step_status()
                if self.step_details.get("asserts"):
                    failed_assertions = any(
                        assertion["status"] == "F" for assertion in self.step_details["asserts"]
                    )
                    if failed_assertions:
                        self.step_details["stepStatus"] = "F"

                self.step_details["stepEndTime"] = self.date_time_util.get_current_date_time()

                duration_seconds = self.date_time_util.get_time_difference_seconds(
                    self.step_details["stepEndTime"], self.step_details["stepStartTime"]
                )
                self.step_details["stepDurationSeconds"] = duration_seconds
                self.step_details["stepDuration"] = self.date_time_util.seconds_to_human_readable(
                    duration_seconds
                )

                test_data = self.session_store.reporting["tests"].get(node_id)
                test_data.setdefault("steps", []).append(self.step_details)
                if self.step_details["stepStatus"] == "F":
                    test_data["testStatus"] = "F"
                self.session_store.reporting["tests"][node_id] = test_data

        except Exception as e:
            self.logger.error(f"Error in after_step_auto_dash_configuration: {e}")
        finally:
            self.session_store.current_step = None
            self.session_store.current_step_details = None

    def get_step_status(self):
        try:
            return "F" if self.step.failed else "P"
        except Exception as e:
            self.logger.error(f"Error in get_step_status: {e}")

    def capture_screenshot_for_step(self):
        """
        Description:
            |  This method is used to save screenshots of UI applications

        :return: None
        """
        try:
            screenshot_path = capture_screenshot(self.step.name)
            add_screenshot_to_report(self.step_details, screenshot_path)
        except Exception as e:
            self.logger.error(f"Error while saving screenshot: {e}")
            raise
