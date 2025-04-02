from typing import Tuple, Union

from appium import webdriver
from appium.webdriver import WebElement
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from cafex_core.logging.logger_ import CoreLogger
from cafex_core.singletons_.session_ import SessionStore
from cafex_core.utils.config_utils import ConfigUtils
from cafex_core.utils.exceptions import CoreExceptions


class MobileClientActions:
    """Provides actions for interacting with mobile elements."""

    def __init__(self, mobile_driver: webdriver.Remote = None, default_explicit_wait: int = None):
        """Initializes MobileClientActions with a driver and optional explicit
        wait.

        Args:
            mobile_driver: The Appium webdriver instance.
                            if not provided, it will be picked from Session Store
            default_explicit_wait: The default explicit wait time (in seconds).
                                   If not provided, it will be retrieved from ConfigUtils.
        """
        self.mobile_driver = mobile_driver or SessionStore().mobile_driver
        self.default_explicit_wait = default_explicit_wait or ConfigUtils().get_explicit_wait()
        self.logger = CoreLogger(name=__name__).get_logger()
        self.__exceptions_generic = CoreExceptions()

        self.mobile_locator_strategies = {
            "XPATH": AppiumBy.XPATH,
            "ID": AppiumBy.ID,
            "NAME": AppiumBy.NAME,
            "CLASS_NAME": AppiumBy.CLASS_NAME,
            "ACCESSIBILITY_ID": AppiumBy.ACCESSIBILITY_ID,
            "ANDROID_UIAUTOMATOR": AppiumBy.ANDROID_UIAUTOMATOR,
            "IOS_PREDICATE": AppiumBy.IOS_PREDICATE,
            "CLASS_CHAIN": AppiumBy.IOS_CLASS_CHAIN,
        }

    def get_driver_context(self) -> str:
        """Returns the current driver context (e.g., WEBVIEW, NATIVE)."""
        try:
            return self.mobile_driver.current_context
        except Exception as e:
            error_description = f"Error getting driver context: {str(e)}"
            self.__exceptions_generic.raise_generic_exception(
                message=error_description, fail_test=False
            )
            return ""

    def switch_driver_context(self, context: str) -> bool:
        """Switches the driver context to 'WEBVIEW' or 'NATIVE'.

        Args:
            context: The desired context ('WEBVIEW' or 'NATIVE').

        Returns:
            True if the context switch was successful, False otherwise.
        """
        try:
            context = context.lower()
            if context == "webview":
                self.mobile_driver.switch_to.context(self.mobile_driver.contexts[1])
                return True
            if context == "native":
                self.mobile_driver.switch_to.context(self.mobile_driver.contexts[0])
                return True
            return False  # If context is not webview or native
        except Exception as e:
            error_description = f"Error switching driver context to '{context}': {str(e)}"
            self.__exceptions_generic.raise_generic_exception(
                message=error_description, fail_test=False
            )
            return False

    def open_deep_link(self, link: str) -> None:
        """Opens a deep link in the mobile app.

        Args:
            link: The deep link URL.
        """
        try:
            self.mobile_driver.get(link)
        except Exception as e:
            self.logger.exception("Error opening deep link '%s': %s", link, e)
            raise e

    def get_page_url(self) -> str:
        """Returns the current URL of the webview context."""
        try:
            return self.mobile_driver.current_url
        except Exception as e:
            self.logger.exception("Error getting page URL: %s", e)
            raise e

    def terminate_mobile_app(self, package: str) -> None:
        """Terminates the mobile app specified by the package name or bundle
        ID.

        Args:
            package:  The Android package name or iOS bundle ID of the app.

        Raises:
            Exception: If an error occurs during app termination.
        """
        try:
            self.mobile_driver.terminate_app(package)
        except Exception as e:
            self.logger.exception("Error terminating mobile app '%s': %s", package, e)
            raise e

    def activate_mobile_app(self, package: str) -> None:
        """Activates the mobile app specified by the package name or bundle ID.

        Args:
            package: The Android package name or iOS bundle ID of the app.

        Raises:
            Exception: If an error occurs during app activation.
        """
        try:
            self.mobile_driver.activate_app(package)
            self.mobile_driver.orientation = "PORTRAIT"
            # Switch to native context if not already there
            if self.get_driver_context() != self.mobile_driver.contexts[0]:
                self.switch_driver_context("NATIVE")
        except Exception as e:
            self.logger.exception("Error activating mobile app '%s': %s", package, e)
            raise e

    def _get_mobile_locator_strategy(self, locator_strategy: str) -> str:
        """Returns the AppiumBy locator strategy based on the input string.

        Args:
            locator_strategy: The locator strategy as a string
                             (e.g., 'XPATH', 'ID', 'ACCESSIBILITY_ID').

        Returns:
            The corresponding AppiumBy locator strategy.

        Raises:
            ValueError: If the locator strategy is not supported.
        """
        try:
            strategy = locator_strategy.strip().replace(" ", "_").upper()
            if strategy in self.mobile_locator_strategies:
                return self.mobile_locator_strategies[strategy]

            raise ValueError(
                f"Unsupported locator strategy: {locator_strategy}. "
                f"Supported strategies are: {', '.join(self.mobile_locator_strategies.keys())}"
            )
        except Exception as e:
            self.logger.exception("Error in get_mobile_locator_strategy: %s", e)
            raise e

    def _parse_locator(self, locator_string: str) -> Tuple[str, str]:
        """Parses a locator string in the format "strategy=value" and returns
        the corresponding AppiumBy strategy and locator value.

        Args:
            locator_string: The locator string.

        Returns:
            A tuple containing the AppiumBy strategy and the locator value.

        Raises:
            ValueError: If the locator string is invalid.
        """
        try:
            strategy, value = locator_string.split("=", 1)
            strategy = self._get_mobile_locator_strategy(strategy)
            return strategy, value.strip()
        except ValueError as e:
            raise ValueError(
                f"Invalid locator string: {locator_string}. "
                f"It must be in the format 'strategy=value'."
            ) from e

    def is_element_displayed(
            self, locator: Union[str, WebElement], explicit_wait: int = None
    ) -> bool:
        """Verifies if an element is displayed on the screen.

        Args:
            locator: Locator string in the format "strategy=value"
                     (e.g., "id=my_element" or "xpath=//button[@name='submit']")
                     or a WebElement object.
            explicit_wait:  Optional explicit wait time (in seconds).
                           Defaults to the configured default explicit wait.

        Returns:
            True if the element is displayed, False otherwise.

        Raises:
            ValueError: If an invalid locator string is provided.
            TypeError: If an invalid locator type is provided.
            Exception: If any other error occurs while checking element visibility.
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait

            if isinstance(locator, str):
                strategy, value = self._parse_locator(locator)

                element = WebDriverWait(self.mobile_driver, explicit_wait).until(
                    EC.visibility_of_element_located((strategy, value))
                )
                return bool(element)
            if isinstance(locator, WebElement):
                return locator.is_displayed()

            raise TypeError("Invalid locator type. Must be a string or a WebElement.")

        except Exception as e:
            error_description = f"Error checking visibility of element: '{locator}': {str(e)}"
            self.__exceptions_generic.raise_generic_exception(
                message=error_description, trim_log=True, fail_test=False
            )
            return False

    def get_clickable_mobile_element(
            self, locator: Union[str, WebElement], explicit_wait: int = None
    ) -> WebElement:
        """Waits for an element to be clickable and returns it.

        Args:
            locator: Locator string in the format "strategy=value" or a WebElement object.
            explicit_wait: Optional explicit wait time (seconds).

        Returns:
            The clickable WebElement.

        Raises:
            ValueError: If an invalid locator string is provided.
            TypeError: If an invalid locator type is provided.
            TimeoutException: If the element is not clickable within the explicit wait time.
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait

            if isinstance(locator, str):
                strategy, value = self._parse_locator(locator)
                return WebDriverWait(self.mobile_driver, explicit_wait).until(
                    EC.element_to_be_clickable((strategy, value))
                )
            if isinstance(locator, WebElement):
                return locator

            raise TypeError("Invalid locator type. Must be a string or a WebElement.")
        except Exception as e:
            self.logger.exception("Error getting clickable element: %s. Error: %s", locator, e)
            raise e

    def click(self, locator: str, explicit_wait: int = None) -> None:
        """Clicks on a mobile element.

        Args:
            locator: Locator string in the format "strategy=value".
            explicit_wait: Optional explicit wait time (seconds).

        Raises:
            ValueError: If an invalid locator string is provided.
            Exception: If an error occurs while clicking the element.
        """
        try:
            element = self.get_clickable_mobile_element(locator, explicit_wait)
            element.click()
        except Exception as e:
            self.logger.exception("Error clicking element: %s. Error: %s", locator, e)
            raise e

    def type(
            self,
            locator: str,
            text: str,
            explicit_wait: int = None,
            clear: bool = False,
            click_before_type: bool = True,
    ) -> None:
        """Types text into a mobile element.

        Args:
            locator: Locator string in the format "strategy=value".
            text: The text to type.
            explicit_wait: Optional explicit wait time (seconds).
            clear: If True, clears the element before typing.
            click_before_type: If True, clicks the element before typing.

        Raises:
            ValueError: If an invalid locator string is provided.
            Exception: If an error occurs while typing.
        """
        try:
            element = self.get_clickable_mobile_element(locator, explicit_wait)
            if click_before_type:
                element.click()
            if clear:
                element.clear()
            element.send_keys(text)
        except Exception as e:
            self.logger.exception(
                "Error typing text '%s' into element: %s. Error: %s", text, locator, e
            )
            raise e

    def is_element_present(
            self, locator: Union[str, WebElement], explicit_wait: int = None
    ) -> bool:
        """Checks if an element is present in the DOM.

        Args:
            locator: Locator string in the format "strategy=value" or a WebElement object.
            explicit_wait: Optional explicit wait time (seconds).

        Returns:
            True if the element is present, False otherwise.

        Raises:
            ValueError: If an invalid locator string is provided.
            TypeError: If an invalid locator type is provided.
            Exception: If an error occurs while checking element presence.
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait

            if isinstance(locator, str):
                strategy, value = self._parse_locator(locator)
                element = WebDriverWait(self.mobile_driver, explicit_wait).until(
                    EC.presence_of_element_located((strategy, value))
                )
                return bool(element)
            if isinstance(locator, WebElement):
                return True  # A WebElement object is always considered present

            raise TypeError("Invalid locator type. Must be a string or a WebElement.")
        except Exception as e:
            self.logger.exception("Error checking presence of element: %s. Error: %s", locator, e)
            raise e

    def get_web_element(
            self, locator: Union[str, WebElement], explicit_wait: int = None
    ) -> WebElement:
        """Locates and returns a mobile element.

        Args:
            locator: Locator string in the format "strategy=value" or a WebElement object.
            explicit_wait: Optional explicit wait time (seconds).

        Returns:
            The located WebElement.

        Raises:
            ValueError: If an invalid locator string is provided.
            TypeError: If an invalid locator type is provided.
            TimeoutException: If the element is not found within the explicit wait time.
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait

            if isinstance(locator, str):
                strategy, value = self._parse_locator(locator)
                return WebDriverWait(self.mobile_driver, explicit_wait).until(
                    EC.presence_of_element_located((strategy, value))
                )
            if isinstance(locator, WebElement):
                return locator

            raise TypeError("Invalid locator type. Must be a string or a WebElement.")
        except Exception as e:
            self.logger.exception("Error locating element: %s. Error: %s", locator, e)
            raise e

    def scroll_mobile(
            self, direction: str, find_locator: str, explicit_wait: int = None, max_swipes: int = 10
    ) -> bool:
        """Scrolls horizontally or vertically to find an element.

        Args:
            direction: Scroll direction ('down', 'up', 'right', 'left').
            find_locator: Locator string of the element to find.
            explicit_wait: Optional explicit wait time (seconds).
            max_swipes: Maximum number of swipes to attempt.

        Returns:
            True if the element is found, False otherwise.

        Raises:
            Exception: If an error occurs during scrolling.
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait

            if self.is_element_displayed(find_locator, explicit_wait):
                return True

            size = self.mobile_driver.get_window_size()
            for _ in range(max_swipes):
                if direction == "down":
                    self.mobile_driver.swipe(
                        size["width"] * 0.20,
                        size["height"] * 0.80,
                        size["width"] * 0.20,
                        size["height"] * 0.20,
                        3000,
                    )
                elif direction == "up":
                    self.mobile_driver.swipe(
                        size["width"] * 0.20,
                        size["height"] * 0.20,
                        size["width"] * 0.20,
                        size["height"] * 0.80,
                        3000,
                    )
                elif direction == "right":
                    self.mobile_driver.swipe(
                        size["width"] * 0.80,
                        size["height"] * 0.50,
                        size["width"] * 0.20,
                        size["height"] * 0.50,
                        3000,
                    )
                elif direction == "left":
                    self.mobile_driver.swipe(
                        size["width"] * 0.20,
                        size["height"] * 0.50,
                        size["width"] * 0.80,
                        size["height"] * 0.50,
                        3000,
                    )

                if self.is_element_displayed(find_locator, explicit_wait):
                    return True

            return False

        except Exception as e:
            self.logger.exception("Exception in scroll_mobile method. Exception Details: %s", e)
            raise e
