import platform

if platform.system().upper() == "WINDOWS":
    from pywinauto.application import Application

from cafex_core.context import get_session_context
from cafex_desktop.desktop_client.desktop_client_actions.base_desktop_client_actions import (
    DesktopClientActions,
)


class DesktopClientActionsClass(DesktopClientActions):
    def __init__(self):
        context = get_session_context()
        super().__init__(context=context)
        self.desktop_client_actions: "DesktopClientActions" = context.globals["obj_dca"]
        self.handler: "Application" = context.handler


__all__ = ["DesktopClientActionsClass"]
