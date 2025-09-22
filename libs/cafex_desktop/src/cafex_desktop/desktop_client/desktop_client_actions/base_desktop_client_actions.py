import platform

if platform.system().upper() == "WINDOWS":
    from pywinauto.application import Application

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

    def __init__(self, handler: Application = None):
        """Initialize the DesktopClientActions class."""
        super().__init__(handler)
        self.window_actions = WindowActions(handler)
        self.element_interactions = DesktopElementInteractions(handler)
        self.advanced_element_interactions = AdvancedElementInteractions(handler)
