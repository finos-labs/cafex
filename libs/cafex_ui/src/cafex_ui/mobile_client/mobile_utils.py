import json
import os
import random
from typing import Any, Dict, List

import requests
from cafex_core.logging.logger_ import CoreLogger
from cafex_ui.ui_security import UISecurity


class MobileUtils:
    """Provides utility functions for mobile automation, including BrowserStack
    integration and device management."""

    def __init__(self):
        self.bs_local = None
        self.logger = CoreLogger(name=__name__).get_logger()

    def browserstack_upload_appcenter_app(
        self,
        appcenter_token: str,
        appcenter_url: str,
        browserstack_url: str,
        browserstack_user_name: str,
        browserstack_access_key: str,
        custom_app_id: str,
        proxy: str = None,
        verify_ssl: bool = True,
    ) -> bool:
        """Uploads the latest app from App Center to BrowserStack.

        Args:
            appcenter_token: App Center API token.
            appcenter_url: App Center URL for the latest release.
            browserstack_url: BrowserStack app upload URL.
            browserstack_user_name: BrowserStack username.
            browserstack_access_key: BrowserStack access key.
            custom_app_id: Custom ID for the app on BrowserStack.
            proxy: Proxy server URL (optional).
            verify_ssl: Whether to verify SSL certificates (default: True).

        Returns:
            True if the upload is successful, False otherwise.

        Raises:
            ValueError: If any of the required parameters are missing.
            Exception: If an error occurs during the upload process.
        """
        try:
            required_params = [
                appcenter_token,
                appcenter_url,
                browserstack_url,
                browserstack_user_name,
                browserstack_access_key,
                custom_app_id,
            ]
            if any(param is None for param in required_params):
                raise ValueError(
                    "Missing required parameters for BrowserStack app upload. "
                    "Please provide appcenter_token, appcenter_url, browserstack_url, "
                    "browserstack_user_name, browserstack_access_key, and custom_app_id."
                )

            headers = {
                "Content-Type": "application/json",
                "X-Api-Token": appcenter_token,
            }
            appcenter_response = requests.get(
                url=appcenter_url, headers=headers, proxies=proxy, verify=verify_ssl, timeout=30
            )

            if appcenter_response.status_code == 200:
                appcenter_json = appcenter_response.json()
                appcenter_app_url = appcenter_json["download_url"]
                bs_response = UISecurity().mobile_upload_browserstack_app(
                    browserstack_user_name=browserstack_user_name,
                    browserstack_access_key=browserstack_access_key,
                    appcenter_app_url=appcenter_app_url,
                    custom_id=custom_app_id,
                    browserstack_url=browserstack_url,
                )
                if bs_response.status_code == 200:
                    bs_json = bs_response.json()
                    self.logger.info("App uploaded to BrowserStack. Details: %s", bs_json)
                    return True

                self.logger.error(
                    "Failed to upload app to BrowserStack. Response: %s", bs_response.text
                )
                return False

            self.logger.error(
                "Failed to fetch app from App Center. Response: %s", appcenter_response.text
            )
            return False
        except ValueError as e:
            self.logger.exception(str(e))
            raise e
        except Exception as e:
            self.logger.exception("Error uploading app to BrowserStack: %s", e)
            raise e

    def get_browser_stack_device_list(
        self,
        mobile_os: str,
        browserstack_user_name: str,
        browserstack_access_key: str,
        get_browserstack_devices_url: str,
    ) -> List[Dict[str, Any]]:
        """Retrieves a list of available devices from BrowserStack.

        Args:
            mobile_os: The target mobile OS ('ios' or 'android').
            browserstack_user_name: BrowserStack username.
            browserstack_access_key: BrowserStack access key.
            get_browserstack_devices_url: BrowserStack devices API URL.

        Returns:
            A list of dictionaries, each representing a device.

        Raises:
            Exception: If an error occurs while fetching devices from BrowserStack.
        """
        try:
            bs_response = UISecurity().get_browser_stack_devices_list(
                browserstack_user_name=browserstack_user_name,
                browserstack_access_key=browserstack_access_key,
                browserstack_url=get_browserstack_devices_url,
            )
            if bs_response.status_code == 200:
                devices = bs_response.json()
                filtered_devices = [
                    {k: v for k, v in device.items() if k not in ("os", "realMobile")}
                    for device in devices
                    if device["os"] == mobile_os.lower()
                ]
                return filtered_devices

            self.logger.error(
                "Failed to fetch devices from BrowserStack. Response: %s", bs_response.text
            )
            return []
        except Exception as e:
            self.logger.exception("Error fetching devices from BrowserStack: %s", e)
            raise e

    def get_device_list_from_json(
        self, mobile_os: str, ios_device_json_path: str, android_device_json_path: str
    ) -> List[Dict[str, Any]]:
        """Reads a JSON file containing a list of devices.

        Args:
            mobile_os: The target mobile OS ('ios' or 'android').
            ios_device_json_path: Path to the JSON file for iOS devices.
            android_device_json_path: Path to the JSON file for Android devices.

        Returns:
            A list of dictionaries, each representing a device.

        Raises:
            FileNotFoundError: If the specified JSON file is not found.
            ValueError: If the file is not in JSON format.
            Exception: For any other errors during file reading.
        """
        try:
            file_path = (
                ios_device_json_path if mobile_os.lower() == "ios" else android_device_json_path
            )
            return self.get_device_list_from_file(file_path)
        except Exception as e:
            self.logger.exception("Error getting device list from JSON: %s", e)
            raise e

    def get_device_list_from_file(self, json_file_path: str) -> List[Dict[str, Any]]:
        """Reads a JSON file and returns a list of devices.

        Args:
            json_file_path (str): The path to the JSON file.

        Returns:
            A list of dictionaries, each representing a device.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            ValueError: If the given file is not in JSON format.
            Exception: For any other errors during file reading.
        """
        try:
            if not os.path.exists(json_file_path):
                raise FileNotFoundError(f"The device list file '{json_file_path}' was not found")

            if not json_file_path.endswith(".json"):
                raise ValueError("Given file is not in JSON format.")

            with open(json_file_path, "r", encoding="utf-8") as json_file:
                json_data = json.load(json_file)
            return json_data

        except (FileNotFoundError, ValueError) as e:
            self.logger.exception("Error reading device list from file: %s", e)
            raise e

        except Exception as e:
            self.logger.exception("Error reading device list from file: %s", e)
            raise e

    def get_available_devices(
        self,
        mobile_os: str,
        browserstack_user_name: str,
        browserstack_access_key: str,
        get_browserstack_devices_url: str,
        ios_device_json_path: str = None,
        android_device_json_path: str = None,
    ) -> dict:
        """Retrieves a random available device from BrowserStack, filtering by
        devices specified in local JSON files.

        Args:
            mobile_os: The target mobile OS ('ios' or 'android').
            browserstack_user_name: BrowserStack username.
            browserstack_access_key: BrowserStack access key.
            get_browserstack_devices_url: BrowserStack devices API URL.
            ios_device_json_path: Path to the JSON file for iOS devices (required if mobile_os is 'ios').
            android_device_json_path: Path to the JSON file for Android devices (required if mobile_os is 'android').

        Returns:
            A dictionary representing a randomly selected available device.

        Raises:
            ValueError: If any of the required parameters are missing or if no common devices are found.
            Exception: For any other errors while fetching devices.
        """
        try:
            required_params = [
                mobile_os,
                browserstack_user_name,
                browserstack_access_key,
                get_browserstack_devices_url,
            ]
            if any(param is None for param in required_params):
                raise ValueError(
                    "Missing required parameters: mobile_os, browserstack_user_name, browserstack_access_key, "
                    "and get_browserstack_devices_url are mandatory."
                )

            if mobile_os.lower() == "android" and android_device_json_path is None:
                raise ValueError(
                    "android_device_json_path is required when mobile_os is 'android'."
                )
            if mobile_os.lower() == "ios" and ios_device_json_path is None:
                raise ValueError("ios_device_json_path is required when mobile_os is 'ios'.")

            browser_stack_devices = self.get_browser_stack_device_list(
                mobile_os=mobile_os,
                browserstack_user_name=browserstack_user_name,
                browserstack_access_key=browserstack_access_key,
                get_browserstack_devices_url=get_browserstack_devices_url,
            )
            client_devices = self.get_device_list_from_json(
                mobile_os=mobile_os,
                ios_device_json_path=ios_device_json_path,
                android_device_json_path=android_device_json_path,
            )
            common_devices = [
                device for device in browser_stack_devices if device in client_devices
            ]

            if not common_devices:
                raise ValueError(
                    "No common devices found between client usage and BrowserStack lists."
                )

            return random.choice(common_devices)
        except Exception as e:
            self.logger.exception("Error while fetching devices: %s", e)
            raise e
