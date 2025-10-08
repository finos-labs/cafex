import pytest
from playwright.sync_api import sync_playwright

""" This test file was generated using Playwright's codegen tool, which records browser 
interactions and outputs test code. The generated logic was then adapted and 
copied into this pytest-bassed test suite for consistency with our existing test framework.
Note: Playwright's native pytest plugin is not supported in our environment. 
Therefore, we manually manage the Playwright driver setup and teardown using a custom
pytest fixture. This ensures browser sessions are properly handled within our test runs. """

@pytest.fixture(scope="session")
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        yield page
        context.close()
        browser.close()

def test_dropdown(page):
    page.goto("http://the-internet.herokuapp.com/")
    page.get_by_role("listitem").filter(has_text="Dynamic Content").click()
    page.get_by_role("link", name="Dropdown").click()
    page.locator("#dropdown").select_option("1")

def test_login(page):
    page.goto("http://the-internet.herokuapp.com/")
    page.get_by_role("listitem").filter(has_text="Dynamic Content").click()
    page.get_by_role("link", name="Form Authentication").click()
    page.locator("#username").fill("tomsmith")
    page.locator("#password").fill("SuperSecretPassword!")
    page.get_by_role("button", name="Login").click()
    assert "You logged into a secure area!" in page.locator("#flash").inner_text()
