from cafex_core.logging.logger_ import CoreLogger
from cafex_core.singletons_.request_ import RequestSingleton
from cafex_core.singletons_.session_ import SessionStore
from cafex_core.utils.config_utils import ConfigUtils
from cafex_core.utils.hooks_.hook_util import HookUtil


class PytestAfterScenario:
    def __init__(self, scenario, sys_args, feature):
        self.scenario = scenario
        self.sys_args = sys_args
        self.feature = feature
        self.request_ = RequestSingleton().request
        self.logger = CoreLogger(name=__name__).get_logger()
        self.session_store = SessionStore()
        self.config_utils = ConfigUtils()
        self.hook_util = HookUtil()
        self.is_parallel_execution = self.hook_util.is_parallel_execution(self.sys_args)

    def after_scenario_hook(self):
        fetch_run_on_mobile_bool = False
        if "run_on_mobile" in self.session_store.base_config:
            fetch_run_on_mobile_bool = self.config_utils.fetch_run_on_mobile()
        if "ui_web" in self.scenario.tags and not fetch_run_on_mobile_bool:
            self.after_scenario_browser_teardown()
        if "ui_thick_client" in self.scenario.tags and not self.is_parallel_execution:
            pass
        if "mobile_web" in self.scenario.tags and not self.is_parallel_execution:
            self.after_scenario_mobile_teardown()
        if "mobile_app" in self.scenario.tags:
            self.after_scenario_mobile_teardown()

        self.pop_scenario_end_values()

        self.logger.info(f"Completed execution of pytest-bdd scenario : {self.scenario.name}")

    def pop_scenario_end_values(self):
        try:
            str_test_name = self.request_.node.nodeid
            self.hook_util.pop_value_from_globals(str_test_name + "_bool_api_scenarios")
            self.hook_util.pop_value_from_globals(str_test_name + "_current_scenario_id")
            self.hook_util.pop_value_from_globals(str_test_name + "_scenario_failure_reason")
            self.hook_util.pop_value_from_globals(str_test_name + "_current_scenario_failed")
            self.hook_util.pop_value_from_globals(str_test_name + "_scenario_data_modify")
        except Exception as e:
            self.logger.error("Error in pop_scenario_end_values-->" + str(e))

    def after_scenario_browser_teardown(self):
        """This method is to teardown the browser based on the
        configuration."""
        try:
            bool_data = False
            scenario_name = self.scenario.name
            examples_len = len(self.scenario.feature.scenarios[scenario_name].examples.examples)

            def reset_session_store():
                self.session_store.driver = None
                self.session_store.counter = 1
                self.session_store.datadriven = 1

            def quit_and_reset(session_store, debug_id):
                self.quit_driver(session_store, debug_id)
                reset_session_store()

            if self.session_store.base_config.get("session_end_driver_teardown_flag") is False:
                if self.is_parallel_execution:
                    self.close_driver()
                    reset_session_store()
                else:
                    quit_and_reset(self.session_store, 4)
            elif self.session_store.base_config.get("skip_teardown_per_example_flag") is False:
                if examples_len == 0 and len(self.scenario.params) == 0:
                    bool_data = True
                if examples_len == 0 and bool_data and not self.is_parallel_execution:
                    quit_and_reset(self.session_store, 1)
                else:
                    if examples_len > 0 and examples_len == self.session_store.counter:
                        quit_and_reset(self.session_store, 2)
                    elif self.session_store.datadriven == self.session_store.rowcount:
                        quit_and_reset(self.session_store, 3)
                    else:
                        self.session_store.datadriven += 1
                        self.session_store.counter += 1
                    if self.is_parallel_execution:
                        self.close_driver()
                        reset_session_store()
            if examples_len == 0:
                bool_data = True
            if examples_len == 0 and bool_data and not self.is_parallel_execution:
                quit_and_reset(self.session_store, 5)
            else:
                if (
                    examples_len == self.session_store.counter
                    or self.session_store.datadriven == self.session_store.rowcount
                ):
                    quit_and_reset(self.session_store, 6)
                else:
                    if self.session_store.datadriven == self.session_store.rowcount:
                        quit_and_reset(self.session_store, 7)
                    else:
                        self.session_store.datadriven += 1
                    self.session_store.counter += 1
                if (
                    self.is_parallel_execution
                    and self.session_store.datadriven != self.session_store.rowcount
                ):
                    quit_and_reset(self.session_store, 8)
        except Exception as e:
            self.logger.exception("Error in after_scenario_browser_teardown-->" + str(e))

    def close_driver(self):
        try:
            self.session_store.driver.close()
        except Exception as e:
            self.logger.exception(f"Error while closing driver : {e}")

    def quit_driver(self, session_object, debug_id):
        try:
            session_object.driver.quit()
        except Exception as e:
            self.logger.exception(f"Error while quitting driver {e} : Debug Id : {debug_id}")

    def after_scenario_mobile_teardown(self):
        """
        Description:
            |  This method is invoked after every scenario

        """
        try:
            if "mobile_after_scenario_flag" in self.session_store.mobile_config.keys():
                if self.session_store.mobile_config["mobile_after_scenario_flag"] is True:
                    if self.session_store.mobile_driver is not None:
                        self.session_store.mobile_driver.quit()
                        self.session_store.mobile_driver = None
        except Exception as e:
            self.logger.exception("Error in after_scenario_mobile_teardown-->" + str(e))
