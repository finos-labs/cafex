"""This module provides the ChromeDriver class for handling ChromeDriver
related operations.

The ChromeDriver class provides methods for setting up Chrome options
and creating a WebDriver instance.
"""
from selenium.webdriver import Chrome, Remote
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from cafex_core.logging.logger_ import CoreLogger
from cafex_ui.web_client.browserstack_integration import (
    BrowserStackDriverFactory,
)


class ChromeDriver:
    """A class used to handle ChromeDriver related operations.

    Attributes
    ----------
    chrome_options : list
        a list of Chrome options to be set
    chrome_preferences : dict
        a dictionary of Chrome preferences to be set
    chrome_version : str
        the version of Chrome to be used
    proxies : str
        the proxies to be used
    grid_execution : bool
        a flag indicating whether grid execution is enabled
    chrome_options : ChromeOptions
        the ChromeOptions object

    Methods
    -------
    setup_options():
        Sets up Chrome options.
    create_driver(selenium_grid_ip=None):
        Creates a WebDriver instance.
    """

    def __init__(
            self,
            chrome_options: list = None,
            chrome_preferences: dict = None,
            proxies: str = None,
            grid_execution: bool = False,
            chrome_version: str = None,
            run_on_browserstack: bool = False,
            browserstack_username: str = None,
            browserstack_access_key: str = None,
            browserstack_capabilities: list = None,
    ):
        """Constructs all the necessary attributes for the ChromeDriver object.

        Parameters
        ----------
        chrome_options : list, optional
            a list of Chrome options to be set (default is None)
        chrome_preferences: dict, optional
            a dictionary of Chrome preferences to be set (default is None)
        proxies : str, optional
            the proxies to be used (default is None)
        grid_execution : bool, optional
            a flag indicating whether grid execution is enabled (default is False)
        chrome_version : str, optional
            the version of Chrome to be used (default is None)
        run_on_browserstack : bool, optional
            a flag indicating whether to run on BrowserStack (default is False)
        browserstack_username : str, optional
            the username for BrowserStack (default is None)
        browserstack_access_key : str, optional
            the access key for BrowserStack (default is None)
        browserstack_capabilities: dict, optional
            the BrowserStack capabilities (default is None)

        Examples
        --------
        >>> chrome_driver = ChromeDriver(chrome_options=['--headless'], project_path='/path/to/project')
        >>> chrome_driver.chrome_options
        ['--headless']
        """
        self.chrome_options = chrome_options
        self.chrome_preferences = chrome_preferences
        self.chrome_version = chrome_version
        self.proxies = proxies
        self.grid_execution = grid_execution
        self.run_on_browserstack = run_on_browserstack
        self.browserstack_username = browserstack_username
        self.browserstack_access_key = browserstack_access_key
        self.browserstack_capabilities = browserstack_capabilities
        self.chrome_options_object = ChromeOptions()
        self.logger = CoreLogger(name=__name__).get_logger()
        self.web_driver = None

    def setup_options(self) -> None:
        """Sets up Chrome options.

        The method sets up Chrome options based on the attributes of the
        ChromeDriver object.

        Examples
        --------
        >>> chrome_driver = ChromeDriver(chrome_options=['--headless'])
        >>> chrome_driver.setup_options()
        >>> '--headless' in chrome_driver.chrome_options_object.arguments
        True
        """
        try:
            if self.proxies:
                self.chrome_options.proxy = self.proxies
            self.chrome_options_object.add_experimental_option(
                "excludeSwitches", ["enable-logging"]
            )
            if self.chrome_preferences:
                self.chrome_options_object.add_experimental_option("prefs", self.chrome_preferences)
            if self.chrome_options:
                for option in self.chrome_options:
                    self.chrome_options_object.add_argument(option)
        except Exception as e:
            self.logger.exception("Error setting up Chrome options: %s", e)
            raise e

    def get_window_size_from_options(self):
        """Parses the window size from the list_chrome_options attribute.

        Returns
        -------
        tuple
            A tuple containing the width and height as integers, or None if not specified.

        Examples
        --------
        >>> chrome_driver = ChromeDriver(chrome_options=['--window-size=800x600'])
        >>> chrome_driver.get_window_size_from_options()
        (800, 600)
        """
        try:
            if self.chrome_options:
                for option in self.chrome_options:
                    if "--window-size" in option:
                        size = option.split("=")[1]
                        width, height = map(int, size.split("x"))
                        return width, height
        except Exception as e:
            self.logger.exception("Error getting window size from Chrome options: %s", e)
            raise e

    def create_driver(self, selenium_grid_ip: str = None) -> Remote or Chrome or None:
        """Creates a WebDriver instance.

        The method creates a WebDriver instance based on the attributes of the
        ChromeDriver object and the provided parameters.

        Parameters
        ----------
        selenium_grid_ip : str, optional
            the IP of the Selenium grid (default is None)
        Returns
        -------
        web_driver : WebDriver
            the created WebDriver instance

        Examples
        --------
        >>> chrome_driver = ChromeDriver(chrome_options=['--headless'])
        >>> driver = chrome_driver.create_driver()
        >>> driver.name
        'chrome'
        """
        try:
            self.setup_options()
            if str(self.run_on_browserstack).lower() == "true":
                self.chrome_options_object.set_capability(
                    "bstack:options", self.browserstack_capabilities
                )
                self.web_driver = BrowserStackDriverFactory().create_browserstack_webdriver(
                    self.browserstack_username,
                    self.browserstack_access_key,
                    self.chrome_options_object,
                )
            else:
                if self.chrome_version is not None and not self.grid_execution:
                    self.chrome_options_object.browser_version = self.chrome_version
                self.web_driver = (
                    Remote(
                        command_executor=str(selenium_grid_ip), options=self.chrome_options_object
                    )
                    if self.grid_execution
                    else Chrome(options=self.chrome_options_object, service=ChromeService())
                )
            # sets the window size if specified based on the chrome_options attribute
            if self.chrome_options and any("window-size" in opt for opt in self.chrome_options):
                width, height = self.get_window_size_from_options()
                self.web_driver.set_window_position(0, 0)
                self.web_driver.set_window_size(width, height)
            # Defaults the window size to maximum if not specified
            else:
                self.web_driver.maximize_window()
            return self.web_driver
        except Exception as e:
            self.logger.exception("Error creating Chrome driver: %s", e)
            raise e
