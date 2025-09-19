from cafex_core.logging.logger_ import CoreLogger
from cafex_core.singletons_.session_ import SessionStore
from cafex_core.utils.config_utils import ConfigUtils
from cafex_desktop.desktop_client.desktop_application_handler import (
    DesktopApplicationHandler,
)
from cafex_desktop.desktop_client.desktop_client_actions.base_desktop_client_actions import (
    DesktopClientActions,
)


class DesktopClientDriverInitializer:
    """
    The DesktopClientDriverInitializer class is responsible for initializing the desktop client
    driver.

    It sets up the driver and handles the configuration for the desktop client.
    """

    def __init__(self):
        self.logger = CoreLogger(name=__name__).get_logger()
        self.session_store = SessionStore()
        self.config_utils = ConfigUtils()

    def initialize_driver(self):
        try:
            if self.session_store.ui_desktop_client_scenario:
                desktop_client_config = self.config_utils.fetch_thick_client_parameters()
                self.session_store.globals["obj_dah"] = DesktopApplicationHandler(
                    desktop_client_config
                )
                self.session_store.handler = self.session_store.globals["obj_dah"].get_handler()
                self.session_store.globals["obj_dca"] = DesktopClientActions(
                    self.session_store.handler
                )
        except Exception as error_before_scenario_desktop_client_setup:
            self.logger.error(
                "Error occurred in initialize driver method: %s",
                str(error_before_scenario_desktop_client_setup),
            )
            raise error_before_scenario_desktop_client_setup
