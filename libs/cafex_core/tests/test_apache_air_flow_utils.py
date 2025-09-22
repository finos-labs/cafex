import unittest
from unittest.mock import MagicMock, patch
from paramiko.ssh_exception import SSHException
from cafex_core.utils.apache_utils.apache_air_flow_utils import ApacheAirFlow


class TestApacheAirFlow(unittest.TestCase):
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.SshHandler')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreExceptions')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreLogger')
    def test_trigger_dag_success(self, MockLogger, MockCoreExceptions, MockSshHandler):
        # Setup Mocks
        mock_ssh_client = MagicMock()
        mock_logger = MockLogger.return_value.get_logger.return_value
        mock_ssh_handler = MockSshHandler.return_value
        mock_ssh_handler.execute.return_value = ["Triggering DAG Success"]

        # Test
        airflow = ApacheAirFlow()
        result = airflow.trigger_dag(mock_ssh_client, 'TestDagId')

        # Assertions
        mock_ssh_handler.execute.assert_called_once_with(mock_ssh_client, ['airflow trigger_dag TestDagId'],
                                                         in_buffer=2048, out_buffer=2048)
        self.assertEqual(result, ["Triggering DAG Success"])

    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.SshHandler')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreExceptions')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreLogger')
    def test_trigger_dag_ssh_exception(self, MockLogger, MockCoreExceptions, MockSshHandler):
        # Setup Mocks
        mock_ssh_client = MagicMock()
        mock_logger = MockLogger.return_value.get_logger.return_value
        mock_ssh_handler = MockSshHandler.return_value
        mock_ssh_handler.execute.side_effect = SSHException("SSH error")

        # Test
        airflow = ApacheAirFlow()
        result = airflow.trigger_dag(mock_ssh_client, 'TestDagId')

        # Assertions
        mock_ssh_handler.execute.assert_called_once_with(mock_ssh_client, ['airflow trigger_dag TestDagId'],
                                                         in_buffer=2048, out_buffer=2048)
        self.assertEqual(result, [])

    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.SshHandler')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreExceptions')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreLogger')
    def test_trigger_dag_value_error(self, MockLogger, MockCoreExceptions, MockSshHandler):
        # Setup Mocks
        mock_ssh_client = MagicMock()
        mock_logger = MockLogger.return_value.get_logger.return_value
        mock_ssh_handler = MockSshHandler.return_value
        mock_ssh_handler.execute.side_effect = ValueError("Invalid command")

        # Test
        airflow = ApacheAirFlow()
        result = airflow.trigger_dag(mock_ssh_client, 'TestDagId')

        # Assertions
        mock_ssh_handler.execute.assert_called_once_with(mock_ssh_client, ['airflow trigger_dag TestDagId'],
                                                         in_buffer=2048, out_buffer=2048)
        self.assertEqual(result, [])

    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.SshHandler')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreExceptions')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreLogger')
    def test_check_dag_state_success(self, MockLogger, MockCoreExceptions, MockSshHandler):
        # Setup Mocks
        mock_ssh_client = MagicMock()
        mock_logger = MockLogger.return_value.get_logger.return_value
        mock_ssh_handler = MockSshHandler.return_value
        mock_ssh_handler.execute.return_value = ["Dag State: Running"]

        # Test
        dag_result = ["dag_result_line_1", "dag_result_line_2__2023-01-01,00:00:00"]
        airflow = ApacheAirFlow()
        result = airflow.check_dag_state(mock_ssh_client, 'TestDagId', dag_result)

        # Assertions
        mock_ssh_handler.execute.assert_called_once_with(mock_ssh_client, ['airflow dag_state TestDagId 2023-01-01'],
                                                         in_buffer=2048, out_buffer=2048)
        self.assertEqual(result, ["Dag State: Running"])

    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.SshHandler')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreExceptions')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreLogger')
    def test_check_dag_state_ssh_exception(self, MockLogger, MockCoreExceptions, MockSshHandler):
        # Setup Mocks
        mock_ssh_client = MagicMock()
        mock_logger = MockLogger.return_value.get_logger.return_value
        mock_ssh_handler = MockSshHandler.return_value
        mock_ssh_handler.execute.side_effect = SSHException("SSH error")

        # Test
        dag_result = ["dag_result_line_1", "dag_result_line_2__2023-01-01,00:00:00"]
        airflow = ApacheAirFlow()
        result = airflow.check_dag_state(mock_ssh_client, 'TestDagId', dag_result)

        # Assertions
        mock_ssh_handler.execute.assert_called_once_with(mock_ssh_client, ['airflow dag_state TestDagId 2023-01-01'],
                                                         in_buffer=2048, out_buffer=2048)
        self.assertEqual(result, [])

    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.SshHandler')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreExceptions')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreLogger')
    def test_check_dag_state_value_error(self, MockLogger, MockCoreExceptions, MockSshHandler):
        # Setup Mocks
        mock_ssh_client = MagicMock()
        mock_logger = MockLogger.return_value.get_logger.return_value
        mock_ssh_handler = MockSshHandler.return_value
        mock_ssh_handler.execute.side_effect = ValueError("Invalid command")

        # Test
        dag_result = ["dag_result_line_1", "dag_result_line_2__2023-01-01,00:00:00"]
        airflow = ApacheAirFlow()
        result = airflow.check_dag_state(mock_ssh_client, 'TestDagId', dag_result)

        # Assertions
        mock_ssh_handler.execute.assert_called_once_with(mock_ssh_client, ['airflow dag_state TestDagId 2023-01-01'],
                                                         in_buffer=2048, out_buffer=2048)
        self.assertEqual(result, [])

    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.SshHandler')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreExceptions')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreLogger')
    def test_unpause_dag_success(self, MockLogger, MockCoreExceptions, MockSshHandler):
        # Setup Mocks
        mock_ssh_client = MagicMock()
        mock_logger = MockLogger.return_value.get_logger.return_value
        mock_ssh_handler = MockSshHandler.return_value
        mock_ssh_handler.execute.return_value = ["Unpaused DAG"]

        # Test
        airflow = ApacheAirFlow()
        result = airflow.unpause_dag(mock_ssh_client, 'TestDagId')

        # Assertions
        mock_ssh_handler.execute.assert_called_once_with(mock_ssh_client, ['airflow dags unpause TestDagId'],
                                                         in_buffer=2048, out_buffer=2048)
        self.assertTrue(result)

    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.SshHandler')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreExceptions')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreLogger')
    def test_unpause_dag_ssh_exception(self, MockLogger, MockCoreExceptions, MockSshHandler):
        # Setup Mocks
        mock_ssh_client = MagicMock()
        mock_logger = MockLogger.return_value.get_logger.return_value
        mock_ssh_handler = MockSshHandler.return_value
        mock_ssh_handler.execute.side_effect = SSHException("SSH error")

        # Test
        airflow = ApacheAirFlow()
        result = airflow.unpause_dag(mock_ssh_client, 'TestDagId')

        # Assertions
        mock_ssh_handler.execute.assert_called_once_with(mock_ssh_client, ['airflow dags unpause TestDagId'],
                                                         in_buffer=2048, out_buffer=2048)
        self.assertFalse(result)

    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.SshHandler')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreExceptions')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreLogger')
    def test_pause_dag_success(self, MockLogger, MockCoreExceptions, MockSshHandler):
        # Setup Mocks
        mock_ssh_client = MagicMock()
        mock_logger = MockLogger.return_value.get_logger.return_value
        mock_ssh_handler = MockSshHandler.return_value
        mock_ssh_handler.execute.return_value = ["Paused DAG"]

        # Test
        airflow = ApacheAirFlow()
        result = airflow.pause_dag(mock_ssh_client, 'TestDagId')

        # Assertions
        mock_ssh_handler.execute.assert_called_once_with(mock_ssh_client, ['airflow dags pause TestDagId'],
                                                         in_buffer=2048, out_buffer=2048)
        self.assertTrue(result)

    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.SshHandler')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreExceptions')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreLogger')
    def test_pause_dag_ssh_exception(self, MockLogger, MockCoreExceptions, MockSshHandler):
        # Setup Mocks
        mock_ssh_client = MagicMock()
        mock_logger = MockLogger.return_value.get_logger.return_value
        mock_ssh_handler = MockSshHandler.return_value
        mock_ssh_handler.execute.side_effect = SSHException("SSH error")

        # Test
        airflow = ApacheAirFlow()
        result = airflow.pause_dag(mock_ssh_client, 'TestDagId')

        # Assertions
        mock_ssh_handler.execute.assert_called_once_with(mock_ssh_client, ['airflow dags pause TestDagId'],
                                                         in_buffer=2048, out_buffer=2048)
        self.assertFalse(result)

    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.SshHandler')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreExceptions')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreLogger')
    def test_get_dag_details_success(self, MockLogger, MockCoreExceptions, MockSshHandler):
        # Setup Mocks
        mock_ssh_client = MagicMock()
        mock_logger = MockLogger.return_value.get_logger.return_value
        mock_ssh_handler = MockSshHandler.return_value
        mock_ssh_handler.execute.return_value = ["Dag Details: Success"]

        # Test
        airflow = ApacheAirFlow()
        result = airflow.get_dag_details(mock_ssh_client, 'TestDagId')

        # Assertions
        mock_ssh_handler.execute.assert_called_once_with(mock_ssh_client, ['airflow dags show TestDagId'],
                                                         in_buffer=2048, out_buffer=2048)
        self.assertEqual(result, ["Dag Details: Success"])

    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.SshHandler')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreExceptions')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreLogger')
    def test_get_dag_details_ssh_exception(self, MockLogger, MockCoreExceptions, MockSshHandler):
        # Setup Mocks
        mock_ssh_client = MagicMock()
        mock_logger = MockLogger.return_value.get_logger.return_value
        mock_ssh_handler = MockSshHandler.return_value
        mock_ssh_handler.execute.side_effect = SSHException("SSH error")

        # Test
        airflow = ApacheAirFlow()
        result = airflow.get_dag_details(mock_ssh_client, 'TestDagId')

        # Assertions
        mock_ssh_handler.execute.assert_called_once_with(mock_ssh_client, ['airflow dags show TestDagId'],
                                                         in_buffer=2048, out_buffer=2048)
        self.assertEqual(result, [])

    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.SshHandler')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreExceptions')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreLogger')
    def test_list_dags_success(self, MockLogger, MockCoreExceptions, MockSshHandler):
        # Setup Mocks
        mock_ssh_client = MagicMock()
        mock_logger = MockLogger.return_value.get_logger.return_value
        mock_ssh_handler = MockSshHandler.return_value
        mock_ssh_handler.execute.return_value = ["dag1", "dag2", "dag3"]

        # Test
        airflow = ApacheAirFlow()
        result = airflow.list_dags(mock_ssh_client)

        # Assertions
        mock_ssh_handler.execute.assert_called_once_with(mock_ssh_client, ['airflow dags list'], in_buffer=2048,
                                                         out_buffer=2048)
        self.assertEqual(result, ["dag1", "dag2", "dag3"])

    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.SshHandler')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreExceptions')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreLogger')
    def test_list_dags_ssh_exception(self, MockLogger, MockCoreExceptions, MockSshHandler):
        """
        Test the scenario where SSHException is raised during the execution of list_dags.
        """
        # Setup Mocks
        mock_ssh_client = MagicMock()
        mock_logger = MockLogger.return_value.get_logger.return_value
        mock_ssh_handler = MockSshHandler.return_value
        mock_ssh_handler.execute.side_effect = SSHException("SSH connection error")

        mock_exception_handler = MockCoreExceptions.return_value

        # Test the method
        airflow = ApacheAirFlow()
        result = airflow.list_dags(mock_ssh_client)

        # Assertions
        mock_ssh_handler.execute.assert_called_once_with(mock_ssh_client, ['airflow dags list'], in_buffer=2048,
                                                         out_buffer=2048)
        mock_exception_handler.raise_generic_exception.assert_called_once_with(
            message="Error occurred while listing DAGs: SSH connection error",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False
        )
        self.assertEqual(result, [])

    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.SshHandler')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreExceptions')
    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreLogger')
    def test_list_dags_value_error(self, MockLogger, MockCoreExceptions, MockSshHandler):
        """
        Test the scenario where ValueError is raised during the execution of list_dags.
        """
        # Setup Mocks
        mock_ssh_client = MagicMock()
        mock_logger = MockLogger.return_value.get_logger.return_value
        mock_ssh_handler = MockSshHandler.return_value
        mock_ssh_handler.execute.side_effect = ValueError("Invalid command error")

        mock_exception_handler = MockCoreExceptions.return_value

        # Test the method
        airflow = ApacheAirFlow()
        result = airflow.list_dags(mock_ssh_client)

        # Assertions
        mock_ssh_handler.execute.assert_called_once_with(mock_ssh_client, ['airflow dags list'], in_buffer=2048,
                                                         out_buffer=2048)
        mock_exception_handler.raise_generic_exception.assert_called_once_with(
            message="Error occurred while listing DAGs: Invalid command error",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False
        )
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()
