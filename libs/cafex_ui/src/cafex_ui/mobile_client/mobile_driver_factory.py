from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.common import AppiumOptions
from appium.options.ios import XCUITestOptions
from cafex_core.logging.logger_ import CoreLogger
from cafex_ui.ui_security import UISecurity


class MobileDriverFactory:
    """Handles the creation and configuration of Appium drivers for mobile
    automation."""

    def __init__(self):
        """Initializes the MobileDriverFactory with a logger."""
        self.logger = CoreLogger(name=__name__).get_logger()

    def create_mobile_driver(
        self,
        mobile_os: str,
        mobile_platform: str,
        capabilities_dictionary: dict,
        browserstack_username: str = None,
        browserstack_access_key: str = None,
        ip_address: str = None,
        port_number: int = None,
    ) -> webdriver.Remote:
        """Creates and returns an Appium driver instance.

        Args:
            mobile_os: The mobile operating system ('android' or 'ios').
            mobile_platform: The platform to run on ('simulator', 'device', 'browserstack').
            capabilities_dictionary: A dictionary of desired capabilities.
            browserstack_username: BrowserStack username (required if mobile_platform is 'browserstack').
            browserstack_access_key: BrowserStack access key (required if mobile_platform is 'browserstack').
            ip_address: Appium server IP address (required if mobile_platform is not 'browserstack').
            port_number: Appium server port number (required if mobile_platform is not 'browserstack').

        Returns:
            An instance of the Appium webdriver.

        Raises:
            TypeError: If any of the required arguments are of incorrect type.
            ValueError: If required arguments are missing based on the 'mobile_platform' or  unsupported mobile OS.
            Exception: If an error occurs during driver creation.
        """
        try:
            if not isinstance(mobile_os, str):
                raise TypeError("mobile_os must be a string.")
            if not isinstance(mobile_platform, str):
                raise TypeError("mobile_platform must be a string.")
            if not isinstance(capabilities_dictionary, dict):
                raise TypeError("capabilities_dictionary must be a dictionary.")

            if mobile_platform.lower() == "browserstack":
                if not browserstack_username or not browserstack_access_key:
                    raise ValueError(
                        "browserstack_username and browserstack_access_key are required "
                        "when mobile_platform is 'browserstack'."
                    )
            else:
                if not ip_address or not port_number:
                    raise ValueError(
                        "ip_address and port_number are required when "
                        "mobile_platform is 'simulator/device'."
                    )

            options = self.get_appium_options(
                mobile_os=mobile_os, desired_caps=capabilities_dictionary
            )
            appium_url = UISecurity().build_appium_url(
                mobile_platform=mobile_platform,
                browserstack_username=browserstack_username,
                browserstack_access_key=browserstack_access_key,
                ip_address=ip_address,
                port_number=port_number,
            )
            self.logger.info("Creating Appium driver")

            mobile_driver = webdriver.Remote(command_executor=appium_url, options=options)
            return mobile_driver

        except (TypeError, ValueError) as e:
            self.logger.exception("Invalid input: %s", e)
            raise e
        except Exception as e:
            self.logger.exception("Error creating mobile driver: %s", e)
            raise e

    def get_appium_options(self, mobile_os: str, desired_caps: dict) -> AppiumOptions:
        """Returns the appropriate Appium options based on the mobile OS.

        Args:
            mobile_os: The mobile operating system ('android' or 'ios').
            desired_caps: A dictionary of desired capabilities.

        Returns:
            An AppiumOptions object.

        Raises:
            ValueError: If an unsupported mobile OS is provided.
        """
        try:
            mobile_os = mobile_os.lower()
            if mobile_os == "android":
                return UiAutomator2Options().load_capabilities(desired_caps)
            if mobile_os == "ios":
                return XCUITestOptions().load_capabilities(desired_caps)

            raise ValueError(f"Unsupported mobile OS: {mobile_os}")
        except Exception as e:
            self.logger.exception("Error creating appium options: %s", e)
            raise e
