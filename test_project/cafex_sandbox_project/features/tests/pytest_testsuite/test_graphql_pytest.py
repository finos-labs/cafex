"""
Unit tests for the GraphQLUtils class using real GraphQL APIs.

This module contains tests that verify the functionality of the GraphQLUtils class
by making real API calls to public GraphQL endpoints with SSL verification disabled
for corporate environments.
"""

import pytest
import urllib3
from cafex_api.graphql_utils import GraphQLUtils

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class TestGraphQLUtils:
    """Test suite for the GraphQLUtils class."""

    COUNTRIES_API = "https://countries.trevorblades.com/"
    RICK_AND_MORTY_API = "https://rickandmortyapi.com/graphql"

    @pytest.fixture
    def gql_utils(self):
        """Create a GraphQLUtils instance for testing."""
        return GraphQLUtils()

    def test_create_client(self, gql_utils):
        """Test creating a GraphQL client."""
        # Test creating a client with a valid endpoint and SSL verification disabled
        result = gql_utils.create_client(self.COUNTRIES_API, verify=False)
        assert result is True
        assert gql_utils.client is not None

        # Test with custom headers
        headers = {"X-Test-Header": "test-value"}
        result = gql_utils.create_client(self.COUNTRIES_API, headers=headers, verify=False)
        assert result is True

        # Test with timeout
        result = gql_utils.create_client(self.COUNTRIES_API, timeout=30, verify=False)
        assert result is True

    def test_create_client_invalid_endpoint(self, gql_utils):
        """Test creating a client with an invalid endpoint."""
        # Test with empty endpoint
        result = gql_utils.create_client("", verify=False)
        assert result is False

        # Test with invalid URL
        result = gql_utils.create_client("https://invalid-graphql-endpoint.example", verify=False)
        assert result is False

    def test_execute_query_countries(self, gql_utils):
        """Test executing a query against the Countries API."""
        # Create client with SSL verification disabled
        gql_utils.create_client(self.COUNTRIES_API, verify=False)

        # Simple query to get all country codes
        query = """
        query {
          countries {
            code
            name
          }
        }
        """

        # Execute query
        result = gql_utils.execute_query(query)

        # Verify response
        assert result is not None
        assert "countries" in result
        assert isinstance(result["countries"], list)
        assert len(result["countries"]) > 0
        assert "code" in result["countries"][0]
        assert "name" in result["countries"][0]

    def test_execute_query_with_variables(self, gql_utils):
        """Test executing a query with variables."""
        # Create client with SSL verification disabled
        gql_utils.create_client(self.COUNTRIES_API, verify=False)

        # Query for a specific country by code
        query = """
        query GetCountry($code: ID!) {
          country(code: $code) {
            code
            name
            capital
            currency
            languages {
              name
            }
          }
        }
        """

        # Variables
        variables = {"code": "US"}

        # Execute query
        result = gql_utils.execute_query(query, variables)

        # Verify response
        assert result is not None
        assert "country" in result
        assert result["country"]["code"] == "US"
        assert result["country"]["name"] == "United States"
        assert "capital" in result["country"]
        assert "currency" in result["country"]
        assert "languages" in result["country"]

    def test_execute_query_one_time_endpoint(self, gql_utils):
        """Test executing a query with a one-time endpoint."""
        # Query for countries
        query = """
        query {
          countries {
            code
            name
            continent {
              name
            }
          }
        }
        """

        # Execute query with endpoint and SSL verification disabled
        result = gql_utils.execute_query(query, endpoint=self.COUNTRIES_API, verify=False)

        # Verify response
        assert result is not None
        assert "countries" in result
        assert isinstance(result["countries"], list)
        assert len(result["countries"]) > 0
        assert "code" in result["countries"][0]
        assert "name" in result["countries"][0]
        assert "continent" in result["countries"][0]

    def test_execute_query_no_client(self, gql_utils):
        """Test executing a query without initializing a client."""
        # Reset client
        gql_utils.client = None

        # Simple query
        query = """
        query {
          countries {
            code
          }
        }
        """

        # Execute query without endpoint or client
        result = gql_utils.execute_query(query)

        # Should fail
        assert result is None

    def test_execute_query_invalid_query(self, gql_utils):
        """Test executing an invalid query."""
        # Create client with SSL verification disabled
        gql_utils.create_client(self.COUNTRIES_API, verify=False)

        # Invalid query
        query = """
        query {
          invalidField {
            something
          }
        }
        """

        # Execute query
        result = gql_utils.execute_query(query)

        # Should return None due to GraphQL error
        assert result is None

    def test_execute_query_with_raw_request(self, gql_utils):
        """Test executing a query using raw HTTP request."""
        # Query for Rick and Morty characters
        query = """
        query {
          characters(page: 1) {
            results {
              id
              name
              species
            }
          }
        }
        """

        # Execute with raw request and SSL verification disabled
        result = gql_utils.execute_query_with_raw_request(query, self.RICK_AND_MORTY_API, verify=False)

        # Verify response
        assert result is not None
        assert "data" in result
        data = result["data"]
        assert "characters" in data
        assert "results" in data["characters"]
        assert isinstance(data["characters"]["results"], list)
        assert len(data["characters"]["results"]) > 0

        # Check character data
        character = data["characters"]["results"][0]
        assert "id" in character
        assert "name" in character
        assert "species" in character

    def test_execute_raw_with_variables(self, gql_utils):
        """Test executing a raw request with variables."""
        # Query for specific character
        query = """
        query GetCharacter($id: ID!) {
          character(id: $id) {
            id
            name
            species
            status
            gender
          }
        }
        """

        # Variables
        variables = {"id": "1"}  # Rick Sanchez

        # Execute with raw request and SSL verification disabled
        result = gql_utils.execute_query_with_raw_request(
            query,
            self.RICK_AND_MORTY_API,
            variables=variables,
            verify=False
        )

        # Verify response
        assert result is not None
        assert "data" in result
        data = result["data"]
        assert "character" in data
        assert data["character"]["id"] == "1"
        assert data["character"]["name"] == "Rick Sanchez"

    def test_execute_raw_invalid_endpoint(self, gql_utils):
        """Test executing a raw request with invalid endpoint."""
        query = """
        query {
          test {
            id
          }
        }
        """

        # Execute with empty endpoint
        result = gql_utils.execute_query_with_raw_request(query, "", verify=False)
        assert result is None

        # Execute with invalid endpoint
        result = gql_utils.execute_query_with_raw_request(query, "https://invalid-api.example", verify=False)
        assert result is None

    def test_execute_raw_invalid_query(self, gql_utils):
        """Test executing an invalid query with raw request."""
        # Invalid query
        query = """
        query {
          invalidField {
            something
          }
        }
        """

        # Execute with raw request and SSL verification disabled
        result = gql_utils.execute_query_with_raw_request(query, self.RICK_AND_MORTY_API, verify=False)

        # Should return response with errors
        assert result is not None
        assert "errors" in result
        assert len(result["errors"]) > 0

    def test_get_data(self, gql_utils):
        """Test extracting data from a response."""
        # Create a test response with data
        response = {
            "data": {
                "test": "value"
            }
        }

        # Extract data
        data = gql_utils.get_data(response)

        # Verify
        assert data is not None
        assert data == {"test": "value"}

        # Test with direct data (GQL client response)
        direct_response = {"test": "value"}
        data = gql_utils.get_data(direct_response)
        assert data == {"test": "value"}

    def test_get_data_invalid(self, gql_utils):
        """Test extracting data from invalid responses."""
        # Test with None
        data = gql_utils.get_data(None)
        assert data is None

        # Test with non-dict
        data = gql_utils.get_data("not a dict")
        assert data is None

        # Test with empty dict
        data = gql_utils.get_data({})
        assert data == {}

    def test_get_errors(self, gql_utils):
        """Test extracting errors from a response."""
        # Create a test response with errors
        response = {
            "errors": [
                {"message": "Error 1", "path": ["test"]},
                {"message": "Error 2", "path": ["test2"]}
            ]
        }

        # Extract errors
        errors = gql_utils.get_errors(response)

        # Verify
        assert errors is not None
        assert len(errors) == 2
        assert errors[0]["message"] == "Error 1"
        assert errors[1]["message"] == "Error 2"

    def test_get_errors_no_errors(self, gql_utils):
        """Test extracting errors when none exist."""
        # Response with no errors
        response = {
            "data": {"test": "value"}
        }

        # Extract errors
        errors = gql_utils.get_errors(response)

        # Should be None
        assert errors is None

    def test_get_errors_invalid(self, gql_utils):
        """Test extracting errors from invalid responses."""
        # Test with None
        errors = gql_utils.get_errors(None)
        assert errors is None

        # Test with non-dict
        errors = gql_utils.get_errors("not a dict")
        assert errors is None

    def test_real_api_workflow(self, gql_utils):
        """Test a complete workflow with a real API."""
        gql_utils.create_client(self.COUNTRIES_API, verify=False)

        # Query for countries with variables
        query = """
        query GetCountries($filter: CountryFilterInput) {
          countries(filter: $filter) {
            code
            name
            capital
            currency
            continent {
              name
            }
            languages {
              name
              native
            }
          }
        }
        """

        variables = {"filter": {"continent": {"eq": "EU"}}}

        # Execute query
        result = gql_utils.execute_query(query, variables)

        # Extract data
        data = gql_utils.get_data(result)

        # Verify
        assert data is not None
        assert "countries" in data
        assert isinstance(data["countries"], list)
        assert len(data["countries"]) > 0  # Should have multiple European countries

        # Get errors (should be None)
        errors = gql_utils.get_errors(result)
        assert errors is None

        # Check country data
        if data["countries"]:
            country = data["countries"][0]
            assert "code" in country
            assert "name" in country
            assert "capital" in country
            assert "continent" in country
            assert "name" in country["continent"]
            assert country["continent"]["name"] == "Europe"  # Verify filter worked

    def test_graphql_workflow_with_filtering(self, gql_utils):
        """Test workflow with filtering data from the Countries API."""
        # Create client with SSL verification disabled
        gql_utils.create_client(self.COUNTRIES_API, verify=False)

        # Query for filtering European countries
        query = """
        query GetEuropeanCountries {
          continent(code: "EU") {
            name
            countries {
              code
              name
              capital
              currency
              languages {
                name
                native
              }
            }
          }
        }
        """

        # Execute query
        result = gql_utils.execute_query(query)

        # Verify
        assert result is not None
        assert "continent" in result
        assert "name" in result["continent"]
        assert result["continent"]["name"] == "Europe"
        assert "countries" in result["continent"]
        assert isinstance(result["continent"]["countries"], list)
        assert len(result["continent"]["countries"]) > 0

        # If there are countries, check the structure
        countries = result["continent"]["countries"]
        if countries:
            country = countries[0]
            assert "code" in country
            assert "name" in country
            assert "capital" in country
            assert "currency" in country
            assert "languages" in country

    def test_error_handling_workflow(self, gql_utils):
        """Test a workflow that includes error handling."""
        # Create client for the Countries API with SSL verification disabled
        gql_utils.create_client(self.COUNTRIES_API, verify=False)

        # Invalid query (misspelled field)
        query = """
        query {
          countries {
            code
            nmae  # Misspelled "name"
          }
        }
        """

        # Execute the invalid query using raw request to get error response
        result = gql_utils.execute_query_with_raw_request(query, self.COUNTRIES_API, verify=False)

        # Should have errors
        assert result is not None
        assert "errors" in result

        # Extract errors
        errors = gql_utils.get_errors(result)
        assert errors is not None
        assert len(errors) > 0

        # Verify error message contains information about the misspelled field
        error_msg = errors[0].get("message", "")
        assert "nmae" in error_msg or "name" in error_msg

        # There should be no data or it should be null
        data = gql_utils.get_data(result)
        if data:
            assert data.get("countries") is None

    def test_verify_parameter_handling(self, gql_utils):
        """Test that the verify parameter is correctly passed to the transport."""
        # Test with verify=False - this should always work
        result = gql_utils.create_client(self.COUNTRIES_API, verify=False)
        assert result is True

        # Test simple query
        query = """
        query {
          countries {
            code
            name
          }
        }
        """

        # Execute query with one-time endpoint using verify=False
        result = gql_utils.execute_query(query, endpoint=self.COUNTRIES_API, verify=False)
        assert result is not None

        # Raw request with verify=False
        result = gql_utils.execute_query_with_raw_request(query, self.COUNTRIES_API, verify=False)
        assert result is not None
        assert "data" in result

    def test_real_mutation_graphqlzero(self, gql_utils):
        """Test executing a real mutation using GraphQLZero API."""
        graphqlzero_api = "https://graphqlzero.almansi.me/api"

        # Create client
        gql_utils.create_client(graphqlzero_api, verify=False)

        # Build a mutation to create a post
        mutation_str = """
        mutation CreatePost($input: CreatePostInput!) {
          createPost(input: $input) {
            id
            title
            body
          }
        }
        """

        # Variables for the mutation
        variables = {
            "input": {
                "title": "Test Post",
                "body": "This is a test post created via GraphQL mutation"
            }
        }

        # Execute the mutation
        result = gql_utils.execute_mutation(mutation_str, variables)

        # GraphQLZero simulates mutations but doesn't actually persist data
        assert result is not None
        assert "createPost" in result
        assert "id" in result["createPost"]
        assert result["createPost"]["title"] == "Test Post"
        assert result["createPost"]["body"] == "This is a test post created via GraphQL mutation"

    def test_update_mutation_graphqlzero(self, gql_utils):
        """Test executing an update mutation using GraphQLZero API."""
        graphqlzero_api = "https://graphqlzero.almansi.me/api"

        # Create client
        gql_utils.create_client(graphqlzero_api, verify=False)

        # Build a mutation to update a post
        # Using our build_mutation helper
        mutation = gql_utils.build_mutation(
            operation_name="UpdatePost",
            input_variables={"id": "ID!", "input": "UpdatePostInput!"},
            return_fields=["id", "title", "body"]
        )

        # Convert the field name to match GraphQLZero API
        # (their mutation field is updatePost(id:, input:) not updatePost(input: {id:, input:}))
        mutation = mutation.replace(
            "updatePost(input: {id: $id, input: $input})",
            "updatePost(id: $id, input: $input)"
        )

        # Variables for the mutation - update post with ID 1
        variables = {
            "id": "1",
            "input": {
                "title": "Updated Title",
                "body": "This post was updated via GraphQL mutation"
            }
        }

        # Execute the mutation
        result = gql_utils.execute_mutation(mutation, variables)

        # GraphQLZero simulates mutations but doesn't actually persist data
        assert result is not None
        assert "updatePost" in result
        assert result["updatePost"]["id"] == "1"
        assert result["updatePost"]["title"] == "Updated Title"
        assert result["updatePost"]["body"] == "This post was updated via GraphQL mutation"

    def test_delete_mutation_graphqlzero(self, gql_utils):
        """Test executing a delete mutation using GraphQLZero API."""
        graphqlzero_api = "https://graphqlzero.almansi.me/api"

        # Create client
        gql_utils.create_client(graphqlzero_api, verify=False)

        # Delete mutation is simpler, doesn't use an input object
        mutation_str = """
        mutation DeletePost($id: ID!) {
          deletePost(id: $id)
        }
        """

        # Variables for the mutation - delete post with ID 1
        variables = {"id": "1"}

        # Execute the mutation
        result = gql_utils.execute_mutation(mutation_str, variables)

        # GraphQLZero returns a boolean for delete operations
        assert result is not None
        assert "deletePost" in result
        assert result["deletePost"] is True  # Should be successful

    def test_complex_mutation_with_nested_data(self, gql_utils):
        """Test a complex mutation with nested data structure."""
        graphqlzero_api = "https://graphqlzero.almansi.me/api"

        # Create client
        gql_utils.create_client(graphqlzero_api, verify=False)

        # First query for a user to get valid data for our mutation
        query_str = """
        query {
          user(id: "1") {
            id
            name
            username
            email
            address {
              street
              suite
              city
              zipcode
            }
            phone
            website
            company {
              name
              catchPhrase
              bs
            }
          }
        }
        """

        # Get user data
        user_result = gql_utils.execute_query(query_str)
        assert user_result is not None
        assert "user" in user_result

        # Now use this data to simulate updating a complex nested object
        user_data = user_result["user"]

        # Build a mutation to update a user with nested fields
        mutation_str = """
        mutation UpdateUser($id: ID!, $input: UpdateUserInput!) {
          updateUser(id: $id, input: $input) {
            id
            name
            email
            address {
              street
              city
            }
            company {
              name
            }
          }
        }
        """

        # Modify some values for the update
        variables = {
            "id": "1",
            "input": {
                "name": "Updated " + user_data["name"],
                "email": "updated_" + user_data["email"],
                "address": {
                    "street": "New " + user_data["address"]["street"],
                    "city": user_data["address"]["city"]
                },
                "company": {
                    "name": "New " + user_data["company"]["name"]
                }
            }
        }

        # Execute the mutation
        result = gql_utils.execute_mutation(mutation_str, variables)

        # Verify the complex nested structure in the response
        assert result is not None
        assert "updateUser" in result
        assert result["updateUser"]["id"] == "1"
        assert result["updateUser"]["name"] == "Updated " + user_data["name"]
        assert result["updateUser"]["email"] == "updated_" + user_data["email"]
        assert result["updateUser"]["address"]["street"] == "New " + user_data["address"]["street"]
        assert result["updateUser"]["company"]["name"] == "New " + user_data["company"]["name"]

    def test_mutation_error_handling(self, gql_utils):
        """Test how the GraphQL utils handle mutation errors."""
        graphqlzero_api = "https://graphqlzero.almansi.me/api"

        # Create client
        gql_utils.create_client(graphqlzero_api, verify=False)

        # Create an invalid mutation that will cause an error
        mutation_str = """
        mutation InvalidMutation {
          nonExistentMutation {
            id
          }
        }
        """

        # Execute with raw request to get error details
        result = gql_utils.execute_query_with_raw_request(
            mutation_str,
            graphqlzero_api,
            verify=False
        )

        # Should return response with errors
        assert result is not None
        assert "errors" in result
        assert len(result["errors"]) > 0

        # Extract errors using our utility
        errors = gql_utils.get_errors(result)
        assert errors is not None
        assert len(errors) > 0

        # Check the error contains information about the invalid field
        error_message = errors[0].get("message", "")
        assert "nonExistentMutation" in error_message

    def test_mutation_variables_validation(self, gql_utils):
        """Test validation of mutation variables."""
        graphqlzero_api = "https://graphqlzero.almansi.me/api"

        # Create client
        gql_utils.create_client(graphqlzero_api, verify=False)

        # Valid mutation but with invalid variable type
        mutation_str = """
        mutation CreatePost($input: CreatePostInput!) {
          createPost(input: $input) {
            id
            title
          }
        }
        """

        # Invalid variables - should be an object but we're passing a string
        variables = {"input": "not an object"}

        # Execute with raw request to get error details
        result = gql_utils.execute_query_with_raw_request(
            mutation_str,
            graphqlzero_api,
            variables=variables,
            verify=False
        )

        # Should return response with errors
        assert result is not None
        assert "errors" in result

        # Extract errors
        errors = gql_utils.get_errors(result)
        assert errors is not None
        assert len(errors) > 0

        # Error should be about the variable type
        error_message = errors[0].get("message", "")
        assert "input" in error_message.lower()