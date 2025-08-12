import os

import pytest
from selenium.webdriver.common.by import By
from cafex_ui.web_client.web_driver_factory import WebDriverFactory
from cafex_ui import CafeXWeb
from test_project.cafex_sandbox_project.features.forms.ui_methods.internet_page_locators import InternetPage

web_config = InternetPage()


# If you don't want to use cafex browserstack driver you can create driver like below
# please pass the browserstack credentials in the create_driver method and run_on_browserstack as True

# if you specify ui_web marker then cafex itself create the driver with the capabilities mentioned in
# config.yml file
@pytest.fixture
def browser():
    browser_options = {'projectName': 'Cafex Web Automation',
                       'buildName': 'Cafex Web Automation',
                       'sessionName': 'Cafex UI Automation', 'local': False,
                       'browserName': 'edge', 'os': 'Windows', 'osVersion': '10', 'browserVersion': '130.0'}
    driver = WebDriverFactory().create_driver(browser="chrome", run_on_browserstack=True,
                                              browserstack_capabilities=browser_options,
                                              browserstack_username=os.getenv("BROWSERSTACK_USERNAME"),
                                              browserstack_access_key=os.getenv("BROWSERSTACK_ACCESS_KEY")
                                              )
    yield driver
    driver.quit()


@pytest.mark.ui_web
def test_add_remove_elements():
    CafeXWeb().navigate("https://the-internet.herokuapp.com/")
    CafeXWeb().click(locator=web_config.add_or_remove_elements_link, explicit_wait=20)
    CafeXWeb().click(locator=web_config.add_element_button, explicit_wait=20)
    delete_button = CafeXWeb().get_web_element(web_config.delete_element_button)
    assert delete_button.is_displayed()


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
