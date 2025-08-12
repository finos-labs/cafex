from selenium.webdriver import Edge, Remote
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from cafex_core.logging.logger_ import CoreLogger
from cafex_ui.web_client.browserstack_integration import (
    BrowserStackDriverFactory,
)


class EdgeDriver:
    """A class used to represent an Edge Driver.

    Attributes
    ----------
    edge_options : list
        a list of options for the Edge browser
    proxies : str
        the proxies to be used
    grid_execution : bool
        a flag indicating whether to use grid execution
    edge_options_object : EdgeOptions
        the Edge options object
    ie_and_edge_clear_browser_history : bool
        a flag indicating whether to clear browser history
    run_on_browserstack : bool
        a flag indicating whether to run on BrowserStack
    browserstack_username : str
        the username for BrowserStack
    browserstack_access_key : str
        the access key for BrowserStack

    Methods
    -------
    setup_options():
        Sets up Edge options based on the provided parameters.
    create_driver(pstr_selenium_grid_ip):
        Creates a WebDriver instance based on the provided parameters.
    """

    def __init__(
            self,
            edge_options: list = None,
            proxies: str = None,
            grid_execution: bool = False,
            ie_and_edge_clear_browser_history: bool = False,
            run_on_browserstack: bool = False,
            browserstack_username: str = None,
            browserstack_access_key: str = None,
            browserstack_capabilities: list = None,
    ):
        """Initializes the EdgeDriver with the given parameters.

        Parameters:
        edge_options (list): A list of options for the Edge browser.
        proxies (str): The proxies to be used.
        grid_execution (bool): A flag indicating whether to use grid execution.
        ie_and_edge_clear_browser_hist (bool): A flag indicating whether to clear browser history.
        browserstack_capabilities (list): The capabilities to be used.
        run_on_browserstack (bool): A flag indicating whether to run on BrowserStack.
        browserstack_username (str): The username for BrowserStack.
        browserstack_access_key (str): The access key for BrowserStack.
        """
        self.edge_options = edge_options
        self.proxies = proxies
        self.grid_execution = grid_execution
        self.edge_options_object = EdgeOptions()
        self.ie_and_edge_clear_browser_history = ie_and_edge_clear_browser_history
        self.browserstack_username = browserstack_username
        self.browserstack_access_key = browserstack_access_key
        self.run_on_browserstack = run_on_browserstack
        self.browserstack_capabilities = browserstack_capabilities
        self.logger = CoreLogger(name=__name__).get_logger()
        self.web_driver = None

    def setup_options(self) -> None:
        """Sets up Edge options based on the provided parameters."""
        try:
            # Set proxy if provided
            if self.proxies:
                self.edge_options_object.proxy = self.proxies

            # Clear browser history if flag is set
            if self.ie_and_edge_clear_browser_history:
                self.edge_options_object.ensure_clean_session = True

            # Use Chromium
            self.edge_options_object.use_chromium = True

            # Add options to Edge options
            if self.edge_options is not None:
                for opt in self.edge_options:
                    self.edge_options_object.add_argument(opt)
        except Exception as e:
            self.logger.error("Error occurred while setting up Edge options: %s", e)
            raise e

    def create_driver(self, selenium_grid_ip: str = None) -> object:
        """Creates a WebDriver instance based on the provided parameters.

        Parameters:
        selenium_grid_ip (str): The IP of the Selenium grid.

        Returns:
        web_driver (WebDriver): The created WebDriver instance.
        """
        try:
            # Set up options
            self.setup_options()
            # Create a WebDriver instance
            if str(self.run_on_browserstack).lower() == "true":
                self.edge_options_object.set_capability(
                    "bstack:options", self.browserstack_capabilities
                )
                self.web_driver = BrowserStackDriverFactory().create_browserstack_webdriver(
                    self.browserstack_username,
                    self.browserstack_access_key,
                    self.edge_options_object,
                )
            else:
                self.web_driver = (
                    Remote(command_executor=str(selenium_grid_ip), options=self.edge_options_object)
                    if (self.grid_execution and str(selenium_grid_ip) is not None)
                    else Edge(options=self.edge_options_object, service=EdgeService())
                )
            # Maximize window if no width or height options are provided
            if not self.edge_options or not any("window-size" in opt for opt in self.edge_options):
                self.web_driver.maximize_window()

            return self.web_driver
        except Exception as e:
            self.logger.error("Error creating Edge driver: %s", e)
            raise e
