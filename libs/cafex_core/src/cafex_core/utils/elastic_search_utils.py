"""
This module contains utility methods to query Kibana or Elasticsearch through its API.
"""
import collections
import itertools
import json
import re
import time
import types
import requests
from cafex_api.api_exceptions import APIExceptions
from cafex_core.logging.logger_ import CoreLogger
from cafex_core.parsers.json_parser import ParseJsonData
from cafex_core.utils.exceptions import CoreExceptions


class ElasticSearchUtils:
    """
    Description:
        This class contains methods to query Kibana or Elasticsearch through its API.
    """

    def __init__(self):
        self.logger_class = CoreLogger(name=__name__)
        self.logger = self.logger_class.get_logger()
        self.response = None
        self.__exceptions = CoreExceptions()
        self.__exceptions_services = APIExceptions()

    def generate_payload(self,
                         must_parameters: dict = None,
                         any_parameters: dict = None,
                         not_parameters: dict = None,
                         payload: dict = None,
                         json_payload: str = None,
                         index: str = "*",
                         strict_match: bool = False) -> dict:
        """
        Generates the payload based on the filter criteria of the user.

        Args:
            must_parameters (dict): Must (mandatory) conditions to filter.
            any_parameters (dict): Any (match one of) conditions to filter.
            not_parameters (dict): Not (match none) conditions to filter.
            payload (dict): Custom payload to use instead of dynamic construction.
            json_payload (str): Custom JSON payload to use instead of dynamic construction.
            index (str): Index to filter (e.g., cafex-services-*).
            strict_match (bool): Whether to use strict string matching.

        Returns:
            dict: The generated payload.

        Examples:
            >> payload = ElasticSearchUtils().generate_payload(pdict_must_parameters=
            {"Application.Name": "DataApiService_int", "Application.LogType": "heartbeat"})
        """
        try:
            dict_payload = payload or {}
            if payload:
                self.logger.debug("Using custom JSON payload.")
                return json.loads(json_payload)

            dict_must_parameters = must_parameters or {}
            if "@timestamp" not in dict_must_parameters:
                dict_must_parameters["@timestamp"] = {"gt": "now-15m"}
                self.logger.debug("Added default @timestamp filter: %s",
                                  dict_must_parameters["@timestamp"])
            if "Application.LogType" not in dict_must_parameters:
                dict_must_parameters["Application.LogType"] = "trace"
                self.logger.debug("Added default Application.LogType filter: %s",
                                  dict_must_parameters["Application.LogType"])

            filters = [{"range": {"@timestamp": dict_must_parameters.pop("@timestamp")}}]
            if index != "*":
                filters.append({"wildcard": {"_index": {"value": index}}})
                self.logger.debug("Using index filter: %s", index)

            payload = self.__condition_builder(must_parameters, {}, "must", strict_match)
            payload = self.__condition_builder(any_parameters or {}, payload,
                                               "should", strict_match)
            payload = self.__condition_builder(not_parameters or {}, payload,
                                               "must_not", strict_match)

            dict_payload["query"] = {"bool": {**payload, "filter": filters}}
            self.logger.debug("Generated payload: %s", dict_payload)
            return dict_payload

        except Exception as e:
            error_description = f"Error generating payload: {str(e)}"
            self.__exceptions.raise_generic_exception(
                message=error_description,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            raise e

    def __condition_builder(self, parameters: dict, payload: dict, condition: str,
                            sub_condition_strict_match: bool = False) -> dict:
        """
        Builds the condition for the query based on the provided parameters.

        Args:
            parameters (dict): The parameters to build conditions from.
            payload (dict): The existing payload to update with conditions.
            condition (str): The type of condition to apply (must, should, must_not).
            sub_condition_strict_match (bool): Whether to use strict matching for sub_conditions.

        Returns:
            dict: The updated payload with conditions added.
        """
        try:
            if parameters:
                any_filters = []
                for k, v in parameters.items():
                    if sub_condition_strict_match:
                        any_filters.append({"match_phrase": {str(k): v}})
                    else:
                        any_filters.append({"match": {str(k): v}})
                payload.update({condition: any_filters})
                if condition == "should":
                    payload.update({"minimum_should_match": 1})
            return payload
        except Exception as e:
            self.logger.error("Error building condition: %s", str(e))
            self.__exceptions.raise_generic_exception(
                message=str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            raise e

    def run_query(self, host_name: str, endpoint: str, payload: dict,
                  message_count: int = 100, headers: dict = None,
                  **kwargs):
        """
        Queries Kibana using the specified payload and fetches the appropriate results.

        Args:
            host_name (str): Kibana/Elastic server hostname.
            endpoint (str): Specific endpoint for the Kibana/Elastic call.
            payload (dict): Payload to filter the message for elastic search.
            message_count (int): Number of elements to filter (default is 100).
            headers (dict): Headers for the Kibana search.

        Returns:
            requests.Response: Response from the Elasticsearch server.

        Raises:
            ValueError: If the host name is not provided.

        Examples:
            >> response = ElasticSearchUtils().run_query("http://localhost:9200",
             payload)
            >> response = ElasticSearchUtils().run_query("http://localhost:9200",
             payload,pint_message_count=50)
        """
        if not host_name:
            raise ValueError("Kibana host name is mandatory")

        str_end_point = endpoint.format(item_size=message_count)

        try:
            response = self.call_request(
                pstr_method="GET",
                pstr_url=host_name + str_end_point,
                pdict_headers=headers or {},
                pstr_payload=json.dumps(payload),
                **kwargs
            )
            return response

        except requests.exceptions.RequestException as e:
            self.logger.error("Error in run_query: %s", str(e))
            raise e

    def run_custom_query(self, method: str, host_name: str, end_point: str,
                         payload: dict, headers: dict = None,
                         **kwargs):
        """
        Executes a custom query on Kibana with user-defined parameters.

        Args:
            method (str): HTTP request method (e.g., 'GET', 'POST').
            host_name (str): Kibana/Elastic server hostname.
            end_point (str): Specific endpoint for the Kibana/Elastic call.
            payload (dict): Payload for filtering messages in Elasticsearch.
            headers (dict): Optional headers for the request.

        Returns:
            requests.Response: Response from the Elasticsearch server.

        Raises:
            ValueError: If the host name is not provided.
            Exception: For any errors during the request execution.

        Examples:
            >> response = ElasticSearchUtils().run_custom_query("POST",
             "http://localhost:9200", "/my_endpoint", payload)
        """
        if not host_name:
            raise ValueError("Kibana host name is mandatory")

        payload = json.dumps(payload) if payload else None

        try:
            response = self.call_request(
                pstr_method=method,
                pstr_url=f"{host_name}{end_point}",
                pdict_headers=headers or {},
                pstr_payload=payload,
                **kwargs,
            )
            return response

        except requests.exceptions.RequestException as e:
            self.logger.error("Error in run_custom_query: %s", str(e))
            raise ConnectionError(f"Error in run_custom_query: {str(e)}") from e
        except Exception as e:
            self.logger.error("An error occurred: %s", str(e))
            raise e

    def __retry_request(self, condition, **kwargs) -> bool:
        """
        Internal method to retry a request until a specified condition is met.

        Args:
            condition (function): A function that returns a boolean indicating if
            the condition is met.
            **kwargs: Additional parameters:
                - max_wait_period_sec (int): Maximum wait period in seconds (default is 60).
                - polling_interval_sec (int): Polling interval in seconds (default is 15).
                - response (requests.Response): The response object to validate.

        Returns:
            bool: True if the condition is met; otherwise, False.

        Examples:
            >> success = ElasticSearchUtils().
            __retry_request(lambda r: r.status_code == 200)
        """
        max_wait_period: int = kwargs.get("max_wait_period_sec", 60)
        polling_interval: int = kwargs.get("polling_interval_sec", 15)
        response = kwargs.get("response", self.response)

        if response is None:
            self.logger.error("Response object is not found.")
            self.__exceptions_services.raise_null_value(
                message="response object is not found",
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )

        try:
            start_time: int = 0
            while start_time < max_wait_period:
                if condition(response, **kwargs):
                    return True

                time.sleep(polling_interval)
                self.logger.info("Retrying request...")
                response = requests.Session().send(response.request)
                start_time += polling_interval

            return False
        except Exception as e:
            self.logger.error("Error during retry: %s", str(e))
            self.__exceptions.raise_generic_exception(
                message=str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True,
            )
            raise e

    def __verify_node(self, json_response: object, **kwargs) -> bool:
        """
        Internal method to verify if a specified node equals an expected value.

        Args:
            json_response (object): JSON response object for validation.
            **kwargs: Additional parameters:
                - node_path (str): Path of the property in the JSON object.
                - expected_value (object): Expected value to compare against.

        Returns:
            bool: True if the node equals the expected value; otherwise, False.

        Examples:
            >> is_equal = ElasticSearchUtils().__verify_node(response,
            node_path=".status", expected_value="success")
        """
        node_path = kwargs.get("node_path", "")
        expected_value = kwargs.get("expected_value", "")

        actual_value = self.get_node_value(
            node_path=node_path, content=json_response, **kwargs
        )
        if isinstance(actual_value, (itertools.chain, types.GeneratorType)):
            for value in actual_value:
                if value == expected_value:
                    return True
            return False
        return actual_value == expected_value

    def __verify_node_contains(self, json_response: object, **kwargs) -> bool:
        """
        Internal method to verify if a specified node contains an expected value.

        Args:
            pobj_json_response (object): JSON response object for validation.
            **kwargs: Additional parameters:
                - node_path (str): Path of the property in the JSON object.
                - expected_value (object): Expected value to check for containment.
                - fun_condition (function): Custom condition function to check for
                 containment.

        Returns:
            bool: True if the node contains the expected value; otherwise, False.

        Examples:
            >> contains = ElasticSearchUtils().__verify_node_contains(response,
            node_path=".messages",expected_value="error")
        """
        node_path = kwargs.get("node_path", "")
        expected_value = kwargs.get("pobj_expected_value", "")
        condition = kwargs.get("fun_condition", lambda x, y: str(x).__contains__(y))

        actual_value = self.get_node_value(
            pstr_node_path=node_path, pjson_content=json_response, **kwargs
        )
        if not isinstance(actual_value, (itertools.chain, types.GeneratorType)):
            return condition(actual_value, expected_value)
        for item in actual_value:
            if condition(item, expected_value):
                return True
        return False

    def verify_response_code(self, expected_response_code, **kwargs):
        """
        Verifies the response code and retries based on retry condition.

        Args:
            expected_response_code (int): Expected HTTP response code.
            **kwargs: Additional parameters for retry conditions:
                - retry (bool): When true, will retry until the condition is true or
                timeout occurs.
                - max_wait_period_sec (int): Maximum wait period, default is 60 sec.
                - polling_interval_sec (int): Polling interval for retry condition,
                default is 15 sec.
                - response (requests.Response): The response object to validate.

        Returns:
            bool: True if the expected response code matches.

        Examples:
            >> is_valid = ElasticSearchUtils().verify_response_code(200)
            >> is_valid = ElasticSearchUtils().verify_response_code(404, retry=True)
        """

        def response_code_validation(response, **params):
            return response.status_code == int(params["expected_response_code"])

        try:
            retry = kwargs.get("retry", False)
            response_object = kwargs.get("response")  # Get the response object
            kwargs["expected_response_code"] = expected_response_code

            if retry:
                return self.__retry_request(condition=response_code_validation, **kwargs)
            return response_object.status_code == int(expected_response_code)
        except Exception as e:
            self.logger.error("Error verifying response code: %s", str(e))
            self.__exceptions.raise_generic_exception(
                message=f"Error verifying response code: {str(e)}",
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            raise e

    def verify_node_equals(self, node_path: str, expected_value: object, **kwargs) -> bool:
        """
        Verifies if a node equals an expected value.

        Args:
            node_path (str): JSON path/node path.
            expected_value (object): Expected value.
            **kwargs: Additional parameters for retry conditions:
                - retry (bool): When true, will retry until the condition is true or timeout occurs.
                - _max_wait_period_sec (int): Maximum wait period, default is 60 sec.
                - polling_interval_sec (int): Polling interval for retry condition,
                default is 15 sec.

        Returns:
            bool: True if the node equals the expected value; otherwise, False.

        Examples:
            >> is_equal = ElasticSearchUtils().verify_node_equals(".status", "success")
            >> is_equal = ElasticSearchUtils().verify_node_equals(".data", {"id": 1}, retry=True)
        """
        try:
            retry = kwargs.get("retry", False)
            if node_path is None:
                raise ValueError("node_path cannot be None")
            if expected_value is None:
                raise ValueError("expected_value cannot be None")

            kwargs["response"] = self.response
            kwargs["node_path"] = node_path
            kwargs["expected_value"] = expected_value

            if retry:
                return self.__retry_request(condition=self.__verify_node, **kwargs)
            return self.__verify_node(json_response=self.response, **kwargs)
        except Exception as e:
            self.logger.error("Error verifying node equals: %s", str(e))
            self.__exceptions.raise_generic_exception(
                message=str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            raise e

    def verify_node_contains(self, node_path: str, expected_value: object, **kwargs) -> bool:
        """
        Verifies if a node contains an expected value.

        Args:
            node_path (str): JSON path/node path.
            expected_value (object): Expected value.
            **kwargs: Additional parameters for retry conditions:
                - retry (bool): When true, will retry until the condition is true or timeout occurs.
                - pint_max_wait_period_sec (int): Maximum wait period, default is 60 sec.
                - pint_polling_interval_sec (int): Polling interval for retry condition,
                default is 15 sec.
                - response (requests.Response): The response object to validate.

        Returns:
            bool: True if the node contains the expected value; otherwise, False.

        Examples:
            >> contains = ElasticSearchUtils().verify_node_contains(response,node_path=".messages",
             expected_value="error")
        """
        try:
            bln_retry = kwargs.get("retry", False)

            if node_path is None:
                raise ValueError("node_path cannot be None")
            if expected_value is None:
                raise ValueError("expected_value cannot be None")

            kwargs["response"] = self.response
            kwargs["node_path"] = node_path
            kwargs["expected_value"] = expected_value

            if bln_retry:
                return self.__retry_request(condition=self.__verify_node_contains, **kwargs)
            return self.__verify_node_contains(json_response=self.response, **kwargs)
        except Exception as e:
            self.logger.error("Error verifying node contains: %s", str(e))
            self.__exceptions.raise_generic_exception(
                message=str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            raise e

    def verify_message_contains(self, node_path: str, expected_value: str, **kwargs) -> bool:
        """
        Verify if a message property in the returned Kibana logs has the expected value.

        Args:
            node_path (str): JSON path of the node to verify (e.g., .Message or Log.Type).
            expected_value (str): Value to search in the message.
            **kwargs: Additional parameters:
                - max_wait_period_sec (int): Maximum wait period, default is 60 sec.
                - polling_interval_sec (int): Polling interval for retry condition,
                default is 15 sec.
                - retry (bool): When true, will retry until the condition is true or timeout occurs.

        Returns:
            bool: True if the expected value is found in the message; otherwise, False.

        Examples:
            >> found = ElasticSearchUtils().verify_message_contains("Success")
            >> found = ElasticSearchUtils().verify_message_contains("Error occurred", retry=True)
        """
        try:
            return self.verify_node_contains(
                node_path=node_path,
                expected_value=expected_value,
                **kwargs,
            )
        except Exception as e:
            self.__exceptions.raise_generic_exception(
                message=str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            raise e

    def verify_message_contains_at_path(self, node_path: str, expected_message: str,
                                        **kwargs) -> bool:
        """
        Verify if the expected message is present in the JSON path mentioned.

        Args:
            node_path (str): JSON path of the node to verify (e.g., .Message or Log.Type).
            expected_message (str): Message to verify.
            **kwargs: Additional parameters:
                - max_wait_period_sec (int): Maximum wait period, default is 60 sec.
                - polling_interval_sec (int): Polling interval for each retry,
                default is 15 sec.
                - retry (bool): When true, will retry until the condition is true or timeout occurs.

        Returns:
            bool: True if the expected message is found; otherwise, False.

        Examples:
            >> found = ElasticSearchUtils().verify_message_contains_at_path(".Message", "Success")
            >> found = ElasticSearchUtils().
            verify_message_contains_at_path(".Message", "Failed", retry=True)
        """
        try:
            return self.verify_node_contains(
                node_path=node_path, expected_value=expected_message, **kwargs
            )

        except Exception as e:
            self.__exceptions.raise_generic_exception(
                message=str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            raise e

    def verify_message_equals_at_path(self, node_path, expected_message, **kwargs):
        """
        Verify if the expected message is equal to the message in the JSON path mentioned.

        Args:
            node_path (str): JSON path of the node to verify (e.g., .Message or Log.Type).
            expected_message (str): Message to verify.
            **kwargs: Additional parameters:
                - max_wait_period_sec (int): Maximum wait period, default is 60 sec.
                - polling_interval_sec (int): Polling interval for each retry,
                default is 15 sec.
                - retry (bool): When true, will retry until the condition is true or
                timeout occurs.

        Returns:
            bool: True if the expected message matches; otherwise, False.

        Examples:
            >> matches = ElasticSearchUtils().verify_message_equals_at_path(".Message", "Success")
            >> matches = ElasticSearchUtils().verify_message_equals_at_path(".Message",
            "Failed", retry=True)
        """
        try:
            return self.verify_node_equals(
                node_path=node_path, expected_value=expected_message, **kwargs
            )

        except Exception as e:
            self.__exceptions.raise_generic_exception(
                message=str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            raise e

    # endregion
    # region Extraction Methods
    def get_node_value(self, node_path: str, **kwargs) -> collections.Iterable | None | object:
        """
        Returns the value present in the JSON path.

        Args:
            node_path (str): JSON path/node path.
            **kwargs: Additional parameters:
                - delimiter (str): Delimiter for JSON path (default is .).
                - json_content (json): JSON content on which the JSON path parser
                 would run (default is self.response).
                 -parser (bool): Whether to parse the JSON content (default is False).

        Returns:
            object: The value found at the specified JSON path.

        Examples:
            >> value = ElasticSearchUtils().get_node_value(".Message")
            >> value = ElasticSearchUtils().get_node_value(".SomeNodePath",
            json_content=response.content)
        """
        json_content = kwargs.get("json_content", self.response)
        delimiter = kwargs.get("delimiter", ".")
        parser = kwargs.get("parser", False)

        try:
            values = list(ParseJsonData().get_json_values_by_key_path(
                json_content, delimiter, keypath=node_path, parser=parser
            ))

            if not values:
                return None

            return values if len(values) > 1 else values[0]

        except Exception as e:
            self.logger.error("Error getting node value: %s", str(e))
            self.__exceptions.raise_generic_exception(
                message=str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            raise e

    def get_values_with_msg(self, node_path, msg_contains, **kwargs):
        """
        Returns a list of values matching the specified message from the JSON path.

        Args:
            node_path (str): JSON path/node path.
            msg_contains (str): Expected message to filter values.
            **kwargs: Additional parameters:
                - delimiter (str): Delimiter for JSON path (default is .).
                - json_content (json): JSON content on which the JSON path parser would run
                (default is self.response).

        Returns:
            list: List of values containing the specified message.

        Examples:
            >> values = ElasticSearchUtils().get_values_with_msg(".Message", "error")
            >> values = ElasticSearchUtils().get_values_with_msg(".Logs", "success",
            json_content=response.content)
        """
        if node_path is None:
            raise ValueError("node_path cannot be None")
        if msg_contains is None:
            raise ValueError("msg_contains cannot be None")

        json_content = kwargs.get("json_content", self.response)

        if json_content is None:
            return []

        try:
            values = self.get_node_value(node_path, **kwargs)
            return [match for match in values if msg_contains in match] if values else []

        except Exception as e:
            self.logger.error("Error getting values with message: %s", str(e))
            self.__exceptions.raise_generic_exception(
                message=str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            raise e

    def get_node_count(self, node_path):
        """
        Returns the count of the node occurrence in the response message.

        Args:
            node_path (str): JSON path of the node.

        Returns:
            int: Count of occurrences of the specified node.

        Examples:
            >> count = ElasticSearchUtils().get_node_count(".Message")
            >> count = ElasticSearchUtils().get_node_count(".Logs")
        """
        if node_path is None:
            raise ValueError("Invalid path format")

        try:
            node_path_count = self.get_node_value(node_path)

            if node_path_count is None:
                return 0

            if isinstance(node_path_count, list):
                return len(node_path_count)

            if isinstance(node_path_count, (types.GeneratorType, itertools.chain)):
                return len(list(node_path_count))

            return 1

        except Exception as e:
            self.logger.error("Error getting node count: %s", str(e))
            self.__exceptions.raise_generic_exception(
                message=str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            raise e

    def get_message_count(self, expected_message: str, node_path: str = None) -> int:
        """
        Returns the count of the expected message occurrence in the response messages.

        Args:
            node_path (str): JSON path of the node.
            expected_message (str): Expected message to count occurrences of.

        Returns:
            int: Count of occurrences of the expected message.

        Examples:
            >> count = ElasticSearchUtils().get_message_count("Success")
            >> count = ElasticSearchUtils().get_message_count("Error occurred",
            node_path=".Errors")
        """
        if self.response is None:
            raise ValueError("Response cannot be None.")

        try:
            if node_path is None:
                total_count = 0
                for key in self.response.keys():
                    values = self.get_values_with_msg(f".{key}", expected_message)
                    total_count += len(values)
                return total_count

            values = self.get_values_with_msg(node_path, expected_message)
            return len(values)

        except Exception as e:
            self.logger.error("Error getting message count: %s", str(e))
            self.__exceptions.raise_generic_exception(
                message=str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            raise e

    def extract_regex_matches(self, node_path: str, regex: str, **kwargs) -> list:
        """
        Returns a list of values matching the specified regex from the JSON path.

        Args:
            node_path (str): JSON path/node path.
            regex (str): Regex pattern to match values.

        Returns:
            list: List of matching values.

        Examples:
            >> matches = ElasticSearchUtils().extract_regex_matches(".Message", r"a-z")
            >> matches = ElasticSearchUtils().extract_regex_matches(".Logs", r"error",
            json_content=response.content)
        """
        try:
            output = []
            lst_values = self.get_node_value(pstr_node_path=node_path, **kwargs)
            for node_value in lst_values:
                output.extend(re.findall(regex, node_value, re.IGNORECASE))
            return output
        except Exception as e:
            self.logger.error("Error extracting regex matches: %s", str(e))
            self.__exceptions.raise_generic_exception(
                message=str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            raise e

    def extract_regex_matches_on_filter(self, node_path: str, msg_contains: str,
                                        regex: str, **kwargs) -> list:
        """
        Returns extracted values from the filtered messages, filtering all values
        containing the specified string.

        Args:
            node_path (str): JSON path/node path.
            regex (str): Regex pattern to match values.
            msg_contains (str): String to filter messages by.

        Returns:
            list: List of matching values.

        Examples:
            >> matches = ElasticSearchUtils().
            extract_regex_matches_on_filter(".Message", "error")
            >> matches = ElasticSearchUtils().
            extract_regex_matches_on_filter(".Logs", "failed", r"error",
             json_content=response.content)
        """
        try:
            output = []
            lst_value = self.get_node_value(node_path=node_path, **kwargs)

            if lst_value is None:
                return output

            for item in lst_value:
                if msg_contains in item:
                    output.extend(re.findall(regex, item, re.IGNORECASE))
            return output
        except Exception as e:
            self.logger.error("Error extracting regex matches on filter: %s", str(e))
            self.__exceptions.raise_generic_exception(
                message=str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            raise e

    def extract_regex_matches_on_messages(self, node_path, msg_search: str,
                                          regex_match: str) -> list:
        """
        Extracts matches of regex from the message, considering only messages
         containing the specified string.

        Args:
            node_path (str): JSON path/node path.
            msg_search (str): Message selection criteria.
            regex_match (str): Regex to run to extract the match.

        Returns:
            list: List of matching regex values.

        Examples:
            >> matches = ElasticSearchUtils().extract_regex_matches_on_messages("error",r"a-z")
            >> matches = ElasticSearchUtils().extract_regex_matches_on_messages("failed", r"failed",
             json_content=response.content)
        """
        try:
            return self.extract_regex_matches_on_filter(
                node_path, msg_search, regex_match
            )
        except Exception as e:
            self.logger.error("Error extracting regex matches on messages: %s", str(e))
            self.__exceptions.raise_generic_exception(
                message=str(e),
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=False,
            )
            raise e

    def call_request(self, method: str, url: str, headers: dict, **kwargs) -> requests.Response:
        """
        Performs various HTTP requests (GET, POST, PUT, PATCH, DELETE).

        Args:
            method (str): The HTTP method (e.g., 'GET', 'POST').
            url (str): The request URL.
            headers (dict): Request headers.

        Kwargs:
            json (str): JSON data for the request body.
            payload (dict): Data for the request body.
            cookies (dict): Cookies for the request.
            allow_redirects (bool): Allow or disallow redirects.
            files (str): File path for file uploads.
            verify (bool): Verify SSL certificates.
            auth_username (str): Username for authentication.
            auth_password (str): Password for authentication.
            timeout (float or tuple): Timeout in seconds for the request.

        Returns:
            requests.Response: The response object from the request.

        Examples:
            >> response = ApacheUtils.Nifi().call_request("GET", "https://www.samplesite.com/api",
             headers={"Accept": "application/json"})
        """
        if not url:
            raise ValueError("URL cannot be null")

        auth_username = kwargs.get("auth_username")
        auth_password = kwargs.get("auth_password")
        auth = (auth_username, auth_password) if auth_username and auth_password else None
        method = method.upper()
        try:
            if method == "GET":
                response = requests.get(
                    url,
                    headers=headers,
                    verify=kwargs.get("verify", False),
                    allow_redirects=kwargs.get("allow_redirects", False),
                    cookies=kwargs.get("cookies", {}),
                    auth=auth,
                    timeout=kwargs.get("timeout", None),
                    proxies=kwargs.get("proxies", None),
                )
            elif method == "POST":
                response = requests.post(
                    url,
                    headers=headers,
                    data=kwargs.get("payload", None),
                    json=kwargs.get("json", None),
                    verify=kwargs.get("verify", False),
                    allow_redirects=kwargs.get("allow_redirects", False),
                    cookies=kwargs.get("cookies", {}),
                    auth=auth,
                    timeout=kwargs.get("timeout", None),
                    proxies=kwargs.get("proxies", None),
                )
            elif method == "PUT":
                response = requests.put(
                    url,
                    headers=headers,
                    data=kwargs.get("payload", None),
                    verify=kwargs.get("verify", False),
                    allow_redirects=kwargs.get("allow_redirects", False),
                    cookies=kwargs.get("cookies", {}),
                    auth=auth,
                    timeout=kwargs.get("timeout", None),
                    proxies=kwargs.get("proxies", None),
                )
            elif method == "PATCH":
                response = requests.patch(
                    url,
                    headers=headers,
                    data=kwargs.get("payload", None),
                    verify=kwargs.get("verify", False),
                    allow_redirects=kwargs.get("allow_redirects", False),
                    cookies=kwargs.get("cookies", {}),
                    auth=auth,
                    timeout=kwargs.get("timeout", None),
                    proxies=kwargs.get("proxies", None),
                )
            elif method == "DELETE":
                response = requests.delete(
                    url,
                    headers=headers,
                    verify=kwargs.get("verify", False),
                    allow_redirects=kwargs.get("allow_redirects", False),
                    cookies=kwargs.get("cookies", {}),
                    auth=auth,
                    timeout=kwargs.get("timeout", None),
                    proxies=kwargs.get("proxies", None),
                )
            else:
                raise ValueError(f"Invalid HTTP method: {method}. Valid options are: "
                                 f"GET, POST, PUT, PATCH, DELETE")

            return response

        except Exception as e:
            self.logger.exception("Error in API Request: %s", e)
            raise e

    def count_documents(self, host_name: str, index: str, query: dict = None,
                        headers: dict = None) -> requests.Response:
        """
        Counts the number of documents in a specified index based on the given query.

        Args:
            host_name (str): Kibana/Elastic server hostname.
            index (str): Index name.
            query (dict): Query to filter documents (optional).
            headers (dict): Headers for the request.

        Returns:
            requests.Response: Response from the Elasticsearch server.

        Examples:
            >> response = ElasticSearchUtils().count_documents("http://localhost:9200",
             "my_index", {"match_all": {}})

        """
        try:
            if not host_name or not index:
                raise ValueError("Host name and index are mandatory")

            url = f"{host_name}/{index}/_count"
            payload = {"query": query} if query else {}
            response = self.call_request(
                method="POST",
                url=url,
                headers=headers or {},
                payload=json.dumps(payload)
            )
            return response
        except Exception as e:
            self.logger.error("Error counting documents: %s", str(e))
            raise e

    def get_all_documents(self, host_name: str, index: str, size: int = 1000,
                          headers: dict = None) -> requests.Response:
        """
        Retrieves all documents from a specified index.

        Args:
            host_name (str): Kibana/Elastic server hostname.
            index (str): Index name.
            size (int): Number of documents to retrieve (default is 1000).
            headers (dict): Headers for the request.

        Returns:
            requests.Response: Response from the Elasticsearch server.

        Examples:
            >> response = ElasticSearchUtils().get_all_documents("http://localhost:9200",
             "my_index", pint_size=10)

        """
        try:
            if not host_name or not index:
                raise ValueError("Host name and index are mandatory")

            url = f"{host_name}/{index}/_search?size={size}"
            response = self.call_request(
                method="GET",
                url=url,
                headers=headers or {}
            )
            return response
        except Exception as e:
            self.logger.error("Error getting all documents: %s", str(e))
            raise e

    def update_document(self, host_name: str, index: str, document_id: str,
                        payload: dict, headers: dict = None) -> requests.Response:
        """
        Updates a document in Elasticsearch by its ID.

        Args:
            host_name (str): Kibana/Elastic server hostname.
            index (str): Index name.
            document_id(str): Document ID to update.
            payload (dict): Payload with updated fields.
            headers (dict): Headers for the request.

        Returns:
            requests.Response: Response from the Elasticsearch server.

        Examples:
            >> update_payload = {"field": "new_value"}
            >> response = ElasticSearchUtils().update_document("http://localhost:9200",
            "my_index", "document_id", update_payload)

        """
        try:
            if not host_name or not index or not document_id:
                raise ValueError("Host name, index, and ID are mandatory")
            url = f"{host_name}/{index}/_update/{document_id}"
            update_payload = {"doc": payload}
            response = self.call_request(
                method="POST",
                url=url,
                headers=headers or {},
                payload=json.dumps(update_payload)
            )
            return response
        except ConnectionError as e:
            self.logger.error("Error updating document: %s", str(e))
            raise e

    def delete_document(self, host_name: str, index: str,
                        document_id: str, headers: dict = None) -> requests.Response:
        """
        Deletes a document from Elasticsearch by its ID.

        Args:
            host_name (str): Kibana/Elastic server hostname.
            index (str): Index name.
            document_id (str): Document ID to delete.
            headers (dict): Headers for the request.

        Returns:
            requests.Response: Response from the Elasticsearch server.

        Examples:
            >> response = ElasticSearchUtils().delete_document("http://localhost:9200",
             "my_index", "document_id")

        """
        try:
            if not host_name or not index or not document_id:
                raise ValueError("Host name, index, and ID are mandatory")

            url = f"{host_name}/{index}/_doc/{document_id}"
            response = self.call_request(
                method="DELETE",
                url=url,
                headers=headers or {}
            )
            return response
        except Exception as e:
            self.logger.error("Error deleting document: %s", str(e))
            raise e

    def bulk_insert(self, host_name: str, payloads: list,
                    headers: dict = None) -> requests.Response:
        """
        Inserts multiple documents into Elasticsearch in a single request.

        Args:
            host_name (str): Kibana/Elastic server hostname.
            payloads (list): List of payloads to insert.
            headers (dict): Headers for the request.

        Returns:
            requests.Response: Response from the Elasticsearch server.

        Examples:
            >> payloads = [{"field1": "value1"}, {"field2": "value2"}]
            >> response = ElasticSearchUtils().bulk_insert("http://localhost:9200", payloads)

        """
        try:
            if not host_name:
                raise ValueError("Kibana host name is mandatory")
            url = f"{host_name}/_bulk"
            bulk_payload = "\n".join(
                [json.dumps({"index": {}}) + "\n" + json.dumps(payload)
                 for payload in payloads]) + "\n"
            response = self.call_request(
                method="POST",
                url=url,
                headers=headers or {},
                payload=bulk_payload
            )
            return response
        except Exception as e:
            self.logger.error("Error bulk inserting documents: %s", str(e))
            raise e
