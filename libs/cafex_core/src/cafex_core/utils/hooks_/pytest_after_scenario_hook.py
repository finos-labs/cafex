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
        self.session_context = self.session_store.context
        self.metadata = self.session_context.metadata
        self.drivers = self.session_context.drivers
        self.config_utils = ConfigUtils()
        self.hook_util = HookUtil()
        self.is_parallel_execution = self.hook_util.is_parallel_execution(self.sys_args)

    def after_scenario_hook(self):
        fetch_run_on_mobile_bool = False
        base_config = self.metadata.base_config or {}
        if "run_on_mobile" in base_config:
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
            metadata = self.metadata
            drivers = self.drivers
            base_config = metadata.base_config or {}

            def reset_session_state():
                drivers.driver = None
                metadata.counter = 1
                metadata.datadriven = 1

            def quit_and_reset(debug_id):
                self.quit_driver(debug_id)
                reset_session_state()

            if base_config.get("session_end_driver_teardown_flag") is False:
                if self.is_parallel_execution:
                    self.close_driver()
                    reset_session_state()
                else:
                    quit_and_reset(4)
            elif base_config.get("skip_teardown_per_example_flag") is False:
                if examples_len == 0 and len(self.scenario.params) == 0:
                    bool_data = True
                if examples_len == 0 and bool_data and not self.is_parallel_execution:
                    quit_and_reset(1)
                else:
                    if examples_len > 0 and examples_len == metadata.counter:
                        quit_and_reset(2)
                    elif metadata.datadriven == metadata.rowcount:
                        quit_and_reset(3)
                    else:
                        metadata.datadriven += 1
                        metadata.counter += 1
                    if self.is_parallel_execution:
                        self.close_driver()
                        reset_session_state()
            if examples_len == 0:
                bool_data = True
            if examples_len == 0 and bool_data and not self.is_parallel_execution:
                quit_and_reset(5)
            else:
                if (
                    examples_len == metadata.counter
                    or metadata.datadriven == metadata.rowcount
                ):
                    quit_and_reset(6)
                else:
                    if metadata.datadriven == metadata.rowcount:
                        quit_and_reset(7)
                    else:
                        metadata.datadriven += 1
                    metadata.counter += 1
                if (
                    self.is_parallel_execution
                    and metadata.datadriven != metadata.rowcount
                ):
                    quit_and_reset(8)
        except Exception as e:
            self.logger.exception("Error in after_scenario_browser_teardown-->" + str(e))

    def close_driver(self):
        try:
            if self.drivers.driver is not None:
                self.drivers.driver.close()
        except Exception as e:
            self.logger.exception(f"Error while closing driver : {e}")

    def quit_driver(self, debug_id):
        try:
            if self.drivers.driver is not None:
                self.drivers.driver.quit()
        except Exception as e:
            self.logger.exception(f"Error while quitting driver {e} : Debug Id : {debug_id}")

    def after_scenario_mobile_teardown(self):
        """
        Description:
            |  This method is invoked after every scenario

        """
        try:
            mobile_config = self.metadata.mobile_config or {}
            if mobile_config.get("mobile_after_scenario_flag") is True:
                if self.drivers.mobile_driver is not None:
                    self.drivers.mobile_driver.quit()
                    self.drivers.mobile_driver = None
        except Exception as e:
            self.logger.exception("Error in after_scenario_mobile_teardown-->" + str(e))
