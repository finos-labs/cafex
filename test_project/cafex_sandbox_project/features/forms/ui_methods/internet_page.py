import time

from cafex_core.reporting_.reporting import Reporting
from cafex_core.utils.config_utils import ConfigUtils
from cafex_core.utils.core_security import decrypt_password, use_secured_password
from cafex import CafeXWeb
from test_project.cafex_sandbox_project.features.forms.ui_methods. \
    internet_page_locators import InternetPage


class InternetPageMethods:
    """
    Description:
        |   This class contains the methods to perform the search functionality.
    """

    def __init__(self):
        self.obj_locators = InternetPage()
        self.config_obj = ConfigUtils()
        self.reporting = Reporting()

    def open_home_page(self) -> bool:
        """
        Description:
            |   This function will open the home page.
        :return: bool
        .. note::
            |   This is a generic method that can be used to open the home page.
        """
        try:
            str_url = self.config_obj.fetch_base_url()
            CafeXWeb().navigate(str_url)
            title = CafeXWeb().get_title()
            if title is not None:
                self.reporting.insert_step("Open Home Page", "Home Page is opened successfully", "Pass")
                return True
            else:
                self.reporting.insert_step("Open Home Page", "Home Page is not opened successfully", "Fail")
                return False
        except Exception as e:
            raise e

    def validate_home_page_title(self, expected_text) -> bool:
        """
        Description:
            |   This function will validate the title of the home page.
        Returns:bool

        """
        try:
            actual_text = CafeXWeb().get_web_element(self.obj_locators.home_page_header, explicit_wait=60).text
            if expected_text == actual_text:
                self.reporting.insert_step("Validate Home Page Title", "Home Page Title is validated "
                                                                       "successfully", "Pass")
                return True
            else:
                self.reporting.insert_step("Validate Home Page Title", "Home Page Title is not validated ", "Fail")
                return False
        except Exception as e:
            raise e

    def navigate_to_given_page(self, page_name) -> bool:
        """
        Description:
            |   This function will navigate to the A/B Testing page.
        :param page_name: str
        :return: bool
        """
        try:
            if page_name == "A/B Testing":
                link_name = CafeXWeb().get_web_element(self.obj_locators.a_or_b_testing_link).text
                CafeXWeb().click(self.obj_locators.a_or_b_testing_link)
            else:
                link_name = CafeXWeb().get_web_element(self.obj_locators.add_or_remove_elements_link).text
                CafeXWeb().click(self.obj_locators.add_or_remove_elements_link)
            if link_name == page_name:
                self.reporting.insert_step(f"Navigate to {page_name} Page", f"{page_name} Page is opened successfully",
                                           "Pass")
                return True
            else:
                self.reporting.insert_step(f"Navigate to {page_name} Page",
                                           f"{page_name} Page is not opened successfully",
                                           "Fail")
                return False
        except Exception as e:
            raise e

    def validate_a_or_b_testing_header(self, header) -> bool:
        """
        Description:
            |   This function will navigate to the A/B Testing page.
        Args:
            header: str
        Returns: bool
        """
        try:
            link_name = CafeXWeb().get_web_element(self.obj_locators.a_or_b_testing_header).text
            if header in link_name:
                self.reporting.insert_step("Navigate to A/B Testing Page",
                                           "A/B Testing Page is opened successfully",
                                           "Pass")
                return True
            else:
                self.reporting.insert_step("Navigate to A/B Testing Page",
                                           "A/B Testing Page is not opened successfully",
                                           "Fail")
                return False
        except Exception as e:
            raise e

    def navigate_to_add_or_remove_page(self, page_name) -> bool:
        """
        Description:
            |   This function will navigate to the Add/Remove Elements page.
        :param page_name: str
        :return: bool
        """
        try:
            link_name = CafeXWeb().get_web_element(self.obj_locators.add_or_remove_elements_link).text
            CafeXWeb().click(self.obj_locators.a_or_b_testing_link)
            if link_name == page_name:
                self.reporting.insert_step("Navigate to Add/Remove Elements Page",
                                           "Add/Remove Elements Page is opened successfully",
                                           "Pass")
                return True
            else:
                self.reporting.insert_step("Navigate to Add/Remove Elements Page",
                                           "Add/Remove Elements Page is not opened successfully",
                                           "Fail")
                return False
        except Exception as e:
            raise e

    def add_element_page(self) -> bool:
        """
        Description:
            |   This function will add an element to the Add/Remove Elements page.
        :return: bool
        """
        try:
            CafeXWeb().click(self.obj_locators.add_element_button)
            time.sleep(5)
            if CafeXWeb().is_element_present(self.obj_locators.add_element_search_locator):
                self.reporting.insert_step("Add Element", "Element is added successfully", "Pass")
                return True
            else:
                self.reporting.insert_step("Add Element", "Element is not added successfully", "Fail")
                return False
        except Exception as e:
            raise e

    def validate_delete_button(self):
        """
        Description:
            |   This function will validate the presence of the delete button on the Add/Remove Elements page.
        """
        try:
            if CafeXWeb().is_element_present(self.obj_locators.delete_element_button):
                self.reporting.insert_step("Validate Delete Button", "Delete Button is present", "Pass")
                return True
            else:
                self.reporting.insert_step("Validate Delete Button", "Delete Button is not present", "Fail")
                return False
        except Exception as e:
            raise e

    def navigate_to_form_authentication_page(self):
        """
        Description:
            |   This function will navigate to the Form Authentication page.
        """
        try:
            CafeXWeb().click(self.obj_locators.form_authentication_link)
            if CafeXWeb().is_element_present(self.obj_locators.form_authentication_header):
                self.reporting.insert_step("Navigate to Form Authentication Page", "Form Authentication Page is opened",
                                           "Pass")
                return True
            else:
                self.reporting.insert_step("Navigate to Form Authentication Page",
                                           "Form Authentication Page is not opened", "Fail")
                return False
        except Exception as e:
            raise e

    def enter_credentials(self, username, password):
        """
        Description:
            |   This function will enter the username and password on the Form Authentication page.
        Args:
            username: str
            password: str
        """
        try:
            CafeXWeb().type(self.obj_locators.form_username, username)
            if use_secured_password():
                password = decrypt_password(password)
            CafeXWeb().type(self.obj_locators.form_password, password)
            if CafeXWeb().is_element_present(self.obj_locators.form_login_button):
                self.reporting.insert_step("Enter Credentials", "Credentials are entered successfully", "Pass")
                return True
            else:
                self.reporting.insert_step("Enter Credentials", "Credentials are not entered successfully", "Fail")
                return False
        except Exception as e:
            raise e

    def click_login_button(self):
        """
        Description:
            |   This function will click the login button on the Form Authentication page.
        """
        try:
            CafeXWeb().click(self.obj_locators.form_login_button)
            if CafeXWeb().is_element_present(self.obj_locators.flash_message):
                self.reporting.insert_step("Click Login Button", "Login Button is clicked successfully", "Pass")
                return True
            else:
                self.reporting.insert_step("Click Login Button", "Login Button is not clicked successfully", "Fail")
                return False
        except Exception as e:
            raise e

    def validate_flash_message(self, expected_message):
        """
        Description:
            |   This function will validate the flash message on the Form Authentication page.
        Args:
            expected_message: str
        """
        try:
            actual_message = CafeXWeb().get_web_element(self.obj_locators.flash_message).text
            if expected_message in actual_message:
                self.reporting.insert_step("Validate Flash Message", "Flash Message is validated successfully", "Pass")
                return True
            else:
                self.reporting.insert_step("Validate Flash Message", "Flash Message is not validated", "Fail")
                return False
        except Exception as e:
            raise e

    def get_credentials_from_config_file(self):
        """
        Description:
            |   This function will get the credentials from the config file.
        """
        try:
            credentials = self.config_obj.fetch_login_credentials()
            self.enter_credentials(credentials[0], credentials[1])
        except Exception as e:
            raise e
