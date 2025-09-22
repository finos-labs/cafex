from pytest_bdd import given, when, then, scenario,parsers

from cafex_ui import CafeXWeb


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


@when('I navigate to "https://the-internet.herokuapp.com/login"')
def navigate_to_url():
    CafeXWeb().playwright_page.goto("https://the-internet.herokuapp.com/login")


@when('I enter the username "tomsmith" in the field with XPath "//input[@id=\'username\']"')
def enter_username():
    CafeXWeb().playwright_page.locator("//input[@id='username']").fill("tomsmith")


@when('I enter the password "SuperSecretPassword!" in the field with XPath "//input[@id=\'password\']"')
def enter_password():
    CafeXWeb().playwright_page.locator("//input[@id='password']").fill("SuperSecretPassword!")


@when('I click the login button with XPath "//button[@type=\'submit\']"')
def click_login_button():
    CafeXWeb().playwright_page.locator("//button[@type='submit']").click()


@then('I should see the secure area with XPath "//div[@id=\'flash\']"')
def validate_secure_area():
    flash_message = CafeXWeb().playwright_page.locator("//div[@id='flash']").text_content()
    assert "You logged into a secure area!" in flash_message, "Login validation failed"
    print("Login validation passed")

@when('I navigate to "https://the-internet.herokuapp.com/checkboxes"')
def navigate_to_checkboxes():
    CafeXWeb().playwright_page.goto("https://the-internet.herokuapp.com/checkboxes")


@then(parsers.cfparse('the page title should contain "{expected_title}"'))
def verify_page_title(expected_title):
    title = CafeXWeb().playwright_page.title()
    assert expected_title in title, f"Expected '{expected_title}' to be in the title, but got '{title}'"


@then(parsers.cfparse('I verify checkbox with XPath "{xpath}" is unchecked'))
def verify_checkbox_unchecked(xpath):
    is_checked = CafeXWeb().playwright_page.locator(xpath).is_checked()
    assert not is_checked, f"Checkbox with XPath '{xpath}' is checked, but expected to be unchecked"


@then(parsers.cfparse('I verify checkbox with XPath "{xpath}" is checked'))
def verify_checkbox_checked(xpath):
    is_checked = CafeXWeb().playwright_page.locator(xpath).is_checked()
    assert is_checked, f"Checkbox with XPath '{xpath}' is not checked, but expected to be checked"


@when(parsers.cfparse('I click on the checkbox with XPath "{xpath}"'))
def click_checkbox(xpath):
    CafeXWeb().playwright_page.locator(xpath).click()


@then(parsers.cfparse('the checkbox with XPath "{xpath}" should be checked'))
def verify_checkbox_is_checked(xpath):
    is_checked = CafeXWeb().playwright_page.locator(xpath).is_checked()
    assert is_checked, f"Checkbox with XPath '{xpath}' is not checked after clicking"


@then(parsers.cfparse('the checkbox with XPath "{xpath}" should be unchecked'))
def verify_checkbox_is_unchecked(xpath):
    is_checked = CafeXWeb().playwright_page.locator(xpath).is_checked()
    assert not is_checked, f"Checkbox with XPath '{xpath}' is still checked after clicking"
