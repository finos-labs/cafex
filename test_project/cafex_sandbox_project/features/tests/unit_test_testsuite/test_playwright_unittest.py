import unittest
from cafex_core.reporting_.step_decorator import step
from test_project.cafex_sandbox_project.features.forms.playwright.login_form import LoginForm, CheckboxForm
import pytest

class TestPlaywrightLoginForm(unittest.TestCase):
    def setUp(self):
        self.login_form = LoginForm()
        self.checkbox_form = CheckboxForm()

    @pytest.mark.playwright_web
    @step("Test successful login using Playwright form methods.")
    def test_login_success(self):
        self.login_form.goto_login()
        self.login_form.enter_username("tomsmith")
        self.login_form.enter_password("SuperSecretPassword!")
        self.login_form.click_login()
        msg = self.login_form.get_flash_message()
        self.assertIn("You logged into a secure area!", msg)

    @pytest.mark.playwright_web
    @step("Test checkbox page interactions using Playwright form methods.")
    def test_checkbox_interaction(self):
        self.checkbox_form.goto_checkboxes()
        title = self.checkbox_form.get_title()
        self.assertIn("The Internet", title)
        self.assertFalse(self.checkbox_form.is_checkbox1_checked())
        self.assertTrue(self.checkbox_form.is_checkbox2_checked())
        self.checkbox_form.click_checkbox1()
        self.assertTrue(self.checkbox_form.is_checkbox1_checked())
        self.checkbox_form.click_checkbox2()
        self.assertFalse(self.checkbox_form.is_checkbox2_checked())

if __name__ == "__main__":
    unittest.main()

