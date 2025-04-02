"""
Description: This module provides automation support for Apache AirFlow. User can interact
with AirFlow DAGs, by triggering the DAG and track the progress by getting state of DAG
"""
from paramiko.ssh_exception import SSHException

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.utils.exceptions import CoreExceptions
from cafex_core.utils.ssh_handler import SshHandler


class ApacheAirFlow:
    """
    Description:
        |  This Class provides automation support for Apache AirFlow. User can interact
        with AirFlow DAGs, by triggering the DAG and track the progress by getting state
        of DAG
        |   Apache Airflow is a workflow automation and scheduling system that can be used to
         author and manage data pipelines.
        |   Airflow uses workflows made of directed acyclic graphs (DAGs) of tasks.

    """

    def __init__(self):
        self.__ssh_handler = SshHandler()
        self.__obj_exception = CoreExceptions()
        self.logger = CoreLogger(name=__name__).get_logger()

    def trigger_dag(
            self, ssh_client, dag_id, in_buffer=2048, out_buffer=2048
    ) -> list:
        """
        Triggers the AirFlow DAG and returns a list of results from AirFlow.

        Args:
            ssh_client: SSH client object used for connection.
            dag_id (str): AirFlow DAG ID (case sensitive).
            in_buffer (int): Input buffer size.
            out_buffer (int): Output buffer size.

        Returns:
            list: Contains results from execution of AirFlow DAG.

        Examples:
            >> results = ApacheUtils.AirFlow().trigger_dag(ssh_client, 'TestDagId')
        """
        try:
            commands = [f"airflow trigger_dag {dag_id}"]
            dag_results = self.__ssh_handler.execute(
                ssh_client,
                commands,
                in_buffer=in_buffer,
                out_buffer=out_buffer,
            )

            return dag_results
        except (SSHException, ValueError) as e:
            error_message = f"Error occurred while triggering DAG '{dag_id}': {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return []

    def check_dag_state(
            self,
            ssh_client,
            dag_id: str,
            dag_result: list,
            in_buffer: int = 2048,
            out_buffer: int = 2048,
    ) -> list:
        """
        Returns the current status of the DAG based on the list provided, which is returned
        by the trigger AirFlow DAG method.

        Args:
            ssh_client: SSH client object used for connection.
            dag_id (str): AirFlow DAG ID (case sensitive).
            dag_result (list): List of results from AirFlow DAG trigger.
            in_buffer (int): Input buffer size.
            out_buffer (int): Output buffer size.

        Returns:
            list: Contains results from execution of AirFlow DAG.

        Examples:
            >> state = ApacheUtils.AirFlow().
            check_dag_state(ssh_client, 'TestDagId', lst_trigger_dag_results)
        """
        try:
            execution_date = dag_result[-1].split("__")[1].split(",")[0]
            commands = [f"airflow dag_state {dag_id} {execution_date}"]
            dag_results = self.__ssh_handler.execute(
                ssh_client,
                commands,
                in_buffer=in_buffer,
                out_buffer=out_buffer,
            )
            return dag_results
        except (SSHException, ValueError) as e:
            error_message = f"Error occurred while checking DAG state for ID {dag_id}: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return []

    def unpause_dag(self, ssh_client, dag_id: str) -> bool:
        """
        Unpauses a specified DAG in Airflow.

        Args:
            ssh_client: SSH client object used for connection.
            dag_id (str): The ID of the DAG to unpause.

        Returns:
            bool: True if the operation was successful; otherwise, False.

        Examples:
            >> success = ApacheUtils.AirFlow().unpause_dag(ssh_client, "TestDagId")

        """
        try:
            commands = [f"airflow dags unpause {dag_id}"]
            self.__ssh_handler.execute(
                ssh_client,
                commands,
                in_buffer=2048,
                out_buffer=2048,
            )
            self.logger.info("DAG %s unpaused successfully.", dag_id)
            return True
        except (SSHException, ValueError) as e:
            error_message = f"Error occurred while unpausing DAG '{dag_id}': {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False

    def pause_dag(self, ssh_client, dag_id: str) -> bool:
        """
        Pauses a specified DAG in Airflow.

        Args:
            ssh_client: SSH client object used for connection.
            dag_id (str): The ID of the DAG to pause.

        Returns:
            bool: True if the operation was successful; otherwise, False.

        Examples:
            >> success = ApacheUtils.AirFlow().pause_dag(ssh_client, "TestDagId")

        """
        try:
            commands = [f"airflow dags pause {dag_id}"]
            self.__ssh_handler.execute(
                ssh_client,
                commands,
                in_buffer=2048,
                out_buffer=2048,
            )
            self.logger.info("DAG %s paused successfully.", dag_id)
            return True
        except (SSHException, ValueError) as e:
            error_message = f"Error occurred while pausing DAG '{dag_id}': {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return False

    def get_dag_details(self, ssh_client, dag_id: str) -> list:
        """
        Retrieves detailed information about a specific DAG.

        Args:
            ssh_client: SSH client object used for connection.
            dag_id (str): The ID of the DAG to retrieve details for.

        Returns:
            dict: A dictionary containing details about the specified DAG.

        Examples:
            >> details = ApacheUtils.AirFlow().get_dag_details(ssh_client, "TestDagId")

        """

        try:
            commands = [f"airflow dags show {dag_id}"]
            dag_results = self.__ssh_handler.execute(
                ssh_client,
                commands,
                in_buffer=2048,
                out_buffer=2048,
            )
            return dag_results
        except (SSHException, ValueError) as e:
            error_message = f"Error occurred while retrieving details for " \
                            f"DAG '{dag_id}': {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return []

    def list_dags(self, ssh_client) -> list:
        """
        Lists all available DAGs in the Airflow environment.

        Args:
            ssh_client: SSH client object used for connection.

        Returns:
            list: A list of DAG IDs.

        Examples:
            >> dags = ApacheUtils.AirFlow().list_dags(ssh_client)

        """
        try:
            commands = ["airflow dags list"]
            dag_results = self.__ssh_handler.execute(
                ssh_client,
                commands,
                in_buffer=2048,
                out_buffer=2048,
            )
            return dag_results
        except (SSHException, ValueError) as e:
            error_message = f"Error occurred while listing DAGs: {str(e)}"
            self.__obj_exception.raise_generic_exception(
                message=error_message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            return []
