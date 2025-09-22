import unittest
from unittest.mock import patch, MagicMock
import nipyapi
import requests
from cafex_core.utils.apache_utils.nifi_process_group_utils import NifiProcessGroupUtils


class TestNifiProcessGroupUtils(unittest.TestCase):

    def test_check_process_group_status_success(self):
        # Arrange
        mock_flow_api = MagicMock()
        mock_process_group_status = MagicMock()
        mock_process_group_status.process_group_status.to_dict.return_value = {"status": "available"}
        mock_flow_api.get_process_group_status.return_value = mock_process_group_status

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.apis = {"flow_api": mock_flow_api}  # Dynamically set the 'apis' attribute
        nifi_utils.reporting = MagicMock()
        nifi_utils.logger = MagicMock()

        # Act
        result = nifi_utils.check_process_group_status("test_process_group_id")

        # Assert
        self.assertTrue(result)
        mock_flow_api.get_process_group_status.assert_called_with("test_process_group_id")
        nifi_utils.reporting.insert_step.assert_called_with(
            "Successfully returned process group status",
            "Successfully returned process group status",
            "Pass"
        )
        nifi_utils.logger.info.assert_called_with("Successfully returned process group status for ID: %s.",
                                                  "test_process_group_id")

    def test_check_process_group_status_failure(self):
        # Arrange
        mock_flow_api = MagicMock()
        mock_process_group_status = MagicMock()
        mock_process_group_status.process_group_status.to_dict.return_value = {}
        mock_flow_api.get_process_group_status.return_value = mock_process_group_status

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.apis = {"flow_api": mock_flow_api}  # Dynamically set the 'apis' attribute
        nifi_utils.reporting = MagicMock()  # Dynamically set the 'reporting' attribute
        nifi_utils.logger = MagicMock()  # Dynamically set the 'logger' attribute

        # Act
        result = nifi_utils.check_process_group_status("test_process_group_id")

        # Assert
        self.assertFalse(result)
        nifi_utils.reporting.insert_step.assert_called_with(
            "Process group status retrieval",
            "Unable to get process group status",
            "Fail"
        )
        nifi_utils.logger.warning.assert_called_with("Unable to get process group status for ID: %s",
                                                     "test_process_group_id")

    @patch('cafex_core.utils.apache_utils.apache_air_flow_utils.CoreExceptions')
    def test_check_process_group_status_exception(self, mock_obj_exception):
        try:
            # Arrange
            mock_flow_api = MagicMock()
            mock_flow_api.get_process_group_status.side_effect = ValueError("Test Exception")
            mock_obj_exception.raise_generic_exception = MagicMock()

            nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
            nifi_utils.apis = {"flow_api": mock_flow_api}  # Dynamically set the 'apis' attribute
            nifi_utils.logger = MagicMock()  # Dynamically set the 'logger' attribute

            # Act
            result = nifi_utils.check_process_group_status("test_process_group_id")

            # Assert
            self.assertFalse(result)
            mock_obj_exception.raise_generic_exception.assert_called_once_with(
                message="Error occurred while checking status for process group test_process_group_id: Test Exception",
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False
            )
        except Exception as e:
            print("An unexpected exception occurred")

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.schedule_process_group')
    def test_change_process_group_state_success(self, mock_schedule_process_group):
        # Arrange
        mock_schedule_process_group.return_value = True
        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()
        nifi_utils.logger = MagicMock()

        # Act
        result = nifi_utils.change_process_group_state("test_process_group_id", True)

        # Assert
        self.assertTrue(result)
        mock_schedule_process_group.assert_called_once_with("test_process_group_id", scheduled=True)
        nifi_utils.reporting.insert_step.assert_called_with(
            "Successfully changed process group state to True",
            "Successfully changed process group state",
            "Pass"
        )
        nifi_utils.logger.info.assert_called_with("Process group %s state changed to %s.",
                                                  "test_process_group_id", True)

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.schedule_process_group')
    def test_change_process_group_state_failure(self, mock_schedule_process_group):
        # Arrange
        mock_schedule_process_group.return_value = False
        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()
        nifi_utils.logger = MagicMock()

        # Act
        result = nifi_utils.change_process_group_state("test_process_group_id", False)

        # Assert
        self.assertFalse(result)
        mock_schedule_process_group.assert_called_once_with("test_process_group_id", scheduled=False)
        nifi_utils.reporting.insert_step.assert_called_with(
            "Failed to change process group state to False",
            "Failed to change process group state",
            "Fail"
        )
        nifi_utils.logger.warning.assert_called_with("Failed to change process group %s state to %s.",
                                                     "test_process_group_id", False)

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.schedule_process_group')
    def test_change_process_group_state_exception(self, mock_schedule_process_group):
        # Arrange
        mock_schedule_process_group.side_effect = ValueError("Test Exception")
        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()
        nifi_utils.logger = MagicMock()

        # Dynamically set the private attribute __obj_exception
        nifi_utils._NifiProcessGroupUtils__obj_exception = MagicMock()

        # Act
        result = nifi_utils.change_process_group_state("test_process_group_id", True)

        # Assert
        self.assertFalse(result)
        mock_schedule_process_group.assert_called_once_with("test_process_group_id", scheduled=True)
        nifi_utils._NifiProcessGroupUtils__obj_exception.raise_generic_exception.assert_called_once_with(
            message="Error occurred while changing state for process group test_process_group_id: Test Exception",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False
        )

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.NifiProcessGroupUtils.call_request')
    def test_about_nifi_success(self, mock_call_request):
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_call_request.return_value = mock_response

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()
        nifi_utils._NifiProcessGroupUtils__nifi_token = "Bearer test_token"

        # Act
        result = nifi_utils.about_nifi("http://localhost:8080")

        # Assert
        self.assertTrue(result)
        mock_call_request.assert_called_once_with(
            "GET",
            "http://localhost:8080/nifi-api/flow/about",
            {"Content-Type": "application/json", "Authorization": "Bearer test_token"}
        )
        nifi_utils.reporting.insert_step.assert_called_with(
            "Successfully retrieved info about NiFi",
            "Successfully retrieved info about NiFi",
            "Pass"
        )

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.NifiProcessGroupUtils.call_request')
    def test_about_nifi_failure(self, mock_call_request):
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_call_request.return_value = mock_response

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()

        # Act
        result = nifi_utils.about_nifi("http://localhost:8080")

        # Assert
        self.assertFalse(result)
        mock_call_request.assert_called_once_with(
            "GET",
            "http://localhost:8080/nifi-api/flow/about",
            {"Content-Type": "application/json"}
        )
        nifi_utils.reporting.insert_step.assert_called_with(
            "Unable to get info about NiFi",
            "Failed to retrieve info about NiFi",
            "Fail"
        )

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.NifiProcessGroupUtils.call_request')
    def test_about_nifi_exception(self, mock_call_request):
        # Arrange
        mock_call_request.side_effect = ValueError("Test Exception")
        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()
        nifi_utils._NifiProcessGroupUtils__obj_exception = MagicMock()

        # Act
        result = nifi_utils.about_nifi("http://localhost:8080")

        # Assert
        self.assertFalse(result)
        mock_call_request.assert_called_once_with(
            "GET",
            "http://localhost:8080/nifi-api/flow/about",
            {"Content-Type": "application/json"}
        )
        nifi_utils._NifiProcessGroupUtils__obj_exception.raise_generic_exception.assert_called_once_with(
            message="Error occurred while retrieving NiFi info: Test Exception",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False
        )

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.NifiProcessGroupUtils.'
           '_NifiProcessGroupUtils__get_flow_file_details')
    def test_get_flow_files_queue_details_success(self, mock_get_flow_file_details):
        # Arrange
        mock_flowfile_queues_api = MagicMock()
        mock_listing_request_entity = MagicMock()
        mock_listing_request_entity.listing_request.uri = "test_uri"
        mock_flowfile_queues_api.create_flow_file_listing.return_value = mock_listing_request_entity
        mock_get_flow_file_details.return_value = [{"file": "file1"}, {"file": "file2"}]

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.apis = {"flowfile_queues_api": mock_flowfile_queues_api}
        nifi_utils.reporting = MagicMock()

        # Act
        result = nifi_utils.get_flow_files_queue_details("test_connection_id")

        # Assert
        self.assertEqual(result, [{"file": "file1"}, {"file": "file2"}])
        mock_flowfile_queues_api.create_flow_file_listing.assert_called_once_with("test_connection_id")
        mock_get_flow_file_details.assert_called_once_with("test_uri")

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.NifiProcessGroupUtils.'
           '_NifiProcessGroupUtils__get_flow_file_details')
    def test_get_flow_files_queue_details_failure(self, mock_get_flow_file_details):
        # Arrange
        mock_flowfile_queues_api = MagicMock()
        mock_listing_request_entity = MagicMock()
        mock_listing_request_entity.listing_request.uri = "test_uri"
        mock_flowfile_queues_api.create_flow_file_listing.return_value = mock_listing_request_entity
        mock_get_flow_file_details.return_value = False

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.apis = {"flowfile_queues_api": mock_flowfile_queues_api}
        nifi_utils.reporting = MagicMock()

        # Act
        result = nifi_utils.get_flow_files_queue_details("test_connection_id")

        # Assert
        self.assertFalse(result)
        mock_flowfile_queues_api.create_flow_file_listing.assert_called_once_with("test_connection_id")
        mock_get_flow_file_details.assert_called_once_with("test_uri")

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.NifiProcessGroupUtils.'
           '_NifiProcessGroupUtils__get_flow_file_details')
    def test_get_flow_files_queue_details_exception(self, mock_get_flow_file_details):
        # Arrange
        mock_flowfile_queues_api = MagicMock()
        mock_flowfile_queues_api.create_flow_file_listing.side_effect = ValueError("Test Exception")
        mock_get_flow_file_details.return_value = False

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.apis = {"flowfile_queues_api": mock_flowfile_queues_api}
        nifi_utils.reporting = MagicMock()
        nifi_utils._NifiProcessGroupUtils__obj_exception = MagicMock()

        # Act
        result = nifi_utils.get_flow_files_queue_details("test_connection_id")

        # Assert
        self.assertFalse(result)
        mock_flowfile_queues_api.create_flow_file_listing.assert_called_once_with("test_connection_id")
        nifi_utils._NifiProcessGroupUtils__obj_exception.raise_generic_exception.assert_called_once_with(
            message="Error occurred while retrieving flow files for connection ID test_connection_id: Test Exception",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False
        )

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.schedule_process_group')
    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.get_process_group_status')
    @patch('time.sleep', return_value=None)  # Mock time.sleep to avoid delays
    def test_start_then_stop_pg_success(self, mock_sleep, mock_get_process_group_status, mock_schedule_process_group):
        # Arrange
        mock_process_group_status = MagicMock()
        mock_get_process_group_status.return_value = mock_process_group_status
        mock_schedule_process_group.return_value = True

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()
        nifi_utils.logger = MagicMock()

        # Act
        result = nifi_utils.start_then_stop_pg("test_pg_id", wait_time=5)

        # Assert
        self.assertTrue(result)
        mock_get_process_group_status.assert_called_once_with(pg_id="test_pg_id", detail="names")
        mock_schedule_process_group.assert_any_call("test_pg_id", scheduled=True)
        mock_schedule_process_group.assert_any_call("test_pg_id", scheduled=False)
        nifi_utils.reporting.insert_step.assert_called_with("Processor group found", "Processor group found", "Pass")
        nifi_utils.logger.info.assert_any_call("Process group %s started.", "test_pg_id")
        nifi_utils.logger.info.assert_any_call("Process group %s stopped after %s seconds.", "test_pg_id", 5)

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.get_process_group_status')
    def test_start_then_stop_pg_not_found(self, mock_get_process_group_status):
        # Arrange
        mock_get_process_group_status.return_value = None

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()
        nifi_utils.logger = MagicMock()

        # Act
        result = nifi_utils.start_then_stop_pg("test_pg_id")

        # Assert
        self.assertFalse(result)
        mock_get_process_group_status.assert_called_once_with(pg_id="test_pg_id", detail="names")
        nifi_utils.reporting.insert_step.assert_called_with("Processor group not found", "Processor group not found",
                                                            "Fail")
        nifi_utils.logger.warning.assert_called_with("Process group %s not found.", "test_pg_id")

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.schedule_process_group')
    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.get_process_group_status')
    def test_start_then_stop_pg_exception(self, mock_get_process_group_status, mock_schedule_process_group):
        # Arrange
        mock_get_process_group_status.side_effect = ValueError("Test Exception")

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()
        nifi_utils.logger = MagicMock()
        nifi_utils._NifiProcessGroupUtils__obj_exception = MagicMock()

        # Act
        result = nifi_utils.start_then_stop_pg("test_pg_id")

        # Assert
        self.assertFalse(result)
        mock_get_process_group_status.assert_called_once_with(pg_id="test_pg_id", detail="names")
        nifi_utils._NifiProcessGroupUtils__obj_exception.raise_generic_exception.assert_called_once_with(
            message="Error occurred while starting and stopping process group test_pg_id: Test Exception",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False
        )

    def test_get_access_config_success(self):
        # Arrange
        mock_access_api = MagicMock()
        mock_access_config_entity = MagicMock()
        mock_access_config_entity.config.to_dict.return_value = {"key": "value"}
        mock_access_api.get_login_config.return_value = mock_access_config_entity

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.apis = {"access_api": mock_access_api}
        nifi_utils.logger = MagicMock()
        nifi_utils.reporting = MagicMock()

        # Act
        result = nifi_utils.get_access_config()

        # Assert
        self.assertTrue(result)
        mock_access_api.get_login_config.assert_called_once()
        nifi_utils.logger.debug.assert_called_with("Access configuration retrieved: %s", {"key": "value"})
        nifi_utils.reporting.insert_step.assert_called_with(
            "Successfully retrieved NiFi access config",
            "Access configuration retrieved successfully",
            "Pass"
        )

    def test_get_access_config_failure(self):
        # Arrange
        mock_access_api = MagicMock()
        mock_access_config_entity = MagicMock()
        mock_access_config_entity.config.to_dict.return_value = {}
        mock_access_api.get_login_config.return_value = mock_access_config_entity

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.apis = {"access_api": mock_access_api}
        nifi_utils.reporting = MagicMock()

        # Act
        result = nifi_utils.get_access_config()

        # Assert
        self.assertFalse(result)
        mock_access_api.get_login_config.assert_called_once()
        nifi_utils.reporting.insert_step.assert_called_with(
            "Failed to retrieve NiFi access config",
            "Access configuration is empty or invalid",
            "Fail"
        )

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.Security.nifi_get_token')
    def test_get_security_token_success(self, mock_nifi_get_token):
        # Arrange
        mock_nifi_get_token.return_value = (True, "test_token")
        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.logger = MagicMock()

        # Act
        result = nifi_utils.get_security_token("username", "password", False)

        # Assert
        self.assertTrue(result)
        self.assertEqual(nifi_utils._NifiProcessGroupUtils__nifi_token, "test_token")
        nifi_utils.logger.info.assert_called_with("Successfully generated NiFi security token.")

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.Security.nifi_get_token')
    def test_get_security_token_failure(self, mock_nifi_get_token):
        # Arrange
        mock_nifi_get_token.return_value = (False, None)
        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.logger = MagicMock()

        # Act
        result = nifi_utils.get_security_token("username", "password", False)

        # Assert
        self.assertFalse(result)
        nifi_utils.logger.warning.assert_called_with("Failed to generate NiFi security token: Invalid credentials.")

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.Security.nifi_get_token')
    def test_get_security_token_exception(self, mock_nifi_get_token):
        # Arrange
        mock_nifi_get_token.side_effect = ValueError("Test Exception")
        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.logger = MagicMock()
        nifi_utils._NifiProcessGroupUtils__obj_exception = MagicMock()

        # Act
        result = nifi_utils.get_security_token("username", "password", False)

        # Assert
        self.assertFalse(result)
        nifi_utils._NifiProcessGroupUtils__obj_exception.raise_generic_exception.assert_called_once_with(
            message="Error occurred while generating NiFi security token: Test Exception",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False
        )

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.list_all_process_groups')
    def test_get_process_group_id_success(self, mock_list_all_process_groups):
        # Arrange
        mock_process_group = MagicMock()
        mock_process_group.to_dict.return_value = {
            "component": {"name": "test_pg_name", "id": "test_pg_id"}
        }
        mock_list_all_process_groups.return_value = [mock_process_group]

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()

        # Act
        success, component_id = nifi_utils.get_process_group_id("test_pg_name")

        # Assert
        self.assertTrue(success)
        self.assertEqual(component_id, "test_pg_id")
        nifi_utils.reporting.insert_step.assert_called_with(
            "Successfully retrieved process group ID for: test_pg_name",
            "Successfully retrieved process group ID",
            "Pass"
        )

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.list_all_process_groups')
    def test_get_process_group_id_not_found(self, mock_list_all_process_groups):
        # Arrange
        mock_list_all_process_groups.return_value = []

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()

        # Act
        success, component_id = nifi_utils.get_process_group_id("nonexistent_pg_name")

        # Assert
        self.assertFalse(success)
        self.assertIsNone(component_id)
        nifi_utils.reporting.insert_step.assert_called_with(
            "Failed to retrieve process group ID for: nonexistent_pg_name",
            "Process group not found",
            "Fail"
        )

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.list_all_process_groups')
    def test_get_process_group_id_exception(self, mock_list_all_process_groups):
        # Arrange
        mock_list_all_process_groups.side_effect = ValueError("Test Exception")

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()
        nifi_utils._NifiProcessGroupUtils__obj_exception = MagicMock()

        # Act
        success, component_id = nifi_utils.get_process_group_id("test_pg_name")

        # Assert
        self.assertFalse(success)
        self.assertIsNone(component_id)
        nifi_utils._NifiProcessGroupUtils__obj_exception.raise_generic_exception.assert_called_once_with(
            message="Error occurred while retrieving process group ID: Test Exception",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False
        )

    @patch(
        'cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.nifi.apis.flowfile_queues_api.FlowfileQueuesApi')
    def test_list_queue_data_success(self, mock_create_flow_file_listing):
        # Arrange
        mock_listing_request = MagicMock()
        mock_create_flow_file_listing.return_value = mock_listing_request

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.apis = {"flowfile_queues_api": MagicMock(create_flow_file_listing=mock_create_flow_file_listing)}
        nifi_utils.reporting = MagicMock()

        # Act
        result = nifi_utils.list_queue_data("test_connection_id")

        # Assert
        self.assertEqual(result, mock_listing_request)
        nifi_utils.reporting.insert_step.assert_called_with(
            "Successfully listed queue connection data",
            "Successfully listed queue connection data",
            "Pass"
        )

    @patch(
        'cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.nifi.apis.flowfile_queues_api.FlowfileQueuesApi')
    def test_list_queue_data_no_data(self, mock_create_flow_file_listing):
        # Arrange
        mock_create_flow_file_listing.return_value = None

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.apis = {"flowfile_queues_api": MagicMock(create_flow_file_listing=mock_create_flow_file_listing)}
        nifi_utils.reporting = MagicMock()

        # Act
        result = nifi_utils.list_queue_data("test_connection_id")

        # Assert
        self.assertIsNone(result)
        nifi_utils.reporting.insert_step.assert_called_with(
            "Failed to list queue connection data",
            "No data returned for the queue connection",
            "Fail"
        )

    @patch(
        'cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.nifi.apis.flowfile_queues_api.FlowfileQueuesApi.create_flow_file_listing'
    )
    def test_list_queue_data_exception(self, mock_create_flow_file_listing):
        # Arrange
        mock_create_flow_file_listing.side_effect = ValueError("Test Exception")

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.apis = {"flowfile_queues_api": MagicMock(create_flow_file_listing=mock_create_flow_file_listing)}
        nifi_utils.reporting = MagicMock()
        nifi_utils._NifiProcessGroupUtils__obj_exception = MagicMock()

        # Act
        result = nifi_utils.list_queue_data("test_connection_id")

        # Assert
        self.assertIsNone(result)
        mock_create_flow_file_listing.assert_called_once_with("test_connection_id")
        nifi_utils._NifiProcessGroupUtils__obj_exception.raise_generic_exception.assert_called_once_with(
            message="Error occurred while listing queue data for connection ID test_connection_id: Test Exception",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False
        )

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.list_all_connections')
    def test_list_connections_success(self, mock_list_all_connections):
        # Arrange
        mock_connection = MagicMock()
        mock_connection.to_dict.return_value = {"id": "test_connection_id", "name": "test_connection_name"}
        mock_list_all_connections.return_value = [mock_connection]

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.get_key_path_value = MagicMock(return_value="test_connection_name")

        # Act
        result = nifi_utils.list_connections(pg_id="test_pg_id", key_path="name")

        # Assert
        self.assertEqual(result, ["test_connection_name"])
        mock_list_all_connections.assert_called_once_with(pg_id="test_pg_id")
        nifi_utils.get_key_path_value.assert_called_once_with(
            json={"id": "test_connection_id", "name": "test_connection_name"},
            keyPath="name",
            keyPathType="absolute"
        )

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.list_all_connections')
    def test_list_connections_no_key_path(self, mock_list_all_connections):
        # Arrange
        mock_connection = MagicMock()
        mock_list_all_connections.return_value = [mock_connection]

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")

        # Act
        result = nifi_utils.list_connections(pg_id="test_pg_id")

        # Assert
        self.assertEqual(result, [mock_connection])
        mock_list_all_connections.assert_called_once_with(pg_id="test_pg_id")

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.list_all_connections')
    def test_list_connections_exception(self, mock_list_all_connections):
        # Arrange
        mock_list_all_connections.side_effect = ValueError("Test Exception")
        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils._NifiProcessGroupUtils__obj_exception = MagicMock()

        # Act
        result = nifi_utils.list_connections(pg_id="test_pg_id")

        # Assert
        self.assertEqual(result, [])
        mock_list_all_connections.assert_called_once_with(pg_id="test_pg_id")
        nifi_utils._NifiProcessGroupUtils__obj_exception.raise_generic_exception.assert_called_once_with(
            message="Error occurred while listing connections for process group ID test_pg_id: Test Exception",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False
        )

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.list_all_process_groups')
    def test_get_process_groups_success(self, mock_list_all_process_groups):
        # Arrange
        mock_pg = MagicMock()
        mock_pg.to_dict.return_value = {"id": "test_pg_id", "name": "test_pg_name"}
        mock_list_all_process_groups.return_value = [mock_pg]

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.get_key_path_value = MagicMock(return_value="test_pg_name")

        # Act
        result = nifi_utils.get_process_groups(pg_id="test_pg_id", key_path="name")

        # Assert
        self.assertEqual(result, ["test_pg_name"])
        mock_list_all_process_groups.assert_called_once_with(pg_id="test_pg_id")
        nifi_utils.get_key_path_value.assert_called_once_with(
            json={"id": "test_pg_id", "name": "test_pg_name"},
            keyPath="name",
            keyPathType="absolute"
        )

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.list_all_process_groups')
    def test_get_process_groups_no_key_path(self, mock_list_all_process_groups):
        # Arrange
        mock_pg = MagicMock()
        mock_list_all_process_groups.return_value = [mock_pg]

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")

        # Act
        result = nifi_utils.get_process_groups(pg_id="test_pg_id")

        # Assert
        self.assertEqual(result, [mock_pg])
        mock_list_all_process_groups.assert_called_once_with(pg_id="test_pg_id")

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.list_all_process_groups')
    def test_get_process_groups_exception(self, mock_list_all_process_groups):
        # Arrange
        mock_list_all_process_groups.side_effect = ValueError("Test Exception")
        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils._NifiProcessGroupUtils__obj_exception = MagicMock()

        # Act
        result = nifi_utils.get_process_groups(pg_id="test_pg_id")

        # Assert
        self.assertEqual(result, [])
        mock_list_all_process_groups.assert_called_once_with(pg_id="test_pg_id")
        nifi_utils._NifiProcessGroupUtils__obj_exception.raise_generic_exception.assert_called_once_with(
            message="Error occurred while retrieving process groups for ID test_pg_id: Test Exception",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False
        )

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.list_all_remote_process_groups')
    def test_get_remote_process_groups_success(self, mock_list_all_remote_process_groups):
        # Arrange
        mock_rpg = MagicMock()
        mock_rpg.to_dict.return_value = {"id": "test_rpg_id", "name": "test_rpg_name"}
        mock_list_all_remote_process_groups.return_value = [mock_rpg]

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.get_key_path_value = MagicMock(return_value="test_rpg_name")

        # Act
        result = nifi_utils.get_remote_process_groups(pg_id="test_pg_id", key_path="name")

        # Assert
        self.assertEqual(result, ["test_rpg_name"])
        mock_list_all_remote_process_groups.assert_called_once_with(pg_id="test_pg_id")
        nifi_utils.get_key_path_value.assert_called_once_with(
            json={"id": "test_rpg_id", "name": "test_rpg_name"},
            keyPath="name",
            keyPathType="absolute"
        )

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.list_all_remote_process_groups')
    def test_get_remote_process_groups_no_key_path(self, mock_list_all_remote_process_groups):
        # Arrange
        mock_rpg = MagicMock()
        mock_list_all_remote_process_groups.return_value = [mock_rpg]

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")

        # Act
        result = nifi_utils.get_remote_process_groups(pg_id="test_pg_id")

        # Assert
        self.assertEqual(result, [mock_rpg])
        mock_list_all_remote_process_groups.assert_called_once_with(pg_id="test_pg_id")

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.list_all_remote_process_groups')
    def test_get_remote_process_groups_exception(self, mock_list_all_remote_process_groups):
        # Arrange
        mock_list_all_remote_process_groups.side_effect = ValueError("Test Exception")
        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils._NifiProcessGroupUtils__obj_exception = MagicMock()

        # Act
        result = nifi_utils.get_remote_process_groups(pg_id="test_pg_id")

        # Assert
        self.assertEqual(result, [])
        mock_list_all_remote_process_groups.assert_called_once_with(pg_id="test_pg_id")
        nifi_utils._NifiProcessGroupUtils__obj_exception.raise_generic_exception.assert_called_once_with(
            message="Error occurred while retrieving remote process groups for process group ID test_pg_id: Test Exception",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False
        )

    @patch(
        'cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.set_remote_process_group_transmission')
    def test_change_remote_process_group_state_success(self, mock_set_transmission):
        # Arrange
        mock_set_transmission.return_value = True
        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()

        # Act
        result = nifi_utils.change_remote_process_group_state("test_rpg_id", True)

        # Assert
        self.assertTrue(result)
        mock_set_transmission.assert_called_once_with("test_rpg_id", enable=True, refresh=True)
        nifi_utils.reporting.insert_step.assert_called_with(
            "Successfully changed the state of the remote process group.",
            "State change completed successfully.",
            "Pass"
        )

    @patch(
        'cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.set_remote_process_group_transmission')
    def test_change_remote_process_group_state_failure(self, mock_set_transmission):
        # Arrange
        mock_set_transmission.return_value = None
        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()

        # Act
        result = nifi_utils.change_remote_process_group_state("test_rpg_id", False)

        # Assert
        self.assertFalse(result)
        mock_set_transmission.assert_called_once_with("test_rpg_id", enable=False, refresh=True)
        nifi_utils.reporting.insert_step.assert_called_with(
            "Failed to change the state of the remote process group.",
            "No status returned from the operation.",
            "Fail"
        )

    @patch(
        'cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.set_remote_process_group_transmission')
    def test_change_remote_process_group_state_exception(self, mock_set_transmission):
        # Arrange
        mock_set_transmission.side_effect = ValueError("Test Exception")
        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()
        nifi_utils._NifiProcessGroupUtils__obj_exception = MagicMock()

        # Act
        result = nifi_utils.change_remote_process_group_state("test_rpg_id", True)

        # Assert
        self.assertFalse(result)
        mock_set_transmission.assert_called_once_with("test_rpg_id", enable=True, refresh=True)
        nifi_utils._NifiProcessGroupUtils__obj_exception.raise_generic_exception.assert_called_once_with(
            message="Error occurred while changing the state of remote process group test_rpg_id: Test Exception",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False
        )

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.get_process_group')
    def test_get_process_group_q_count_success(self, mock_get_process_group):
        # Arrange
        mock_process_group = MagicMock()
        mock_process_group.to_dict.return_value = {
            "status": {
                "aggregate_snapshot": {
                    "queued_count": 10
                }
            }
        }
        mock_get_process_group.return_value = mock_process_group

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.get_key_path_value = MagicMock(return_value=10)

        # Act
        result = nifi_utils.get_process_group_q_count("test_pg_id")

        # Assert
        self.assertEqual(result, 10)
        mock_get_process_group.assert_called_once_with("test_pg_id", identifier_type="id")
        nifi_utils.get_key_path_value.assert_called_once_with(
            json=mock_process_group.to_dict(),
            keyPath="status/aggregate_snapshot/queued_count",
            keyPathType="absolute"
        )

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.get_process_group')
    def test_get_process_group_q_count_invalid_data(self, mock_get_process_group):
        # Arrange
        mock_process_group = MagicMock()
        mock_process_group.to_dict.return_value = {}
        mock_get_process_group.return_value = mock_process_group

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.get_key_path_value = MagicMock(return_value=None)

        # Act
        result = nifi_utils.get_process_group_q_count("test_pg_id")

        # Assert
        self.assertEqual(result, None)
        mock_get_process_group.assert_called_once_with("test_pg_id", identifier_type="id")
        nifi_utils.get_key_path_value.assert_called_once_with(
            json=mock_process_group.to_dict(),
            keyPath="status/aggregate_snapshot/queued_count",
            keyPathType="absolute"
        )

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.nipyapi.canvas.get_process_group')
    def test_get_process_group_q_count_exception(self, mock_get_process_group):
        # Arrange
        mock_get_process_group.side_effect = ValueError("Test Exception")

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils._NifiProcessGroupUtils__obj_exception = MagicMock()

        # Act
        result = nifi_utils.get_process_group_q_count("test_pg_id")

        # Assert
        self.assertEqual(result, 0)
        mock_get_process_group.assert_called_once_with("test_pg_id", identifier_type="id")
        nifi_utils._NifiProcessGroupUtils__obj_exception.raise_generic_exception.assert_called_once_with(
            message="Error occurred while retrieving queue count for process group ID test_pg_id: Test Exception",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False
        )

    @patch(
        'cafex_core.utils.apache_utils.nifi_process_group_utils.NifiProcessGroupUtils._NifiProcessGroupUtils__get_flow_file_details')
    def test_get_flow_file_count_success(self, mock_get_flow_file_details):
        # Arrange
        mock_flowfile_queues_api = MagicMock()
        mock_listing_request_entity = MagicMock()
        mock_listing_request_entity.listing_request.uri = "test_uri"
        mock_flowfile_queues_api.create_flow_file_listing.return_value = mock_listing_request_entity
        mock_get_flow_file_details.return_value = [{"file": "file1"}, {"file": "file2"}]

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.apis = {"flowfile_queues_api": mock_flowfile_queues_api}

        # Act
        result = nifi_utils.get_flow_file_count("test_connection_id")

        # Assert
        self.assertEqual(result, 2)
        mock_flowfile_queues_api.create_flow_file_listing.assert_called_once_with("test_connection_id")
        mock_get_flow_file_details.assert_called_once_with("test_uri")

    @patch(
        'cafex_core.utils.apache_utils.nifi_process_group_utils.NifiProcessGroupUtils._NifiProcessGroupUtils__get_flow_file_details')
    def test_get_flow_file_count_invalid_data(self, mock_get_flow_file_details):
        # Arrange
        mock_flowfile_queues_api = MagicMock()
        mock_listing_request_entity = MagicMock()
        mock_listing_request_entity.listing_request.uri = "test_uri"
        mock_flowfile_queues_api.create_flow_file_listing.return_value = mock_listing_request_entity
        mock_get_flow_file_details.return_value = []

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.apis = {"flowfile_queues_api": mock_flowfile_queues_api}

        # Act
        result = nifi_utils.get_flow_file_count("test_connection_id")

        # Assert
        self.assertEqual(result, 0)
        mock_flowfile_queues_api.create_flow_file_listing.assert_called_once_with("test_connection_id")
        mock_get_flow_file_details.assert_called_once_with("test_uri")

    @patch(
        'cafex_core.utils.apache_utils.nifi_process_group_utils.NifiProcessGroupUtils._NifiProcessGroupUtils__get_flow_file_details')
    def test_get_flow_file_count_exception(self, mock_get_flow_file_details):
        # Arrange
        mock_flowfile_queues_api = MagicMock()
        mock_flowfile_queues_api.create_flow_file_listing.side_effect = ValueError("Test Exception")
        mock_get_flow_file_details.return_value = []

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.apis = {"flowfile_queues_api": mock_flowfile_queues_api}
        nifi_utils._NifiProcessGroupUtils__obj_exception = MagicMock()

        # Act
        result = nifi_utils.get_flow_file_count("test_connection_id")

        # Assert
        self.assertEqual(result, 0)
        mock_flowfile_queues_api.create_flow_file_listing.assert_called_once_with("test_connection_id")
        nifi_utils._NifiProcessGroupUtils__obj_exception.raise_generic_exception.assert_called_once_with(
            message="Error occurred while retrieving flow file count for connection ID test_connection_id: Test Exception",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False
        )

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.ParseJsonData.get_value_from_key_path')
    def test_get_key_path_value_success(self, mock_get_value_from_key_path):
        # Arrange
        self.nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        mock_get_value_from_key_path.return_value = "value"
        kwargs = {
            "json": {"key": "value"},
            "keyPath": "key",
            "keyPathType": "absolute",
            "delimiter": "/"
        }

        # Act
        result = self.nifi_utils.get_key_path_value(**kwargs)

        # Assert
        self.assertEqual(result, "value")
        mock_get_value_from_key_path.assert_called_once_with(**kwargs)

    def test_get_key_path_value_missing_json(self):
        # Arrange
        self.nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        self.nifi_utils.logger = MagicMock()
        kwargs = {
            "keyPath": "key",
            "keyPathType": "absolute"
        }

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.nifi_utils.get_key_path_value(**kwargs)
        self.assertEqual(str(context.exception), "json argument is required.")
        self.nifi_utils.logger.info.assert_called_with("No json argument provided")

    def test_get_key_path_value_missing_keyPath(self):
        # Arrange
        self.nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        self.nifi_utils.logger = MagicMock()
        kwargs = {
            "json": {"key": "value"},
            "keyPathType": "absolute"
        }

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.nifi_utils.get_key_path_value(**kwargs)
        self.assertEqual(str(context.exception), "keyPath argument is required.")
        self.nifi_utils.logger.info.assert_called_with("No keyPath argument provided")

    def test_get_key_path_value_missing_keyPathType(self):
        self.nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        self.nifi_utils.logger = MagicMock()
        # Arrange
        kwargs = {
            "json": {"key": "value"},
            "keyPath": "key"
        }

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.nifi_utils.get_key_path_value(**kwargs)
        self.assertEqual(str(context.exception), "keyPathType argument is required.")
        self.nifi_utils.logger.info.assert_called_with("No keyPathType argument provided")

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.ParseJsonData.get_value_from_key_path')
    def test_get_key_path_value_exception(self, mock_get_value_from_key_path):
        # Arrange
        self.nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        self.nifi_utils.logger = MagicMock()
        mock_get_value_from_key_path.side_effect = ValueError("Test Exception")
        kwargs = {
            "json": {"key": "value"},
            "keyPath": "key",
            "keyPathType": "absolute"
        }

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.nifi_utils.get_key_path_value(**kwargs)
        self.assertEqual(str(context.exception), "Test Exception")

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.NifiProcessGroupUtils.call_request')
    def test_get_flow_file_details_success(self, mock_call_request):
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "listingRequest": {
                "flowFileSummaries": [{"file": "file1"}, {"file": "file2"}]
            }
        }
        mock_call_request.return_value = mock_response

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils._NifiProcessGroupUtils__nifi_token = "test_token"

        # Act
        result = nifi_utils._NifiProcessGroupUtils__get_flow_file_details("test_uri")

        # Assert
        self.assertEqual(result, [{"file": "file1"}, {"file": "file2"}])
        mock_call_request.assert_called_once_with(
            "GET", "test_uri", {"Content-Type": "application/json", "Authorization": "test_token"}
        )

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.NifiProcessGroupUtils.call_request')
    def test_get_flow_file_details_invalid_data(self, mock_call_request):
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {"listingRequest": {"flowFileSummaries": []}}
        mock_call_request.return_value = mock_response

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")

        # Act
        result = nifi_utils._NifiProcessGroupUtils__get_flow_file_details("test_uri")

        # Assert
        self.assertEqual(result, [])
        mock_call_request.assert_called_once_with(
            "GET", "test_uri", {"Content-Type": "application/json"}
        )

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.NifiProcessGroupUtils.call_request')
    def test_get_flow_file_details_exception(self, mock_call_request):
        # Arrange
        mock_call_request.side_effect = ValueError("Test Exception")

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils._NifiProcessGroupUtils__obj_exception = MagicMock()

        # Act
        result = nifi_utils._NifiProcessGroupUtils__get_flow_file_details("test_uri")

        # Assert
        self.assertFalse(result)
        mock_call_request.assert_called_once_with(
            "GET", "test_uri", {"Content-Type": "application/json"}
        )
        nifi_utils._NifiProcessGroupUtils__obj_exception.raise_generic_exception.assert_called_once_with(
            message="Error occurred while retrieving flow file details from URI test_uri: Test Exception",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False,
        )

    @patch('requests.get')
    def test_call_request_get_success(self, mock_get):
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        headers = {"Accept": "application/json"}

        # Act
        response = nifi_utils.call_request("GET", "http://test.com", headers)

        # Assert
        self.assertEqual(response.status_code, 200)
        mock_get.assert_called_once_with(
            "http://test.com",
            headers=headers,
            verify=False,
            allow_redirects=False,
            cookies={},
            auth="",
            timeout=None,
            proxies=None,
        )

    @patch('requests.delete')
    def test_call_request_delete_success(self, mock_delete):
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        headers = {"Authorization": "Bearer token"}

        # Act
        response = nifi_utils.call_request("DELETE", "http://test.com", headers)

        # Assert
        self.assertEqual(response.status_code, 204)
        mock_delete.assert_called_once_with(
            "http://test.com",
            headers=headers,
            verify=False,
            allow_redirects=False,
            cookies={},
            auth="",
            data=None,
            json=None,
            timeout=None,
            proxies=None,
        )

    def test_call_request_invalid_method(self):
        # Arrange
        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        headers = {"Accept": "application/json"}

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            nifi_utils.call_request("INVALID", "http://test.com", headers)
        self.assertEqual(str(context.exception),
                         "Invalid HTTP method: INVALID. Valid options are: GET, POST, PUT, PATCH, DELETE")

    @patch('requests.get')
    def test_call_request_exception(self, mock_get):
        # Arrange
        mock_get.side_effect = requests.RequestException("Test Exception")

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.logger = MagicMock()
        headers = {"Accept": "application/json"}

        # Act & Assert
        with self.assertRaises(requests.RequestException):
            nifi_utils.call_request("GET", "http://test.com", headers)
        nifi_utils.logger.exception.assert_called_once_with("Error in Apache call request method: %s", "Test Exception")

    @patch('cafex_core.utils.apache_utils.nifi_process_group_utils.Security.get_auth_string')
    @patch('requests.get')
    def test_call_request_with_auth_string(self, mock_get, mock_get_auth_string):
        # Arrange
        mock_get_auth_string.return_value = "Basic test_auth_string"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        headers = {"Accept": "application/json"}

        # Act
        response = nifi_utils.call_request(
            method="GET",
            url="http://test.com",
            headers=headers,
            auth_type="basic",
            auth_username="user",
            auth_password="pass"
        )

        # Assert
        mock_get_auth_string.assert_called_once_with("basic", "user", "pass")
        self.assertEqual(response.status_code, 200)

    def test_call_request_with_null_url(self):
        # Arrange
        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        headers = {"Accept": "application/json"}

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            nifi_utils.call_request(
                method="GET",
                url=None,  # Passing a null URL
                headers=headers
            )
        self.assertEqual(str(context.exception), "URL cannot be null")

    def test_call_request_post_put_patch_without_payload(self):
        # Arrange
        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        headers = {"Accept": "application/json"}

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            nifi_utils.call_request(
                method="POST",  # Can also test with "PUT" or "PATCH"
                url="http://test.com",
                headers=headers,
                payload=None  # No payload provided
            )
        self.assertEqual(str(context.exception), "Payload is required for POST, PUT, and PATCH requests.")

    @patch('requests.request')
    def test_call_request_post_success(self, mock_request):
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"message": "Created"}
        mock_request.return_value = mock_response

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        headers = {"Content-Type": "application/json"}
        payload = {"key": "value"}

        # Act
        response = nifi_utils.call_request(
            method="POST",
            url="http://test.com",
            headers=headers,
            payload=payload
        )

        # Assert
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"message": "Created"})

    def test_get_access_config_api_exception(self):
        # Arrange
        mock_access_api = MagicMock()
        mock_access_api.get_login_config.side_effect = nipyapi.nifi.rest.ApiException("API Exception occurred")

        nifi_utils = NifiProcessGroupUtils("http://localhost:8080")
        nifi_utils.apis = {"access_api": mock_access_api}  # Directly set the apis attribute
        nifi_utils._NifiProcessGroupUtils__obj_exception = MagicMock()

        # Act
        result = nifi_utils.get_access_config()

        # Assert
        self.assertFalse(result)

    @patch('nipyapi.config.registry_config')
    def test_init_with_registry_url(self, mock_registry_config):
        # Arrange
        pstr_nifi_url = "http://localhost:8080"
        pstr_nifi_registry_url = "http://localhost:18080"
        expected_host = pstr_nifi_registry_url + "/nifi-registry-api"

        # Act
        nifi_utils = NifiProcessGroupUtils(pstr_nifi_url, pstr_nifi_registry_url)

        # Assert
        self.assertEqual(mock_registry_config.host, expected_host)


if __name__ == '__main__':
    unittest.main()
