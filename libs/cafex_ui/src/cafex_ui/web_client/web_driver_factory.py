"""This module provides the BaseDriverFactory class for creating WebDriver
instances.

The BaseDriverFactory class provides methods for creating WebDriver
instances based on the specified browser and other parameters.
"""

import platform
import typing
from selenium.webdriver import DesiredCapabilities, Proxy
from selenium.webdriver.remote.webdriver import WebDriver
from cafex_ui.web_client.drivers.chrome_driver import ChromeDriver
from cafex_ui.web_client.drivers.edge_driver import EdgeDriver
from cafex_ui.web_client.drivers.firefox_driver import FirefoxDriverFactory
from cafex_ui.web_client.drivers.internet_explorer_driver import IEDriver
from cafex_ui.web_client.drivers.safari_driver import SafariDriver
from cafex_ui.web_client.web_client_enum import Browser


class WebDriverFactory:
    """A class used to create WebDriver instances.

    ...

    Attributes
    ----------
    platform : str
        the name of the platform

    Methods
    -------
    platform_name():
        Returns the name of the platform.
    selenium_desired_capabilities(browser):
        Returns the desired capabilities for the specified browser.
    create_driver(browser, use_grid=None, selenium_grid_ip=None, proxies=None, capabilities=None,
                  chrome_options=None, edge_options=None, firefox_options=None, safari_options=None,
                  custom_experimental_options=None, ie_edge_clear_browser_history=False, firefox_preferences=None,
                  grid_directory_path=None, chrome_version=None, project_path=None):
        Creates a WebDriver instance based on the specified parameters.
    """

    def __init__(self) -> None:
        """Constructs all the necessary attributes for the BaseDriverFactory
        object."""
        self.platform = self.platform_name

    @classmethod
    def platform_name(cls) -> str | None:
        """Returns the name of the platform.

        The method returns the name of the platform based on the platform attribute of the BaseDriverFactory
        object.

        Returns
        -------
            platform_name : str
                the name of the platform
        """
        platform_name = platform.system().lower()
        if "win" in platform_name:
            return "WINDOWS"
        if "darwin" in platform_name or "os" in platform_name:
            return "MAC"
        if "linux" in platform_name:
            return "LINUX"
        return None

    @staticmethod
    def selenium_desired_capabilities(browser: str) -> dict:
        """Returns the desired capabilities for the specified browser.

        The method returns the desired capabilities for the specified browser.

        Parameters
        ----------
            browser : str
                the name of the browser

        Returns
        -------
            browser_capabilities : dict
                the desired capabilities for the specified browser
        """
        capabilities = {
            Browser.CHROME.value: DesiredCapabilities.CHROME,
            Browser.FIREFOX.value: DesiredCapabilities.FIREFOX,
            Browser.INTERNETEXPLORER.value: DesiredCapabilities.INTERNETEXPLORER,
            Browser.HEADLESS_CHROME.value: DesiredCapabilities.CHROME,
            Browser.EDGE.value: DesiredCapabilities.EDGE,
        }
        return capabilities.get(browser, {})

    def create_driver(
            self,
            browser: str,
            use_grid: bool = None,
            selenium_grid_ip: str = None,
            proxies: str = None,
            capabilities: dict = None,
            browser_version: str = None,
            chrome_options: list = None,
            chrome_preferences: dict = None,
            firefox_options: list = None,
            firefox_preferences: dict = None,
            safari_options: list = None,
            ie_and_edge_clear_browser_history: bool = False,
            edge_options: list = None,
            ie_options: list = None,
            run_on_browserstack: bool = False,
            browserstack_username: str = None,
            browserstack_access_key: str = None,
            browserstack_capabilities: dict = None,
    ) -> typing.Union[WebDriver, None]:
        """Creates a WebDriver instance.

        The method creates a WebDriver instance based on the specified parameters.

        Parameters
        ----------
            browser : str
                the name of the browser
            use_grid : bool, optional
                a flag indicating whether to use grid execution (default is None)
            selenium_grid_ip : str, optional
                the IP of the Selenium grid (default is None)
            proxies : str, optional
                the proxies to be used (default is None)
            capabilities : dict, optional
                the capabilities to be used (default is None)
            chrome_options : list, optional
                a list of Chrome options to be set (default is None)
            chrome_preferences : dict, optional
                a dictionary of Chrome preferences to be set (default is None)
            firefox_options : list, optional
                a list of Firefox options to be set (default is None)
            firefox_preferences : dict, optional
                a dictionary of Firefox preferences to be set (default is None)
            edge_options : list, optional
                a list of Edge options to be set (default is None)
            safari_options : list, optional
                a list of Safari options to be set (default is None)
            ie_and_edge_clear_browser_history : bool, optional
                a flag indicating whether to clear browser history for IE Edge (default is False)
            browser_version : str, optional
                the version of browser to be used (default is None)
            ie_options : list, optional
                a list of IE options to be set (default is None)
            run_on_browserstack : bool, optional
                a flag indicating whether to run on BrowserStack (default is False)
            browserstack_username : str, optional
                the username for BrowserStack (default is None)
            browserstack_access_key : str, optional
                the access key for BrowserStack (default is None)
            browserstack_capabilities : dict, optional
                a dict of BrowserStack capabilities to be set (default is None)

        Returns
        -------
            driver_ : WebDriver
                the created WebDriver instance
        """
        default_capabilities = self.selenium_desired_capabilities(browser)
        if capabilities:
            default_capabilities.update(capabilities or {})
        proxies = Proxy(proxies).to_capabilities() if proxies else {}

        driver_map = {
            Browser.CHROME.value: ChromeDriver(
                chrome_options=chrome_options,
                chrome_preferences=chrome_preferences,
                chrome_version=browser_version,
                proxies=proxies,
                grid_execution=use_grid,
                run_on_browserstack=run_on_browserstack,
                browserstack_username=browserstack_username,
                browserstack_access_key=browserstack_access_key,
                browserstack_capabilities=browserstack_capabilities,
            ),
            Browser.FIREFOX.value: FirefoxDriverFactory(
                firefox_options=firefox_options,
                firefox_preferences=firefox_preferences,
                proxies=proxies,
                grid_execution=use_grid,
                run_on_browserstack=run_on_browserstack,
                browserstack_username=browserstack_username,
                browserstack_access_key=browserstack_access_key,
                browserstack_capabilities=browserstack_capabilities,
            ),
            Browser.EDGE.value: EdgeDriver(
                edge_options=edge_options,
                proxies=proxies,
                grid_execution=use_grid,
                ie_and_edge_clear_browser_history=ie_and_edge_clear_browser_history,
                run_on_browserstack=run_on_browserstack,
                browserstack_username=browserstack_username,
                browserstack_access_key=browserstack_access_key,
                browserstack_capabilities=browserstack_capabilities,
            ),
            Browser.SAFARI.value: SafariDriver(
                safari_options=safari_options,
                proxies=proxies,
                grid_execution=use_grid,
                run_on_browserstack=run_on_browserstack,
                browserstack_username=browserstack_username,
                browserstack_access_key=browserstack_access_key,
                browserstack_capabilities=browserstack_capabilities,
            ),
            Browser.INTERNETEXPLORER.value: IEDriver(
                ie_options=ie_options,
                proxies=proxies,
                grid_execution=use_grid,
                ie_and_edge_clear_browser_history=ie_and_edge_clear_browser_history,
                run_on_browserstack=run_on_browserstack,
                browserstack_username=browserstack_username,
                browserstack_access_key=browserstack_access_key,
                browserstack_capabilities=browserstack_capabilities,
            ),
        }

        driver_obj = driver_map.get(browser)
        if driver_obj:
            return driver_obj.create_driver(selenium_grid_ip=selenium_grid_ip)
        raise Exception(
            "browser value should be either chrome, firefox, edge, safari or internet explorer"
        )
