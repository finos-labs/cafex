"""
Description: This module contains methods related to fetching data from config.yml and
team_or_functionality_config.yml. This module also contains methods to fetch base URLs,
default user details, service descriptions, and database configurations.
"""
import operator
import os
from functools import reduce

import yaml
from cafex_core.logging.logger_ import CoreLogger
from cafex_core.singletons_.session_ import SessionStore


class ConfigUtils:
    """
    Description:
        |  1. This class contains methods related to fetching data from config.yml and
        team_or_functionality_config.yml
        |  2. This class also contains methods to fetch base URLs, default user details,
        service descriptions and db configurations

    .. note::
        |  Create an object for this class as obj = ConfigUtils('team_config_filename')

    """

    def __init__(self, team_config_filename=None):
        """
        Description:
            |  This method acts as a constructor for the ConfigUtils class. It initializes several
            class attributes
            |  and checks if a mobile platform is specified in the base configuration. If a team
            configuration filename
            |  is provided, it reads the team configuration file.

        :param team_config_filename: The name of the team configuration file. If provided,
        the team configuration file is read.
        :type team_config_filename: String, optional

        """
        self.logger_class = CoreLogger(name=__name__)
        self.logger = self.logger_class.get_logger()
        self._base_config = None
        self.session_store = SessionStore()
        self.features_dir_path = self.get_features_directory_path()
        self.mobile_os = None
        self.mobile_platform = None
        self.team_config = {}
        if team_config_filename is not None:
            self.team_config = self.read_team_config_file(team_config_filename)

    def read_base_config_file(self):
        """Reads the base configuration file and stores it in the session
        store.

        Returns:
        dict: The base configuration.
        """
        try:
            if self.session_store.base_config is None:
                with open(self.base_config_file_path, "r", encoding='utf-8') as config_yml:
                    self._base_config = yaml.safe_load(config_yml)
                self.session_store.base_config = self._base_config
            return self.session_store.base_config
        except (KeyError, ValueError) as config_read_error:
            self.logger.exception("Error while reading config.yml (base) --> %s",
                                  str(config_read_error))
            raise config_read_error

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

    def __get_folder_path_from_dir(self, folder_or_file_name, dir_path="root"):
        """Gets the path of a folder or file from a given directory.

        Parameters:
        folder_or_file_name (str): The name of the folder or file.
        dir_path (str): The directory path. Default is "root".

        Returns:
        str: The path of the folder or file.
        """
        root_dir = self.session_store.conf_dir if dir_path == "root" else dir_path
        return os.path.join(root_dir, str(folder_or_file_name))

    @property
    def base_config_file_path(self):
        """Gets the path of the base configuration file.

        Returns:
        str: The path of the base configuration file.
        """
        return self.__get_folder_path_from_dir("config.yml")

    @property
    def mobile_config_file_path(self):
        """Gets the path to the mobile-config.yml file."""
        return self.__get_folder_path_from_dir("mobile-config.yml")

    def read_team_config_file(self, team_config_file_name):
        """
        Description:
            |  This method reads team_config.yml file and loads the content into a dictionary
            object.

        :param team_config_file_name: The name of the team configuration file.
        :type team_config_file_name: str

        :return: Dictionary containing the team configuration.
        :rtype: dict

        :raises FileNotFoundError: If the specified file is not found.
        :raises ValueError: If the given file is not in YAML format.
        :raises KeyError: If there is an error in reading the file.
        :raises OSError: For any other OS-related errors.
        """
        try:
            if str(team_config_file_name).endswith(".yml"):
                with open(
                        os.path.join(self.get_configuration_directory_path(),
                                     team_config_file_name), "r", encoding='utf-8'
                ) as config_yml:
                    team_config = yaml.safe_load(config_yml)
                return team_config
            raise ValueError("Given team configuration file is not in yaml format")
        except (FileNotFoundError, ValueError, KeyError, OSError) as e:
            self.logger.exception("Error in read_team_config_file method--> %s", str(e))
            raise e

    @property
    def base_config(self):
        """Fetches the base configuration from the session store.

        This property retrieves the base configuration from the session store.

        Returns:
            dict: The base configuration from the session store.
        """
        return self.session_store.base_config

    @property
    def mobile_config(self):
        """Fetches the mobile configuration from the session store.

        This property retrieves the mobile configuration from the session store.

        Returns:
            dict: The mobile configuration from the session store.
        """
        return self.session_store.mobile_config

    @property
    def browserstack_web_config(self):
        """Fetches the browserstack web configuration from the session store.

        This property retrieves the browserstack web configuration from the session
        store.

        Returns:
            dict: The browserstack web configuration from the session store.
        """
        return self.session_store.browserstack_web_configuration

    @property
    def execution_environment(self):
        """Fetches the execution environment.

        This property retrieves the execution environment by calling the
        fetch_execution_environment method.
        The execution environment is a string that represents the current environment
        in which the application is running (e.g., 'dev', 'prod').

        Returns:
            str: The execution environment.
        """
        return self.fetch_execution_environment()

    @property
    def environment_type(self):
        """Fetches the environment type.

        This property retrieves the environment type by calling the
        fetch_environment_type method.
        The environment type is a string that represents the type of the current
        environment (e.g., 'on-prem', 'cloud').

        Returns:
            str: The environment type.
        """
        return self.fetch_environment_type()

    def get_project_path(self):
        """
        Description:
            |  This method fetches path of the root Project folder

        :return: String
        """
        try:
            return os.path.dirname(self.features_dir_path)
        except Exception as e:
            self.logger.exception("Error in get_project_path method--> %s", str(e))
            raise e

    def get_features_directory_path(self):
        """This method is used to fetch the path of the features' directory.

        Returns:
        str: The path of the features' directory.

        Raises:
        Exception: If there is an error in fetching the path.
        """
        try:
            return self.__get_folder_path_from_dir("features")
        except Exception as e:
            self.logger.exception("Error in get_features_directory_path method--> %s", str(e))
            raise e

    def get_value_of_key_base_config(
            self, key_, environment_based=True, execution_environment=None, environment_type=None
    ):
        """This method is used to fetch the value of a specific key from the
        base configuration file.

        Parameters:
        key_ (str): The key for which the value needs to be fetched.
        environment_based (bool, optional): Determines if the key needs to be searched within an
        environment. Defaults to True.
        execution_environment (str, optional): The execution environment (e.g., 'dev'). If not
        provided,it will pick the default values based on the execution environment passed during
        execution.
        environment_type (str, optional): The environment type (e.g., 'on-prem'). If not provided,
        it will pick the default values based on the execution environment passed during execution.

        Returns:
        str: The value of the key in the configuration.

        Raises:
        Exception: If the given key is not present in the configuration file.
        """
        try:
            if environment_based:
                execution_environment = execution_environment or self.execution_environment
                environment_type = environment_type or self.environment_type
                values = self.session_store.base_config["env"][execution_environment][
                    environment_type
                ]
            else:
                values = self.session_store.base_config
            if key_ in values:
                return values[key_]
            raise KeyError(f"The given key {key_} is not present in base config file")
        except KeyError as error_get_key_base_config:
            self.logger.exception(
                "Error in get_value_of_key_base_config method--> %s", str(error_get_key_base_config)
            )
            raise error_get_key_base_config

    def get_value_of_key_team_config(
            self, key_, environment_based=True, execution_environment=None, environment_type=None
    ):
        """This method is used to fetch the value of a specific key from the
        team configuration file.

        Parameters:
        key_ (str): The key for which the value needs to be fetched.
        environment_based (bool, optional): Determines if the key needs to be searched
        within an environment. Defaults to True.
        execution_environment (str, optional): The execution environment (e.g., 'dev').
        If not provided, it will pick the default values based on the execution environment passed
        during execution.
        environment_type (str, optional): The environment type (e.g., 'on-prem'). If not provided,
        it will pick the default values based on the execution environment passed during execution.

        Returns:
        str: The value of the key in the configuration.

        Raises:
        Exception: If the given key is not present in the team configuration file.
        """
        try:
            if environment_based:
                execution_environment = execution_environment or self.execution_environment
                environment_type = environment_type or self.environment_type
                values = self.team_config["env"][execution_environment][environment_type]
            else:
                values = self.session_store.base_config
            if key_ in values:
                return values[key_]
            raise KeyError(f"The given key {key_} is not present in base config file")
        except KeyError as error_get_key_team_config:
            self.logger.exception("Error in get_value_of_key_team_config method--> %s",
                                  str(error_get_key_team_config))
            raise error_get_key_team_config

    def get_configuration_directory_path(self):
        """This method is used to fetch the path of the configuration
        directory.

        Returns:
        str: The path of the configuration directory.

        Raises:
        Exception: If there is an error in fetching the path.
        """
        try:
            return os.path.join(self.features_dir_path, "configuration")
        except Exception as error_config_dir_path:
            self.logger.exception("Error in get_configuration_directory_path method--> %s"
                                  , str(error_config_dir_path))
            raise error_config_dir_path

    def get_value_from_yaml_keypath(self, yaml_filepath, keypath, delimiter="/"):
        """This method is used to fetch the value from a YAML file based on a
        given keypath.

        Parameters:
        yaml_filepath (str): The path of the YAML file.
        keypath (str): The keypath for which the value needs to be fetched. The keypath is a string
        of keys separated by a delimiter.
        delimiter (str, optional): The delimiter used in the keypath. Defaults to '/'.

        Returns:
        str: The value of the key in the YAML file.

        Raises:
        Exception: If there is an error in fetching the value.
        """
        try:
            with open(yaml_filepath, "r", encoding='utf-8') as config_yml:
                config = yaml.safe_load(config_yml)
            return reduce(operator.getitem, keypath.split(delimiter), config)
        except Exception as error_yaml_read:
            self.logger.exception("Error in get_value_from_yaml_keypath method --> %s",
                                  str(error_yaml_read))
            raise error_yaml_read

    def get_value_from_config_object(self, config_obj, keypath, delimiter="/"):
        """Fetches the value of a key from a given configuration object.

        Parameters:
        config_obj (dict): The configuration object from which the value needs to be fetched.
        keypath (str): The keypath for which the value needs to be fetched. The keypath is
        a string of keys separated by a delimiter.
        delimiter (str, optional): The delimiter used in the keypath. Defaults to '/'.

        Returns:
        Any: The value of the key in the configuration object.

        Raises:
        Exception: If there is an error in fetching the value.
        """
        try:
            lst_key = keypath.split(delimiter)
            return reduce(operator.getitem, lst_key, config_obj)
        except Exception as error_get_value_from_config:
            self.logger.exception("Error in get_value_from_config_object method--> %s",
                                  str(error_get_value_from_config))
            raise error_get_value_from_config

    def fetch_testdata_path(self):
        """This method is used to fetch the path of the testdata directory.

        Returns:
        str: The path of the testdata directory.

        Raises:
        Exception: If there is an error in fetching the path.
        """
        try:

            return os.path.join(self.features_dir_path, "testdata")
        except Exception as error_fetch_testdata:
            self.logger.exception("Error in fetch_testdata_path method--> %s",
                                  str(error_fetch_testdata))
            raise error_fetch_testdata

    def fetch_base_url(self):
        """Fetches the base URL for the selected environment based on the
        values applied for the keys 'execution_environment' and
        'environment_type' in the config.yml.

        Returns:
        str: The base URL for the selected environment.

        Raises:
        Exception: If there is an error while fetching the base URL from the base config.
        """
        try:
            base_url = self.session_store.base_config["env"][self.execution_environment][
                self.environment_type]["base_url"]
            return base_url
        except Exception as error_fetch_base_url:
            self.logger.exception("Error while fetching base url from base config in "
                                  "fetch_base_url method --> %s", str(error_fetch_base_url))
            raise error_fetch_base_url

    def fetch_environment_type(self):
        """Fetches the environment type from the base configuration.

        This method is used to retrieve the environment type (e.g., 'dev', 'prod')
        from the base configuration.

        Returns:
        str: The environment type from the base configuration.

        Raises:
        Exception: If there is an error in fetching the environment type.
        """
        try:
            return self.session_store.base_config.get("environment_type")
        except Exception as error_fetch_environment_type:
            self.logger.exception("Error in fetch_environment_type method--> %s",
                                  str(error_fetch_environment_type))
            raise error_fetch_environment_type

    def fetch_execution_environment(self):
        """Fetches the execution environment from the base configuration.

        This method is used to retrieve the execution environment (e.g., 'dev', 'prod')
        from the base configuration.

        Returns:
        str: The execution environment from the base configuration.

        Raises:
        Exception: If there is an error in fetching the execution environment.
        """
        try:
            return self.session_store.base_config.get("execution_environment")
        except Exception as error_fetch_execution_environment:
            self.logger.exception("Error in fetch_execution_environment method--> %s",
                                  str(error_fetch_execution_environment))
            raise error_fetch_execution_environment

    def fetch_selenium_grid_ip(self):
        """Fetches the IP address of the Selenium Grid from the base
        configuration.

        This method is used to retrieve the IP address of the Selenium Grid
        from the base configuration. The Selenium Grid IP is used to connect
        and send commands to the Selenium Grid server.

        Returns:
        str: The IP address of the Selenium Grid.

        Raises:
        Exception: If there is an error in fetching the Selenium Grid IP.
        """
        try:
            str_selenium_grid_ip = self.session_store.base_config.get("selenium_grid_ip")
            return str_selenium_grid_ip
        except Exception as error_fetch_selenium_grid_ip:
            self.logger.exception("Error in fetch_selenium_grid_ip method--> %s",
                                  str(error_fetch_selenium_grid_ip))
            raise error_fetch_selenium_grid_ip

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

    def fetch_service_description_path(self):
        """Fetches the path of the service description directory.

        This method retrieves the path of the service description directory.
        The path is constructed by joining the features directory path and the
        service description directory name from the base configuration.
        If an error occurs during this process, it logs the exception with a custom
        error message.

        Returns:
            str: The path of the service description directory.

        Raises:
            Exception: If there is an error in fetching the path of the service description
             directory.

        Example:
            >> config_utils = ConfigUtils()
            >> service_description_path_ = config_utils.fetch_service_description_path()
            >> print(service_description_path_)
        """
        try:
            service_description_path = os.path.join(
                self.features_dir_path, self.session_store.base_config["service_description"]
            )
            return service_description_path
        except Exception as error_fetch_service_description_path:
            self.logger.exception("Error in fetch_service_description_path method--> %s",
                                  str(error_fetch_service_description_path))
            raise error_fetch_service_description_path

    def fetch_service_payload_path(self):
        """Fetches the path of the service payload's directory.

        This method retrieves the path of the service payload's directory. The path is
        constructed by joining the features directory path and the service payloads
        directory name from the base configuration.
        If an error occurs during this process, it logs the exception with a custom error
         message.

        Returns:
            str: The path of the service payload's directory.

        Raises:
            Exception: If there is an error in fetching the path of the service payload's
             directory.

        Example:
            >> config_utils = ConfigUtils()
            >> service_payloads_path_ = config_utils.fetch_service_payload_path()
            >> print(service_payloads_path_)
        """
        try:
            service_payloads_path = os.path.join(
                self.features_dir_path, self.session_store.base_config["service_payloads"]
            )
            return service_payloads_path
        except Exception as error_fetch_service_payload_path:
            self.logger.exception("Error in fetch_service_payload_path method--> %s",
                                  str(error_fetch_service_payload_path))
            raise error_fetch_service_payload_path

    def fetch_overwrite_base_url(self):
        """
        Description:
            |  This method fetches value of overwrite_base_url flag set in
            team_config.yml

        :return: Boolean
        """
        try:
            overwrite_base_url = self.team_config["env"][self.execution_environment][
                self.environment_type]["overwrite_base_url"]
            return overwrite_base_url
        except Exception as error_fetch_overwrite_base_url:
            self.logger.exception("Error in fetch_overwrite_base_url method--> %s",
                                  str(error_fetch_overwrite_base_url))
            raise error_fetch_overwrite_base_url

    def fetch_login_credentials(self, user_account_type="default_user"):
        """Fetches the login credentials for a user account.

        This method retrieves the username and password for a specified user account
        type from the base configuration or the team configuration.
        By default, it fetches the credentials for the 'default_user' from the base
        configuration. If a different user account type is specified, it fetches the
        credentials for that user account type from the team configuration.

        Parameters:
            user_account_type (str, optional): The type of the user account for which the
            credentials need to be fetched. Defaults to 'default_user'.

        Returns:
            tuple: A tuple containing the username and password for the specified user
            account type.

        Raises:
            Exception: If there is an error in fetching the login credentials.

        Example:
            >> config_utils = ConfigUtils()
            >> username_, password_ = config_utils.fetch_login_credentials('admin_user')
            >> print(username_, password_)
        """
        try:
            config = (
                self.session_store.base_config
                if user_account_type == "default_user"
                else self.team_config
            )
            username = config["env"][self.execution_environment][self.environment_type][
                user_account_type
            ]["username"]
            password = config["env"][self.execution_environment][self.environment_type][
                user_account_type
            ]["password"]
            return username, password
        except Exception as error_fetch_login_credentials:
            self.logger.exception("Error in fetch_login_credentials method--> %s",
                                  str(error_fetch_login_credentials))
            raise error_fetch_login_credentials

    def fetch_target_url(self, target_key):
        """Fetches the target URL based on the provided key.

        This method retrieves the target URL from the team configuration based on the
        provided key.

        Parameters:
            target_key (str): The key for which the target URL needs to be fetched.

        Returns:
            str: The target URL for the specified key.

        Raises:
            Exception: If there is an error in fetching the target URL.

        Example:
            >> config_utils = ConfigUtils()
            >> target_url_ = config_utils.fetch_target_url('target_key')
            >> print(target_url_)
        """
        try:
            target_url = self.team_config["env"][self.execution_environment][self.
            environment_type][target_key]
            return target_url
        except Exception as error_fetch_target_url:
            self.logger.exception("Error in fetch_target_url method--> %s",
                                  str(error_fetch_target_url))
            raise error_fetch_target_url

    def get_service_description(self, service_desc_rel_filepath: str, keypath: str) -> dict:
        """Fetches the service description of a particular service mentioned in
        the service description yaml file.

        The service desc contains keys such as method, endpoint, query params, headers,
         payload, and target_url.

        Parameters:
            service_desc_rel_filepath (str): Relative path of the service description file.
            keypath (str): The keypath for which the value needs to be fetched.

        Returns:
            dict: The service description.
        """
        try:
            service_desc_path = os.path.join(
                self.fetch_service_description_path(), service_desc_rel_filepath
            )
            service_description = self.get_value_from_yaml_keypath(service_desc_path, keypath)
            target_url = service_description.get("target_url", "None")
            overwrite_base_url = self.fetch_overwrite_base_url()

            service_desc = {
                "target_url": (
                    self.fetch_target_url(target_url)
                    if target_url != "None" and overwrite_base_url
                    else self.fetch_base_url()
                ),
                "method": service_description.get("method"),
                "endpoint": service_description.get("endpoint"),
                "queryparams": service_description.get("queryparams", ""),
                "headers": service_description.get("headers", {}),
                "payload": self.get_payload(service_description.get("payload", "None")),
            }
            return service_desc
        except Exception as error_get_service_description:
            self.logger.exception("Error in get_service_description method--> %s",
                                  str(error_get_service_description))
            raise error_get_service_description

    def get_payload(self, payload):
        """Fetches the payload content from a file.

        Parameters:
            payload (str): The name of the payload file.

        Returns:
            str: The content of the payload file, or None if the payload parameter is "None".

        Example:
            >> config_utils = ConfigUtils()
            >> payload_content = config_utils.get_payload('payload_file')
            >> print(payload_content)
        """
        if payload == "None":
            return None
        payload_path = os.path.join(self.fetch_service_payload_path(), payload)
        with open(payload_path, "r", encoding="utf-8") as file:
            return file.read()

    def fetch_db_default_login_credentials(self, user_account_type="default_db_user"):
        """Fetches the default login credentials for a database.

        This method retrieves the username and password for a specified user account type
        from the base configuration or the team configuration.
        By default, it fetches the credentials for the 'default_db_user' from the base
         configuration. If a different user account type is specified, it fetches the
         credentials for that user account type from the team configuration.

        Parameters:
        user_account_type (str, optional): The type of the user account for which the
        credentials need to be fetched. Defaults to 'default_db_user'.

        Returns:
        tuple: A tuple containing the username and password for the specified user account
         type.

        Raises:
        Exception: If there is an error in fetching the login credentials.

        Example:
            >> config_utils = ConfigUtils()
            >> username_, password_ = config_utils.
            fetch_db_default_login_credentials('admin_user')
            >> print(username_, password_)
        """
        try:
            config = (
                self.session_store.base_config
                if user_account_type == "default_db_user"
                else self.team_config
            )
            username = config["env"][self.execution_environment][self.environment_type][
                user_account_type
            ]["username"]
            password = config["env"][self.execution_environment][self.environment_type][
                user_account_type
            ]["password"]
            return username, password
        except Exception as error_fetch_db_default_login_credentials:
            self.logger.exception("Error in fetch_db_default_login_credentials method--> %s"
                                  , str(error_fetch_db_default_login_credentials))
            raise error_fetch_db_default_login_credentials

    # def get_db_configuration(self, key_path, append_mode=True):
    #     """Fetches the database configuration based on the provided key path.
    #
    #     This method retrieves the database configuration from the team configuration based
    #     on the provided key path.
    #     It fetches the database type, server, name, port, and user from the team configuration.
    #     It also fetches additional configuration based on the database type.
    #     If the database user is the default user or the 'overwrite_default_db_user'
    #     flag is set, it fetches the default login credentials.
    #     Otherwise, it fetches the username and password for the specified user from the
    #     team configuration.
    #
    #     Parameters:
    #     key_path (str): The key path for which the database configuration needs to be fetched.
    #     append_mode (bool, optional): Determines if the key path needs to be appended with
    #     the execution environment and environment type. Defaults to True.
    #
    #     Returns:
    #     dict: The database configuration for the specified key path.
    #
    #     Raises:
    #     Exception: If there is an error in fetching the database configuration.
    #     """
    #     try:
    #         if append_mode:
    #             key_path = f"env/{self.execution_environment}/{self.environment_type}/{key_path}"
    #         dict_db_configuration = self.get_value_from_config_object(self.team_config, key_path)
    #         db_desc = {
    #             "db_type": dict_db_configuration.get("db_type", "None"),
    #             "db_server": dict_db_configuration.get("db_server", "None"),
    #             "db_name": dict_db_configuration.get("db_name", "None"),
    #             "port": dict_db_configuration.get("port", "None"),
    #             "user": dict_db_configuration.get("user", "default_db_user"),
    #             "username": None,
    #             "password": None,
    #         }
    #
    #         db_type = db_desc["db_type"].lower()
    #         if db_type == "oracle":
    #             db_desc["sid"] = dict_db_configuration.get("sid", "None")
    #             db_desc["service_name"] = dict_db_configuration.get("service_name", "None")
    #         elif db_type in ["hive", "spark", "ec2_hive"]:
    #             db_desc["secret_key"] = dict_db_configuration.get("secret_key", "None")
    #             db_desc["is_password_encoded"] = dict_db_configuration.get(
    #                 "is_password_encoded", "None"
    #             )
    #             db_desc["key_file"] = (
    #                 "None"
    #                 if dict_db_configuration.get("key_file", "None") == "None"
    #                 else os.path.join(
    #                     self.get_configuration_directory_path(),
    #                     dict_db_configuration.get("key_file"),
    #                 )
    #             )
    #         elif db_type == "h2":
    #             db_desc["db_path"] = dict_db_configuration.get("db_path", "None")
    #             db_desc["jar_path"] = dict_db_configuration.get("jar_path", "None")
    #             db_desc["class_name"] = dict_db_configuration.get("class_name", "None")
    #             db_desc["credentials"] = dict_db_configuration.get("credentials", "None")
    #             db_desc["libs"] = dict_db_configuration.get("libs", "None")
    #
    #         if (
    #                 dict_db_configuration.get("overwrite_default_db_user", False)
    #                 or db_desc["user"] == "default_db_user"
    #         ):
    #             db_desc["username"], db_desc["password"] = self.fetch_db_default_login_credentials()
    #         else:
    #             dict_user = self.team_config["env"][self.execution_environment][
    #                 self.environment_type
    #             ][db_desc["user"]]
    #             db_desc["username"] = dict_user.get("username", "None")
    #             db_desc["password"] = dict_user.get("password", "None")
    #         return db_desc
    #     except Exception as error_get_db_configuration:
    #         self.logger.exception("Error in get_db_configuration method--> %s",
    #                               str(error_get_db_configuration))
    #         raise error_get_db_configuration

    def get_db_configuration(self, pstr_keypath, append_mode=True):
        """
        Description:
            |  This method fetches entire db description from team_config.yml

        :param pstr_keypath:
        :type pstr_keypath: String

        :return: Dictionary
        """
        try:
            if append_mode is True:
                str_execution_environment = self.fetch_execution_environment()
                str_environment_type = self.fetch_environment_type()
                pstr_keypath = "env" + "/" + str_execution_environment + "/" + str_environment_type + "/" + pstr_keypath
            elif append_mode is False:
                pstr_keypath = pstr_keypath
            else:
                raise Exception("append_mode parameter can only accept True/False")
            dict_db_desc = {}

            dict_db_configuration = self.get_valuefrom_configobject(self.team_config, pstr_keypath)
            dict_db_desc["db_type"] = dict_db_configuration.get("db_type", "None")
            dict_db_desc["db_server"] = dict_db_configuration.get("db_server", "None")
            dict_db_desc["db_name"] = dict_db_configuration.get("db_name", "None")
            dict_db_desc["port"] = dict_db_configuration.get("port", "None")
            bln_overwrite_default_db_user = dict_db_configuration.get("overwrite_default_db_user", False)
            dict_db_desc["user"] = dict_db_configuration.get("user", "default_db_user")
            if dict_db_desc["db_type"].lower() == "oracle":
                dict_db_desc["sid"] = dict_db_configuration.get("sid", "None")
                dict_db_desc["service_name"] = dict_db_configuration.get("service_name", "None")
            elif (dict_db_desc["db_type"].lower() == "hive") or (dict_db_desc["db_type"].lower() == "spark") or (
                    dict_db_desc["db_type"].lower() == "ec2_hive"):
                dict_db_desc["secret_key"] = dict_db_configuration.get("secret_key", "None")
                dict_db_desc["is_password_encoded"] = dict_db_configuration.get("is_password_encoded", "None")
                if dict_db_configuration.get("key_file", "None") == "None":
                    dict_db_desc["key_file"] = "None"
                else:
                    dict_db_desc["key_file"] = os.path.join(self.get_configuration_dirpath(),
                                                            dict_db_configuration.get("key_file"))
            elif dict_db_desc["db_type"].lower() == "h2":
                dict_db_desc["db_path"] = dict_db_configuration.get("db_path", "None")
                dict_db_desc["jar_path"] = dict_db_configuration.get("jar_path", "None")
                dict_db_desc["class_name"] = dict_db_configuration.get("class_name", "None")
                dict_db_desc["credentials"] = dict_db_configuration.get("credentials", "None")
                dict_db_desc["libs"] = dict_db_configuration.get("libs", "None")

            if bln_overwrite_default_db_user == False or dict_db_desc["user"] == "default_db_user":
                dict_db_desc["username"], dict_db_desc["password"] = self.fetch_db_default_login_credentials()

            elif (bln_overwrite_default_db_user == True):
                dict_user = self.team_config["env"][str_execution_environment][str_environment_type][
                    dict_db_desc["user"]]
                dict_db_desc["username"] = dict_user.get("username", "None")
                dict_db_desc["password"] = dict_user.get("password", "None")
            else:
                raise Exception("Error-->overwrite_default_db_user in config.yml can accept only True/False")
            return dict_db_desc
        except Exception as error_get_db_configuration:
            self.logger.exception("Error in get_db_configuration method--> %s",
                                  str(error_get_db_configuration))
            raise error_get_db_configuration

    def get_valuefrom_configobject(self, pobj_config, pstr_keypath, pstr_delimiter='/'):
        """
        Description:
            |  This method fetches value of a key from a yaml file

        :param pobj_config:
        :type pobj_config: Dictionary
        :param pstr_keypath:
        :type pstr_keypath: String

        :return: List
        Examples:
            |  An example of pstr_keypath is root/level1/level2/key

        """
        try:
            lst_key = pstr_keypath.split(pstr_delimiter)
            return reduce(operator.getitem, lst_key, pobj_config)
        except Exception as e:
            self.logger.exception('Error in get_valuefrom_configobject method-->' + str(e))


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

    def get_bool_decrypt_test_password(self):
        """Checks if the secured password feature is enabled.

        This method retrieves the 'use_secured_password' setting from the base configuration.
        The 'use_secured_password' setting determines whether the secured password feature is
        used or not.
        If the 'use_secured_password' key is not present in the base configuration, it
        defaults to False.

        Returns:
        bool: The 'use_secured_password' setting from the base configuration.

        Raises:
        Exception: If there is an error in fetching the 'use_secured_password' setting.
        """
        try:
            return self.session_store.base_config.get("use_secured_password", False)
        except KeyError as e:
            self.logger.exception("Error in get_bool_decrypt_test_password method--> %s", str(e))
            raise e

    def is_grid_execution(self):
        """Checks if the grid execution is enabled.

        This method retrieves the 'use_grid' setting from the base configuration.
        The 'use_grid' setting determines whether the grid feature is used or not.
        If the 'use_grid' key is not present in the base configuration, it defaults to False.

        Returns:
        bool: The 'use_grid' setting from the base configuration.

        Raises:
        Exception: If there is an error in fetching the 'use_grid' setting.
        """
        try:
            self.session_store.base_config.get("use_grid", False)
        except Exception as e:
            self.logger.exception("Error in is_grid_execution method--> %s", str(e))
            raise e

    def get_grid_directory_path(self):
        """Fetches the grid directory path from the base configuration.

        This method retrieves the value of the 'grid_directory_path' key from the base
        configuration stored in the session store.
        If the key is not found, it raises an exception.

        Raises:
            Exception: If there is an error in fetching the grid directory path.
        """
        try:
            self.session_store.base_config.get("grid_directory_path", None)
        except Exception as e:
            self.logger.exception("Error in get_grid_directory_path method--> %s", str(e))
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

    def is_api_artifacts(self):
        """Checks if API artifacts are present in the base configuration.

        This method checks if the key "API_Artifacts" exists in the base configuration
        dictionary and returns its value.
        If the key does not exist, it returns False. If an exception occurs, it raises the
        exception.

        Returns:
            bool: True if "API_Artifacts" exists in the base configuration, False otherwise.

        Raises:
            Exception: If there is an error in fetching the "API_Artifacts" key.
        """
        try:
            is_present = self.session_store.base_config.get("API_Artifacts", False)
            return is_present
        except Exception as error_is_api_artifacts:
            self.logger.exception("Error in is_api_artifacts method--> %s",
                                  str(error_is_api_artifacts))
            raise error_is_api_artifacts

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

    def get_appium_port_number(self, mobile_os: str) -> str:
        """Fetches the port number for Mobile Automation from the
        configuration.

        This method retrieves port number for Mobile Automation from the configuration.

        Returns:
            str: The port number for Mobile Automation. If an error occurs, it returns
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
