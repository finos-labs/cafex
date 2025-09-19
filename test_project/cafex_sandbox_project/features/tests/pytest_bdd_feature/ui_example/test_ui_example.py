from pytest_bdd import given, when, then, scenario, parsers

from test_project.cafex_sandbox_project.features.forms.ui_methods.internet_page import InternetPageMethods

internet_page = InternetPageMethods()


@scenario('ui_example.feature', 'Check for a specific element on the homepage')
def test_check_for_a_specific_element():
    print("Scenario: Check for a specific element on the homepage")


@scenario('ui_example.feature', 'Navigate to the "A/B Testing" page and verify its content')
def test_navigate_to_a_or_b_testing():
    print("Scenario: Navigate to the A/B Testing page and verify its content")


@scenario('ui_example.feature', 'Navigate to the "Add/Remove Elements" page and add an element')
def test_navigate_to_add_or_remove_elements():
    print("Scenario: Navigate to the Add/Remove Elements page and add an element")


@scenario('ui_example.feature', 'Navigate to Form Authentication page and validate the login mechanism')
def test_navigate_to_form_auth_pages():
    print("Scenario:Navigate to Form Authentication page and validate the login mechanism")


@scenario('ui_example.feature',
          'Navigate to Form Authentication page and validate the login mechanism using config file')
def test_navigate_to_form_pages():
    print("Scenario:Navigate to Form Authentication page and validate the login mechanism using config file")


@given('the user is on the homepage')
def step_given_homepage():
    print("Given the user is on the homepage")
    assert internet_page.open_home_page()


@then(parsers.parse('the user should see the "{text}" text'))
def step_then_check_text(text):
    print("Then the user should see the text")
    assert internet_page.validate_home_page_title(text)


@when(parsers.parse('the user navigates to the "{page}" page'))
def step_when_navigate(page):
    print("When the user navigates to the page")
    assert internet_page.navigate_to_given_page(page)


@then(parsers.parse('the user should see the "{text}" particular text'))
def step_then_verify_text(text):
    print("Then the user should see the text")
    assert internet_page.validate_a_or_b_testing_header(text)


@when('the user adds an element')
def step_when_add_element():
    print("When the user adds an element")
    assert internet_page.add_element_page()


@then('the user should see the "Delete" button')
def step_then_see_delete_button():
    print("Then the user should see the Delete button")
    assert internet_page.validate_delete_button()


@when("the user navigates to the Form Authentication page")
def step_when_navigate_to_form_authentication():
    print("When the user navigates to the Form Authentication page")
    assert internet_page.navigate_to_form_authentication_page()


@when(parsers.parse('the user enters the username {username} and password {password}'))
def step_when_enter_credentials(username, password):
    print("When the user enters the username and password")
    assert internet_page.enter_credentials(username, password)


@when("the user hits the login button")
def step_when_click_login_button():
    print("When the user hits the login button")
    assert internet_page.click_login_button()


@then(parsers.parse('the user should see the message {message}'))
def step_then_login_successful(message):
    print("Then the user should be logged in successfully")
    assert internet_page.validate_flash_message(message)


@when("the user enters the credentials")
def step_when_enter_credentials():
    print("When the user enters the credentials")
    internet_page.get_credentials_from_config_file()


@then(parsers.parse('the user should see the "{message}"'))
def step_then_verify_login_message(message):
    print("Then the user should see the message")
    assert internet_page.validate_flash_message(message)
