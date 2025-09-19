import os

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.singletons_.session_ import SessionStore
from cafex_ui.cafex_ui_config_utils import WebConfigUtils
from cafex_ui.web_client.browserstack_integration import (
    BrowserStackDriverFactory,
)
from cafex_ui.web_client.keyboard_mouse_actions import KeyboardMouseActions
from cafex_ui.web_client.web_client_actions.base_web_client_actions import (
    WebClientActions,
)
from cafex_ui.web_client.web_driver_factory import WebDriverFactory


class WebDriverInitializer:
    """A class that initializes the web driver."""

    def __init__(self) -> None:
        self.session_store = SessionStore()
        self.config_utils = WebConfigUtils()
        self.logger = CoreLogger(name=__name__).get_logger()
        self.bs_obj = None

    def initialize_driver(self) -> None:
        """Initialize the driver."""
        try:
            web_capabilities = self._get_web_capabilities()
            bs_capabilities, current_browser = self._get_browserstack_capabilities(web_capabilities)
            driver_obj = self._create_web_driver(web_capabilities, bs_capabilities, current_browser)
            self._store_driver_in_session(driver_obj)
        except Exception as error_before_scenario_browser_setup:
            self.logger.error(
                "Error occurred in before_scenario_browser_setup: %s",
                str(error_before_scenario_browser_setup),
            )
            raise error_before_scenario_browser_setup

    def _get_web_capabilities(self) -> dict:
        web_capabilities = self.config_utils.fetch_web_browser_capabilities()
        if web_capabilities and web_capabilities.get("use_caps", False):
            self.logger.debug("Desired Capabilities: %s", web_capabilities)
        else:
            web_capabilities = {}
        return web_capabilities

    def _get_browserstack_capabilities(self, web_capabilities: dict) -> tuple:
        run_on_browserstack = self.config_utils.base_config.get("run_on_browserstack", False)
        if str(run_on_browserstack).lower() == "true":
            self.bs_obj = BrowserStackDriverFactory()
            bs_capabilities, current_browser = self._configure_browserstack()
        else:
            bs_capabilities = []
            current_browser = self.config_utils.base_config.get(
                "current_execution_browser", "chrome"
            )
        return bs_capabilities, current_browser

    def _configure_browserstack(self) -> tuple:
        browserstack_username = os.getenv("BROWSERSTACK_USERNAME")
        browserstack_access_key = os.getenv("BROWSERSTACK_ACCESS_KEY")
        if not browserstack_username or not browserstack_access_key:
            self.logger.error("BROWSERSTACK_USERNAME or BROWSERSTACK_ACCESS_KEY not found.")
            raise Exception("Browserstack credentials not found in environment variables.")
        browserstack_config_file = self.config_utils.base_config.get(
            "browserstack_config_file", "browserstack.yml"
        )
        bs_config = self.config_utils.read_browserstack_web_yml_file(browserstack_config_file)
        if (
                "use_random_browsers" in bs_config.keys()
                and str(bs_config["use_random_browsers"]).lower() == "true"
        ):
            random_browser = self._get_random_browser(
                bs_config, browserstack_username, browserstack_access_key
            )
            bs_browser_capabilities = random_browser["bstack:options"]
            current_browser = random_browser["browserName"].lower()
        else:
            current_browser = self.config_utils.base_config.get(
                "current_execution_browser", "chrome"
            )
            bs_browser_capabilities = bs_config["browser"].get(current_browser, {})
        if current_browser == "ie":
            current_browser = "internet explorer"
        bs_capabilities = {**bs_browser_capabilities, **bs_config["bstack:options"]}
        return bs_capabilities, current_browser

    def _get_random_browser(
            self, bs_config: dict, browserstack_username: str, browserstack_access_key: str
    ) -> dict:
        if (
                "browserstack_browsers_file" in bs_config.keys()
                and bs_config["browserstack_browsers_file"] is not None
        ):
            return self.bs_obj.get_available_browsers(
                bs_config["browserstack_browsers_file"],
                browserstack_username,
                browserstack_access_key,
            )
        return self.bs_obj.get_available_browsers(
            "browsers.json", browserstack_username, browserstack_access_key
        )

    def _create_web_driver(
            self, web_capabilities: dict, bs_capabilities: dict, current_browser: str
    ):
        chrome_options = self.config_utils.base_config.get("chrome_options", [])
        chrome_preferences = self.config_utils.base_config.get("chrome_preferences", {})
        firefox_options = self.config_utils.base_config.get("firefox_options", [])
        firefox_preferences = self.config_utils.base_config.get("firefox_preferences", {})
        edge_options = self.config_utils.base_config.get("edge_options", [])
        safari_options = self.config_utils.base_config.get("safari_options", [])
        use_proxy = self.config_utils.base_config.get("use_proxy", False)
        ie_and_edge_clear_browser_history = self.config_utils.base_config.get(
            "ie_and_edge_clear_browser_history", False
        )
        browser_version = self.config_utils.base_config.get("browser_version", None)
        proxy_options = self._get_proxy_options(use_proxy)
        selenium_grid_ip = self.config_utils.fetch_selenium_grid_ip()
        use_grid = self.config_utils.fetch_use_grid()
        browserstack_username = os.getenv("BROWSERSTACK_USERNAME")
        browserstack_access_key = os.getenv("BROWSERSTACK_ACCESS_KEY")
        web_driver_factory = WebDriverFactory()
        return web_driver_factory.create_driver(
            current_browser,
            use_grid=use_grid,
            selenium_grid_ip=selenium_grid_ip,
            proxies=proxy_options,
            capabilities=web_capabilities,
            browser_version=browser_version,
            chrome_options=chrome_options,
            chrome_preferences=chrome_preferences,
            edge_options=edge_options,
            firefox_options=firefox_options,
            firefox_preferences=firefox_preferences,
            safari_options=safari_options,
            ie_and_edge_clear_browser_history=ie_and_edge_clear_browser_history,
            browserstack_capabilities=bs_capabilities,
            run_on_browserstack=str(
                self.config_utils.base_config.get("run_on_browserstack", False)
            ).lower()
                                == "true",
            browserstack_username=browserstack_username,
            browserstack_access_key=browserstack_access_key,
        )

    def _get_proxy_options(self, use_proxy: bool) -> str:
        if use_proxy and "proxy_options" in self.session_store.base_config.keys():
            return self.session_store.base_config["proxy_options"]
        return ""

    def _store_driver_in_session(self, driver_obj) -> None:
        self.session_store.driver = driver_obj
        self.session_store.globals["obj_wdf"] = WebDriverFactory()
        self.session_store.globals["obj_wca"] = WebClientActions(self.session_store.driver)
        self.session_store.globals["obj_kma"] = KeyboardMouseActions(self.session_store.driver)

    def initialize_playwright_driver(self) -> None:
        from playwright.sync_api import sync_playwright
        self.logger.info("playwright_web configuration")
        try:
            browser_args = self.config_utils.base_config.get("playwright_browser_args", {})
            if self.session_store.playwright_browser is None:
                playwright = sync_playwright().start()
                browser_type = self.config_utils.fetch_current_browser()
                if 'headless' not in browser_args or browser_args.get('headless') is None:
                    browser_args['headless'] = False
                if os.environ.get("isCTBuild") == "1":
                    browser_args['headless'] = True
                if browser_type in ["chromium","edge","chrome"]:
                    browser = playwright.chromium.launch(**browser_args)
                elif browser_type == "firefox":
                    browser = playwright.firefox.launch(**browser_args)
                elif browser_type in ["webkit","safari"]:
                    browser = playwright.webkit.launch(**browser_args)
                else:
                    raise ValueError(f"Unsupported browser type: {browser_type}")

                context = browser.new_context()
                page = context.new_page()
                self.session_store.playwright_browser = browser
                self.session_store.playwright_context = context
                self.session_store.playwright_page = page
                self.logger.info("Playwright driver created successfully")
        except Exception as e:
            self.logger.exception(f"Error in playwright_web configuration: {str(e)}")
            raise e

