"""
This module provides automation support for Apache NiFi processors.
"""
import json
import time
from typing import Any
import nipyapi

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.reporting_.reporting import Reporting
from cafex_core.utils.apache_utils.nifi_process_group_utils import NifiProcessGroupUtils
from cafex_core.utils.core_security import Security
from cafex_core.utils.exceptions import CoreExceptions


class NifiProcessorUtils:
    """
    This Class provides automation support for Apache NiFi processors.
    """

    def __init__(self, pstr_nifi_url, pstr_nifi_registry_url=None):
        self.reporting = Reporting()
        self.__obj_exception = CoreExceptions()
        self.__nifi_token = None
        self.nifi_module = nipyapi
        self.logger = CoreLogger(name=__name__).get_logger()
        self.security = Security()

        nipyapi.config.nifi_config.verify_ssl = False
        nipyapi.config.nifi_config.host = pstr_nifi_url

        self.apis = {
            "flow_api": self.nifi_module.nifi.apis.flow_api.FlowApi(),
            "flowfile_queues_api": self.nifi_module.nifi.apis.flowfile_queues_api.FlowfileQueuesApi(),
            "access_api": nipyapi.nifi.apis.access_api.AccessApi()
        }

        if pstr_nifi_registry_url is not None:
            nipyapi.config.registry_config.host = pstr_nifi_registry_url + "/nifi-registry-api"
        self.nifi_process_group_utils = NifiProcessGroupUtils(pstr_nifi_url, pstr_nifi_registry_url)

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
            response = self.nifi_process_group_utils.call_request(
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
                response = self.nifi_process_group_utils.call_request(
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
                    field_values = self.nifi_process_group_utils.get_key_path_value(
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
            processor_q_count = self.nifi_process_group_utils.get_key_path_value(
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
            self.nifi_process_group_utils.call_request(
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
                value = self.nifi_process_group_utils.get_key_path_value(
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
            self.nifi_process_group_utils.call_request(
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
                value = self.nifi_process_group_utils.get_key_path_value(
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
                json_counter = self.nifi_process_group_utils.get_key_path_value(
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
