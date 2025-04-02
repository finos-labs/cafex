from typing import Union
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common import keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from cafex_core.logging.logger_ import CoreLogger
from cafex_core.singletons_.session_ import SessionStore
from cafex_core.utils.config_utils import ConfigUtils
from cafex_ui.web_client.web_client_actions.base_web_client_actions import (
    WebClientActions,
)


class KeyboardMouseActions:
    """
    Description:
        |  This class contains methods related to ActionChains Class of Selenium package.
    """

    def __init__(self, web_driver: webdriver.Remote = None, default_explicit_wait: int = None):
        """Initializes KeyboardMouseActions with a driver and optional explicit
        wait.

        Args:
            web_driver: The selenium webdriver instance.
                            if not provided, it will be picked from Session Store
            default_explicit_wait: The default explicit wait time (in seconds).
                                   If not provided, it will be retrieved from ConfigUtils.
        """
        self.default_explicit_wait = default_explicit_wait or ConfigUtils().get_explicit_wait()
        self.logger = CoreLogger(name=__name__).get_logger()
        self.driver = web_driver or SessionStore().storage.get("driver")
        self.actions = ActionChains(self.driver)
        self.wca = WebClientActions(
            self.driver, default_explicit_wait=self.default_explicit_wait, default_implicit_wait=5
        )

    def robust_click(self, locator: Union[str, WebElement], explicit_wait: int = None) -> None:
        """Click on the locator provided.It will find the element for the
        locator given, convert it into a web element then wait for it to be
        clickable. The time of wait will depend on the value passed in the
        explicit wait.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().robust_click("xpath=//a[@class='advanced-search-link']")
            >> CafeXWeb().robust_click("xpath=//a[@class='advanced-search-link']", 30)

        Args:
            locator: A string representing the locator in a fixed format which is, locator_type=locator/web_element.
                     For example: id=username or xpath=.//*[@id='username'] or web_element
            explicit_wait: An integer representing the explicit wait time (in seconds) for the particular element.

        Returns:
            None
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            self.wca.get_clickable_web_element(locator, explicit_wait).click()
        except Exception:
            try:
                self.actions.click(
                    self.wca.get_clickable_web_element(locator, explicit_wait)
                ).perform()
            except Exception:
                try:
                    self.wca.execute_javascript(
                        "arguments[0].click();",
                        self.wca.get_clickable_web_element(locator, explicit_wait),
                    )
                except Exception as e3:
                    self.logger.exception(
                        "Exception in robust_click method. Exception Details:", exc_info=e3
                    )
                    raise e3

    def right_click(
            self, locator: Union[str, WebElement] = None, explicit_wait: int = None
    ) -> None:
        """Perform right click operation on the locator / web element which
        user passes. If element/locator is not being passed, right click
        operation gets performed on where cursor point is.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().right_click()
            >> CafeXWeb().right_click("xpath=//div[@id='context-menu']")
            >> CafeXWeb().right_click("xpath=//div[@id='context-menu']", 30)

        Args:
            locator: A string representing the locator in a fixed format which is, locator_type=locator.
                     For example: id=username or xpath=.//*[@id='username'] or web_element
            explicit_wait: An integer representing the explicit wait time (in seconds) for the particular element.

        Returns:
            None
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            if locator is not None:
                self.actions.context_click(
                    self.wca.get_clickable_web_element(locator, explicit_wait)
                ).perform()
            else:
                self.actions.context_click().perform()
        except Exception as e:
            self.logger.exception("Exception in right_click method.Exception Details: %s", str(e))
            raise e

    def double_click(
            self, locator: Union[str, WebElement] = None, explicit_wait: int = None
    ) -> None:
        """Perform double click operation on the locator / web element which
        user passes. If element/locator is not being passed, double click
        operation gets performed on where cursor point is.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().double_click()
            >> CafeXWeb().double_click("xpath=//button[@id='double-click']")
            >> CafeXWeb().double_click("xpath=//button[@id='double-click']", 30)

        Args:
            locator: A string representing the locator in a fixed format which is, locator_type=locator.
                     For example: id=username or xpath=.//*[@id='username'] or web_element
            explicit_wait: An integer representing the explicit wait time (in seconds) for the particular element.

        Returns:
            None
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            if locator is not None:
                self.actions.double_click(
                    self.wca.get_clickable_web_element(locator, explicit_wait)
                ).perform()
            else:
                self.actions.double_click().perform()
        except Exception as e:
            self.logger.exception("Exception in double_click method.Exception Details: %s", str(e))
            raise e

    def drag_and_drop(
            self,
            source_element: Union[str, WebElement],
            target_element: Union[str, WebElement],
            explicit_wait: int = None,
    ) -> None:
        """Drag source element and drop source element to the target element.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().drag_and_drop("xpath=//div[@id='source']", "xpath=//div[@id='target']")
            >> CafeXWeb().drag_and_drop("xpath=//div[@id='source']", "xpath=//div[@id='target']", 30)

        Args:
            source_element: A string representing the locator in a fixed format which is, locator_type=locator.
                            For example: id=username or xpath=.//*[@id='username'],or web_element
            target_element: A string representing the locator in a fixed format which is, locator_type=locator.
                            For example: id=username or xpath=.//*[@id='username'],or web_element
            explicit_wait: An integer representing the explicit wait time (in seconds) for the particular element.

        Returns:
            None
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            self.actions.drag_and_drop(
                self.wca.get_web_element(source_element, explicit_wait=explicit_wait),
                self.wca.get_web_element(target_element, explicit_wait=explicit_wait),
            ).perform()
        except Exception as e:
            self.logger.exception("Exception in drag_and_drop method.Exception Details: %s", str(e))
            raise e

    def drag_and_drop_by_offset(
            self,
            source_element: Union[str, WebElement],
            x_offset: int,
            y_offset: int,
            explicit_wait: int = None,
    ) -> None:
        """Hold down the left mouse button on the source element, then move to
        the target offset and release the mouse button.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().drag_and_drop_by_offset("xpath=//div[@id='source']", 100, 200)
            >> CafeXWeb().drag_and_drop_by_offset("xpath=//div[@id='source']", 100, 200, 30)

        Args:
            source_element: A string representing the locator in a fixed format which is, locator_type=locator.
                    For example: id=username or xpath=.//*[@id='username'] or web_element
            x_offset: X offset to move to.
            y_offset: Y offset to move to.
            explicit_wait: An integer representing the explicit wait time (in seconds) for the particular element.

        Returns:
            None
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            self.actions.drag_and_drop_by_offset(
                self.wca.get_web_element(source_element, explicit_wait), x_offset, y_offset
            ).perform()
        except Exception as e:
            self.logger.exception(
                "Exception in drag_and_drop_by_offset method.Exception Details: %s", str(e)
            )
            raise e

    def move_to_element(
            self, locator: Union[str, WebElement], then_click: bool = False, explicit_wait: int = None
    ) -> None:
        """Move the mouse cursor to the web element or the locator the cursor
        needs to move to.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().move_to_element("xpath=//div[@id='element']")
            >> CafeXWeb().move_to_element("xpath=//div[@id='element']", 30)

        Args:
            locator: A string representing the locator in a fixed format which is, locator_type=locator.
                     For example: id=username or xpath=.//*[@id='username'] or web_element
            then_click: A boolean representing whether to click after moving to the element.
            explicit_wait: An integer representing the explicit wait time (in seconds) for the particular element.

        Returns:
            None
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            if then_click:
                self.actions.move_to_element(
                    self.wca.get_clickable_web_element(locator, explicit_wait)
                ).click()
            else:
                self.actions.move_to_element(
                    self.wca.get_clickable_web_element(locator, explicit_wait)
                ).perform()
        except Exception as e:
            self.logger.exception(
                "Exception in move_to_element method.Exception Details: %s", str(e)
            )
            raise e

    def control_click(self, locator: Union[str, WebElement], explicit_wait: int = None) -> None:
        """Perform control click operation on given web element and the element
        would be opened in new window.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().control_click("xpath=//a[@id='link']")
            >> CafeXWeb().control_click("xpath=//a[@id='link']", 30)

        Args:
            locator: A string representing the locator in a fixed format which is, locator_type=locator.
                     For example: id=username or xpath=.//*[@id='username'] or web_element
            explicit_wait: An integer representing the explicit wait time (in seconds) for the particular element.

        Returns:
            None
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            self.actions.key_down(keys.Keys.CONTROL).click(
                self.wca.get_web_element(locator, explicit_wait=explicit_wait)
            ).key_up(keys.Keys.CONTROL).perform()
        except Exception as e:
            self.logger.exception("Exception in control_click method.Exception Details: %s", str(e))
            raise e

    def release(self, key: str = None) -> None:
        """Release all the keys which are pressed.If single key specified, it
        releases that key.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().release()
            >> CafeXWeb().release(keys.Keys.CONTROL)

        Args:
            key: A key which needs to be released.

        Returns:
            None
        """
        try:
            if key is not None:
                self.actions.key_up(key).perform()
            else:
                self.actions.release().perform()
        except Exception as e:
            self.logger.exception("Exception in release method.Exception Details: %s", str(e))
            raise e

    def move_to_element_with_offset(
            self,
            locator: Union[str, WebElement],
            x_offset: int,
            y_offset: int,
            explicit_wait: int = None,
    ) -> None:
        """Move the mouse cursor to the web element or the locator the cursor
        needs to move to.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().move_to_element_by_offset("xpath=//div[@id='element']", 100, 200)
            >> CafeXWeb().move_to_element_by_offset("xpath=//div[@id='element']", 100, 200, 30)

        Args:
            locator: A string representing the locator in a fixed format which is, locator_type=locator.
                     For example: id=username or xpath=.//*[@id='username'] or web_element
            x_offset: X offset to move to.
            y_offset: Y offset to move to.
            explicit_wait: An integer representing the explicit wait time (in seconds) for the particular element.

        Returns:
            None
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            self.actions.move_to_element_with_offset(
                self.wca.get_clickable_web_element(locator, explicit_wait), x_offset, y_offset
            ).perform()
        except Exception as e:
            self.logger.exception(
                "Exception in move_to_element_by_offset method.Exception Details: %s", str(e)
            )
            raise e

    def click_and_hold(self, locator: [str, WebElement], explicit_wait: int = None) -> None:
        """Perform click and hold operation on the locator / web element which
        user passes.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().click_and_hold("xpath=//div[@id='element']")
            >> CafeXWeb().click_and_hold("xpath=//div[@id='element']", 30)

        Args:
            locator: A string representing the locator in a fixed format which is, locator_type=locator.
                     For example: id=username or xpath=.//*[@id='username'] or web_element
            explicit_wait: An integer representing the explicit wait time (in seconds) for the particular element.

        Returns:
            None
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            self.actions.click_and_hold(
                self.wca.get_clickable_web_element(locator, explicit_wait)
            ).perform()
        except Exception as e:
            self.logger.exception(
                "Exception in click_and_hold method.Exception Details: %s", str(e)
            )
            raise e

    def reset_actions(self) -> None:
        """Reset the actions.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().reset_actions()

        Returns:
            None
        """
        try:
            self.actions.reset_actions()
        except Exception as e:
            self.logger.exception("Exception in reset_actions method.Exception Details: %s", str(e))
            raise e

    def copy_and_paste(
            self,
            source_locator: Union[str, WebElement],
            destination_locator: Union[str, WebElement],
            explicit_wait: int = None,
    ) -> None:
        """Copy text from the source element and paste it into the destination
        element.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().copy_and_paste("xpath=//input[@id='source']", "xpath=//input[@id='destination']")
            >> CafeXWeb().copy_and_paste("xpath=//input[@id='source']", "xpath=//input[@id='destination
        Args:
            source_locator: A string or WebElement representing the source element locator.
            destination_locator: A string or WebElement representing the destination element locator.
            explicit_wait: An optional integer representing the explicit wait time (in seconds) for the elements.

        Returns:
            None

        Raises:
            Exception: If an error occurs during the copy and paste operation.
        """
        try:
            source = self.wca.get_web_element(source_locator, explicit_wait)
            target = self.wca.get_web_element(destination_locator, explicit_wait)
            self.actions.click(source).key_down(Keys.CONTROL).send_keys("a").key_up(
                Keys.CONTROL
            ).perform()
            self.actions.key_down(Keys.CONTROL).send_keys("c").key_up(Keys.CONTROL).perform()
            self.actions.click(target).key_down(Keys.CONTROL).send_keys("v").key_up(
                Keys.CONTROL
            ).perform()
        except Exception as e:
            self.logger.exception(
                "Exception in enter_control_c method.Exception Details: %s", str(e)
            )
            raise e

    def move_by_offset(self, x_offset: int, y_offset: int, then_click: bool = False) -> None:
        """Move the mouse cursor to the x and y offset.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().move_by_offset(100, 200)

        Args:
            x_offset: X offset to move to.
            y_offset: Y offset to move to.
            then_click: A boolean representing whether to click after moving to the offset.

        Returns:
            None
        """
        try:
            if then_click:
                self.actions.move_by_offset(x_offset, y_offset).click()
            else:
                self.actions.move_by_offset(x_offset, y_offset).perform()
        except Exception as e:
            self.logger.exception(
                "Exception in move_by_offset method.Exception Details: %s", str(e)
            )
            raise e

    def send_keys(
            self,
            key: str | WebElement,
            locator: Union[str, WebElement] = None,
            explicit_wait: int = None,
    ) -> None:
        """Perform any key operation, including control, escape, backspace,
        delete, etc on any web element or the page.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().perform_key_action(key.Keys.CONTROL, "xpath=//input[@id='element']")
            >> CafeXWeb().perform_key_action(key.Keys.ESCAPE)
            >> CafeXWeb().perform_key_action("username")
            >> CafeXWeb().perform_key_action(key.Keys.BACKSPACE, "xpath=//input[@id='element']", 30)

        Args:
            key: A key which needs to be performed.
            locator: A string representing the locator in a fixed format which is, locator_type=locator or WebElement.
            explicit_wait: An integer representing the explicit wait time (in seconds) for the particular element.

        Returns:
            None
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            if locator is not None:
                web_element = self.wca.get_web_element(locator=locator, explicit_wait=explicit_wait)
                self.actions.send_keys_to_element(web_element, key).perform()
            else:
                self.actions.send_keys(key).perform()
        except Exception as e:
            self.logger.exception("Exception in send_keys method. Exception Details: %s", str(e))
            raise e

    def scroll(
            self, x_offset: int = None, y_offset: int = None, locator: Union[str, WebElement] = None
    ) -> None:
        """Scroll to the specified element or scroll by the specified amount.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().scroll("xpath=//div[@id='element']", 100, 200)
            >> CafeXWeb().scroll(100, 200)

        Args:
            locator: A string representing the locator in a fixed format which is, locator_type=locator or WebElement.
            x_offset: X offset to move to.
            y_offset: Y offset to move to.

        Returns:
            None
        """
        try:
            if locator is None:
                if x_offset is None or y_offset is None:
                    raise ValueError("x_offset and y_offset must be provided")
                self.actions.scroll_by_amount(x_offset, y_offset).perform()
            else:
                self.actions.scroll_to_element(self.wca.get_web_element(locator)).perform()
        except Exception as e:
            self.logger.exception("Exception in scroll method.Exception Details: %s", str(e))
            raise e
