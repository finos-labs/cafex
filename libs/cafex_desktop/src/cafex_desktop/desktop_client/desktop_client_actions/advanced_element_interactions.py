import datetime
import os
import platform

if platform.system().upper() == "WINDOWS":
    import pyautogui as py
    import pywinauto
    from pywinauto.application import Application
    from pywinauto.base_wrapper import BaseWrapper
    from pywinauto import mouse, controls, uia_defines, uia_element_info, keyboard
    from ctypes.wintypes import tagPOINT

from cafex_core.singletons_.session_ import SessionStore
from cafex_core.logging.logger_ import CoreLogger
from cafex_core.utils.exceptions import CoreExceptions
from cafex_desktop.desktop_client.desktop_client_actions.desktop_element_interactions import (
    DesktopElementInteractions,
)
from cafex_desktop.desktop_client.desktop_client_exceptions import (
    DesktopClientExceptions,
)


class AdvancedElementInteractions:

    def __init__(self, phandler: Application = None):
        self.app = phandler or SessionStore().storage.get("handler")
        self.window = None
        self.__exceptions_generic = CoreExceptions()
        self.__exceptions_desktop_client = DesktopClientExceptions()
        self.logger = CoreLogger(name=__name__).get_logger()
        self.element_interactions = DesktopElementInteractions(phandler)

    def scrolling(
        self,
        scroll_direction: str,
        scroll_count: int,
        retry_count: int = None,
        parent_element: BaseWrapper = None,
        scrollable_element: BaseWrapper = None,
    ) -> None:
        """
        Perform scroll functionality on a specified element or section.

        This method scrolls a given element or section based on the provided direction and count.
        It supports both standard and custom controls. For custom controls, the `parent_element`
        parameter can be used when unique identification of the element is difficult.

        Args:
            scroll_direction (str): The direction to scroll. Valid values are "up", "down", "left", "right".
            scroll_count (int): The number of times to scroll in the specified direction.
            retry_count (int, optional): The number of retries for the scroll operation. Defaults to None.
            parent_element (object, optional): The parent element to use for custom controls. Defaults to None.
            scrollable_element (object, optional): The element or section where the scroll bar exists. Defaults to None.

        Returns:
            None

        Raises:
            ValueError: If invalid arguments are provided for direction or count.
            Exception: If an error occurs during the scroll operation.

        Examples:
            1. Scroll down 10 times on a standard element:
                >>> actions = AdvancedElementInteractions(self.app)
                >>> element_actions = DesktopElementInteractions(self.app)
                >>> window= self.app.window(title="My Window")
                >>> element = element_actions.get_element(window, locator_type="title", locator="ScrollableElement")
                >>> actions.scrolling(scrollable_element=element, scroll_count=10, scroll_direction="down")

            2. Scroll up 5 times on a custom control:
                >>> actions.scrolling(scrollable_element=element, parent_element=parent_element,
                                  scroll_count=5, scroll_direction="up")

        Notes:
            - For custom controls, this method works when only one scroll bar exists.
            - For standard controls, it works in both single and multiple scroll bar sections.
        """
        try:
            scrollable_element_wrapper = scrollable_element.wrapper_object()
            if scrollable_element_wrapper.element_info.control_type.lower() != "custom":
                if scroll_direction.lower() in ["up", "down", "left", "right"]:
                    if scroll_count in ["page", "end"]:
                        scrollable_element.scroll(scroll_direction, scroll_count, count=retry_count)
                    else:
                        raise ValueError('Invalid scroll count. Use "page" or "end".')
                else:
                    raise ValueError(
                        'Invalid scroll direction. Use "up", "down", "left", or "right".'
                    )
            elif scrollable_element_wrapper.element_info.control_type.lower() == "custom":
                temp_count = 0
                if parent_element is None:
                    vertical_scroll = self.element_interactions.get_elements(
                        scrollable_element, auto_id="VerticalScrollBar"
                    )
                    horizontal_scroll = self.element_interactions.get_elements(
                        scrollable_element, auto_id="HorizontalScrollBar"
                    )
                    if vertical_scroll[0] is not None and horizontal_scroll[0] is not None:
                        while temp_count < scroll_count:
                            if scroll_direction.lower() == "up":
                                up_button = self.element_interactions.get_element(
                                    vertical_scroll[0], "auto_id", "PART_LineUpButton"
                                )
                                self.mouse_operations(up_button, "click", click_type="left")
                            elif scroll_direction.lower() == "down":
                                down_button = self.element_interactions.get_element(
                                    vertical_scroll[0], "auto_id", "PART_LineDownButton"
                                )
                                self.mouse_operations(down_button, "click", click_type="left")
                            elif scroll_direction.lower() == "left":
                                left_button = self.element_interactions.get_element(
                                    horizontal_scroll[0], "auto_id", "PART_LineLeftButton"
                                )
                                self.mouse_operations(left_button, "click", click_type="left")
                            elif scroll_direction.lower() == "right":
                                right_button = self.element_interactions.get_element(
                                    horizontal_scroll[0], "auto_id", "PART_LineRightButton"
                                )
                                self.mouse_operations(right_button, "click", click_type="left")
                            else:
                                raise ValueError("Invalid scroll direction for custom control.")
                            temp_count += 1
                    else:
                        raise ValueError("Unable to locate scroll bars for the custom control.")
            else:
                raise ValueError("Invalid control type for the scrollable element.")
        except ValueError as ve:
            self.__exceptions_desktop_client.raise_invalid_parameters(
                insert_report=True, trim_log=True, log_local=True, fail_test=False
            )
            raise ve
        except Exception as e:
            error_message = "Unable to scroll! Error occurred while scrolling: %s" % str(e)
            self.__exceptions_generic.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            raise e

    def mouse_operations(
        self,
        element: BaseWrapper,
        mouse_action_type: str,
        click_type: str = None,
        destination: BaseWrapper = None,
        coordinates: str = None,
    ) -> None:
        """
        Perform mouse operations such as left click, right click, double click, move, or drag.

        This method allows the user to perform various mouse operations on a specified UI element.
        The central position of the element is calculated using the `find_central_position` method.
        For drag operations, the user can specify either the destination element or the coordinates
        of the destination.

        Args:
            element (BaseWrapper): The UI element object on which the mouse operation is to be performed.
            mouse_action_type (str): The type of mouse action to perform. Accepts "click", "move", or "drag".
            click_type (str, optional): The type of click to perform. Accepts "left", "right", or "double".
                                        Defaults to "left" if not provided.
            destination (BaseWrapper, optional): The destination element for drag operations.
            coordinates (str, optional): The destination coordinates for drag operations in the format "x,y".

        Raises:
            ValueError: If invalid parameters are provided or required parameters are missing.
            Exception: If an error occurs during the mouse operation.

        Returns:
            None

        Examples:
            Perform a left click on an element:
                >>> actions = AdvancedElementInteractions(self.app)
                >>> actions.mouse_operations(element, "click", click_type="left")

            Perform a double click on an element:
                >>> actions.mouse_operations(element, "click", click_type="double")

            Move the mouse to an element:
                >>> actions.mouse_operations(element, "move")

            Drag an element to another element:
                >>> actions.mouse_operations(element, "drag", destination=destination)

            Drag an element to specific coordinates:
                >>> actions.mouse_operations(element, "drag", coordinates="200,300")
        """
        try:
            if mouse_action_type is not None:
                try:
                    if "click" in mouse_action_type.lower():
                        # Default to left-click if no click type is provided
                        if click_type is None or "left" in click_type.lower():
                            pywinauto.mouse.click(
                                coords=(self.find_central_position(element)), button="left"
                            )
                        elif "right" in click_type.lower():
                            pywinauto.mouse.right_click(
                                coords=(self.find_central_position(element))
                            )
                        elif "double" in click_type.lower():
                            pywinauto.mouse.double_click(
                                coords=(self.find_central_position(element))
                            )
                    elif "move" in mouse_action_type.lower():
                        pywinauto.mouse.move(coords=(self.find_central_position(element)))
                    elif "drag" in mouse_action_type.lower():
                        if destination is not None:
                            pywinauto.mouse.press(
                                button="left", coords=self.find_central_position(element)
                            )
                            pywinauto.mouse.release(
                                button="left",
                                coords=self.find_central_position(destination),
                            )
                        elif coordinates is not None:
                            coords = coordinates.split(",")
                            pywinauto.mouse.press(
                                button="left", coords=self.find_central_position(element)
                            )
                            pywinauto.mouse.release(
                                button="left",
                                coords=(int(coords[0]), int(coords[1])),
                            )
                        else:
                            raise ValueError("Invalid parameters for drag operation.")
                except Exception as e:
                    self.__exceptions_desktop_client.raise_invalid_parameters(
                        insert_report=True,
                        trim_log=True,
                        log_local=True,
                        fail_test=True,
                    )
            else:
                raise ValueError("Mouse action type cannot be None.")

        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                message="Error occurred while performing mouse operation: %s" % str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def find_central_position(self, element: BaseWrapper) -> tuple[int, int]:
        """
        Fetch the central coordinates of the specified UI element.

        This method calculates the central position of the given element based on its rectangle coordinates
        and returns the (x, y) coordinates.

        Args:
            element (BaseWrapper): The UI element object for which the central position is to be calculated.

        Returns:
            tuple[int, int]: The (x, y) coordinates of the central position of the element.

        Raises:
            Exception: If an error occurs while calculating the central position.

        Examples:
            >>> actions = AdvancedElementInteractions(self.app)
            >>> central_position = actions.find_central_position(element)
        """
        try:
            elem_position = element.rectangle()
            x_central = int((elem_position.left + elem_position.right) / 2)
            y_central = int((elem_position.top + elem_position.bottom) / 2)
            elem_center_point = (x_central, y_central)
            return elem_center_point
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                message="Error occurred while finding central position of specified element: %s"
                % str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def click_based_on_coordinates(
        self, center_position: list[int], double_click: bool = False
    ) -> None:
        """
        Perform a click operation on an element based on its coordinates.

        This method allows the user to perform a single or double click operation on a UI element
        based on the provided center position coordinates.

        Args:
            center_position (list[int]): The center position of the element as a list of [x, y] coordinates.
            double_click (bool, optional): Set to True to perform a double click operation. Defaults to False.

        Examples:
            Perform a single click on an element:
                >>> actions = AdvancedElementInteractions(self.app)
                >>> actions.click_based_on_coordinates([100, 200])

            Perform a double click on an element:
                >>> actions = AdvancedElementInteractions(self.app)
                >>> actions.click_based_on_coordinates([100, 200], double_click=True)

        Raises:
            Exception: If an error occurs during the click operation.

        Notes:
            - Ensure the `center_position` is a valid list containing two integers representing the x and y coordinates.
            - This method uses the `pyautogui` library to perform the click operation.
            - The method handles exceptions and logs errors using the `__exceptions_generic` object.
        """
        try:
            if double_click:
                py.click(center_position, clicks=2)
            else:
                py.click(center_position)
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                message="Error occurred during click operation: %s" % str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def control_type_by_coordinates(self, x: int, y: int) -> str:
        """
        Fetch the control type of specified UI element based on its coordinates.

        This method identifies a UI element using the provided x and y coordinates and retrieves its control type.

        Args:
            x (int): The x-coordinate of the element.
            y (int): The y-coordinate of the element.

        Returns:
            str: The control type of the specified element.

        Examples:
            Set the focus on the window where you want to locate the element, then call the method:
                >>> actions = AdvancedElementInteractions(self.app)
                >>> control_type = actions.control_type_by_coordinates(-1098, 247)

        Raises:
            Exception: If the control type cannot be retrieved or an error occurs.

        Notes:
            - Ensure the coordinates provided are valid and correspond to an existing UI element.
            - This method uses the `return_element_by_coordinates` method to locate the element.
        """
        try:
            element = self.return_element_by_coordinates(x, y)
            if element and element._control_types:
                return element._control_types[0]
            else:
                raise ValueError(
                    "No control types found for element at coordinates ({%s}, {%s}).", x, y
                )
        except Exception as e:
            error_message = (
                "Failed to fetch control type for coordinates ("
                + str(x)
                + ", "
                + str(y)
                + "): "
                + str(e)
            )
            self.__exceptions_generic.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def return_element_by_coordinates(
        self, x: int, y: int
    ) -> pywinauto.controls.uiawrapper.UIAWrapper:
        """
        Fetch the UI element at the specified coordinates.

        This method identifies a UI element using the provided x and y coordinates and returns the element wrapper.
        It uses the `pywinauto` library to interact with the UI Automation framework and locate the element at the
        specified screen coordinates. If the element is found, it wraps the element in a `UIAWrapper` object for
        further interaction. If the element cannot be found, an exception is raised with a detailed error message.

        Args:
            x (int): The x-coordinate of the element on the screen.
            y (int): The y-coordinate of the element on the screen.

        Returns:
            pywinauto.controls.uiawrapper.UIAWrapper: The wrapper object for the UI element located at the specified
             coordinates.

        Raises:
            Exception: If the element cannot be found or an error occurs during the process.

        Examples:
            1. Locate an element at specific screen coordinates:
                >>> actions = AdvancedElementInteractions(self.app)
                >>> element = actions.return_element_by_coordinates(-1098, 247)

            2. Handle exceptions when the element is not found:
                >>> try:
                >>>     element = actions.return_element_by_coordinates(100, 200)
                >>> except Exception as e:
                >>>     print(f"Error: {e}")

        Notes:
            - Ensure the coordinates provided are valid and correspond to an existing UI element on the screen.
            - This method relies on the `pywinauto` library, which requires the application to be running and accessible.
            - The method uses the `tagPOINT` structure to represent the screen coordinates and the `ElementFromPoint`
              function to locate the element.
            - If an exception occurs, it is logged and re-raised using the `raise_generic_exception` method for consistent
              error handling across the application.
        """
        try:
            # Locate the element at the specified coordinates
            elem = pywinauto.uia_defines.IUIA().iuia.ElementFromPoint(tagPOINT(x, y))
            element_info = pywinauto.uia_element_info.UIAElementInfo(elem)
            wrapper = pywinauto.controls.uiawrapper.UIAWrapper(element_info)
            return wrapper
        except Exception as e:
            # Construct a detailed error message
            error_message = f"Error occurred! Unable to find element at coordinates ({x}, {y}): {e}"
            # Raise a generic exception with the error message
            self.__exceptions_generic.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def keyboard_operation(self, key: str) -> None:
        """
        Perform a keyboard operation by sending a specified key or key combination.

        This method allows the user to perform keyboard operations by sending a key or key combination
        to the active window or control.

        Args:
            key (str): The keyboard key or key combination to send. For example, '^g' for Ctrl+G or '{VK_DOWN}' for the Down arrow key.

        Returns:
            None

        Raises:
            ValueError: If the provided key is invalid or empty.
            Exception: For any unexpected errors during execution.

        Examples:
            Perform a keyboard operation with a key combination:
                >>> actions = AdvancedElementInteractions(self.app)
                >>> actions.keyboard_operation('^g')

            Perform a keyboard operation with a special key:
                >>> actions.keyboard_operation('{VK_DOWN}')
        """
        try:
            if not key or not isinstance(key, str):
                raise ValueError("Invalid or empty key provided for keyboard operation.")

            pywinauto.keyboard.send_keys(key)
        except ValueError as ve:
            self.logger.error(f"Validation error: {ve}")
            raise ValueError(f"Invalid key provided: {key}. Error: {ve}")
        except Exception as e:
            self.logger.exception(f"Unexpected error during keyboard operation: {e}")
            self.__exceptions_generic.raise_generic_exception(
                message=f"Error occurred while performing keyboard operation: {e}",
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )

    def take_screenshot(self, path: str, extension: str = "png") -> None:
        """
        Take a screenshot and save it to the specified path.

        This method captures a screenshot of the current screen and saves it to the provided file path.
        The user can specify the file format (extension) of the screenshot.

        Args:
            path (str): The directory where the screenshot will be saved.
            extension (str, optional): The file format of the screenshot (e.g., "png", "jpg"). Defaults to "png".

        Examples:
            Save a screenshot in PNG format:
                take_screenshot("C:\\Backup")

            Save a screenshot in JPG format:
                take_screenshot("C:\\Backup", extension="jpg")

        Raises:
            Exception: If an error occurs while taking or saving the screenshot.
        """
        try:
            # Take screenshot
            screenshot = py.screenshot()
            # Generate a unique file name based on the current timestamp
            file_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f") + f".{extension}"
            # Save the screenshot to the specified path
            screenshot.save(os.path.join(path, file_name))
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                message="Error occurred while taking screenshot: %s" % str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def dynamic_wait(
        self, element: BaseWrapper, status: str, timeout: int = 60, state: bool = True
    ) -> bool:
        """
        Dynamically wait for an element/object based on the specified status.

        This method waits for the given element to meet the specified status (e.g., exists, visible, enabled, ready)
        within the provided timeout period.

        Args:
            element (BaseWrapper): The window element object to wait for.
            status (str): The status to wait for (e.g., "exists", "visible", "enabled", "ready").
            timeout (int, optional): The maximum time (in seconds) to wait. Defaults to 60.
            state (bool, optional): If True, waits for the status to be met. If False, waits for the status to not be met. Defaults to True.

        Returns:
            bool: True if the condition is met within the timeout, False otherwise.

        Raises:
            Exception: If invalid parameters are provided or an error occurs during execution.

        Examples:
            1. Wait for an element to become visible:
                >>> actions = AdvancedElementInteractions(self.app)
                >>> button = self.app.top_window().window(auto_id="QuickGet", control_type="Button")
                >>> actions.dynamic_wait(button, "visible", timeout=120)

            2. Wait for an element to not be visible:
                >>> actions.dynamic_wait(button, "visible", timeout=120, state=False)

        Notes:
            - The `status` parameter accepts values in lowercase: "exists", "visible", "enabled", "ready".
            - "exists" means the object is present in the window and valid.
            - "visible" means the object is not hidden in the window.
            - "enabled" means the object is not disabled in the window.
            - "ready" means the object is both visible and enabled.
        """
        try:
            if state:
                element.wait(status, timeout=timeout)
            else:
                element.wait_not(status, timeout=timeout)
            return True
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                message="Error during dynamic wait: " + str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False
