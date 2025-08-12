from enum import Enum


class Browser(Enum):
    """Enum class for supported browsers."""

    CHROME = "chrome"
    HEADLESS_CHROME = "headless"
    FIREFOX = "firefox"
    INTERNETEXPLORER = "internet explorer"
    EDGE = "edge"
    SAFARI = "safari"
