import unittest
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
        payload = self.elastic_search_utils.generate_payload(pdict_must_parameters=pdict_must_parameters)
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
        payload = self.elastic_search_utils.generate_payload(pdict_must_parameters=pdict_must_parameters)
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
        payload = self.elastic_search_utils.generate_payload(pdict_must_parameters=pdict_must_parameters,
                                              pdict_any_parameters=pdict_any_parameters)
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
        payload = self.elastic_search_utils.generate_payload(pdict_must_parameters=pdict_must_parameters,
                                              pdict_not_parameters=pdict_not_parameters)
        self.assertEqual(payload, expected_payload)

    def test_generate_payload_with_custom_payload(self):
        custom_payload = {
            "custom_key": "custom_value"
        }
        payload = self.elastic_search_utils.generate_payload(pdict_payload=custom_payload)
        self.assertEqual(payload, custom_payload)

    def test_generate_payload_with_json_payload(self):
        json_payload = '{"custom_key": "custom_value"}'
        payload = self.elastic_search_utils.generate_payload(pjson_payload=json_payload)
        self.assertEqual(payload, {"custom_key": "custom_value"})

    def test_invalid_json_payload(self):
        with self.assertRaises(Exception) as context:
            self.elastic_search_utils.generate_payload(pjson_payload='{"key": "value"')
        self.assertIn("Error generating payload:", str(context.exception))

    def test_invalid_type_must_parameters(self):
        with self.assertRaises(Exception) as context:
            self.elastic_search_utils.generate_payload(pdict_must_parameters=["invalid", "list"])
        self.assertIn("Error generating payload:", str(context.exception))

    def test_call_request_get(self):
        url = "https://www.samplesite.com/api"
        headers = {"Accept": "application/json"}
        response = self.elastic_search_utils.call_request(
            "GET",
            url,
            headers,
            pstr_auth_username='your_username',
            pstr_auth_password='your_password'
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
            pstr_auth_username='wrong_user',
            pstr_auth_password='wrong_password'
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
            pint_message_count=100,
            pdict_headers=headers,
            pstr_auth_username='your_username',
            pstr_auth_password='your_password'
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
            pdict_headers=headers,
            pstr_auth_username='your_username',
            pstr_auth_password='your_password'
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
            pint_message_count=100,
            pdict_headers=headers,
            pstr_auth_username='your_username',
            pstr_auth_password='your_password'
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
            pdict_headers=headers,
            pstr_auth_username='your_username',
            pstr_auth_password='your_password'
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
            pdict_headers=headers,
            pstr_auth_username='your_username',
            pstr_auth_password='your_password'
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
            pdict_headers=headers,
            pstr_auth_username='your_username',
            pstr_auth_password='your_password'
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

    def test_verify_message_contains_success(self):
        result = self.elastic_search_utils.verify_message_contains("Success")
        self.assertTrue(result)

    def test_verify_message_contains_failure(self):
        result = self.elastic_search_utils.verify_message_contains("Failure")
        self.assertFalse(result)

    def test_verify_message_contains_with_retry_success(self):
        result = self.elastic_search_utils.verify_message_contains("Operation completed", pbln_retry=True)
        self.assertTrue(result)

    def test_verify_message_contains_with_retry_failure(self):
        result = self.elastic_search_utils.verify_message_contains("Unknown error", pbln_retry=True)
        self.assertFalse(result)

    def test_verify_message_contains_with_none_expected_value(self):
        with self.assertRaises(Exception) as context:
            self.elastic_search_utils.verify_message_contains(None)
        self.assertEqual(str(context.exception), "pobj_expected_value cannot be None")

    def test_verify_message_contains_at_path_success(self):
        result = self.elastic_search_utils.verify_message_contains_at_path(".Message", "Success: Operation completed successfully.")
        self.assertTrue(result)

    def test_verify_message_contains_at_path_failure(self):
        result = self.elastic_search_utils.verify_message_contains_at_path(".Message", "Failed")
        self.assertFalse(result)

    def test_verify_message_contains_at_path_in_list_success(self):
        result = self.elastic_search_utils.verify_message_contains_at_path(".Log.Details", "Success")
        self.assertTrue(result)

    def test_verify_message_contains_at_path_in_list_failure(self):
        result = self.elastic_search_utils.verify_message_contains_at_path(".Log.Details", "Error")
        self.assertFalse(result)

    def test_verify_message_contains_at_path_with_none_expected_value(self):
        with self.assertRaises(Exception) as context:
            self.elastic_search_utils.verify_message_contains_at_path(".Message", None)
        self.assertEqual(str(context.exception), "pobj_expected_value cannot be None")

    def test_verify_message_contains_at_path_with_none_path(self):
        with self.assertRaises(Exception) as context:
            self.elastic_search_utils.verify_message_contains_at_path(None, "Success")
        self.assertEqual(str(context.exception), "pstr_nodepath cannot be None")

    def test_get_node_value_success(self):
        result = self.elastic_search_utils.get_node_value(".Message")
        self.assertEqual(result, "Success: Operation completed successfully.")

    def test_get_node_value_list_success(self):
        result = self.elastic_search_utils.get_node_value(".Log.Details")
        self.assertEqual(result, ["Success", "Warning"])

    def test_get_node_value_not_found(self):
        result = self.elastic_search_utils.get_node_value(".NonExistentPath")
        self.assertIsNone(result)

    def test_get_node_value_empty_list(self):
        result = self.elastic_search_utils.get_node_value(".Log.EmptyList")
        self.assertIsNone(result)

    def test_get_node_value_with_custom_json(self):
        custom_json = {
            "Status": "Completed",
            "Errors": []
        }
        result = self.elastic_search_utils.get_node_value(".Status", pjson_content=custom_json)
        self.assertEqual(result, "Completed")

    def test_get_node_value_with_invalid_path(self):
        with self.assertRaises(Exception) as context:
            self.elastic_search_utils.get_node_value("")
        self.assertEqual(str(context.exception), "Expected an attribute name.")

    def test_get_values_with_msg_success(self):
        result = self.elastic_search_utils.get_values_with_msg(".Messages", "Error")
        self.assertEqual(result, ["Error: Operation failed."])

    def test_get_values_with_msg_multiple_matches(self):
        result = self.elastic_search_utils.get_values_with_msg(".Logs.Details", "Success")
        self.assertEqual(result, ["Success: Backup completed."])

    def test_get_values_with_msg_no_matches(self):
        result = self.elastic_search_utils.get_values_with_msg(".Messages", "Critical")
        self.assertEqual(result, [])

    def test_get_values_with_msg_with_none_node_path(self):
        with self.assertRaises(ValueError) as context:
            self.elastic_search_utils.get_values_with_msg(None, "Error")
        self.assertEqual(str(context.exception), "pstr_node_path cannot be None")

    def test_get_values_with_msg_with_none_message(self):
        with self.assertRaises(ValueError) as context:
            self.elastic_search_utils.get_values_with_msg(".Messages", None)
        self.assertEqual(str(context.exception), "pstr_msg_contains cannot be None")

    def test_get_values_with_msg_with_none_json_content(self):
        self.elastic_search_utils.response = None
        result = self.elastic_search_utils.get_values_with_msg(".Messages", "Error")
        self.assertEqual(result, [])

    def test_get_node_count_success(self):
        count = self.elastic_search_utils.get_node_count(".Messages")
        self.assertEqual(count, 4)

    def test_get_node_count_single_value(self):
        count = self.elastic_search_utils.get_node_count(".Message")
        self.assertEqual(count, 1)

    def test_get_node_count_no_matches(self):
        count = self.elastic_search_utils.get_node_count(".NonExistentPath")
        self.assertEqual(count, 0)

    def test_get_node_count_empty_list(self):
        self.elastic_search_utils.response["EmptyList"] = []
        count = self.elastic_search_utils.get_node_count(".EmptyList")
        self.assertEqual(count, 0)

    def test_get_node_count_with_generator(self):
        self.elastic_search_utils.response["GeneratorTest"] = (x for x in ["Error", "Success"])
        count = self.elastic_search_utils.get_node_count(".GeneratorTest")
        print(f"Count obtained: {count}")
        self.assertEqual(count, 2)

    def test_get_node_count_with_none_path(self):
        with self.assertRaises(Exception) as context:
            self.elastic_search_utils.get_node_count(None)
        self.assertEqual(str(context.exception), "Invalid path format")

    def test_get_message_count_success(self):
        count = self.elastic_search_utils.get_message_count("Success")
        self.assertEqual(count, 2)

    def test_get_message_count_error_in_errors(self):
        count = self.elastic_search_utils.get_message_count("Error occurred", pstr_node_path=".Errors")
        self.assertEqual(count, 1)

    def test_get_message_count_error(self):
        count = self.elastic_search_utils.get_message_count("Error occurred")
        self.assertEqual(count, 2)

    def test_get_message_count_no_occurrences(self):
        count = self.elastic_search_utils.get_message_count("Non-existent message")
        self.assertEqual(count, 0)

    def test_get_message_count_with_custom_node_path(self):
        count = self.elastic_search_utils.get_message_count("Error occurred", pstr_node_path=".Errors")
        self.assertEqual(count, 1)

    def test_get_message_count_response_none(self):
        self.elastic_search_utils.response = None
        with self.assertRaises(Exception) as context:
            self.elastic_search_utils.get_message_count("Success")
        self.assertEqual(str(context.exception), "Response cannot be None.")

    def test_extract_regex_matches_success_messages(self):
        matches = self.elastic_search_utils.extract_regex_matches(".Messages", r"Success")
        self.assertEqual(matches, ["Success", "Success"])

    def test_extract_regex_matches_error_messages(self):
        matches = self.elastic_search_utils.extract_regex_matches(".Messages", r"Error")
        self.assertTrue(any("Error" in match for match in matches))

    def test_extract_regex_matches_no_matches(self):
        matches = self.elastic_search_utils.extract_regex_matches(".Messages", r"NonExistent")
        self.assertEqual(matches, [])

    def test_extract_regex_matches_multiple_patterns(self):
        matches = self.elastic_search_utils.extract_regex_matches(".Logs.Details", r"(Error|Warning)")
        self.assertEqual(sorted(set(matches)), sorted(["Error", "Warning"]))

    def test_extract_regex_matches_partial_match(self):
        matches = self.elastic_search_utils.extract_regex_matches(".Messages", r"Error occurred")
        self.assertEqual(matches, ["Error occurred"])

    def test_extract_regex_matches_with_special_characters(self):
        matches = self.elastic_search_utils.extract_regex_matches(".Logs.Details", r"Disk space low")
        self.assertEqual(matches, ["Disk space low"])

    def test_extract_regex_matches_all_messages(self):
        matches = self.elastic_search_utils.extract_regex_matches(".Messages", r".*")
        self.assertEqual(sorted(matches),
                         sorted(
                             [""] * len(self.elastic_search_utils.response["Messages"]) + ["Error occurred",
                                                                                           "Success",
                                                                                           "Success"]))

if __name__ == '__main__':
    unittest.main()
