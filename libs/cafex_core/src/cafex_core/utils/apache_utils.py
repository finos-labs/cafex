"""
This module provides automation support for Apache NiFi.
"""
import json
import time
from typing import Any
import nipyapi
import requests
from cafex_core.parsers.json_parser import ParseJsonData
from cafex_core.utils.core_security import Security
from cafex_core.reporting_.reporting import Reporting
from cafex_core.utils.exceptions import CoreExceptions
from cafex_core.logging.logger_ import CoreLogger


class ApacheNifiUtils:
    """
    Description:
        |   This Class provides automation support for Apache Nifi. User can interact with
        Nifi processors by using this Class.
        |   Apache NiFi is an open source software for automating and managing the flow of data
        between systems.
        |   It's a powerful and reliable system to process and distribute data.
        |   It provides a web-based User Interface for creating, monitoring, & controlling
        data flows.
    """

    def __init__(self, pstr_nifi_url, pstr_nifi_registry_url=None):
        self.reporting = Reporting()
        self.__obj_exception = CoreExceptions()
        self.__nifi_token = None
        self.nifi_module = nipyapi
        self.logger = CoreLogger(name=__name__).get_logger()
        self.security = Security()

        nipyapi.config.nifi_config.verify_ssl = False  # Set to True if using valid SSL
        nipyapi.config.nifi_config.host = pstr_nifi_url  # Use the provided URL directly

        self.apis = {
            "flow_api": self.nifi_module.nifi.apis.flow_api.FlowApi(),
            "flowfile_queues_api": self.nifi_module.nifi.apis.
            flowfile_queues_api.FlowfileQueuesApi(),
            "access_api": nipyapi.nifi.apis.access_api.AccessApi()
        }

        if pstr_nifi_registry_url is not None:
            nipyapi.config.registry_config.host = (
                    pstr_nifi_registry_url + "/nifi-registry-api"
            )

    def check_processor_status(self, processor_id: str) -> bool:
        """
        Checks the status of a processor.

        Args:
            processor_id (str): NiFi processor ID.

        Returns:
            bool: True if the processor is available with a 200 response; otherwise, False.

        Examples:
            >> status = ApacheUtils.Nifi().
            check_processor_status("f03899a8-0193-1000-d8fc-53112a5e7c3a")
        """
        try:
            processor_status_entity = self.apis.get("flow_api").get_processor_status(processor_id)
            self.logger.info("API response for processor status: %s", processor_status_entity)
            if processor_status_entity.processor_status.to_dict():
                self.reporting.insert_step(
                    f"Successfully returned processor status for {processor_id}",
                    "Successfully returned processor status",
                    "Pass",
                )
                self.logger.info("Successfully returned processor status for %s.",
                                 processor_id)
                return True
            self.reporting.insert_step(
                "Processor status retrieval",
                f"Processor with ID {processor_id} does not exist or is not "
                f"available.", "Fail", )
            self.logger.error("Processor with ID %s does not exist or is not available.",
                              processor_id)
            return False
        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while checking status for processor " \
                            f"{processor_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False

    def check_process_group_status(self, process_group_id: str) -> bool:
        """
        Checks the status of a process group.

        Args:
            process_group_id (str): NiFi process group ID.

        Returns:
            bool: True if the process group status is available; otherwise, False.

        Examples:
            >> status = ApacheUtils.Nifi().check_process_group_status("process_group_id")
        """
        try:
            process_group_entity = self.apis.get("flow_api"). \
                get_process_group_status(process_group_id)
            self.logger.info("API response for process group status: %s", process_group_entity)
            if process_group_entity.process_group_status.to_dict():
                self.reporting.insert_step(
                    "Successfully returned process group status",
                    "Successfully returned process group status",
                    "Pass",
                )
                self.logger.info("Successfully returned process group status for ID: %s."
                                 , process_group_id)
                return True
            self.reporting.insert_step(
                "Process group status retrieval",
                "Unable to get process group status",
                "Fail",
            )
            self.logger.warning("Unable to get process group status for ID: %s"
                                , process_group_id)
            return False

        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while checking status for process group " \
                            f"{process_group_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False

    def change_process_group_state(self, process_group_id: str, state: bool = True) -> bool:
        """
        Changes the status of a NiFi process group.

        Args:
            process_group_id (str): NiFi process group ID.
            state (bool): True to schedule the process group; False to unschedule.

        Returns:
            bool: True if the state change was successful; otherwise, False.

        Examples:
            >> result = ApacheUtils.Nifi().
            change_process_group_state("process_group_id", True)
        """
        try:
            run_status = nipyapi.canvas.schedule_process_group(process_group_id,
                                                               scheduled=state)
            if run_status:
                self.reporting.insert_step(
                    f"Successfully changed process group state to {state}",
                    "Successfully changed process group state",
                    "Pass",
                )
                self.logger.info("Process group %s state changed to %s.",
                                 process_group_id, state)
                return True
            self.reporting.insert_step(
                f"Failed to change process group state to {state}",
                "Failed to change process group state",
                "Fail",
            )
            self.logger.warning("Failed to change process group %s state to %s."
                                , process_group_id, state)
            return False

        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while changing state for process group " \
                            f"{process_group_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False

    def change_processor_state(self, server_name: str, payload: str, nifi_id: str) -> bool:
        """
        Starts or stops a NiFi processor.

        Args:
            server_name (str): NiFi server name.
            payload (str): Processor payload.
            nifi_id (str): NiFi processor ID.

        Returns:
            bool: True if the operation was successful; otherwise, False.

        Examples:
            >> result = ApacheUtils.Nifi().change_processor_state("http://localhost:8080",
            payload, "processor_id")
        """
        try:
            api_method = "PUT"
            api_header = {"Content-Type": "application/json"}
            method_path = "/nifi-api/flow/process-groups/"
            request_url = f"{server_name}{method_path}{nifi_id}"
            response = self.call_request(
                api_method, request_url, api_header, pstr_payload=payload
            )
            self.logger.debug("Response from NiFi API: %s", response.content.decode('utf-8'))
            if response.status_code == 200:
                self.logger.info("Successfully changed processor state for ID: %s", nifi_id)
                return True
            self.logger.warning("Failed to change processor state for ID: %s ."
                                "Response: %s", nifi_id,
                                response.content.decode('utf-8'))
            return False
        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while changing processor state for " \
                            f"ID {nifi_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False

    def change_nifi_processor_state(self, nifi_server: str,
                                    processor_id: str, state: str) -> bool:
        """
        Changes the status of a NiFi processor.

        Args:
            nifi_server (str): Server name.
            processor_id (str): NiFi process ID.
            state (str): RUNNING or STOPPED.

        Returns:
            bool: True if the operation was successful; otherwise, False.

        Examples:
            >> result = ApacheUtils.Nifi().
            change_nifi_processor_state("http://localhost:8080", "processor_id",
            "RUNNING")
        """
        try:
            nifi_server = nipyapi.config.nifi_config.host
            processor = self.__get_processor(processor_id)
            is_scheduled = str.upper(state) == "RUNNING"
            run_status = nipyapi.canvas.schedule_processor(processor[1], scheduled=is_scheduled)
            if run_status:
                self.reporting.insert_step(
                    f"Processor state: {state} should be changed for {nifi_server}",
                    f"Successfully changed processor state: {state}",
                    "Pass",
                )
                self.logger.info("Successfully changed processor %s state to %s."
                                 , processor_id, state)
                return True
            self.reporting.insert_step(
                f"Failed to change processor state: {state}",
                "Failed to change processor state",
                "Fail",
            )
            self.logger.warning("Failed to change processor %s state to %s."
                                , processor_id, state)
            return False

        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while changing state for processor " \
                            f"{processor_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False

    def about_nifi(self, server_name: str) -> bool:
        """
        Retrieves details about this NiFi.

        Args:
            server_name (str): NiFi server name.

        Returns:
            bool: True if the operation was successful, otherwise False.

        Examples:
            >> info = ApacheUtils.Nifi().about_nifi("http://localhost:8080")
        """
        try:
            str_api_method = "GET"
            api_header = {"Content-Type": "application/json"}
            method_path = "/nifi-api/flow/about"
            request_url = f"{server_name}{method_path}"
            if self.__nifi_token is not None:
                api_header["Authorization"] = self.__nifi_token
            obj_response = self.call_request(str_api_method, request_url, api_header)
            if obj_response.status_code == 200:
                self.reporting.insert_step(
                    "Successfully retrieved info about NiFi",
                    "Successfully retrieved info about NiFi",
                    "Pass",
                )
                return True
            self.reporting.insert_step(
                "Unable to get info about NiFi",
                "Failed to retrieve info about NiFi",
                "Fail",
            )
            return False

        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while retrieving NiFi info: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False

    def get_flow_files_queue_details(self, connection_id: str) -> list | bool:
        """
        Provides a list of files present in a NiFi queue.

        Args:
            connection_id (str): NiFi connection ID.

        Returns:
            list: List containing the details of all files, or False if an error occurs.

        Examples:
            >> files = ApacheUtils.Nifi().get_flow_files_queue_details("connection_id")
        """
        try:
            obj_listing_request_entity = self.apis.get("flowfile_queues_api"). \
                create_flow_file_listing(connection_id)
            str_uri = obj_listing_request_entity.listing_request.uri
            list_flow_files = self.__get_flow_file_details(str_uri)
            return list_flow_files
        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while retrieving flow files for connection ID " \
                            f"{connection_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False

    def __get_flow_file_details(self, uri: str) -> list | bool:
        """
        Returns a list of files present in a NiFi queue.

        Args:
            uri (str): URI received after capturing details.

        Returns:
            list: List of files, or False if an error occurs.

        Examples:
            >> files = self.__get_flow_file_details("uri")
        """
        try:
            api_method = "GET"
            api_header = {"Content-Type": "application/json"}
            if self.__nifi_token is not None:
                api_header["Authorization"] = self.__nifi_token
            obj_response = self.call_request(api_method, uri, api_header)
            response_content = obj_response.json()
            file_details = response_content["listingRequest"]["flowFileSummaries"]
            return file_details
        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while retrieving flow file details " \
                            f"from URI {uri}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False

    def start_then_stop_pg(self, pg_id: str, wait_time: int = 10) -> bool:
        """
        Starts and stops the NiFi process group.

        Args:
            pg_id (str): The NiFi process group ID.
            wait_time (int): Time to wait before stopping the NiFi process group.

        Returns:
            bool: True if successful; otherwise, False.

        Examples:
            >> result = ApacheUtils.Nifi().start_then_stop_pg("process_group_id", 10)
        """
        try:
            process_group_status = nipyapi.canvas. \
                get_process_group_status(pg_id=pg_id, detail="names")
            if process_group_status is not None:
                self.reporting.insert_step(
                    "Processor group found", "Processor group found", "Pass"
                )
                nipyapi.canvas.schedule_process_group(pg_id, scheduled=True)
                self.logger.info("Process group %s started.", pg_id)
                time.sleep(wait_time)
                nipyapi.canvas.schedule_process_group(pg_id, scheduled=False)
                self.logger.info("Process group %s stopped after %s seconds."
                                 , pg_id, wait_time)
                return True
            self.reporting.insert_step(
                "Processor group not found", "Processor group not found", "Fail"
            )
            self.logger.warning("Process group %s not found.", pg_id)
            return False

        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while starting and stopping process" \
                            f" group {pg_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False

    def get_access_config(self) -> bool:
        """
        Gets the access config of a NiFi instance.

        Returns:
            bool: Indicates if the function ran successfully.

        Examples:
            >> success = ApacheUtils.Nifi().get_access_config()
        """
        try:
            obj_access_configuration_entity = self.apis.get("access_api").get_login_config()
            if bool(obj_access_configuration_entity.config.to_dict()):
                self.logger.debug("Access configuration retrieved: %s",
                                  obj_access_configuration_entity.config.to_dict())
                self.reporting.insert_step(
                    "Successfully retrieved NiFi access config",
                    "Access configuration retrieved successfully",
                    "Pass",
                )
                return True
            self.reporting.insert_step(
                "Failed to retrieve NiFi access config",
                "Access configuration is empty or invalid",
                "Fail",
            )
            return False

        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while retrieving NiFi access config: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False

    def get_security_token(self, username: str, password: str, is_password_encrypted: False) -> bool:
        """
        Generates the authorized token used for login into NiFi.

        Args:
            is_password_encrypted: boolean value to check if password is encrypted
            username (str): Username.
            password (str): Password.

        Returns:
            bool: Indicates if the token was generated successfully.

        Examples:
            >> success = ApacheUtils.Nifi().get_security_token("username", "password")
        """
        try:
            bool_token = Security().nifi_get_token(username, password,is_password_encrypted)
            if bool_token[0]:
                self.__nifi_token = bool_token[1]
                self.logger.info("Successfully generated NiFi security token.")
                return True
            self.logger.warning("Failed to generate NiFi security token: Invalid credentials.")
            return False
        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while generating NiFi security token: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False

    def get_process_group_id(self, pstr_process_group_name,
                             parent_pg_id="root") -> tuple[bool, Any]:
        """
        Retrieves the process group ID.

        Args:
            pstr_process_group_name (str): Process group name.
            parent_pg_id (str): Parent Process Group ID.

        Returns:
            bool: Indicates whether the operation was successful.

        Examples:
            >> success = ApacheUtils.Nifi().get_process_group_id("process_group_name")
        """
        component_id = None
        try:
            process_group_list = nipyapi.canvas.list_all_process_groups(pg_id=parent_pg_id)
            for process_group in process_group_list:
                if process_group.to_dict()["component"]["name"] == pstr_process_group_name:
                    component_id = process_group.to_dict()["component"]["id"]
                    break
            if component_id is not None:
                self.reporting.insert_step(
                    f"Successfully retrieved process group ID for: {pstr_process_group_name}",
                    "Successfully retrieved process group ID",
                    "Pass",
                )
                return True, component_id

            self.reporting.insert_step(
                f"Failed to retrieve process group ID for: {pstr_process_group_name}",
                "Process group not found",
                "Fail",
            )
            return False, component_id
        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while retrieving process group ID: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False, component_id

    def get_processor_id(self, processor_name: str, parent_pg_id: str = "root") -> bool:
        """
        Retrieves the processor ID.

        Args:
            processor_name (str): Processor name.
            parent_pg_id (str): Parent Process Group ID.

        Returns:
            bool: Indicates if the processor ID was retrieved successfully.

        Examples:
            >> success = ApacheUtils.Nifi().get_processor_id("processor_name")
        """
        component_id = None
        try:
            processor_list = nipyapi.canvas.list_all_processors(pg_id=parent_pg_id)
            for processor in processor_list:
                if processor.to_dict()["component"]["name"] == processor_name:
                    component_id = processor.to_dict()["component"]["id"]
                    break
            if component_id is not None:
                self.reporting.insert_step(
                    f"Successfully retrieved processor ID for: {processor_name}",
                    "Successfully retrieved processor ID",
                    "Pass",
                )
                return True
            self.reporting.insert_step(
                f"Failed to retrieve processor ID for: {processor_name}",
                "Processor not found",
                "Fail",
            )
            return False
        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while retrieving processor ID: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False

    def __get_processor(self, processor_id: str) -> tuple[bool, Any]:
        """
        Retrieves the processor object.

        Args:
            processor_id (str): Processor ID.

        Returns:
            bool: Indicates if the processor was retrieved successfully.

        Examples:
            >> success = ApacheUtils.Nifi().__get_processor("processor_id")
        """
        processor = None
        try:
            processor = nipyapi.canvas.get_processor(processor_id, identifier_type="id")
            if processor is not None:
                self.reporting.insert_step(
                    f"Successfully retrieved processor details: {processor_id}",
                    "Successfully retrieved processor details",
                    "Pass",
                )
                return True, processor
            self.reporting.insert_step(
                f"Failed to retrieve processor details: {processor_id}",
                "Unable to get processor details",
                "Fail",
            )
            return False, processor

        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while retrieving processor" \
                            f" ID {processor_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False, processor

    def get_component_connections(self, processor_id: str,
                                  return_list: bool = False) -> tuple[bool, dict]:
        """
        Retrieves the connections of a component/processor.

        Args:
            processor_id (str): Processor ID.
            return_list (bool): Return type identifier.

        Returns:
            bool, dict: Tuple indicating 'execution_result' and connections
            dictionary object.

        Examples:
            >> success, connections = ApacheUtils.Nifi().
            get_component_connections("processor_id")
        """
        connections_dict = {"source": {}, "destination": {}}

        try:
            execution, processor = self.__get_processor(processor_id)

            if execution:
                connections = nipyapi.canvas.get_component_connections(processor)
                for connection in connections:
                    connection_status = connection.to_dict()["status"]
                    connection_name = connection_status["name"]
                    connection_id = connection_status["id"]

                    if connection_status["source_id"] == processor_id:
                        if return_list:
                            connections_dict["source"].setdefault(connection_name, []). \
                                append(connection_id)
                        else:
                            connections_dict["source"][connection_name] = connection_id

                    elif connection_status["destination_id"] == processor_id:
                        if return_list:
                            connections_dict["destination"]. \
                                setdefault(connection_name, []).append(connection_id)
                        else:
                            connections_dict["destination"][connection_name] = connection_id

                if connections:
                    self.reporting.insert_step(
                        f"Successfully retrieved component connections for: {processor_id}",
                        "Successfully retrieved component connections",
                        "Pass",
                    )
                    return True, connections_dict

                self.reporting.insert_step(
                    f"Unable to get component connections for: {processor_id}",
                    "No connections found",
                    "Fail",
                )
                return False, connections_dict

        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while retrieving component " \
                            f"connections for {processor_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False, connections_dict

    def list_queue_data(self, connection_id: str) -> list | None:
        """
        Lists the information of the queue in this connection.

        Args:
            connection_id (str): Connection ID.

        Returns:
            ListingRequestEntity: Lists the queue details.

        Examples:
            >> queue_data = ApacheUtils.Nifi().list_queue_data("connection_id")
        """
        try:
            listing_request = self.apis.get("flowfile_queues_api"). \
                create_flow_file_listing(connection_id)
            if listing_request is not None:
                self.reporting.insert_step(
                    "Successfully listed queue connection data",
                    "Successfully listed queue connection data",
                    "Pass",
                )
                return listing_request
            self.reporting.insert_step(
                "Failed to list queue connection data",
                "No data returned for the queue connection",
                "Fail",
            )
            return None

        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while listing queue data for connection " \
                            f"ID {connection_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return None

    def delete_queue_data(self, connection_id: str) -> bool:
        """
        Deletes the contents of the queue in the connection.

        Args:
            connection_id (str): Connection ID.

        Returns:
            bool: True if deletion was successful; otherwise, False.

        Examples:
            >> success = ApacheUtils.Nifi().delete_queue_data("connection_id")
        """
        try:
            drop_req_id = self.apis.get("flowfile_queues_api").create_drop_request(connection_id)

            if drop_req_id is not None:
                self.reporting.insert_step(
                    "Successfully deleted queue connection data",
                    "Successfully deleted queue connection data",
                    "Pass",
                )
                return True
            self.reporting.insert_step(
                "Failed to delete queue connection data",
                "Unable to delete queue connection data",
                "Fail",
            )
            return False

        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while deleting queue data for connection " \
                            f"ID {connection_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False

    def list_connections(self, pg_id: str = "root", key_path: str = None) -> list:
        """
        Lists the connections of the queue in the process group.

        Args:
            pg_id (str): Process Group ID.
            key_path (str): Path of the field to be retrieved.

        Returns:
            list: Connections list or specified key path values.

        Examples:
            >> connections = ApacheUtils.Nifi().list_connections("process_group_id")
        """
        try:
            connections_list = []
            connection_list = nipyapi.canvas.list_all_connections(pg_id=pg_id)
            for conn in connection_list:
                if key_path:
                    field_values = self.get_key_path_value(
                        json=conn.to_dict(), keyPath=key_path, keyPathType="absolute"
                    )
                    connections_list.append(field_values)
                else:
                    connections_list.append(conn)

            return connections_list

        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while listing connections for " \
                            f"process group ID {pg_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return []

    def get_process_groups(self, pg_id: str = "root", key_path: str = None) -> list:
        """
        Retrieves details of process groups under the mentioned process group recursively.

        Args:
            pg_id (str): Process Group ID.
            key_path (str): Path of the field to be retrieved.

        Returns:
            list: Process groups list or specified key path values.

        Examples:
            >> process_groups = ApacheUtils.Nifi().
            get_process_groups("process_group_id")
        """
        try:
            pgs_list = []
            pg_list = nipyapi.canvas.list_all_process_groups(pg_id=pg_id)
            for pg in pg_list:
                if key_path:
                    field_values = self.get_key_path_value(
                        json=pg.to_dict(), keyPath=key_path, keyPathType="absolute"
                    )
                    pgs_list.append(field_values)
                else:
                    pgs_list.append(pg)
            return pgs_list

        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while retrieving process groups for " \
                            f"ID {pg_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return []

    def get_processors(self, pg_id: str = "root", key_path: str = None) -> list:
        """
        Retrieves details of processors under the mentioned process group recursively.

        Args:
            pg_id (str): Process Group ID.
            key_path (str): Path of the field to be retrieved.

        Returns:
            list: Processors list or specified key path values.

        Examples:
            >> processors = ApacheUtils.Nifi().get_processors("process_group_id")
        """
        try:
            processors_list = []
            processor_list = nipyapi.canvas.list_all_processors(pg_id=pg_id)
            for processor in processor_list:
                if key_path:
                    field_values = self.get_key_path_value(
                        json=processor.to_dict(), keyPath=key_path,
                        keyPathType="absolute"
                    )
                    processors_list.append(field_values)
                else:
                    processors_list.append(processor)

            return processors_list

        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while retrieving processors for " \
                            f"process group ID {pg_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return []

    def get_remote_process_groups(self, pg_id: str = "root", key_path: str = None) -> list:
        """
        Retrieves all remote processor groups under the mentioned process group recursively.

        Args:
            pg_id (str): Process Group ID.
            key_path (str): Path of the field to be retrieved.

        Returns:
            list: Remote processor groups list or specified key path values.

        Examples:
            >> remote_groups = ApacheUtils.Nifi().get_remote_process_groups("process_group_id")
        """
        try:
            rpgs_list = []
            rpg_list = nipyapi.canvas.list_all_remote_process_groups(pg_id=pg_id)

            for pg in rpg_list:
                if key_path:
                    field_values = self.get_key_path_value(
                        json=pg.to_dict(), keyPath=key_path, keyPathType="absolute"
                    )
                    rpgs_list.append(field_values)
                else:
                    rpgs_list.append(pg)

            return rpgs_list

        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while retrieving remote process groups for " \
                            f"process group ID {pg_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return []

    def change_remote_process_group_state(self, rpg_id: str, enable: bool) -> bool:
        """
        Changes the state of the remote process group.

        Args:
            rpg_id (str): Remote Process Group ID.
            enable (bool): True to enable; False to disable.

        Returns:
            bool: Status of completion.

        Examples:
            >> success = ApacheUtils.Nifi().
            change_remote_process_group_state("remote_group_id", True)
        """
        try:
            status = nipyapi.canvas.set_remote_process_group_transmission(
                rpg_id, enable=enable, refresh=True
            )

            if status is not None:
                self.reporting.insert_step(
                    "Successfully changed the state of the remote process group.",
                    "State change completed successfully.",
                    "Pass",
                )
                return True
            self.reporting.insert_step(
                "Failed to change the state of the remote process group.",
                "No status returned from the operation.",
                "Fail",
            )
            return False

        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while changing the state of remote " \
                            f"process group {rpg_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False

    def get_process_group_q_count(self, process_group_id: str) -> int:
        """
        Gets the queue count of documents in the NiFi Process group.

        Args:
            process_group_id (str): NiFi process group ID.

        Returns:
            int: Queue count of the process group.

        Examples:
            >> count = ApacheUtils.Nifi().
            get_process_group_q_count("process_group_id")
        """
        try:
            key_path = "status/aggregate_snapshot/queued_count"
            process_group = self.nifi_module.canvas.get_process_group(
                process_group_id, identifier_type="id"
            )
            group_q_count = self.get_key_path_value(
                json=process_group.to_dict(), keyPath=key_path, keyPathType="absolute"
            )

            return group_q_count

        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while retrieving queue count for process " \
                            f"group ID " \
                            f"{process_group_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return 0

    def get_processor_q_count(self, processor_id: str) -> int:
        """
        Gets the queue count of documents in the NiFi Processor.

        Args:
            processor_id (str): NiFi processor ID.

        Returns:
            int: Queue count of the processor.

        Examples:
            >> count = ApacheUtils.Nifi().get_processor_q_count("processor_id")
        """
        try:
            key_path = "status/aggregate_snapshot/queued_count"
            processor = self.nifi_module.canvas.get_processor(
                processor_id, identifier_type="id"
            )
            processor_q_count = self.get_key_path_value(
                json=processor.to_dict(), keyPath=key_path, keyPathType="absolute"
            )

            return processor_q_count

        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while retrieving queue count for processor ID " \
                            f"{processor_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return 0

    def enable_processor(
            self,
            server_name: str,
            processor_id: str,
            max_wait_time: int = 60,
            wait_interval: int = 5,
            end_point: str = "/nifi-api/processors/{processor_id}/run-status",
    ):
        """
        Enables the processor and keeps it in a stopped state.

        Args:
            server_name (str): NiFi server URL.
            processor_id (str): NiFi processor ID.
            max_wait_time (int): Max wait time to wait for processor to enable.
            wait_interval (int): Interval time to check the status.
            end_point (str): Service endpoint to invoke API call.

        Returns:
            bool: True if successful; otherwise, False.

        Examples:
            >> result = ApacheUtils.Nifi().
            enable_processor("http://localhost:8080", "processor_id")
        """
        try:
            _, dict_processor_data = self.__get_processor(processor_id)
            dict_payload = {
                "revision": {
                    "clientId": dict_processor_data.revision.client_id,
                    "version": dict_processor_data.revision.version,
                },
                "state": "STOPPED",
            }
            str_api_method = "PUT"
            dict_api_header = {"Content-Type": "application/json"}
            if self.__nifi_token is not None:
                dict_api_header["Authorization"] = self.__nifi_token

            str_request_url = f"{server_name}{end_point.format(processor_id=processor_id)}"
            self.call_request(
                str_api_method,
                str_request_url,
                dict_api_header,
                pstr_payload=json.dumps(dict_payload),
            )
            count = 0
            max_count = max_wait_time // wait_interval

            while count < max_count:
                time.sleep(wait_interval)
                str_path = "status/aggregate_snapshot/run_status"
                _, processor_data = self.__get_processor(processor_id)
                value = self.get_key_path_value(
                    json=processor_data.to_dict(), keyPath=str_path, keyPathType="absolute"
                )

                count += 1
                if value.strip().lower() != "validating":
                    break
            else:
                self.reporting.insert_step(
                    f"Processor ID {processor_id} should get enabled.",
                    f"Processor is not getting enabled after: {max_wait_time} seconds.",
                    "Fail",
                )
                return False

            self.reporting.insert_step(
                f"Successfully enabled processor: {processor_id}",
                "Processor has been successfully enabled.",
                "Pass",
            )
            return True

        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while enabling processor ID " \
                            f"{processor_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False

    def disable_processor(
            self,
            server_name: str,
            processor_id: str,
            max_wait_time: int = 60,
            wait_interval: int = 5,
            end_point: str = "/nifi-api/processors/{processor_id}/run-status",
    ) -> bool:
        """
        Disables the processor.

        Args:
            server_name (str): NiFi server URL.
            processor_id (str): NiFi processor ID.
            max_wait_time (int): Max wait time to wait for processor to disable.
            wait_interval (int): Interval time to check the status.
            end_point (str): Service endpoint to invoke API call.

        Returns:
            bool: True if successful; otherwise, False.

        Examples:
            >> result = ApacheUtils.Nifi().
            disable_processor("http://localhost:8080", "processor_id")
        """
        try:
            _, dict_processor_data = self.__get_processor(processor_id)
            dict_payload = {
                "revision": {
                    "clientId": dict_processor_data.revision.client_id,
                    "version": dict_processor_data.revision.version,
                },
                "state": "DISABLED",
            }
            str_api_method = "PUT"
            dict_api_header = {"Content-Type": "application/json"}
            if self.__nifi_token is not None:
                dict_api_header["Authorization"] = self.__nifi_token

            str_request_url = f"{server_name}{end_point.format(processor_id=processor_id)}"
            self.call_request(
                str_api_method,
                str_request_url,
                dict_api_header,
                pstr_payload=json.dumps(dict_payload),
            )
            count = 0
            max_count = max_wait_time // wait_interval

            while count < max_count:
                time.sleep(wait_interval)
                str_path = "status/aggregate_snapshot/active_thread_count"
                _, str_processor_data = self.__get_processor(processor_id)
                value = self.get_key_path_value(
                    json=str_processor_data.to_dict(), keyPath=str_path, keyPathType="absolute"
                )

                if int(value) == 0:
                    break

                count += 1
            else:
                self.reporting.insert_step(
                    f"Processor {processor_id} should be disabled.",
                    f"Processor is not getting disabled after {max_wait_time} seconds.",
                    "Fail",
                )
                return False
            self.reporting.insert_step(
                f"Processor {processor_id} has been successfully disabled.",
                "Processor has been disabled.",
                "Pass",
            )
            return True

        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while disabling processor ID " \
                            f"{processor_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False

    def clear_queues(
            self, processor_id: str, inbound_queue: bool = True, outbound_queue: bool = True
    ) -> bool:
        """
        Clears the in/out queues for the given processor based on input parameters.

        Args:
            processor_id (str): NiFi processor ID.
            inbound_queue (bool): If True, clears the input queue for the processor.
            outbound_queue (bool): If True, clears the output queue for the processor.

        Returns:
            bool: True if successful; otherwise, False.

        Examples:
            >> result = ApacheUtils.Nifi().clear_queues("processor_id")
        """
        try:
            _, dict_connections = self.get_component_connections(processor_id, True)
            if inbound_queue:
                for key, val in dict_connections["source"].items():
                    for connection_id in val:
                        if not self.delete_queue_data(connection_id):
                            self.reporting.insert_step(
                                "Failed to clear input queue",
                                f"Error occurred while deleting input "
                                f"connection: {connection_id}",
                                "Fail",
                            )
                            return False

                self.reporting.insert_step(
                    f"Successfully cleared all input queues for processor ID: {processor_id}",
                    "All input queues cleared.",
                    "Pass",
                )
            if outbound_queue:
                for key, val in dict_connections["destination"].items():
                    for connection_id in val:
                        if not self.delete_queue_data(connection_id):
                            self.reporting.insert_step(
                                "Failed to clear output queue",
                                f"Error occurred while deleting output "
                                f"connection: {connection_id}",
                                "Fail",
                            )
                            return False

                self.reporting.insert_step(
                    f"Successfully cleared all output queues for processor ID: {processor_id}",
                    "All output queues cleared.",
                    "Pass",
                )

            return True

        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while clearing queues for processor " \
                            f"ID {processor_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False

    def start_then_stop_processor(
            self,
            server_name: str,
            processor_id: str,
            min_wait_time: int = 0,
            max_wait_time: int = 50,
            wait_interval: int = 5,
    ) -> bool:
        """
        Starts and stops the given processor.

        Args:
            server_name (str): NiFi server URL.
            processor_id (str): NiFi processor ID.
            min_wait_time (int): Minimum wait time in seconds.
            max_wait_time (int): Maximum wait time in seconds.
            wait_interval (int): Polling time to check each time in seconds.

        Returns:
            bool: True if successful; otherwise, False.

        Examples:
            >> result = ApacheUtils.Nifi().
            start_then_stop_processor("http://localhost:8080", "processor_id")
        """
        try:
            self.change_nifi_processor_state(server_name, processor_id, "RUNNING")
            time.sleep(min_wait_time)
            if wait_interval <= 0:
                self.reporting.insert_step(
                    "Invalid wait interval",
                    "Wait interval must be greater than 0",
                    "Fail",
                )
                return False
            limit = max_wait_time // wait_interval
            count = 0
            while count < limit:
                time.sleep(wait_interval)
                path = "status/aggregate_snapshot/active_thread_count"
                _, processor_data = self.__get_processor(processor_id)
                json_counter = self.get_key_path_value(
                    json=processor_data.to_dict(), keyPath=path, keyPathType="absolute"
                )

                if int(json_counter) == 0:
                    break

                count += 1
            else:
                self.reporting.insert_step(
                    f"Processor {processor_id} should not have active threads.",
                    f"Processor is taking more than {max_wait_time} seconds to stop.",
                    "Fail",
                )
                return False
            self.change_nifi_processor_state(server_name, processor_id, "STOPPED")
            self.reporting.insert_step(
                f"Processor {processor_id} has been successfully started and stopped.",
                "Processor started and stopped successfully.",
                "Pass",
            )
            return True

        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while starting and stopping processor" \
                            f" ID {processor_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False

    def call_request(self, method: str, url: str, headers: dict, **kwargs):
        """
        Performs various HTTP requests (GET, POST, PUT, PATCH, DELETE).

        Args:
            method (str): The HTTP method (e.g., 'GET', 'POST').
            url (str): The request URL.
            headers (dict): Request headers.

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
            pdict_proxies (dict): Proxies for the request.

        Returns:
            requests.Response: The response object from the request.

        Examples:
            >> response = ApacheUtils.Nifi().
            call_request("GET", "https://www.samplesite.com/api",
            headers={"Accept": "application/json"})
        """
        if not url:
            raise ValueError("URL cannot be null")
        json_data = kwargs.get("json_data")
        payload = kwargs.get("payload")
        cookies = kwargs.get("cookies", {})
        allow_redirects = kwargs.get("allow_redirects", False)
        files = kwargs.get("files")
        verify = kwargs.get("verify", False)
        auth_type = kwargs.get("auth_type")
        auth_username = kwargs.get("auth_username")
        auth_password = kwargs.get("auth_password")
        timeout = kwargs.get("timeout")
        proxies = kwargs.get("proxies")
        auth_string = ""
        if auth_type:
            auth_string = self.security.get_auth_string(
                auth_type, auth_username, auth_password
            )
        method = method.upper()
        try:
            if method == "GET":
                response = requests.get(
                    url,
                    headers=headers,
                    verify=verify,
                    allow_redirects=allow_redirects,
                    cookies=cookies,
                    auth=auth_string,
                    timeout=timeout,
                    proxies=proxies,
                )
            elif method in ["POST", "PUT", "PATCH"]:
                if payload is None:
                    raise ValueError("Payload is required for POST, PUT, and PATCH requests.")
                response = requests.request(
                    method,
                    url,
                    headers=headers,
                    data=payload,
                    json=json_data,
                    verify=verify,
                    allow_redirects=allow_redirects,
                    cookies=cookies,
                    files=files,
                    auth=auth_string,
                    timeout=timeout,
                    proxies=proxies,
                )
            elif method == "DELETE":
                response = requests.delete(
                    url,
                    headers=headers,
                    verify=verify,
                    allow_redirects=allow_redirects,
                    cookies=cookies,
                    auth=auth_string,
                    data=payload,
                    json=json_data,
                    timeout=timeout,
                    proxies=proxies,
                )
            else:
                raise ValueError(f"Invalid HTTP method: {method}. Valid "
                                 f"options are: GET, POST, PUT, PATCH, DELETE")
            return response
        except Exception as e:
            self.logger.exception("Error in Apache call request method: %s", str(e))
            raise e

    def get_key_path_value(self, **kwargs: Any) -> Any:
        """
        Extracts the value at the specified key path from the JSON data.

        Kwargs:
            json: The JSON data (string or dictionary).
            keyPath: The path to the key, using the specified delimiter.
            keyPathType: Either "absolute" or "relative" (default: "absolute").
            delimiter: The delimiter used in the key path (default: "/").
            key: The key to retrieve the value for when using relative key paths.

        Returns:
            The value associated with the key path.

        Raises:
            ValueError: If required arguments are missing, invalid, or the key path
            is not found.
            json.JSONDecodeError: If the JSON data is invalid.

        Examples:
            >> value = ApacheUtils.Nifi().
            get_key_path_value(json='{"key": "value"}', keyPath='key')
        """
        try:
            if "json" not in kwargs:
                self.logger.info("No json argument provided")
                raise ValueError("json argument is required.")
            if "keyPath" not in kwargs:
                self.logger.info("No keyPath argument provided")
                raise ValueError("keyPath argument is required.")
            if "keyPathType" not in kwargs:
                self.logger.info("No keyPathType argument provided")
                raise ValueError("keyPathType argument is required.")
            obj_parse_data = ParseJsonData()
            return obj_parse_data.get_value_from_key_path(**kwargs)
        except Exception as e:
            self.logger.exception("Error in extracting the value at the specified "
                                  "key path: %s", e)
            raise e

    def get_processor_properties(self, processor_id: str) -> dict | bool:
        """
        Retrieves the configuration properties of a specified NiFi processor.

        Args:
            processor_id (str): NiFi processor ID.

        Returns:
            dict: A dictionary of properties if successful; otherwise, False.

        Examples:
            >> properties = ApacheUtils.Nifi().get_processor_properties("processor_id")
        """

        try:
            processor = nipyapi.canvas.get_processor(processor_id)
            if processor is not None:
                properties = processor.to_dict()["component"]["config"]
                self.reporting.insert_step(
                    f"Successfully retrieved properties for processor ID: {processor_id}",
                    "Properties retrieved successfully",
                    "Pass",
                )
                return properties
            self.reporting.insert_step(
                f"Failed to retrieve properties for processor ID: {processor_id}",
                "Processor not found",
                "Fail",
            )
            return False
        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while retrieving properties for processor " \
                            f"ID {processor_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False

    def update_processor_properties(self, processor_id: str, properties: dict) -> bool:
        """
        Updates the properties of a specified NiFi processor with the provided properties.

        Args:
            processor_id (str): NiFi processor ID.
            properties (dict): A dictionary containing the properties to update.

        Returns:
            bool: True if the update was successful; otherwise, False.

        Examples:
            >> success = ApacheUtils.Nifi().
            update_processor_properties("processor_id", {"property_name": "value"})

        """
        try:
            processor = nipyapi.canvas.get_processor(processor_id)
            if processor is not None:
                # Prepare the payload for updating properties
                payload = {
                    "revision": {
                        "clientId": processor.revision.client_id,
                        "version": processor.revision.version,
                    },
                    "component": {
                        "config": properties
                    }
                }
                response = self.call_request(
                    "PUT",
                    f"/nifi-api/processors/{processor_id}",
                    {"Content-Type": "application/json"},
                    pstr_payload=json.dumps(payload)
                )
                if response.status_code == 200:
                    self.reporting.insert_step(
                        f"Successfully updated properties for processor ID: {processor_id}",
                        "Properties updated successfully",
                        "Pass",
                    )
                    return True
                self.reporting.insert_step(
                    f"Failed to update properties for processor ID: {processor_id}",
                    "Update failed",
                    "Fail",
                )
                return False
        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while updating properties for processor ID " \
                            f"{processor_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False

    def get_flow_file_count(self, connection_id: str) -> int:
        """
        Retrieves the count of flow files in a specified NiFi connection.

        Args:
            connection_id (str): The ID of the connection.

        Returns:
            int: The count of flow files.

        Examples:
            >> count = ApacheUtils.Nifi().get_flow_file_count("connection_id")

        """
        try:
            flow_file_listing = self.apis.get("flowfile_queues_api"). \
                create_flow_file_listing(connection_id)
            str_uri = flow_file_listing.listing_request.uri
            flow_file_details = self.__get_flow_file_details(str_uri)
            return len(flow_file_details)  # Count of flow files
        except (nipyapi.nifi.rest.ApiException, ValueError) as e:
            error_message = f"Error occurred while retrieving flow file count for connection " \
                            f"ID {connection_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return 0
