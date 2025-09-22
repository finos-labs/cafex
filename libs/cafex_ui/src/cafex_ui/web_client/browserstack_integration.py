import json
import os
import random

from browserstack.local import Local
from selenium.webdriver.remote.webdriver import WebDriver
from cafex_core.logging.logger_ import CoreLogger
from cafex_core.utils.exceptions import CoreExceptions
from cafex_ui.cafex_ui_config_utils import WebConfigUtils
from cafex_ui.ui_security import UISecurity


class BrowserStackDriverFactory:
    def __init__(self) -> None:
        self.exceptions = CoreExceptions()
        self.web_driver: "WebDriver" = None
        self.bs_local = None
        self.logger = CoreLogger(name=__name__).get_logger()
        self.obj_config = WebConfigUtils()

    def create_browserstack_webdriver(
            self, browserstack_username: str, browserstack_access_key: str,
            browser_options: object | list
    ) -> WebDriver | Exception:
        """Create a remote webdriver session on BrowserStack.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().create_browserstack_webdriver([{"browser": "chrome"}])

        Args:
            browserstack_username: The username for BrowserStack.
            browserstack_access_key: The access key for BrowserStack.
            browser_options: A dictionary containing browser options.

        Returns:
            WebDriver
        """
        try:
            self._start_browserstack_local(browserstack_access_key)
            self.web_driver, response = UISecurity().create_browserstack_webdriver(
                browserstack_username, browserstack_access_key, browser_options
            )
            details = json.loads(response)
            self.logger.info("Browserstack execution results: %s", details["public_url"])
            return self.web_driver
        except Exception as e:
            custom_exception_message = (
                "Exception in create_browserstack_webdriver method. Exception Details: %s",
                repr(e),
            )
            self.exceptions.raise_generic_exception(
                message=str(custom_exception_message),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            raise e

    def _get_data_from_browserstack_config_file(self) -> dict:
        """Get data from the BrowserStack configuration file."""

        browserstack_config_file = self.obj_config.base_config.get(
            "browserstack_config_file", "browserstack.yml"
        )
        bs_config = self.obj_config.read_browserstack_web_yml_file(browserstack_config_file)
        return bs_config

    def _start_browserstack_local(self, browserstack_access_key: str) -> None:
        """Start Browserstack Local Server if the execution is happening on
        BrowserStack and 'local' is set as 'true' in the configuration file.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().start_browserstack_local(browserstack_access_key="your_access_key")

        Args:
            browserstack_access_key: The access key for BrowserStack.
        Returns:
            None
        """
        try:
            self.bs_local = Local()
            use_browserstack_local = False
            bs_config = self._get_data_from_browserstack_config_file()
            if "bstack:options" in bs_config.keys():
                if "local" in bs_config["bstack:options"]:
                    if str(bs_config["bstack:options"]["local"]).lower() == "true":
                        use_browserstack_local = True
            if use_browserstack_local and not self.bs_local.isRunning():
                bs_local_args = {
                    "key": browserstack_access_key,
                    "force": "true",
                    "onlyAutomate": "true",
                }
                self.bs_local = UISecurity().start_bs_local(self.bs_local, bs_local_args)
        except Exception as e:
            self.logger.exception("Error in start_browserstack_local method--> %s", str(e))

    def stop_browserstack_local(self):
        """Stop the Browserstack Local Server if it is running.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> CafeXWeb().stop_browserstack_local()

        Returns:
            None
        """
        try:
            if self.bs_local is not None:
                if self.bs_local.isRunning():
                    self.bs_local.stop()
        except Exception as e:
            self.logger.exception("Error in stop_browserstack_local method--> %s", str(e))

    def get_browser_stack_browsers_list(
            self, browserstack_username: str, browserstack_access_key: str
    ) -> list | Exception:
        """Retrieve a list of browsers from BrowserStack.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> browsers_list = CafeXWeb().get_browser_stack_browsers_list()

        Args:
            browserstack_username: The username for BrowserStack.
            browserstack_access_key: The access key for BrowserStack.

        Returns:
            List
        """
        try:
            browserstack_api_endpoint = "https://api.browserstack.com/automate/browsers.json"
            bs_config = self._get_data_from_browserstack_config_file()
            resultant_list = []
            if "use_random_browsers" in bs_config.keys():
                response = UISecurity().get_browser_stack_browsers_list(
                    browserstack_api_endpoint, browserstack_username, browserstack_access_key
                )
                if response.status_code == 200:
                    browsers_list = response.json()
                    for browser in browsers_list:
                        browser_dict = {
                            "browserName": browser["browser"].lower(),
                            "bstack:options": {
                                "os": browser["os"],
                                "osVersion": browser["os_version"],
                                "browserVersion": browser["browser_version"],
                            },
                        }
                        resultant_list.append(browser_dict)
                return resultant_list
            return resultant_list
        except Exception as e:
            self.logger.exception("Error in get_browser_stack_browsers_list method--> %s", str(e))
            return e

    def get_device_list_from_json(self, file_name: str) -> list:
        """Retrieve a list of devices from a JSON file.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> devices_list = CafeXWeb().get_device_list_from_json("devices.json")

        Args:
            file_name: The file name which contains the list of devices.

        Returns:
            list: A list of devices with their names converted to lowercase.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            IOError: If there is an error while reading the file.
            Exception: If the file is not in JSON format or any other exception occurs.
        """
        try:
            details = []
            if str(file_name).endswith(".json"):
                res_file_path = (
                        self.obj_config.get_browserstack_web_configuration_directory_path()
                        + os.sep
                        + file_name
                )
                with open(res_file_path, encoding="utf-8") as json_file:
                    json_data = json.load(json_file)
                for browser in json_data:
                    browser["browserName"] = browser["browserName"].lower()
                    details.append(browser)
                return details
            raise Exception("Given file is not in json format")
        except FileNotFoundError as exc:
            raise FileNotFoundError("The specified file does not exist.") from exc
        except IOError as exc:
            raise IOError("Error while reading the file.") from exc
        except Exception as e:
            self.logger.exception("Could not get device list from JSON--> %s", str(e))
            raise e

    def get_available_browsers(
            self, browsers_file: str, browserstack_username: str, browserstack_access_key: str
    ) -> dict:
        """Retrieve a randomly selected browser from a list of common browsers.

        Examples:
            >> from cafex_ui import CafeXWeb
            >> available_browser = CafeXWeb().get_available_browsers("browsers.json")

        Args:
            browsers_file: The file name which contains the list of browsers.
            browserstack_username: The username for BrowserStack.
            browserstack_access_key: The access key for BrowserStack.

        Returns:
            dict: A randomly selected available browser from the common devices list.

        Raises:
            ValueError: If no common browsers are found between client usage and BrowserStack lists.
        """
        try:
            client_intended_browsers = self.get_device_list_from_json(browsers_file)
            browser_stack_browsers = self.get_browser_stack_browsers_list(
                browserstack_username, browserstack_access_key
            )
            common_browsers = [
                browser for browser in browser_stack_browsers if browser in client_intended_browsers
            ]
            if not common_browsers:
                raise ValueError(
                    "No common browsers found between user list and BrowserStack list."
                )
            random_browser = random.choice(common_browsers)
            self.logger.info("Randomly selected browser: %s", random_browser)
            return random_browser
        except Exception as e:
            print("Error in get_available_browsers method--> %s", str(e))
            raise e
