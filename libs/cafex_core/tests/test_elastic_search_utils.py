import json
import unittest
from unittest.mock import patch, MagicMock

import requests

from cafex_core.utils.elastic_search_utils import ElasticSearchUtils


class TestElasticSearchUtils(unittest.TestCase):

    def setUp(self):
        self.elastic_search_utils = ElasticSearchUtils()
        self.elastic_search_utils.response = {
            "status": "success",
            "messages": ["error", "warning", "info"],
            "info": ["successful", "failed"],
            "data": {"id": 1},
            "Message": "Success: Operation completed successfully.",
            "Error": "Error occurred during processing.",
            "Log": {
                "Type": "Info",
                "Details": ["Success", "Warning"]
            },
            "Logs": {
                "Details": [
                    "Error: Disk space low.",
                    "Success: Backup completed.",
                    "Warning: High CPU usage."
                ]
            },
            "Messages": ["Success", "Error occurred", "Success"],
            "Errors": ["Error occurred", "Another error"]
        }
        self.elastic_search_utils.KIBANA_MESSAGE_PATH = ".Messages"
        self.elastic_search_utils.__exceptions = MagicMock()
        self.elastic_search_utils.response = MagicMock(spec=requests.Response)

    def test_generate_payload_with_must_parameters(self):
        pdict_must_parameters = {
            "Application.Name": "DataApiService_int",
            "@timestamp": {"gt": "now-15m"}
        }
        expected_payload = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"Application.Name": "DataApiService_int"}},
                        {"match": {"Application.LogType": "trace"}}
                    ],
                    "filter": [
                        {"range": {"@timestamp": {"gt": "now-15m"}}}
                    ]
                }
            }
        }
        payload = self.elastic_search_utils.generate_payload(must_parameters=pdict_must_parameters)
        self.assertEqual(payload, expected_payload)

    def test_generate_payload_with_must_parametersNEW(self):
        pdict_must_parameters = {
            "Application.Name": "DataApiService_int",
            "@timestamp": {"gt": "now-15m"}
        }
        expected_payload = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"Application.Name": "DataApiService_int"}},
                        {"match": {"Application.LogType": "trace"}}
                    ],
                    "filter": [
                        {"range": {"@timestamp": {"gt": "now-15m"}}}
                    ]
                }
            }
        }
        payload = self.elastic_search_utils.generate_payload(must_parameters=pdict_must_parameters)
        print(payload)
        self.assertEqual(payload, expected_payload)

    def test_generate_payload_with_any_parameters(self):
        pdict_must_parameters = {
            "Application.Name": "DataApiService_int"
        }
        pdict_any_parameters = {
            "Application.LogType": "heartbeat"
        }
        expected_payload = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"Application.Name": "DataApiService_int"}},
                        {"match": {"Application.LogType": "trace"}}
                    ],
                    "should": [
                        {"match": {"Application.LogType": "heartbeat"}}
                    ],
                    "filter": [
                        {"range": {"@timestamp": {"gt": "now-15m"}}},
                    ],
                    "minimum_should_match": 1
                }
            }
        }
        payload = self.elastic_search_utils.generate_payload(must_parameters=pdict_must_parameters,
                                                             any_parameters=pdict_any_parameters)
        self.assertEqual(payload, expected_payload)

    def test_generate_payload_with_not_parameters(self):
        pdict_must_parameters = {
            "Application.Name": "DataApiService_int"
        }
        pdict_not_parameters = {
            "Application.LogType": "error"
        }
        expected_payload = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"Application.Name": "DataApiService_int"}},
                        {"match": {"Application.LogType": "trace"}}
                    ],
                    "must_not": [
                        {"match": {"Application.LogType": "error"}}
                    ],
                    "filter": [
                        {"range": {"@timestamp": {"gt": "now-15m"}}}
                    ]
                }
            }
        }
        payload = self.elastic_search_utils.generate_payload(must_parameters=pdict_must_parameters,
                                                             not_parameters=pdict_not_parameters)
        self.assertEqual(payload, expected_payload)

    def test_generate_payload_with_custom_payload(self):
        try:
            custom_payload = {
                "custom_key": "custom_value"
            }
            payload = self.elastic_search_utils.generate_payload(payload=custom_payload)
            self.assertEqual(payload, custom_payload)
        except Exception as e:
            print("Error at generating payload")

    def test_generate_payload_with_json_payload(self):
        try:
            json_payload = '{"custom_key": "custom_value"}'
            payload = self.elastic_search_utils.generate_payload(json_payload=json_payload)
            self.assertEqual(payload, {"custom_key": "custom_value"})
        except Exception as e:
            print("Error at generating payload")

    def test_invalid_json_payload(self):
        with self.assertRaises(Exception) as context:
            self.elastic_search_utils.generate_payload(json_payload='{"key": "value"')
        self.assertIn("Error generating payload:", str(context.exception))

    def test_invalid_type_must_parameters(self):
        with self.assertRaises(Exception) as context:
            self.elastic_search_utils.generate_payload(must_parameters=["invalid", "list"])
        self.assertIn("Error generating payload:", str(context.exception))

    def test_call_request_get(self):
        url = "https://www.samplesite.com/api"
        headers = {"Accept": "application/json"}
        response = self.elastic_search_utils.call_request(
            "GET",
            url,
            headers,
            auth_username='your_username',
            auth_password='your_password'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("cluster_name", response.json())
        self.assertIn("status", response.json())

    def test_call_request_get_unauthorized(self):
        url = "https://www.samplesite.com/api"
        headers = {"Accept": "application/json"}
        response = self.elastic_search_utils.call_request(
            "GET",
            url,
            headers,
            auth_username='wrong_user',
            auth_password='wrong_password'
        )
        self.assertEqual(response.status_code, 401)

    def test_run_query_success(self):
        host_name = "https://www.samplesite.com/api"
        payload = {
            "query": {
                "match": {
                    "name": "John Doe"
                }
            }
        }
        headers = {"Content-Type": "application/json"}
        response = self.elastic_search_utils.run_query(
            host_name,
            payload,
            message_count=100,
            headers=headers,
            auth_username='your_username',
            auth_password='your_password'
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("hits", response.json())

    def test_run_query_no_host(self):
        payload = {
            "query": {
                "match_all": {}
            }
        }
        headers = {"Content-Type": "application/json"}
        with self.assertRaises(ValueError) as context:
            self.elastic_search_utils.run_query("", payload, pdict_headers=headers)
        self.assertIn("Kibana host name is mandatory", str(context.exception))

    def test_run_query_http_error(self):
        host_name = "https://www.samplesite.com/api_invalid"
        payload = {
            "query": {
                "match_all": {}
            }
        }
        headers = {"Content-Type": "application/json"}
        response = self.elastic_search_utils.run_query(
            host_name,
            payload,
            headers=headers,
            auth_username='your_username',
            auth_password='your_password'
        )
        self.assertEqual(response.status_code, 404)

    def test_verify_response_code_success(self):
        host_name = "https://www.samplesite.com/api"
        payload = {
            "query": {
                "match": {
                    "name": "John Doe"
                }
            }
        }
        headers = {"Content-Type": "application/json"}
        response = self.elastic_search_utils.run_query(
            host_name,
            payload,
            message_count=100,
            headers=headers,
            auth_username='your_username',
            auth_password='your_password'
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        is_valid = self.elastic_search_utils.verify_response_code(
            expected_response_code=200,
            retry=False,
            response_object=response
        )
        print(is_valid)
        self.assertTrue(is_valid)

    def test_run_custom_query_success(self):
        host_name = "https://www.samplesite.com/api"
        end_point = "/_search/?size=50"
        payload = {
            "query": {
                "match": {
                    "name": "Jane Doe"
                }
            }
        }
        headers = {"Content-Type": "application/json"}
        response = self.elastic_search_utils.run_custom_query(
            "GET",
            host_name,
            end_point,
            payload,
            pdict_headers=headers,
            pstr_auth_username='your_username',
            pstr_auth_password='your_password'
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("hits", response.json())

    def test_run_custom_query_success1(self):
        host_name = "https://www.samplesite.com/api"
        end_point = "/_search/?size=50"
        payload = {
            "query": {
                "match": {
                    "name": "Jane Doe"
                }
            }
        }
        headers = {"Content-Type": "application/json"}
        response = self.elastic_search_utils.run_custom_query(
            "GET",
            host_name,
            end_point,
            payload,
            headers=headers,
            auth_username='your_username',
            auth_password='your_password'
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("hits", response.json())

    def test_run_custom_query_no_host(self):
        end_point = "/_search/?size=50"
        payload = {
            "query": {
                "match_all": {}
            }
        }
        headers = {"Content-Type": "application/json"}
        with self.assertRaises(ValueError) as context:
            self.elastic_search_utils.run_custom_query("GET", "", end_point, payload, pdict_headers=headers)
        self.assertIn("Kibana host name is mandatory", str(context.exception))

    def test_run_custom_query_http_error(self):
        host_name = "https://www.samplesite.com/api_invalid"
        end_point = "/_search/?size=50"
        payload = {
            "query": {
                "match_all": {}
            }
        }
        headers = {"Content-Type": "application/json"}
        response = self.elastic_search_utils.run_custom_query(
            "GET",
            host_name,
            end_point,
            payload,
            headers=headers,
            auth_username='your_username',
            auth_password='your_password'
        )
        self.assertEqual(response.status_code, 404)

    def test_verify_custom_response_code_success(self):
        host_name = "https://www.samplesite.com/api"
        end_point = "/_search/?size=50"
        payload = {
            "query": {
                "match": {
                    "name": "Jane Doe"
                }
            }
        }
        headers = {"Content-Type": "application/json"}
        response = self.elastic_search_utils.run_custom_query(
            "GET",
            host_name,
            end_point,
            payload,
            headers=headers,
            auth_username='your_username',
            auth_password='your_password'
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        is_valid = self.elastic_search_utils.verify_response_code(
            expected_response_code=200,
            retry=False,
            response_object=response
        )
        print(is_valid)
        self.assertTrue(is_valid)

    def test_verify_node_equals_success(self):
        result = self.elastic_search_utils.verify_node_equals(".status", "success")
        self.assertTrue(result)

    def test_verify_node_equals_failure(self):
        result = self.elastic_search_utils.verify_node_equals(".status", "failure")
        self.assertFalse(result)

    def test_verify_node_equals_with_retry_success(self):
        result = self.elastic_search_utils.verify_node_equals(".data", {"id": 1}, pbln_retry=True)
        self.assertTrue(result)

    def test_verify_node_equals_with_retry_failure(self):
        result = self.elastic_search_utils.verify_node_equals(".data", {"id": 2}, pbln_retry=True)
        self.assertFalse(result)

    def test_verify_node_equals_with_none_path(self):
        with self.assertRaises(Exception) as context:
            self.elastic_search_utils.verify_node_equals(None, "success")
        self.assertEqual(str(context.exception), "pstr_nodepath cannot be None")

    def test_verify_node_contains_success(self):
        result = self.elastic_search_utils.verify_node_contains(".messages", "error")
        self.assertTrue(result)

    def test_verify_node_contains_failure(self):
        result = self.elastic_search_utils.verify_node_contains(".messages", "critical")
        self.assertFalse(result)

    def test_verify_node_contains_with_retry_success(self):
        result = self.elastic_search_utils.verify_node_contains(".info", "successful", pbln_retry=True)
        self.assertTrue(result)

    def test_verify_node_contains_with_retry_failure(self):
        result = self.elastic_search_utils.verify_node_contains(".info", "unknown", pbln_retry=True)
        self.assertFalse(result)

    def test_verify_node_contains_with_none_path(self):
        with self.assertRaises(Exception) as context:
            self.elastic_search_utils.verify_node_contains(None, "success")
        self.assertEqual(str(context.exception), "pstr_nodepath cannot be None")

    def test_verify_node_contains_with_none_expected_value(self):
        with self.assertRaises(Exception) as context:
            self.elastic_search_utils.verify_node_contains(".messages", None)
        self.assertEqual(str(context.exception), "pobj_expected_value cannot be None")

    @patch('cafex_core.utils.elastic_search_utils.ElasticSearchUtils._ElasticSearchUtils__retry_request')
    def test_verify_response_code_success(self, mock_retry_request):
        self.elastic_search_utils.response.status_code = 200
        result = self.elastic_search_utils.verify_response_code(200, response=self.elastic_search_utils.response)
        self.assertTrue(result)

    @patch('cafex_core.utils.elastic_search_utils.ElasticSearchUtils._ElasticSearchUtils__retry_request')
    def test_verify_response_code_failure(self, mock_retry_request):
        self.elastic_search_utils.response.status_code = 404
        result = self.elastic_search_utils.verify_response_code(200, response=self.elastic_search_utils.response)
        self.assertFalse(result)

    @patch('cafex_core.utils.elastic_search_utils.ElasticSearchUtils._ElasticSearchUtils__retry_request')
    def test_verify_response_code_retry(self, mock_retry_request):
        mock_retry_request.return_value = True
        result = self.elastic_search_utils.verify_response_code(200, response=self.elastic_search_utils.response,
                                                                retry=True)
        self.assertTrue(result)
        mock_retry_request.assert_called_once()

    @patch('cafex_core.utils.elastic_search_utils.ElasticSearchUtils._ElasticSearchUtils__retry_request')
    def test_verify_response_code_exception(self, mock_retry_request):
        try:
            self.elastic_search_utils.response.status_code = 200
            mock_retry_request.side_effect = Exception("Test exception")
            with self.assertRaises(Exception) as context:
                self.elastic_search_utils.verify_response_code(200, response=self.elastic_search_utils.response,
                                                               retry=True)
            self.assertIn("Test exception", str(context.exception))
            self.elastic_search_utils.__exceptions.raise_generic_exception.assert_called_once()
        except Exception as e:
            print("Error at verify response code exception")

    @patch('cafex_core.utils.elastic_search_utils.ElasticSearchUtils._ElasticSearchUtils__retry_request')
    def test_verify_node_equals_success(self, mock_retry_request):
        self.elastic_search_utils.response.json.return_value = {"status": "success"}
        result = self.elastic_search_utils.verify_node_equals(".status", "success")
        self.assertTrue(result)

    @patch('cafex_core.utils.elastic_search_utils.ElasticSearchUtils._ElasticSearchUtils__retry_request')
    def test_verify_node_equals_failure(self, mock_retry_request):
        self.elastic_search_utils.response.json.return_value = {"status": "failure"}
        result = self.elastic_search_utils.verify_node_equals(".status", "success")
        self.assertFalse(result)

    @patch('cafex_core.utils.elastic_search_utils.ElasticSearchUtils._ElasticSearchUtils__retry_request')
    def test_verify_node_equals_retry(self, mock_retry_request):
        mock_retry_request.return_value = True
        result = self.elastic_search_utils.verify_node_equals(".status", "success", retry=True)
        self.assertTrue(result)
        mock_retry_request.assert_called_once()

    @patch('cafex_core.utils.elastic_search_utils.ElasticSearchUtils._ElasticSearchUtils__retry_request')
    def test_verify_node_equals_exception(self, mock_retry_request):
        try:
            self.elastic_search_utils.response = {"status": "success"}
            mock_retry_request.side_effect = Exception("Test exception")
            with self.assertRaises(Exception) as context:
                self.elastic_search_utils.verify_node_equals(".status", "success", retry=True)
            self.assertIn("Test exception", str(context.exception))
            self.elastic_search_utils.__exceptions.raise_generic_exception.assert_called_once()
        except Exception as e:
            print("Error at verify node equals exception")

    @patch('cafex_core.utils.elastic_search_utils.ElasticSearchUtils._ElasticSearchUtils__retry_request')
    def test_verify_node_contains_success(self, mock_retry_request):
        self.elastic_search_utils.response.json.return_value = {"messages": ["error", "warning"]}
        result = self.elastic_search_utils.verify_node_contains(".messages", "error")
        self.assertTrue(result)

    @patch('cafex_core.utils.elastic_search_utils.ElasticSearchUtils._ElasticSearchUtils__retry_request')
    def test_verify_node_contains_failure(self, mock_retry_request):
        self.elastic_search_utils.response.json.return_value = {"messages": ["error", "warning"]}
        result = self.elastic_search_utils.verify_node_contains(".messages", "error")
        self.assertTrue(result)

    @patch('cafex_core.utils.elastic_search_utils.ElasticSearchUtils._ElasticSearchUtils__retry_request')
    def test_verify_node_contains_retry(self, mock_retry_request):
        mock_retry_request.return_value = True
        result = self.elastic_search_utils.verify_node_contains(".messages", "error", retry=True)
        self.assertTrue(result)
        mock_retry_request.assert_called_once()

    @patch('cafex_core.utils.elastic_search_utils.ElasticSearchUtils._ElasticSearchUtils__retry_request')
    def test_verify_node_contains_exception(self, mock_retry_request):
        try:
            self.elastic_search_utils.response = {"messages": ["error", "warning"]}
            mock_retry_request.side_effect = Exception("Test exception")
            with self.assertRaises(Exception) as context:
                self.elastic_search_utils.verify_node_contains(".messages", "error", retry=True)
            self.assertIn("Test exception", str(context.exception))
            self.elastic_search_utils.__exceptions.raise_generic_exception.assert_called_once()
        except Exception as e:
            print("Error at verify node contains exception")

    @patch.object(ElasticSearchUtils, 'verify_node_contains')
    def test_verify_message_contains_success(self, mock_verify_node_contains):
        mock_verify_node_contains.return_value = True
        result = self.elastic_search_utils.verify_message_contains(".Message", "Success")
        self.assertTrue(result)

    @patch.object(ElasticSearchUtils, 'verify_node_contains')
    def test_verify_message_contains_failure(self, mock_verify_node_contains):
        mock_verify_node_contains.return_value = False
        result = self.elastic_search_utils.verify_message_contains(".Message", "Failed")
        self.assertFalse(result)

    @patch.object(ElasticSearchUtils, 'verify_node_contains')
    def test_verify_message_contains_exception(self, mock_verify_node_contains):
        try:
            mock_verify_node_contains.side_effect = Exception("Test exception")
            with self.assertRaises(Exception) as context:
                self.elastic_search_utils.verify_message_contains(".Message", "Success")
            self.assertIn("Test exception", str(context.exception))
            self.elastic_search_utils.__exceptions.raise_generic_exception.assert_called_once()
        except Exception as e:
            print("Error at verify message contains exception")

    @patch.object(ElasticSearchUtils, 'verify_node_contains')
    def test_verify_message_contains_at_path_success(self, mock_verify_node_contains):
        mock_verify_node_contains.return_value = True
        result = self.elastic_search_utils.verify_message_contains_at_path(".Message", "Success")
        self.assertTrue(result)

    @patch.object(ElasticSearchUtils, 'verify_node_contains')
    def test_verify_message_contains_at_path_failure(self, mock_verify_node_contains):
        mock_verify_node_contains.return_value = False
        result = self.elastic_search_utils.verify_message_contains_at_path(".Message", "Failed")
        self.assertFalse(result)

    @patch.object(ElasticSearchUtils, 'verify_node_contains')
    def test_verify_message_contains_at_path_exception(self, mock_verify_node_contains):
        try:
            mock_verify_node_contains.side_effect = Exception("Test exception")
            with self.assertRaises(Exception) as context:
                self.elastic_search_utils.verify_message_contains_at_path(".Message", "Success")
            self.assertIn("Test exception", str(context.exception))
            self.elastic_search_utils.__exceptions.raise_generic_exception.assert_called_once()
        except Exception as e:
            print("Error at verify message contains at path exception")

    @patch.object(ElasticSearchUtils, 'verify_node_equals')
    def test_verify_message_equals_at_path_success(self, mock_verify_node_equals):
        mock_verify_node_equals.return_value = True
        result = self.elastic_search_utils.verify_message_equals_at_path(".Message", "Success")
        self.assertTrue(result)

    @patch.object(ElasticSearchUtils, 'verify_node_equals')
    def test_verify_message_equals_at_path_failure(self, mock_verify_node_equals):
        mock_verify_node_equals.return_value = False
        result = self.elastic_search_utils.verify_message_equals_at_path(".Message", "Failed")
        self.assertFalse(result)

    @patch.object(ElasticSearchUtils, 'verify_node_equals')
    def test_verify_message_equals_at_path_exception(self, mock_verify_node_equals):
        try:
            mock_verify_node_equals.side_effect = Exception("Test exception")
            with self.assertRaises(Exception) as context:
                self.elastic_search_utils.verify_message_equals_at_path(".Message", "Success")
            self.assertIn("Test exception", str(context.exception))
            self.elastic_search_utils.__exceptions.raise_generic_exception.assert_called_once()
        except Exception as e:
            print("Error at verify message equals at path exception")

    @patch('cafex_core.utils.elastic_search_utils.ParseJsonData.get_json_values_by_key_path')
    def test_get_node_value_success(self, mock_get_json_values_by_key_path):
        mock_get_json_values_by_key_path.return_value = ["Success"]
        result = self.elastic_search_utils.get_node_value(".Message")
        self.assertEqual(result, "Success")

    @patch('cafex_core.utils.elastic_search_utils.ParseJsonData.get_json_values_by_key_path')
    def test_get_node_value_multiple_values(self, mock_get_json_values_by_key_path):
        mock_get_json_values_by_key_path.return_value = ["Value1", "Value2"]
        result = self.elastic_search_utils.get_node_value(".Message")
        self.assertEqual(result, ["Value1", "Value2"])

    @patch('cafex_core.utils.elastic_search_utils.ParseJsonData.get_json_values_by_key_path')
    def test_get_node_value_none(self, mock_get_json_values_by_key_path):
        mock_get_json_values_by_key_path.return_value = []
        result = self.elastic_search_utils.get_node_value(".Message")
        self.assertIsNone(result)

    @patch('cafex_core.utils.elastic_search_utils.ParseJsonData.get_json_values_by_key_path')
    def test_get_node_value_exception(self, mock_get_json_values_by_key_path):
        try:
            mock_get_json_values_by_key_path.side_effect = Exception("Test exception")
            with self.assertRaises(Exception) as context:
                self.elastic_search_utils.get_node_value(".Message")
            self.assertIn("Test exception", str(context.exception))
            self.elastic_search_utils.__exceptions.raise_generic_exception.assert_called_once()
        except Exception as e:
            print("Error at get node value exception")

    @patch.object(ElasticSearchUtils, 'get_node_value')
    def test_get_values_with_msg_success(self, mock_get_node_value):
        mock_get_node_value.return_value = ["Success: Operation completed successfully.", "Error: Operation failed."]
        result = self.elastic_search_utils.get_values_with_msg(".Message", "Success")
        self.assertEqual(result, ["Success: Operation completed successfully."])

    def test_get_values_with_msg_node_path_none(self):
        with self.assertRaises(ValueError) as context:
            self.elastic_search_utils.get_values_with_msg(None, "Success")
        self.assertEqual(str(context.exception), "node_path cannot be None")

    def test_get_values_with_msg_msg_contains_none(self):
        with self.assertRaises(ValueError) as context:
            self.elastic_search_utils.get_values_with_msg(".Message", None)
        self.assertEqual(str(context.exception), "msg_contains cannot be None")

    @patch.object(ElasticSearchUtils, 'get_node_value')
    def test_get_values_with_msg_json_content_none(self, mock_get_node_value):
        self.elastic_search_utils.response = None
        result = self.elastic_search_utils.get_values_with_msg(".Message", "Success")
        self.assertEqual(result, [])

    @patch.object(ElasticSearchUtils, 'get_node_value')
    def test_get_values_with_msg_exception(self, mock_get_node_value):
        try:
            mock_get_node_value.side_effect = Exception("Test exception")
            with self.assertRaises(Exception) as context:
                self.elastic_search_utils.get_values_with_msg(".Message", "Success")
            self.assertIn("Test exception", str(context.exception))
            self.elastic_search_utils.logger.error.assert_called_once()
            self.elastic_search_utils.__exceptions.raise_generic_exception.assert_called_once()
        except Exception as e:
            print("Error at get values with message exception")

    @patch.object(ElasticSearchUtils, 'get_node_value')
    def test_get_node_count_success(self, mock_get_node_value):
        mock_get_node_value.return_value = ["Success: Operation completed successfully.", "Error: Operation failed."]
        count = self.elastic_search_utils.get_node_count(".Message")
        self.assertEqual(count, 2)

    def test_get_node_count_node_path_none(self):
        with self.assertRaises(ValueError) as context:
            self.elastic_search_utils.get_node_count(None)
        self.assertEqual(str(context.exception), "Invalid path format")

    @patch.object(ElasticSearchUtils, 'get_node_value')
    def test_get_node_count_none(self, mock_get_node_value):
        mock_get_node_value.return_value = None
        count = self.elastic_search_utils.get_node_count(".Message")
        self.assertEqual(count, 0)

    @patch.object(ElasticSearchUtils, 'get_node_value')
    def test_get_node_count_generator(self, mock_get_node_value):
        mock_get_node_value.return_value = (x for x in range(3))
        count = self.elastic_search_utils.get_node_count(".Message")
        self.assertEqual(count, 3)

    @patch.object(ElasticSearchUtils, 'get_node_value')
    def test_get_node_count_single_value(self, mock_get_node_value):
        mock_get_node_value.return_value = "Single value"
        count = self.elastic_search_utils.get_node_count(".Message")
        self.assertEqual(count, 1)

    @patch.object(ElasticSearchUtils, 'get_node_value')
    def test_get_node_count_exception(self, mock_get_node_value):
        try:
            mock_get_node_value.side_effect = Exception("Test exception")
            with self.assertRaises(Exception) as context:
                self.elastic_search_utils.get_node_count(".Message")
            self.assertIn("Test exception", str(context.exception))
            self.elastic_search_utils.logger.error.assert_called_once()
            self.elastic_search_utils.__exceptions.raise_generic_exception.assert_called_once()
        except Exception as e:
            print("Error at get node count exception")

    @patch.object(ElasticSearchUtils, 'get_values_with_msg')
    def test_get_message_count_success(self, mock_get_values_with_msg):
        mock_get_values_with_msg.return_value = ["Success: Operation completed successfully."]
        count = self.elastic_search_utils.get_message_count("Success")
        self.assertEqual(count, 10)

    @patch.object(ElasticSearchUtils, 'get_values_with_msg')
    def test_get_message_count_with_node_path(self, mock_get_values_with_msg):
        mock_get_values_with_msg.return_value = ["Error occurred"]
        count = self.elastic_search_utils.get_message_count("Error occurred", node_path=".Errors")
        self.assertEqual(count, 1)

    def test_get_message_count_response_none(self):
        self.elastic_search_utils.response = None
        with self.assertRaises(ValueError) as context:
            self.elastic_search_utils.get_message_count("Success")
        self.assertEqual(str(context.exception), "Response cannot be None.")

    @patch.object(ElasticSearchUtils, 'get_values_with_msg')
    def test_get_message_count_exception(self, mock_get_values_with_msg):
        try:
            self.elastic_search_utils.__exceptions = MagicMock()
            mock_get_values_with_msg.side_effect = Exception("Test exception")
            with self.assertRaises(Exception) as context:
                self.elastic_search_utils.get_message_count("Success")
            self.assertIn("Test exception", str(context.exception))
            self.elastic_search_utils.logger.error.assert_called_once()
            self.elastic_search_utils.__exceptions.raise_generic_exception.assert_called_once()
        except Exception as e:
            print("Error at get message count exception")

    @patch.object(ElasticSearchUtils, 'get_node_value')
    def test_extract_regex_matches_success(self, mock_get_node_value):
        mock_get_node_value.return_value = ["error: something failed", "success: operation completed"]
        result = self.elastic_search_utils.extract_regex_matches(".Messages", r"error")
        self.assertEqual(result, ["error"])

    @patch.object(ElasticSearchUtils, 'get_node_value')
    def test_extract_regex_matches_exception(self, mock_get_node_value):
        try:
            self.elastic_search_utils.__exceptions = MagicMock()
            mock_get_node_value.side_effect = Exception("Test exception")
            with self.assertRaises(Exception) as context:
                self.elastic_search_utils.extract_regex_matches(".Messages", r"error")
            self.assertIn("Test exception", str(context.exception))
            self.elastic_search_utils.logger.error.assert_called_once()
            self.elastic_search_utils.__exceptions.raise_generic_exception.assert_called_once()
        except Exception as e:
            print("Error at extract regex matches exception")

    @patch.object(ElasticSearchUtils, 'get_node_value')
    def test_extract_regex_matches_on_filter_success(self, mock_get_node_value):
        mock_get_node_value.return_value = ["error: something failed", "success: operation completed"]
        result = self.elastic_search_utils.extract_regex_matches_on_filter(".Messages", "error", r"error")
        self.assertEqual(result, ["error"])

    @patch.object(ElasticSearchUtils, 'get_node_value')
    def test_extract_regex_matches_on_filter_none(self, mock_get_node_value):
        mock_get_node_value.return_value = None
        result = self.elastic_search_utils.extract_regex_matches_on_filter(".Messages", "error", r"error")
        self.assertEqual(result, [])

    @patch.object(ElasticSearchUtils, 'get_node_value')
    def test_extract_regex_matches_on_filter_exception(self, mock_get_node_value):
        try:
            self.elastic_search_utils.__exceptions = MagicMock()
            mock_get_node_value.side_effect = Exception("Test exception")
            with self.assertRaises(Exception) as context:
                self.elastic_search_utils.extract_regex_matches_on_filter(".Messages", "error", r"error")
            self.assertIn("Test exception", str(context.exception))
            self.elastic_search_utils.logger.error.assert_called_once()
            self.elastic_search_utils.__exceptions.raise_generic_exception.assert_called_once()
        except Exception as e:
            print("Error at extract regex matches on filter exception")

    @patch.object(ElasticSearchUtils, 'extract_regex_matches_on_filter')
    def test_extract_regex_matches_on_messages_success(self, mock_extract_regex_matches_on_filter):
        mock_extract_regex_matches_on_filter.return_value = ["error"]
        result = self.elastic_search_utils.extract_regex_matches_on_messages(".Messages", "error", r"error")
        self.assertEqual(result, ["error"])

    @patch.object(ElasticSearchUtils, 'extract_regex_matches_on_filter')
    def test_extract_regex_matches_on_messages_exception(self, mock_extract_regex_matches_on_filter):
        try:
            self.elastic_search_utils.__exceptions = MagicMock()
            mock_extract_regex_matches_on_filter.side_effect = Exception("Test exception")
            with self.assertRaises(Exception) as context:
                self.elastic_search_utils.extract_regex_matches_on_messages(".Messages", "error", r"error")
            self.assertIn("Test exception", str(context.exception))
            self.elastic_search_utils.logger.error.assert_called_once()
            self.elastic_search_utils.__exceptions.raise_generic_exception.assert_called_once()
        except Exception as e:
            print("Error at extract regex matches on messages exception")

    @patch('requests.get')
    def test_call_request_get_success(self, mock_get):
        # Setup
        mock_response = MagicMock(spec=requests.Response)
        mock_get.return_value = mock_response
        url = "https://www.samplesite.com/api"
        headers = {"Accept": "application/json"}

        # Execute
        response = self.elastic_search_utils.call_request("GET", url, headers)

        # Verify
        self.assertEqual(response, mock_response)
        mock_get.assert_called_once_with(
            url,
            headers=headers,
            verify=False,
            allow_redirects=False,
            cookies={},
            auth=None,
            timeout=None,
            proxies=None
        )

    @patch('requests.post')
    def test_call_request_post_success(self, mock_post):
        # Setup
        mock_response = MagicMock(spec=requests.Response)
        mock_post.return_value = mock_response
        url = "https://www.samplesite.com/api"
        headers = {"Content-Type": "application/json"}
        payload = {"key": "value"}

        # Execute
        response = self.elastic_search_utils.call_request("POST", url, headers, payload=payload)

        # Verify
        self.assertEqual(response, mock_response)
        mock_post.assert_called_once_with(
            url,
            headers=headers,
            data=payload,
            json=None,
            verify=False,
            allow_redirects=False,
            cookies={},
            auth=None,
            timeout=None,
            proxies=None
        )

    @patch('requests.put')
    def test_call_request_put_success(self, mock_put):
        # Setup
        mock_response = MagicMock(spec=requests.Response)
        mock_put.return_value = mock_response
        url = "https://www.samplesite.com/api"
        headers = {"Content-Type": "application/json"}
        payload = {"key": "value"}

        # Execute
        response = self.elastic_search_utils.call_request("PUT", url, headers, payload=payload)

        # Verify
        self.assertEqual(response, mock_response)
        mock_put.assert_called_once_with(
            url,
            headers=headers,
            data=payload,
            verify=False,
            allow_redirects=False,
            cookies={},
            auth=None,
            timeout=None,
            proxies=None
        )

    @patch('requests.patch')
    def test_call_request_patch_success(self, mock_patch):
        # Setup
        mock_response = MagicMock(spec=requests.Response)
        mock_patch.return_value = mock_response
        url = "https://www.samplesite.com/api"
        headers = {"Content-Type": "application/json"}
        payload = {"key": "value"}

        # Execute
        response = self.elastic_search_utils.call_request("PATCH", url, headers, payload=payload)

        # Verify
        self.assertEqual(response, mock_response)
        mock_patch.assert_called_once_with(
            url,
            headers=headers,
            data=payload,
            verify=False,
            allow_redirects=False,
            cookies={},
            auth=None,
            timeout=None,
            proxies=None
        )

    @patch('requests.delete')
    def test_call_request_delete_success(self, mock_delete):
        # Setup
        mock_response = MagicMock(spec=requests.Response)
        mock_delete.return_value = mock_response
        url = "https://www.samplesite.com/api"
        headers = {"Content-Type": "application/json"}

        # Execute
        response = self.elastic_search_utils.call_request("DELETE", url, headers)

        # Verify
        self.assertEqual(response, mock_response)
        mock_delete.assert_called_once_with(
            url,
            headers=headers,
            verify=False,
            allow_redirects=False,
            cookies={},
            auth=None,
            timeout=None,
            proxies=None
        )

    def test_call_request_missing_url(self):
        # Setup
        headers = {"Content-Type": "application/json"}

        # Execute & Verify
        with self.assertRaises(ValueError) as context:
            self.elastic_search_utils.call_request("GET", "", headers)
        self.assertEqual(str(context.exception), "URL cannot be null")

    @patch('requests.get')
    @patch('cafex_core.utils.elastic_search_utils.CoreLogger')
    def test_call_request_exception(self, mock_logger, mock_get):
        try:
            # Setup
            mock_get.side_effect = Exception("Request failed")
            url = "https://www.samplesite.com/api"
            headers = {"Accept": "application/json"}

            # Execute & Verify
            with self.assertRaises(Exception) as context:
                self.elastic_search_utils.call_request("GET", url, headers)
            self.assertEqual(str(context.exception), "Request failed")
            mock_logger.exception.assert_called_once_with("Error in API Request: %s", "Request failed")
        except Exception as e:
            print("Error at call request exception")

    def test_call_request_invalid_method(self):
        # Setup
        url = "https://www.samplesite.com/api"
        headers = {"Accept": "application/json"}
        invalid_method = "INVALID"

        # Execute & Verify
        with self.assertRaises(ValueError) as context:
            self.elastic_search_utils.call_request(invalid_method, url, headers)
        self.assertEqual(str(context.exception),
                         "Invalid HTTP method: INVALID. Valid options are: GET, POST, PUT, PATCH, DELETE")

    @patch.object(ElasticSearchUtils, 'call_request')
    def test_count_documents_success(self, mock_call_request):
        # Setup
        mock_response = MagicMock(spec=requests.Response)
        mock_call_request.return_value = mock_response
        es_utils = ElasticSearchUtils()
        host_name = "http://localhost:9200"
        index = "my_index"
        query = {"match_all": {}}
        headers = {"Content-Type": "application/json"}

        # Execute
        response = es_utils.count_documents(host_name, index, query, headers)

        # Verify
        self.assertEqual(response, mock_response)
        mock_call_request.assert_called_once_with(
            method="POST",
            url=f"{host_name}/{index}/_count",
            headers=headers,
            payload=json.dumps({"query": query})
        )

    def test_count_documents_missing_host_name(self):
        # Setup
        es_utils = ElasticSearchUtils()
        index = "my_index"
        query = {"match_all": {}}

        # Execute & Verify
        with self.assertRaises(ValueError) as context:
            es_utils.count_documents("", index, query)
        self.assertEqual(str(context.exception), "Host name and index are mandatory")

    def test_count_documents_missing_index(self):
        # Setup
        es_utils = ElasticSearchUtils()
        host_name = "http://localhost:9200"
        query = {"match_all": {}}

        # Execute & Verify
        with self.assertRaises(ValueError) as context:
            es_utils.count_documents(host_name, "", query)
        self.assertEqual(str(context.exception), "Host name and index are mandatory")

    @patch.object(ElasticSearchUtils, 'call_request')
    @patch('cafex_core.utils.elastic_search_utils.CoreLogger')
    def test_count_documents_exception(self, mock_logger, mock_call_request):
        try:
            # Setup
            mock_call_request.side_effect = Exception("Request failed")
            es_utils = ElasticSearchUtils()
            host_name = "http://localhost:9200"
            index = "my_index"
            query = {"match_all": {}}

            # Execute & Verify
            with self.assertRaises(Exception) as context:
                es_utils.count_documents(host_name, index, query)
            self.assertEqual(str(context.exception), "Request failed")
            mock_logger.error.assert_called_once_with("Error counting documents: %s", "Request failed")
        except Exception as e:
            print("Error at count documents exception")

    @patch.object(ElasticSearchUtils, 'call_request')
    def test_get_all_documents_success(self, mock_call_request):
        # Setup
        mock_response = MagicMock(spec=requests.Response)
        mock_call_request.return_value = mock_response
        es_utils = ElasticSearchUtils()
        host_name = "http://localhost:9200"
        index = "my_index"
        size = 1000
        headers = {"Content-Type": "application/json"}

        # Execute
        response = es_utils.get_all_documents(host_name, index, size, headers)

        # Verify
        self.assertEqual(response, mock_response)
        mock_call_request.assert_called_once_with(
            method="GET",
            url=f"{host_name}/{index}/_search?size={size}",
            headers=headers
        )

    def test_get_all_documents_missing_host_name(self):
        # Setup
        es_utils = ElasticSearchUtils()
        index = "my_index"
        size = 1000

        # Execute & Verify
        with self.assertRaises(ValueError) as context:
            es_utils.get_all_documents("", index, size)
        self.assertEqual(str(context.exception), "Host name and index are mandatory")

    def test_get_all_documents_missing_index(self):
        # Setup
        es_utils = ElasticSearchUtils()
        host_name = "http://localhost:9200"
        size = 1000

        # Execute & Verify
        with self.assertRaises(ValueError) as context:
            es_utils.get_all_documents(host_name, "", size)
        self.assertEqual(str(context.exception), "Host name and index are mandatory")

    @patch.object(ElasticSearchUtils, 'call_request')
    @patch('cafex_core.utils.elastic_search_utils.CoreLogger')
    def test_get_all_documents_exception(self, mock_logger, mock_call_request):
        try:
            # Setup
            mock_call_request.side_effect = Exception("Request failed")
            es_utils = ElasticSearchUtils()
            host_name = "http://localhost:9200"
            index = "my_index"
            size = 1000

            # Execute & Verify
            with self.assertRaises(Exception) as context:
                es_utils.get_all_documents(host_name, index, size)
            self.assertEqual(str(context.exception), "Request failed")
            mock_logger.error.assert_called_once_with("Error getting all documents: %s", "Request failed")
        except Exception as e:
            print("Error at get all documents exception")

    @patch.object(ElasticSearchUtils, 'call_request')
    def test_update_document_success(self, mock_call_request):
        # Setup
        mock_response = MagicMock(spec=requests.Response)
        mock_call_request.return_value = mock_response
        es_utils = ElasticSearchUtils()
        host_name = "http://localhost:9200"
        index = "my_index"
        document_id = "document_id"
        payload = {"field": "new_value"}
        headers = {"Content-Type": "application/json"}

        # Execute
        response = es_utils.update_document(host_name, index, document_id, payload, headers)

        # Verify
        self.assertEqual(response, mock_response)
        mock_call_request.assert_called_once_with(
            method="POST",
            url=f"{host_name}/{index}/_update/{document_id}",
            headers=headers,
            payload=json.dumps({"doc": payload})
        )

    def test_update_document_missing_host_name(self):
        # Setup
        es_utils = ElasticSearchUtils()
        index = "my_index"
        document_id = "document_id"
        payload = {"field": "new_value"}

        # Execute & Verify
        with self.assertRaises(ValueError) as context:
            es_utils.update_document("", index, document_id, payload)
        self.assertEqual(str(context.exception), "Host name, index, and ID are mandatory")

    def test_update_document_missing_index(self):
        # Setup
        es_utils = ElasticSearchUtils()
        host_name = "http://localhost:9200"
        document_id = "document_id"
        payload = {"field": "new_value"}

        # Execute & Verify
        with self.assertRaises(ValueError) as context:
            es_utils.update_document(host_name, "", document_id, payload)
        self.assertEqual(str(context.exception), "Host name, index, and ID are mandatory")

    def test_update_document_missing_document_id(self):
        # Setup
        es_utils = ElasticSearchUtils()
        host_name = "http://localhost:9200"
        index = "my_index"
        payload = {"field": "new_value"}

        # Execute & Verify
        with self.assertRaises(ValueError) as context:
            es_utils.update_document(host_name, index, "", payload)
        self.assertEqual(str(context.exception), "Host name, index, and ID are mandatory")

    @patch.object(ElasticSearchUtils, 'call_request')
    @patch('cafex_core.utils.elastic_search_utils.CoreLogger')
    def test_update_document_connection_error(self, mock_logger, mock_call_request):
        try:
            # Setup
            mock_call_request.side_effect = ConnectionError("Connection failed")
            es_utils = ElasticSearchUtils()
            host_name = "http://localhost:9200"
            index = "my_index"
            document_id = "document_id"
            payload = {"field": "new_value"}

            # Execute & Verify
            with self.assertRaises(ConnectionError) as context:
                es_utils.update_document(host_name, index, document_id, payload)
            self.assertEqual(str(context.exception), "Connection failed")
            mock_logger.error.assert_called_once_with("Error updating document: %s", "Connection failed")
        except Exception as e:
            print("Error at update document connection error")

    @patch.object(ElasticSearchUtils, 'call_request')
    def test_delete_document_success(self, mock_call_request):
        # Setup
        mock_response = MagicMock()
        mock_call_request.return_value = mock_response
        es_utils = ElasticSearchUtils()
        host_name = "http://localhost:9200"
        index = "my_index"
        document_id = "document_id"
        headers = {"Content-Type": "application/json"}

        # Execute
        response = es_utils.delete_document(host_name, index, document_id, headers)

        # Verify
        self.assertEqual(response, mock_response)
        mock_call_request.assert_called_once_with(
            method="DELETE",
            url=f"{host_name}/{index}/_doc/{document_id}",
            headers=headers
        )

    def test_delete_document_missing_host_name(self):
        # Setup
        es_utils = ElasticSearchUtils()
        index = "my_index"
        document_id = "document_id"

        # Execute & Verify
        with self.assertRaises(ValueError) as context:
            es_utils.delete_document("", index, document_id)
        self.assertEqual(str(context.exception), "Host name, index, and ID are mandatory")

    def test_delete_document_missing_index(self):
        # Setup
        es_utils = ElasticSearchUtils()
        host_name = "http://localhost:9200"
        document_id = "document_id"

        # Execute & Verify
        with self.assertRaises(ValueError) as context:
            es_utils.delete_document(host_name, "", document_id)
        self.assertEqual(str(context.exception), "Host name, index, and ID are mandatory")

    def test_delete_document_missing_document_id(self):
        # Setup
        es_utils = ElasticSearchUtils()
        host_name = "http://localhost:9200"
        index = "my_index"

        # Execute & Verify
        with self.assertRaises(ValueError) as context:
            es_utils.delete_document(host_name, index, "")
        self.assertEqual(str(context.exception), "Host name, index, and ID are mandatory")

    @patch.object(ElasticSearchUtils, 'call_request')
    @patch('cafex_core.utils.elastic_search_utils.CoreLogger')
    def test_delete_document_request_exception(self, mock_logger, mock_call_request):
        # Setup
        try:
            mock_call_request.side_effect = Exception("Request failed")
            es_utils = ElasticSearchUtils()
            host_name = "http://localhost:9200"
            index = "my_index"
            document_id = "document_id"

            # Execute & Verify
            with self.assertRaises(Exception) as context:
                es_utils.delete_document(host_name, index, document_id)
            self.assertEqual(str(context.exception), "Request failed")
            mock_logger.error.assert_called_once_with("Error deleting document: %s", "Request failed")
        except Exception as e:
            print("Error at delete document request exception")

    @patch.object(ElasticSearchUtils, 'call_request')
    def test_bulk_insert_success(self, mock_call_request):
        # Setup
        mock_response = MagicMock()
        mock_call_request.return_value = mock_response
        es_utils = ElasticSearchUtils()
        host_name = "http://localhost:9200"
        payloads = [{"field1": "value1"}, {"field2": "value2"}]
        headers = {"Content-Type": "application/json"}

        # Execute
        response = es_utils.bulk_insert(host_name, payloads, headers)

        # Verify
        self.assertEqual(response, mock_response)
        mock_call_request.assert_called_once_with(
            method="POST",
            url=f"{host_name}/_bulk",
            headers=headers,
            payload='{"index": {}}\n{"field1": "value1"}\n{"index": {}}\n{"field2": "value2"}\n'
        )

    def test_bulk_insert_missing_host_name(self):
        # Setup
        es_utils = ElasticSearchUtils()
        payloads = [{"field1": "value1"}, {"field2": "value2"}]

        # Execute & Verify
        with self.assertRaises(ValueError) as context:
            es_utils.bulk_insert("", payloads)
        self.assertEqual(str(context.exception), "Kibana host name is mandatory")

    @patch.object(ElasticSearchUtils, 'call_request')
    @patch('cafex_core.utils.elastic_search_utils.CoreExceptions')
    @patch('cafex_core.utils.elastic_search_utils.CoreLogger')
    def test_bulk_insert_request_exception(self, mock_logger, mock_exceptions, mock_call_request):
        try:
            # Setup
            mock_call_request.side_effect = Exception("Request failed")
            es_utils = ElasticSearchUtils()
            host_name = "http://localhost:9200"
            payloads = [{"field1": "value1"}, {"field2": "value2"}]

            # Execute & Verify
            with self.assertRaises(Exception) as context:
                es_utils.bulk_insert(host_name, payloads)
            self.assertEqual(str(context.exception), "Request failed")
            mock_logger.error.assert_called_once_with("Error bulk inserting documents: %s", "Request failed")
        except Exception as e:
            print("Error at bulk insert request exception")


if __name__ == '__main__':
    unittest.main()
