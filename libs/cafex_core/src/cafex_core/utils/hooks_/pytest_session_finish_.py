"""This module contains the PytestSessionFinish class which is used to handle
the end of a pytest session.

It includes methods to initialize the class and finish the session,
which involves logging the session finish event and saving the session
report to a JSON file.
"""

import os
from datetime import datetime

import xdist
from cafex_core.handlers.file_handler import FileHandler
from cafex_core.handlers.folder_handler import FolderHandler
from cafex_core.logging.logger_ import CoreLogger
from cafex_core.reporting_.report_generator import ReportGenerator
from cafex_core.singletons_.session_ import SessionStore
from cafex_core.utils.date_time_utils import DateTimeActions
from cafex_core.utils.regex_constants import INVALID_FILENAME_CHARS_PATTERN


class PytestSessionFinish:
    """A class that handles the end of a pytest session.

    Attributes:
        session_ (Session): The pytest session object.
        logger (Logger): The logger object.
        session_store (SessionStore): The session store object.

    Methods:
        __init__: Initializes the PytestSessionFinish class.
        session_finish_: Finishes the session.
    """

    def __init__(self, session_):
        """Initialize the PytestSessionFinish class.

        Args:
            session_: The pytest session object.
        """
        self.scenarios_folder = None
        self.session_ = session_
        self.logger = CoreLogger(name=__name__).get_logger()
        self.session_store = SessionStore()
        self.session_context = self.session_store.context
        self.reporting = self.session_context.reporting
        self.paths = self.session_context.paths
        self.drivers = self.session_context.drivers
        self.metadata = self.session_context.metadata
        self.file_handler = FileHandler()
        self.folder_handler = FolderHandler()
        self.datetime_util = DateTimeActions()
        self.tests_data = []
        self.execution_data = {}
        self.collection_data = {}

    def session_finish_(self):
        """Finishes the session.

        It logs the session finish event and saves the session report to
        a JSON file in the specified result directory. The file name
        includes the current date and time to ensure uniqueness.
        """
        self.scenarios_folder = self.paths.temp_execution_dir + os.sep + "scenarios"
        if not os.path.exists(self.scenarios_folder):
            os.makedirs(self.scenarios_folder)
        for node_id in self.reporting["tests"]:
            file_name = node_id.replace("/", "-").replace("::", "-")
            # Sanitize the filename by removing invalid characters
            file_name = INVALID_FILENAME_CHARS_PATTERN.sub("", file_name)
            self.file_handler.create_json_file(
                self.scenarios_folder,
                f"{file_name}.json",
                self.reporting["tests"][node_id],
            )

        self.driver_teardown()

        if xdist.get_xdist_worker_id(self.session_) == "master":
            self.logger.info("Combining all files")
            self.combine_all_tests_data()
            self.generate_report()

    def combine_all_tests_data(self):
        """Combines all the JSON files in the scenarios folder into a single
        JSON file.

        The combined JSON file is saved in the result directory.
        """
        for file_name in os.listdir(self.scenarios_folder):
            test_data = self.file_handler.read_data_from_json_file(
                self.scenarios_folder + os.sep + file_name
            )
            # Gather screenshots from step evidence
            if "steps" in test_data:
                for step in test_data["steps"]:
                    if "evidence" in step:
                        if "screenshots" in step["evidence"]:
                            # Extract screenshot paths from the evidence dictionary
                            screenshot_paths = list(step["evidence"]["screenshots"].values())
                            test_data["evidence"]["screenshots"].extend(screenshot_paths)
                self.tests_data.append(test_data)  # Append the modified test_data

    def generate_report(self):
        """Generates a report by combining collection data, execution data, and
        test data.

        This method reads data from the 'collection.json' and
        'execution.json' files located in the temporary directory. It
        then combines this data with the test data into a single
        dictionary. Finally, it creates a new JSON file named
        'result.json' in the result directory, containing the combined
        data.

        The structure of the 'result.json' file is as follows: {
        "collection_info": <data from 'collection.json'>,
        "execution_info": <data from 'execution.json'>,     "tests":
        <test data> }
        """
        execution_end_time = self.datetime_util.get_current_date_time()
        self.execution_data = self.file_handler.read_data_from_json_file(
            os.path.join(self.paths.temp_execution_dir, "execution.json")
        )
        self.collection_data = self.file_handler.read_data_from_json_file(
            os.path.join(self.paths.temp_execution_dir, "collection.json")
        )

        self.execution_data.update({"executionEndTime": execution_end_time})

        duration_seconds = self.datetime_util.get_time_difference_seconds(
            execution_end_time, self.execution_data.get("executionStartTime")
        )
        self.execution_data.update(
            {
                "executionDurationSeconds": duration_seconds,
                "executionDuration": self.datetime_util.seconds_to_human_readable(duration_seconds),
            }
        )

        self.execution_data.update({"executionStatus": self.find_execution_status(self.tests_data)})

        restructured_tests = self.restructure_tests_data(self.tests_data)
        # Combine all test data into a single dictionary
        report_data = {
            "collectionInfo": self.collection_data,
            "executionInfo": self.execution_data,
            "tests": restructured_tests,
        }

        # Generate the JSON report
        self.file_handler.create_json_file(
            self.paths.execution_dir, "result.json", report_data
        )
        ReportGenerator.prepare_report_viewer(self.paths.execution_dir)
        self.folder_handler.delete_folder(self.paths.temp_dir)

    def find_execution_status(self, tests_data):
        """Determines the overall execution status based on individual test
        results.

        Args:
            tests_data (list): A list of test data dictionaries.

        Returns:
            str: The execution status ('P' for passed, 'F' for failed, 'E' for error).
        """
        total_passed = 0
        total_failed = 0

        for each_test_data in tests_data:
            if "testStatus" in each_test_data:
                if each_test_data["testStatus"] == "F":
                    total_failed += 1  # Increment failed count in feature details
                else:
                    total_passed += 1  # Increment passed count in feature details

        # Update execution_info with total counts
        self.execution_data["totalPassed"] = total_passed
        self.execution_data["totalFailed"] = total_failed

        if total_failed > 0:
            return "F"  # Return "F" if any test failed
        else:
            return "P"  # Return "P" only if all tests passed

    def driver_teardown(self):
        """Quits the driver if it is not None."""
        try:
            driver = self.drivers.driver
            mobile_driver = self.drivers.mobile_driver
            if driver is not None:
                driver.quit()
                self.logger.info("Driver quit successfully")
                self.drivers.driver = None
            if mobile_driver is not None:
                mobile_driver.quit()
                self.logger.info("Mobile driver quit successfully")
                self.drivers.mobile_driver = None
        except Exception as e:
            self.logger.error(f"Error in driver teardown: {e}")

    @staticmethod
    def restructure_tests_data(tests_data):
        """Restructures the tests data by grouping tests by their type and
        sorting by start time.

        Args:
            tests_data (list): A list of test data dictionaries.

        Returns:
            dict: Restructured tests data.
        """
        new_tests = {"pytestBdd": [], "pytest": [], "unittest": []}

        # Categorize tests
        for test in tests_data:
            test_type = test["testType"]
            if test_type in new_tests:
                new_tests[test_type].append(test)

        # Sort each category by start_time (high to low)
        for test_type in new_tests:
            new_tests[test_type].sort(
                key=lambda x: datetime.strptime(x["startTime"], "%Y-%m-%dT%H:%M:%S.%f")
            )

        return new_tests
