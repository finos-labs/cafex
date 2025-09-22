import os
import yaml
from cafex_core.utils.config_utils import ConfigUtils


class WebConfigUtils(ConfigUtils):
    """
    This class is used to fetch the configuration for web automation.
    It reads the configuration files and provides methods to access various
    configuration parameters.
    """

    def read_browserstack_web_yml_file(self, file_name):
        """Reads the yml file if it exists, otherwise creates an empty
        browserstack_web_configuration."""
        try:
            browserstack_configuration = self.read_browserstack_web_capabilities_file(file_name)
            self.session_store.browserstack_web_configuration = {}
            if browserstack_configuration:
                self.session_store.browserstack_web_configuration = browserstack_configuration
            return self.session_store.browserstack_web_configuration
        except Exception as config_read_error:
            self.logger.exception("Error while reading %s --> %s", file_name,
                                  str(config_read_error))
            raise config_read_error

    @property
    def browserstack_web_config(self):
        """Fetches the browserstack web configuration from the session store.

        This property retrieves the browserstack web configuration from the session
        store.

        Returns:
            dict: The browserstack web configuration from the session store.
        """
        return self.session_store.browserstack_web_configuration

    def fetch_web_browser_capabilities(self):
        """Fetches the web capabilities from the base configuration.

        This method retrieves the web capabilities from the base configuration. These capabilities are required for execution in the Selenium Grid.
        The method attempts to get the value of the "web_capabilities" key from the base configuration. If successful, it returns the value.
        If an error occurs during this process, it logs the exception with a custom error message.

        Returns:
            str: The web capabilities from the base configuration.

        Raises:
            Exception: If there is an error in fetching the web capabilities.

        Example:
            >>config_utils = ConfigUtils()
            >> web_capabilities_ = config_utils.fetch_web_browser_capabilities()
            >> print(web_capabilities_)
        """
        try:
            web_capabilities = self.session_store.base_config.get("web_capabilities")
            return web_capabilities
        except Exception as error_fetch_web_browser_capabilities:
            self.logger.exception(
                "Error in fetch_web_browser_capabilities method--> %s"
                , str(error_fetch_web_browser_capabilities)
            )

    def fetch_use_grid(self):
        """Fetches the user grid from the base configuration.

        This method is used to retrieve the user grid setting from the base configuration.
        The user grid setting determines whether the grid feature is used or not.

        Returns:
        bool: The user grid setting from the base configuration.

        Raises:
        Exception: If there is an error in fetching the user grid setting.
        """
        try:
            bool_use_grid = self.session_store.base_config.get("use_grid")
            return bool_use_grid
        except Exception as error_fetch_use_grid:
            self.logger.exception("Error in fetch_use_grid method--> %s",
                                  str(error_fetch_use_grid))
            raise error_fetch_use_grid

    def fetch_current_browser(self):
        """Fetches the current browser for execution from the base
        configuration.

        This method is used to retrieve the current browser for execution
        (e.g., 'chrome', 'firefox')
        from the base configuration. If the 'current_execution_browser' key is not
        present in the base configuration,
        it defaults to 'chrome'.

        Returns:
        str: The current browser for execution from the base configuration.

        Raises:
        Exception: If there is an error in fetching the current browser.
        """
        try:
            current_execution_browser = (
                    self.session_store.base_config.get("current_execution_browser", None)
                    or "chrome"
            )
            return current_execution_browser
        except Exception as error_fetch_current_browser:
            self.logger.exception("Error in fetch_current_browser method--> %s",
                                  str(error_fetch_current_browser))
            raise error_fetch_current_browser

    def get_explicit_wait(self):
        """Fetches the explicit wait time from the user's custom configuration
        file.

         This method retrieves the explicit wait time from the user's custom configuration
          file.
         If the custom configuration file is not present, it fetches the explicit wait time
          from the base configuration file.

         Returns:
         int: The explicit wait time.

         Raises:
         Exception: If there is an error in fetching the explicit wait time.

         Example:
             >> config_utils = ConfigUtils()
             >> explicit_wait_ = config_utils.get_explicit_wait()
             >> print(explicit_wait_)
        """
        try:
            return self.team_config.get(
                "default_explicit_wait", self.session_store.base_config.
                get("default_explicit_wait")
            )
        except KeyError as error_get_explicit_wait:
            self.logger.exception("Error in get_explicit_wait method--> %s",
                                  str(error_get_explicit_wait))
            return 30

    def get_implicit_wait(self):
        """Fetches the implicit wait from the configuration.

        This method retrieves the implicit wait time from the team configuration if present,
        otherwise from the base configuration.

        Returns:
        int: The implicit wait time.
        """
        try:
            return self.team_config.get(
                "default_implicit_wait",
                self.session_store.base_config.get("default_implicit_wait", 30),
            )
        except KeyError as e:
            self.logger.exception("Error in get_implicit_wait method--> %s", str(e))
            return 30

    def get_browserstack_username(self):
        """Fetches the browserstack username from the configuration.

        This method retrieves the browserstack username from the configuration.

        Returns:
            str: The browserstack username. If an error occurs, it returns the exception.

        Raises:
            Exception: If there is an error in fetching the browserstack username.

        Example:
            >> config_utils = ConfigUtils()
            >> browserstack_username = config_utils.get_browserstack_username()
            >> print(browserstack_username)
        """
        try:
            return self.session_store.mobile_config.get("browserstack_username")
        except Exception as error_get_browserstack_username:
            self.logger.exception("Error in get_browserstack_username method--> %s",
                                  str(error_get_browserstack_username))
            raise error_get_browserstack_username

    def get_browserstack_access_key(self):
        """Fetches the browserstack access key from the configuration.

        This method retrieves the browserstack access key from the configuration.

        Returns:
            str: The browserstack access key. If an error occurs, it returns the exception.

        Raises:
            Exception: If there is an error in fetching the browserstack access key.

        Example:
            >> config_utils = ConfigUtils()
            >> browserstack_access_key = config_utils.get_browserstack_access_key()
            >> print(browserstack_access_key)
        """
        try:
            return self.session_store.mobile_config.get("browserstack_access_key")
        except Exception as error_get_browserstack_access_key:
            self.logger.exception("Error in get_browserstack_access_key method--> %s",
                                  str(error_get_browserstack_access_key))
            raise error_get_browserstack_access_key

    def get_browserstack_web_configuration_directory_path(self):
        """This method is used to fetch the path of the configuration
        directory.

        Returns:
        str: The path of the configuration directory.

        Raises:
        Exception: If there is an error in fetching the path.
        """
        try:
            return os.path.join(
                self.features_dir_path, "configuration", "browserstack_web_configuration"
            )
        except Exception as error_config_dir_path:
            self.logger.exception("Error in get_configuration_directory_path method--> %s",
                                  str(error_config_dir_path))
            raise error_config_dir_path

    def read_browserstack_web_capabilities_file(self, filename):
        """Reads the desired capabilities file and loads the content into a
        dictionary object.

        Returns:
            dict: A dictionary that contains the desired capabilities.

        Raises:
            FileNotFoundError: If the specified file is not found.
            ValueError: If the given file is not in YAML format.
            Exception: For any other errors during file reading.
        """
        try:
            file_path = os.path.join(
                self.get_browserstack_web_configuration_directory_path(), filename
            )

            if not os.path.exists(file_path):
                raise FileNotFoundError(
                    f"The desired capabilities file '{filename}' was not found "
                    f"in the directory: {self.get_browserstack_web_configuration_directory_path()}"
                )

            if filename.endswith(".yml"):
                with open(file_path, "r", encoding='utf-8') as capability_yml:
                    return yaml.safe_load(capability_yml)
            else:
                raise ValueError("Given file is not in YAML format.")

        except FileNotFoundError as e:
            self.logger.exception("File not found: %s", str(e))
            raise e
        except ValueError as e:
            self.logger.exception("File not in YAML format: %s", str(e))
            raise e
        except Exception as e:
            self.logger.exception("Error in read_browserstack_web_capabilities_file "
                                  "method--> %s", str(e))
            raise e


class MobileConfigUtils(ConfigUtils):
    """This class is used to fetch the configuration for mobile automation.
       It reads the configuration files and provides methods to access various
       configuration parameters.
       """

    def read_mobile_config_file(self):
        """Reads the mobile-config.yml file if it exists, otherwise creates an
        empty mobile_config."""
        try:
            if os.path.exists(self.mobile_config_file_path):
                with open(self.mobile_config_file_path, "r", encoding='utf-8') as mobile_config_yml:
                    mobile_config = yaml.safe_load(mobile_config_yml)
            else:
                mobile_config = {}  # Create an empty dictionary if the file doesn't exist

            self.session_store.mobile_config = mobile_config
            return self.session_store.mobile_config
        except Exception as config_read_error:
            self.logger.exception("Error while reading mobile-config.yml --> %s",
                                  str(config_read_error))
            raise config_read_error

    @property
    def mobile_config(self):
        """Fetches the mobile configuration from the session store.

        This property retrieves the mobile configuration from the session store.

        Returns:
            dict: The mobile configuration from the session store.
        """
        return self.session_store.mobile_config

    def get_appium_ip_address(self, mobile_os: str) -> str:
        """Fetches the ip address for Mobile Automation from the configuration.

        This method retrieves ip address for Mobile Automation from the configuration.

        Returns:
            str: The ip address for Mobile Automation. If an error occurs, it returns the
            exception.

        Raises:
            Exception: If there is an error in fetching the ip address.

        Example:
            >> config_utils = ConfigUtils()
            >> ip_address = config_utils.get_appium_ip_address("android")
            >> print(ip_address)
        """
        try:
            appium_ip_key = f"{mobile_os}_appium_ip_address"
            appium_ip_address = self.session_store.mobile_config.get(appium_ip_key)
            if appium_ip_address is None:
                raise KeyError(f"Key '{appium_ip_key}' not found in the configuration.")
            return appium_ip_address
        except KeyError as e:
            self.logger.exception("KeyError in get_appium_ip_address method--> %s", str(e))
            raise e
        except Exception as e:
            self.logger.exception("Error in get_appium_ip_address method--> %s", str(e))
            raise e

    def get_appium_port_number(self, mobile_os: str) -> int:
        """Fetches the port number for Mobile Automation from the
        configuration.

        This method retrieves port number for Mobile Automation from the configuration.

        Returns:
            int: The port number for Mobile Automation. If an error occurs, it returns
            the exception.

        Raises:
            Exception: If there is an error in fetching the port number.

        Example:
            >> config_utils = ConfigUtils()
            >> ip_address = config_utils.get_appium_port_number("android")
            >> print(ip_address)
        """
        try:
            appium_port_key = f"{mobile_os}_appium_port_number"
            appium_port_number = self.session_store.mobile_config.get(appium_port_key)
            if appium_port_number is None:
                raise KeyError(f"Key '{appium_port_key}' not found in the configuration.")
            return appium_port_number
        except KeyError as e:
            self.logger.exception("KeyError in get_appium_port_number method--> %s", str(e))
            raise e
        except Exception as e:
            self.logger.exception("Error in get_appium_port_number method--> %s", str(e))
            raise e

    def get_mobile_configuration_directory_path(self):
        """This method is used to fetch the path of the configuration
        directory.

        Returns:
        str: The path of the configuration directory.

        Raises:
        Exception: If there is an error in fetching the path.
        """
        try:
            return os.path.join(self.features_dir_path, "configuration", "mobile_configuration")
        except Exception as error_config_dir_path:
            self.logger.exception("Error in get_configuration_directory_path method--> %s",
                                  str(error_config_dir_path))
            raise error_config_dir_path

    def fetch_run_on_mobile(self):
        """Fetches the 'run_on_mobile' configuration from the base
        configuration.

        This method retrieves the value of the 'run_on_mobile' key from the base configuration.
        If the key is not found, it raises an exception.

        Returns:
        bool: The value of the 'run_on_mobile' key in the base configuration.

        Raises:
        Exception: If there is an error in fetching the 'run_on_mobile' configuration.
        """
        try:
            return self.session_store.base_config["run_on_mobile"]
        except KeyError as e:
            self.logger.exception("Exception in fetch_run_on_mobile --> %s", str(repr(e)))
            raise e

    def get_custom_desired_properties(self):
        """Builds the desired capability object for Android and iOS mobile
        platform from the capabilities file.

        This method retrieves the desired capabilities for a specific mobile platform based on the
         tag name.
        The capabilities are fetched from a configuration file specified in the base configuration
        under the key 'desired_capabilities_file'.
        If this key is not present in the base configuration, the default file 'capabilities.yml'
        is used.

        Parameters:
        tag_name (str): The tag name which is used to determine the mobile platform details.

        Returns:
        dict: The desired capabilities for the specific mobile platform.

        Raises:
        Exception: If there is an error in fetching the mobile platform details or constructing
        the desired capabilities.
        """
        try:
            desired_capabilities = self.fetch_capabilities_dictionary()
            return desired_capabilities
        except Exception as e:
            self.logger.exception("Error in get_custom_desired_properties method--> %s", str(e))
            raise e

    def fetch_capabilities_dictionary(self):
        """Fetches the desired capabilities for a specific mobile platform.

        This method retrieves the desired capabilities for a specific mobile platform from a
        configuration file.
        The configuration file is specified in the base configuration under the key
        'desired_capabilities_file'.
        If this key is not present in the base configuration, the default file
        'capabilities.yml' is used.
        The method also fetches the execution environment, environment type, and mobile platform
         type.
        Depending on the mobile platform type (simulator, cloud, real device), it fetches the
        corresponding desired capabilities.
        If the 'chromedriverExecutable' key is present in the desired capabilities, it updates the
        value with the path to the Chrome driver.

        Raises:
        Exception: If the mobile platform type is not 'simulator', 'cloud', or 'realdevice'.
        Exception: If there is an error in fetching the desired capabilities.

        Returns:
        dict: The desired capabilities for the specific mobile platform.
        """
        try:
            capabilities_file = self.session_store.mobile_config.get(
                "desired_capabilities_file", "capabilities.yml"
            )
            desired_capability_config = self.read_desired_capabilities_file(capabilities_file)
            mobile_os = self.get_mobile_os()
            mobile_platform = self.get_mobile_platform()
            if mobile_os and mobile_platform:
                desired_caps = desired_capability_config[mobile_os][mobile_platform]
                return desired_caps
            raise ValueError("For Mobile Automation mobile_os and mobile_platform should "
                             "be present in configuration file")
        except (KeyError, ValueError) as e:
            self.logger.exception("Error in fetch_capabilities_dictionary method--> %s", str(e))
            return e

    def read_desired_capabilities_file(self, filename):
        """Reads the desired capabilities file and loads the content into a
        dictionary object.

        Returns:
            dict: A dictionary that contains the desired capabilities.

        Raises:
            FileNotFoundError: If the specified file is not found.
            ValueError: If the given file is not in YAML format.
            Exception: For any other errors during file reading.
        """
        try:
            file_path = os.path.join(self.get_mobile_configuration_directory_path(), filename)

            if not os.path.exists(file_path):
                raise FileNotFoundError(
                    f"The desired capabilities file '{filename}' was not found "
                    f"in the directory: {self.get_mobile_configuration_directory_path()}"
                )

            if filename.endswith(".yml"):
                with open(file_path, "r", encoding='utf-8') as capability_yml:
                    return yaml.safe_load(capability_yml)
            else:
                raise ValueError("Given file is not in YAML format.")

        except FileNotFoundError as e:
            self.logger.exception("Desired capabilities file not found. %s", str(e))
            raise e
        except ValueError as e:
            self.logger.exception("Given file is not in YAML format. %s", str(e))
            raise e
        except Exception as e:
            self.logger.exception("Error in read_desired_capabilities_file method--> %s", str(e))
            raise e

    def get_mobile_os(self):
        """Fetches the mobile os (ios/android) from the mobile configuration
        file.

        This method retrieves the mobile os from the mobile configuration file.

        Returns:
            str: The mobile os in lowercase.

        Raises:
            FileNotFoundError: If the 'mobile-config.yml' file is not found.
            KeyError: If the 'mobile_os' key is not present in the mobile configuration.
            Exception: For any other errors encountered while fetching the mobile OS.

        Example:
            >> config_utils = ConfigUtils()
            >> mobile_app_os = config_utils.get_mobile_os()
            >> print(mobile_app_os)
        """
        try:
            if not os.path.exists(self.mobile_config_file_path):
                raise FileNotFoundError(
                    "The 'mobile-config.yml' file was not found. "
                    "Please make sure the file exists and is correctly configured."
                )
            mobile_os = self.session_store.mobile_config.get("mobile_os")
            if not mobile_os:
                raise KeyError(
                    "The 'mobile_os' key is missing in the 'mobile-config.yml' file. "
                    "Please specify the mobile OS (ios or android)."
                )
            return mobile_os.lower()

        except FileNotFoundError as e:
            self.logger.exception("FileNotFoundError in get_mobile_os method--> %s", str(e))
            raise e
        except KeyError as e:
            self.logger.exception("KeyError in get_mobile_os method--> %s", str(e))
            raise e
        except Exception as error_get_mobile_os:
            self.logger.exception("Error in get_mobile_os method--> %s", str(error_get_mobile_os))
            raise error_get_mobile_os

    def get_mobile_platform(self):
        """Fetches the mobile platform (simulator/device/browserstack) from the
        mobile configuration file.

        Returns:
            str: The mobile platform in lowercase.

        Raises:
            FileNotFoundError: If the 'mobile-config.yml' file is not found.
            KeyError: If the 'mobile_platform' key is not present in the mobile configuration.
            Exception: For any other errors encountered while fetching the mobile platform.
        """
        try:
            if not os.path.exists(self.mobile_config_file_path):
                raise FileNotFoundError(
                    "The 'mobile-config.yml' file was not found. "
                    "Please make sure the file exists and is correctly configured."
                )

            mobile_platform = self.session_store.mobile_config.get("mobile_platform")
            if not mobile_platform:
                raise KeyError(
                    "The 'mobile_platform' key is missing in the 'mobile-config.yml' file. "
                    "Please specify the mobile platform (simulator, device, or browserstack)."
                )
            return mobile_platform.lower()

        except FileNotFoundError as e:
            self.logger.exception("FileNotFoundError in get_mobile_platform method--> %s", str(e))
            raise e
        except KeyError as e:
            self.logger.exception("KeyError in get_mobile_platform method--> %s", str(e))
            raise e
        except Exception as error_get_mobile_platform:
            self.logger.exception("Error in get_mobile_platform method--> %s",
                                  str(error_get_mobile_platform))
            raise error_get_mobile_platform

