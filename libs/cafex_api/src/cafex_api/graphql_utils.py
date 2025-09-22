"""
Module providing GraphQL utilities for API testing in the framework.

This module wraps established GraphQL libraries and integrates them with the framework for GraphQL
API testing.
"""

from typing import Any, Dict, List, Optional

import requests
from gql import Client
from gql import gql as gql_lib
from gql.transport.requests import RequestsHTTPTransport

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.utils.exceptions import CoreExceptions

from .api_exceptions import APIExceptions
from .request_builder import RequestBuilder


class GraphQLUtils:
    """
    Utility class for GraphQL API testing that wraps the GQL library.

    This class provides methods to build GraphQL queries and mutations,
    execute requests against GraphQL endpoints, and process the responses,
    while integrating with CAFEX's exception handling and reporting.

    Examples:
        >>> # Initialize GraphQL utilities
        >>> gql_utils = GraphQLUtils()
        >>>
        >>> # Create a client for a specific endpoint
        >>> gql_utils.create_client(
        ...     "https://api.example.com/graphql",
        ...     headers={"Authorization": "Bearer token123"}
        ... )
        >>>
        >>> # Execute a query
        >>> query = '''
        ... query GetUsers {
        ...   users {
        ...     id
        ...     name
        ...     email
        ...   }
        ... }
        ... '''
        >>> response = gql_utils.execute_query(query)
        >>>
        >>> # Process the response
        >>> data = gql_utils.get_data(response)
        >>> users = data.get("users", [])
        >>> print(f"Found {len(users)} users")
    """

    def __init__(self):
        self.logger = CoreLogger(name=__name__).get_logger()
        self.__exceptions_generic = CoreExceptions()
        self.__exceptions_services = APIExceptions()
        self.request_builder = RequestBuilder()
        self.client = None

    def create_client(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        verify: bool = True,
    ) -> bool:
        """
        Create a GraphQL client for a specific endpoint.

        Args:
            endpoint: The GraphQL API endpoint URL
            headers: HTTP headers to include with requests
            timeout: Request timeout in seconds
            verify: Whether to verify SSL certificates (default: True)

        Returns:
            True if client creation was successful, False otherwise

        Examples:
            >>> gql_utils = GraphQLUtils()
            >>>
            >>> # Create client with default settings
            >>> result = gql_utils.create_client("https://api.example.com/graphql")
            >>>
            >>> # Create client with SSL verification disabled
            >>> result_no_ssl = gql_utils.create_client(
            ...     "https://api.example.com/graphql",
            ...     verify=False
            ... )
            >>>
            >>> # Create client with authentication
            >>> result_auth = gql_utils.create_client(
            ...     "https://api.example.com/graphql",
            ...     headers={"Authorization": "Bearer token123"}
            ... )
            >>>
            >>> # Create client with timeout
            >>> result_var = gql_utils.create_client(
            ...     "https://api.example.com/graphql",
            ...     timeout=30
            ... )
        """
        try:
            if not endpoint:
                self.__exceptions_services.raise_null_value(
                    "GraphQL endpoint cannot be null", fail_test=False
                )
                return False

            if headers is None:
                headers = {}

            if "Content-Type" not in headers:
                headers["Content-Type"] = "application/json"

            if "Accept" not in headers:
                headers["Accept"] = "application/json"

            # Try to validate the endpoint exists before creating the client
            try:
                response = requests.get(
                    endpoint, headers=headers, timeout=timeout if timeout else 5, verify=verify
                )

                if response is None:
                    return False

            except (requests.RequestException, ConnectionError):
                # Connection error - definitely not a valid endpoint
                return False

            transport_kwargs = {"headers": headers, "verify": verify}

            if timeout is not None:
                transport_kwargs["timeout"] = timeout

            transport = RequestsHTTPTransport(url=endpoint, **transport_kwargs)

            self.client = Client(transport=transport, fetch_schema_from_transport=False)

            return True

        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error creating GraphQL client: {str(e)}", fail_test=False
            )
            return False

    def execute_query(
        self,
        query_str: str,
        variables: Optional[Dict[str, Any]] = None,
        endpoint: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        verify: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a GraphQL query against an endpoint.

        If an endpoint is provided, a new client will be created for that endpoint.
        Otherwise, the previously created client will be used.

        Args:
            query_str: The GraphQL query string
            variables: Dictionary of variables for the query
            endpoint: The GraphQL API endpoint URL (optional if client already exists)
            headers: HTTP headers to include with the request (optional)
            timeout: Request timeout in seconds (optional)
            verify: Whether to verify SSL certificates (default: True)

        Returns:
            The JSON response as a dictionary, or None if the request fails

        Examples:
            >>> gql_utils = GraphQLUtils()
            >>>
            >>> # Execute a query with an existing client
            >>> gql_utils.create_client("https://api.example.com/graphql")
            >>> query = '''
            ... query GetUsers {
            ...   users {
            ...     id
            ...     name
            ...     email
            ...   }
            ... }
            ... '''
            >>> result_query = gql_utils.execute_query(query)
            >>>
            >>> # Execute a query with SSL verification disabled
            >>> result_no_ssl = gql_utils.execute_query(
            ...     query,
            ...     endpoint="https://api.example.com/graphql",
            ...     verify=False
            ... )
            >>>
            >>> # Execute a query with variables
            >>> query_with_vars = '''
            ... query GetUser($id: ID!) {
            ...   user(id: $id) {
            ...     id
            ...     name
            ...     email
            ...     role
            ...   }
            ... }
            ... '''
            >>> variables_gql = {"id": "user-123"}
            >>> result_var = gql_utils.execute_query(query_with_vars, variables_gql)
            >>>
            >>> # Execute a query with a one-time endpoint
            >>> result_endpoint = gql_utils.execute_query(
            ...     query,
            ...     endpoint="https://api.example.com/graphql"
            ... )
            >>>
            >>> # Execute a query with custom headers
            >>> result_custom = gql_utils.execute_query(
            ...     query,
            ...     headers={"Authorization": "Bearer token123"}
            ... )
        """
        try:
            if not query_str:
                self.__exceptions_services.raise_null_value(
                    "GraphQL query cannot be null", fail_test=False
                )
                return None

            # Create a new client if endpoint is provided
            if endpoint:
                client_created = self.create_client(endpoint, headers, timeout, verify)
                if not client_created:
                    return None

            if not self.client:
                self.__exceptions_services.raise_null_value(
                    "GraphQL client not initialized. Call create_client() first or provide an endpoint.",
                    fail_test=False,
                )
                return None

            query_obj = gql_lib(query_str)

            try:
                result = self.client.execute(query_obj, variable_values=variables)
                return result
            except Exception as e:
                self.__exceptions_services.raise_invalid_response_format(
                    f"Error executing GraphQL query: {str(e)}", fail_test=False
                )
                return None

        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error in GraphQL execution: {str(e)}", fail_test=False
            )
            return None

    def execute_query_with_raw_request(
        self,
        query_str: str,
        endpoint: str,
        variables: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        verify: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a GraphQL query using direct HTTP requests instead of the GQL client.

        This method is useful for cases where you need more control over the HTTP request
        or when troubleshooting issues with the GQL client.

        Args:
            query_str: The GraphQL query string
            endpoint: The GraphQL API endpoint URL
            variables: Dictionary of variables for the query
            headers: HTTP headers to include with the request
            timeout: Request timeout in seconds
            verify: Whether to verify SSL certificates (default: True)

        Returns:
            The JSON response as a dictionary, or None if the request fails

        Examples:
            >>> gql_utils = GraphQLUtils()
            >>>
            >>> # Execute a simple query with raw request
            >>> query = '''
            ... query GetUsers {
            ...   users {
            ...     id
            ...     name
            ...     email
            ...   }
            ... }
            ... '''
            >>> result = gql_utils.execute_query_with_raw_request(
            ...     query,
            ...     "https://api.example.com/graphql"
            ... )
            >>>
            >>> # Execute with SSL verification disabled
            >>> result_no_ssl = gql_utils.execute_query_with_raw_request(
            ...     query,
            ...     "https://api.example.com/graphql",
            ...     verify=False
            ... )
            >>>
            >>> # Execute a query with variables
            >>> query_with_vars = '''
            ... query GetUser($id: ID!) {
            ...   user(id: $id) {
            ...     id
            ...     name
            ...     email
            ...   }
            ... }
            ... '''
            >>> variables_gql = {"id": "user-123"}
            >>> result_var = gql_utils.execute_query_with_raw_request(
            ...     query_with_vars,
            ...     "https://api.example.com/graphql",
            ...     variables=variables_gql
            ... )
            >>>
            >>> # Execute with authentication headers
            >>> auth_headers = {"Authorization": "Bearer token123"}
            >>> result_auth = gql_utils.execute_query_with_raw_request(
            ...     query,
            ...     "https://api.example.com/graphql",
            ...     headers=auth_headers
            ... )
            >>>
            >>> # Execute with a timeout
            >>> result_timeout = gql_utils.execute_query_with_raw_request(
            ...     query,
            ...     "https://api.example.com/graphql",
            ...     timeout=30
            ... )
        """
        try:
            if not endpoint:
                self.__exceptions_services.raise_null_value(
                    "GraphQL endpoint cannot be null", fail_test=False
                )
                return None

            if not query_str:
                self.__exceptions_services.raise_null_value(
                    "GraphQL query cannot be null", fail_test=False
                )
                return None

            payload = {"query": query_str}

            if variables:
                payload["variables"] = variables

            if headers is None:
                headers = {}

            if "Content-Type" not in headers:
                headers["Content-Type"] = "application/json"

            if "Accept" not in headers:
                headers["Accept"] = "application/json"

            response_obj = self.request_builder.call_request(
                method="POST",
                url=endpoint,
                headers=headers,
                json_data=payload,
                timeout=timeout,
                verify=verify,
            )

            if response_obj is None:
                self.__exceptions_services.raise_null_response_object(fail_test=False)
                return None

            try:
                response_data = response_obj.json()

                if "errors" in response_data and response_data["errors"]:
                    error_messages = [
                        error.get("message", "Unknown error") for error in response_data["errors"]
                    ]
                    self.__exceptions_services.raise_invalid_response_format(
                        f"GraphQL errors: {', '.join(error_messages)}", fail_test=False
                    )

                return response_data
            except ValueError:
                self.__exceptions_services.raise_invalid_response_format(
                    "Invalid JSON response from GraphQL endpoint", fail_test=False
                )
                return None

        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error executing GraphQL query: {str(e)}", fail_test=False
            )
            return None

    def get_data(self, response_data: Dict[str, Any]) -> Optional[Any]:
        """
        Extract data from a GraphQL response.

        Args:
            response_data: The GraphQL response dictionary

        Returns:
            The data from the response, or None if not found or on error

        Examples:
            >>> gql_utils = GraphQLUtils()
            >>>
            >>> # Execute a query and get data
            >>> query = '''
            ... query GetUsers {
            ...   users {
            ...     id
            ...     name
            ...     email
            ...   }
            ... }
            ... '''
            >>> result = gql_utils.execute_query(
            ...     query,
            ...     endpoint="https://api.example.com/graphql"
            ... )
            >>>
            >>> # Extract data from response
            >>> data = gql_utils.get_data(result)
            >>>
            >>> # Check if data exists and use it
            >>> if data:
            ...     users = data.get("users", [])
            ...     print(f"Found {len(users)} users")
            ...
            ...     # Access specific user data
            ...     if users:
            ...         first_user = users[0]
            ...         print(f"First user: {first_user.get('name')}")
            ... else:
            ...     print("No data found in response")
            >>>
            >>> # Extract data for error handling
            >>> data = gql_utils.get_data(result)
            >>> errors = gql_utils.get_errors(result)
            >>>
            >>> if data:
            ...     # Process data
            ...     pass
            ... elif errors:
            ...     # Handle errors
            ...     print(f"GraphQL errors: {errors}")
            ... else:
            ...     # Handle unexpected response
            ...     print("Invalid response format")
        """
        try:
            if response_data is None:
                self.__exceptions_services.raise_null_value(
                    "Response cannot be null", fail_test=False
                )
                return None

            if not isinstance(response_data, dict):
                self.__exceptions_services.raise_invalid_value(
                    "Response must be a dictionary", fail_test=False
                )
                return None

            if len(response_data) == 0:
                return response_data

            # For the GQL client, the data is directly returned
            # For raw requests, it's under the "data" key
            if "data" in response_data:
                return response_data["data"]
            return response_data

        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error extracting data from GraphQL response: {str(e)}", fail_test=False
            )
            return None

    def get_errors(self, response_data: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """
        Extract errors from a GraphQL response.

        Args:
            response_data: The GraphQL response dictionary

        Returns:
            List of error objects, or None if no errors or on error

        Examples:
            >>> gql_utils = GraphQLUtils()
            >>>
            >>> # Execute a query that might have errors
            >>> query = '''
            ... query GetUser($id: ID!) {
            ...   user(id: $id) {
            ...     id
            ...     name
            ...     email
            ...   }
            ... }
            ... '''
            >>> variables = {"id": "invalid-id"}
            >>> result = gql_utils.execute_query(
            ...     query,
            ...     variables=variables,
            ...     endpoint="https://api.example.com/graphql"
            ... )
            >>>
            >>> # Check for errors
            >>> errors_gql = gql_utils.get_errors(result)
            >>>
            >>> if errors_gql:
            ...     # Handle specific error types
            ...     for error in errors_gql:
            ...         error_message = error.get("message", "Unknown error")
            ...         error_path = error.get("path", [])
            ...         error_locations = error.get("locations", [])
            ...
            ...         print(f"Error: {error_message}")
            ...
            ...         if "not found" in error_message.lower():
            ...             print("User ID not found in the system")
            ...         elif "unauthorized" in error_message.lower():
            ...             print("Authentication error - please check credentials")
            ... else:
            ...     print("Query executed without errors")
            >>>
            >>> # Combined error and data handling
            >>> data = gql_utils.get_data(result)
            >>> errors_gql = gql_utils.get_errors(result)
            >>>
            >>> if errors_gql:
            ...     print("Query executed with errors:")
            ...     for error in errors_gql:
            ...         print(f" - {error.get('message', 'Unknown error')}")
            ...
            >>> if data:
            ...     print("Partial data received despite errors")
            ...     # Process available data
            ... elif not errors_gql:
            ...     print("No data returned and no errors reported")
        """
        try:
            if not response_data:
                self.__exceptions_services.raise_null_value(
                    "Response cannot be null", fail_test=False
                )
                return None

            if not isinstance(response_data, dict):
                self.__exceptions_services.raise_invalid_value(
                    "Response must be a dictionary", fail_test=False
                )
                return None

            errors = response_data.get("errors")

            return errors

        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error extracting errors from GraphQL response: {str(e)}", fail_test=False
            )
            return None

    def build_mutation(
        self,
        operation_name: str,
        input_variables: Dict[str, str],
        return_fields: List[str],
        nested_return_fields: Optional[Dict[str, List[str]]] = None,
    ) -> str:
        """
        Build a GraphQL mutation string.

        Args:
            operation_name: Name of the GraphQL mutation
            input_variables: Dictionary of input variable names and types
            return_fields: List of fields to return after mutation
            nested_return_fields: Dictionary of field names and their nested fields to return

        Returns:
            A formatted GraphQL mutation string, or empty string if operation fails

        Examples:
            >>> gql_utils = GraphQLUtils()
            >>>
            >>> # Simple mutation
            >>> mutation = gql_utils.build_mutation(
            ...     operation_name="CreateUser",
            ...     input_variables={"name": "String!", "email": "String!"},
            ...     return_fields=["id", "name", "email"]
            ... )
            >>> print(mutation)
            mutation CreateUser($name: String!, $email: String!) {
              createUser(input: {name: $name, email: $email}) {
                id
                name
                email
              }
            }
            >>>
            >>> # Mutation with nested return fields
            >>> mutation = gql_utils.build_mutation(
            ...     operation_name="UpdateUser",
            ...     input_variables={"id": "ID!", "name": "String"},
            ...     return_fields=["id", "name", "email"],
            ...     nested_return_fields={"profile": ["avatar", "bio"]}
            ... )
            >>> print(mutation)
            mutation UpdateUser($id: ID!, $name: String) {
              updateUser(input: {id: $id, name: $name}) {
                id
                name
                email
                profile {
                  avatar
                  bio
                }
              }
            }
        """
        try:
            if not operation_name:
                self.__exceptions_services.raise_null_value(
                    "Operation name cannot be null", fail_test=False
                )
                return ""

            if not input_variables:
                self.__exceptions_services.raise_null_value(
                    "Input variables cannot be null", fail_test=False
                )
                return ""

            if not return_fields:
                self.__exceptions_services.raise_null_value(
                    "Return fields cannot be null", fail_test=False
                )
                return ""

            # Build variable declarations
            vars_items = [f"${var}: {type_}" for var, type_ in input_variables.items()]
            variables_str = f"({', '.join(vars_items)})"

            # Build mutation signature
            mutation_str = f"mutation {operation_name}{variables_str} {{\n"

            # Convert operation name to camelCase for the field name (common GraphQL convention)
            field_name = operation_name[0].lower() + operation_name[1:]

            # Add input variables for the mutation
            input_args = [f"{var}: ${var}" for var in input_variables.keys()]
            input_args_str = f"{{{', '.join(input_args)}}}"

            # Add the main operation
            mutation_str += f"  {field_name}(input: {input_args_str}) {{\n"

            # Add return fields
            for field in return_fields:
                mutation_str += f"    {field}\n"

            # Add nested return fields if provided
            if nested_return_fields:
                for field, subfields in nested_return_fields.items():
                    mutation_str += f"    {field} {{\n"
                    for subfield in subfields:
                        mutation_str += f"      {subfield}\n"
                    mutation_str += "    }\n"

            # Close brackets
            mutation_str += "  }\n"
            mutation_str += "}"

            return mutation_str

        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error building GraphQL mutation: {str(e)}", fail_test=False
            )
            return ""

    def execute_mutation(
        self,
        mutation_str: str,
        variables: Dict[str, Any],
        endpoint: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        verify: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a GraphQL mutation against an endpoint.

        This is a convenience method that calls execute_query with the mutation string.

        Args:
            mutation_str: The GraphQL mutation string
            variables: Dictionary of variables for the mutation (required for mutations)
            endpoint: The GraphQL API endpoint URL (optional if client already exists)
            headers: HTTP headers to include with the request (optional)
            timeout: Request timeout in seconds (optional)
            verify: Whether to verify SSL certificates (default: True)

        Returns:
            The JSON response as a dictionary, or None if the request fails

        Examples:
            >>> gql_utils = GraphQLUtils()
            >>>
            >>> # Create client
            >>> gql_utils.create_client("https://api.example.com/graphql")
            >>>
            >>> # Build mutation
            >>> mutation = gql_utils.build_mutation(
            ...     operation_name="CreateUser",
            ...     input_variables={"name": "String!", "email": "String!"},
            ...     return_fields=["id", "name", "email"]
            ... )
            >>>
            >>> # Execute mutation with variables
            >>> variables_gq = {"name": "John Doe", "email": "john@example.com"}
            >>> result_var = gql_utils.execute_mutation(mutation, variables_gq)
            >>>
            >>> # Process result
            >>> if result_var:
            ...     created_user = gql_utils.get_data(result_var).get("createUser")
            ...     print(f"Created user with ID: {created_user['id']}")
        """
        try:
            if not mutation_str:
                self.__exceptions_services.raise_null_value(
                    "Mutation string cannot be null", fail_test=False
                )
                return None

            if not variables:
                self.__exceptions_services.raise_null_value(
                    "Variables are required for mutations", fail_test=False
                )
                return None

            return self.execute_query(
                query_str=mutation_str,
                variables=variables,
                endpoint=endpoint,
                headers=headers,
                timeout=timeout,
                verify=verify,
            )

        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error executing GraphQL mutation: {str(e)}", fail_test=False
            )
            return None

    def build_fragment(
        self,
        fragment_name: str,
        type_name: str,
        fields: List[str],
        nested_fields: Optional[Dict[str, List[str]]] = None,
    ) -> str:
        """
        Build a GraphQL fragment for reuse in queries and mutations.

        Args:
            fragment_name: Name of the fragment
            type_name: GraphQL type this fragment is for
            fields: List of fields to include
            nested_fields: Dictionary of field names and their nested fields

        Returns:
            A formatted GraphQL fragment string, or empty string if operation fails

        Examples:
            >>> gql_utils = GraphQLUtils()
            >>>
            >>> # Simple fragment
            >>> fragment = gql_utils.build_fragment(
            ...     fragment_name="UserFields",
            ...     type_name="User",
            ...     fields=["id", "name", "email"]
            ... )
            >>> print(fragment)
            fragment UserFields on User {
              id
              name
              email
            }
            >>>
            >>> # Fragment with nested fields
            >>> fragment = gql_utils.build_fragment(
            ...     fragment_name="UserWithPosts",
            ...     type_name="User",
            ...     fields=["id", "name", "email"],
            ...     nested_fields={"posts": ["id", "title", "content"]}
            ... )
            >>> print(fragment)
            fragment UserWithPosts on User {
              id
              name
              email
              posts {
                id
                title
                content
              }
            }
        """
        try:
            if not fragment_name:
                self.__exceptions_services.raise_null_value(
                    "Fragment name cannot be null", fail_test=False
                )
                return ""

            if not type_name:
                self.__exceptions_services.raise_null_value(
                    "Type name cannot be null", fail_test=False
                )
                return ""

            if not fields:
                self.__exceptions_services.raise_null_value(
                    "Fields list cannot be null", fail_test=False
                )
                return ""

            # Build fragment header
            fragment_str = f"fragment {fragment_name} on {type_name} {{\n"

            # Add fields
            for field in fields:
                fragment_str += f"  {field}\n"

            # Add nested fields if provided
            if nested_fields:
                for field, subfields in nested_fields.items():
                    fragment_str += f"  {field} {{\n"
                    for subfield in subfields:
                        fragment_str += f"    {subfield}\n"
                    fragment_str += "  }\n"

            # Close brackets
            fragment_str += "}"

            return fragment_str

        except Exception as e:
            self.__exceptions_generic.raise_generic_exception(
                f"Error building GraphQL fragment: {str(e)}", fail_test=False
            )
            return ""
