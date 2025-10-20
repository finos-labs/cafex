from cafex_core.context import get_session_context
from cafex_ui.web_client.keyboard_mouse_actions import KeyboardMouseActions
from cafex_ui.web_client.web_client_actions.base_web_client_actions import (
    WebClientActions,
)
from selenium.webdriver.remote.webdriver import WebDriver

class WebDriverClass(WebClientActions, KeyboardMouseActions):
    def __init__(self):
        context = get_session_context()
        super().__init__(context=context)
        if "obj_wca" in context.globals or "obj_kma" in context.globals:
            self.web_client_actions: "WebClientActions" = context.globals["obj_wca"]
            self.get_driver: "WebDriver" = context.driver
            self.web_keyboard_mouse_actions: "KeyboardMouseActions" = context.globals["obj_kma"]

class PlaywrightClass:
    def __init__(self):
        from playwright.sync_api import Browser, BrowserContext, Page
        context = get_session_context()
        if context.playwright_page is not None:
            self.playwright_page: Page = context.playwright_page
            self.playwright_browser: Browser = context.playwright_browser
            self.playwright_context: BrowserContext = context.playwright_context


__all__ = ["WebDriverClass", "PlaywrightClass"]
