from pytest_bdd import (given, scenario, when, then, parsers)

from test_project.cafex_sandbox_project.features.queries.database_methods import EmployeeDbQueries

db_queries_obj = EmployeeDbQueries()


@scenario(r'db_example.feature', 'Executing a SQL Query from file')
def test_executing_a_sql_query_from_file():
    """Executing a SQL Query from file."""


@given(parsers.cfparse('user connects to server "{str_server_name}"'))
def user_connects_to_avconsql_server(str_server_name):
    db_queries_obj.mi_establish_connection(str_server_name)
    
    print(str_server_name)

@when(parsers.parse('user executes query from file {str_filepath}'))
def user_executes_query_from_file_filepath(str_filepath):
    result = db_queries_obj.query_execute_with_file(str_filepath)
    print(result)


@then(parsers.parse('the result should contain {result}'))
def the_result_should_contain_result(result):
    assert db_queries_obj.compare_resultsets(result)
    print('Test is passed')
