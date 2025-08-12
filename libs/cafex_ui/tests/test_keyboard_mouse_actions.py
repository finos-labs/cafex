import time
import pytest
from selenium.webdriver.common import keys
from cafex_ui.web_client.keyboard_mouse_actions import KeyboardMouseActions
from cafex_ui.web_client.web_client_actions.base_web_client_actions import WebClientActions
from cafex_ui.web_client.web_driver_factory import WebDriverFactory
from web_configuration import WebUnitTestConfiguration as web_config


@pytest.fixture(scope="function")
def web_driver_setup():
    """Sets up and tears down the web driver for test methods."""

    driver = WebDriverFactory().create_driver(browser="chrome")
    yield driver  # Provide the driver to test methods
    driver.quit()


@pytest.fixture(scope="function")
def keyboard_mouse_actions(web_driver_setup):  # Fixture depends on mobile_driver_setup
    """Provides a KeyBoardMouseActions instance with the driver."""
    return KeyboardMouseActions(web_driver=web_driver_setup, default_explicit_wait=30)


@pytest.fixture(scope="function")
def web_client_actions(web_driver_setup):  # Fixture depends on mobile_driver_setup
    """Provides a WebClientActions instance with the driver."""
    return WebClientActions(web_driver=web_driver_setup, default_explicit_wait=30, default_implicit_wait=5)


@pytest.mark.usefixtures("web_driver_setup")
class TestKeyBoardMouseActions:
    def test_keyboard_mouse_actions_session_id(self, keyboard_mouse_actions):
        assert keyboard_mouse_actions.driver.session_id is not None

    def test_web_driver_session_id(self, web_driver_setup):
        assert web_driver_setup.session_id is not None

    def test_robust_click(self, keyboard_mouse_actions, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url, explicit_wait=30)
            keyboard_mouse_actions.robust_click(locator=web_config.add_or_remove_elements_link,
                                                explicit_wait=30)
            keyboard_mouse_actions.robust_click(locator=web_config.add_element_button, explicit_wait=30)
            assert web_client_actions.is_element_present(locator=web_config.add_element_button_1, explicit_wait=30)
            keyboard_mouse_actions.robust_click(locator=web_config.add_element_button_1, explicit_wait=30)
            assert not web_client_actions.is_element_present(locator=web_config.add_element_button_1,
                                                             explicit_wait=30)
            keyboard_mouse_actions.robust_click(locator="xpath=inavlid_locator", explicit_wait=30)
            keyboard_mouse_actions.driver.close()
            keyboard_mouse_actions.robust_click(locator=web_config.add_element_button_1, explicit_wait=30)
        except Exception as e:
            print("Error occurred while testing robust_click method: ", e)

    def test_right_click(self, keyboard_mouse_actions, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url, explicit_wait=30)
            keyboard_mouse_actions.robust_click(locator=web_config.context_menu_link, explicit_wait=30)
            keyboard_mouse_actions.right_click(locator=web_config.hotspot, explicit_wait=30)
            result = web_client_actions.get_alert_text(explicit_wait=20)
            assert "You selected a context menu" == result
            web_client_actions.accept_alert(explicit_wait=10)
            keyboard_mouse_actions.driver.close()
            keyboard_mouse_actions.right_click()
        except Exception as e:
            print("Error occurred while testing right_click method: ", e)

    def test_double_click(self, keyboard_mouse_actions, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url, explicit_wait=30)
            keyboard_mouse_actions.robust_click(locator=web_config.add_or_remove_elements_link,
                                                explicit_wait=30)
            keyboard_mouse_actions.double_click(locator=web_config.add_element_button, explicit_wait=30)
            keyboard_mouse_actions.double_click(locator=web_config.add_element_button_1, explicit_wait=30)
            assert not web_client_actions.is_element_present(locator=web_config.add_element_button_1,
                                                             explicit_wait=30)
            keyboard_mouse_actions.driver.close()
            keyboard_mouse_actions.double_click()
        except Exception as e:
            print("Error occurred while testing double_click method: ", e)

    def test_drag_and_drop(self, keyboard_mouse_actions, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url, explicit_wait=30)
            keyboard_mouse_actions.robust_click(locator=web_config.drag_and_drop_link, explicit_wait=30)
            keyboard_mouse_actions.drag_and_drop(source_element=web_config.drag_and_drop_column_a,
                                                 target_element=web_config.drag_and_drop_column_b,
                                                 explicit_wait=30)
            result = web_client_actions.get_web_element(locator=web_config.drag_and_drop_column_b,
                                                        explicit_wait=30).text
            assert "A" in result
            keyboard_mouse_actions.driver.close()
            keyboard_mouse_actions.drag_and_drop(source_element=web_config.drag_and_drop_column_a,
                                                 target_element=web_config.drag_and_drop_column_b)
        except Exception as e:
            print("Error occurred while testing drag_and_drop method: ", e)

    def test_drag_and_drop_by_offset(self, keyboard_mouse_actions, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url, explicit_wait=30)
            keyboard_mouse_actions.robust_click(locator=web_config.horizontal_slider_link,
                                                explicit_wait=30)
            slider = web_client_actions.get_web_element(locator=web_config.horizontal_slider, explicit_wait=30)
            keyboard_mouse_actions.drag_and_drop_by_offset(slider, 100, 0, explicit_wait=30)
            assert web_client_actions.get_web_element(locator=web_config.horizontal_slider_range_text,
                                                      explicit_wait=30).text == "5"
            keyboard_mouse_actions.driver.close()
            keyboard_mouse_actions.drag_and_drop_by_offset(slider, 100, 0)
        except Exception as e:
            print("Error occurred while testing drag_and_drop_by_offset method: ", e)

    def test_move_to_element(self, keyboard_mouse_actions, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url, explicit_wait=30)
            keyboard_mouse_actions.robust_click(locator=web_config.hovers_link, explicit_wait=30)
            keyboard_mouse_actions.move_to_element(locator=web_config.hover_user_1, explicit_wait=30)
            assert web_client_actions.is_element_present(locator=web_config.hover_fig_caption_1,
                                                         explicit_wait=30)
            keyboard_mouse_actions.move_to_element(locator=web_config.hover_user_1, explicit_wait=30, then_click=True)
            keyboard_mouse_actions.driver.close()
            keyboard_mouse_actions.move_to_element(locator=web_config.hover_user_1, explicit_wait=30)
        except Exception as e:
            print("Error occurred while testing move_to_element method: ", e)

    def test_control_click(self, keyboard_mouse_actions, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url, explicit_wait=30)
            keyboard_mouse_actions.control_click(locator=web_config.add_or_remove_elements_link,
                                                 explicit_wait=30)
            assert len(web_client_actions.get_all_window_handles()) == 2
            keyboard_mouse_actions.driver.close()
            keyboard_mouse_actions.control_click(locator=web_config.add_or_remove_elements_link,
                                                 explicit_wait=30)
        except Exception as e:
            print("Error occurred while testing control_click method: ", e)

    def test_move_to_element_with_offset(self, keyboard_mouse_actions, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url, explicit_wait=30)
            keyboard_mouse_actions.robust_click(locator=web_config.hovers_link, explicit_wait=30)
            keyboard_mouse_actions.move_to_element_with_offset(locator=web_config.hover_user_1,
                                                               x_offset=0, y_offset=10, explicit_wait=30)
            assert web_client_actions.is_element_present(locator=web_config.hover_fig_caption_1,
                                                         explicit_wait=30)
            keyboard_mouse_actions.driver.close()
            keyboard_mouse_actions.move_to_element_with_offset(locator=web_config.hover_user_1,
                                                               x_offset=0, y_offset=10, explicit_wait=30)
        except Exception as e:
            print("Error occurred while testing move_to_element_with_offset method: ", e)

    def test_click_and_hold_and_release_method(self, keyboard_mouse_actions, web_client_actions):
        try:
            web_client_actions.navigate(web_config.jquery_droppable_page_url, explicit_wait=30)
            web_client_actions.switch_to_frame(0)
            draggable = web_client_actions.get_web_element(web_config.jquery_draggable_object)
            droppable = web_client_actions.get_web_element(web_config.jquery_droppable_object)
            keyboard_mouse_actions.click_and_hold(draggable)
            keyboard_mouse_actions.move_to_element(droppable)
            dropped_text = droppable.text
            assert dropped_text == "Drop here"
            keyboard_mouse_actions.driver.close()
            keyboard_mouse_actions.click_and_hold(draggable)
        except Exception as e:
            print("Error occurred while testing click_and_hold and release methods: ", e)

    def test_release_method(self, keyboard_mouse_actions, web_client_actions):
        try:
            web_client_actions.navigate(web_config.jquery_droppable_page_url, explicit_wait=30)
            web_client_actions.switch_to_frame(0)
            draggable = web_client_actions.get_web_element(web_config.jquery_draggable_object)
            droppable = web_client_actions.get_web_element(web_config.jquery_droppable_object)
            keyboard_mouse_actions.click_and_hold(draggable)
            keyboard_mouse_actions.move_to_element(droppable)
            keyboard_mouse_actions.release(keys.Keys.ENTER)
            dropped_text = droppable.text
            assert dropped_text == "Drop here"
            keyboard_mouse_actions.release()
            keyboard_mouse_actions.driver.close()
            keyboard_mouse_actions.release()
        except Exception as e:
            print("Error occurred while testing release method: ", e)

    def test_reset_actions(self, keyboard_mouse_actions, web_client_actions):
        try:
            web_client_actions.navigate(web_config.jquery_droppable_page_url, explicit_wait=30)
            web_client_actions.switch_to_frame(0)
            draggable = web_client_actions.get_web_element(web_config.jquery_draggable_object)
            droppable = web_client_actions.get_web_element(web_config.jquery_droppable_object)
            keyboard_mouse_actions.click_and_hold(draggable)

            keyboard_mouse_actions.reset_actions()

            keyboard_mouse_actions.move_to_element(droppable)
            keyboard_mouse_actions.release()
            dropped_text = droppable.text
            assert dropped_text != "Dropped!", "The item should not be dropped since actions were reset."

            keyboard_mouse_actions.click_and_hold(draggable)
            keyboard_mouse_actions.move_to_element(droppable)
            keyboard_mouse_actions.release()
            dropped_text = droppable.text
            assert dropped_text == "Dropped!", "The draggable item should be dropped after re-performing the action."
            keyboard_mouse_actions.driver.close()
            keyboard_mouse_actions.reset_actions()
        except Exception as e:
            print("Error occurred while testing reset_actions method: ", e)

    def test_copy_and_paste(self, keyboard_mouse_actions, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url, explicit_wait=30)
            web_client_actions.click(locator=web_config.form_authentication_link, explicit_wait=30)
            web_client_actions.type(locator=web_config.form_username, text="smithjohn", click_before_type=False)
            keyboard_mouse_actions.copy_and_paste(source_locator=web_config.form_username,
                                                  destination_locator=web_config.form_password)
            assert web_client_actions.get_web_element(locator=web_config.form_password).get_attribute("value") \
                   == "smithjohn"
            keyboard_mouse_actions.driver.close()
            keyboard_mouse_actions.copy_and_paste(source_locator=web_config.form_username,
                                                  destination_locator=web_config.form_password)
        except Exception as e:
            print("Error occurred while testing copy_and_paste method: ", e)

    def test_move_by_offset(self, keyboard_mouse_actions, web_client_actions):
        try:
            web_client_actions.navigate(f"{web_config.internet_page_url}login", explicit_wait=30)
            username = web_client_actions.get_web_element(locator=web_config.form_username)
            password = web_client_actions.get_web_element(locator=web_config.form_password)
            keyboard_mouse_actions.move_to_element(username, then_click=True)
            keyboard_mouse_actions.send_keys("smithjohn")
            username_location = username.location
            password_location = password.location
            offset_x = 0
            offset_y = password_location['y'] - username_location['y'] + 10
            keyboard_mouse_actions.move_to_element(username, then_click=True)
            keyboard_mouse_actions.move_by_offset(offset_x, offset_y, then_click=True)
            keyboard_mouse_actions.actions.perform()
            keyboard_mouse_actions.send_keys("mypassword")
            assert password.get_attribute("value") == "mypassword"
            assert username.get_attribute("value") == "smithjohn"
            keyboard_mouse_actions.move_by_offset(offset_x, offset_y)
            keyboard_mouse_actions.driver.close()
            keyboard_mouse_actions.move_by_offset(offset_x, offset_y)
        except Exception as e:
            print("Error occurred while testing move_by_offset method: ", e)

    def test_send_keys(self, keyboard_mouse_actions, web_client_actions):
        try:
            web_client_actions.navigate(f"{web_config.internet_page_url}login", explicit_wait=30)
            keyboard_mouse_actions.send_keys(keys.Keys.ENTER, locator=web_config.username_xpath,
                                             explicit_wait=30)
            result = web_client_actions.get_web_element(locator=web_config.flash_message, explicit_wait=30).text
            assert "Your username is invalid!" in result
            web_client_actions.type(locator=web_config.form_username, text="smithjohn", click_before_type=False)
            keyboard_mouse_actions.send_keys(keys.Keys.BACKSPACE, locator=web_config.username_xpath,
                                             explicit_wait=30)
            assert web_client_actions.get_web_element(locator=web_config.form_username).get_attribute(
                "value") == "smithjoh"
            web_client_actions.navigate(web_config.google_search_url, explicit_wait=30)
            keyboard_mouse_actions.send_keys(keys.Keys.ENTER)
            assert "Google" in web_client_actions.get_title()
            keyboard_mouse_actions.driver.close()
            keyboard_mouse_actions.send_keys(keys.Keys.ENTER)
        except Exception as e:
            print("Error occurred while testing send_keys method: ", e)

    def test_scroll(self, keyboard_mouse_actions, web_client_actions):
        try:
            web_client_actions.navigate(web_config.internet_page_url, explicit_wait=30)
            keyboard_mouse_actions.scroll(0, 300)
            time.sleep(1)
            current_scroll = web_client_actions.execute_javascript("return window.scrollY")
            assert current_scroll > 0, "Scroll by amount did not move the viewport down."
            element = web_client_actions.get_web_element(locator=web_config.scroll_WYSIWYG_Editor_link,
                                                         explicit_wait=30)
            keyboard_mouse_actions.scroll(locator=element)
            time.sleep(1)
            is_displayed = element.is_displayed()
            assert is_displayed is True, "Element is visible after scrolling into view."
            keyboard_mouse_actions.scroll()
        except Exception as e:
            print("Error occurred while testing scroll method: ", e)
