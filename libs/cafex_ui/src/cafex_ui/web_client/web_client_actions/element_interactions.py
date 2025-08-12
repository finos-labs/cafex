import time
from typing import List, Union
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.relative_locator import locate_with
from selenium.webdriver.support.ui import Select, WebDriverWait
from cafex_core.logging.logger_ import CoreLogger
from cafex_core.singletons_.session_ import SessionStore
from cafex_core.utils.config_utils import ConfigUtils


class ElementInteractions:
    """This class contains methods to perform various operations on a browser
    and its elements."""

    def __init__(
            self,
            web_driver: WebDriver = None,
            default_explicit_wait: int = None,
            default_implicit_wait: int = None,
    ):
        """Initializes WebClientActions with a driver and optional explicit
        wait.

        Args:
            web_driver: The selenium webdriver instance.
                            if not provided, it will be picked from Session Store
            default_explicit_wait: The default explicit wait time (in seconds).
                                   If not provided, it will be retrieved from ConfigUtils.
        """
        self.default_explicit_wait = default_explicit_wait or ConfigUtils().get_explicit_wait()
        self.default_implicit_wait = default_implicit_wait or ConfigUtils().get_implicit_wait()
        self.logger = CoreLogger(name=__name__).get_logger()
        self.driver = web_driver or SessionStore().storage.get("driver")

    def click(self, locator: Union[str, WebElement], explicit_wait: int = None) -> None:
        """Click on the locator provided.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().click("xpath=//a[@class='advanced-search-link']")
            >> CafeXWeb().click("xpath=//a[@class='advanced-search-link']", 30)

        Args:
            locator: A string representing the locator in a fixed format which is, locator_type=locator.
                     For example: id=username or xpath=.//*[@id='username'],or web element.
            explicit_wait: An integer representing the explicit wait time (in seconds) for the particular element.

        Returns:
            None
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            self.get_clickable_web_element(locator, explicit_wait).click()
        except Exception as e:
            self.logger.exception(
                "Exception in click method for locator: %s. Exception Details: %s", locator, repr(e)
            )
            raise e

    def type(
            self,
            locator: Union[str, WebElement],
            text: str = None,
            clear: bool = False,
            explicit_wait: int = None,
            click_before_type: bool = True,
    ) -> None:
        """Type the given value on the locator provided.If clear is set to
        True, the respective field content will be cleared and by default
        click_before_type is set to True, which means the element will be
        clicked before typing the given text.

        Examples:
           >> from cafex_ui import CafeXWeb
           >> CafeXWeb().type("xpath=//a[@class='username']", "your_username")
           >> CafeXWeb().type("xpath=//a[@class='username']", "your_username", explicit_wait=30)

        Args:
            locator: A string representing the locator in a fixed format which is, locator type=locator.
                     For example: id=username or xpath=.//*[@id='username'] or web element.
            text: A string representing the value to be typed into the web element.
            explicit_wait: An integer representing the explicit wait time (in seconds) for the particular element.
            clear: A boolean to use clear feature, if set to True respective field content will be cleared.
                   By default, this is set to False.
            click_before_type: A boolean to determine whether there will be a click on the element or not before typing
             the given text.

        Returns:
            None
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            if click_before_type:
                self.get_clickable_web_element(locator, explicit_wait).click()
            if clear:
                self.get_clickable_web_element(locator, explicit_wait).clear()
            self.get_clickable_web_element(locator, explicit_wait).send_keys(text)
        except Exception as e:
            self.logger.exception(
                "Exception in type method for locator: %s. Exception Details: %s", locator, repr(e)
            )
            raise e

    def is_element_present(
            self, locator: Union[str, WebElement], explicit_wait: int = None
    ) -> bool:
        """Verify if the given locator or web element is present on the page.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().is_element_present("xpath=//*[@name='password']")

        Args:
            locator: A string or WebElement representing the locator in a fixed format which is,
                     locator_type=locator. For example: id=username or xpath=.//*[@id='username'] or web element.
            explicit_wait: An integer representing the explicit wait time (in seconds) for the particular element.

        Returns:
            A boolean indicating if the element is present.
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            if isinstance(locator, str):
                locator_details = locator.split("=", 1)

                if locator.lower().find("accessibility id") != -1:
                    locator = locator.replace("accessibility id", "id")

                element = WebDriverWait(self.driver, explicit_wait).until(
                    EC.presence_of_element_located(
                        (self.get_locator_strategy(locator_details[0]), locator_details[1])
                    )
                )
                return element is not None
            if isinstance(locator, WebElement):
                return locator.is_displayed()
        except Exception as e:
            self.logger.exception(
                "Exception in is_element_present method. Exception Details: %s", repr(e)
            )
            return False

    def is_element_displayed(
            self, locator: Union[str, WebElement], explicit_wait: int = None
    ) -> bool:
        """Verify if the given locator is present and visible on the page.

        Examples:
           >> from cafex_ui import CafeXWeb
           >> CafeXWeb().is_element_displayed("xpath=//*[@name='password']")

        Args:
            locator: A string or WebElement representing the locator in a fixed format which is,
                     locator_type=locator. For example: id=username or xpath=.//*[@id='username']
            explicit_wait: An integer representing the explicit wait time (in seconds) for the particular element.

        Returns:
            A boolean indicating if the element is displayed.
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            if isinstance(locator, str):
                if locator.lower().find("accessibility id") != -1:
                    locator = locator.replace("accessibility id", "id")

                locator_details = locator.split("=", 1)
                element = WebDriverWait(self.driver, explicit_wait).until(
                    EC.visibility_of_element_located(
                        (self.get_locator_strategy(locator_details[0]), locator_details[1])
                    )
                )
                return element is not None
            if isinstance(locator, WebElement):
                return locator.is_displayed()
        except Exception as e:
            self.logger.exception(
                "Exception in is_element_displayed method. Exception Details: %s", repr(e)
            )
            return False

    def get_web_element(
            self, locator: Union[str, WebElement], explicit_wait: int = None
    ) -> WebElement:
        """Verify if the given locator is present and return the web element
        for the locator.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().get_web_element("xpath=//*[@name='password']")

        Args:
            locator: A string or WebElement representing the locator in a fixed format which is,
                     locator_type=locator. For example: id=username or xpath=.//*[@id='username']
            explicit_wait: An integer representing the explicit wait time (in seconds) for the particular element.

        Returns:
            A WebElement representing the located element.
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            if isinstance(locator, str):
                locator_details = locator.split("=", 1)
                return WebDriverWait(self.driver, explicit_wait).until(
                    EC.presence_of_element_located(
                        (self.get_locator_strategy(locator_details[0]), locator_details[1])
                    )
                )
            if isinstance(locator, WebElement):
                return locator
        except Exception as e:
            self.logger.exception(
                "Exception in get_web_element method. Exception Details: %s", repr(e)
            )
            raise e

    def get_clickable_web_element(
            self, locator: Union[str, WebElement], explicit_wait: int = None
    ) -> WebElement:
        """Verify if the given locator is present and clickable and return the
        web element for the locator.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().get_clickable_web_element("xpath=//*[@name='password']")

        Args:
            locator: A string representing the locator in a fixed format which is, locator_type=locator.
                     For example: id=username or xpath=.//*[@id='username']
            explicit_wait: An integer representing the explicit wait time (in seconds) for the particular element.

        Returns:
            A WebElement representing the located element.
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            if isinstance(locator, str):
                locator_details = locator.split("=", 1)
                return WebDriverWait(self.driver, explicit_wait).until(
                    EC.element_to_be_clickable(
                        (self.get_locator_strategy(locator_details[0]), locator_details[1])
                    )
                )
            if isinstance(locator, WebElement):
                return locator
        except Exception as e:
            self.logger.exception(
                "Exception in get_clickable_web_element method. Exception Details: ", exc_info=e
            )
            raise e

    def get_web_elements(self, locator: str, explicit_wait: int = None) -> List[WebElement]:
        """Verify if the given locator is present and return list of all web
        elements matching this locator.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().get_web_elements("xpath=//*[@name='password']")

        Args:
            locator: A string representing the locator in a fixed format which is, locator_type=locator.
                     For example: id=username or xpath=.//*[@id='username'] or web element.
            explicit_wait: An integer representing the explicit wait time (in seconds) for the particular element.

        Returns:
            A list of WebElements representing the located elements.
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            locator_type, locator_value = locator.split("=", 1)
            return WebDriverWait(self.driver, explicit_wait).until(
                EC.presence_of_all_elements_located(
                    (self.get_locator_strategy(locator_type), locator_value)
                )
            )
        except Exception as e:
            self.logger.exception(
                "Exception in get_web_elements method for locator: {locator}. Exception Details: %s",
                repr(e),
            )
            raise e

    def wait_for_invisibility_web_element(
            self, locator: str, explicit_wait: int = None
    ) -> WebElement | bool:
        """Wait until the locator passed is invisible and return True or False
        based on whether the element is invisible or not.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().wait_for_invisibility_web_element("xpath=//*[@name='password']")

        Args:
            locator: A string representing the locator in a fixed format which is, locator_type=locator.
                     For example: id=username or xpath=.//*[@id='username']
            explicit_wait: An integer representing the explicit wait time (in seconds) for the particular element.

        Returns:
            A boolean indicating if the element is invisible.
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            locator_details = locator.split("=", 1)
            return WebDriverWait(self.driver, explicit_wait).until(
                EC.invisibility_of_element_located(
                    (self.get_locator_strategy(locator_details[0]), locator_details[1])
                )
            )

        except Exception as e:
            self.logger.exception(
                "Exception in wait_for_invisibility_web_element method. Exception Details: ",
                exc_info=e,
            )
            return False

    def get_xpath(self, **kwargs) -> str:
        """Create an xpath for the given tag/element type, attribute, and its
        value.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().get_xpath(tag='a', attribute='text', value='new')

        Args:
            tag: A string representing the element type. For example: a or input or div.
            attribute: A string representing the name of the attribute. For example: value.
            value: A string representing the value of the attribute.

        Returns:
            A string representing the constructed xpath.
        """
        tag = kwargs.get("tag", "*")
        attribute = kwargs.get("attribute")

        if not attribute:
            return f".//{tag}"
        value = kwargs.get("value", "''")
        return f".//{tag}[{attribute}='{value}']"

    def get_attribute_value(
            self, locator: Union[str, WebElement], attribute: str, explicit_wait: int = None
    ) -> str:
        """Return the attribute value for the web element or find the web
        element using the locator passed and then return the attribute value of
        the web element.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().get_attribute_value("xpath=//*[@name='password']", "class")
            >> # This will find the web_element using the xpath in the first parameter then return the value of the class
             attribute for that web element.

        Args:
            locator: A string or WebElement representing the locator in a fixed format which is, locator_type=locator.
                     For example: id=username or xpath=.//*[@id='username']
            attribute: A string representing the attribute for which the value will be returned.
            explicit_wait: An integer representing the explicit wait time (in seconds) for the particular element.

        Returns:
            A string representing the attribute value.
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            return self.get_web_element(locator, explicit_wait).get_attribute(attribute)
        except Exception as e:
            self.logger.exception(
                "Exception in get_attribute_value method. Exception Details: ", exc_info=e
            )
            return ""

    def get_locator_strategy(self, pstr_locator_strategy):
        """Get the locator strategy.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().get_locator_strategy("xpath")

        Args:
            pstr_locator_strategy: A string representing the locator strategy.

        Returns:
            The locator strategy.
        """
        locator_strategies = [
            "XPATH",
            "ID",
            "NAME",
            "CLASS_NAME",
            "LINK_TEXT",
            "CSS_SELECTOR",
            "PARTIAL_LINK_TEXT",
            "TAG_NAME",
        ]

        if pstr_locator_strategy.upper() not in locator_strategies:
            raise Exception(
                "Unsupported locator strategy - "
                + pstr_locator_strategy.upper()
                + "! "
                + "Supported locator strategies are 'XPATH', 'ID', 'NAME', "
                  "'CSS_SELECTOR', 'TAG_NAME', 'LINK_TEXT' , 'CLASS_NAME' and 'PARTIAL_LINK_TEXT'"
            )
        else:
            return getattr(By, pstr_locator_strategy.upper())

    def get_child_elements(
            self,
            parent_locator: Union[str, WebElement] = None,
            search_locator: Union[str, WebElement] = None,
    ) -> List[WebElement] | None:
        """Return the first available child of the element provided.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> p_element = CafeXWeb().get_web_element("xpath=//div[@id='parent']")
            >> child_element = CafeXWeb().get_child_elements(parent_locator=parent_element,
            search_locator="xpath=./*[@name='child']")

        Args:
            parent_locator: A WebElement or string representing the element on which child elements need to be searched.
                            Locator can only be xpath/id/css/classname/tag_name/name/link_text or web element.
            search_locator: A string representing the locator in a fixed format which is, locator_type=locator.
                            For example: id=username or xpath=.//*[@id='username'] or web element.

        Returns:
            A WebElement representing the first available child element.
        """
        try:

            if parent_locator is None:
                self.logger.info("No element is specified.")
                return None

            if search_locator is None:
                self.logger.info("No locator is specified.")
                return None

            locator_details = search_locator.split("=", 1)

            if isinstance(parent_locator, WebElement):
                return parent_locator.find_elements(
                    self.get_locator_strategy(locator_details[0]), locator_details[1]
                )

            if isinstance(parent_locator, str):
                parent_element = self.get_web_element(parent_locator)
                return parent_element.find_elements(
                    self.get_locator_strategy(locator_details[0]), locator_details[1]
                )

        except Exception as e:
            self.logger.exception(
                "Exception in get_child_elements method. Exception Details: ", exc_info=e
            )
            raise e

    def highlight_web_element(
            self, locator: Union[str, WebElement], highlight_time: float = 0.5
    ) -> None:
        """Highlight the web element.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().highlight_web_element("xpath=//*[@name='password']")
            >> CafeXWeb().highlight_web_element("xpath=//*[@name='password']", 0.25)

        Args:
            locator: A string or WebElement representing the locator in a fixed format which is, locator_type=locator.
                     For example: id=username or xpath=.//*[@id='username']
            highlight_time: A float representing the time (in seconds) for which the element needs to be highlighted.

        Returns:
            None
        """
        try:
            locator = self.get_web_element(locator)
            str_original_style = locator.get_attribute("style")
            self.driver.execute_script(
                "arguments[0].setAttribute('style', arguments[1])", locator, "border: 4px solid red"
            )
            time.sleep(highlight_time)
            self.driver.execute_script(
                "arguments[0].setAttribute('style', arguments[1])", locator, str_original_style
            )
        except Exception as e:
            self.logger.exception(
                "Exception in highlight_web_element method. Exception Details: %s", repr(e)
            )
            raise e

    def execute_javascript(self, script: str, *args) -> str:
        """Execute the JavaScript code passed in the 'script' parameter with
        additional parameters for the script (if required).

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().execute_javascript("document.getElementById('some_id').value='someValue';")
            >> CafeXWeb().execute_javascript("arguments[0].click();", web_element)

        Args:
            script: A string representing the actual JavaScript code that needs to be executed.
            *args: Additional arguments for the script (if required).

        Returns:
            A string or None, depending on the JavaScript code.
        """
        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            self.logger.exception(
                "Exception in execute_javascript method for script: {script}. Exception Details: %s",
                repr(e),
            )
            raise e

    def select_dropdown_value(
            self,
            locator: Union[str, WebElement],
            explicit_wait: int = None,
            visible_text: str = None,
            value: str = None,
            index: int = None,
    ) -> None:
        """Select a value from a dropdown. This method works for elements with
        the "select" tag.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().select_dropdown_value("xpath=//*[@name='dropdown']", visible_text='text')
            >> CafeXWeb().select_dropdown_value("xpath=//*[@name='dropdown']", value='text')
            >> CafeXWeb().select_dropdown_value("xpath=//*[@name='dropdown']", index=1)

        Args:
            locator: A string representing the locator in a fixed format which is, locator_type=locator.
                     For example: id=username or xpath=.//*[@id='username']
            explicit_wait: An integer representing the explicit wait time (in seconds) for the particular element.
            visible_text: A string representing the text to be selected from the dropdown.
            value: A string representing the value to be selected from the dropdown.
            index: An integer representing the index of the value to be selected from the dropdown.

        Returns:
            None
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            select_web_element = Select(self.get_clickable_web_element(locator, explicit_wait))

            if visible_text:
                select_web_element.select_by_visible_text(visible_text)
            if value:
                select_web_element.select_by_value(value)
            if index is not None:
                select_web_element.select_by_index(index)
            if not (visible_text or value or index is not None):
                raise Exception(
                    "Please provide a valid argument to select the value from the dropdown."
                )
        except Exception as e:
            self.logger.exception(
                "Exception in select_dropdown_value method. Exception Details: %s", repr(e)
            )
            raise e

    def get_selected_dropdown_values(
            self,
            locator: Union[str, WebElement],
            explicit_wait: int = None,
            first_selected_option: bool = False,
            all_selected_options: bool = False,
            options: bool = False,
    ) -> Union[str, List[str]]:
        """Get the selected value(s) from a dropdown. This method works for
        elements with the "select" tag.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().get_selected_dropdown_values("xpath=//*[@name='dropdown']", first_selected_option=True)

        Args:
            locator: A string representing the locator in a fixed format which is, locator_type=locator.
                     For example: id=username or xpath=.//*[@id='username']
            explicit_wait: An integer representing the explicit wait time (in seconds) for the particular element.
            first_selected_option: A boolean to get the first selected option from the dropdown.
            all_selected_options: A boolean to get all selected options from the dropdown.
            options: A boolean to get all options from the dropdown.

        Returns:
            A string or list of strings representing the selected value(s) from the dropdown.
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            select_web_element = Select(self.get_clickable_web_element(locator, explicit_wait))

            if first_selected_option:
                return select_web_element.first_selected_option.text
            if all_selected_options:
                return [option.text for option in select_web_element.all_selected_options]
            if options:
                return [option.text for option in select_web_element.options]

            raise Exception(
                "Please provide a valid argument to get the selected value from the dropdown."
            )
        except Exception as e:
            self.logger.exception(
                "Exception in get_selected_dropdown_values method. Exception Details: %s", repr(e)
            )
            raise e

    def deselect_dropdown_value(
            self,
            locator: Union[str, WebElement],
            explicit_wait: int = None,
            visible_text: str = None,
            value: str = None,
            index: int = None,
            deselect_all: bool = False,
    ) -> None:
        """Deselect a value from a multiselect dropdown. This method works for
        elements with the "select" tag and supports multiselect options.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().deselect_dropdown_value("xpath=//*[@name='dropdown']", value="option1")

        Args:
            locator: A string representing the locator in a fixed format which is, locator_type=locator.
                     For example: id=username or xpath=.//*[@id='username']
            explicit_wait: An integer representing the explicit wait time (in seconds) for the particular element.
            visible_text: A string representing the text to be deselected from the dropdown.
            value: A string representing the value to be deselected from the dropdown.
            index: An integer representing the index of the value to be deselected from the dropdown.
            deselect_all: A boolean to deselect all the values from the dropdown.

        Returns:
            None
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            select_web_element = Select(self.get_clickable_web_element(locator, explicit_wait))

            if deselect_all:
                select_web_element.deselect_all()
            if visible_text:
                select_web_element.deselect_by_visible_text(visible_text)
            if value:
                select_web_element.deselect_by_value(value)
            if index is not None:
                select_web_element.deselect_by_index(index)
            if not (deselect_all or visible_text or value or index is not None):
                raise Exception(
                    "Please provide a valid argument to deselect the value from the dropdown."
                )
        except Exception as e:
            self.logger.exception(
                "Exception in deselect_dropdown_value method. Exception Details: %s", repr(e)
            )
            raise e

    def find_relative_element(
            self,
            by,
            value: str,
            relative_by: str,
            relative_element: Union[str, WebElement] = None,
            explicit_wait: int = None,
    ):
        """Finds an element relative to another element.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().find_relative_element(By.NAME, "btnK", "below", search_box)
            >> CafeXWeb().find_relative_element(By.NAME, "btnK", "near", search_box, distance=50)

        Args:
            by: Locator strategy for the target element (e.g., By.NAME, By.XPATH).
            value: Locator value for the target element.
            relative_by: Relative position method (e.g., below, above, to_left_of, to_right_of, near).
            relative_element: The reference WebElement or locator.
            explicit_wait: The explicit wait time (in seconds) for the particular element.

        Returns:
            The located WebElement.
        """
        try:
            relative_element = self.get_web_element(relative_element, explicit_wait)
            if relative_by == "below":
                return self.driver.find_element(locate_with(by, value).below(relative_element))
            elif relative_by == "above":
                return self.driver.find_element(locate_with(by, value).above(relative_element))
            elif relative_by == "to_left_of":
                return self.driver.find_element(locate_with(by, value).to_left_of(relative_element))
            elif relative_by == "to_right_of":
                return self.driver.find_element(
                    locate_with(by, value).to_right_of(relative_element)
                )
            elif relative_by == "near":
                return self.driver.find_element(locate_with(by, value).near(relative_element))
        except Exception as e:
            self.logger.exception(
                "Exception in find_relative_element method. Exception Details: %s", repr(e)
            )
            raise e
