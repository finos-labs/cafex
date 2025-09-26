from cafex_core.reporting_.reporting import Reporting
from cafex_ui import CafeXWeb
from .login_locators import LoginLocators, CheckboxLocators
from cafex_core.utils.config_utils import ConfigUtils
class LoginForm:
    def __init__(self):
        self.reporting = Reporting()

    def goto_login(self):
        url=ConfigUtils().fetch_base_url()
        CafeXWeb().playwright_page.goto(url +"/login")
        self.reporting.insert_step("Navigated to login page", "Navigated to login page","Pass")

    def enter_username(self, username):
        CafeXWeb().playwright_page.locator(LoginLocators.USERNAME_INPUT).fill(username)
        self.reporting.insert_step(f"Entered username: {username}", f"Entered username: {username}","Pass")

    def enter_password(self, password):
        CafeXWeb().playwright_page.locator(LoginLocators.PASSWORD_INPUT).fill(password)
        self.reporting.insert_step("Entered password", "Entered password","Pass")

    def click_login(self):
        CafeXWeb().playwright_page.locator(LoginLocators.LOGIN_BUTTON).click()
        self.reporting.insert_step("Clicked login button", "Clicked login button","Pass")

    def get_flash_message(self):
        msg = CafeXWeb().playwright_page.locator(LoginLocators.FLASH_MESSAGE).text_content()
        self.reporting.insert_step(f"Flash message: {msg}", f"Flash message: {msg}","Pass")
        return msg

class CheckboxForm:
    def __init__(self):
        self.reporting = Reporting()

    def goto_checkboxes(self):
        url=ConfigUtils().fetch_base_url()
        CafeXWeb().playwright_page.goto(url +"/checkboxes")
        self.reporting.insert_step("Navigated to checkboxes page", "Navigated to checkboxes page","Pass")

    def get_title(self):
        title = CafeXWeb().playwright_page.title()
        self.reporting.insert_step(f"Page title: {title}", f"Page title: {title}","Pass")
        return title

    def is_checkbox1_checked(self):
        checked = CafeXWeb().playwright_page.locator(CheckboxLocators.CHECKBOX_1).is_checked()
        self.reporting.insert_step(f"Checkbox 1 checked: {checked}", f"Checkbox 1 checked: {checked}","Pass")
        return checked

    def click_checkbox1(self):
        CafeXWeb().playwright_page.locator(CheckboxLocators.CHECKBOX_1).click()
        self.reporting.insert_step("Clicked checkbox 1", "Clicked checkbox 1","Pass")

    def is_checkbox2_checked(self):
        checked = CafeXWeb().playwright_page.locator(CheckboxLocators.CHECKBOX_2).is_checked()
        self.reporting.insert_step(f"Checkbox 2 checked: {checked}", f"Checkbox 2 checked: {checked}","Pass")
        return checked

    def click_checkbox2(self):
        CafeXWeb().playwright_page.locator(CheckboxLocators.CHECKBOX_2).click()
        self.reporting.insert_step("Clicked checkbox 2", "Clicked checkbox 2","Pass")
