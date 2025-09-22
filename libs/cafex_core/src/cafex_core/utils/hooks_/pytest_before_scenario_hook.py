"""This module contains the PytestBeforeScenario class which is used to handle
the before scenario hook in Pytest."""

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.singletons_.session_ import SessionStore
from cafex_core.utils.item_attribute_accessor import ItemAttributeAccessor

from .hook_util import HookUtil


class PytestBeforeScenario:
    """A class that handles the before scenario hook in Pytest."""

    def __init__(self, feature_, scenario_, request_, args_):
        """Initialize the PytestBeforeScenario class.

        Args:
            scenario_: The pytest scenario to be managed.
        """
        self.scenario = scenario_
        self.feature = feature_
        self.request = request_
        self.args = args_
        self.session_store = SessionStore()
        self.logger = CoreLogger(name=__name__).get_logger()
        self.hook_util = HookUtil()
        self.scenario_tags = list(self.scenario.tags)
        self.item_attribute_accessor = None

    def before_scenario_hook(self):
        """The before scenario hook method that is called before each scenario.

        It logs the before scenario event and the worker ID.
        """

        self.logger.info(f"Starting execution of pytest-bdd scenario : {self.scenario.name}")
        self.before_scenario_report_configuration()
        self.scenario_setup()

    def scenario_setup(self):
        if any(tag in self.scenario_tags for tag in ["ui_web", "mobile_web"]):
            from cafex_ui.web_client.ui_web_driver_initializer import (
                WebDriverInitializer,
            )

            self.session_store.ui_scenario = True
            if (self.session_store.datadriven >= self.session_store.rowcount + 1) or len(
                    self.scenario.feature.scenarios[self.scenario.name].examples.examples
            ) >= self.session_store.counter:
                if self.session_store.driver is None:
                    WebDriverInitializer().initialize_driver()
            else:
                if self.session_store.driver is None:
                    WebDriverInitializer().initialize_driver()
        elif "mobile_app" in self.scenario_tags:
            from cafex_ui.mobile_client.mobile_driver_initializer import (
                MobileDriverInitializer,
            )

            self.session_store.mobile_ui_scenario = True
            if (self.session_store.datadriven >= self.session_store.rowcount + 1) or len(
                    self.scenario.feature.scenarios[self.scenario.name].examples.examples
            ) >= self.session_store.counter:
                MobileDriverInitializer().initialize_driver()
            else:
                MobileDriverInitializer().initialize_driver()
        elif "ui_desktop_client" in self.scenario_tags:
            from cafex_desktop.desktop_client.desktop_client_driver_initializer \
                import DesktopClientDriverInitializer
            self.session_store.ui_desktop_client_scenario = True
            if (self.session_store.datadriven >= self.session_store.rowcount + 1) or len(
                    self.scenario.feature.scenarios[self.scenario.name].examples.examples
            ) >= self.session_store.counter:
                DesktopClientDriverInitializer().initialize_driver()
            else:
                DesktopClientDriverInitializer().initialize_driver()
        elif "playwright_web" in self.scenario_tags and "ui_web" not in self.scenario_tags:
            from cafex_ui.web_client.ui_web_driver_initializer import (
                WebDriverInitializer,
            )
            self.session_store.playwright_ui_scenario = True
            if (self.session_store.datadriven >= self.session_store.rowcount + 1) or len(
                    self.scenario.feature.scenarios[self.scenario.name].examples.examples
            ) >= self.session_store.counter:
                if self.session_store.driver is None:
                    WebDriverInitializer().initialize_playwright_driver()
            else:
                if self.session_store.driver is None:
                    WebDriverInitializer().initialize_playwright_driver()

    def before_scenario_report_configuration(self):
        try:
            node_id = self.request.node.nodeid
            item = self.request.node
            self.item_attribute_accessor = ItemAttributeAccessor(item)

            self._set_scenario_globals(node_id)
            feature_details = self._get_feature_details()
            scenario_details = self._get_scenario_details(feature_details)
            self._update_test_data(node_id, scenario_details)
        except Exception as e:
            self.logger.error(f"Error in before_scenario_report_configuration: {e}")

    def _set_scenario_globals(self, node_id):
        globals_to_set = {
            "_current_scenario_id": node_id,
            "_scenario_data_modify": {},
            "_scenario_failure_reason": "",
            "_current_scenario_failed": "No",
            "_scenario_tags": str(self.scenario.tags),
        }
        for key, value in globals_to_set.items():
            self.session_store.globals[f"{node_id}{key}"] = value

        if "api" in self.scenario.tags:
            self.session_store.globals[f"{node_id}_bool_api_scenarios"] = "True"

    def _get_feature_details(self):
        try:
            feature_file, feature_name = self.hook_util.get_feature_file_and_its_name(self.feature)
            return {
                "featureName": feature_name,
                "featureDescription": self.feature.description,
                "featureTags": list(self.feature.tags),
            }
        except Exception as e:
            self.logger.error(f"Error in _get_feature_details: {e}")

    def _get_scenario_details(self, feature_details):
        try:
            scenario_details = feature_details.copy()
            scenario_details.update(
                {
                    "scenarioName": self.scenario.name,
                    "scenarioTags": self.scenario_tags,
                    "scenarioDescription": self.scenario.description,
                }
            )
            return scenario_details
        except Exception as e:
            self.logger.error(f"Error in _get_scenario_details: {e}")

    def _update_test_data(self, node_id, scenario_details):
        try:
            is_data_driven, is_outline, example = self._get_data_set_info()
            test_data = self.session_store.reporting["tests"].get(node_id, {})
            if self.item_attribute_accessor.is_scenario:
                test_data.update(
                    {
                        "scenario": scenario_details,
                        "isDataDriven": is_data_driven,
                        "isOutline": is_outline,
                        "example": example,
                    }
                )
            self.session_store.reporting["tests"][node_id] = test_data
        except Exception as e:
            self.logger.error(f"Error in _update_test_data: {e}")

    def _get_data_set_info(self):
        """Get information about the data set being used in the scenario.

        Handles both scenario outlines and parametrized (data-driven)
        tests correctly.
        """
        try:
            is_data_driven = is_outline = False
            example = None
            if hasattr(self.request.node, "callspec") and self.request.node.callspec.params:
                params = self.request.node.callspec.params
                is_data_driven = True
                is_outline = "_pytest_bdd_example" in params
                example_data = params.get("_pytest_bdd_example") or params
                example = str(dict(sorted(example_data.items()))).replace("'", "")
            return is_data_driven, is_outline, example
        except Exception as e:
            self.logger.error(f"Error in _get_data_set_info: {e}")
            return False, False, None
