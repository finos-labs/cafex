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
                "payload": self.get_payload(service_description.get("payload", None)),
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

    def get_db_configuration(self, key_path, append_mode=True):
        """
        Description:
            |  This method fetches entire db description from team_config.yml

        :param key_path:
        :type key_path: String

        :return: Dictionary
        """
        try:
            str_execution_environment = None
            str_environment_type = None
            if append_mode is True:
                str_execution_environment = self.fetch_execution_environment()
                str_environment_type = self.fetch_environment_type()
                pstr_keypath = "env" + "/" + str_execution_environment + "/" + str_environment_type + "/" + key_path
            elif append_mode is False:
                pstr_keypath = key_path
            else:
                raise Exception("append_mode parameter can only accept True/False")
            dict_db_desc = {}

            dict_db_configuration = self.get_valuefrom_configobject(self.team_config, pstr_keypath)
            dict_db_desc["db_type"] = dict_db_configuration.get("db_type", None)
            dict_db_desc["db_server"] = dict_db_configuration.get("db_server", None)
            dict_db_desc["db_name"] = dict_db_configuration.get("db_name", None)
            dict_db_desc["port"] = dict_db_configuration.get("port", None)
            bln_overwrite_default_db_user = dict_db_configuration.get("overwrite_default_db_user", False)
            dict_db_desc["user"] = dict_db_configuration.get("user", "default_db_user")

            if dict_db_desc["db_type"].lower() == "oracle":
                dict_db_desc["sid"] = dict_db_configuration.get("sid", None)
                dict_db_desc["service_name"] = dict_db_configuration.get("service_name", None)
                # Add the wallet connection parameters
                dict_db_desc["tns_admin"] = dict_db_configuration.get("tns_admin", None)
                dict_db_desc["thick_mode"] = dict_db_configuration.get("thick_mode", False)
                dict_db_desc["use_wallet"] = dict_db_configuration.get("use_wallet", False)
                dict_db_desc["encoding"] = dict_db_configuration.get("encoding", None)
            elif (dict_db_desc["db_type"].lower() == "hive") or (dict_db_desc["db_type"].lower() == "spark") or (
                    dict_db_desc["db_type"].lower() == "ec2_hive"):
                dict_db_desc["secret_key"] = dict_db_configuration.get("secret_key", None)
                dict_db_desc["is_password_encoded"] = dict_db_configuration.get("is_password_encoded", None)
                if dict_db_configuration.get("key_file", "None") == None:
                    dict_db_desc["key_file"] = None
                else:
                    dict_db_desc["key_file"] = os.path.join(self.get_configuration_directory_path(),
                                                            dict_db_configuration.get("key_file"))
            elif dict_db_desc["db_type"].lower() == "h2":
                dict_db_desc["db_path"] = dict_db_configuration.get("db_path", None)
                dict_db_desc["jar_path"] = dict_db_configuration.get("jar_path",None)
                dict_db_desc["class_name"] = dict_db_configuration.get("class_name", None)
                dict_db_desc["credentials"] = dict_db_configuration.get("credentials", None)
                dict_db_desc["libs"] = dict_db_configuration.get("libs", None)

            if bln_overwrite_default_db_user == False or dict_db_desc["user"] == "default_db_user":
                dict_db_desc["username"], dict_db_desc["password"] = self.fetch_db_default_login_credentials()

            elif bln_overwrite_default_db_user:
                dict_user = self.team_config["env"][str_execution_environment][str_environment_type][
                    dict_db_desc["user"]]
                dict_db_desc["username"] = dict_user.get("username", None)
                dict_db_desc["password"] = dict_user.get("password", None)
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

    def fetch_thick_client_parameters(self):
        """
        Fetches configuration parameters for a desktop application from the base configuration.

        This method retrieves the following parameters from the `config.yml` file:
        - Application path (`app_path`): The file path to the desktop application.
        - Process name (`process_name`): The name of the application's process.
        - Application name (`application_name`): The name of the application in lowercase.
        - Connect to open application flag (`connect_to_open_app`): A boolean indicating whether to connect
        to an already open application.
        - Teardown flag (`desktop_client_teardown_flag`): A boolean indicating whether to perform teardown operations
         for the application.

        If the `desktop_client_teardown_flag` is not explicitly defined in the configuration, it defaults to `True`.

        Returns:
            dict: A dictionary containing the desktop application's configuration parameters.

        Raises:
            Exception: If there is an error while fetching the parameters, it logs the exception and raises it.
        """
        try:
            execution_env = self.base_config.get("execution_environment")
            env_type = self.base_config.get("environment_type")
            app_path = self.base_config["env"][execution_env][env_type]["app_path"]
            process_name = self.base_config["env"][execution_env][env_type]["app_process_name"]
            application = self.base_config["env"][execution_env][env_type]["application_name"].lower()
            connect_to_open_app = self.base_config["env"][execution_env][env_type]["connect_to_open_app"]
            teardown_flag = self.base_config.get("desktop_client_teardown_flag", True)

            return {
                "app_path": app_path,
                "process_name": process_name,
                "application_name": application,
                "connect_to_open_app": connect_to_open_app,
                "desktop_client_teardown_flag": teardown_flag,
            }
        except Exception as e:
            self.logger.exception("Error in fetch_thick_client_parameters method --> %s", str(e))
            raise

