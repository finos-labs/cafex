import platform
if platform.system().upper() == "WINDOWS":
    import pyautogui as py
    from pywinauto.base_wrapper import BaseWrapper
    from pywinauto.application import Application

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.utils.exceptions import CoreExceptions
from cafex_core.singletons_.session_ import SessionStore
from cafex_desktop.desktop_client.desktop_client_exceptions import (
    DesktopClientExceptions,
)


class DesktopElementInteractions:
    def __init__(self, phandler: Application = None):
        self.app = phandler or SessionStore().storage.get("handler")
        self.window = None
        self.__exceptions_generic = CoreExceptions()
        self.__exceptions_desktop_client = DesktopClientExceptions()
        self.logger = CoreLogger(name=__name__).get_logger()

    def click(self, element: BaseWrapper) -> None:
        """
        Perform a click operation on the specified UI element.

        This method clicks on the given UI element. The element should be a valid object
        retrieved using the `get_element` method or similar.

        Args:
            element (BaseWrapper): The UI element to click.

        Returns:
            None

        Raises:
            Exception: If an error occurs during the click operation.

        Examples:
            Click on a button element:
                >>> actions = DesktopElementInteractions(self.app)
                >>> window = self.app.window(title="My Window")
                >>> button = actions.get_element(window, locator_type="title", locator="Submit")
                >>> actions.click(button)

        Notes:
            - Ensure the element is a valid clickable object before calling this method.
            - Use the `get_element` method to retrieve the element before passing it to this method.
        """
        try:
            element.click_input()
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                message=f"Error occurred while performing click operation: {e}",
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )

    def double_click(self, element: BaseWrapper) -> None:
        """
        Perform a double click operation on the specified UI element.

        Args:
            element (BaseWrapper): The UI element object on which the double click is to be performed.

        Returns:
            None

        Raises:
            Exception: If an error occurs during the double click operation.

        Examples:
            Perform a double-click on an element:
                >>> actions = DesktopElementInteractions(self.app)
                >>> actions.double_click(element)
        """
        try:
            if element is None:
                raise ValueError("The provided element is None. Please provide a valid UI element.")

            element.click_input(double=True)
        except ValueError as ve:
            self.logger.error(f"Validation error: {ve}")
            raise
        except Exception as e:
            self.logger.exception(f"Unexpected error during double-click operation: {e}")
            self.__exceptions_generic.raise_generic_exception(
                message="Error occurred while performing double-click: " + str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def get_element(
        self,
        window_handle: BaseWrapper,
        locator_type: str,
        locator: str,
        auto_id: str = None,
        title: str = None,
        class_name: str = None,
        partial_text: str = None,
        control_type: str = None,
        found_index: str = None,
    ) -> BaseWrapper:
        """
        Retrieve a UI element based on the specified locator type and value.

        This method locates a UI element within a given window using the specified locator type and value.
        Additional parameters can be provided to refine the search.

        Args:
            window_handle (BaseWrapper): The window object where the element is to be located.
            locator_type (str): The type of locator to use. Accepts "title", "class_name", "auto_id", "title_re", or "control_type".
            locator (str): The value of the locator type (e.g., "title"="Content Tools Suite").
            auto_id (str, optional): The automation ID of the element. Defaults to None.
            title (str, optional): The title of the element. Defaults to None.
            class_name (str, optional): The class name of the element. Defaults to None.
            partial_text (str, optional): Partial text for title matching. Defaults to None.
            control_type (str, optional): The control type of the element. Defaults to None.
            found_index (str, optional): The index of the element if multiple matches are found. Defaults to None.

        Returns:
            object: The located element object if found.

        Raises:
            ValueError: If the locator is None or empty, or if the locator type is invalid.
            LookupError: If the element cannot be found.
            Exception: For any unexpected errors during execution.

        Examples:
            1. Locate an element by title:
                >>> actions = DesktopElementInteractions(self.app)
                >>> element = actions.get_element(window_handle, "title", "Content Tools Suite")

            2. Locate an element by class name with additional parameters:
                >>> element = actions.get_element(window_handle, "class_name", "Button", title="Submit")

            3. Locate an element by partial text:
                >>> element = actions.get_element(window_handle, "title_re", ".*Submit.*", partial_text="Submit")

        Notes:
            - The `locator_type` must be one of the following: "title", "class_name", "auto_id", "title_re",
            or "control_type".
            - If the element is found, it is outlined visually for debugging purposes.
            - If the element does not exist, an exception is raised.
        """
        try:
            if not locator:
                raise ValueError("Locator cannot be None or empty.")

            self.logger.info(f"Locator value: {locator}")

            # Validate locator_type
            valid_locator_types = ["title", "class_name", "auto_id", "title_re", "control_type"]
            if locator_type not in valid_locator_types:
                raise ValueError(
                    f"Invalid locator_type: {locator_type}. Must be one of {valid_locator_types}."
                )

            # Create the child_window object based on locator_type
            obj_element = window_handle.child_window(
                **{
                    locator_type: locator,
                    "auto_id": auto_id,
                    "title": title,
                    "title_re": partial_text,
                    "class_name": class_name,
                    "control_type": control_type,
                    "found_index": found_index,
                }
            )

            # Check if the element exists
            if obj_element.exists():
                obj_element.draw_outline()
                return obj_element
            else:
                raise LookupError(f"Element with {locator_type}='{locator}' not found.")

        except ValueError as ve:
            self.logger.error(f"Validation error: {ve}")
            self.__exceptions_desktop_client.raise_invalid_parameters(
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )
        except LookupError as le:
            self.logger.error(f"Element not found: {le}")
            self.__exceptions_desktop_client.raise_element_not_found(
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )
        except Exception as e:
            self.logger.exception(f"Unexpected error: {e}")
            self.__exceptions_generic.raise_generic_exception(
                message=f"Error while getting element: {e}",
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )

    def get_elements(
        self,
        window_handle: BaseWrapper,
        auto_id: str = None,
        title: str = None,
        class_name: str = None,
        partial_text: str = None,
        control_type: str = None,
    ) -> list[BaseWrapper]:
        """
        Retrieve multiple UI elements based on the provided parameters.

        This method iterates through all descendant elements of the given window handle
        and validates each element against the provided parameters. If an element matches
        the criteria, it is added to the result list.

        Args:
            window_handle (BaseWrapper): The window object where the elements are to be located.
            auto_id (str, optional): The automation ID of the elements. Defaults to None.
            title (str, optional): The title of the elements. Defaults to None.
            class_name (str, optional): The class name of the elements. Defaults to None.
            partial_text (str, optional): Partial text for title matching. Defaults to None.
            control_type (str, optional): The control type of the elements. Defaults to None.

        Returns:
            list[BaseWrapper]: A list of located element objects that match the provided criteria.

        Raises:
            Exception: If an unexpected error occurs during execution.

        Examples:
            1. Retrieve elements by title:
                >>> actions = DesktopElementInteractions(self.app)
                >>> elements = actions.get_elements(window_handle, title="Submit")

            2. Retrieve elements by class name and control type:
                >>> elements = actions.get_elements(window_handle, class_name="Button", control_type="ControlType.Button")

            3. Retrieve elements using partial text:
                >>> elements = actions.get_elements(window_handle, partial_text="Save")

        Notes:
            - At least one of the parameters (`auto_id`, `title`, `class_name`, `partial_text`, `control_type`)
              should be provided to locate elements.
            - The method uses the `validate_element` function to check if an element matches the criteria.
            - If an element is found, it is visually outlined for debugging purposes.
        """
        try:
            obj_elements = []
            for child in window_handle.descendants():
                if self.validate_element(
                    child,
                    auto_id=auto_id,
                    title=title,
                    class_name=class_name,
                    partial_text=partial_text,
                    control_type=control_type,
                ):
                    child.draw_outline()
                    obj_elements.append(child)

            return obj_elements

        except Exception as ex:
            self.__exceptions_generic.raise_generic_exception(
                message=f"Error occurred while getting elements: {ex}",
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def validate_element(
        self,
        element: BaseWrapper,
        auto_id: str = None,
        title: str = None,
        class_name: str = None,
        partial_text: str = None,
        control_type: str = None,
    ) -> bool:
        """
        Validate if a UI element matches the given properties.

        This method checks if the provided UI element matches any of the specified properties
        such as automation ID, title, class name, partial text, or control type.

        Args:
            element (BaseWrapper): The UI element to validate.
            auto_id (str, optional): The automation ID of the element. Defaults to None.
            title (str, optional): The title (name) of the element. Defaults to None.
            class_name (str, optional): The class name of the element. Defaults to None.
            partial_text (str, optional): A substring to match in the element's title. Defaults to None.
            control_type (str, optional): The control type of the element. Defaults to None.

        Returns:
            bool: `True` if the element matches any of the specified properties, `False` otherwise.

        Raises:
            Exception: If an error occurs during validation.

        Examples:
            Validate an element by title:
                >>> actions = DesktopElementInteractions(self.app)
                >>> actions.validate_element(element, title="Commodity")

            Validate an element by class name and control type:
                >>> actions.validate_element(element, class_name="TextBlock", control_type="Button")

            Validate an element using partial text:
                >>> actions.validate_element(element, partial_text="Form")
        """
        try:
            # Retrieve element properties
            element_auto_id = element.element_info.automation_id
            element_title = element.element_info.name
            element_class_name = element.element_info.class_name
            element_control_type = element.element_info.control_type

            # Validate against provided properties
            if auto_id and auto_id.strip().lower() == element_auto_id.strip().lower():
                return True
            if title and title.strip().lower() == element_title.strip().lower():
                return True
            if class_name and class_name.strip().lower() == element_class_name.strip().lower():
                return True
            if (
                control_type
                and control_type.strip().lower() == element_control_type.strip().lower()
            ):
                return True
            if partial_text and partial_text.strip().lower() in element_title.strip().lower():
                return True

            return False

        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                message=f"Error occurred while validating element: {e}",
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def get_text_value(self, element: BaseWrapper) -> str:
        """
        Retrieve the text value of the specified UI element.

        Args:
            element (BaseWrapper): The UI element object for which the text value is required.

        Returns:
            str: The text value of the specified element.

        Raises:
            Exception: If an error occurs while retrieving the text value.

        Examples:
            >>> actions = DesktopElementInteractions(self.app)
            >>> text_value = actions.get_text_value(element)

        Notes:
            - Use the `get_element` method to retrieve the element object before passing it to this method.
        """
        try:
            element.draw_outline()
            return element.window_text()
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                message=f"Error occurred while getting text value: {e}",
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def select_dropdown_value(
        self, pobject_dropdown: BaseWrapper, pstr_value_type: str, pstr_value: str
    ) -> None:
        """
        Select a value from a dropdown (combobox) element.

        This method allows the user to select a value from a dropdown element by specifying the value type
        (either "Text" or "Index") and the corresponding value. The method handles both text-based and
        index-based selection, including special cases for specific dropdowns.

        Args:
            pobject_dropdown (BaseWrapper): The dropdown (combobox) object to interact with.
            pstr_value_type (str): The type of value to select. Accepts "Text" for selecting by visible text
                                   or "Index" for selecting by the index of the item.
            pstr_value (str): The value to select. If `pstr_value_type` is "Text", this should be the visible
                              text of the item. If `pstr_value_type` is "Index", this should be the zero-based
                              index of the item as a string.

        Returns:
            None

        Raises:
            Exception: If an error occurs during the selection process or if invalid parameters are provided.

        Examples:
            1. Select a dropdown value by visible text:
                >>> actions = DesktopElementInteractions(self.app)
                >>> combobox = self.app.window(title="By Queue", auto_id="cmbQueue")
                >>> actions.select_dropdown_value(combobox, "Text", "By pending")

            2. Select a dropdown value by index:
                >>> combobox = self.app.window(title="By Queue", auto_id="cmbQueue")
                >>> actions.select_dropdown_value(combobox, "Index", "2")

        Notes:
            - The `pstr_value_type` parameter is case-insensitive and accepts "text" or "index".
            - If `pstr_value_type` is "Index", the `pstr_value` should be a string representation of the index
              (e.g., "0", "1", "2").
            - The method raises an exception if the provided `pstr_value_type` is invalid or if the selection fails.
        """
        try:
            if pstr_value_type.lower() == "text":
                for str_text in pobject_dropdown.get_properties()["texts"]:
                    if "Name =" in str_text:  # Special case in celsus
                        pobject_dropdown.type_keys("%{DOWN}")
                        pobject_dropdown.type_keys(pstr_value, with_spaces=True)
                        pobject_dropdown.type_keys("%{ENTER}")
                        break
                    elif "SNL.NextGenes" in str_text:  # Special case for SNL.NextGenes
                        list_items = pobject_dropdown.children(control_type="ListItem")
                        list_item_texts = pobject_dropdown.descendants(
                            control_type="Text", title=pstr_value
                        )

                        if list_item_texts:
                            list_item_text_parent = list_item_texts[0].parent()
                            index = list_items.index(list_item_text_parent)
                            if index is not None:
                                pobject_dropdown.select(index)
                                break
                    else:
                        pobject_dropdown.select(pstr_value)
                        break
            elif pstr_value_type.lower() == "index":
                # Select by index (convert to integer)
                index = int(pstr_value)
                pobject_dropdown.select(index)
            else:
                # Raise exception for invalid value type
                self.__exceptions_desktop_client.raise_invalid_parameters(
                    insert_report=True,
                    trim_log=True,
                    log_local=True,
                    fail_test=True,
                )
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                message=f"Error occurred while selecting the item in combobox: {e}",
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def select_radio(
        self,
        window_handle: BaseWrapper,
        check: str,
        auto_id: str = None,
        title: str = None,
        class_name: str = None,
    ):
        """
        Select or validate a radio button in the specified window.

        This method interacts with a radio button in the given window handle. It selects the radio button
        if the `check` parameter is set to "select" and the button is not already selected.

        Args:
            window_handle (BaseWrapper): The window handle containing the radio button.
            check (str): The action to perform. Accepts "select" to select the radio button.
            auto_id (str, optional): The automation ID of the radio button. Defaults to None.
            title (str, optional): The title of the radio button. Defaults to None.
            class_name (str, optional): The class name of the radio button. Defaults to None.

        Returns:
            None

        Raises:
            ValueError: If `check` is not "select".
            Exception: If an error occurs during the operation.

        Examples:
            Select a radio button by title:
                >>> actions = DesktopElementInteractions(self.app)
                >>> actions.select_radio(window_handle, "select", title="Option1")

            Select a radio button by automation ID:
                >>> actions.select_radio(window_handle, "select", auto_id="Radio1")
        """
        try:
            if check.lower() == "select":
                window_handle.draw_outline()
                control = window_handle.child_window(
                    auto_id=auto_id,
                    class_name=class_name,
                    title=title,
                    control_type="RadioButton",
                )
                state = control.is_selected()
                if check.lower() == "select" and state == 0:
                    control.select()
                else:
                    self.logger.info("No action required")
            else:
                self.__exceptions_desktop_client.raise_invalid_parameters(
                    insert_report=True,
                    trim_log=True,
                    log_local=True,
                    fail_test=True,
                )

        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                message="Error occurred while selecting/unselecting the radio button: " + str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def select_checkbox(
        self,
        window_handle: BaseWrapper,
        check: str,
        auto_id: str = None,
        title: str = None,
        class_name: str = None,
    ) -> None:
        """
        Select or unselect a checkbox in the specified window.

        This method interacts with a checkbox in the given window handle. It checks or unchecks the checkbox
        based on the `check` parameter.

        Args:
            window_handle (BaseWrapper): The window handle containing the checkbox.
            check (str): The action to perform. Accepts "check" to select or "uncheck" to deselect the checkbox.
            auto_id (str, optional): The automation ID of the checkbox. Defaults to None.
            title (str, optional): The title of the checkbox. Defaults to None.
            class_name (str, optional): The class name of the checkbox. Defaults to None.

        Returns:
            None

        Raises:
            ValueError: If `check` is not "check" or "uncheck".
            Exception: If an error occurs during the operation.

        Examples:
            Select a checkbox by title:
                >>> actions = DesktopElementInteractions(self.app)
                >>> actions.select_checkbox(window_handle, "check", title="Option1")

            Unselect a checkbox by automation ID:
                >>> actions.select_checkbox(window_handle, "uncheck", auto_id="Checkbox1")

        Notes:
            - Ensure the `window_handle` is a valid window object.
            - The method highlights the window for debugging purposes before interacting with the checkbox.
            - If the checkbox is already in the desired state, no action is performed.
        """
        try:
            if check.lower() not in ["check", "uncheck"]:
                self.__exceptions_desktop_client.raise_invalid_parameters(
                    insert_report=True,
                    trim_log=True,
                    log_local=True,
                    fail_test=True,
                )

            window_handle.draw_outline()
            control = window_handle.child_window(
                auto_id=auto_id,
                class_name=class_name,
                title=title,
                control_type="CheckBox",
            )
            state = control.get_toggle_state()
            if check.lower() == "check" and state == 0:
                control.click_input()
            elif check.lower() == "uncheck" and state == 1:
                control.click_input()
            else:
                self.logger.info("No action required")

        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                message="Error occurred while selecting/unselecting the checkbox: " + str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def select_list(self, list_items: list, index: int, operation: str) -> None:
        """
        Perform an operation on a list item.

        This method allows the user to select, click, or double-click on a list item based on the specified operation.

        Args:
            list_items (list): The list of items to interact with.
            index (int): The index of the list item to operate on (starting from 0).
            operation (str): The operation to perform on the list item. Accepts "click", "select", or "doubleclick".

        Returns:
            None

        Raises:
            ValueError: If the operation is invalid or the index is out of range.
            Exception: If an error occurs during the operation.

        Examples:
            Click on a list item:
                >>> actions = DesktopElementInteractions(self.app)
                >>> actions.select_list(list_items, 2, "click")

            Select a list item:
                >>> actions.select_list(list_items, 0, "select")

        Notes:
            - Index value starts from 0.
            - Ensure the `list_items` object is valid and contains the desired items.
        """
        try:
            if operation == "select":
                list_items[index].select()
            elif operation == "doubleclick":
                list_items[index].double_click_input()
            elif operation == "click":
                list_items[index].click_input()
            else:
                raise ValueError(
                    "Invalid operation: " + operation + ". Use 'click', 'select', or 'doubleclick'."
                )
        except IndexError:
            raise ValueError("Index " + str(index) + " is out of range for the provided list.")
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                message="Error occurred while selecting list value: " + str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )

    def select_menu_item(self, window_handle: BaseWrapper, menu_item_path: str) -> None:
        """
        Select a menu or submenu from the menu bar.

        This method allows the user to select a menu or submenu from the menu bar by providing the menu path
        with "->" as a separator. It handles nested menus and clicks on the appropriate menu items.

        Args:
            window_handle (BaseWrapper): The connected window object where the menu resides.
            menu_item_path (str): The menu path to select, with "->" as a separator for nested menus.

        Returns:
            None

        Raises:
            ValueError: If the menu path is invalid or improperly formatted.
            LookupError: If a menu item in the path cannot be found.
            Exception: For any unexpected errors during execution.

        Examples:
            Select a top-level menu:
                >>> actions = DesktopElementInteractions(self.app)
                >>> actions.select_menu_item(window_handle, "File->New")

            Select a submenu:
                >>> actions.select_menu_item(window_handle, "View->Advanced->Diagnostics")

            Select a deeply nested submenu:
                >>> actions.select_menu_item(window_handle, "View->Advanced->Diagnostics->Query Echo")
        """
        try:
            # Count the number of separators in the menu path
            separator_count = menu_item_path.count("->")

            if separator_count >= 2:
                # Split the menu path into individual menu items
                menu_items = self.split_line(menu_item_path, "->")

                # Click the first menu item
                self.get_element(window_handle, "title", menu_items[0]).click_input()

                # Retrieve and iterate through child menus
                child_menu_texts = self.get_element(
                    window_handle, "title", menu_items[0]
                ).children_texts()
                child_menu_1 = []
                child_menu_2 = []
                i = j = 0
                for i, child_menu in enumerate(child_menu_texts):
                    if menu_items[1] == child_menu:
                        window_handle.child_window(title=menu_items[0]).children()[i].click_input()
                        child_menu_1 = self.get_element(
                            window_handle, "title", menu_items[1], control_type="MenuItem"
                        ).children_texts()
                        print(child_menu_1)

                for j, sub_menu in enumerate(child_menu_1):
                    if menu_items[2] == sub_menu:
                        window_handle.child_window(title=menu_items[0]).children()[i].children()[
                            j
                        ].click_input()
                        child_menu_2 = self.get_element(
                            window_handle, "title", menu_items[2], control_type="MenuItem"
                        ).children_texts()
                        print(child_menu_2)

                for k, nested_menu in enumerate(child_menu_2):
                    if menu_items[3] == nested_menu:
                        window_handle.child_window(title=menu_items[0]).children()[i].children()[
                            j
                        ].children()[k].click_input()
            else:
                # Handle simple menu paths
                window_handle.menu_select(menu_item_path)
        except ValueError as ve:
            self.logger.error(f"Invalid menu path: {menu_item_path}. Error: {ve}")
            raise ValueError(
                f"Invalid menu path: {menu_item_path}. Ensure it is properly formatted with '->' as a separator."
            )
        except LookupError as le:
            self.logger.error(f"Menu item not found: {menu_item_path}. Error: {le}")
            raise LookupError(
                f"Menu item not found: {menu_item_path}. Check if the menu items exist."
            )
        except Exception as e:
            self.logger.exception(
                f"Unexpected error while selecting menu item: {menu_item_path}. Error: {e}"
            )
            self.__exceptions_generic.raise_generic_exception(
                message=f"Error while selecting menu item: {menu_item_path}. Details: {e}",
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def select_image(self, image_path: str) -> tuple[int, int]:
        """
        Locate an image on the primary screen and return its center coordinates.

        This method locates an image within an opened window on the primary screen. If the user has multiple screens,
        it will locate the image on the main window/primary screen.

        Args:
            image_path (str): The file path of the image to locate (e.g., "C:\\users\\test.png").

        Returns:
            tuple[int, int]: The (x, y) coordinates of the center of the located image.

        Raises:
            FileNotFoundError: If the image cannot be located on the screen.
            Exception: For any unexpected errors.

        Examples:
            Locate an image in the root folder:
                >>> actions = DesktopElementInteractions(self.app)
                >>> co_ordinates = actions.select_image("testimage.png")
                >>> py.doubleClick(co_ordinates)

            Locate an image in a specific path:
                >>> co_ordinates = actions.select_image("C:\\testimage.png")
                >>> py.doubleClick(co_ordinates)

        Notes:
            - This method works based on PPI (pixels per inch).
            - Ensure the screenshot is taken on the same machine, screen resolution, and size where the test is executed.
            - Always take screenshots on a maximized window for accurate results.
        """
        try:
            # Locate the image on the screen and get its bounding box
            coordinates = py.locateOnScreen(image_path)
            if not coordinates:
                raise FileNotFoundError(f"Image not found on screen: {image_path}")

            # Calculate the center of the located image
            center_position = py.center(coordinates)
            return center_position
        except FileNotFoundError as fnf_error:
            self.logger.error(fnf_error)
            self.__exceptions_desktop_client.raise_image_not_found(
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
        except Exception as ex:
            self.logger.exception(f"Unexpected error while locating image: {ex}")
            self.__exceptions_generic.raise_generic_exception(
                message=f"Error occurred while locating image: {ex}",
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )

    def type(self, pobject_edit: BaseWrapper, pstr_text: str) -> None:
        """
        Enter a value in a text box of control type Edit.

        Args:
            pobject_edit (BaseWrapper): The edit box object to interact with.
            pstr_text (str): The text to enter into the edit box.

        Returns:
            None

        Examples:
            1. Enter text into an edit box:
                >>> actions = DesktopElementInteractions(self.app)
                >>> editbox_object = self.app.window(title="Edit Box", control_type="Edit")
                >>> actions.type(editbox_object, 'input_text')
            2. Enter text into a search box:
                >>> editbox_search = self.app.window(title="Search Box", control_type="Edit")
                >>> actions.type(editbox_search, 'bank')

        Notes:
            - This method sends the specified text to the selected text box.
            - Ensure the `pobject_edit` is a valid edit box object before calling this method.
        """
        try:
            if not pobject_edit or not isinstance(pstr_text, str):
                raise ValueError("Invalid edit box object or text input provided.")

            pobject_edit.click_input()
            pobject_edit.type_keys(pstr_text, with_spaces=True)
        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                message=f"Error occurred while entering text in Edit box: {e}",
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def get_elements_old(
        self,
        window_handle: BaseWrapper,
        auto_id: str = None,
        title: str = None,
        class_name: str = None,
        partial_text: str = None,
        control_type: str = None,
    ) -> list[BaseWrapper]:
        """
        Retrieve multiple UI elements based on the provided parameters.

        This method locates multiple UI elements within a given window by iterating through
        the child elements and matching them against the provided parameters. If an element
        matches the criteria, it is added to the result list.

        Args:
            window_handle (BaseWrapper): The window object where the elements are to be located.
            auto_id (str, optional): The automation ID of the elements. Defaults to None.
            title (str, optional): The title of the elements. Defaults to None.
            class_name (str, optional): The class name of the elements. Defaults to None.
            partial_text (str, optional): Partial text for title matching. Defaults to None.
            control_type (str, optional): The control type of the elements. Defaults to None.

        Returns:
            list[BaseWrapper]: A list of located element objects that match the provided criteria.

        Raises:
            ValueError: If no valid parameters are provided for locating elements.
            LookupError: If no elements are found matching the criteria.
            Exception: For any unexpected errors during execution.

        Examples:
            1. Retrieve elements by title:
                >>> actions=DesktopElementInteractions(self.app)
                >>> elements = actions.get_elements_old(window_handle, title="Submit")

            2. Retrieve elements by class name and control type:
                >>> elements = actions.get_elements_old(window_handle, class_name="Button",
                control_type="ControlType.Button")

            3. Retrieve elements using partial text:
                >>> elements = actions.get_elements_old(window_handle, partial_text="Save")

        Notes:
            - At least one of the parameters (`auto_id`, `title`, `class_name`, `partial_text`, `control_type`)
              must be provided to locate elements.
            - The method uses a `while` loop to iterate through elements until no more matches are found.
            - If an element is found, it is visually outlined for debugging purposes.
            - If no elements are found, a `LookupError` is raised.
        """
        try:
            if not any([auto_id, title, class_name, partial_text, control_type]):
                raise ValueError("At least one parameter must be provided to locate elements.")

            found_index = 0
            elements = []

            while True:
                try:
                    element = window_handle.child_window(
                        auto_id=auto_id,
                        title=title,
                        class_name=class_name,
                        title_re=partial_text,
                        control_type=control_type,
                        found_index=found_index,
                    )
                    if element.exists():
                        self.logger.info(f"Found element at index: {found_index}")
                        elements.append(element)
                        element.draw_outline()
                        found_index += 1
                    else:
                        self.logger.info(f"Total elements found: {found_index}")
                        break
                except Exception:
                    self.logger.info(f"Total elements found: {found_index}")
                    break

            if not elements:
                raise LookupError("No elements found matching the provided criteria.")

            return elements

        except ValueError as ve:
            self.logger.error(f"Validation error: {ve}")
            raise
        except LookupError as le:
            self.logger.error(f"Element not found: {le}")
            raise
        except Exception as e:
            self.logger.exception(f"Unexpected error while getting elements: {e}")
            self.__exceptions_generic.raise_generic_exception(
                message=f"Error occurred while getting elements: {e}",
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )

    def split_line(self, text_to_split: str, split_string: str) -> list[str]:
        """
        Split a string using the specified separator.

        This method splits a given string into a list of substrings based on the provided separator.

        Args:
            text_to_split (str): The complete string to be split.
            split_string (str): The separator used to split the string.

        Returns:
            list[str]: A list of substrings obtained after splitting the input string.

        Examples:
            Split a string using "->" as a separator:
                >>> actions = DesktopElementInteractions(self.app)
                >>> actions.split_line("File->Open Containing Folder->cmd", "->")
                ['File', 'Open Containing Folder', 'cmd']

            Split a string using "," as a separator:
                >>> actions.split_line("test,image,png", ",")
                ['test', 'image', 'png']
        """
        split_words = text_to_split.split(split_string)
        for word in split_words:
            self.logger.info(word)
        return split_words
