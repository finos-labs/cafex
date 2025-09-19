from appium.webdriver import webdriver
from cafex_core.singletons_.session_ import SessionStore
from cafex_ui.mobile_client.mobile_client_actions import MobileClientActions


class MobileClientActionsClass(MobileClientActions):
    def __init__(self):
        super().__init__()
        session_context = SessionStore().context
        self.mobile_client_actions: "MobileClientActions" = session_context.metadata.globals["obj_mca"]


class MobileDriverClass:
    def __init__(self):
        super().__init__()
        self.get_mobile_driver: "webdriver" = SessionStore().context.drivers.mobile_driver


__all__ = ["MobileClientActionsClass", "MobileDriverClass"]
