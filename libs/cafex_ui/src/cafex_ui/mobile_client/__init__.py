from appium.webdriver import webdriver

from cafex_core.context import get_session_context
from cafex_ui.mobile_client.mobile_client_actions import MobileClientActions


class MobileClientActionsClass(MobileClientActions):
    def __init__(self):
        context = get_session_context()
        super().__init__(context=context)
        self.mobile_client_actions: "MobileClientActions" = context.globals["obj_mca"]


class MobileDriverClass:
    def __init__(self):
        super().__init__()
        self.get_mobile_driver: "webdriver" = get_session_context().mobile_driver


__all__ = ["MobileClientActionsClass", "MobileDriverClass"]
