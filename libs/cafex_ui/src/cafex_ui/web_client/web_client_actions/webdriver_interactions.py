import os
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from cafex_core.logging.logger_ import CoreLogger
from cafex_core.singletons_.session_ import SessionStore
from cafex_ui.cafex_ui_config_utils import WebConfigUtils


class WebDriverInteractions:
    """This class contains methods to perform various operations on a browser
    and its elements."""

    def __init__(
            self,
            web_driver: WebDriver = None,
            default_explicit_wait: int = None,
            default_implicit_wait: int = None,
    ):
        """Initializes WebClientActions with a driver and optional explicit
        wait.

        Args:
            web_driver: The selenium webdriver instance.
                            if not provided, it will be picked from Session Store
            default_explicit_wait: The default explicit wait time (in seconds).
                                   If not provided, it will be retrieved from ConfigUtils.
        """
        self.default_explicit_wait = default_explicit_wait or WebConfigUtils().get_explicit_wait()
        self.default_implicit_wait = default_implicit_wait or WebConfigUtils().get_implicit_wait()
        self.logger = CoreLogger(name=__name__).get_logger()
        self.driver = web_driver or SessionStore().storage.get("driver")

    def get_title(self, expected_title: str = None, explicit_wait: int = None) -> str:
        """Return the title of the browser after waiting for it to be present.

        Examples:
            >>from cafex_ui import CafeXWeb
            >>CafeXWeb().get_title()
            >>CafeXWeb().get_title("Example Title",30)
        Args:
            expected_title: A string representing the title of the page which user is expecting.
            explicit_wait: An integer representing the maximum time to wait for the title to be present (in seconds).

        Returns:
            A string representing the title of the browser.
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            if expected_title:
                WebDriverWait(self.driver, explicit_wait).until(EC.title_is(expected_title))
            else:
                WebDriverWait(self.driver, explicit_wait).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
            return self.driver.title
        except Exception as e:
            self.logger.exception("Exception in get_title method. Exception Details: %s", repr(e))
            raise e

    def get_current_url(self, expected_url: str = None, explicit_wait: int = None) -> str:
        """Return the current URL of the browser after waiting for the page to
        stop loading.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().get_current_url()
            >> CafeXWeb().get_current_url("http://example.com",30)
        Args:
            expected_url: A string representing the URL of the page which user is expecting.
            explicit_wait: An integer representing the maximum time to wait for the page to stop loading (in seconds).

        Returns:
            A string representing the current URL of the browser.
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            if expected_url:
                WebDriverWait(self.driver, explicit_wait).until(EC.url_to_be(expected_url))
            else:
                WebDriverWait(self.driver, explicit_wait).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
            return self.driver.current_url
        except Exception as e:
            self.logger.exception(
                "Exception in get_current_url method. Exception Details: %s", str(e)
            )
            raise e

    def navigate(self, url: str, explicit_wait: int = None) -> None:
        """Navigate to the given URL and wait until the page is fully loaded.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().navigate("http://example.com")

        Args:
            url: A string representing the URL to which the driver needs to be navigated to.
            explicit_wait: An integer representing the explicit wait time (in seconds) for the page to load.

        Returns:
            None
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            self.driver.get(url)
            self.wait_for_page_readyState(explicit_wait)
        except Exception as e:
            self.logger.exception("Exception in navigate method. Exception Details:", exc_info=e)
            raise e

    def go_to_url(self, endpoint: str, base_url: str = None, explicit_wait: int = None) -> None:
        """Combine the base URL and the partial URL/page URL and navigate to
        the resultant URL.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().go_to_url("/endpoint", base_url="http://example.com")
            >> CafeXWeb().web_client_actions.go_to_url("/endpoint")

        Args:
            endpoint: A string representing the partial URL which will be combined with the base URL/the platform.
            base_url: A string representing the URL of the platform.
            explicit_wait: An integer representing the explicit wait time for the page to load.

        Returns:
            None
        """
        try:
            base_url = base_url or WebConfigUtils().fetch_base_url()
            explicit_wait = explicit_wait or self.default_explicit_wait
            if base_url is None:
                raise Exception("Base URL is not provided and not found in configuration file")
            self.navigate(base_url + os.sep + endpoint)
            self.wait_for_page_readyState(explicit_wait)
        except Exception as e:
            self.logger.exception("Exception in go_to_url method. Exception Details: %s", str(e))
            raise e

    def navigate_forward(self, explicit_wait: int = None) -> None:
        """Navigate forward in the browser history.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().navigate_forward()
            >> CafeXWeb().navigate_forward(30)

        Args:
            explicit_wait: An integer representing the time to wait for the page to load.

        Returns:
            None
        """
        try:
            self.driver.forward()
            self.wait_for_page_readyState(explicit_wait)
        except Exception as e:
            self.logger.exception(
                "Exception in navigate_forward method. Exception Details: %s", str(e)
            )
            raise e

    def navigate_back(self, explicit_wait: int = None) -> None:
        """Navigate back in the browser history.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().navigate_back()
            >> CafeXWeb().navigate_back(30)
        Args:
            explicit_wait: An integer representing the time to wait for the page to load.

        Returns:
            None
        """
        try:
            self.driver.back()
            self.wait_for_page_readyState(explicit_wait)
        except Exception as e:
            self.logger.exception(
                "Exception in navigate_back method. Exception Details: ", exc_info=e
            )
            raise e

    def wait_for_page_readyState(self, explicit_wait: int = None):
        """Wait until the page's readyState is 'complete' or the specified wait
        time elapses.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().wait_for_page_readyState(30)

        Args:
            explicit_wait: An integer representing the maximum wait time in seconds.

        Returns:
            None
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            WebDriverWait(self.driver, explicit_wait).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )

        except Exception as e:
            self.logger.exception(
                "Exception in wait_for_page_readyState method. Exception Details: ", exc_info=e
            )
            raise e

    def switch_to_last_open_window(self):
        """Switch the user to the last open window.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().switch_to_last_open_window()

        Returns:
            None
        """
        try:
            list_window_handle = self.get_all_window_handles()
            pstr_last_open_window = list_window_handle[len(list_window_handle) - 1]
            self.switch_to_window(window_handle=pstr_last_open_window)
        except Exception as e:
            self.logger.exception(
                "Exception in switch_to_last_open_window method. Exception Details: %s", str(e)
            )
            raise e

    def switch_to_window(self, **kwargs):
        """Switch to window by window handle or window title.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().switch_to_window(window_handle='value of window handle')
            >> CafeXWeb().switch_to_window(title='the page title')

        Args:
            window_handle: A string representing the handle ID of the window user wants to switch to.
            title: A string representing the title of the window user wants to switch to.
            new_window: A boolean value to switch to the new window.
            new_tab: A boolean value to switch to the new tab.

        Returns:
            None
        """
        title_found = False
        try:
            if "window_handle" in kwargs:
                self.driver.switch_to.window(kwargs.get("window_handle"))
            elif "title" in kwargs:
                current_handle = self.get_current_window_handle()
                for w in self.get_all_window_handles():
                    self.driver.switch_to.window(w)
                    if self.driver.title.lower() == kwargs.get("title").lower():
                        title_found = True
                        break
                if not title_found:
                    self.driver.switch_to.window(current_handle)
                    raise "Window with the given title : " + kwargs.get("title") + " not found"
            elif "new_window" in kwargs and kwargs.get("new_window"):
                self.driver.switch_to.new_window("window")
            elif "new_tab" in kwargs and kwargs.get("new_tab"):
                self.driver.switch_to.new_window("tab")
        except Exception as e:
            self.logger.exception(
                "Exception in switch_to_window method. Exception Details: ", exc_info=e
            )
            raise e

    def get_all_window_handles(self):
        """Get all current window handles which are present.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().get_all_window_handles()

        Returns:
            A list of window handles.
        """
        try:
            return self.driver.window_handles
        except Exception as e:
            self.logger.exception(
                "Exception in get_all_window_handles method. Exception Details: %s", str(e)
            )
            raise e

    def get_current_window_handle(self):
        """Get the current window handle.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().get_current_window_handle()

        Returns:
            A string representing the current window handle.
        """
        try:
            return self.driver.current_window_handle
        except Exception as e:
            self.logger.exception(
                "Exception in get_current_window_handle method. Exception Details: %s", repr(e)
            )
            raise e

    def switch_to_default_content(self):
        """Switch back to the default frame.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().switch_to_default_content()

        Returns:
            None
        """
        try:
            return self.driver.switch_to.default_content()
        except Exception as e:
            self.logger.exception(
                "Exception in switch_to_default_content method. Exception Details: %s", str(e)
            )
            raise e

    def switch_to_frame(self, frame_reference, explicit_wait: int = None):
        """Switch to frame based on reference.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> web_element = CafeXWeb().get_web_element(locator="xpath=//iframe[@name='frame_name']")
            >> CafeXWeb().switch_to_frame('frame_name')
            >> CafeXWeb().switch_to_frame(1)
            >> CafeXWeb().switch_to_frame(web_element)

        Args:
            frame_reference: A string representing the locator of the frame to switch into.
            explicit_wait: An integer representing the explicit wait time (in seconds) for the frame to be available.

        Returns:
            None
        """
        try:
            return self.driver.switch_to.frame(frame_reference)
        except Exception:
            try:
                explicit_wait = explicit_wait or self.default_explicit_wait
                return WebDriverWait(self.driver, explicit_wait).until(
                    EC.frame_to_be_available_and_switch_to_it((By.ID, frame_reference))
                )
            except Exception as e:
                self.logger.exception(
                    "Exception in switch_to_frame method. Exception Details: %s", repr(e)
                )
                raise e

    def accept_alert(self, explicit_wait: int = None) -> None:
        """Accept the alert if present.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().accept_alert()
            >> CafeXWeb().accept_alert(30)

        Args:
            explicit_wait: An integer representing the explicit wait time (in seconds) for the alert to be present.

        Returns:
            None
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            WebDriverWait(self.driver, explicit_wait).until(EC.alert_is_present())
            alert_obj = self.driver.switch_to.alert
            alert_obj.accept()
        except Exception as e:
            self.logger.exception(
                "Exception in accept_alert method. Exception Details: %s", repr(e)
            )
            raise e

    def dismiss_alert(self, explicit_wait: int = None) -> None:
        """Dismiss the alert if present.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().dismiss_alert()
            >> CafeXWeb().dismiss_alert(30)

        Args:
            explicit_wait: An integer representing the explicit wait time (in seconds) for the alert to be present.

        Returns:
            None
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            WebDriverWait(self.driver, explicit_wait).until(EC.alert_is_present())
            alert_obj = self.driver.switch_to.alert
            alert_obj.dismiss()
        except Exception as e:
            self.logger.exception(
                "Exception in dismiss_alert method. Exception Details: %s", repr(e)
            )
            raise e

    def send_keys_to_alert(self, text: str = None, explicit_wait: int = None):
        """Enter the given text in the alert box if present.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().send_keys_to_alert("Sample text")
            >> CafeXWeb().send_keys_to_alert("Sample text", 30)

        Args:
            text: A string representing the text to be entered in the alert box.
            explicit_wait: An integer representing the explicit wait time (in seconds) for the alert to be present.

        Returns:
            None
        """
        try:
            current_handle = self.get_current_window_handle()
            explicit_wait = explicit_wait or self.default_explicit_wait
            WebDriverWait(self.driver, explicit_wait).until(EC.alert_is_present())
            alert_obj = self.driver.switch_to.alert
            alert_obj.send_keys(text)
            self.switch_to_window(window_handle=current_handle)
        except Exception as e:
            self.logger.exception(
                "Exception in send_text_in_alert method. Exception Details: %s", repr(e)
            )
            raise e

    def get_alert_text(self, explicit_wait: int = None):
        """Return the text of the alert if present.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().get_alert_text()
            >> CafeXWeb().get_alert_text(30)

        Args:
            explicit_wait: An integer representing the explicit wait time (in seconds) for the alert to be present.

        Returns:
            A string representing the text of the alert.
        """
        try:
            explicit_wait = explicit_wait or self.default_explicit_wait
            WebDriverWait(self.driver, explicit_wait).until(EC.alert_is_present())
            alert_obj = self.driver.switch_to.alert
            return alert_obj.text
        except Exception as e:
            self.logger.exception(
                "Exception in get_alert_text method. Exception Details: ", exc_info=e
            )
            raise e

    def check_cookies(self, cookies_to_search: list, complete_cookie_data: dict) -> bool:
        """Search the list of cookies in the current set of cookies.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> cookies_to_search = ["cookie1", "cookie2"]
            >> complete_cookie_data = {"cookie1": "value1", "cookie3": "value3"}
            >> CafeXWeb().check_cookies(cookies_to_search, complete_cookie_data)

        Args:
            cookies_to_search: List of cookies to be searched.
            complete_cookie_data: Dictionary of cookies generated for the current page.

        Returns:
            A boolean indicating whether any of the cookies to search are present in the complete cookie data.
        """
        try:
            return any(item in complete_cookie_data for item in cookies_to_search)
        except Exception as e:
            self.logger.exception(
                "Exception in check_cookies method. Exception Details: %s", repr(e)
            )
            raise e

    def return_cookie_list(self) -> dict:
        """Return the cookie list created.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().return_cookie_list()

        Returns:
            A dictionary containing the cookies.
        """
        try:
            cookies_list = self.driver.get_cookies()
            dict_cookies = {}
            for cookie in cookies_list:
                dict_cookies[cookie["name"]] = cookie["value"]
            return dict_cookies
        except Exception as e:
            self.logger.exception(
                "Exception in return_cookie_list method. Exception Details: %s", repr(e)
            )
            raise e

    def get_cookie_value(self, cookie_name: str) -> str:
        """Return the value of the cookie if present, otherwise return "No
        Cookie Present".

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().get_cookie_value("session_id")

        Args:
            cookie_name: Name of the cookie to be retrieved.

        Returns:
            A string representing the value of the cookie.
        """
        try:
            cookie = self.driver.get_cookie(cookie_name)
            if cookie is None:
                return "No Cookie Present"
            else:
                return cookie["value"]
        except Exception as e:
            self.logger.exception(
                "Exception in get_cookie_value method. Exception Details: ", exc_info=e
            )
            raise e

    def add_cookie(self, cookie: dict) -> None:
        """Add a cookie to the current session.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> cookie = {"name": "cookie_name", "value": "cookie_value"}
            >> CafeXWeb().add_cookie(cookie)

        Args:
            cookie: A dictionary containing the cookie name and value.

        Returns:
            None
        """
        try:
            self.driver.add_cookie(cookie)
        except Exception as e:
            self.logger.exception("Exception in add_cookie method. Exception Details: ", exc_info=e)
            raise e

    def delete_cookies(self, cookie_name: str = None, all_cookies: bool = False) -> None:
        """Delete the cookie from the current session.If all_cookies is True,
        it will delete all cookies.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().delete_cookies("cookie_name")

        Args:
            cookie_name: Name of the cookie to be deleted.
            all_cookies: A boolean value to delete all cookies

        Returns:
            None
        """
        try:
            if all_cookies and cookie_name is None:
                self.driver.delete_all_cookies()
            else:
                self.driver.delete_cookie(cookie_name)
        except Exception as e:
            self.logger.exception(
                "Exception in delete_cookie method. Exception Details: ", exc_info=e
            )
            raise e
