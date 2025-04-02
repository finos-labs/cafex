from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.remote.webdriver import WebDriver
from cafex_core.logging.logger_ import CoreLogger
from cafex_ui.web_client.browserstack_integration import (
    BrowserStackDriverFactory,
)


class FirefoxDriverFactory:

    def __init__(
            self,
            firefox_options: list = None,
            firefox_preferences: dict = None,
            proxies: str = None,
            grid_execution: bool = False,
            run_on_browserstack: bool = False,
            browserstack_username: str = None,
            browserstack_access_key: str = None,
            browserstack_capabilities: list = None,
    ):
        """Initializes the FirefoxDriverFactory with the given parameters.

        Parameters
        ----------
        firefox_options : list, optional
            A list of options for the Firefox browser (default is None).
        firefox_preferences : dict, optional
            A dictionary of Firefox preferences (default is None).
        proxies : str, optional
            The proxies to be used (default is None).
        grid_execution : bool, optional
            A flag indicating whether to use grid execution (default is False).
        run_on_browserstack : bool, optional
            A flag indicating whether to run on BrowserStack (default is False).
        browserstack_username : str, optional
            The username for BrowserStack (default is None).
        browserstack_access_key : str, optional
            The access key for BrowserStack (default is None).
        Examples
        --------
        >>> firefox_driver = FirefoxDriverFactory(project_path='/path/to/project')
        >>> firefox_driver.firefox_options
        '/path/to/project'
        """
        self.firefox_options = firefox_options
        self.firefox_preferences = firefox_preferences
        self.proxies = proxies
        self.grid_execution = grid_execution
        self.browserstack_capabilities = browserstack_capabilities
        self.run_on_browserstack = run_on_browserstack
        self.browserstack_username = browserstack_username
        self.browserstack_access_key = browserstack_access_key
        self.firefox_options_object = FirefoxOptions()
        self.logger = CoreLogger(name=__name__).get_logger()
        self.web_driver = None

    def setup_options(self):
        """Sets up Firefox options based on the provided parameters.

        Raises
        ------
        Exception
            If an error occurs while setting up Firefox options.

        Examples
        --------
        >>> firefox_driver = FirefoxDriverFactory()
        >>> firefox_driver.setup_options()
        """
        try:
            if self.proxies:
                self.firefox_options_object.proxy = self.proxies

            fp = FirefoxProfile()
            if self.firefox_preferences:
                for key, value in self.firefox_preferences.items():
                    fp.set_preference(key, value)
            if self.firefox_options:
                for option in self.firefox_options:
                    self.firefox_options_object.add_argument(option)
        except Exception as e:
            self.logger.error("Error occurred while setting up Firefox options: %s", e)

    def create_driver(self, selenium_grid_ip: str = None) -> WebDriver | None:
        """Creates a WebDriver instance based on the provided parameters.

        Parameters
        ----------
        selenium_grid_ip : str, optional
            The IP of the Selenium grid (default is None).

        Returns
        -------
        web_driver : WebDriver or None
            The created WebDriver instance, or None if an error occurs.

        Raises
        ------
        Exception
            If an error occurs while creating the Firefox driver.

        Examples
        --------
        >>> firefox_driver = FirefoxDriverFactory(list_firefox_options=['--headless'])
        >>> driver = firefox_driver.create_driver()
        >>> driver.name
        'firefox'
        """
        try:
            self.setup_options()
            if str(self.run_on_browserstack).lower() == "true":
                self.firefox_options_object.set_capability(
                    "bstack:options", self.browserstack_capabilities
                )
                self.web_driver = BrowserStackDriverFactory().create_browserstack_webdriver(
                    self.browserstack_username,
                    self.browserstack_access_key,
                    self.firefox_options_object,
                )
            else:
                if str(selenium_grid_ip) is not None and self.grid_execution is True:
                    self.web_driver = webdriver.Remote(
                        command_executor=str(selenium_grid_ip), options=self.firefox_options_object
                    )
                else:
                    firefox_service = FirefoxService()
                    self.web_driver = webdriver.Firefox(
                        options=self.firefox_options_object, service=firefox_service
                    )
            if self.firefox_options:
                if not any("width" in opt or "height" in opt for opt in self.firefox_options):
                    self.web_driver.maximize_window()
            else:
                self.web_driver.maximize_window()
            return self.web_driver
        except Exception as e:
            self.logger.error("Error occurred while creating Firefox driver: %s", e)
            raise e
