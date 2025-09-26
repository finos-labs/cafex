from pytest_bdd import given, when, then, scenario,parsers
from test_project.cafex_sandbox_project.features.forms.playwright.login_form import LoginForm, CheckboxForm


@scenario('playwright.feature', 'Validate user login')
def test_login_and_validate_secure_area():
    """Scenario to perform login and validate secure area using Playwright."""
    print("Starting test: Validate user login")

@scenario('playwright.feature', 'Validate checkbox functionality')
def test_checkbox_functionality():
    """Scenario to validate checkbox functionality using Playwright."""
    print("Starting test: Validate checkbox functionality")

@given("the browser is launched")
def launch_browser():
    print("Launching the browser...")


@when('I navigate to the login page')
def navigate_to_login_page():
    LoginForm().goto_login()


@when('I enter the username "tomsmith"')
def enter_username():
    LoginForm().enter_username("tomsmith")


@when('I enter the password "SuperSecretPassword!"')
def enter_password():
    LoginForm().enter_password("SuperSecretPassword!")


@when('I click the login button')
def click_login_button():
    LoginForm().click_login()


@then('I should see the secure area')
def validate_secure_area():
    flash_message = LoginForm().get_flash_message()
    assert "You logged into a secure area!" in flash_message, "Login validation failed"
    print("Login validation passed")

@when('I navigate to the checkboxes page')
def navigate_to_checkboxes_page():
    CheckboxForm().goto_checkboxes()


@then(parsers.cfparse('the page title should contain "{expected_title}"'))
def verify_page_title(expected_title):
    title = CheckboxForm().get_title()
    assert expected_title in title, f"Expected '{expected_title}' to be in the title, but got '{title}'"


@then('I verify the first checkbox is unchecked')
def verify_first_checkbox_unchecked():
    is_checked = CheckboxForm().is_checkbox1_checked()
    assert not is_checked, "First checkbox is checked, but expected to be unchecked"


@then('I verify the second checkbox is checked')
def verify_second_checkbox_checked():
    is_checked = CheckboxForm().is_checkbox2_checked()
    assert is_checked, "Second checkbox is not checked, but expected to be checked"


@when('I click on the first checkbox')
def click_first_checkbox():
    CheckboxForm().click_checkbox1()


@then('the first checkbox should be checked')
def verify_first_checkbox_checked():
    is_checked = CheckboxForm().is_checkbox1_checked()
    assert is_checked, "First checkbox is not checked after clicking"


@when('I click on the second checkbox')
def click_second_checkbox():
    CheckboxForm().click_checkbox2()


@then('the second checkbox should be unchecked')
def verify_second_checkbox_unchecked():
    is_checked = CheckboxForm().is_checkbox2_checked()
    assert not is_checked, "Second checkbox is still checked after clicking"
