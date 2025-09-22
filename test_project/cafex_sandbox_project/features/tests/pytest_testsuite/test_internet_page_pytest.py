import pytest

from cafex_core.reporting_.step_decorator import step
from test_project.cafex_sandbox_project.features.forms.\
    ui_methods.internet_page import InternetPageMethods

internet_page = InternetPageMethods()


@pytest.mark.ui_web
def test_check_for_a_specific_element():
    """Check for a specific element on the homepage."""

    @step("Given the user is on the homepage")
    def step_given_homepage():
        assert internet_page.open_home_page()

    @step('Then the user should see the "Welcome to the-internet" text')
    def step_then_check_text():
        assert internet_page.validate_home_page_title("Welcome to the-internet")

    # Execute the steps
    step_given_homepage()
    step_then_check_text()


@pytest.mark.ui_web
def test_navigate_to_a_or_b_testing():
    """Navigate to the A/B Testing page and verify its content."""

    @step("Given the user is on the homepage")
    def step_given_homepage():
        assert internet_page.open_home_page()

    @step('When the user navigates to the "A/B Testing" page')
    def step_when_navigate():
        assert internet_page.navigate_to_given_page("A/B Testing")

    @step('Then the user should see the "A/B Test Control" text')
    def step_then_verify_text():
        assert internet_page.validate_a_or_b_testing_header("A/B")

    # Execute the steps
    step_given_homepage()
    step_when_navigate()
    step_then_verify_text()


@pytest.mark.ui_web
def test_navigate_to_add_or_remove_elements():
    """Navigate to the Add/Remove Elements page and add an element."""

    @step("Given the user is on the homepage")
    def step_given_homepage():
        assert internet_page.open_home_page()

    @step('When the user navigates to the "Add/Remove Elements" page')
    def step_when_navigate():
        assert internet_page.navigate_to_given_page("Add/Remove Elements")

    @step("When the user adds an element")
    def step_when_add_element():
        assert internet_page.add_element_page()

    @step('Then the user should see the "Delete" button')
    def step_then_see_delete_button():
        assert internet_page.validate_delete_button()

    # Execute the steps
    step_given_homepage()
    step_when_navigate()
    step_when_add_element()
    step_then_see_delete_button()


@pytest.mark.ui_web
def test_navigate_to_form_auth_pages():
    """Navigate to Form Authentication page and validate the login mechanism."""

    @step("Given the user is on the homepage")
    def step_given_homepage():
        assert internet_page.open_home_page()

    @step("When the user navigates to the Form Authentication page")
    def step_when_navigate_to_form_authentication():
        assert internet_page.navigate_to_form_authentication_page()

    @step('When the user enters the username "tomsmith" and '
          'password "8GPtex4qM7BhgisF5sgR0pLL2UgHMQ93fL9Y4WxwYxWSQGFoVQKuJt4u/TW1zptVFhgg7g=="')
    def step_when_enter_credentials():
        assert internet_page.enter_credentials("tomsmith", "8GPtex4qM7BhgisF5sgR0pLL2UgHMQ93fL9Y4WxwYxWSQGFoVQKuJt4u/TW1zptVFhgg7g==")

    @step("When the user hits the login button")
    def step_when_click_login_button():
        assert internet_page.click_login_button()

    @step('Then the user should see the message "You logged into a secure area!"')
    def step_then_login_successful():
        assert internet_page.validate_flash_message("You logged into a secure area!")

    # Execute the steps
    step_given_homepage()
    step_when_navigate_to_form_authentication()
    step_when_enter_credentials()
    step_when_click_login_button()
    step_then_login_successful()


@pytest.mark.ui_web
def test_navigate_to_form_pages():
    """Navigate to Form Authentication page and validate the login mechanism using config file."""

    @step("Given the user is on the homepage")
    def step_given_homepage():
        assert internet_page.open_home_page()

    @step("When the user navigates to the Form Authentication page")
    def step_when_navigate_to_form_authentication():
        assert internet_page.navigate_to_form_authentication_page()

    @step("When the user enters the credentials")
    def step_when_enter_credentials():
        internet_page.get_credentials_from_config_file()

    @step("the user should click the login button")
    def step_when_click_login_button():
        assert internet_page.click_login_button()

    @step('Then the user should see the "You logged into a secure area!"')
    def step_then_verify_login_message():
        assert internet_page.validate_flash_message("You logged into a secure area!")

    # Execute the steps
    step_given_homepage()
    step_when_navigate_to_form_authentication()
    step_when_enter_credentials()
    step_when_click_login_button()
    step_then_verify_login_message()
