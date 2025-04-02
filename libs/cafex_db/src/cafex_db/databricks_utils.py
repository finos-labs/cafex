import base64
import json
import os
import time

import requests
from cafex_core.logging.logger_ import CoreLogger
from cafex_core.utils.core_security import Security
from cafex_core.utils.exceptions import CoreExceptions
from cafex_core.utils.pyglobals import PyGlobals
from pyhive import hive
from requests.auth import HTTPBasicAuth
from thrift.transport import THttpClient


class DatabricksUtils:
    """
    Description:
        |  This Class provides methods to automate different scenarios related to spark, delta lake executed through
        Databricks Rest API
    """

    def __init__(self, pstr_databricks_url, pstr_access_token=None):
        self.__obj_generic_exception = CoreExceptions()
        self.__databricks_api_version = "2.0"
        self.__databricks_api_path = pstr_databricks_url + "/api/" + self.__databricks_api_version
        self.databricks_access_token = pstr_access_token
        self.hive_connection = None
        self.context_id = None
        self.logger = CoreLogger(name=__name__).get_logger()
        self.security = Security()

    def list_dbfs_files(self, pstr_dbfs_path):
        """
        Description:
                |  This method is used to get the list of files at given dbfs path.

        :param pstr_dbfs_path: DBFS path in databricks
        :type pstr_dbfs_path: String

        :return: boolean, list - Tuple without parentheses indicating 'execution_result' and list object which contains
        the list of files at given dbfs path
        Examples:
                |  list_dbfs_files("/FileStore/mdata-1/")

        """
        try:
            str_api_method = "GET"
            dict_api_header = {"Content-Type": "application/json"}
            dict_api_header["Authorization"] = "Bearer " + self.databricks_access_token
            str_resource = "/dbfs/list"
            pstr_uri = self.__databricks_api_path + str_resource
            pstr_payload = {"path": pstr_dbfs_path}
            obj_response = self.call_request(
                str_api_method, pstr_uri, dict_api_header, pstr_payload=json.dumps(pstr_payload)
            )
            if obj_response.status_code == 200:
                return True, obj_response.json()
            return False, None
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def upload_files_in_dbfs(self, pstr_src_path, pstr_dbfs_path):
        """
        Description:
                |  This method is used to upload files from the source path to the given dbfs path.

        :param pstr_src_path: Source Path for the File to upload
        :type pstr_src_path: String
        :param pstr_dbfs_path: DBFS path
        :type pstr_dbfs_path: String

        :return: boolean - Indicating the result whether file is uploaded successully or not.
        Examples:
                |  upload_files_in_dbfs( "\queries\data_ingestion_pipeline\DatabricksApps-0.0.7-SNAPSHOT.jar", "/FileStore/mdata-1/")
                |  upload_files_in_dbfs( "\testdata\data_ingestion_pipeline\student.csv", "/FileStore/mdata-1/")

        .. note::
                |  Please don't include the name of file in 'pstr_dbfs_path' parameter. Refer Examples

        """
        try:
            str_api_method = "POST"
            dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
            str_resource = "/dbfs/put"
            pstr_uri = self.__databricks_api_path + str_resource
            file_name = os.path.basename(pstr_src_path)
            if file_name != "":
                with open(pstr_src_path, "rb") as fp:
                    file_data = fp.read()
                pstr_payload = {"path": pstr_dbfs_path + file_name, "overwrite": "true"}
                pstr_files = {"filefield": (file_name, file_data)}
                obj_response = self.call_request(
                    str_api_method,
                    pstr_uri,
                    dict_api_header,
                    pstr_payload=pstr_payload,
                    pstr_files=pstr_files,
                )
                if obj_response.status_code == 200:
                    return True
                self.logger.info("Not a valid response code.")
                return False
            else:
                self.logger.info("FileName not present in source path")
                return False
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def create_notebook(self, pstr_file_path, pstr_workspace_path, pstr_language="PYTHON"):
        """
        Description:
                |  This method is used to create a notebook in databricks workspace.

        :param pstr_file_path: Source file path for databricks notebook
        :type pstr_file_path: String
        :param pstr_workspace_path: Target Workspace path where notebook will be created
        :type pstr_workspace_path: String
        :param pstr_language: Coding Language used (Optional parameter with default value 'PYTHON')
        :type pstr_language: String

        :return: boolean - Indicating the result whether notebook is successully created or not.
        Examples:
                |  create_notebook("\queries\data_ingestion_pipeline\sample.py", "/Shared/mdata/sample")
                |  create_notebook("\queries\data_ingestion_pipeline\sample.py", "/Shared/mdata/sample", pstr_language="PYTHON")

        """
        try:
            str_api_method = "POST"
            dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
            str_resource = "/workspace/import"
            pstr_uri = self.__databricks_api_path + str_resource
            with open(pstr_file_path, "rb") as fp:
                file_data = fp.read()
                encoded_data = base64.b64encode(file_data)
            decoded_data = encoded_data.decode("utf-8")
            pstr_payload = {
                "path": pstr_workspace_path,
                "format": "SOURCE",
                "language": pstr_language,
                "content": decoded_data,
                "overwrite": "false",
            }
            obj_response = self.call_request(
                str_api_method, pstr_uri, dict_api_header, pstr_payload=json.dumps(pstr_payload)
            )
            if obj_response.status_code == 200:
                return True
            return False
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def check_notebook(self, pstr_workspace_path):
        """
        Description:
                |  This method is to check if the notebook exists at the given workspace path

        :param pstr_workspace_path: Databricks Workspace Path
        :type pstr_workspace_path: String

        :return: boolean - Indicating the result whether notebook actually exists at the given databricks workspace path
        Examples:
                |  check_notebook("/Shared/mdata/sample")

        """
        try:
            str_api_method = "GET"
            dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
            str_resource = "/workspace/get-status"
            pstr_uri = self.__databricks_api_path + str_resource
            pstr_payload = {"path": pstr_workspace_path}
            obj_response = self.call_request(
                str_api_method, pstr_uri, dict_api_header, pstr_payload=json.dumps(pstr_payload)
            )
            if obj_response.status_code == 200:
                if obj_response.json()["object_type"] == "NOTEBOOK":
                    return True
            return False
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def delete_notebook(self, pstr_workspace_path, pbln_recursive=False):
        """
        Description:
                |  This method is to delete the notebook exists at the given workspace path

        :param pstr_workspace_path: Databricks Workspace Path
        :type pstr_workspace_path: String
        :param pbln_recursive: An optional boolean parameter to delete recursively all the files at given workspace path
         (default Value: False)
        :type pbln_recursive: Boolean

        :return: boolean - Indicating the result whether notebook actually deleted at the given databricks workspace
        path or not.
        Examples:
                |  delete_notebook("/Shared/mdata/sample")
                |  delete_notebook("/Shared/mdata/", True)

        """
        try:
            str_api_method = "POST"
            dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
            str_resource = "/workspace/delete"
            pstr_uri = self.__databricks_api_path + str_resource
            pstr_payload = {"path": pstr_workspace_path, "recursive": pbln_recursive}
            obj_response = self.call_request(
                str_api_method, pstr_uri, dict_api_header, pstr_payload=json.dumps(pstr_payload)
            )
            if obj_response.status_code == 200:
                return True
            return False
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def list_clusters(self):
        """
        Description:
                |  This method is to get the list of clusters in the Databricks

        :return: boolean, list - Tuple without parentheses indicating 'execution_result' and list object which contains
         the list of clusters in databricks
        Examples:
                |  list_clusters()

        """
        try:
            str_api_method = "GET"
            dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
            str_resource = "/clusters/list"
            pstr_uri = self.__databricks_api_path + str_resource
            obj_response = self.call_request(str_api_method, pstr_uri, dict_api_header)
            if obj_response.status_code == 200:
                return True, obj_response.json()
            return False, None
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def get_cluster_id(self, pstr_cluster_name):
        """
        Description:
                |  This method is used to get the cluster id with the name

        :param pstr_cluster_name: Databricks Cluster Name
        :type pstr_cluster_name: String

        :return: String - Cluster Id
        Examples:
                |  get_cluster_id("databricks-dev-training-spark2")

        """
        try:
            str_cluster_id = None
            execution, response_cluster_list = self.list_clusters()
            if execution:
                data = next(
                    (
                        cluster
                        for cluster in response_cluster_list["clusters"]
                        if cluster["cluster_name"].lower() == pstr_cluster_name.lower()
                    ),
                    None,
                )
                if data is not None:
                    str_cluster_id = data["cluster_id"]
            return str_cluster_id
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def get_cluster(self, pstr_cluster_id):
        """
        Description:
                |  This method is used to get the cluster

        :param pstr_cluster_id: Databricks Cluster Id
        :type pstr_cluster_id: String

        :return: boolean, dict - Tuple without parentheses indicating 'execution_result' and dictionary object
        which contains the details of cluster
        Examples:
                |  get_cluster("0715-113640-giddy195")

        """
        try:
            str_api_method = "GET"
            dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
            str_resource = "/clusters/get"
            pstr_uri = self.__databricks_api_path + str_resource
            pstr_payload = {"cluster_id": pstr_cluster_id}
            obj_response = self.call_request(
                str_api_method, pstr_uri, dict_api_header, pstr_payload=json.dumps(pstr_payload)
            )
            if obj_response.status_code == 200:
                return True, obj_response.json()
            return False, None
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def start_cluster(self, pstr_cluster_id):
        """
        Description:
                |  This method is used to start the cluster

        :param pstr_cluster_id: Databricks Cluster Id
        :type pstr_cluster_id: String

        :return: boolean - True/False indicating 'execution_result' from the api response
        Examples:
                |  start_cluster("0715-113640-giddy195")

        """
        try:
            str_api_method = "POST"
            dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
            str_resource = "/clusters/start"
            pstr_uri = self.__databricks_api_path + str_resource
            pstr_payload = {"cluster_id": pstr_cluster_id}
            obj_response = self.call_request(
                str_api_method, pstr_uri, dict_api_header, pstr_payload=json.dumps(pstr_payload)
            )
            if obj_response.status_code == 200:
                return True
            return False
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def restart_cluster(self, pstr_cluster_id):
        """
        Description:
                |  This method is used to restart cluster in databricks

        :param pstr_cluster_id: Databricks Cluster Id
        :type pstr_cluster_id: String

        :return: boolean - True/False indicating 'execution_result' from the api response
        Examples:
                |  restart_cluster("0715-113640-giddy195")

        """
        try:
            str_api_method = "POST"
            dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
            str_resource = "/clusters/restart"
            pstr_uri = self.__databricks_api_path + str_resource
            pstr_payload = {"cluster_id": pstr_cluster_id}
            obj_response = self.call_request(
                str_api_method, pstr_uri, dict_api_header, pstr_payload=json.dumps(pstr_payload)
            )
            if obj_response.status_code == 200:
                return True
            return False
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def stop_cluster(self, pstr_cluster_id):
        """
        Description:
                |  This method is used to stop cluster in databricks

        :param pstr_cluster_id: Databricks Cluster Id
        :type pstr_cluster_id: String

        :return: boolean - True/False indicating 'execution_result' from the api response
        Examples:
                |  stop_cluster("0715-113640-giddy195")

        """
        try:
            str_api_method = "POST"
            dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
            str_resource = "/clusters/delete"
            pstr_uri = self.__databricks_api_path + str_resource
            pstr_payload = {"cluster_id": pstr_cluster_id}
            obj_response = self.call_request(
                str_api_method, pstr_uri, dict_api_header, pstr_payload=json.dumps(pstr_payload)
            )
            if obj_response.status_code == 200:
                return True
            return False
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def delete_cluster(self, pstr_cluster_id):
        """
        Description:
                |  This method is used to permanently delete cluster in databricks

        :param pstr_cluster_id: Databricks Cluster Id
        :type pstr_cluster_id: String

        :return: boolean - True/False indicating 'execution_result' from the api response
        Examples:
                |  delete_cluster("0715-113640-giddy195")

        """
        try:
            str_api_method = "POST"
            dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
            str_resource = "/clusters/permanent-delete"
            pstr_uri = self.__databricks_api_path + str_resource
            pstr_payload = {"cluster_id": pstr_cluster_id}
            obj_response = self.call_request(
                str_api_method, pstr_uri, dict_api_header, pstr_payload=json.dumps(pstr_payload)
            )
            if obj_response.status_code == 200:
                return True, obj_response.json()
            return False, None
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def create_cluster(self, pdict_payload):
        """
        Description:
                |  This method is used to create cluster in databricks

        :param pdict_payload: dictionary payload to create a cluster
        :type pdict_payload: dictionary

        :return: boolean, dict - Tuple without parentheses indicating 'execution_result' and dictionary object
        .. note::
                |  For creating a cluster, the user needs to have create permissions on databricks.

        """
        try:
            str_api_method = "POST"
            dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
            str_resource = "/clusters/create"
            pstr_uri = self.__databricks_api_path + str_resource
            obj_response = self.call_request(
                str_api_method, pstr_uri, dict_api_header, pstr_payload=json.dumps(pdict_payload)
            )
            if obj_response.status_code == 200:
                return True, obj_response.json()
            return False, None
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def delete_dbfs_path(self, pstr_dbfs_path, pbln_recursive=False):
        """
        Description:
                |  This method is used to delete file at dbfs path

        :param pstr_dbfs_path: dbfs path
        :type pstr_dbfs_path: String
        :param pbln_recursive: Boolean parameter for deleting the files recursively at given dbfs path
        (default value: False)
        :type pbln_recursive: Boolean

        :return: boolean - True/False indicating 'execution_result' from the api response
        Examples:
                |  delete_dbfs_path("/FileStore/mdata-1/users-11.csv")
                |  delete_dbfs_path("/FileStore/mdata-1", True)

        """
        try:
            str_api_method = "POST"
            dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
            str_resource = "/dbfs/delete"
            pstr_uri = self.__databricks_api_path + str_resource
            pstr_payload = {"path": pstr_dbfs_path, "recursive": pbln_recursive}
            obj_response = self.call_request(
                str_api_method, pstr_uri, dict_api_header, pstr_payload=json.dumps(pstr_payload)
            )
            if obj_response.status_code == 200:
                return True
            return False
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def create_job(self, pdict_payload):
        """
        Description:
                |  This method is used to create a spark job in databricks

        :param pdict_payload: dictionary payload to create a data processing job
        :type pdict_payload: dictionary

        :return: boolean, dict - Tuple without parentheses indicating 'execution_result' and dictionary object
        """
        try:
            str_api_method = "POST"
            dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
            str_resource = "/jobs/create"
            pstr_uri = self.__databricks_api_path + str_resource
            obj_response = self.call_request(
                str_api_method, pstr_uri, dict_api_header, pstr_payload=json.dumps(pdict_payload)
            )
            if obj_response.status_code == 200:
                return True, obj_response.json()
            return False, None
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def delete_job(self, pint_job_id):
        """
        Description:
                |  This method is used to delete a spark job in databricks

        :param pint_job_id: spark job id
        :type pint_job_id: integer

        :return: boolean - True/False indicating 'execution_result' from the api response
        Examples:
                |  delete_job(34343)

        """
        try:
            str_api_method = "POST"
            dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
            str_resource = "/jobs/delete"
            pstr_uri = self.__databricks_api_path + str_resource
            dict_payload = {"job_id": pint_job_id}
            obj_response = self.call_request(
                str_api_method, pstr_uri, dict_api_header, pstr_payload=json.dumps(dict_payload)
            )
            if obj_response.status_code == 200:
                return True
            return False
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def list_jobs(self):
        """
        Description:
                |  This method is used to all the spark jobs in databricks

        :return: boolean, dict - Tuple without parentheses indicating 'execution_result' and dictionary object which
         contains the details of all the jobs
        Examples:
                |  list_jobs()

        """
        try:
            str_api_method = "GET"
            dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
            str_resource = "/jobs/list"
            pstr_uri = self.__databricks_api_path + str_resource
            obj_response = self.call_request(str_api_method, pstr_uri, dict_api_header)
            if obj_response.status_code == 200:
                return True, obj_response.json()
            return False, None
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def get_job_id(self, pstr_job_name):
        """
        Description:
                |  This method is used to get the spark job id with it's name.

        :param pstr_job_name: Spark Job name
        :type pstr_job_name: String

        :return: boolean, dict - Tuple without parentheses indicating 'execution_result' and spark job id.
        Examples:
                |  get_job_id("Student_analysis_job")

        """
        try:
            job_id = None
            execution, response_jobs_list = self.list_jobs()
            if execution:
                data = next(
                    (
                        job
                        for job in response_jobs_list["jobs"]
                        if job["settings"]["name"].lower() == pstr_job_name.lower()
                    ),
                    None,
                )
                if data is not None:
                    job_id = data["job_id"]
                    return True, job_id
            return False, job_id
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def get_job(self, pint_job_id):
        """
        Description:
                |  This method is used to get the job details with the id

        :param pint_job_id: Spark Job id
        :type pint_job_id: integer

        :return: boolean, dict - Tuple without parentheses indicating 'execution_result' and spark job dictionary object.
        Examples:
                |  get_job(476474)

        """
        try:
            str_api_method = "GET"
            dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
            str_resource = "/jobs/get"
            pstr_uri = self.__databricks_api_path + str_resource
            dict_payload = {"job_id": pint_job_id}
            obj_response = self.call_request(
                str_api_method, pstr_uri, dict_api_header, pstr_payload=json.dumps(dict_payload)
            )
            if obj_response.status_code == 200:
                return True, obj_response.json()
            return False, None
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def execute_job(self, pint_job_id, pdict_params=None):
        """
        Description:
                |  This method is used to execute the spark job

        :param pint_job_id: Spark Job id
        :type pint_job_id: integer
        :param pdict_params: dictionary object which contains all the optional parameters to execute spark job with
        :type pdict_params: dictionary

        :return: boolean, dict - Tuple without parentheses indicating 'execution_result' and dictionary object.
        Examples:
                |  parameter_dict = {
            |    "notebook_params": {
            |        "fileLocation": "/FileStore/mdata-1/users-11.csv"
            |        }
            |    }
                |  execute_job(65656)
                |  execute_job(65656, pdict_params=parameter_dict )

        """
        try:
            str_api_method = "POST"
            dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
            str_resource = "/jobs/run-now"
            pstr_uri = self.__databricks_api_path + str_resource
            dict_payload = {"job_id": pint_job_id}
            if pdict_params is not None:
                for key, value in pdict_params.items():
                    dict_payload[key] = value
            obj_response = self.call_request(
                str_api_method, pstr_uri, dict_api_header, pstr_payload=json.dumps(dict_payload)
            )
            if obj_response.status_code == 200:
                return True, obj_response.json()
            return False, None
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def get_job_output(self, pint_run_id):
        """
        Description:
                |  This method is used to get the job output

        :param pint_job_id: Spark Job id
        :type pint_job_id: integer

        :return: boolean, dict - Tuple without parentheses indicating 'execution_result' and dictionary object.
        Examples:
                |  get_job_output(65655)

        """
        try:
            str_api_method = "GET"
            dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
            str_resource = "/jobs/runs/get-output"
            pstr_uri = self.__databricks_api_path + str_resource
            dict_payload = {"run_id": pint_run_id}
            obj_response = self.call_request(
                str_api_method, pstr_uri, dict_api_header, pstr_payload=json.dumps(dict_payload)
            )
            if obj_response.status_code == 200:
                return True, obj_response.json()
            return False, None
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def read_dbfs_file(self, pstr_dbfs_path, pint_offset=0, pint_length=1000):
        """
        Description:
                |  This method is used to read file from the dbfs path

        :param pstr_dbfs_path: dbfs path
        :type pstr_dbfs_path: String
        :param pint_offset: offset: the point from where to start reading the content
        :type pint_offset: integer
        :param pint_length: length of the content to read in terms of bytes
        :type pint_length: integer

        :return: boolean, dict - Tuple without parentheses indicating 'execution_result' and dictionary object.
        Examples:
                |  read_dbfs_file("/FileStore/mdata-1/users-11.csv", pint_offset=0, pint_length=10000)

        """
        try:
            str_api_method = "GET"
            dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
            str_resource = "/dbfs/read"
            pstr_uri = self.__databricks_api_path + str_resource
            pstr_payload = {"path": pstr_dbfs_path, "offset": pint_offset, "length": pint_length}
            obj_response = self.call_request(
                str_api_method, pstr_uri, dict_api_header, pstr_payload=json.dumps(pstr_payload)
            )
            if obj_response.status_code == 200:
                return True, obj_response.json()
            return False, None
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def __create_context(self, pstr_language, pstr_cluster_id, pstr_version=None):
        """
        Description:
                |  This private method is used to create context id

        :param pstr_language: coding language to be used for e.g. java/python/shell scripting
        :type pstr_language: String
        :param pstr_cluster_id: Cluster id
        :type pstr_cluster_id: String
        :param pstr_version: api version
        :type pstr_version: String

        :return: boolean, dict - Tuple without parentheses indicating 'execution_result' and dictionary object.
        Examples:
                |  __create_context("python", "0107-192239-lobed1", pstr_version = "1.2"):

        .. note::
                |  As of now till date 06/01/2021, this method is executable with api version 1.2 only

        """
        try:
            str_api_path = self.__databricks_api_path
            if pstr_version is not None:
                str_api_path = str_api_path[0 : str_api_path.rfind("/") + 1] + str(pstr_version)
            str_api_method = "POST"
            dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
            str_resource = "/contexts/create"
            pstr_uri = str_api_path + str_resource
            pstr_payload = {"language": pstr_language, "clusterId": pstr_cluster_id}
            obj_response = self.call_request(
                str_api_method, pstr_uri, dict_api_header, pstr_payload=json.dumps(pstr_payload)
            )
            if obj_response.status_code == 200:
                return True, obj_response.json()
            return False, None
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def destroy_context(self, pstr_cluster_id, pstr_version=None):
        """
        Description:
                |  This method is used to destroy context id

        :param pstr_cluster_id: Cluster id
        :type pstr_cluster_id: String
        :param pstr_version: api version
        :type pstr_version: String

        :return: boolean, dict - Tuple without parentheses indicating 'execution_result' and dictionary object.
        Examples:
                |  destroy_context("0107-192239-lobed1", pstr_version = "1.2"):

        .. note::
                |  As of now till date 06/01/2021, this method is executable with api version 1.2 only

        """
        try:
            if self.context_id is not None:
                str_api_path = self.__databricks_api_path
                if pstr_version is not None:
                    str_api_path = str_api_path[0 : str_api_path.rfind("/") + 1] + str(pstr_version)
                str_api_method = "POST"
                dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
                str_resource = "/contexts/destroy"
                pstr_uri = str_api_path + str_resource
                pstr_payload = {"contextId": self.context_id, "clusterId": pstr_cluster_id}
                obj_response = self.call_request(
                    str_api_method, pstr_uri, dict_api_header, pstr_payload=json.dumps(pstr_payload)
                )
                if obj_response.status_code == 200:
                    return True, obj_response.json()
            return False, None
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def execute_command(self, pstr_language, pstr_cluster_id, pstr_command, pstr_version=None):
        """
        Description:
                |  This method is used to execute command

        :param pstr_language: coding language used
        :type pstr_language: String
        :param pstr_cluster_id: Cluster id
        :type pstr_cluster_id: String
        :param pstr_command: Command to be execute in databricks notebook
        :type pstr_command: String
        :param pstr_version: api version
        :type pstr_version: String

        :return: boolean, dict - Tuple without parentheses indicating 'execution_result' and dictionary object.
        Examples:
                |  execute_command("sql", "0107-192239-lobed1", "Select * from users_11_csv limit 1", pstr_version = "1.2")
                |  execute_command("python", "0107-192239-lobed1", "dbutils.fs.ls('/FileStore/mdata-1')", pstr_version = "1.2"):

        .. note::
                |  As of now till date 06/01/2021, this method is executable with api version 1.2 only

        """
        try:
            if self.context_id is None:
                execution, response = self.__create_context(
                    pstr_language, pstr_cluster_id, pstr_version=pstr_version
                )
                if execution:
                    self.context_id = response["id"]
            str_api_path = self.__databricks_api_path
            if pstr_version is not None:
                str_api_path = str_api_path[0 : str_api_path.rfind("/") + 1] + pstr_version
            str_api_method = "POST"
            dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
            str_resource = "/commands/execute"
            pstr_uri = str_api_path + str_resource
            pstr_payload = {
                "language": pstr_language,
                "contextId": self.context_id,
                "clusterId": pstr_cluster_id,
                "command": pstr_command,
            }
            obj_response = self.call_request(
                str_api_method, pstr_uri, dict_api_header, pstr_payload=json.dumps(pstr_payload)
            )
            if obj_response.status_code == 200:
                return True, obj_response.json()
            return False, None
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def command_status(self, pstr_cluster_id, pstr_command_id, pstr_version=None):
        """
        Description:
                |  This method is used to get the status of the command

        :param pstr_cluster_id: Cluster id
        :type pstr_cluster_id: String
        :param pstr_command_id: Command to be execute in databricks notebook
        :type pstr_command_id: String
        :param pstr_version: api version
        :type pstr_version: String

        :return: boolean, dict - Tuple without parentheses indicating 'execution_result' and dictionary object.
        Examples:
                |  command_status( "0107-192239-lobed1", "4KASJSHJ545SAEE", pstr_version = "1.2")
                |

        .. note::
                |  As of now till date 06/01/2021, this method is executable with api version 1.2 only

        """
        try:
            if self.context_id is not None:
                str_api_path = self.__databricks_api_path
                if pstr_version is not None:
                    str_api_path = str_api_path[0 : str_api_path.rfind("/") + 1] + str(pstr_version)
                str_api_method = "GET"
                dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
                str_resource = "/commands/status?clusterId={}&contextId={}&commandId={}".format(
                    pstr_cluster_id, self.context_id, pstr_command_id
                )
                pstr_uri = str_api_path + str_resource
                obj_response = self.call_request(str_api_method, pstr_uri, dict_api_header)
                if obj_response.status_code == 200:
                    return True, obj_response.json()
            return False, None
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def __create_hive_connection(self, pint_workspace_id, pstr_cluster_id):
        """
        Description:
                |  This private method is used to create the connection in order to execute hive queries

        :param pint_workspace_id: workspace id
        :type pint_workspace_id: integer
        :param pstr_cluster_id: Cluster id
        :type pstr_cluster_id: String

        :return: hive connection - This private function will return the hive connection object
        Examples:
                |  __create_hive_connection(7372722, "0107-192239-lobed1")
                |
        """
        try:

            str_api_path = self.__databricks_api_path
            str_api_path = str_api_path[0 : str_api_path.rfind("api") - 1]
            connection_url = "%s/sql/protocolv1/o/%s/%s" % (
                str_api_path,
                pint_workspace_id,
                pstr_cluster_id,
            )
            transport = THttpClient.THttpClient(connection_url)
            transport.setCustomHeaders(
                {"Authorization": "Bearer %s" % self.databricks_access_token}
            )
            hive_connection = hive.connect(thrift_transport=transport).cursor()
            return hive_connection

        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def execute_hive_query(self, pint_workspace_id, pstr_cluster_id, pstr_query):
        """
        Description:
                |  This method is used to execute the hive query

        :param pint_workspace_id: workspace id
        :type pint_workspace_id: integer
        :param pstr_cluster_id: Cluster id
        :type pstr_cluster_id: String
        :param pstr_query: Hive query
        :type pstr_query: String

        :return: lst_data_items - List of data items to be returned from this hive sql query
        Examples:
                |  execute_hive_query(7372722, "0107-192239-lobed1", "Select * from users_11_csv limit 1")
                |

        """
        lst_data_items = []
        try:
            if self.hive_connection is None:
                self.hive_connection = self.__create_hive_connection(
                    pint_workspace_id, pstr_cluster_id
                )
            self.hive_connection.execute(pstr_query)
            for data in self.hive_connection.fetchall():
                lst_data_items.append(list(data))
            return lst_data_items
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def create_access_token(
        self,
        pstr_username,
        pstr_password,
        pstr_auth_type="Basic",
        pint_token_lifetime_seconds=7200,
        pstr_comment="Data Test Automation authorization",
    ):
        """
        Description:
                |  This method is used to create the access token

        :param pstr_username: Databricks username
        :type pstr_username: String
        :param pstr_password: Databricks password
        :type pstr_password: String
        :param pstr_auth_type: User Authorization type
        :type pstr_auth_type: String
        :param pint_token_lifetime_seconds: tokekn lifetime in seconds
        :type pint_token_lifetime_seconds: integer
        :param pstr_comment: Comment for access tokken
        :type pstr_comment: String

        :return: boolean, dict - Tuple without parentheses indicating 'execution_result' and dictionary object.
        Examples:
                |  create_access_token("abc@spglobal.com", "12345678", pstr_auth_type = "Basic",
                |  pint_token_lifetime_seconds = 7200, pstr_comment = "Data Test Automation authorization")
                |

        """
        try:
            str_api_method = "POST"
            # dict_api_header = {'Authorization': 'Bearer ' + self.databricks_access_token}
            str_resource = "/token/create"
            pstr_uri = self.__databricks_api_path + str_resource
            pstr_payload = {
                "lifetime_seconds": pint_token_lifetime_seconds,
                "comment": pstr_comment,
            }
            """obj_response = self.call_request(str_api_method, pstr_uri,
            dict_api_header, pstr_payload=json.dumps(pstr_payload))"""
            obj_response = requests.post(
                pstr_uri,
                auth=HTTPBasicAuth(pstr_username, pstr_password),
                data=json.dumps(pstr_payload),
            )
            if obj_response.status_code == 200:
                return True, obj_response.json()
            return False, None
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def delete_access_token(self, pstr_token_id):
        """
        Description:
                |  This method is used to delete the access token

        :param pstr_token_id: Access Token Id
        :type pstr_token_id: String

        :return: boolean - Boolean value indicating 'execution_result'
        Examples:
                |  delete_access_token("33REE45455Y5H55565")
                |

        """
        try:
            str_api_method = "POST"
            dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
            str_resource = "/token/delete"
            pstr_uri = self.__databricks_api_path + str_resource
            pstr_payload = {"token_id": pstr_token_id}
            obj_response = self.call_request(
                str_api_method, pstr_uri, dict_api_header, pstr_payload=json.dumps(pstr_payload)
            )
            if obj_response.status_code == 200:
                return True
            return False
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def get_token_list(self):
        """
        Description:
                |  This method is used to get the list of tokens

        :return: boolean, dict - Tuple without parentheses indicating 'execution_result' and dictionary object
        containing the list of tokens.
        Examples:
                |  get_token_list()
                |
        """
        try:
            str_api_method = "GET"
            dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
            str_resource = "/token/list"
            pstr_uri = self.__databricks_api_path + str_resource
            obj_response = self.call_request(str_api_method, pstr_uri, dict_api_header)
            if obj_response.status_code == 200:
                return True, obj_response.json()
            return False, None
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def check_job_status_and_wait(self, pint_run_id, pint_retry_count, pint_retry_interval):
        """
        Description: Check the status of a Databricks Job based on a schedule. For e.g. if pint_retry_count = 10 and
        pint_retry_interval = 30, then there will be a total 10*30 = 300 seconds wait time before the methods return
        false.
        :param pint_run_id: Databricks Job Run ID
        :type pint_run_id: String
        :param pint_retry_count: Number of times to retry to check the status
        :type pint_retry_count: int
        :param pint_retry_interval: Time interval between every retry
        :type pint_retry_interval: int
        :return: If the job status is SUCCESS method returns true.
        """
        try:
            bln_job_completed = False
            for int_cnt in range(pint_retry_count):
                bool_job_output_exists, dict_job_output = self.get_job_output(pint_run_id)
                if bool_job_output_exists and (
                    dict_job_output["metadata"]["state"]["life_cycle_state"] == "TERMINATED"
                    or dict_job_output["metadata"]["state"]["life_cycle_state"] == "INTERNAL_ERROR"
                ):
                    str_job_result_state = dict_job_output["metadata"]["state"]["result_state"]
                    if str_job_result_state is not None and str_job_result_state == "FAILED":
                        bln_job_completed = False
                        break
                    if str_job_result_state is not None and str_job_result_state == "SUCCESS":
                        bln_job_completed = True
                        break
                elif not bool_job_output_exists:
                    self.logger.info(
                        "The databricks Job Run ID do not exits or has some issue."
                        + str(pint_run_id)
                    )
                    break
                else:
                    time.sleep(pint_retry_interval)
            return bln_job_completed
        except Exception as ex:
            self.__obj_generic_exception.raise_custom_exception(str(ex))

    def run_job_and_get_run_id(self, pstr_job_id, pdict_notebook_params: dict = None):
        """
        Description: This method runs a databricks job and returns the databricks job run id
        :param pstr_job_id:
        :param pdict_notebook_params:
        :return: Databricks Job Run Id
        """
        try:
            bool_response, obj_response = self.execute_job(pstr_job_id)
            if bool_response:
                PyGlobals().kibana_report.insert_step(
                    "Run databricks Job", "Databricks jobs Ran successfully", "Pass"
                )
                int_run_id = obj_response["run_id"]
                return int_run_id
            else:
                PyGlobals().kibana_report.insert_step(
                    "Run databricks Job", "Failed to Run Databricks Job", "Fail"
                )
                return None
        except Exception as ex:
            self.__obj_generic_exception.raise_custom_exception(str(ex))

    def get_list_of_job_runs(self, pint_job_id, pdict_payload=None):
        """
        Description:
           |  This method is used to list the databriks job runs

        :return: boolean, dict - Tuple without parentheses indicating 'execution_result' and dictionary object which
         contains the details of databricks job runs
        Examples:
           |  dict_payload = {'active_only': 'true', 'job_id': 1234567}
           |  list_job_runs(job_id, dict_payload)
        """
        if pdict_payload is None:
            pdict_payload = {}
        try:
            str_api_method = "GET"
            dict_api_header = {"Authorization": "Bearer " + self.databricks_access_token}
            str_resource = "/jobs/runs/list"
            pstr_uri = self.__databricks_api_path + str_resource
            if "job_id" not in pdict_payload:
                pdict_payload["job_id"] = pint_job_id
            obj_response = self.call_request(
                str_api_method, pstr_uri, dict_api_header, pstr_payload=json.dumps(pdict_payload)
            )
            if obj_response.status_code == 200:
                return True, obj_response.json()
            return False
        except Exception as e:
            self.__obj_generic_exception.raise_generic_exception(
                pstr_message=str(e),
                pbool_insert_kibana=True,
                pbool_trim_log=True,
                pbool_log_local_exceptions=True,
                pbool_fail_on_exception=False,
                pbool_use_pytest_format=True,
            )

    def call_request(self, pstr_method, pstr_url, pdict_headers, **kwargs):
        """Performs various HTTP requests (GET, POST, PUT, PATCH, DELETE).

        Args:
            pstr_method (str): The HTTP method (e.g., 'GET', 'POST').
            pstr_url (str): The request URL.
            pdict_headers (dict): Request headers.

        Kwargs:
            pstr_json (str): JSON data for the request body.
            pstr_payload (dict): Data for the request body.
            pdict_cookies (dict): Cookies for the request.
            pbln_allow_redirects (bool): Allow or disallow redirects.
            pstr_files (str): File path for file uploads.
            pbln_verify (bool): Verify SSL certificates.
            pstr_auth_type (str): Authentication type (e.g., 'basic', 'digest').
            pstr_auth_username (str): Username for authentication.
            pstr_auth_password (str): Password for authentication.
            ptimeout (float or tuple): Timeout in seconds for the request.

        Returns:
            requests.Response: The response object from the request.

        Examples:
            call_request("GET", "https://www.samplesite.com/param1/param2", headers={"Accept":
            "application/json"})
            call_request("POST", "https://www.samplesite.com/param1/param2", headers={"Accept":
            "application/json"}, pstr_payload='{"KOU": "123456"}', pbln_allow_redirects=True)
        """
        try:
            if pstr_url == "":
                raise ValueError("URL cannot be null")
            pstr_json = kwargs.get("pstr_json", None)
            pstr_payload = kwargs.get("pstr_payload", None)
            pdict_cookies = kwargs.get("pdict_cookies", {})
            pbln_allow_redirects = kwargs.get("pbln_allow_redirects", False)
            pstr_files = kwargs.get("pstr_files", None)
            pbln_verify = kwargs.get("pbln_verify", False)
            pstr_auth_type = kwargs.get("pstr_auth_type", None)
            pstr_auth_username = kwargs.get("pstr_auth_username", None)
            pstr_auth_password = kwargs.get("pstr_auth_password", None)
            ptimeout = kwargs.get("ptimeout", None)
            pdict_proxies = kwargs.get("pdict_proxies", None)

            str_auth_string = ""
            if pstr_auth_type is not None:
                str_auth_string = self.security.get_auth_string(
                    pstr_auth_type, pstr_auth_username, pstr_auth_password
                )
            method = pstr_method.upper()
            if method == "GET":
                response = requests.get(
                    pstr_url,
                    headers=pdict_headers,
                    verify=pbln_verify,
                    allow_redirects=pbln_allow_redirects,
                    cookies=pdict_cookies,
                    auth=str_auth_string,
                    data=pstr_payload,
                    json=pstr_json,
                    timeout=ptimeout,
                    proxies=pdict_proxies,
                )
            elif method == "POST":
                if pstr_payload is not None:
                    response = requests.post(
                        pstr_url,
                        headers=pdict_headers,
                        data=pstr_payload,
                        json=pstr_json,
                        verify=pbln_verify,
                        allow_redirects=pbln_allow_redirects,
                        cookies=pdict_cookies,
                        files=pstr_files,
                        auth=str_auth_string,
                        timeout=ptimeout,
                        proxies=pdict_proxies,
                    )
                else:
                    raise Exception("Error-->Payload is missing")
            elif method == "PUT":
                if pstr_payload is not None:
                    response = requests.put(
                        pstr_url,
                        headers=pdict_headers,
                        data=pstr_payload,
                        verify=pbln_verify,
                        allow_redirects=pbln_allow_redirects,
                        cookies=pdict_cookies,
                        files=pstr_files,
                        auth=str_auth_string,
                        timeout=ptimeout,
                        proxies=pdict_proxies,
                    )
                else:
                    raise Exception("Error-->Payload is missing")
            elif method == "PATCH":
                if pstr_payload is not None:
                    response = requests.patch(
                        pstr_url,
                        headers=pdict_headers,
                        data=pstr_payload,
                        verify=pbln_verify,
                        allow_redirects=pbln_allow_redirects,
                        cookies=pdict_cookies,
                        files=pstr_files,
                        auth=str_auth_string,
                        timeout=ptimeout,
                        proxies=pdict_proxies,
                    )
                else:
                    raise Exception("Error-->Payload is missing")
            elif method == "DELETE":
                response = requests.delete(
                    pstr_url,
                    headers=pdict_headers,
                    verify=pbln_verify,
                    allow_redirects=pbln_allow_redirects,
                    cookies=pdict_cookies,
                    auth=str_auth_string,
                    data=pstr_payload,
                    json=pstr_json,
                    timeout=ptimeout,
                    proxies=pdict_proxies,
                )
            else:
                raise ValueError(
                    f"Invalid HTTP method: {method}. Valid options are: GET, POST, PUT, PATCH, DELETE"
                )
            return response
        except Exception as e:
            self.logger.exception(f"Error in API Request: {e}")
            raise e
