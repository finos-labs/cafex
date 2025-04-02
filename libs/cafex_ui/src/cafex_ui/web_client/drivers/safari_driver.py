from selenium import webdriver
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.safari.service import Service as SafariService
from cafex_core.logging.logger_ import CoreLogger
from cafex_ui.web_client.browserstack_integration import (
    BrowserStackDriverFactory,
)


class SafariDriver:
    """This class is responsible for setting up the Safari WebDriver.

    It allows for the configuration of various options such as proxies,
    grid execution, and browser version. It only supports Safari browser
    and macOS operating system.
    """

    def __init__(
            self,
            safari_options: list = None,
            proxies: str = None,
            grid_execution: bool = False,
            run_on_browserstack: bool = False,
            browserstack_username: str = None,
            browserstack_access_key: str = None,
            browserstack_capabilities: list = None,
    ):
        """Initializes the SafariDriver with the given parameters.

        Parameters:
        list_safari_options (list): A list of options for the Safari browser.
        proxies (dict): A dictionary of proxies to be used.
        grid_execution (bool): A flag indicating whether to use grid execution.
        run_on_browserstack (bool): A flag indicating whether to run on BrowserStack.
        browserstack_username (str): The username for BrowserStack.
        browserstack_access_key (str): The access key for BrowserStack.
        browserstack_capabilities (list): A list of BrowserStack capabilities.
        """
        self.list_safari_options = safari_options if safari_options is not None else []
        self.proxies = proxies
        self.grid_execution = grid_execution
        self.run_on_browserstack = run_on_browserstack
        self.browserstack_username = browserstack_username
        self.browserstack_access_key = browserstack_access_key
        self.browserstack_capabilities = browserstack_capabilities
        self.logger = CoreLogger(name=__name__).get_logger()
        self.safari_options = SafariOptions()
        self.safari_window_size_options = {}
        self.web_driver = None

    def setup_options(self):
        """Sets up the options for the Safari browser."""
        try:
            safari_options = SafariOptions()
            if self.proxies:
                safari_options.proxy = self.proxies
            if self.list_safari_options is not None:
                for safari_opt in self.list_safari_options:
                    if "width" in safari_opt or "height" in safari_opt:
                        dim_details = safari_opt.split("=")
                        if dim_details:
                            self.safari_window_size_options[dim_details[0].strip()] = dim_details[
                                1
                            ].strip()
                    else:
                        safari_options.add_argument(safari_opt)
        except Exception as e:
            self.logger.error("Error occurred while setting up Safari options: %s", e)
            raise e

    def create_driver(self, selenium_grid_ip=None):
        """Creates and returns a WebDriver instance for Safari.

        Parameters:
        pstr_selenium_grid_ip (str): The IP of the Selenium grid.

        Returns:
        WebDriver: The created WebDriver instance.
        """
        try:
            self.setup_options()
            if str(self.run_on_browserstack).lower() == "true":
                self.safari_options.set_capability("bstack:options", self.browserstack_capabilities)
                self.web_driver = BrowserStackDriverFactory().create_browserstack_webdriver(
                    self.browserstack_username, self.browserstack_access_key, self.safari_options
                )
            else:
                if self.grid_execution and selenium_grid_ip is not None:
                    self.web_driver = webdriver.Remote(
                        command_executor=str(selenium_grid_ip), options=self.safari_options
                    )
                else:
                    safari_service = SafariService()
                    self.web_driver = webdriver.Safari(
                        service=safari_service, options=self.safari_options
                    )

            if (
                    "width" in self.safari_window_size_options
                    and "height" in self.safari_window_size_options
            ):
                self.web_driver.set_window_size(
                    self.safari_window_size_options["width"],
                    self.safari_window_size_options["height"],
                )
            else:
                self.web_driver.maximize_window()
            return self.web_driver
        except Exception as e:
            self.logger.error("Error occurred while creating Safari WebDriver: %s", e)
            raise e
