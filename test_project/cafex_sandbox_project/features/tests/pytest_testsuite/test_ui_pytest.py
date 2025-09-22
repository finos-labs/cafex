"""
This module contains the test cases for the UI tests using pytest framework.
"""
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

from cafex import CafeXWeb
from test_project.cafex_sandbox_project.features.forms.ui_methods. \
    internet_page_locators import InternetPage

web_config = InternetPage()


@pytest.fixture
def browser():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()


@pytest.mark.ui_web
def test_internet_page_alert():
    CafeXWeb().navigate("https://the-internet.herokuapp.com/")
    CafeXWeb().execute_javascript("alert('Hello, World!');")
    assert CafeXWeb().get_alert_text(explicit_wait=10) == "Hello, World!"


@pytest.mark.ui_web
def test_delete_cookies_functionality():
    CafeXWeb().navigate("https://the-internet.herokuapp.com/")
    CafeXWeb().click(locator=web_config.add_or_remove_elements_link, explicit_wait=20)
    CafeXWeb().click(locator=web_config.add_element_button, explicit_wait=20)
    CafeXWeb().click(locator=web_config.add_element_button, explicit_wait=20)
    CafeXWeb().click(locator=web_config.delete_element_button, explicit_wait=20)
    CafeXWeb().delete_cookies("optimizelyEndUserId")
    assert CafeXWeb().get_cookie_value("optimizelyEndUserId") == "No Cookie Present"


@pytest.mark.ui_web
def test_add_remove_elements():
    CafeXWeb().navigate("https://the-internet.herokuapp.com/")
    CafeXWeb().click(locator=web_config.add_or_remove_elements_link, explicit_wait=20)
    CafeXWeb().click(locator=web_config.add_element_button, explicit_wait=20)
    delete_button = CafeXWeb().get_web_element(web_config.delete_element_button)
    assert delete_button.is_displayed()
    delete_button.click()
    assert not CafeXWeb().is_element_present(web_config.delete_element_button)


@pytest.mark.ui_web
def test_ab_testing_page():
    CafeXWeb().navigate("https://the-internet.herokuapp.com/")
    CafeXWeb().click(locator=web_config.a_or_b_testing_link, explicit_wait=20)
    header = CafeXWeb().get_web_element(web_config.a_or_b_testing_header)
    assert header.is_displayed()
    assert "A/B" in header.text


def test_add_remove_elements_with_normal_driver_creation(browser):
    browser.get("https://the-internet.herokuapp.com/")
    browser.find_element(By.XPATH, "//a[normalize-space()='Add/Remove Elements']").click()
    browser.find_element(By.XPATH, "//button[normalize-space()='Add Element']").click()
    delete_button = browser.find_element(By.XPATH, "//button[normalize-space()='Delete']")
    assert delete_button.is_displayed()
    delete_button.click()
    assert not browser.find_elements(By.XPATH, "//button[normalize-space()='Delete']")
