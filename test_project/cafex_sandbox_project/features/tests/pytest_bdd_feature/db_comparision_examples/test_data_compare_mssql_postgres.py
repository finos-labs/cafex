"""Data validation between sql and postgres feature tests."""
import pandas as pd
from pytest_bdd import (given, scenario, when, then, parsers)

from cafex_db.database_comparator import CompareDB

db_comparator = CompareDB()

result_postgresql = None
result_mssql = None
@scenario('data_compare_mssql_postgress.feature', 'Count of rows in sql db and postgres db are same')
def test_count_of_rows_in_sql_db_and_postgres_db_are_same():
    """Count of rows in sql db and postgres db are same."""


@given(parsers.cfparse('user is connected to Postgres "{str_server_name}" db server'))
def user_connect_to_postgres_server(str_server_name):
    """user is connected to Postgres "postgres" db server."""
    db_comparator.database_establish_connection(str_server_name, 'mi_api_db_config.yml')


@given(parsers.cfparse('user is connected to MSSQL "{str_server_name}" db server'))
def user_connect_to_mssql_server(str_server_name):
    """user is connected to MS SQL "mi" db server."""
    db_comparator.database_establish_connection(str_server_name, 'mi_api_db_config.yml')


@when(parsers.cfparse('user executes Postgres query from file "{file_path}"'))
def execute_store_result_postgres(file_path):
    print("Executing Postgres query from file:", file_path)
    result_postgresql = db_comparator.query_execute_with_file(file_path)
    print(result_postgresql)

@when(parsers.cfparse('user executes MSSQL query from file "{file_path}"'))
def execute_store_result_mssql(file_path):
    print("Executing MSSQL query from file:", file_path)
    result_mssql = db_comparator.query_execute_with_file(file_path)
    print(result_mssql)

@then(parsers.parse('the result should contain {result}'))
def check_expected_result():
    """
    Compares the counts obtained from PostgreSQL and MSSQL queries.
    Asserts whether the comparison matches the expected_result ('pass' or 'fail').
    """
    assert (result_postgresql==result_mssql)
    db_comparator.close_establish_connection()
    print('Test is passed')

