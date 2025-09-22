"""This module contains the PytestSessionStart class which is used to
initialize and manage a pytest session."""

import functools
import importlib.metadata
import operator
import os
import platform
import shutil
import sys
from ast import literal_eval

import pytest
import xdist
import yaml
from cafex_core.handlers.file_handler import FileHandler
from cafex_core.handlers.folder_handler import FolderHandler
from cafex_core.logging.logger_ import CoreLogger
from cafex_core.singletons_.session_ import SessionStore
from cafex_core.utils.config_utils import ConfigUtils
from cafex_core.utils.date_time_utils import DateTimeActions
from cafex_ui.cafex_ui_config_utils import WebConfigUtils, MobileConfigUtils


class PytestSessionStart:
    """Represents the start of a pytest session.

    Args:
        session: The pytest session object.

    Attributes:
        logger: The logger object.
        session_store: The session store object.
        sys_arg: system arguments
        session: The pytest session object.
        date_time_util: The datetime utility object.
        file_handler_obj: The file handler object.
        session_worker: The xdist worker ID for the session.

    Methods:
        __init_session_start: Initializes the session start.
        session_start_hook: Hook method called at the start of the session.
        update_commandline_data: Updates the command line data.
        pytest_session_start_auto_dash_configuration: Configures the auto dashboard for pytest session.
    """

    def __init__(self, session, sys_arg):
        self.session = session
        self.sys_arg = sys_arg
        self.file_handler_obj = None
        self.session_worker = xdist.get_xdist_worker_id(self.session)
        self.is_worker = xdist.get_xdist_worker_id(self.session)
        self.session_store = SessionStore()
        self.session_store.global_dict = {}
        self.session_store.collection_details = {}
        self.session_store.base_config = None
        self.logger = CoreLogger(name=__name__).get_logger()
        self.date_time_util = DateTimeActions()
        self.file_handler_obj = FileHandler()
        self.folder_handler = FolderHandler()
        self.config_utils = ConfigUtils()
        self.config_utils_web = WebConfigUtils()
        self.config_utils_mobile = MobileConfigUtils()
        self.config_utils.read_base_config_file()
        self.config_utils_mobile.read_mobile_config_file()

    def session_start_hook(self):
        """Hook method called at the start of the session."""
        if "auto_dashboard_report" in self.config_utils.base_config.keys():
            self.session_store.is_report = self.config_utils.base_config.get(
                "auto_dashboard_report"
            )
        else:
            self.logger.warning(
                "Warning! To push data to reporting server."
                "Add 'auto_dashboard_report' key and its value in config.yml file"
            )
        self.logger.info("STARTED EXECUTION OF SESSION:")
        self.logger.info(f"Session Worker: {self.session_worker}")
        self.update_commandline_data()
        self.pytest_session_start_auto_dash_configuration()

    def update_commandline_data(self):
        """Updates the command line data based on the options provided."""
        try:
            config_yaml = self.session_store.base_config
            options = self.session.config.option
            attributes = [
                "mobile_platform",
                "selenium_grid_ip",
                "current_execution_browser",
                "chrome_options",
                "firefox_options",
                "edge_options",
                "ie_options",
                "safari_options",
            ]
            attributes_browser_options = [
                "chrome_options",
                "firefox_options",
                "edge_options",
                "ie_options",
                "safari_options",
            ]
            for attr in attributes:
                option_value = getattr(options, attr, None)
                if option_value is not None:
                    if attr in attributes_browser_options:
                        config_yaml[attr] = literal_eval(option_value)
                    else:
                        config_yaml[attr] = option_value
            self.session_store.global_dict["jenkins_build"] = options.jenkins_build
            auto_dashboard_report = options.auto_dashboard_report
            if auto_dashboard_report is not None:
                config_yaml["auto_dashboard_report"] = auto_dashboard_report.lower() == "true"
            if options.config_keys is not None:
                cust_keys = self.session_store.config.option.config_keys
                yaml_data = yaml.safe_load(cust_keys)
                key_lst1 = []
                for cu_k, cu_v in yaml_data.items():
                    if "__" in cu_k:
                        paths = str(cu_k).split("__")
                        key_lst1 = key_lst1 + paths
                        config_yaml = self.set_nested_item(config_yaml, key_lst1, cu_v)
                    else:
                        if cu_k not in config_yaml.keys():
                            pytest.fail("Given :" + cu_k + "  is not available in config.yml")
                        else:
                            config_yaml[cu_k] = cu_v
            execution_environment = (
                options.execution_environment or config_yaml["execution_environment"]
            )
            environment_type = options.environment_type or config_yaml["environment_type"]
            environment = options.environment or config_yaml["env"][execution_environment][
                environment_type
            ].get("base_url", "NA")
            config_yaml["execution_environment"] = execution_environment
            config_yaml["environment_type"] = environment_type
            config_yaml["environment"] = environment
            if options.username and options.password:
                config_yaml["env"][execution_environment][environment_type]["default_user"] = {
                    "username": options.username,
                    "password": options.password,
                }

            if options.default_db_user__username and options.default_db_user__password:
                config_yaml["env"][execution_environment][environment_type]["default_db_user"] = {
                    "username": options.default_db_user__username,
                    "password": options.default_db_user__password,
                }
            # TODO: add the logic for custom_params, config_keys
            self.session_store.base_config = config_yaml
        except Exception as error_in_update_commandline_data:
            self.logger.exception(
                f"Error in update_commandline_data --> {error_in_update_commandline_data}"
            )
            raise error_in_update_commandline_data

    def set_nested_item(self, data, map_list, val_):
        """Updates a nested item in a dictionary.

        This method takes a dictionary, a list of keys representing the path to the nested item, and a value.
        It updates the nested item in the dictionary with the provided value.

        Parameters:
        data (dict): The dictionary containing the nested item.
        map_list (list): The list of keys representing the path to the nested item.
        val_ : The value to update the nested item with.

        Returns:
        dict: The updated dictionary.

        Raises:
        Exception: If there is an error in updating the nested item.
        """
        try:
            functools.reduce(operator.getitem, map_list[:-1], data)[map_list[-1]] = val_
            return data
        except Exception as e:
            self.logger.exception("Error in set_nested_item-->" + str(e))

    @property
    def is_parallel_execution(self):
        """Checks if the pytest session is running in parallel mode.

        This method takes a list of command-line arguments and checks if any of the parallel execution flags are present
        The parallel execution flags are "-c", "-n=", "--tests-per-worker", "--workers", and "-n".

        Parameters:
        args_list (list): The list of command-line arguments.

        Returns:
        bool: True if any of the parallel execution flags are present in the command-line arguments, False otherwise.

        Raises:
        Exception: If there is an error in checking for parallel execution.
        """
        parallel_flags = ["-c", "-n=", "--tests-per-worker", "--workers", "-n"]
        return any(flag in self.sys_arg for flag in parallel_flags)

    def pytest_session_start_auto_dash_configuration(self):
        """Configures the auto dashboard for pytest session."""
        options = self.session.config.option
        execution_id = self.session_store.execution_uuid
        execution_start_time = self.date_time_util.get_current_date_time()
        is_ct_build = "1" if options.jenkins_build else "0"
        os.environ["isCTBuild"] = is_ct_build
        if (
            self.session_worker.lower() == "master"
            or os.environ.get("PYTEST_XDIST_WORKER", "master") == "master"
        ):
            execution_details = {
                "executionId": execution_id,
                "executionStatus": "L",
                "executionStartTime": None,
                "executionEndTime": None,
                "executionDuration": None,
                "executionDurationSeconds": None,
                "totalPassed": 0,
                "totalFailed": 0,
                "runCommands": None,
                "executionTags": None,
                "frameworkVersions": self.get_package_versions(),
                "browser": self.config_utils_web.fetch_current_browser(),
                "isCTBuild": is_ct_build,
                "isReRun": 0,
                "isPerformanceExecution": 0,
            }
            if "rerun_failures" in self.session_store.base_config.keys():
                is_rerun = self.session_store.base_config["rerun_failures"]
                if is_rerun:
                    execution_details["isReRun"] = 1
            str_exec_env = (
                str(self.session_store.base_config["execution_environment"]).strip().lower()
            )
            os.environ["execution_environment"] = str_exec_env
            str_environment_type = self.session_store.base_config["environment_type"]
            os.environ["environment_type"] = str_environment_type
            ct_details = {}
            if options.jenkins_build:
                ct_details.update(
                    {
                        "triggeredBy": options.triggeredby,
                        "jenkinsSlaveName": options.jenkinsslavename,
                        "repoName": options.reponame,
                        "branchName": options.branchname,
                        "devBuildNumber": (
                            None
                            if options.devbuildnumber in ["", "null"]
                            else options.devbuildnumber
                        ),
                        "jobBuildId": options.jenkins_build,
                        "executionStartTime": execution_start_time,
                    }
                )
            str_username = (
                os.environ["userdomain"] + os.sep + os.getlogin()
                if "userdomain" in os.environ
                else os.getlogin()
            )

            execution_details.update(
                {
                    "ctDetails": ct_details,
                    "isDebugExecution": self.get_execution_mode(),
                    "executionStartTime": execution_start_time,
                    "executionEnvironment": str_exec_env,
                    "isGrid": int(self.session_store.base_config.get("use_grid", 0)),
                    "environment": (
                        self.session_store.base_config["environment"]
                        if "environment" in self.session_store.base_config.keys()
                        else None
                    ),
                    "machineName": platform.uname()[1],
                    "user": str_username,
                    "isParallel": True if self.session_store.workers_count > 1 else False,
                    "runCommands": self.get_run_commands(),
                }
            )
            prefixes = ["-m=", "-k="]
            for prefix in prefixes:
                for arg in self.sys_arg:
                    if arg.startswith(prefix):
                        execution_details["executionTags"] = arg.replace(prefix, "")
                    elif arg == prefix.strip("="):
                        execution_details["executionTags"] = self.sys_arg[
                            self.sys_arg.index(arg) + 1
                        ]
            self.file_handler_obj.create_json_file(
                self.session_store.temp_execution_dir, "execution.json", execution_details
            )

    def get_run_commands(self):
        run_commands = list(self.sys_arg).copy()
        str_set_args = set(run_commands)
        for str_argument in str_set_args:
            str_argument = str(str_argument)
            if "pytest" in str_argument or "py.test" in str_argument:
                run_commands.remove(str_argument)
            elif "features" in str_argument and "tests" in str_argument:
                last_forward_slash = str(str_argument).rfind("/")
                last_backward_slash = str(str_argument).rfind("\\")
                str_arg = str(str_argument)[max(last_forward_slash, last_backward_slash) + 1 :]
                run_commands.remove(str_argument)
                run_commands.append(str_arg)
            elif "python" in str_argument:
                run_commands.remove(str_argument)
        return run_commands

    def re_run_data(self):
        var_rerun = self.session_store.base_config
        is_rerun = self.session_store.base_config.get("rerun_failures", False)
        if is_rerun:
            if "--lf" not in sys.argv:
                var_master = os.environ.get("execution_id")
                master_id = var_master
                parent_id = "NA"
                if "rerun_failures_count" in self.session_store.base_config.keys():
                    var_rerun["rerun_iteration"] = "NA"
                    int_re = self.session_store.base_config["rerun_failures_count"]
                    if int_re > 5:
                        var_rerun["rerun_failures_count"] = 5
                self.session_store.base_config = var_rerun
        else:
            var_rerun["rerun_iteration"] = "NA"
            self.session_store.base_config = var_rerun
        rerun_data = self.session_store.base_config
        if "rerun_failures" not in self.session_store.base_config.keys():
            config_yaml_re_del = self.session_store.base_config
            if "rerun_failures_count_dummy" in self.session_store.base_config.keys():
                config_yaml_re_del.popf("rerun_failures_count_dummy")
                self.session_store.base_config = config_yaml_re_del
        if "rerun_failures" in self.session_store.base_config.keys():
            config_yaml_re_del1 = self.session_store.base_config
            rerun_value = self.session_store.base_config["rerun_failures"]
            if not rerun_value:
                if "rerun_failures_count_dummy" in self.session_store.base_config.keys():
                    config_yaml_re_del1.pop("rerun_failures_count_dummy")
                    self.session_store.base_config = config_yaml_re_del1
            # Below condition is to handle when pytest is triggered in parallel - makes sure only one session is created
            dir_path = os.path.join(
                self.config_utils.get_project_path(), ".pytest_cache/v/cache/lastfailed"
            )
            if os.path.exists(dir_path):
                os.remove(dir_path)
            if "--lf" not in sys.argv:
                if "rerun_failures_count" in self.session_store.base_config.keys() and is_rerun:
                    re_run_val = self.session_store.base_config["rerun_failures_count"]
                    config_yaml = self.session_store.base_config
                    if "rerun_failures_count_dummy" not in self.session_store.base_config.keys():
                        config_yaml["rerun_failures_count_dummy"] = re_run_val
                    elif "rerun_failures_count_dummy" in self.session_store.base_config.keys():
                        config_yaml["rerun_failures_count_dummy"] = re_run_val
                    self.session_store.base_config = config_yaml
                if os.path.isdir(
                    os.path.join(self.config_utils.get_project_path(), ".pytest_cache")
                ):
                    shutil.rmtree(self.config_utils.get_project_path() + "/" + ".pytest_cache")

    def get_execution_mode(self):
        """
        Description: This method is called
        :return:
        """
        try:
            debug_execution = self.session_store.base_config.get("is_debug_execution", False)
            if debug_execution:
                if str(debug_execution) in ("True", "true", "TRUE"):
                    return 1
            else:
                self.logger.warning(
                    "Warning!!! Please add 'is_debug_execution' key in config.yml file. "
                    "This will ensure there is no junk data in Reporting"
                )
                return 0
            if "Debug" in str(sys.stdin):
                return 1
            else:
                return 0
        except Exception as e:
            self.logger.error("Error occurred in get_execution_mode -->" + str(e))

    @staticmethod
    def get_package_versions():
        packages = ["cafex", "cafex-core", "cafex-api", "cafex-db", "cafex-ui", "cafex-desktop"]
        versions = {}
        for package in packages:
            try:
                version = importlib.metadata.version(package)
                versions[package] = version
            except importlib.metadata.PackageNotFoundError:
                versions[package] = "NA"
        return versions
