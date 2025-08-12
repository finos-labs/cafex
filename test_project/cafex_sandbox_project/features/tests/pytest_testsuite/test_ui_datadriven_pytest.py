import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

from cafex_ui import CafeXWeb
from test_project.cafex_sandbox_project.features.forms.ui_methods\
    .internet_page_locators import InternetPage

web_config = InternetPage()


@pytest.fixture
def browser():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()


@pytest.mark.parametrize("link_locator, header_locator, expected_header_text", [
    (web_config.a_or_b_testing_link, web_config.a_or_b_testing_header, "A/B"),
    (web_config.add_or_remove_elements_link, web_config.add_or_remove_elements_header, "Add/Remove Elements"),
    (web_config.form_authentication_link, web_config.form_authentication_header, "Login Page")
])
@pytest.mark.ui_web
def test_internet_page_links(link_locator, header_locator, expected_header_text):
    CafeXWeb().navigate("https://the-internet.herokuapp.com/")
    CafeXWeb().click(locator=link_locator, explicit_wait=20)
    CafeXWeb().is_element_displayed(locator=header_locator, explicit_wait=20)
    header = CafeXWeb().get_web_element(locator=header_locator)
    assert expected_header_text in header.text


@pytest.mark.parametrize("username, password", [
    ("tomsmith", "SuperSecretPassword!"),
    ("invalid_user", "invalid_password")
])
@pytest.mark.ui_web
def test_form_authentication(username, password):
    CafeXWeb().navigate("https://the-internet.herokuapp.com/")
    CafeXWeb().click(locator=web_config.form_authentication_link, explicit_wait=20)
    CafeXWeb().is_element_displayed(locator=web_config.form_username, explicit_wait=20)
    CafeXWeb().is_element_displayed(locator=web_config.form_password, explicit_wait=20)
    CafeXWeb().type(locator=web_config.form_username, text=username)
    CafeXWeb().type(locator=web_config.form_password, text=password)
    CafeXWeb().click(locator=web_config.form_login_button, explicit_wait=20)
    flash_message = CafeXWeb().get_web_element(locator=web_config.flash_message)
    assert flash_message.is_displayed()


@pytest.mark.parametrize("action", ["add", "remove"])
def test_add_remove_elements(browser, action):
    browser.get("https://the-internet.herokuapp.com/")
    browser.find_element(By.XPATH, "//a[normalize-space()='Add/Remove Elements']").click()
    if action == "add":
        browser.find_element(By.XPATH, "//button[normalize-space()='Add Element']").click()
        delete_button = browser.find_element(By.XPATH, "//button[normalize-space()='Delete']")
        assert delete_button.is_displayed()
    elif action == "remove":
        browser.find_element(By.XPATH, "//button[normalize-space()='Add Element']").click()
        delete_button = browser.find_element(By.XPATH, "//button[normalize-space()='Delete']")
        delete_button.click()
        assert not browser.find_elements(By.XPATH, "//button[normalize-space()='Delete']")
