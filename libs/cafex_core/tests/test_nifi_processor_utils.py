import json
import unittest
from unittest.mock import patch, MagicMock

from nipyapi.nifi.rest import ApiException

from cafex_core.utils.apache_utils.nifi_processor_utils import NifiProcessorUtils


class TestNifiProcessorUtils(unittest.TestCase):

    def test_check_processor_status_success(self):
        # Arrange
        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils.apis = MagicMock()  # Mock the apis attribute
        mock_flow_api = MagicMock()
        mock_processor_status = MagicMock()
        mock_processor_status.processor_status.to_dict.return_value = {"status": "RUNNING"}
        mock_flow_api.get_processor_status.return_value = mock_processor_status
        nifi_utils.apis.get.return_value = mock_flow_api
        nifi_utils.reporting = MagicMock()
        nifi_utils.logger = MagicMock()

        # Act
        result = nifi_utils.check_processor_status("test_processor_id")

        # Assert
        self.assertTrue(result)
        mock_flow_api.get_processor_status.assert_called_once_with("test_processor_id")
        nifi_utils.reporting.insert_step.assert_called_with(
            "Successfully returned processor status for test_processor_id",
            "Successfully returned processor status",
            "Pass"
        )
        nifi_utils.logger.info.assert_called_with(
            "Successfully returned processor status for %s.", "test_processor_id"
        )

    def test_check_processor_status_not_available(self):
        # Arrange
        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils.apis = MagicMock()  # Mock the apis attribute
        mock_flow_api = MagicMock()
        mock_processor_status = MagicMock()
        mock_processor_status.processor_status.to_dict.return_value = None
        mock_flow_api.get_processor_status.return_value = mock_processor_status
        nifi_utils.apis.get.return_value = mock_flow_api
        nifi_utils.reporting = MagicMock()
        nifi_utils.logger = MagicMock()

        # Act
        result = nifi_utils.check_processor_status("test_processor_id")

        # Assert
        self.assertFalse(result)
        mock_flow_api.get_processor_status.assert_called_once_with("test_processor_id")
        nifi_utils.reporting.insert_step.assert_called_with(
            "Processor status retrieval",
            "Processor with ID test_processor_id does not exist or is not available.",
            "Fail"
        )
        nifi_utils.logger.error.assert_called_with(
            "Processor with ID %s does not exist or is not available.", "test_processor_id"
        )

    def test_check_processor_status_exception(self):
        # Arrange
        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils.apis = MagicMock()  # Mock the apis attribute
        nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()  # Mock the exception handler
        mock_flow_api = MagicMock()
        mock_flow_api.get_processor_status.side_effect = ValueError("Test exception")
        nifi_utils.apis.get.return_value = mock_flow_api

        # Act
        result = nifi_utils.check_processor_status("test_processor_id")

        # Assert
        self.assertFalse(result)
        mock_flow_api.get_processor_status.assert_called_once_with("test_processor_id")
        nifi_utils._NifiProcessorUtils__obj_exception.raise_generic_exception.assert_called_once_with(
            message="Error occurred while checking status for processor test_processor_id: Test exception",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False
        )

    def test_change_processor_state_success(self):
        # Arrange
        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils.call_request = MagicMock()
        nifi_utils.logger = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content.decode.return_value = '{"status": "success"}'
        nifi_utils.call_request.return_value = mock_response

        # Act
        result = nifi_utils.change_processor_state(
            "http://localhost:8080", '{"state": "RUNNING"}', "test_processor_id"
        )

        # Assert
        self.assertTrue(result)
        nifi_utils.call_request.assert_called_once_with(
            "PUT",
            "http://localhost:8080/nifi-api/flow/process-groups/test_processor_id",
            {"Content-Type": "application/json"},
            pstr_payload='{"state": "RUNNING"}'
        )
        nifi_utils.logger.info.assert_called_with(
            "Successfully changed processor state for ID: %s", "test_processor_id"
        )

    def test_change_processor_state_failure(self):
        # Arrange
        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils.call_request = MagicMock()
        nifi_utils.logger = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.content.decode.return_value = '{"error": "Bad Request"}'
        nifi_utils.call_request.return_value = mock_response

        # Act
        result = nifi_utils.change_processor_state(
            "http://localhost:8080", '{"state": "STOPPED"}', "test_processor_id"
        )

        # Assert
        self.assertFalse(result)
        nifi_utils.call_request.assert_called_once_with(
            "PUT",
            "http://localhost:8080/nifi-api/flow/process-groups/test_processor_id",
            {"Content-Type": "application/json"},
            pstr_payload='{"state": "STOPPED"}'
        )
        nifi_utils.logger.warning.assert_called_with(
            "Failed to change processor state for ID: %s .Response: %s",
            "test_processor_id",
            '{"error": "Bad Request"}'
        )

    def test_change_processor_state_exception(self):
        # Arrange
        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils.call_request = MagicMock(side_effect=ValueError("Test exception"))
        nifi_utils.logger = MagicMock()
        nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()

        # Act
        result = nifi_utils.change_processor_state(
            "http://localhost:8080", '{"state": "RUNNING"}', "test_processor_id"
        )

        # Assert
        self.assertFalse(result)
        nifi_utils._NifiProcessorUtils__obj_exception.raise_generic_exception.assert_called_once_with(
            message="Error occurred while changing processor state for ID test_processor_id: Test exception",
            insert_report=True,
            trim_log=True,
            log_local=True,
            fail_test=False
        )

    @patch("nipyapi.canvas.schedule_processor")
    @patch("nipyapi.config.nifi_config")
    def test_change_state_to_running_success(self, mock_config, mock_schedule_processor):
        # Arrange
        mock_config.host = "http://localhost:8080"
        mock_schedule_processor.return_value = True
        nifi_utils = NifiProcessorUtils("http://localhost:8080")  # Use the actual class
        nifi_utils.reporting = MagicMock()
        nifi_utils.logger = MagicMock()
        nifi_utils._NifiProcessorUtils__get_processor = MagicMock(return_value=(None, "mock_processor"))

        # Act
        result = nifi_utils.change_nifi_processor_state("http://localhost:8080", "test_processor_id", "RUNNING")

        # Assert
        self.assertTrue(result)
        mock_schedule_processor.assert_called_once_with("mock_processor", scheduled=True)
        nifi_utils.reporting.insert_step.assert_called_with(
            "Processor state: RUNNING should be changed for http://localhost:8080",
            "Successfully changed processor state: RUNNING",
            "Pass"
        )
        nifi_utils.logger.info.assert_called_with(
            "Successfully changed processor %s state to %s.", "test_processor_id", "RUNNING"
        )

    @patch("nipyapi.canvas.schedule_processor")
    @patch("nipyapi.config.nifi_config")
    def test_change_state_to_stopped_success(self, mock_config, mock_schedule_processor):
        # Arrange
        mock_config.host = "http://localhost:8080"
        mock_schedule_processor.return_value = True
        nifi_utils = NifiProcessorUtils("http://localhost:8080")  # Use the actual class
        nifi_utils.reporting = MagicMock()
        nifi_utils.logger = MagicMock()
        nifi_utils._NifiProcessorUtils__get_processor = MagicMock(return_value=(None, "mock_processor"))

        # Act
        result = nifi_utils.change_nifi_processor_state("http://localhost:8080", "test_processor_id", "STOPPED")

        # Assert
        self.assertTrue(result)
        mock_schedule_processor.assert_called_once_with("mock_processor", scheduled=False)
        nifi_utils.reporting.insert_step.assert_called_with(
            "Processor state: STOPPED should be changed for http://localhost:8080",
            "Successfully changed processor state: STOPPED",
            "Pass"
        )
        nifi_utils.logger.info.assert_called_with(
            "Successfully changed processor %s state to %s.", "test_processor_id", "STOPPED"
        )

    @patch("nipyapi.canvas.schedule_processor")
    @patch("nipyapi.config.nifi_config")
    def test_change_state_failure(self, mock_config, mock_schedule_processor):
        # Arrange
        mock_config.host = "http://localhost:8080"
        mock_schedule_processor.return_value = False
        nifi_utils = NifiProcessorUtils("http://localhost:8080")  # Use the actual class
        nifi_utils.reporting = MagicMock()
        nifi_utils.logger = MagicMock()
        nifi_utils._NifiProcessorUtils__get_processor = MagicMock(return_value=(None, "mock_processor"))

        # Act
        result = nifi_utils.change_nifi_processor_state("http://localhost:8080", "test_processor_id", "RUNNING")

        # Assert
        self.assertFalse(result)
        mock_schedule_processor.assert_called_once_with("mock_processor", scheduled=True)
        nifi_utils.reporting.insert_step.assert_called_with(
            "Failed to change processor state: RUNNING",
            "Failed to change processor state",
            "Fail"
        )
        nifi_utils.logger.warning.assert_called_with(
            "Failed to change processor %s state to %s.", "test_processor_id", "RUNNING"
        )

    @patch("nipyapi.canvas.schedule_processor")
    @patch("nipyapi.config.nifi_config")
    def test_change_state_exception(self, mock_config, mock_schedule_processor):
        # Arrange
        mock_config.host = "http://localhost:8080"
        mock_schedule_processor.side_effect = ApiException("Test exception")
        nifi_utils = NifiProcessorUtils("http://localhost:8080")  # Use the actual class
        nifi_utils.reporting = MagicMock()
        nifi_utils.logger = MagicMock()
        nifi_utils._NifiProcessorUtils__get_processor = MagicMock(return_value=(None, "mock_processor"))
        nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()

        # Act
        result = nifi_utils.change_nifi_processor_state("http://localhost:8080", "test_processor_id", "RUNNING")

        # Assert
        self.assertFalse(result)
        mock_schedule_processor.assert_called_once_with("mock_processor", scheduled=True)

    @patch("nipyapi.canvas.list_all_processors")
    def test_get_processor_id_success(self, mock_list_all_processors):
        # Arrange
        mock_processor = MagicMock()
        mock_processor.to_dict.return_value = {
            "component": {"name": "test_processor", "id": "test_id"}
        }
        mock_list_all_processors.return_value = [mock_processor]
        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()

        # Act
        result = nifi_utils.get_processor_id("test_processor")

        # Assert
        self.assertTrue(result)
        mock_list_all_processors.assert_called_once_with(pg_id="root")
        nifi_utils.reporting.insert_step.assert_called_with(
            "Successfully retrieved processor ID for: test_processor",
            "Successfully retrieved processor ID",
            "Pass"
        )

    @patch("nipyapi.canvas.list_all_processors")
    def test_get_processor_id_not_found(self, mock_list_all_processors):
        # Arrange
        mock_processor = MagicMock()
        mock_processor.to_dict.return_value = {
            "component": {"name": "other_processor", "id": "other_id"}
        }
        mock_list_all_processors.return_value = [mock_processor]
        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()

        # Act
        result = nifi_utils.get_processor_id("test_processor")

        # Assert
        self.assertFalse(result)
        mock_list_all_processors.assert_called_once_with(pg_id="root")
        nifi_utils.reporting.insert_step.assert_called_with(
            "Failed to retrieve processor ID for: test_processor",
            "Processor not found",
            "Fail"
        )

    @patch("nipyapi.canvas.list_all_processors")
    def test_get_processor_id_exception(self, mock_list_all_processors):
        # Arrange
        mock_list_all_processors.side_effect = ApiException("Test exception")
        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()
        nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()

        # Act
        result = nifi_utils.get_processor_id("test_processor")

        # Assert
        self.assertFalse(result)
        mock_list_all_processors.assert_called_once_with(pg_id="root")

    @patch("nipyapi.canvas.get_processor")
    def test_get_processor_properties_success(self, mock_get_processor):
        # Arrange
        mock_processor = MagicMock()
        mock_processor.to_dict.return_value = {
            "component": {
                "config": {"property1": "value1", "property2": "value2"}
            }
        }
        mock_get_processor.return_value = mock_processor
        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()

        # Act
        result = nifi_utils.get_processor_properties("test_processor_id")

        # Assert
        self.assertEqual(result, {"property1": "value1", "property2": "value2"})
        mock_get_processor.assert_called_once_with("test_processor_id")
        nifi_utils.reporting.insert_step.assert_called_with(
            "Successfully retrieved properties for processor ID: test_processor_id",
            "Properties retrieved successfully",
            "Pass"
        )

    @patch("nipyapi.canvas.get_processor")
    def test_get_processor_properties_not_found(self, mock_get_processor):
        # Arrange
        mock_get_processor.return_value = None
        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()

        # Act
        result = nifi_utils.get_processor_properties("test_processor_id")

        # Assert
        self.assertFalse(result)
        mock_get_processor.assert_called_once_with("test_processor_id")
        nifi_utils.reporting.insert_step.assert_called_with(
            "Failed to retrieve properties for processor ID: test_processor_id",
            "Processor not found",
            "Fail"
        )

    @patch("nipyapi.canvas.get_processor")
    def test_get_processor_properties_exception(self, mock_get_processor):
        # Arrange
        mock_get_processor.side_effect = ApiException("Test exception")
        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()
        nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()

        # Act
        result = nifi_utils.get_processor_properties("test_processor_id")

        # Assert
        self.assertFalse(result)
        mock_get_processor.assert_called_once_with("test_processor_id")

    @patch("nipyapi.canvas.get_processor")
    def test_update_processor_properties_success(self, mock_get_processor):
        # Arrange
        mock_processor = MagicMock()
        mock_processor.revision.client_id = "test_client_id"
        mock_processor.revision.version = 1
        mock_get_processor.return_value = mock_processor

        mock_response = MagicMock()
        mock_response.status_code = 200

        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils.call_request = MagicMock(return_value=mock_response)
        nifi_utils.reporting = MagicMock()

        properties = {"property_name": "value"}

        # Act
        result = nifi_utils.update_processor_properties("test_processor_id", properties)

        # Assert
        self.assertTrue(result)
        nifi_utils.call_request.assert_called_once_with(
            "PUT",
            "/nifi-api/processors/test_processor_id",
            {"Content-Type": "application/json"},
            pstr_payload=json.dumps({
                "revision": {
                    "clientId": "test_client_id",
                    "version": 1
                },
                "component": {
                    "config": properties
                }
            })
        )
        nifi_utils.reporting.insert_step.assert_called_with(
            "Successfully updated properties for processor ID: test_processor_id",
            "Properties updated successfully",
            "Pass"
        )

    @patch("nipyapi.canvas.get_processor")
    def test_update_processor_properties_failure(self, mock_get_processor):
        # Arrange
        mock_processor = MagicMock()
        mock_processor.revision.client_id = "test_client_id"
        mock_processor.revision.version = 1
        mock_get_processor.return_value = mock_processor

        mock_response = MagicMock()
        mock_response.status_code = 400

        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils.call_request = MagicMock(return_value=mock_response)
        nifi_utils.reporting = MagicMock()

        properties = {"property_name": "value"}

        # Act
        result = nifi_utils.update_processor_properties("test_processor_id", properties)

        # Assert
        self.assertFalse(result)
        nifi_utils.reporting.insert_step.assert_called_with(
            "Failed to update properties for processor ID: test_processor_id",
            "Update failed",
            "Fail"
        )

    @patch("nipyapi.canvas.get_processor")
    def test_update_processor_properties_exception(self, mock_get_processor):
        # Arrange
        mock_get_processor.side_effect = ApiException("Test exception")

        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()

        properties = {"property_name": "value"}

        # Act
        result = nifi_utils.update_processor_properties("test_processor_id", properties)

        # Assert
        self.assertFalse(result)

    @patch("nipyapi.canvas.get_processor")
    def test_get_processor_success(self, mock_get_processor):
        # Arrange
        mock_processor = MagicMock()
        mock_get_processor.return_value = mock_processor
        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()

        # Act
        success, processor = nifi_utils._NifiProcessorUtils__get_processor("test_processor_id")

        # Assert
        self.assertTrue(success)
        self.assertEqual(processor, mock_processor)
        mock_get_processor.assert_called_once_with("test_processor_id", identifier_type="id")
        nifi_utils.reporting.insert_step.assert_called_with(
            "Successfully retrieved processor details: test_processor_id",
            "Successfully retrieved processor details",
            "Pass"
        )

    @patch("nipyapi.canvas.get_processor")
    def test_get_processor_not_found(self, mock_get_processor):
        # Arrange
        mock_get_processor.return_value = None
        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()

        # Act
        success, processor = nifi_utils._NifiProcessorUtils__get_processor("test_processor_id")

        # Assert
        self.assertFalse(success)
        self.assertIsNone(processor)
        mock_get_processor.assert_called_once_with("test_processor_id", identifier_type="id")
        nifi_utils.reporting.insert_step.assert_called_with(
            "Failed to retrieve processor details: test_processor_id",
            "Unable to get processor details",
            "Fail"
        )

    @patch("nipyapi.canvas.get_processor")
    def test_get_processor_exception(self, mock_get_processor):
        # Arrange
        mock_get_processor.side_effect = ApiException("Test exception")
        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()

        # Act
        success, processor = nifi_utils._NifiProcessorUtils__get_processor("test_processor_id")

        # Assert
        self.assertFalse(success)
        self.assertIsNone(processor)
        mock_get_processor.assert_called_once_with("test_processor_id", identifier_type="id")

    @patch("nipyapi.canvas.list_all_processors")
    def test_get_processors_success(self, mock_list_all_processors):
        # Arrange
        mock_processor = MagicMock()
        mock_processor.to_dict.return_value = {"component": {"name": "test_processor"}}
        mock_list_all_processors.return_value = [mock_processor]
        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils.get_key_path_value = MagicMock()

        # Act
        result = nifi_utils.get_processors("test_pg_id")

        # Assert
        self.assertEqual(result, [mock_processor])
        mock_list_all_processors.assert_called_once_with(pg_id="test_pg_id")

    @patch("nipyapi.canvas.list_all_processors")
    def test_get_processors_with_key_path(self, mock_list_all_processors):
        # Arrange
        mock_processor = MagicMock()
        mock_processor.to_dict.return_value = {"component": {"name": "test_processor"}}
        mock_list_all_processors.return_value = [mock_processor]
        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils.get_key_path_value = MagicMock(return_value="test_value")

        # Act
        result = nifi_utils.get_processors("test_pg_id", key_path="component.name")

        # Assert
        self.assertEqual(result, ["test_value"])
        mock_list_all_processors.assert_called_once_with(pg_id="test_pg_id")
        nifi_utils.get_key_path_value.assert_called_once_with(
            json={"component": {"name": "test_processor"}},
            keyPath="component.name",
            keyPathType="absolute"
        )

    @patch("nipyapi.canvas.list_all_processors")
    def test_get_processors_exception(self, mock_list_all_processors):
        # Arrange
        mock_list_all_processors.side_effect = ApiException("Test exception")
        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()

        # Act
        result = nifi_utils.get_processors("test_pg_id")

        # Assert
        self.assertEqual(result, [])
        mock_list_all_processors.assert_called_once_with(pg_id="test_pg_id")

    @patch("nipyapi.canvas.get_processor")
    def test_get_processor_q_count_success(self, mock_get_processor):
        # Arrange
        mock_processor = MagicMock()
        mock_processor.to_dict.return_value = {
            "status": {
                "aggregate_snapshot": {
                    "queued_count": 5
                }
            }
        }
        mock_get_processor.return_value = mock_processor
        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils.get_key_path_value = MagicMock(return_value=5)

        # Act
        result = nifi_utils.get_processor_q_count("test_processor_id")

        # Assert
        self.assertEqual(result, 5)
        mock_get_processor.assert_called_once_with("test_processor_id", identifier_type="id")
        nifi_utils.get_key_path_value.assert_called_once_with(
            json=mock_processor.to_dict(),
            keyPath="status/aggregate_snapshot/queued_count",
            keyPathType="absolute"
        )

    @patch("nipyapi.canvas.get_processor")
    def test_get_processor_q_count_exception(self, mock_get_processor):
        # Arrange
        mock_get_processor.side_effect = ApiException("Test exception")
        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()

        # Act
        result = nifi_utils.get_processor_q_count("test_processor_id")

        # Assert
        self.assertEqual(result, 0)
        mock_get_processor.assert_called_once_with("test_processor_id", identifier_type="id")

    @patch("nipyapi.canvas.get_component_connections")
    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils._NifiProcessorUtils__get_processor")
    def test_get_component_connections_success(self, mock_get_processor, mock_get_component_connections):
        # Arrange
        mock_processor = MagicMock()
        mock_get_processor.return_value = (True, mock_processor)
        mock_connection = MagicMock()
        mock_connection.to_dict.return_value = {
            "status": {
                "name": "test_connection",
                "id": "test_connection_id",
                "source_id": "test_processor_id",
                "destination_id": "other_processor_id"
            }
        }
        mock_get_component_connections.return_value = [mock_connection]

        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()

        # Act
        success, connections = nifi_utils.get_component_connections("test_processor_id")

        # Assert
        self.assertTrue(success)
        self.assertEqual(connections, {
            "source": {"test_connection": "test_connection_id"},
            "destination": {}
        })
        mock_get_processor.assert_called_once_with("test_processor_id")
        mock_get_component_connections.assert_called_once_with(mock_processor)
        nifi_utils.reporting.insert_step.assert_called_with(
            "Successfully retrieved component connections for: test_processor_id",
            "Successfully retrieved component connections",
            "Pass"
        )

    @patch("nipyapi.canvas.get_component_connections")
    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils._NifiProcessorUtils__get_processor")
    def test_get_component_connections_no_connections(self, mock_get_processor, mock_get_component_connections):
        # Arrange
        mock_processor = MagicMock()
        mock_get_processor.return_value = (True, mock_processor)
        mock_get_component_connections.return_value = []

        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()

        # Act
        success, connections = nifi_utils.get_component_connections("test_processor_id")

        # Assert
        self.assertFalse(success)
        self.assertEqual(connections, {"source": {}, "destination": {}})
        mock_get_processor.assert_called_once_with("test_processor_id")
        mock_get_component_connections.assert_called_once_with(mock_processor)
        nifi_utils.reporting.insert_step.assert_called_with(
            "Unable to get component connections for: test_processor_id",
            "No connections found",
            "Fail"
        )

    @patch("nipyapi.canvas.get_component_connections")
    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils._NifiProcessorUtils__get_processor")
    def test_get_component_connections_return_list(self, mock_get_processor, mock_get_component_connections):
        # Arrange
        mock_processor = MagicMock()
        mock_get_processor.return_value = (True, mock_processor)
        mock_connection = MagicMock()
        mock_connection.to_dict.return_value = {
            "status": {
                "name": "test_connection",
                "id": "test_connection_id",
                "source_id": "test_processor_id",
                "destination_id": "other_processor_id"
            }
        }
        mock_get_component_connections.return_value = [mock_connection]

        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()

        # Act
        success, connections = nifi_utils.get_component_connections("test_processor_id", return_list=True)

        # Assert
        self.assertTrue(success)
        self.assertEqual(connections, {
            "source": {"test_connection": ["test_connection_id"]},
            "destination": {}
        })
        mock_get_processor.assert_called_once_with("test_processor_id")
        mock_get_component_connections.assert_called_once_with(mock_processor)
        nifi_utils.reporting.insert_step.assert_called_with(
            "Successfully retrieved component connections for: test_processor_id",
            "Successfully retrieved component connections",
            "Pass"
        )

    @patch("nipyapi.canvas.get_component_connections")
    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils._NifiProcessorUtils__get_processor")
    def test_get_component_connections_destination_id(self, mock_get_processor, mock_get_component_connections):
        # Arrange
        mock_processor = MagicMock()
        mock_get_processor.return_value = (True, mock_processor)
        mock_connection = MagicMock()
        mock_connection.to_dict.return_value = {
            "status": {
                "name": "test_connection",
                "id": "test_connection_id",
                "source_id": "other_processor_id",
                "destination_id": "test_processor_id"
            }
        }
        mock_get_component_connections.return_value = [mock_connection]

        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()

        # Act
        success, connections = nifi_utils.get_component_connections("test_processor_id", return_list=True)

        # Assert
        self.assertTrue(success)
        self.assertEqual(connections, {
            "source": {},
            "destination": {"test_connection": ["test_connection_id"]}
        })
        mock_get_processor.assert_called_once_with("test_processor_id")
        mock_get_component_connections.assert_called_once_with(mock_processor)
        nifi_utils.reporting.insert_step.assert_called_with(
            "Successfully retrieved component connections for: test_processor_id",
            "Successfully retrieved component connections",
            "Pass"
        )

    @patch("nipyapi.canvas.get_component_connections")
    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils._NifiProcessorUtils__get_processor")
    def test_get_component_connections_destination_id_no_list(self, mock_get_processor, mock_get_component_connections):
        # Arrange
        mock_processor = MagicMock()
        mock_get_processor.return_value = (True, mock_processor)
        mock_connection = MagicMock()
        mock_connection.to_dict.return_value = {
            "status": {
                "name": "test_connection",
                "id": "test_connection_id",
                "source_id": "other_processor_id",
                "destination_id": "test_processor_id"
            }
        }
        mock_get_component_connections.return_value = [mock_connection]

        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils.reporting = MagicMock()

        # Act
        success, connections = nifi_utils.get_component_connections("test_processor_id", return_list=False)

        # Assert
        self.assertTrue(success)
        self.assertEqual(connections, {
            "source": {},
            "destination": {"test_connection": "test_connection_id"}
        })
        mock_get_processor.assert_called_once_with("test_processor_id")
        mock_get_component_connections.assert_called_once_with(mock_processor)
        nifi_utils.reporting.insert_step.assert_called_with(
            "Successfully retrieved component connections for: test_processor_id",
            "Successfully retrieved component connections",
            "Pass"
        )

    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils._NifiProcessorUtils__get_processor")
    def test_get_component_connections_exception(self, mock_get_processor):
        # Arrange
        mock_get_processor.side_effect = ApiException("Test exception")

        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()

        # Act
        success, connections = nifi_utils.get_component_connections("test_processor_id")

        # Assert
        self.assertFalse(success)
        self.assertEqual(connections, {"source": {}, "destination": {}})

    def test_delete_queue_data_success(self):
        self.nifi_utils = NifiProcessorUtils("http://localhost:8080")
        self.nifi_utils.apis = MagicMock()  # Mock the apis attribute
        self.nifi_utils.reporting = MagicMock()  # Mock the reporting attribute
        self.nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()  # Mock the exception handler
        # Arrange
        mock_flowfile_queues_api = MagicMock()
        mock_flowfile_queues_api.create_drop_request.return_value = "valid_drop_req_id"
        self.nifi_utils.apis.get.return_value = mock_flowfile_queues_api

        # Act
        result = self.nifi_utils.delete_queue_data("test_connection_id")

        # Assert
        self.assertTrue(result)
        mock_flowfile_queues_api.create_drop_request.assert_called_once_with("test_connection_id")
        self.nifi_utils.reporting.insert_step.assert_called_with(
            "Successfully deleted queue connection data",
            "Successfully deleted queue connection data",
            "Pass"
        )

    def test_delete_queue_data_failure(self):
        self.nifi_utils = NifiProcessorUtils("http://localhost:8080")
        self.nifi_utils.apis = MagicMock()  # Mock the apis attribute
        self.nifi_utils.reporting = MagicMock()  # Mock the reporting attribute
        self.nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()
        # Arrange
        mock_flowfile_queues_api = MagicMock()
        mock_flowfile_queues_api.create_drop_request.return_value = None
        self.nifi_utils.apis.get.return_value = mock_flowfile_queues_api

        # Act
        result = self.nifi_utils.delete_queue_data("test_connection_id")

        # Assert
        self.assertFalse(result)
        mock_flowfile_queues_api.create_drop_request.assert_called_once_with("test_connection_id")
        self.nifi_utils.reporting.insert_step.assert_called_with(
            "Failed to delete queue connection data",
            "Unable to delete queue connection data",
            "Fail"
        )

    def test_delete_queue_data_exception(self):
        self.nifi_utils = NifiProcessorUtils("http://localhost:8080")
        self.nifi_utils.apis = MagicMock()  # Mock the apis attribute
        self.nifi_utils.reporting = MagicMock()  # Mock the reporting attribute
        self.nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()
        # Arrange
        mock_flowfile_queues_api = MagicMock()
        mock_flowfile_queues_api.create_drop_request.side_effect = ApiException("Test exception")
        self.nifi_utils.apis.get.return_value = mock_flowfile_queues_api

        # Act
        result = self.nifi_utils.delete_queue_data("test_connection_id")

        # Assert
        self.assertFalse(result)
        mock_flowfile_queues_api.create_drop_request.assert_called_once_with("test_connection_id")

    @patch("time.sleep", return_value=None)  # Mock time.sleep to avoid delays
    def test_start_then_stop_processor_success(self, mock_sleep):
        self.nifi_utils = NifiProcessorUtils("http://localhost:8080")
        self.nifi_utils.change_nifi_processor_state = MagicMock()
        self.nifi_utils.reporting = MagicMock()
        self.nifi_utils._NifiProcessorUtils__get_processor = MagicMock()
        self.nifi_utils.get_key_path_value = MagicMock()
        self.nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()
        # Arrange
        self.nifi_utils._NifiProcessorUtils__get_processor.return_value = (
            True, MagicMock(to_dict=lambda: {"status": {"aggregate_snapshot": {"active_thread_count": 0}}}))
        self.nifi_utils.get_key_path_value.return_value = 0

        # Act
        result = self.nifi_utils.start_then_stop_processor("http://localhost:8080", "test_processor_id")

        # Assert
        self.assertTrue(result)
        self.nifi_utils.change_nifi_processor_state.assert_any_call("http://localhost:8080", "test_processor_id",
                                                                    "RUNNING")
        self.nifi_utils.change_nifi_processor_state.assert_any_call("http://localhost:8080", "test_processor_id",
                                                                    "STOPPED")
        self.nifi_utils.reporting.insert_step.assert_called_with(
            "Processor test_processor_id has been successfully started and stopped.",
            "Processor started and stopped successfully.",
            "Pass"
        )

    @patch("time.sleep", return_value=None)
    def test_start_then_stop_processor_invalid_wait_interval(self, mock_sleep):
        self.nifi_utils = NifiProcessorUtils("http://localhost:8080")
        self.nifi_utils.change_nifi_processor_state = MagicMock()
        self.nifi_utils.reporting = MagicMock()
        self.nifi_utils._NifiProcessorUtils__get_processor = MagicMock()
        self.nifi_utils.get_key_path_value = MagicMock()
        self.nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()
        # Act
        result = self.nifi_utils.start_then_stop_processor("http://localhost:8080", "test_processor_id",
                                                           wait_interval=0)

        # Assert
        self.assertFalse(result)
        self.nifi_utils.reporting.insert_step.assert_called_with(
            "Invalid wait interval",
            "Wait interval must be greater than 0",
            "Fail"
        )

    @patch("time.sleep", return_value=None)
    def test_start_then_stop_processor_takes_too_long(self, mock_sleep):
        self.nifi_utils = NifiProcessorUtils("http://localhost:8080")
        self.nifi_utils.change_nifi_processor_state = MagicMock()
        self.nifi_utils.reporting = MagicMock()
        self.nifi_utils._NifiProcessorUtils__get_processor = MagicMock()
        self.nifi_utils.get_key_path_value = MagicMock()
        self.nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()
        # Arrange
        self.nifi_utils._NifiProcessorUtils__get_processor.return_value = (
            True, MagicMock(to_dict=lambda: {"status": {"aggregate_snapshot": {"active_thread_count": 1}}}))
        self.nifi_utils.get_key_path_value.return_value = 1

        # Act
        result = self.nifi_utils.start_then_stop_processor("http://localhost:8080", "test_processor_id",
                                                           max_wait_time=10, wait_interval=2)

        # Assert
        self.assertFalse(result)
        self.nifi_utils.reporting.insert_step.assert_called_with(
            "Processor test_processor_id should not have active threads.",
            "Processor is taking more than 10 seconds to stop.",
            "Fail"
        )

    @patch("time.sleep", return_value=None)
    def test_start_then_stop_processor_exception(self, mock_sleep):
        self.nifi_utils = NifiProcessorUtils("http://localhost:8080")
        self.nifi_utils.change_nifi_processor_state = MagicMock()
        self.nifi_utils.reporting = MagicMock()
        self.nifi_utils._NifiProcessorUtils__get_processor = MagicMock()
        self.nifi_utils.get_key_path_value = MagicMock()
        self.nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()
        # Arrange
        self.nifi_utils.change_nifi_processor_state.side_effect = ApiException("Test exception")

        # Act
        result = self.nifi_utils.start_then_stop_processor("http://localhost:8080", "test_processor_id")

        # Assert
        self.assertFalse(result)

    def test_clear_queues_success(self):
        self.nifi_utils = NifiProcessorUtils("http://localhost:8080")
        self.nifi_utils.get_component_connections = MagicMock()
        self.nifi_utils.delete_queue_data = MagicMock()
        self.nifi_utils.reporting = MagicMock()
        self.nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()
        # Arrange
        self.nifi_utils.get_component_connections.return_value = (
            True,
            {
                "source": {"key1": ["conn1", "conn2"]},
                "destination": {"key2": ["conn3", "conn4"]}
            }
        )
        self.nifi_utils.delete_queue_data.return_value = True

        # Act
        result = self.nifi_utils.clear_queues("test_processor_id")

        # Assert
        self.assertTrue(result)
        self.nifi_utils.delete_queue_data.assert_any_call("conn1")
        self.nifi_utils.delete_queue_data.assert_any_call("conn2")
        self.nifi_utils.delete_queue_data.assert_any_call("conn3")
        self.nifi_utils.delete_queue_data.assert_any_call("conn4")
        self.nifi_utils.reporting.insert_step.assert_any_call(
            "Successfully cleared all input queues for processor ID: test_processor_id",
            "All input queues cleared.",
            "Pass"
        )
        self.nifi_utils.reporting.insert_step.assert_any_call(
            "Successfully cleared all output queues for processor ID: test_processor_id",
            "All output queues cleared.",
            "Pass"
        )

    def test_clear_queues_inbound_failure(self):
        self.nifi_utils = NifiProcessorUtils("http://localhost:8080")
        self.nifi_utils.get_component_connections = MagicMock()
        self.nifi_utils.delete_queue_data = MagicMock()
        self.nifi_utils.reporting = MagicMock()
        self.nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()
        # Arrange
        self.nifi_utils.get_component_connections.return_value = (
            True,
            {
                "source": {"key1": ["conn1", "conn2"]},
                "destination": {"key2": ["conn3", "conn4"]}
            }
        )
        self.nifi_utils.delete_queue_data.side_effect = lambda conn_id: conn_id != "conn1"

        # Act
        result = self.nifi_utils.clear_queues("test_processor_id")

        # Assert
        self.assertFalse(result)
        self.nifi_utils.reporting.insert_step.assert_called_with(
            "Failed to clear input queue",
            "Error occurred while deleting input connection: conn1",
            "Fail"
        )

    def test_clear_queues_outbound_failure(self):
        self.nifi_utils = NifiProcessorUtils("http://localhost:8080")
        self.nifi_utils.get_component_connections = MagicMock()
        self.nifi_utils.delete_queue_data = MagicMock()
        self.nifi_utils.reporting = MagicMock()
        self.nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()
        # Arrange
        self.nifi_utils.get_component_connections.return_value = (
            True,
            {
                "source": {"key1": ["conn1", "conn2"]},
                "destination": {"key2": ["conn3", "conn4"]}
            }
        )
        self.nifi_utils.delete_queue_data.side_effect = lambda conn_id: conn_id != "conn3"

        # Act
        result = self.nifi_utils.clear_queues("test_processor_id")

        # Assert
        self.assertFalse(result)
        self.nifi_utils.reporting.insert_step.assert_called_with(
            "Failed to clear output queue",
            "Error occurred while deleting output connection: conn3",
            "Fail"
        )

    def test_clear_queues_exception(self):
        self.nifi_utils = NifiProcessorUtils("http://localhost:8080")
        self.nifi_utils.get_component_connections = MagicMock()
        self.nifi_utils.delete_queue_data = MagicMock()
        self.nifi_utils.reporting = MagicMock()
        self.nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()
        # Arrange
        self.nifi_utils.get_component_connections.side_effect = ApiException("Test exception")

        # Act
        result = self.nifi_utils.clear_queues("test_processor_id")

        # Assert
        self.assertFalse(result)

    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils._NifiProcessorUtils__get_processor")
    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils.call_request")
    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils.get_key_path_value")
    def test_enable_processor_success(self, mock_get_key_path_value, mock_call_request, mock_get_processor):
        # Arrange
        mock_processor_data = MagicMock()
        mock_processor_data.revision.client_id = "test_client_id"
        mock_processor_data.revision.version = 1
        mock_get_processor.return_value = (True, mock_processor_data)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_call_request.return_value = mock_response

        mock_get_key_path_value.return_value = "RUNNING"  # Mock the expected return value

        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils._NifiProcessorUtils__nifi_token = "test_token"

        # Act
        result = nifi_utils.enable_processor("http://localhost:8080", "test_processor_id")

        # Assert
        self.assertTrue(result)
        self.assertEqual(mock_get_processor.call_count, 2)  # Assert it was called twice
        mock_get_processor.assert_has_calls([  # Verify the exact calls
            unittest.mock.call("test_processor_id"),
            unittest.mock.call("test_processor_id")
        ])
        mock_call_request.assert_called_once()
        mock_get_key_path_value.assert_called_once_with(
            json=mock_processor_data.to_dict(),
            keyPath="status/aggregate_snapshot/run_status",
            keyPathType="absolute"
        )

    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils._NifiProcessorUtils__get_processor")
    def test_enable_processor_no_token(self, mock_get_processor):
        # Arrange
        mock_processor_data = MagicMock()
        mock_processor_data.revision.client_id = "test_client_id"
        mock_processor_data.revision.version = 1
        mock_get_processor.return_value = (True, mock_processor_data)

        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils._NifiProcessorUtils__nifi_token = None  # No token set
        nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()  # Mock exception handler

        # Act
        result = nifi_utils.enable_processor("http://localhost:8080", "test_processor_id")

        # Assert
        self.assertFalse(result)
        nifi_utils._NifiProcessorUtils__obj_exception.raise_generic_exception.assert_called_once()

    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils._NifiProcessorUtils__get_processor")
    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils.call_request")
    def test_enable_processor_exception(self, mock_call_request, mock_get_processor):
        # Arrange
        mock_processor_data = MagicMock()
        mock_processor_data.revision.client_id = "test_client_id"
        mock_processor_data.revision.version = 1
        mock_get_processor.return_value = (True, mock_processor_data)

        # Simulate an exception during the API call
        mock_call_request.side_effect = ApiException("Test exception")

        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils._NifiProcessorUtils__nifi_token = "test_token"
        nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()  # Mock exception handler

        # Act
        result = nifi_utils.enable_processor("http://localhost:8080", "test_processor_id")

        # Assert
        self.assertFalse(result)  # Ensure the method returns False
        mock_get_processor.assert_called_once_with("test_processor_id")  # Verify the processor retrieval
        mock_call_request.assert_called_once()  # Verify the API call was attempted
        nifi_utils._NifiProcessorUtils__obj_exception.raise_generic_exception.assert_called_once()

    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils._NifiProcessorUtils__get_processor")
    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils.call_request")
    def test_enable_processor_exception(self, mock_call_request, mock_get_processor):
        # Arrange
        mock_processor_data = MagicMock()
        mock_processor_data.revision.client_id = "test_client_id"
        mock_processor_data.revision.version = 1
        mock_get_processor.return_value = (True, mock_processor_data)

        # Simulate an exception during the API call
        mock_call_request.side_effect = ApiException("Test exception")

        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils._NifiProcessorUtils__nifi_token = "test_token"
        nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()  # Mock exception handler

        # Act
        result = nifi_utils.enable_processor("http://localhost:8080", "test_processor_id")

        # Assert
        self.assertFalse(result)
        mock_get_processor.assert_called_once_with("test_processor_id")
        mock_call_request.assert_called_once()
        nifi_utils._NifiProcessorUtils__obj_exception.raise_generic_exception.assert_called_once()

    @patch("time.sleep", return_value=None)  # Mock time.sleep to avoid delays
    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils._NifiProcessorUtils__get_processor")
    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils.get_key_path_value")
    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils.call_request")
    def test_enable_processor_timeout(self, mock_call_request, mock_get_key_path_value, mock_get_processor, mock_sleep):
        # Arrange
        mock_processor_data = MagicMock()
        mock_processor_data.revision.client_id = "test_client_id"
        mock_processor_data.revision.version = 1
        mock_get_processor.return_value = (True, mock_processor_data)

        # Simulate the processor state not changing to "RUNNING"
        mock_get_key_path_value.return_value = "VALIDATING"

        # Mock the API call response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_call_request.return_value = mock_response

        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils._NifiProcessorUtils__nifi_token = "test_token"
        nifi_utils.reporting = MagicMock()  # Mock the reporting attribute
        nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()  # Mock exception handler

        # Act
        result = nifi_utils.enable_processor("http://localhost:8080", "test_processor_id")

        # Assert
        self.assertFalse(result)  # Ensure the method returns False
        mock_get_processor.assert_called()  # Verify the processor retrieval was attempted
        nifi_utils.reporting.insert_step.assert_called_with(
            f"Processor ID test_processor_id should get enabled.",
            f"Processor is not getting enabled after: 60 seconds.",
            "Fail",
        )

    @patch("time.sleep", return_value=None)  # Mock time.sleep to avoid delays
    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils._NifiProcessorUtils__get_processor")
    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils.call_request")
    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils.get_key_path_value")
    def test_disable_processor_success(self, mock_get_key_path_value, mock_call_request, mock_get_processor,
                                       mock_sleep):
        # Arrange
        mock_processor_data = MagicMock()
        mock_processor_data.revision.client_id = "test_client_id"
        mock_processor_data.revision.version = 1
        mock_get_processor.return_value = (True, mock_processor_data)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_call_request.return_value = mock_response

        mock_get_key_path_value.return_value = 0  # Simulate active thread count as 0

        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils._NifiProcessorUtils__nifi_token = "test_token"
        nifi_utils.reporting = MagicMock()

        # Act
        result = nifi_utils.disable_processor("http://localhost:8080", "test_processor_id")

        # Assert
        self.assertTrue(result)
        mock_get_processor.assert_called()
        mock_call_request.assert_called_once()
        nifi_utils.reporting.insert_step.assert_called_with(
            f"Processor test_processor_id has been successfully disabled.",
            "Processor has been disabled.",
            "Pass",
        )

    @patch("time.sleep", return_value=None)
    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils._NifiProcessorUtils__get_processor")
    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils.call_request")
    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils.get_key_path_value")
    def test_disable_processor_timeout(self, mock_get_key_path_value, mock_call_request, mock_get_processor,
                                       mock_sleep):
        # Arrange
        mock_processor_data = MagicMock()
        mock_processor_data.revision.client_id = "test_client_id"
        mock_processor_data.revision.version = 1
        mock_get_processor.return_value = (True, mock_processor_data)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_call_request.return_value = mock_response

        mock_get_key_path_value.return_value = 1  # Simulate active thread count not reaching 0

        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils._NifiProcessorUtils__nifi_token = "test_token"
        nifi_utils.reporting = MagicMock()

        # Act
        result = nifi_utils.disable_processor("http://localhost:8080", "test_processor_id")

        # Assert
        self.assertFalse(result)
        mock_get_processor.assert_called()
        mock_call_request.assert_called_once()
        nifi_utils.reporting.insert_step.assert_called_with(
            f"Processor test_processor_id should be disabled.",
            f"Processor is not getting disabled after 60 seconds.",
            "Fail",
        )

    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils._NifiProcessorUtils__get_processor")
    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils.call_request")
    def test_disable_processor_exception(self, mock_call_request, mock_get_processor):
        # Arrange
        mock_processor_data = MagicMock()
        mock_processor_data.revision.client_id = "test_client_id"
        mock_processor_data.revision.version = 1
        mock_get_processor.return_value = (True, mock_processor_data)

        mock_call_request.side_effect = ApiException("Test exception")

        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils._NifiProcessorUtils__nifi_token = "test_token"
        nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()

        # Act
        result = nifi_utils.disable_processor("http://localhost:8080", "test_processor_id")

        # Assert
        self.assertFalse(result)
        mock_get_processor.assert_called_once_with("test_processor_id")
        mock_call_request.assert_called_once()
        nifi_utils._NifiProcessorUtils__obj_exception.raise_generic_exception.assert_called_once()

    @patch("cafex_core.utils.apache_utils.nifi_processor_utils.NifiProcessorUtils._NifiProcessorUtils__get_processor")
    def test_disable_processor_no_token(self, mock_get_processor):
        # Arrange
        mock_processor_data = MagicMock()
        mock_processor_data.revision.client_id = "test_client_id"
        mock_processor_data.revision.version = 1
        mock_get_processor.return_value = (True, mock_processor_data)

        nifi_utils = NifiProcessorUtils("http://localhost:8080")
        nifi_utils._NifiProcessorUtils__nifi_token = None  # No token set
        nifi_utils._NifiProcessorUtils__obj_exception = MagicMock()

        # Act
        result = nifi_utils.disable_processor("http://localhost:8080", "test_processor_id")

        # Assert
        self.assertFalse(result)
        nifi_utils._NifiProcessorUtils__obj_exception.raise_generic_exception.assert_called_once()


if __name__ == '__main__':
    unittest.main()
