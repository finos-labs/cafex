from cafex_core.singletons_.session_ import SessionStore
from cafex_ui.web_client.keyboard_mouse_actions import KeyboardMouseActions
from cafex_ui.web_client.web_client_actions.base_web_client_actions import (
    WebClientActions,
)
from selenium.webdriver.remote.webdriver import WebDriver


class WebDriverClass(WebClientActions):
    def __init__(self):
        super().__init__()
        self.web_client_actions: "WebClientActions" = SessionStore().globals["obj_wca"]
        self.get_driver: "WebDriver" = SessionStore().driver


class Keyboard_Mouse_Class(KeyboardMouseActions):
    def __init__(self):
        super().__init__()
        self.web_keyboard_mouse_actions: "KeyboardMouseActions" = SessionStore().globals["obj_kma"]


__all__ = ["Keyboard_Mouse_Class", "WebDriverClass"]
