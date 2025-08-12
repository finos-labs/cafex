import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from cafex_ui.web_client.web_client_actions.base_web_client_actions import WebClientActions
from cafex_ui.web_client.web_driver_factory import WebDriverFactory
from web_configuration import WebUnitTestConfiguration as web_config
import pandas as pd


@pytest.fixture(scope="function")
def web_driver_setup():
    """Sets up and tears down the web driver for test methods."""
    chrome_prefs = {
        "download.prompt_for_download": False,  # Do not prompt for download
        "download.directory_upgrade": True,  # Allow directory upgrade
        "safebrowsing.enabled": False  # Enable safe browsing
    }
    driver = WebDriverFactory().create_driver(browser="chrome", capabilities={"se:downloadsEnabled": True},
                                              chrome_preferences=chrome_prefs)
    yield driver  # Provide the driver to test methods
    driver.quit()


@pytest.fixture(scope="function")
def web_client_actions(web_driver_setup):  # Fixture depends on mobile_driver_setup
    """Provides a WebClientActions instance with the driver."""
    return WebClientActions(web_driver=web_driver_setup, default_explicit_wait=30, default_implicit_wait=5)


@pytest.mark.usefixtures("web_driver_setup")
class TestWebClientActions:

    def test_web_client_actions_session_id(self, web_client_actions):
        assert web_client_actions.driver.session_id is not None

    def test_web_driver_session_id(self, web_driver_setup):
        assert web_driver_setup.session_id is not None

    def test_get_title_method(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.google_search_url)
            web_client_actions.click(locator=web_config.google_doodles_button, explicit_wait=20)
            title = web_client_actions.get_title(explicit_wait=20)
            assert "Google Doodles - Google’s Search Logo Changes for Every Occasion" == title
            web_client_actions.navigate_back()
            assert "Google" == web_client_actions.get_title(expected_title="Google", explicit_wait=20)
            assert "Google" == web_client_actions.get_title(expected_title="Internet", explicit_wait=20)
        except Exception as e:
            print(e)

    def test_get_current_url(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.google_search_url)
            web_client_actions.click(locator=web_config.google_doodles_button, explicit_wait=20)
            assert web_config.google_doodles_page == web_client_actions.get_current_url(explicit_wait=10)
            web_client_actions.navigate_back()
            assert web_config.google_search_url == web_client_actions.get_current_url(explicit_wait=10)
            assert web_client_actions.get_current_url(expected_url=
                                                      web_config.google_search_url, explicit_wait=10) \
                   == web_config.google_search_url
            web_client_actions.get_current_url(expected_url=20)
        except Exception as e:
            print("Error occurred while testing get_current_url method: ", e)

    def test_navigate_method(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url, explicit_wait=10)
            assert "The Internet" == web_client_actions.get_title(explicit_wait=10)
            web_client_actions.navigate("http://www.invalid.com")
        except Exception as e:
            print("Error occurred while testing navigate method: ", e)

    def test_go_to_url(self, web_client_actions):
        try:
            web_client_actions.go_to_url(endpoint="dynamic_content", base_url=web_config.internet_page_url)
            assert web_client_actions.is_element_present(locator=web_config.dynamic_content_header,
                                                         explicit_wait=10)
            web_client_actions.navigate(web_config.internet_page_url)
            web_client_actions.go_to_url(endpoint="download")
        except Exception as e:
            print("Error occurred while testing go_to_url method: ", e)

    def test_navigate_forward(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            web_client_actions.click(locator=web_config.add_or_remove_elements_link, explicit_wait=20)
            web_client_actions.navigate_back()
            web_client_actions.navigate_forward()
            assert web_client_actions.is_element_present(locator=web_config.add_or_remove_elements_header)
            web_client_actions.navigate_forward("invalid")
        except Exception as e:
            print("Error occurred while testing navigate_forward method: ", e)

    def test_navigate_back(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            web_client_actions.click(locator=web_config.add_or_remove_elements_link, explicit_wait=20)
            web_client_actions.navigate_back()
            assert web_client_actions.is_element_present(locator=web_config.home_page_header)
            web_client_actions.navigate_back("invalid")
        except Exception as e:
            print("Error occurred while testing navigate_back method: ", e)

    def test_wait_for_page_readyState(self, web_client_actions):
        web_client_actions.navigate(web_config.internet_page_url)
        web_client_actions.wait_for_page_readyState()
        assert "The Internet" == web_client_actions.get_title(explicit_wait=10)

    def test_switch_to_last_open_window(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.windows_page_link)
            web_client_actions.click(locator=web_config.windows_click_here_link, explicit_wait=20)
            web_client_actions.switch_to_last_open_window()
            assert "New Window" == web_client_actions.get_title(explicit_wait=20)
            main_window_handle = web_client_actions.driver.current_window_handle
            all_window_handles = web_client_actions.driver.window_handles
            for handle in all_window_handles:
                if handle != main_window_handle:
                    web_client_actions.driver.switch_to.window(handle)
                    web_client_actions.driver.close()
            web_client_actions.driver.switch_to.window(main_window_handle)
            web_client_actions.driver.close()
            web_client_actions.switch_to_last_open_window()
        except Exception as e:
            print("Error occurred while testing switch_to_last_open_window method: ", e)

    def test_switch_to_window(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.windows_page_link)
            handle = web_client_actions.get_current_window_handle()
            main_window_handle = web_client_actions.driver.current_window_handle
            web_client_actions.click(locator=web_config.windows_click_here_link, explicit_wait=20)
            web_client_actions.switch_to_window(title="New Window")
            assert "New Window" == web_client_actions.get_title(explicit_wait=20)
            web_client_actions.switch_to_window(window_handle=handle)
            assert "The Internet" == web_client_actions.get_title(explicit_wait=20)
            web_client_actions.switch_to_window(new_window=True)
            web_client_actions.switch_to_window(new_tab=True)
            print(web_client_actions.get_all_window_handles())
            all_window_handles = web_client_actions.driver.window_handles

            for handle in all_window_handles:
                if handle != main_window_handle:
                    web_client_actions.driver.switch_to.window(handle)
                    web_client_actions.driver.close()

            web_client_actions.driver.switch_to.window(main_window_handle)
            web_client_actions.switch_to_window(title="Internet")
            web_client_actions.driver.close()
            web_client_actions.switch_to_window()
        except Exception as e:
            print("Error occurred while testing switch_to_window method: ", e)

    def test_get_all_window_handles(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.windows_page_link)
            web_client_actions.click(locator=web_config.windows_click_here_link, explicit_wait=20)
            assert len(web_client_actions.get_all_window_handles()) == 2
            web_client_actions.driver.close()
            web_client_actions.driver.close()
            web_client_actions.get_all_window_handles()
        except Exception as e:
            print("Error occurred while testing get_all_window_handles method: ", e)

    def test_get_current_window_handle(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            web_client_actions.click(locator=web_config.mutiple_windows_link, explicit_wait=20)
            web_client_actions.click(locator=web_config.windows_click_here_link, explicit_wait=20)
            assert web_client_actions.get_current_window_handle() == web_client_actions.driver.current_window_handle
            web_client_actions.driver.close()
            web_client_actions.get_current_window_handle()
        except Exception as e:
            print("Error occurred while testing get_current_window_handle method: ", e)

    def test_switch_to_default_content(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            web_client_actions.click(locator=web_config.frames_link, explicit_wait=20)
            web_client_actions.click(locator=web_config.iframe_link, explicit_wait=20)
            web_client_actions.switch_to_frame('mce_0_ifr')
            web_client_actions.switch_to_default_content()
            assert web_client_actions.is_element_present(
                locator=web_config.iframe_header_check, explicit_wait=20)
            web_client_actions.driver.close()
            web_client_actions.switch_to_default_content()
        except Exception as e:
            print("Error occurred while testing switch_to_default_content method: ", e)

    def test_switch_to_frame(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            web_client_actions.click(locator=web_config.frames_link, explicit_wait=20)
            web_client_actions.click(locator=web_config.iframe_link, explicit_wait=20)
            web_client_actions.switch_to_frame('mce_0_ifr')
            assert web_client_actions.is_element_present(locator=web_config.iframe_body, explicit_wait=20)
            web_client_actions.switch_to_frame('invalid')
        except Exception as e:
            print("Error occurred while testing switch_to_frame method: ", e)

    def test_accept_alert(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            web_client_actions.click(locator=web_config.javascript_alerts_link, explicit_wait=20)
            web_client_actions.click(locator=web_config.javascript_alerts_button, explicit_wait=20)
            web_client_actions.accept_alert(explicit_wait=20)
            assert web_client_actions.get_web_element(locator=web_config.javascript_result, explicit_wait=20).text \
                   == "You successfully clicked an alert"
            web_client_actions.accept_alert(explicit_wait="invalid")
        except Exception as e:
            print("Error occurred while testing accept_alert method: ", e)

    def test_dismiss_alert(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            web_client_actions.click(locator=web_config.javascript_alerts_link)
            web_client_actions.click(locator=web_config.javascript_alerts_confirm_button)
            web_client_actions.dismiss_alert()
            assert web_client_actions.get_web_element(locator=web_config.javascript_result).text \
                   == "You clicked: Cancel"
            web_client_actions.dismiss_alert(explicit_wait="invalid")
        except Exception as e:
            print("Error occurred while testing dismiss_alert method: ", e)

    def test_send_keys_to_alert(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            web_client_actions.click(locator=web_config.javascript_alerts_link, explicit_wait=20)
            web_client_actions.click(locator=web_config.javascript_alerts_prompt_button, explicit_wait=20)
            web_client_actions.send_keys_to_alert("Hello, World!", explicit_wait=20)
            web_client_actions.accept_alert(explicit_wait=20)
            assert web_client_actions.get_web_element(locator=web_config.javascript_result, explicit_wait=20).text \
                   == "You entered: Hello, World!"
            web_client_actions.send_keys_to_alert("Hello, World!", explicit_wait="invalid")
        except Exception as e:
            print("Error occurred while testing send_keys_to_alert method: ", e)

    def test_get_alert_text(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            web_client_actions.click(locator=web_config.javascript_alerts_link, explicit_wait=20)
            web_client_actions.click(locator=web_config.javascript_alerts_button, explicit_wait=20)
            assert "I am a JS Alert" == web_client_actions.get_alert_text(explicit_wait=20)
            web_client_actions.accept_alert(explicit_wait=20)
            web_client_actions.get_alert_text(explicit_wait="invalid")
        except Exception as e:
            print("Error occurred while testing get_alert_text method: ", e)

    def test_check_cookies(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            web_client_actions.click(locator=web_config.add_or_remove_elements_link, explicit_wait=20)
            web_client_actions.click(locator=web_config.add_element_button, explicit_wait=20)
            web_client_actions.click(locator=web_config.add_element_button, explicit_wait=20)
            web_client_actions.click(locator=web_config.delete_element_button, explicit_wait=20)
            cookie_list = ["optimizelyEndUserId", "optimizelyBuckets", "optimizelySegments"]
            cookie_data = web_client_actions.return_cookie_list()
            assert web_client_actions.check_cookies(cookie_list, cookie_data)
            cookies_to_search = ["cookie1"]
            complete_cookie_data = None  # This will cause an exception
            with pytest.raises(TypeError):
                web_client_actions.check_cookies(cookies_to_search, complete_cookie_data)
        except Exception as e:
            print("Error occurred while testing check_cookies method: ", e)

    def test_return_cookie_list(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            web_client_actions.click(locator=web_config.add_or_remove_elements_link, explicit_wait=20)
            web_client_actions.click(locator=web_config.add_element_button, explicit_wait=20)
            web_client_actions.click(locator=web_config.add_element_button, explicit_wait=20)
            web_client_actions.click(locator=web_config.delete_element_button, explicit_wait=20)
            cookies = web_client_actions.return_cookie_list()
            assert len(cookies) > 0
            web_client_actions.driver.close()
            web_client_actions.return_cookie_list()
        except Exception as e:
            print("Error occurred while testing return_cookie_list method: ", e)

    def test_get_cookie_value(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            web_client_actions.click(locator=web_config.add_or_remove_elements_link, explicit_wait=20)
            web_client_actions.click(locator=web_config.add_element_button, explicit_wait=20)
            web_client_actions.click(locator=web_config.add_element_button, explicit_wait=20)
            web_client_actions.click(locator=web_config.delete_element_button, explicit_wait=20)
            cookie_value = web_client_actions.get_cookie_value(cookie_name="optimizelyEndUserId")
            assert cookie_value is not None
            assert cookie_value != "No Cookie Present"
            web_client_actions.driver.close()
            web_client_actions.get_cookie_value(cookie_name="cookie1")
        except Exception as e:
            print("Error occurred while testing get_cookie_value method: ", e)

    def test_add_cookie(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            cookie = {"name": "cookie_name", "value": "cookie_value"}
            web_client_actions.add_cookie(cookie)
            assert web_client_actions.get_cookie_value("cookie_name") == "cookie_value"
            web_client_actions.delete_cookies("cookie_name")
            assert web_client_actions.get_cookie_value("cookie_name") == "No Cookie Present"
            web_client_actions.driver.close()
            web_client_actions.add_cookie(cookie)
        except Exception as e:
            print("Error occurred while testing add_cookie method: ", e)

    def test_delete_cookies(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            web_client_actions.click(locator=web_config.add_or_remove_elements_link, explicit_wait=20)
            web_client_actions.click(locator=web_config.add_element_button, explicit_wait=20)
            web_client_actions.click(locator=web_config.add_element_button, explicit_wait=20)
            web_client_actions.click(locator=web_config.delete_element_button, explicit_wait=20)
            web_client_actions.delete_cookies("optimizelyEndUserId")
            assert web_client_actions.get_cookie_value("optimizelyEndUserId") == "No Cookie Present"
            web_client_actions.delete_cookies(all_cookies=True)
            assert len(web_client_actions.return_cookie_list()) == 0
            web_client_actions.driver.close()
            web_client_actions.delete_cookies("optimizelyEndUserId")
        except Exception as e:
            print("Error occurred while testing delete_cookies method: ", e)

    def test_click_method(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            web_client_actions.click(locator=web_config.add_or_remove_elements_link)
            web_client_actions.click(locator=web_config.add_element_button, explicit_wait=20)
            assert web_client_actions.is_element_present(locator=web_config.add_or_remove_elements_header,
                                                         explicit_wait=20)
            web_client_actions.driver.close()
            web_client_actions.click(locator="xpath=invalid", explicit_wait="invalid")
        except Exception as e:
            print("Error occurred while testing click method: ", e)

    def test_type_method(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            web_client_actions.click(locator=web_config.form_authentication_link)
            web_client_actions.type(locator=web_config.form_username, text="smithjohn", click_before_type=False)
            web_client_actions.type(locator=web_config.form_password, text="SuperSecretPassword!", explicit_wait=20)
            if web_client_actions.get_web_element(locator=web_config.form_password, explicit_wait=20).get_attribute(
                    "value") \
                    == "smithjohn":
                web_client_actions.type(locator=web_config.form_username, text="tomsmith", clear=True, explicit_wait=20)
                web_client_actions.type(locator=web_config.form_password, text="SuperSecretPassword!", clear=True,
                                        explicit_wait=20)
                web_client_actions.click(locator=web_config.form_login_button, explicit_wait=30)
                if web_client_actions.is_element_present(locator=web_config.flash_message, explicit_wait=30):
                    assert "You logged into a secure area!" in web_client_actions.get_web_element(
                        locator=web_config.flash_message, explicit_wait=30).text
            web_client_actions.type(locator=web_config.form_username, text="smithjohn", clear=True, explicit_wait=20)
            web_client_actions.driver.close()
            web_client_actions.type(locator=web_config.form_username, text="smithjohn", clear=True, explicit_wait=20)
        except Exception as e:
            print("Error occurred while testing type method: ", e)


    def test_execute_javascript_method(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            web_client_actions.execute_javascript("alert('Hello, World!');")
            assert web_client_actions.get_alert_text(explicit_wait=10) == "Hello, World!"
            web_client_actions.accept_alert(explicit_wait=10)
            web_client_actions.driver.close()
            web_client_actions.execute_javascript("alert('Hello, World!');")
        except Exception as e:
            print("Error occurred while testing execute_javascript method: ", e)

    def test_is_element_present_method(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            element_present_by_locator = web_client_actions.is_element_present(
                locator=web_config.add_or_remove_elements_link, explicit_wait=10)
            assert element_present_by_locator, "Element not present using locator string"
            web_element = web_client_actions.get_web_element(
                locator=web_config.add_or_remove_elements_link, explicit_wait=10)
            element_present_by_web_element = web_client_actions.is_element_present(
                locator=web_element, explicit_wait=10)
            assert element_present_by_web_element, "Element not present using web element"
            web_client_actions.navigate(web_config.google_search_url)
            locator = "//*[@accessibility id='input']"
            element_present_by_xpath = web_client_actions.is_element_present(
                locator=locator, explicit_wait=10)
            assert not element_present_by_xpath, "Element present using xpath"
        except Exception as e:
            print("Error occurred while testing is_element_present method: ", e)

    def test_is_element_displayed_method(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.google_search_url)
            locator = "//*[@accessibility id='input']"
            element_present_by_xpath = web_client_actions.is_element_displayed(
                locator=locator, explicit_wait=10)
            assert not element_present_by_xpath, "Element present using xpath"
            web_client_actions.navigate(web_config.internet_page_url)
            element = web_client_actions.get_web_element(locator=web_config.add_or_remove_elements_link,
                                                         explicit_wait=10)
            assert web_client_actions.is_element_displayed(element, explicit_wait=10)
            web_client_actions.click(locator=web_config.hovers_link, explicit_wait=30)
            if not web_client_actions.is_element_displayed(
                    locator=web_config.hover_fig_caption_1):
                web_client_actions.click(locator=web_config.hover_user_1, explicit_wait=30)
                assert web_client_actions.is_element_displayed(
                    locator=web_config.hover_fig_caption_1,
                    explicit_wait=30)
            web_client_actions.navigate(web_config.google_search_url)
            locator = "//*[@accessibility id='input']"
            element_present_by_xpath = web_client_actions.is_element_present(
                locator=locator, explicit_wait=10)
            assert not element_present_by_xpath, "Element present using xpath"
        except Exception as e:
            print("Error occurred while testing is_element_displayed method: ", e)

    def test_set_implicit_wait(self, web_client_actions):
        try:
            web_client_actions.set_implicit_wait(wait_time=10)
            web_client_actions.driver.close()
            web_client_actions.set_implicit_wait(wait_time=10)
        except Exception as e:
            print("Error occurred while testing set_implicit_wait method: ", e)

    def test_get_web_element_method(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            if isinstance(web_client_actions.get_web_element(locator=web_config.add_or_remove_elements_link,
                                                             explicit_wait=10), WebElement):
                assert web_client_actions.get_web_element(locator=web_config.add_or_remove_elements_link,
                                                          explicit_wait=10).text == "Add/Remove Elements"
            web_element = web_client_actions.get_web_element(
                locator=web_config.add_or_remove_elements_link, explicit_wait=10)
            element_present_by_web_element = web_client_actions.is_element_present(
                locator=web_element, explicit_wait=10)
            assert element_present_by_web_element, "Element not present using web element"
            web_element1 = web_client_actions.get_web_element(
                locator=web_element, explicit_wait=10)
            element_present_by_web_element = web_client_actions.is_element_present(
                locator=web_element1, explicit_wait=10)
            assert element_present_by_web_element, "Element not present using web element"
            web_client_actions.driver.close()
            web_client_actions.get_web_element(locator="xpath=invalid", explicit_wait="invalid")
        except Exception as e:
            print("Error occurred while testing get_web_element method: ", e)

    def test_get_clickable_web_element(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            web_client_actions.click(locator=web_config.add_or_remove_elements_link)
            web_element = web_client_actions.get_clickable_web_element(
                locator=web_config.add_element_button, explicit_wait=20)
            web_element1 = web_client_actions.get_clickable_web_element(
                locator=web_element, explicit_wait=20)
            web_element1.click()
            assert web_client_actions.is_element_present(locator=web_config.add_element_button,
                                                         explicit_wait=20)
            web_client_actions.driver.close()
            web_client_actions.get_clickable_web_element(locator="xpath=invalid", explicit_wait="invalid")
        except Exception as e:
            print("Error occurred while testing get_clickable_web_element method: ", e)

    def test_get_web_elements_method(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            web_elements = web_client_actions.get_web_elements(locator=web_config.to_get_all_links, explicit_wait=10)
            assert len(web_elements) > 0
            web_client_actions.driver.close()
            web_client_actions.get_web_elements(locator="xpath=invalid", explicit_wait="invalid")
        except Exception as e:
            print("Error occurred while testing get_web_elements method: ", e)

    def test_wait_for_invisibility_web_element(self, web_client_actions):
        try:
            web_client_actions.navigate(f"{web_config.internet_page_url}dynamic_loading/1", explicit_wait=20)
            web_client_actions.click(locator=web_config.dynamic_loading_start_button, explicit_wait=20)
            web_client_actions.wait_for_invisibility_web_element(locator=web_config.dynamic_loading_invsibility_element,
                                                                 explicit_wait=20)
            assert web_client_actions.is_element_present(locator=web_config.dynamic_loading_header,
                                                         explicit_wait=20)
            web_client_actions.driver.close()
            web_client_actions.wait_for_invisibility_web_element(locator=web_config.dynamic_loading_invsibility_element,
                                                                 explicit_wait=20)
        except Exception as e:
            print("Error occurred while testing wait_for_invisibility_web_element method: ", e)

    def test_get_xpath(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            xpath = web_client_actions.get_xpath(tag="a", attribute="normalize-space()", value="Add/Remove Elements")
            assert web_client_actions.is_element_present(locator=f"xpath={xpath}", explicit_wait=10)
            xpath1 = web_client_actions.get_xpath(tag="a", value="Add/Remove Elements", index=1)
            assert web_client_actions.is_element_present(locator=f"xpath={xpath1}", explicit_wait=10)
        except Exception as e:
            print("Error occurred while testing get_xpath method: ", e)

    def test_get_attribute_value(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            web_client_actions.click(locator=web_config.add_or_remove_elements_link)
            web_client_actions.click(locator=web_config.add_element_button, explicit_wait=20)
            web_element = web_client_actions.get_web_element(locator=web_config.add_element_button_1,
                                                             explicit_wait=20)
            assert web_client_actions.get_attribute_value(locator=web_element, attribute="class") == "added-manually"
            web_client_actions.driver.close()
            assert web_client_actions.get_attribute_value(locator=web_element, attribute="class") == "added-manually"
        except Exception as e:
            print("Error occurred while testing get_attribute_value method: ", e)

    def test_get_locator_strategy(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            locator = web_config.flash_messages_locator
            locators = locator.split("=")
            locator_strategy = web_client_actions.get_locator_strategy(locators[0])
            assert locator_strategy == "xpath"
            locator = "invalid"
            web_client_actions.get_locator_strategy(locator)
        except Exception as e:
            print("Error occurred while testing get_locator_strategy method: ", e)


    def test_select_dropdown_value(self, web_client_actions):
        web_client_actions.navigate(web_config.internet_page_url)
        web_client_actions.click(locator=web_config.drop_down_link, explicit_wait=20)
        web_client_actions.select_dropdown_value(locator=web_config.dropdown_id, value="1", explicit_wait=20)
        assert web_client_actions.get_web_element(locator=web_config.dropdown_id, explicit_wait=20).get_attribute(
            "value") == "1"
        web_client_actions.select_dropdown_value(locator=web_config.dropdown_id, index=1, explicit_wait=20)
        assert web_client_actions.get_web_element(locator=web_config.dropdown_id, explicit_wait=20).get_attribute(
            "value") == "1"
        web_client_actions.select_dropdown_value(locator=web_config.dropdown_id, visible_text="Option 2",
                                                 explicit_wait=20)
        assert web_client_actions.get_web_element(locator=web_config.dropdown_id, explicit_wait=20).get_attribute(
            "value") == "2"

    def test_get_child_elements(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            web_client_actions.click(locator=web_config.add_or_remove_elements_link, explicit_wait=20)
            web_client_actions.click(locator=web_config.add_element_button, explicit_wait=20)
            web_client_actions.click(locator=web_config.add_element_button, explicit_wait=20)
            web_element = web_client_actions.get_web_element(locator=web_config.add_element_parent, explicit_wait=20)
            web_client_actions.get_child_elements(parent_locator=web_element,
                                                  search_locator=web_config.add_element_search_locator)
            web_elements = web_client_actions.get_child_elements(
                parent_locator=web_config.add_element_parent,
                search_locator=web_config.add_element_search_locator)
            assert len(web_elements) == 2
            web_client_actions.get_child_elements(search_locator=web_config.add_element_search_locator)
            web_client_actions.get_child_elements(parent_locator=web_config.add_element_parent)
            web_client_actions.driver.close()
            web_client_actions.get_child_elements(
                parent_locator=web_config.add_element_parent,
                search_locator=web_config.add_element_search_locator)
        except Exception as e:
            print("Error occurred while testing get_child_elements method: ", e)

    def test_highlight_web_element(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            web_element = web_client_actions.get_web_element(locator=web_config.add_or_remove_elements_link,
                                                             explicit_wait=20)
            web_client_actions.highlight_web_element(web_element, highlight_time=5)
            web_client_actions.driver.close()
            web_client_actions.highlight_web_element(web_element, highlight_time=5)
        except Exception as e:
            print("Error occurred while testing highlight_web_element method: ", e)

    def test_deselect_dropdown_value(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.w3schools_multiselect_page,
                                        explicit_wait=40)
            web_client_actions.switch_to_frame("iframeResult", explicit_wait=40)
            web_client_actions.select_dropdown_value(locator=web_config.dropdown_xpath, visible_text="Volvo",
                                                     explicit_wait=20)
            web_client_actions.select_dropdown_value(locator=web_config.dropdown_xpath, visible_text="Audi")
            web_client_actions.deselect_dropdown_value(locator=web_config.dropdown_xpath, visible_text="Audi")
            web_client_actions.deselect_dropdown_value(locator=web_config.dropdown_xpath, value="volvo")
            assert not web_client_actions.get_web_element(
                locator=web_config.dropdown_option_1).is_selected()
            web_client_actions.select_dropdown_value(locator=web_config.dropdown_xpath, visible_text="Volvo",
                                                     explicit_wait=20)
            web_client_actions.select_dropdown_value(locator=web_config.dropdown_xpath, visible_text="Audi")
            web_client_actions.deselect_dropdown_value(locator=web_config.dropdown_xpath, deselect_all=True)
            assert not web_client_actions.get_web_element(
                locator=web_config.dropdown_option_1).is_selected()
            web_client_actions.deselect_dropdown_value(locator=web_config.dropdown_xpath, index=1)
            web_client_actions.deselect_dropdown_value(locator=web_config.dropdown_xpath)
        except Exception as e:
            print("Error occurred while testing deselect_dropdown_value method: ", e)

    def test_select_dropdown_value_method(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.w3schools_multiselect_page,
                                        explicit_wait=60)
            web_client_actions.switch_to_frame("iframeResult", explicit_wait=40)
            web_client_actions.select_dropdown_value(locator=web_config.dropdown_xpath, visible_text="Volvo",
                                                     explicit_wait=20)
            web_client_actions.select_dropdown_value(locator=web_config.dropdown_xpath, visible_text="Audi")
            assert web_client_actions.get_web_element(
                locator=web_config.dropdown_option_1).is_selected()
            web_client_actions.select_dropdown_value(locator=web_config.dropdown_xpath, value="volvo")
            assert web_client_actions.get_web_element(
                locator=web_config.dropdown_option_1).is_selected()
            web_client_actions.select_dropdown_value(locator=web_config.dropdown_xpath, index=1)
            assert web_client_actions.get_web_element(
                locator=web_config.dropdown_option_1).is_selected()
            web_client_actions.select_dropdown_value(locator=web_config.dropdown_xpath)
        except Exception as e:
            print("Error occurred while testing select_dropdown_value method: ", e)

    def test_get_selected_dropdown_values(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.w3schools_multiselect_page,
                                        explicit_wait=40)
            web_client_actions.switch_to_frame("iframeResult", explicit_wait=40)
            web_client_actions.select_dropdown_value(locator=web_config.dropdown_xpath, visible_text="Volvo",
                                                     explicit_wait=20)
            web_client_actions.select_dropdown_value(locator=web_config.dropdown_xpath, visible_text="Audi")
            selected_values = web_client_actions.get_selected_dropdown_values(locator=web_config.dropdown_xpath,
                                                                              all_selected_options=True)
            assert selected_values == ["Volvo", "Audi"]
            selected_values = web_client_actions.get_selected_dropdown_values(locator=web_config.dropdown_xpath,
                                                                              first_selected_option=True)
            assert selected_values == "Volvo"
            options = web_client_actions.get_selected_dropdown_values(locator=web_config.dropdown_xpath,
                                                                      options=True)
            assert len(options) == 4
            web_client_actions.get_selected_dropdown_values(locator=web_config.dropdown_xpath)
        except Exception as e:
            print("Error occurred while testing get_selected_dropdown_values method: ", e)
    #
    def test_find_relative_locator_method(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url)
            web_client_actions.wait_for_page_readyState()
            link = web_client_actions.get_web_element(web_config.drag_and_drop_link, explicit_wait=20)
            dropdown_link = web_client_actions.find_relative_element(By.LINK_TEXT, value="Dropdown",
                                                                     relative_by="below",
                                                                     relative_element=link)
            dropdown_link.click()
            assert web_client_actions.get_title("The Internet", explicit_wait=30) == "The Internet"
            time.sleep(40)
            web_client_actions.navigate_back(explicit_wait=20)
            assert web_client_actions.get_title() == "The Internet"

            drag_and_drop_link = web_client_actions.find_relative_element(By.LINK_TEXT, value="Drag and Drop",
                                                                          relative_by="above",
                                                                          relative_element=dropdown_link)
            drag_and_drop_link.click()
            assert web_client_actions.is_element_present(locator="xpath=//h3[normalize-space()='Drag and Drop']",
                                                         explicit_wait=20)
            web_client_actions.navigate(web_config.google_search_url, explicit_wait=20)
            store = web_client_actions.get_web_element(locator=web_config.google_store_xpath, explicit_wait=20)
            about = web_client_actions.find_relative_element(By.XPATH, value="//a[normalize-space()='About']",
                                                             relative_by="to_left_of",
                                                             relative_element=store)
            about.click()
            assert web_client_actions.get_title() == "Google - About Google, Our Culture & Company News"
            web_client_actions.navigate_back()
            store = web_client_actions.find_relative_element(By.XPATH, value="//a[normalize-space()='Store']",
                                                             relative_by="to_right_of",
                                                             relative_element=about)
            store.click()
            assert web_client_actions.get_title() == "Google Store for Google Made Devices & Accessories"
            web_client_actions.navigate("https://www.google.com")
            relative_element = web_client_actions.get_web_element(locator=web_config.google_search_textbox,
                                                                  explicit_wait=20)
            print(relative_element.text)
            result_element = web_client_actions.find_relative_element(By.NAME, value="q",
                                                                      relative_by="near",
                                                                      relative_element=relative_element)
            assert result_element is not None, "No element found near the relative element"
            assert result_element.get_attribute(
                "name") == "q", "The found element is not the expected search input field"
        except Exception as e:
            print("Error occurred while testing find_relative_locator method: ", e)

    def test_get_webtable_data_into_dataframe_without_header(self, web_client_actions):
        web_client_actions.navigate(web_config.cosmocode_page)
        expected_df = pd.DataFrame(
            [
                ["", "Afghanistan", "Kabul", "Afghani", "Dari Persian; Pashto"],
                ["", "Albania", "Tirane", "Lek", "Albanian"],
                ["", "Algeria", "Algiers", "Algerian Dinar", "Arabic; Tamazight; French"],
                ["", "Andorra", "Andorra la Vella", "Euro", "Catalan"],
            ],
            columns=["Visited", "Country", "Capital(s)", "Currency", "Primary Language(s)"]
        )
        result_df = web_client_actions.get_webtable_data_into_dataframe(web_config.countries_table_row_locator)
        assert expected_df.shape[1] == result_df.shape[1]

    def test_get_webtable_data_into_dataframe_with_header(self, web_client_actions):
        web_client_actions.navigate(web_config.tutorialspoint_page)
        expected_df = pd.DataFrame(
            {
                "First Name": ["Cierra", "Alden", "Kierra", "Alden", "Kierra"],
                "Last Name": ["Vega", "Cantrell", "Gentry", "Cantrell", "Gentry"],
                "Age": [39, 45, 29, 45, 29],
                "Email": ["cierra@example.com", "alden@example.com", "kierra@example.com", "alden@example.com",
                          "kierra@example.com"],
                "Salary": [10000, 12000, 2000, 12000, 2000],
                "Department": ["Insurance", "Compliance", "Legal", "Compliance", "Legal"],
                "Action": ["", "", "", "", ""]
            }
        )
        result_df = web_client_actions.get_webtable_data_into_dataframe(web_config.tutorialspoint_page_row_locator,
                                                                        pstr_header_locator=web_config.tutorialspoint_page_headers_locator
                                                                        )
        assert expected_df.shape[1] == result_df.shape[1]

    def test_fetch_data_from_dataframe(self, web_client_actions):
        web_client_actions.navigate(web_config.tutorialspoint_page)
        df = web_client_actions.get_webtable_data_into_dataframe(web_config.tutorialspoint_page_row_locator)
        result = web_client_actions.fetch_data_from_dataframe(1, 0, df)
        assert result == "Alden"

    def test_webtable_header_into_list(self, web_client_actions):
        web_client_actions.navigate(web_config.tutorialspoint_page)
        expected_headers = ["First Name", "Last Name", "Age", "Email", "Salary", "Department", "Action"]
        headers = web_client_actions.webtable_header_into_list(web_config.tutorialspoint_page_headers_locator)
        assert headers == expected_headers

    def test_check_stale_element_exception(self, web_client_actions):
        web_client_actions.navigate(web_config.windows_page_link)
        result = web_client_actions.check_stale_element_exception(web_config.windows_click_here_link)
        assert result

    def test_scroll_height(self, web_client_actions):
        web_client_actions.navigate(web_config.internet_page_url)
        web_client_actions.scroll("height", value=476)
        scroll_position = web_client_actions.execute_javascript("return window.pageYOffset;")
        assert scroll_position == 476

    def test_scroll_bottom(self, web_client_actions):
        web_client_actions.navigate(web_config.internet_page_url)
        web_client_actions.scroll("bottom")
        scroll_position = web_client_actions.execute_javascript("return window.pageYOffset;")
        page_height = web_client_actions.execute_javascript("return document.body.scrollHeight;")
        assert scroll_position <= page_height

    def test_scroll_infinite(self, web_client_actions):
        web_client_actions.navigate(f"{web_config.internet_page_url}infinite_scroll")
        web_client_actions.scroll("infinite", scroll_pause_time=1)
        scroll_position = web_client_actions.execute_javascript("return window.pageYOffset;")
        assert scroll_position >= 0

    def test_scroll_web_element_by_locator(self, web_client_actions):
        web_client_actions.navigate(web_config.internet_page_url)
        web_client_actions.scroll("web_element", locator=web_config.elemental_selenium_link)
        element = web_client_actions.get_web_element(web_config.elemental_selenium_link)
        assert element.is_displayed()

    def test_search_broken_links(self, web_client_actions):
        web_client_actions.navigate(web_config.broken_images_link)
        broken_links = web_client_actions.search_broken_links()
        assert broken_links == 2

    def test_browser_logs(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.javascript_error_page_link)
            logs = web_client_actions.get_browser_logs()
            assert "https://the-internet.herokuapp.com/javascript_error 6:51 Uncaught TypeError: " \
                   "Cannot read properties of undefined (reading 'xyz')" in logs
            web_client_actions.navigate("https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Errors")
            print(web_client_actions.get_browser_logs())
            logs1 = web_client_actions.get_browser_logs("info")
            print(logs1)
            logs2 = web_client_actions.get_browser_logs("warning")
            print(logs2)
            logs3 = web_client_actions.get_browser_logs("error")
            print(logs3)
        except Exception as e:
            print("Error occurred while testing browser_logs method: ", e)

    def test_get_webtable_data_into_list(self, web_client_actions):
        try:
            web_client_actions.navigate(web_config.tutorialspoint_page)
            expected_list = [['Cierra', 'Vega', '39', 'cierra@example.com', '10000', 'Insurance', ''],
                             ['Alden', 'Cantrell', '45', 'alden@example.com', '12000', 'Compliance', ''],
                             ['Kierra', 'Gentry', '29', 'kierra@example.com', '2000', 'Legal', ''],
                             ['Alden', 'Cantrell', '45', 'alden@example.com', '12000', 'Compliance', ''],
                             ['Kierra', 'Gentry', '29', 'kierra@example.com', '2000', 'Legal', '']]
            result_list = web_client_actions.get_webtable_all_data_into_list(web_config.tutorialspoint_page_row_locator)
            assert expected_list == result_list
            result = web_client_actions.get_webtable_all_data_into_list(web_config.tutorialspoint_page_row_locator,
                                                                        pstr_text_to_search="Alden")
            assert result is not None
            web_client_actions.get_webtable_all_data_into_list(
                    web_config.tutorialspoint_page_row_locator,
                    pstr_text_to_search="invalid")
        except Exception as e:
            print("Error occurred while testing get_webtable_data_into_list method: ", e)

    def test_wait_until_file_download(self, web_client_actions):
        web_client_actions.navigate("https://www.selenium.dev/downloads/")
        web_client_actions.click(locator="xpath=//a[normalize-space()='32 bit Windows IE']", explicit_wait=20)
        web_client_actions.wait_until_file_download("chrome", 120, 1)
        web_client_actions.get("chrome://downloads/")
        downloads = web_client_actions.driver.execute_script(
            """
            var items = document.querySelector('downloads-manager')
                .shadowRoot.getElementById('downloadsList').items;
            return items.map(e => e.state);
            """
        )
        assert "COMPLETE" in downloads
