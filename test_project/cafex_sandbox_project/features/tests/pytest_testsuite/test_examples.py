import pytest
from cafex import CafeXWeb
from cafex import CafeXAPI
from cafex import CafeXDB
from test_project.cafex_sandbox_project.features.forms.ui_methods. \
    internet_page_locators import InternetPage

web_config = InternetPage()


@pytest.mark.ui_web
def test_ui_example():
    CafeXWeb().navigate("https://the-internet.herokuapp.com/")
    CafeXWeb().click(locator=web_config.add_or_remove_elements_link, explicit_wait=20)
    CafeXWeb().click(locator=web_config.add_element_button, explicit_wait=20)
    CafeXWeb().click(locator=web_config.add_element_button, explicit_wait=20)
    CafeXWeb().click(locator=web_config.delete_element_button, explicit_wait=20)
    CafeXWeb().delete_cookies("optimizelyEndUserId")
    assert CafeXWeb().get_cookie_value("optimizelyEndUserId") == "No Cookie Present"


def test_api_example():
    response = CafeXAPI().call_request("GET", "https://jsonplaceholder.typicode.com/", verify=False)
    assert response.status_code == 200
    headers = CafeXAPI().get_response_headers(response)
    assert headers is not None


def test_db_example():
    connection_object = CafeXDB().create_db_connection(database_type="mysql",
                                                       server_name="",
                                                       username="",
                                                       password="",
                                                       database_name="",
                                                       port_number=13726)
    if connection_object is not None:
        print(connection_object)
        print("Connection successful")


@pytest.mark.ui_desktop_client
def test_desktop_example():
    from cafex import CafeXDesktop
    notepad_window = CafeXDesktop().app.UntitledNotepad
    CafeXDesktop().select_menu_item(notepad_window, "Edit -> Replace")
    replace_dialog = CafeXDesktop().get_window_object(title_regex="Replace", wait_for_exists=False)
    replace_dialog.wait("ready", timeout=10)
    notepad_window.close()
