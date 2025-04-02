import os
import uuid

import xdist
from cafex_core.handlers.folder_handler import FolderHandler
from cafex_core.logging.logger_ import CoreLogger
from cafex_core.singletons_.session_ import SessionStore


class HookUtil:
    def __init__(self):
        self.logger_class = CoreLogger(name=__name__)
        self.logger = self.logger_class.get_logger()
        self.folder_handler = FolderHandler()
        self.session_store = SessionStore()

    @staticmethod
    def get_xdist_worker_id(request_):
        return xdist.get_xdist_worker_id(request_)

    @staticmethod
    def is_worker(request_):
        return xdist.is_xdist_worker(request_)

    @staticmethod
    def is_xdist_controller(request_):
        return xdist.is_xdist_controller(request_)

    @staticmethod
    def workers_count():
        return os.getenv("PYTEST_XDIST_WORKER_COUNT")

    @staticmethod
    def is_master_process():
        return os.environ.get("PYTEST_XDIST_WORKER", "master") == "master"

    def get_or_create_execution_uuid(self):
        if self.is_master_process():
            execution_uuid = str(uuid.uuid4())
            os.environ["execution_id"] = execution_uuid
            return execution_uuid
        return os.environ.get("execution_id")

    def create_folders(self, conf_cwd):
        execution_uuid = os.environ.get("execution_id")
        result_dir = self.folder_handler.create_folder(conf_cwd, "result")
        execution_dir = self.folder_handler.create_folder(result_dir, execution_uuid)
        logs_dir = self.folder_handler.create_folder(execution_dir, "logs")
        screenshots_dir = self.folder_handler.create_folder(execution_dir, "screenshots")
        temp_dir = self.folder_handler.create_folder(conf_cwd, "temp")
        temp_execution_dir = self.folder_handler.create_folder(temp_dir, execution_uuid)

        # Store paths in environment variables
        os.environ["RESULT_DIR"] = result_dir
        os.environ["EXECUTION_DIR"] = execution_dir
        os.environ["LOGS_DIR"] = logs_dir
        os.environ["SCREENSHOTS_DIR"] = screenshots_dir
        os.environ["TEMP_DIR"] = temp_dir
        os.environ["TEMP_EXECUTION_DIR"] = temp_execution_dir

    def set_paths_from_env(self):
        # Set paths in session store from environment variables
        self.session_store.result_dir = os.environ.get("RESULT_DIR")
        self.session_store.execution_dir = os.environ.get("EXECUTION_DIR")
        self.session_store.logs_dir = os.environ.get("LOGS_DIR")
        self.session_store.screenshots_dir = os.environ.get("SCREENSHOTS_DIR")
        self.session_store.temp_dir = os.environ.get("TEMP_DIR")
        self.session_store.temp_execution_dir = os.environ.get("TEMP_EXECUTION_DIR")

    def is_parallel_execution(self, args_list):

        try:
            is_parallel = None
            if "-c" in args_list:
                is_parallel = True
            for i in args_list:
                if "-n=" in i:
                    is_parallel = True
                    break
                if "--tests-per-worker" in i:
                    is_parallel = True
                    break
                if "--workers" in i:
                    is_parallel = True
                    break
                if "-n" == i:
                    is_parallel = True
                    break
            return is_parallel
        except Exception as e:
            self.logger.exception("Error in is_parallel_execution-->" + str(e))

    def get_feature_file_and_its_name(self, feature):
        try:
            filename = feature.rel_filename
            int_last_slash = max(filename.rfind("/"), filename.rfind("\\"))
            feature_file = filename[int_last_slash + 1 :].replace(".feature", "")
            feature_name = feature.name.replace('"', "").replace("'", "")
            feature_file_plus_feature_name = f"{feature_file} :: {feature_name}"
            return feature_file, feature_file_plus_feature_name
        except Exception as error_get_feature_file_and_its_name:
            self.logger.error(
                "Error occurred in get_feature_file_and_its_name-->"
                + str(error_get_feature_file_and_its_name)
            )

    def pop_value_from_globals(self, pstr_pop_value):
        try:
            if pstr_pop_value in globals():
                globals().pop(pstr_pop_value)
        except Exception as e:
            self.logger.error("Error occurred in pop_value_from_globals-> " + str(e))
