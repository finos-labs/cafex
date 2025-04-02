import sys

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.singletons_.request_ import RequestSingleton
from cafex_core.singletons_.session_ import SessionStore
from cafex_core.utils.config_utils import ConfigUtils
from cafex_core.utils.date_time_utils import DateTimeActions
from cafex_core.utils.regex_constants import (
    MULTIPLE_WHITESPACE_PATTERN,
    STEP_NAME_WHITESPACE_PATTERN,
)


class PytestBddBeforeStep:
    def __init__(self, scenario_, step_):
        self.scenario = scenario_
        self.step = step_
        self.request_ = RequestSingleton().request
        self.logger = CoreLogger(name=__name__).get_logger()
        self.date_time_util = DateTimeActions()
        self.session_store = SessionStore()
        self.config_utils = ConfigUtils()

    def before_step_hook(self):
        self.before_step_auto_dash_configuration()

    def before_step_auto_dash_configuration(self):
        try:
            step_name = MULTIPLE_WHITESPACE_PATTERN.sub(
                " ", STEP_NAME_WHITESPACE_PATTERN.sub(" ", self.step.name)
            ).strip()
            node_id = self.request_.node.nodeid

            self.session_store.current_step = step_name

            if f"{node_id}_current_scenario_id" in self.session_store.globals:
                current_time = self.date_time_util.get_current_date_time()
                step_details = {
                    "stepName": step_name,
                    "stepStatus": "IC",
                    "stepStartTime": current_time,
                    "stepEndTime": None,
                    "stepDurationSeconds": None,
                    "stepDuration": None,
                    "screenshot": None,
                    "asserts": [],
                    "evidence": {},
                }

                if "--lf" in sys.argv:
                    step_details["reRunIteration"] = self.config_utils.base_config[
                        "rerun_iteration"
                    ]

                self.session_store.current_step_details = step_details

            self.logger.info(f"Executing step: {step_name}")

        except Exception as error_:
            self.logger.error(f"Error in before_step_auto_dash_configuration: {error_}")
