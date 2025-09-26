import os

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.singletons_.session_ import SessionStore
from cafex_core.utils.date_time_utils import DateTimeActions
from cafex_core.utils.regex_constants import (
    DATETIME_CHARS_PATTERN,
    INVALID_FILENAME_CHARS_PATTERN,
    MAX_SCREENSHOT_NAME_LENGTH,
    MULTIPLE_UNDERSCORE_PATTERN,
    SCREENSHOT_NAME_REPLACE_PATTERN,
    URL_SPECIAL_CHARS_PATTERN,
)


def _sanitize_name(name: str) -> str:
    """Sanitize name for use in screenshot filename.

    Args:
        name: Original name string

    Returns:
        Sanitized name string
    """
    # Replace spaces and special characters with underscore
    name = SCREENSHOT_NAME_REPLACE_PATTERN.sub("_", name)

    # Remove invalid filename characters
    name = INVALID_FILENAME_CHARS_PATTERN.sub("", name)

    # Replace URL special characters with underscore
    name = URL_SPECIAL_CHARS_PATTERN.sub("_", name)

    # Clean up multiple underscores and trailing underscore
    name = MULTIPLE_UNDERSCORE_PATTERN.sub("_", name).rstrip("_")

    # Truncate if too long
    return name[:MAX_SCREENSHOT_NAME_LENGTH]


def _format_timestamp(timestamp: str) -> str:
    """Format timestamp for screenshot filename.

    Args:
        timestamp: Raw timestamp string

    Returns:
        Formatted timestamp string
    """
    return DATETIME_CHARS_PATTERN.sub("", timestamp)


def capture_screenshot(name, error=False):
    logger = CoreLogger(name=__name__).get_logger()
    session_store = SessionStore()
    date_time_util = DateTimeActions()
    try:
        # Process name and timestamp
        name = _sanitize_name(name)
        timestamp = _format_timestamp(date_time_util.get_current_date_time())

        # Build screenshot name
        screenshot_name = f"{name}{'_error' if error else ''}_{timestamp}.png"

        # Get file path
        screenshots_dir = session_store.screenshots_dir
        file_path = os.path.join(screenshots_dir, screenshot_name)

        driver = session_store.driver or session_store.mobile_driver
        if driver:
            driver.save_screenshot(file_path)
            return file_path
        playwright_driver= session_store.playwright_page
        if playwright_driver:
            playwright_driver.screenshot(path=file_path, full_page=True)
            return file_path
    except Exception as e:
        logger.error(f"Error while taking screenshot: {str(e)}")
    return None


def add_screenshot_to_report(step_data, screenshot_path):
    if screenshot_path:
        # Initialize evidence structure if needed
        step_data.setdefault("evidence", {}).setdefault("screenshots", {})

        screenshot_name = os.path.basename(screenshot_path)
        step_data["screenshot"] = screenshot_path
        step_data["evidence"]["screenshots"][screenshot_name] = screenshot_path
