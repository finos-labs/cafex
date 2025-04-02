import time
import requests
from browserstack.local import Local
from requests.auth import HTTPBasicAuth
from selenium import webdriver
from cafex_core.logging.logger_ import CoreLogger
from cafex_core.utils.core_security import Security, decrypt_password, use_secured_password


class UISecurity(Security):
    """Class for UI automation security-related functionality."""

    def __init__(self):
        self.logger_class = CoreLogger(name=__name__)
        self.logger = self.logger_class.get_logger()

    def build_appium_url(
            self,
            mobile_platform: str,
            browserstack_username: str = None,
            browserstack_access_key: str = None,
            ip_address: str = None,
            port_number: str = None,
    ) -> str:
        """Builds the Appium URL."""

        try:
            if mobile_platform.lower() == "browserstack":
                return f"http://{browserstack_username}:{browserstack_access_key}@hub-cloud.browserstack.com/wd/hub"
            return f"http://{ip_address}:{port_number}/wd/hub"
        except Exception as e:
            self.logger.exception("Error in build_appium_url method: %s", e)
            return ""

    @staticmethod
    def start_bs_local(bs_local_obj: Local, local_args: dict) -> Local | Exception:
        """Starts BrowserStack Local Server."""
        try:
            if use_secured_password():
                local_args["key"] = decrypt_password(local_args["key"])
            for attempt in range(3):
                try:
                    bs_local_obj.start(**local_args)
                    if bs_local_obj.isRunning():
                        print("BrowserStack Local started successfully.")
                        return bs_local_obj
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(5)  # Wait for 5 seconds before retrying
            raise Exception("Failed to start BrowserStack Local after maximum retries.")
        except Exception as e:
            print("Error in start_browserstack_local method-->" + str(e))
            raise e

    @staticmethod
    def mobile_upload_browserstack_app(
            browserstack_user_name: str,
            browserstack_access_key: str,
            appcenter_app_url: str,
            custom_id: str,
            browserstack_url: str,
    ) -> requests.Response | Exception:
        """This method sends a request to the BrowserStack API to upload a
        mobile app.

        Args:
            browserstack_user_name (str): The username for accessing the BrowserStack API.
            browserstack_access_key (str): The access key for accessing the BrowserStack API.
            appcenter_app_url (str): The URL of the app to be uploaded.
            custom_id (str): The custom ID for the app.
            browserstack_url (str): The URL of the BrowserStack API.

        Returns:
            response: The response from the BrowserStack API.
        """
        try:
            if use_secured_password():
                browserstack_access_key = decrypt_password(browserstack_access_key)
            payload = {
                "data": '{"url": "' + appcenter_app_url + '","custom_id": "' + custom_id + '"}'
            }
            response = requests.post(
                browserstack_url,
                auth=HTTPBasicAuth(browserstack_user_name, browserstack_access_key),
                data=payload,
                timeout=30,
            )
            return response
        except Exception as e:
            print("Error in uploading mobile broswerstack app-->" + str(e))
            return e

    @staticmethod
    def get_browser_stack_devices_list(browserstack_user_name: str, browserstack_access_key: str, browserstack_url: str
                                       ):
        """This method sends a request to the BrowserStack API and retrieves
        the response.

        Args:
            browserstack_user_name (str): The username for accessing the BrowserStack API.
            browserstack_access_key (str): The access key for accessing the BrowserStack API.
            browserstack_url (str): The URL of the BrowserStack API.

        Returns:
            response: The response from the BrowserStack API in JSON format.
        """
        try:
            response = requests.get(
                browserstack_url,
                auth=HTTPBasicAuth(browserstack_user_name, browserstack_access_key),
                timeout=30,
            )
            return response
        except Exception as e:
            print("Error in getting browser stack available devices list-->" + str(e))
            return e

    def create_browserstack_webdriver(
            self, browserstack_user_name: str, browserstack_access_key: str, options: object | list
    ) -> tuple | None:
        try:
            browserstack_url = self.__create_browserstack_url(
                browserstack_user_name, browserstack_access_key
            )
            browserstack_webdriver = webdriver.Remote(
                command_executor=browserstack_url, options=options
            )
            response = browserstack_webdriver.execute_script(
                'browserstack_executor: {"action": "getSessionDetails"}'
            )
            return browserstack_webdriver, response
        except Exception as e:
            print("Error in creating browserstack webdriver--> " + str(e))
            return None

    @staticmethod
    def __create_browserstack_url(user_name: str, access_key: str) -> str | None:
        try:
            if use_secured_password():
                access_key = decrypt_password(access_key)
            browserstack_url = f"https://{user_name}:{access_key}@hub-cloud.browserstack.com/wd/hub"
            return browserstack_url
        except Exception as e:
            print("Error in creating browserstack webdriver--> " + str(e))
            return None

    @staticmethod
    def get_browser_stack_browsers_list(
            browserstack_url: str,
            browserstack_user_name: str,
            browserstack_access_key: str,
    ) -> requests.Response | Exception:
        """This method sends a request to the BrowserStack API and retrieves
        the response.

        Args:
            browserstack_user_name (str): The username for accessing the BrowserStack API.
            browserstack_access_key (str): The access key for accessing the BrowserStack API.
            browserstack_url (str): The URL of the BrowserStack API.

        Returns:
            response: The response from the BrowserStack API in JSON format.
        """
        try:
            if use_secured_password():
                browserstack_access_key = decrypt_password(browserstack_access_key)
            response = requests.get(
                browserstack_url,
                auth=HTTPBasicAuth(browserstack_user_name, browserstack_access_key),
                timeout=30,
            )
            return response
        except Exception as e:
            print("Error in getting browser stack available browsers list-->" + str(e))
            return e
