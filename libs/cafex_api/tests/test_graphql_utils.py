"""
Unit tests for the GraphQLUtils class using mocks.

This module contains tests that verify the functionality of the GraphQLUtils class
using mocks to avoid external dependencies.
"""

import json
import pytest
import requests
from unittest.mock import patch, Mock, MagicMock

from gql import Client
from gql.transport.exceptions import TransportQueryError, TransportProtocolError

from cafex_api.graphql_utils import GraphQLUtils


class TestGraphQLUtils:
    """Test suite for the GraphQLUtils class using mocks."""

    @pytest.fixture
    def gql_utils(self):
        """Create a GraphQLUtils instance for testing."""
        return GraphQLUtils()

    def test_init(self, gql_utils):
        """Test the initialization of GraphQLUtils."""
        assert gql_utils.client is None
        assert gql_utils.request_builder is not None
        assert gql_utils.logger is not None

    @patch('requests.get')
    def test_create_client_success(self, mock_get, gql_utils):
        """Test creating a GraphQL client successfully."""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Create client
        result = gql_utils.create_client("https://example.com/graphql")

        # Verify
        assert result is True
        assert gql_utils.client is not None
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_create_client_with_headers(self, mock_get, gql_utils):
        """Test creating a client with custom headers."""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Create client with headers
        custom_headers = {"Authorization": "Bearer token123"}
        result = gql_utils.create_client("https://example.com/graphql", headers=custom_headers)

        # Verify
        assert result is True
        assert gql_utils.client is not None
        mock_get.assert_called_once()
        # Check that headers were passed to the request
        call_kwargs = mock_get.call_args[1]
        assert "headers" in call_kwargs
        assert call_kwargs["headers"]["Authorization"] == "Bearer token123"

    @patch('requests.get')
    def test_create_client_with_timeout(self, mock_get, gql_utils):
        """Test creating a client with a timeout."""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Create client with timeout
        result = gql_utils.create_client("https://example.com/graphql", timeout=30)

        # Verify
        assert result is True
        assert gql_utils.client is not None
        mock_get.assert_called_once()
        # Check that timeout was passed to the request
        call_kwargs = mock_get.call_args[1]
        assert "timeout" in call_kwargs
        assert call_kwargs["timeout"] == 30

    @patch('requests.get')
    def test_create_client_with_verify(self, mock_get, gql_utils):
        """Test creating a client with SSL verification disabled."""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Create client with verification disabled
        result = gql_utils.create_client("https://example.com/graphql", verify=False)

        # Verify
        assert result is True
        assert gql_utils.client is not None
        mock_get.assert_called_once()
        # Check that verify was passed to the request
        call_kwargs = mock_get.call_args[1]
        assert "verify" in call_kwargs
        assert call_kwargs["verify"] is False

    @patch('requests.get')
    def test_create_client_empty_endpoint(self, mock_get, gql_utils):
        """Test creating a client with an empty endpoint."""
        # Create client with empty endpoint
        result = gql_utils.create_client("")

        # Verify
        assert result is False
        mock_get.assert_not_called()

    @patch('requests.get')
    def test_create_client_request_exception(self, mock_get, gql_utils):
        """Test creating a client when the request raises an exception."""
        # Setup mock to raise an exception
        mock_get.side_effect = requests.RequestException("Connection error")

        # Create client
        result = gql_utils.create_client("https://example.com/graphql")

        # Verify
        assert result is False
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_create_client_connection_error(self, mock_get, gql_utils):
        """Test creating a client when a ConnectionError occurs."""
        # Setup mock to raise a ConnectionError
        mock_get.side_effect = ConnectionError("Network error")

        # Create client
        result = gql_utils.create_client("https://example.com/graphql")

        # Verify
        assert result is False
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_create_client_generic_exception(self, mock_get, gql_utils):
        """Test creating a client when a generic exception occurs."""
        # Setup mock to raise a generic exception
        mock_get.side_effect = Exception("Something went wrong")

        # Create client
        result = gql_utils.create_client("https://example.com/graphql")

        # Verify
        assert result is False
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_create_client_null_response(self, mock_get, gql_utils):
        """Test creating a client when the response is None."""
        # Setup mock to return None
        mock_get.return_value = None

        # Create client
        result = gql_utils.create_client("https://example.com/graphql")

        # Verify
        assert result is False
        mock_get.assert_called_once()

    def test_execute_query_no_query(self, gql_utils):
        """Test executing a query with no query string."""
        # Execute query with empty query string
        result = gql_utils.execute_query("")

        # Verify
        assert result is None

    def test_execute_query_no_client(self, gql_utils):
        """Test executing a query without initializing a client."""
        # Reset client
        gql_utils.client = None

        # Execute query
        result = gql_utils.execute_query("query { test }")

        # Verify
        assert result is None

    @patch('requests.get')
    @patch.object(Client, 'execute')
    def test_execute_query_success(self, mock_execute, mock_get, gql_utils):
        """Test executing a query successfully."""
        # Setup mocks
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        expected_result = {"data": {"test": "value"}}
        mock_execute.return_value = expected_result

        # Create client and execute query
        gql_utils.create_client("https://example.com/graphql")
        result = gql_utils.execute_query("query { test }")

        # Verify
        assert result == expected_result
        mock_execute.assert_called_once()

    @patch('requests.get')
    @patch.object(Client, 'execute')
    def test_execute_query_with_variables(self, mock_execute, mock_get, gql_utils):
        """Test executing a query with variables."""
        # Setup mocks
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        expected_result = {"data": {"test": "value"}}
        mock_execute.return_value = expected_result

        # Create client and execute query with variables
        gql_utils.create_client("https://example.com/graphql")
        variables = {"id": "123"}
        result = gql_utils.execute_query("query ($id: ID!) { test(id: $id) }", variables)

        # Verify
        assert result == expected_result
        mock_execute.assert_called_once()
        # Check that variables were passed to execute
        call_args = mock_execute.call_args[1]
        assert "variable_values" in call_args
        assert call_args["variable_values"] == variables

    @patch('requests.get')
    @patch.object(Client, 'execute')
    def test_execute_query_with_endpoint(self, mock_execute, mock_get, gql_utils):
        """Test executing a query with a one-time endpoint."""
        # Setup mocks
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        expected_result = {"data": {"test": "value"}}
        mock_execute.return_value = expected_result

        # Execute query with endpoint
        result = gql_utils.execute_query(
            "query { test }",
            endpoint="https://example.com/graphql"
        )

        # Verify
        assert result == expected_result
        mock_execute.assert_called_once()
        assert gql_utils.client is not None

    @patch('requests.get')
    @patch.object(Client, 'execute')
    def test_execute_query_client_error(self, mock_execute, mock_get, gql_utils):
        """Test executing a query when the client raises an error."""
        # Setup mocks
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Setup client execute to raise an error
        mock_execute.side_effect = TransportQueryError("GraphQL query error")

        # Create client and execute query
        gql_utils.create_client("https://example.com/graphql")
        result = gql_utils.execute_query("query { test }")

        # Verify
        assert result is None
        mock_execute.assert_called_once()

    @patch('requests.get')
    @patch.object(Client, 'execute')
    def test_execute_query_generic_exception(self, mock_execute, mock_get, gql_utils):
        """Test executing a query when a generic exception occurs."""
        # Setup mocks
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Setup client execute to raise a generic exception
        mock_execute.side_effect = Exception("Something went wrong")

        # Create client and execute query
        gql_utils.create_client("https://example.com/graphql")
        result = gql_utils.execute_query("query { test }")

        # Verify
        assert result is None
        mock_execute.assert_called_once()

    @patch('cafex_api.graphql_utils.GraphQLUtils.create_client')
    def test_execute_query_client_creation_fails(self, mock_create_client, gql_utils):
        """Test executing a query when client creation fails."""
        # Setup mock
        mock_create_client.return_value = False

        # Execute query with endpoint
        result = gql_utils.execute_query(
            "query { test }",
            endpoint="https://example.com/graphql"
        )

        # Verify
        assert result is None
        mock_create_client.assert_called_once()

    @patch('cafex_api.request_builder.RequestBuilder.call_request')
    def test_execute_raw_request_success(self, mock_call_request, gql_utils):
        """Test executing a raw request successfully."""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = {"data": {"test": "value"}}
        mock_call_request.return_value = mock_response

        # Execute raw request
        result = gql_utils.execute_query_with_raw_request(
            "query { test }",
            "https://example.com/graphql"
        )

        # Verify
        assert result == {"data": {"test": "value"}}
        mock_call_request.assert_called_once()

    @patch('cafex_api.request_builder.RequestBuilder.call_request')
    def test_execute_raw_request_with_variables(self, mock_call_request, gql_utils):
        """Test executing a raw request with variables."""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = {"data": {"test": "value"}}
        mock_call_request.return_value = mock_response

        # Execute raw request with variables
        variables = {"id": "123"}
        result = gql_utils.execute_query_with_raw_request(
            "query ($id: ID!) { test(id: $id) }",
            "https://example.com/graphql",
            variables=variables
        )

        # Verify
        assert result == {"data": {"test": "value"}}
        mock_call_request.assert_called_once()
        # Check that variables were passed to the request
        call_kwargs = mock_call_request.call_args[1]
        assert "json_data" in call_kwargs
        assert call_kwargs["json_data"]["variables"] == variables

    @patch('cafex_api.request_builder.RequestBuilder.call_request')
    def test_execute_raw_request_with_headers(self, mock_call_request, gql_utils):
        """Test executing a raw request with custom headers."""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = {"data": {"test": "value"}}
        mock_call_request.return_value = mock_response

        # Execute raw request with headers
        headers = {"Authorization": "Bearer token123"}
        result = gql_utils.execute_query_with_raw_request(
            "query { test }",
            "https://example.com/graphql",
            headers=headers
        )

        # Verify
        assert result == {"data": {"test": "value"}}
        mock_call_request.assert_called_once()
        # Check that headers were passed to the request
        call_kwargs = mock_call_request.call_args[1]
        assert "headers" in call_kwargs
        assert call_kwargs["headers"]["Authorization"] == "Bearer token123"

    @patch('cafex_api.request_builder.RequestBuilder.call_request')
    def test_execute_raw_request_with_timeout(self, mock_call_request, gql_utils):
        """Test executing a raw request with a timeout."""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = {"data": {"test": "value"}}
        mock_call_request.return_value = mock_response

        # Execute raw request with timeout
        result = gql_utils.execute_query_with_raw_request(
            "query { test }",
            "https://example.com/graphql",
            timeout=30
        )

        # Verify
        assert result == {"data": {"test": "value"}}
        mock_call_request.assert_called_once()
        # Check that timeout was passed to the request
        call_kwargs = mock_call_request.call_args[1]
        assert "timeout" in call_kwargs
        assert call_kwargs["timeout"] == 30

    @patch('cafex_api.request_builder.RequestBuilder.call_request')
    def test_execute_raw_request_with_verify(self, mock_call_request, gql_utils):
        """Test executing a raw request with SSL verification disabled."""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = {"data": {"test": "value"}}
        mock_call_request.return_value = mock_response

        # Execute raw request with verification disabled
        result = gql_utils.execute_query_with_raw_request(
            "query { test }",
            "https://example.com/graphql",
            verify=False
        )

        # Verify
        assert result == {"data": {"test": "value"}}
        mock_call_request.assert_called_once()
        # Check that verify was passed to the request
        call_kwargs = mock_call_request.call_args[1]
        assert "verify" in call_kwargs
        assert call_kwargs["verify"] is False

    @patch('cafex_api.request_builder.RequestBuilder.call_request')
    def test_execute_raw_request_with_errors(self, mock_call_request, gql_utils):
        """Test executing a raw request that returns GraphQL errors."""
        # Setup mock with errors in response
        mock_response = Mock()
        mock_response.json.return_value = {
            "errors": [
                {"message": "Field does not exist", "path": ["test"]}
            ]
        }
        mock_call_request.return_value = mock_response

        # Execute raw request
        result = gql_utils.execute_query_with_raw_request(
            "query { nonExistentField }",
            "https://example.com/graphql"
        )

        # Verify that we get the response with errors
        assert result is not None
        assert "errors" in result
        assert len(result["errors"]) == 1
        assert result["errors"][0]["message"] == "Field does not exist"

    def test_execute_raw_request_empty_endpoint(self, gql_utils):
        """Test executing a raw request with an empty endpoint."""
        # Execute raw request with empty endpoint
        result = gql_utils.execute_query_with_raw_request(
            "query { test }",
            ""
        )

        # Verify
        assert result is None

    def test_execute_raw_request_empty_query(self, gql_utils):
        """Test executing a raw request with an empty query."""
        # Execute raw request with empty query
        result = gql_utils.execute_query_with_raw_request(
            "",
            "https://example.com/graphql"
        )

        # Verify
        assert result is None

    @patch('cafex_api.request_builder.RequestBuilder.call_request')
    def test_execute_raw_request_null_response(self, mock_call_request, gql_utils):
        """Test executing a raw request when the response is None."""
        # Setup mock to return None
        mock_call_request.return_value = None

        # Execute raw request
        result = gql_utils.execute_query_with_raw_request(
            "query { test }",
            "https://example.com/graphql"
        )

        # Verify
        assert result is None
        mock_call_request.assert_called_once()

    @patch('cafex_api.request_builder.RequestBuilder.call_request')
    def test_execute_raw_request_json_error(self, mock_call_request, gql_utils):
        """Test executing a raw request when JSON parsing fails."""
        # Setup mock with invalid JSON
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_call_request.return_value = mock_response

        # Execute raw request
        result = gql_utils.execute_query_with_raw_request(
            "query { test }",
            "https://example.com/graphql"
        )

        # Verify
        assert result is None
        mock_call_request.assert_called_once()

    @patch('cafex_api.request_builder.RequestBuilder.call_request')
    def test_execute_raw_request_generic_exception(self, mock_call_request, gql_utils):
        """Test executing a raw request when a generic exception occurs."""
        # Setup mock to raise an exception
        mock_call_request.side_effect = Exception("Something went wrong")

        # Execute raw request
        result = gql_utils.execute_query_with_raw_request(
            "query { test }",
            "https://example.com/graphql"
        )

        # Verify
        assert result is None
        mock_call_request.assert_called_once()

    def test_get_data_null_response(self, gql_utils):
        """Test extracting data from a null response."""
        # Get data from null response
        result = gql_utils.get_data(None)

        # Verify
        assert result is None

    def test_get_data_non_dict_response(self, gql_utils):
        """Test extracting data from a non-dictionary response."""
        # Get data from non-dict response
        result = gql_utils.get_data("not a dict")

        # Verify
        assert result is None

    def test_get_data_empty_dict(self, gql_utils):
        """Test extracting data from an empty dictionary."""
        # Get data from empty dict
        result = gql_utils.get_data({})

        # Verify
        assert result == {}

    def test_get_data_with_data_field(self, gql_utils):
        """Test extracting data from a response with a data field."""
        # Response with data field
        response = {
            "data": {
                "test": "value"
            }
        }

        # Get data
        result = gql_utils.get_data(response)

        # Verify
        assert result == {"test": "value"}

    def test_get_data_without_data_field(self, gql_utils):
        """Test extracting data from a response without a data field."""
        # Response without data field
        response = {
            "test": "value"
        }

        # Get data
        result = gql_utils.get_data(response)

        # Verify
        assert result == {"test": "value"}

    def test_get_data_exception(self, gql_utils):
        """Test extracting data when an exception occurs."""
        # Create a mock that raises an exception when accessed
        response = MagicMock()
        type(response).__len__ = Mock(side_effect=Exception("Something went wrong"))

        # Get data
        result = gql_utils.get_data(response)

        # Verify
        assert result is None

    def test_get_errors_null_response(self, gql_utils):
        """Test extracting errors from a null response."""
        # Get errors from null response
        result = gql_utils.get_errors(None)

        # Verify
        assert result is None

    def test_get_errors_non_dict_response(self, gql_utils):
        """Test extracting errors from a non-dictionary response."""
        # Get errors from non-dict response
        result = gql_utils.get_errors("not a dict")

        # Verify
        assert result is None

    def test_get_errors_with_errors(self, gql_utils):
        """Test extracting errors from a response with errors."""
        # Response with errors
        response = {
            "errors": [
                {"message": "Error 1", "path": ["test"]},
                {"message": "Error 2", "path": ["test2"]}
            ]
        }

        # Get errors
        result = gql_utils.get_errors(response)

        # Verify
        assert result is not None
        assert len(result) == 2
        assert result[0]["message"] == "Error 1"
        assert result[1]["message"] == "Error 2"

    def test_get_errors_without_errors(self, gql_utils):
        """Test extracting errors from a response without errors."""
        # Response without errors
        response = {
            "data": {"test": "value"}
        }

        # Get errors
        result = gql_utils.get_errors(response)

        # Verify
        assert result is None

    def test_get_errors_exception(self, gql_utils):
        """Test extracting errors when an exception occurs."""
        # Create a mock that raises an exception
        response = MagicMock()
        response.get.side_effect = Exception("Something went wrong")

        # Get errors
        result = gql_utils.get_errors(response)

        # Verify
        assert result is None

    def test_build_mutation(self, gql_utils):
        """Test building a mutation string."""
        # Build mutation
        mutation = gql_utils.build_mutation(
            operation_name="CreateUser",
            input_variables={"name": "String!", "email": "String!"},
            return_fields=["id", "name", "email"]
        )

        # Verify structure
        assert "mutation CreateUser($name: String!, $email: String!)" in mutation
        assert "createUser(input: {name: $name, email: $email})" in mutation
        assert "id" in mutation
        assert "name" in mutation
        assert "email" in mutation

    def test_build_mutation_with_nested_fields(self, gql_utils):
        """Test building a mutation with nested return fields."""
        # Build mutation with nested fields
        mutation = gql_utils.build_mutation(
            operation_name="UpdateUser",
            input_variables={"id": "ID!", "profile": "ProfileInput"},
            return_fields=["id", "name"],
            nested_return_fields={"profile": ["avatar", "bio"]}
        )

        # Verify structure
        assert "mutation UpdateUser($id: ID!, $profile: ProfileInput)" in mutation
        assert "updateUser(input: {id: $id, profile: $profile})" in mutation
        assert "id" in mutation
        assert "name" in mutation
        assert "profile {" in mutation
        assert "avatar" in mutation
        assert "bio" in mutation

    def test_build_mutation_empty_name(self, gql_utils):
        """Test building a mutation with an empty operation name."""
        # Build mutation with empty name
        mutation = gql_utils.build_mutation(
            operation_name="",
            input_variables={"name": "String!"},
            return_fields=["id"]
        )

        # Verify
        assert mutation == ""

    def test_build_mutation_empty_variables(self, gql_utils):
        """Test building a mutation with empty input variables."""
        # Build mutation with empty variables
        mutation = gql_utils.build_mutation(
            operation_name="CreateUser",
            input_variables={},
            return_fields=["id"]
        )

        # Verify
        assert mutation == ""

    def test_build_mutation_empty_fields(self, gql_utils):
        """Test building a mutation with empty return fields."""
        # Build mutation with empty return fields
        mutation = gql_utils.build_mutation(
            operation_name="CreateUser",
            input_variables={"name": "String!"},
            return_fields=[]
        )

        # Verify
        assert mutation == ""

    def test_build_mutation_exception(self, gql_utils):
        """Test building a mutation when an exception occurs."""
        # Create input that will cause an exception
        input_variables = MagicMock()
        input_variables.items.side_effect = Exception("Something went wrong")

        # Build mutation
        mutation = gql_utils.build_mutation(
            operation_name="CreateUser",
            input_variables=input_variables,
            return_fields=["id"]
        )

        # Verify
        assert mutation == ""

    def test_execute_mutation(self, gql_utils):
        """Test executing a mutation."""
        # Patch execute_query to return a known result
        with patch.object(gql_utils, 'execute_query') as mock_execute_query:
            expected_result = {"createUser": {"id": "123", "name": "Test User"}}
            mock_execute_query.return_value = expected_result

            # Execute mutation
            mutation = "mutation CreateUser($name: String!) { createUser(input: {name: $name}) { id name } }"
            variables = {"name": "Test User"}
            result = gql_utils.execute_mutation(mutation, variables)

            # Verify
            assert result == expected_result
            mock_execute_query.assert_called_once_with(
                query_str=mutation,
                variables=variables,
                endpoint=None,
                headers=None,
                timeout=None,
                verify=True
            )

    def test_execute_mutation_with_endpoint(self, gql_utils):
        """Test executing a mutation with an endpoint."""
        # Patch execute_query to return a known result
        with patch.object(gql_utils, 'execute_query') as mock_execute_query:
            expected_result = {"createUser": {"id": "123", "name": "Test User"}}
            mock_execute_query.return_value = expected_result

            # Execute mutation with endpoint
            mutation = "mutation CreateUser($name: String!) { createUser(input: {name: $name}) { id name } }"
            variables = {"name": "Test User"}
            endpoint = "https://example.com/graphql"
            result = gql_utils.execute_mutation(mutation, variables, endpoint=endpoint)

            # Verify
            assert result == expected_result
            mock_execute_query.assert_called_once_with(
                query_str=mutation,
                variables=variables,
                endpoint=endpoint,
                headers=None,
                timeout=None,
                verify=True
            )

    def test_execute_mutation_empty_mutation(self, gql_utils):
        """Test executing a mutation with an empty mutation string."""
        # Execute mutation with empty string
        result = gql_utils.execute_mutation("", {"name": "Test User"})

        # Verify
        assert result is None

    def test_execute_mutation_empty_variables(self, gql_utils):
        """Test executing a mutation with empty variables."""
        # Execute mutation with empty variables
        mutation = "mutation CreateUser($name: String!) { createUser(input: {name: $name}) { id name } }"
        result = gql_utils.execute_mutation(mutation, {})

        # Verify
        assert result is None

    def test_execute_mutation_exception(self, gql_utils):
        """Test executing a mutation when an exception occurs."""
        # Patch execute_query to raise an exception
        with patch.object(gql_utils, 'execute_query') as mock_execute_query:
            mock_execute_query.side_effect = Exception("Something went wrong")

            # Execute mutation
            mutation = "mutation CreateUser($name: String!) { createUser(input: {name: $name}) { id name } }"
            variables = {"name": "Test User"}
            result = gql_utils.execute_mutation(mutation, variables)

            # Verify
            assert result is None
            mock_execute_query.assert_called_once()

    def test_build_fragment(self, gql_utils):
        """Test building a GraphQL fragment."""
        # Build fragment
        fragment = gql_utils.build_fragment(
            fragment_name="UserFields",
            type_name="User",
            fields=["id", "name", "email"]
        )

        # Verify structure
        assert "fragment UserFields on User {" in fragment
        assert "id" in fragment
        assert "name" in fragment
        assert "email" in fragment

    def test_build_fragment_with_nested_fields(self, gql_utils):
        """Test building a fragment with nested fields."""
        # Build fragment with nested fields
        fragment = gql_utils.build_fragment(
            fragment_name="UserWithPosts",
            type_name="User",
            fields=["id", "name"],
            nested_fields={"posts": ["id", "title", "content"]}
        )

        # Verify structure
        assert "fragment UserWithPosts on User {" in fragment
        assert "id" in fragment
        assert "name" in fragment
        assert "posts {" in fragment
        assert "id" in fragment
        assert "title" in fragment

    def test_build_fragment_empty_name(self, gql_utils):
        """Test building a fragment with an empty name."""
        # Build fragment with empty name
        fragment = gql_utils.build_fragment(
            fragment_name="",
            type_name="User",
            fields=["id", "name"]
        )

        # Verify
        assert fragment == ""

    def test_build_fragment_empty_type(self, gql_utils):
        """Test building a fragment with an empty type name."""
        # Build fragment with empty type
        fragment = gql_utils.build_fragment(
            fragment_name="UserFields",
            type_name="",
            fields=["id", "name"]
        )

        # Verify
        assert fragment == ""

    def test_build_fragment_empty_fields(self, gql_utils):
        """Test building a fragment with empty fields."""
        # Build fragment with empty fields
        fragment = gql_utils.build_fragment(
            fragment_name="UserFields",
            type_name="User",
            fields=[]
        )

        # Verify
        assert fragment == ""

    def test_build_fragment_exception(self, gql_utils):
        """Test building a fragment when an exception occurs."""
        # Create fields that will cause an exception
        fields = MagicMock()
        fields.__iter__.side_effect = Exception("Something went wrong")

        # Build fragment
        fragment = gql_utils.build_fragment(
            fragment_name="UserFields",
            type_name="User",
            fields=fields
        )

        # Verify
        assert fragment == ""

    def test_integration_workflow(self, gql_utils):
        """Test a complete workflow with mocks."""
        # Setup mocks
        with patch('requests.get') as mock_get, \
                patch.object(Client, 'execute') as mock_execute:
            # Mock the GET request to validate endpoint
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            # Mock the client execute
            expected_data = {
                "user": {
                    "id": "123",
                    "name": "Test User",
                    "email": "test@example.com"
                }
            }
            mock_execute.return_value = expected_data

            # Workflow:
            # 1. Create client
            result = gql_utils.create_client("https://example.com/graphql")
            assert result is True

            # 2. Build query
            query = """
            query GetUser($id: ID!) {
              user(id: $id) {
                id
                name
                email
              }
            }
            """

            # 3. Execute query with variables
            variables = {"id": "123"}
            query_result = gql_utils.execute_query(query, variables)

            # 4. Process data
            data = gql_utils.get_data(query_result)

            # Verify workflow results
            assert query_result == expected_data
            assert data == expected_data
            assert "user" in data
            assert data["user"]["id"] == "123"
            assert data["user"]["name"] == "Test User"
            assert data["user"]["email"] == "test@example.com"

    def test_mutation_workflow(self, gql_utils):
        """Test a complete mutation workflow with mocks."""
        # Setup mocks
        with patch('requests.get') as mock_get, \
                patch.object(Client, 'execute') as mock_execute:
            # Mock the GET request to validate endpoint
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            # Mock the client execute
            expected_data = {
                "createUser": {
                    "id": "123",
                    "name": "New User",
                    "email": "new@example.com"
                }
            }
            mock_execute.return_value = expected_data

            # Workflow:
            # 1. Create client
            result = gql_utils.create_client("https://example.com/graphql")
            assert result is True

            # 2. Build mutation
            mutation = gql_utils.build_mutation(
                operation_name="CreateUser",
                input_variables={"name": "String!", "email": "String!"},
                return_fields=["id", "name", "email"]
            )

            # Verify mutation structure
            assert "mutation CreateUser($name: String!, $email: String!)" in mutation
            assert "createUser(input: {name: $name, email: $email})" in mutation

            # 3. Execute mutation
            variables = {"name": "New User", "email": "new@example.com"}
            mutation_result = gql_utils.execute_mutation(mutation, variables)

            # 4. Process result
            data = gql_utils.get_data(mutation_result)

            # Verify workflow results
            assert mutation_result == expected_data
            assert data == expected_data
            assert "createUser" in data
            assert data["createUser"]["id"] == "123"
            assert data["createUser"]["name"] == "New User"
            assert data["createUser"]["email"] == "new@example.com"

    def test_error_handling_workflow(self, gql_utils):
        """Test an error handling workflow with mocks."""
        # Setup mocks for raw request
        with patch('cafex_api.request_builder.RequestBuilder.call_request') as mock_call_request:
            # Mock response with GraphQL errors
            mock_response = Mock()
            mock_response.json.return_value = {
                "errors": [
                    {
                        "message": "Cannot query field 'invalid' on type 'Query'",
                        "locations": [{"line": 2, "column": 3}],
                        "path": ["invalid"]
                    }
                ]
            }
            mock_call_request.return_value = mock_response

            # Execute invalid query
            query = "query { invalid }"
            result = gql_utils.execute_query_with_raw_request(
                query,
                "https://example.com/graphql"
            )

            # Get errors
            errors = gql_utils.get_errors(result)

            # Verify workflow results
            assert result is not None
            assert "errors" in result
            assert errors is not None
            assert len(errors) == 1
            assert "Cannot query field 'invalid'" in errors[0]["message"]

    def test_fragment_in_query_workflow(self, gql_utils):
        """Test using a fragment in a query workflow."""
        # Setup mocks
        with patch('requests.get') as mock_get, \
                patch.object(Client, 'execute') as mock_execute:
            # Mock the GET request
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            # Mock the client execute
            expected_data = {
                "user": {
                    "id": "123",
                    "name": "Test User",
                    "email": "test@example.com",
                    "posts": [
                        {
                            "id": "1",
                            "title": "First Post",
                            "content": "Hello world"
                        }
                    ]
                }
            }
            mock_execute.return_value = expected_data

            # Create client
            result = gql_utils.create_client("https://example.com/graphql")
            assert result is True

            # Build fragment
            fragment = gql_utils.build_fragment(
                fragment_name="PostFields",
                type_name="Post",
                fields=["id", "title", "content"]
            )

            # Verify fragment structure
            assert "fragment PostFields on Post {" in fragment

            # Create query with fragment
            query = f"""
            {fragment}

            query GetUserWithPosts($id: ID!) {{
              user(id: $id) {{
                id
                name
                email
                posts {{
                  ...PostFields
                }}
              }}
            }}
            """

            # Execute query
            variables = {"id": "123"}
            query_result = gql_utils.execute_query(query, variables)

            # Process data
            data = gql_utils.get_data(query_result)

            # Verify workflow results
            assert query_result == expected_data
            assert data == expected_data
            assert "user" in data
            assert "posts" in data["user"]
            assert data["user"]["posts"][0]["id"] == "1"
            assert data["user"]["posts"][0]["title"] == "First Post"

    def test_complex_nested_query_workflow(self, gql_utils):
        """Test a workflow with complex nested data structures."""
        # Setup mocks
        with patch('requests.get') as mock_get, \
                patch.object(Client, 'execute') as mock_execute:
            # Mock the GET request
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            # Mock the client execute with complex nested data
            expected_data = {
                "company": {
                    "id": "1",
                    "name": "Acme Inc",
                    "departments": [
                        {
                            "id": "1",
                            "name": "Engineering",
                            "employees": [
                                {
                                    "id": "1",
                                    "name": "John",
                                    "role": "Developer",
                                    "projects": [
                                        {"id": "1", "name": "Project A"},
                                        {"id": "2", "name": "Project B"}
                                    ]
                                },
                                {
                                    "id": "2",
                                    "name": "Jane",
                                    "role": "Designer",
                                    "projects": [
                                        {"id": "1", "name": "Project A"}
                                    ]
                                }
                            ]
                        },
                        {
                            "id": "2",
                            "name": "Marketing",
                            "employees": [
                                {
                                    "id": "3",
                                    "name": "Bob",
                                    "role": "Manager",
                                    "projects": []
                                }
                            ]
                        }
                    ]
                }
            }
            mock_execute.return_value = expected_data

            # Create client
            result = gql_utils.create_client("https://example.com/graphql")
            assert result is True

            # Execute query with complex structure
            query = """
            query {
              company(id: "1") {
                id
                name
                departments {
                  id
                  name
                  employees {
                    id
                    name
                    role
                    projects {
                      id
                      name
                    }
                  }
                }
              }
            }
            """

            query_result = gql_utils.execute_query(query)

            # Process data
            data = gql_utils.get_data(query_result)

            # Verify the complex structure
            assert query_result == expected_data
            assert data == expected_data
            assert "company" in data
            assert "departments" in data["company"]
            assert len(data["company"]["departments"]) == 2
            assert "employees" in data["company"]["departments"][0]
            assert len(data["company"]["departments"][0]["employees"]) == 2
            assert "projects" in data["company"]["departments"][0]["employees"][0]
            assert len(data["company"]["departments"][0]["employees"][0]["projects"]) == 2