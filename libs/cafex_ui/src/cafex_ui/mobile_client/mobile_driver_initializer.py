import os

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.singletons_.session_ import SessionStore
from cafex_core.utils.config_utils import ConfigUtils
from cafex_ui.mobile_client.mobile_client_actions import MobileClientActions
from cafex_ui.mobile_client.mobile_driver_factory import MobileDriverFactory
from cafex_ui.mobile_client.mobile_utils import MobileUtils


class MobileDriverInitializer:
    """Initializes and configures the mobile driver for UI tests."""

    def __init__(self):
        self.session_store = SessionStore()
        self.session_context = self.session_store.context
        self.metadata = self.session_context.metadata
        self.drivers = self.session_context.drivers
        self.config_utils = ConfigUtils()
        self.logger = CoreLogger(name=__name__).get_logger()

    def initialize_driver(self):
        """Sets up the mobile driver based on configuration settings."""
        if self.drivers.mobile_driver is None:
            mobile_os = self.config_utils.get_mobile_os()
            mobile_platform = self.config_utils.get_mobile_platform()
            desired_capabilities = self.config_utils.get_custom_desired_properties()

            if mobile_platform == "browserstack":
                self._setup_browserstack_driver(mobile_os, mobile_platform, desired_capabilities)
            else:
                self._setup_local_driver(mobile_os, mobile_platform, desired_capabilities)

        self.metadata.globals["obj_mca"] = MobileClientActions(self.drivers.mobile_driver)

    def _setup_browserstack_driver(
        self, mobile_os: str, mobile_platform: str, desired_capabilities: dict
    ) -> None:
        """Sets up the mobile driver for BrowserStack."""
        bs_user_name = self.config_utils.get_browserstack_username()
        bs_access_key = self.config_utils.get_browserstack_access_key()

        mobile_config = self.metadata.mobile_config or {}
        if mobile_config.get("use_random_devices_browserstack"):
            desired_capabilities = self._get_random_browserstack_device_caps(
                mobile_os, bs_user_name, bs_access_key, desired_capabilities
            )

        if mobile_config.get("browserstack_upload_appcenter_app"):
            desired_capabilities = self._upload_app_to_browserstack(
                mobile_os, bs_user_name, bs_access_key, desired_capabilities
            )

        self.drivers.mobile_driver = MobileDriverFactory().create_mobile_driver(
            mobile_os=mobile_os,
            mobile_platform=mobile_platform,
            capabilities_dictionary=desired_capabilities,
            browserstack_username=bs_user_name,
            browserstack_access_key=bs_access_key,
        )

    def _setup_local_driver(
        self, mobile_os: str, mobile_platform: str, desired_capabilities: dict
    ) -> None:
        """Sets up the mobile driver for local execution."""
        ip_address = self.config_utils.get_appium_ip_address(mobile_os)
        port = self.config_utils.get_appium_port_number(mobile_os)

        self.drivers.mobile_driver = MobileDriverFactory().create_mobile_driver(
            mobile_os=mobile_os,
            mobile_platform=mobile_platform,
            capabilities_dictionary=desired_capabilities,
            ip_address=ip_address,
            port_number=port,
        )

    def _get_random_browserstack_device_caps(
        self, mobile_os: str, bs_user_name: str, bs_access_key: str, desired_capabilities: dict
    ) -> dict:
        """Retrieves capabilities for a random BrowserStack device."""
        mobile_utils = MobileUtils()
        mobile_config = self.metadata.mobile_config or {}
        ios_device_json = mobile_config.get("ios_device_json", "ios_devices.json")
        android_device_json = mobile_config.get("android_device_json", "android_devices.json")
        ios_device_json_path = (
            self.config_utils.get_mobile_configuration_directory_path() + os.sep + ios_device_json
        )
        android_device_json_path = (
            self.config_utils.get_mobile_configuration_directory_path()
            + os.sep
            + android_device_json
        )

        bs_devices_url = mobile_config.get("get_browserstack_devices_url")
        random_device = mobile_utils.get_available_devices(
            mobile_os=mobile_os,
            browserstack_user_name=bs_user_name,
            browserstack_access_key=bs_access_key,
            get_browserstack_devices_url=bs_devices_url,
            ios_device_json_path=ios_device_json_path,
            android_device_json_path=android_device_json_path,
        )
        desired_capabilities["platformVersion"] = random_device["os_version"]
        desired_capabilities["deviceName"] = random_device["device"]
        return desired_capabilities

    def _upload_app_to_browserstack(
        self, mobile_os: str, bs_user_name: str, bs_access_key: str, desired_capabilities: dict
    ) -> dict:
        """Uploads the app to BrowserStack if not already uploaded."""
        mobile_utils = MobileUtils()
        mobile_config = self.metadata.mobile_config or {}
        proxy = mobile_config.get("proxy")
        if mobile_os.lower() == "ios":
            custom_app_id = mobile_config.get("uploaded_ios_app_id", "ios_app")
            appcenter_token = mobile_config.get("ios_appcenter_token")
            appcenter_url = mobile_config.get("ios_appcenter_url")
        else:
            custom_app_id = mobile_config.get("uploaded_android_app_id", "android_app")
            appcenter_token = mobile_config.get("android_appcenter_token")
            appcenter_url = mobile_config.get("android_appcenter_url")
        desired_capabilities["app"] = custom_app_id
        browserstack_url = mobile_config.get("browserstack_url")
        if not self.session_context.storage.get("browserstack_app_uploaded"):
            if mobile_utils.browserstack_upload_appcenter_app(
                appcenter_token=appcenter_token,
                appcenter_url=appcenter_url,
                browserstack_url=browserstack_url,
                browserstack_user_name=bs_user_name,
                browserstack_access_key=bs_access_key,
                custom_app_id=custom_app_id,
                proxy=proxy,
                verify_ssl=True,
            ):
                self.session_store.browserstack_app_uploaded = True
        return desired_capabilities
