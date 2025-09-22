from cafex_core.singletons_.session_ import SessionStore
from cafex_ui.web_client.keyboard_mouse_actions import KeyboardMouseActions
from cafex_ui.web_client.web_client_actions.base_web_client_actions import (
    WebClientActions,
)
from selenium.webdriver.remote.webdriver import WebDriver

class WebDriverClass(WebClientActions,KeyboardMouseActions):
    def __init__(self):
        super().__init__()
        if "obj_wca" in SessionStore().globals or "obj_kma" in SessionStore().globals:
            self.web_client_actions: "WebClientActions" = SessionStore().globals["obj_wca"]
            self.get_driver: "WebDriver" = SessionStore().driver
            self.web_keyboard_mouse_actions: "KeyboardMouseActions" = SessionStore().globals["obj_kma"]

class PlaywrightClass:
    def __init__(self):
        from playwright.sync_api import Browser, BrowserContext, Page
        if SessionStore().playwright_page is not None:
            self.playwright_page: Page = SessionStore().playwright_page
            self.playwright_browser: Browser = SessionStore().playwright_browser
            self.playwright_context: BrowserContext = SessionStore().playwright_context


__all__ = ["WebDriverClass","PlaywrightClass"]
