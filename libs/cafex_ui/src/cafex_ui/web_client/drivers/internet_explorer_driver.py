from selenium.webdriver import Ie, Remote
from selenium.webdriver.ie.options import Options as IeOptions
from selenium.webdriver.ie.service import Service as IeService
from cafex_core.logging.logger_ import CoreLogger
from cafex_ui.web_client.browserstack_integration import (
    BrowserStackDriverFactory,
)


class IEDriver:
    """
    A class used to represent an Internet Explorer Driver.

    ...

    Attributes
    ----------
    ie_options : list
        a list of options for the Internet Explorer browser
    proxies : str
        the proxies to be used
    grid_execution : bool
        a flag to indicate if grid execution is enabled
    ie_options_object : IeOptions
        the Internet Explorer options object
    window_size_options : dict
        a dictionary to store the width and height options
    logger : Logger
        the logger object
    run_on_browserstack : bool
        a flag to indicate if BrowserStack is being used
    browserstack_username : str
        the username for BrowserStack
    browserstack_access_key : str
        the access key for BrowserStack
    browserstack_capabilities : list
        a list of BrowserStack capabilities
    web_driver : WebDriver
        the WebDriver instance

    Methods
    -------
    setup_options():
        Sets up the Internet Explorer options based on the attributes of the IEDriver object.
    create_driver(selenium_grid_ip=None):
        Creates a WebDriver instance based on the attributes of the IEDriver object and the provided parameters.
    """

    def __init__(
            self,
            ie_options: list = None,
            proxies: str = None,
            grid_execution: bool = False,
            ie_and_edge_clear_browser_history: bool = False,
            run_on_browserstack: bool = False,
            browserstack_username: str = None,
            browserstack_access_key: str = None,
            browserstack_capabilities: list = None,
    ):
        """Initializes the IEDriver object with the given parameters.

        Parameters:
        ie_options (list): List of options for the Internet Explorer browser.
        proxies (str): Proxies to be used.
        grid_execution (bool): Flag indicating whether to use grid execution.
        ie_and_edge_clear_browser_history (bool): Flag indicating whether to clear browser history.
        run_on_browserstack (bool): Flag indicating whether to run on BrowserStack.
        browserstack_username (str): The username for BrowserStack.
        browserstack_access_key (str): The access key for BrowserStack.
        browserstack_capabilities (list): List of BrowserStack capabilities.
        """
        self.ie_options = ie_options if ie_options is not None else []
        self.proxies = proxies
        self.grid_execution = grid_execution
        self.ie_and_edge_clear_browser_history = ie_and_edge_clear_browser_history
        self.run_on_browserstack = run_on_browserstack
        self.browserstack_username = browserstack_username
        self.browserstack_access_key = browserstack_access_key
        self.ie_options_object = IeOptions()
        self.window_size_options = {}
        self.logger = CoreLogger(name=__name__).get_logger()
        self.browserstack_capabilities = browserstack_capabilities
        self.web_driver = None

    def setup_options(self):
        """Sets up Internet Explorer options based on the attributes of the
        IEDriver object."""
        try:
            if self.proxies:
                self.ie_options_object.proxy = self.proxies
            for ie_option in self.ie_options:
                if "width" in ie_option or "height" in ie_option:
                    dim_details = ie_option.split("=")
                    if dim_details:
                        self.window_size_options[dim_details[0].strip()] = dim_details[1].strip()
                else:
                    self.ie_options_object.add_argument(ie_option)
            if self.ie_and_edge_clear_browser_history:
                self.ie_options_object.ensure_clean_session = True
        except Exception as e:
            self.logger.error("Error occurred while setting up Internet Explorer options: %s", e)
            raise e

    def create_driver(self, selenium_grid_ip=None):
        """Creates a WebDriver instance based on the attributes of the IEDriver
        object and the provided parameters.

        Parameters:
        selenium_grid_ip (str): The IP of the Selenium grid.

        Returns:
        web_driver (WebDriver): The created WebDriver instance.
        """
        try:
            self.setup_options()
            if str(self.run_on_browserstack).lower() == "true":
                self.ie_options_object.set_capability(
                    "bstack:options", self.browserstack_capabilities
                )
                self.web_driver = BrowserStackDriverFactory().create_browserstack_webdriver(
                    self.browserstack_username, self.browserstack_access_key, self.ie_options_object
                )
            else:
                self.web_driver = (
                    Remote(command_executor=str(selenium_grid_ip), options=self.ie_options_object)
                    if self.grid_execution and selenium_grid_ip is not None
                    else Ie(service=IeService(), options=self.ie_options_object)
                )
            if self.window_size_options:
                if "width" in self.window_size_options and "height" in self.window_size_options:
                    self.web_driver.set_window_size(
                        self.window_size_options["width"], self.window_size_options["height"]
                    )
            else:
                self.web_driver.maximize_window()
            return self.web_driver
        except Exception as e:
            self.logger.error("Error occurred while creating Internet Explorer driver: %s", e)
            raise e
