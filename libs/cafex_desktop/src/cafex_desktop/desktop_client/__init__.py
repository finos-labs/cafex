import platform

if platform.system().upper() == "WINDOWS":
    from pywinauto.application import Application

from cafex_core.singletons_.session_ import SessionStore
from cafex_desktop.desktop_client.desktop_client_actions.base_desktop_client_actions import (
    DesktopClientActions,
)


class DesktopClientActionsClass(DesktopClientActions):
    def __init__(self):
        super().__init__()
        self.desktop_client_actions: "DesktopClientActions" = SessionStore().globals["obj_dca"]
        self.handler: "Application" = SessionStore().handler


__all__ = ["DesktopClientActionsClass"]
