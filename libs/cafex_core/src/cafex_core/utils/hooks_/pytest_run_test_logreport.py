"""This module contains the PytestRunLogReport class which is used to handle
the logging of test run reports in Pytest.

It includes methods to initialize the class and run the log report.
"""

import os

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.singletons_.session_ import SessionStore
from cafex_core.utils.date_time_utils import DateTimeActions


class PytestRunLogReport:
    """A class that handles the logging of test run reports in Pytest.

    Attributes:
        report (Report): The pytest report object.
        logger (Logger): The logger object.
        session_store (SessionStore): The session store object.

    Methods:
        __init__: Initializes the PytestRunLogReport class.
        run_log_report: Runs the log report.
    """

    def __init__(self, report):
        """Initialize the PytestRunLogReport class.

        Args:
            report: The pytest report object.
        """
        self.report = report
        self.logger = CoreLogger(name=__name__).get_logger()
        self.session_store = SessionStore()
        self.date_time_util = DateTimeActions()

    def run_log_report(self):
        """Runs the log report.

        It logs the outcome and when of the report, and the worker ID.
        It also updates the reporting attribute of the session store.
        """
        outcome_ = self.report.outcome
        when_ = self.report.when
        worker_ = os.getenv("PYTEST_XDIST_WORKER", None)
        node_id = self.report.nodeid
        outcome_map = {"passed": "P", "failed": "F"}
        update_status = False

        if worker_ is not None:
            self.session_store.reporting["tests"][node_id].update({when_: {"outcome": outcome_}})
            update_status = True
        elif worker_ is None and self.session_store.workers_count > 0:
            pass
        else:
            self.session_store.reporting["tests"][node_id].update({when_: {"outcome": outcome_}})
            update_status = True
        if update_status:
            test_data = self.session_store.reporting["tests"][node_id]
            error_messages = []
            current_time = self.date_time_util.get_current_date_time()
            duration_seconds = self.date_time_util.get_time_difference_seconds(
                current_time, test_data["startTime"]
            )

            test_data["endTime"] = current_time
            test_data["durationSeconds"] = duration_seconds
            test_data["duration"] = self.date_time_util.seconds_to_human_readable(duration_seconds)

            if when_ == "call":
                # Check if test had any failed assertions/steps
                if self.session_store.is_current_test_failed():
                    test_data["testStatus"] = "F"
                else:
                    test_data["testStatus"] = outcome_map[outcome_]
                self.logger.info("Test execution completed")

                # Clear the test status after processing
                self.session_store.clear_current_test_status()
                self.session_store.current_test = None

                if outcome_ == "failed":
                    error_messages.append(
                        {
                            "name": node_id,
                            "message": str(self.report.longrepr),
                            "type": "pytest",
                            "timestamp": current_time,
                            "phase": when_,
                        }
                    )
                # Add all stored error messages for this test
                stored_errors = self.session_store.get_error_messages(self.report.nodeid)
                if stored_errors:
                    error_messages.extend(stored_errors)

                if error_messages:
                    test_data["evidence"]["errorMessages"] = error_messages
