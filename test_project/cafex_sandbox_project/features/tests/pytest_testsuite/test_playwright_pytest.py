import pytest
from cafex_core.reporting_.step_decorator import step
from test_project.cafex_sandbox_project.features.forms.playwright.login_form import LoginForm, CheckboxForm

login_form = LoginForm()
checkbox_form = CheckboxForm()

@pytest.mark.playwright_web
def test_login_success():
    """Test successful login using Playwright form methods."""
    @step("Given the user is on the login page")
    def step_given_login_page():
        login_form.goto_login()

    @step('When the user enters the username "tomsmith"')
    def step_when_enter_username():
        login_form.enter_username("tomsmith")

    @step('And the user enters the password "SuperSecretPassword!"')
    def step_when_enter_password():
        login_form.enter_password("SuperSecretPassword!")

    @step('And the user clicks the login button')
    def step_when_click_login():
        login_form.click_login()

    @step('Then the user should see the message "You logged into a secure area!"')
    def step_then_validate_flash():
        assert "You logged into a secure area!" in login_form.get_flash_message()

    step_given_login_page()
    step_when_enter_username()
    step_when_enter_password()
    step_when_click_login()
    step_then_validate_flash()

@pytest.mark.playwright_web
def test_checkbox_interaction():
    """Test checkbox page interactions using Playwright form methods."""
    @step("Given the user is on the checkboxes page")
    def step_given_checkboxes_page():
        checkbox_form.goto_checkboxes()

    @step('Then the page title should contain "The Internet"')
    def step_then_title():
        assert "The Internet" in checkbox_form.get_title()

    @step('And the first checkbox should be unchecked')
    def step_then_first_unchecked():
        assert not checkbox_form.is_checkbox1_checked()

    @step('And the second checkbox should be checked')
    def step_then_second_checked():
        assert checkbox_form.is_checkbox2_checked()

    @step('When the user clicks the first checkbox')
    def step_when_click_first():
        checkbox_form.click_checkbox1()

    @step('Then the first checkbox should be checked')
    def step_then_first_checked():
        assert checkbox_form.is_checkbox1_checked()

    @step('When the user clicks the second checkbox')
    def step_when_click_second():
        checkbox_form.click_checkbox2()

    @step('Then the second checkbox should be unchecked')
    def step_then_second_unchecked():
        assert not checkbox_form.is_checkbox2_checked()

    step_given_checkboxes_page()
    step_then_title()
    step_then_first_unchecked()
    step_then_second_checked()
    step_when_click_first()
    step_then_first_checked()
    step_when_click_second()
    step_then_second_unchecked()

