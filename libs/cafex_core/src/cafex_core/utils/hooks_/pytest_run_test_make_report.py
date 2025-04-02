"""This module contains the PytestRunTestMakeReport class which modifies test
reports based on verification failures."""

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.singletons_.session_ import SessionStore


class PytestRunTestMakeReport:
    """A class that handles modifying test reports based on verification
    failures."""

    def __init__(self, report_):
        """Initialize the PytestRunTestMakeReport class."""
        self.report = report_
        self.logger = CoreLogger(name=__name__).get_logger()
        self.session_store = SessionStore()

    def run_make_report(self):
        """Modifies the test report based on verification failures."""
        try:
            if self.report.when == "call" and not self.report.failed:
                if self.session_store.is_current_test_failed():
                    # Mark the report as failed
                    self.report.outcome = "failed"

                    # Log the modification
                    self.logger.warning(
                        f"Test marked as failed due to verification failures: {self.session_store.current_test}"
                    )
        except Exception as e:
            self.logger.error(f"Error in run_make_report: {e}")
            self.logger.exception(e)
