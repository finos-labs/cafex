from selenium.webdriver.remote.webdriver import WebDriver
from cafex_ui.web_client.web_client_actions.element_interactions import (
    ElementInteractions,
)
from cafex_ui.web_client.web_client_actions.utility_methods import (
    UtilityMethods,
)
from cafex_ui.web_client.web_client_actions.webdriver_interactions import (
    WebDriverInteractions,
)


class WebClientActions(WebDriverInteractions, ElementInteractions, UtilityMethods):
    """A class used to represent WebClientActions."""

    def __init__(
            self,
            web_driver: WebDriver = None,
            default_explicit_wait: int = None,
            default_implicit_wait: int = None,
    ):
        """Initializes WebClientActions with a driver and optional explicit
        wait.

        Args:
            web_driver: The selenium webdriver instance.
                            if not provided, it will be picked from Session Store
            default_explicit_wait: The default explicit wait time (in seconds).
                                   If not provided, it will be retrieved from ConfigUtils.
        """
        super().__init__(
            web_driver=web_driver,
            default_explicit_wait=default_explicit_wait,
            default_implicit_wait=default_implicit_wait,
        )
        self.navigate_methods = WebDriverInteractions(
            web_driver=self.driver,
            default_explicit_wait=self.default_explicit_wait,
            default_implicit_wait=self.default_implicit_wait,
        )
        self.element_interactions = ElementInteractions(
            web_driver=self.driver,
            default_explicit_wait=self.default_explicit_wait,
            default_implicit_wait=self.default_implicit_wait,
        )

    def set_implicit_wait(self, wait_time: int = None) -> None:
        """Set the implicit wait time for the driver. If no value is provided,
        the default implicit wait time from the configuration file will be
        used.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().set_implicit_wait(30)

        Args:
            wait_time: The implicit wait time in seconds.

        Returns:
            None
        """
        try:
            wait_time = wait_time or self.default_implicit_wait
            self.driver.implicitly_wait(wait_time)
        except Exception as e:
            self.logger.exception("Exception in set_implicit_wait method. Exception Details: %s", e)
            raise e
