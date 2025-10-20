import platform

if platform.system().upper() == "WINDOWS":
    from pywinauto.application import Application

from cafex_core.context import SessionContext, get_session_context
from cafex_desktop.desktop_client.desktop_client_actions.advanced_element_interactions import (
    AdvancedElementInteractions,
)
from cafex_desktop.desktop_client.desktop_client_actions.desktop_element_interactions import (
    DesktopElementInteractions,
)
from cafex_desktop.desktop_client.desktop_client_actions.window_actions import (
    WindowActions,
)


class DesktopClientActions(WindowActions, DesktopElementInteractions, AdvancedElementInteractions):
    """A class used to represent DesktopClientActions."""

    def __init__(
            self,
            handler: Application = None,
            context: SessionContext | None = None,
    ):
        """Initialize the DesktopClientActions class."""
        self.session_context: SessionContext = context or get_session_context()
        super().__init__(handler, context=self.session_context)
        self.window_actions = WindowActions(handler, context=self.session_context)
        self.element_interactions = DesktopElementInteractions(handler, context=self.session_context)
        self.advanced_element_interactions = AdvancedElementInteractions(
            handler,
            context=self.session_context,
        )
