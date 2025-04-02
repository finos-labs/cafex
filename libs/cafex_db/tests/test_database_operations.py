# pylint: disable=redefined-outer-name, protected-access
import os
import json
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import sqlalchemy as sc
from cafex_core.utils.exceptions import CoreExceptions

from cafex_db.database_handler import DatabaseConnection
from cafex_db.database_operations import DatabaseOperations
from cafex_db.db_exceptions import DBExceptions
from cafex_db.db_security import DBSecurity
# --- database_operations.py Tests ---

# Mocking cafex_core.logging.logger_ to avoid actual logging during tests
@pytest.fixture(autouse=True)
def mock_core_logger():
    """Mocks the CoreLogger class to prevent actual logging."""
    with patch("cafex_core.logging.logger_.CoreLogger") as mock_logger:
        yield mock_logger


@pytest.fixture
def database_operations():
    """Fixture for creating a DatabaseOperations instance."""
    return DatabaseOperations()

def test_database_operations_execute_statement(database_operations):
    """Tests the execute_statement method."""
    mock_connection = MagicMock()
    mock_result = MagicMock()
    mock_connection.execute.return_value = mock_result
    mock_result.__iter__.return_value = iter([{"col1": "val1"}])
    result = database_operations.execute_statement(mock_connection, "SELECT * FROM table")
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["col1"] == "val1"

def test_database_operations_execute_statement_resultset(database_operations):
    """Tests the execute_statement method with resultset."""
    mock_connection = MagicMock()
    mock_result = MagicMock()
    mock_connection.execute.return_value = mock_result
    result = database_operations.execute_statement(mock_connection, "SELECT * FROM table", str_return_type="resultset")
    assert result == mock_result

def test_database_operations_execute_statement_boolean(database_operations):
    """Tests the execute_statement method to return boolean."""
    mock_connection = MagicMock()
    mock_result = MagicMock()
    mock_result.rowcount = 1
    mock_connection.execute.return_value = mock_result
    result = database_operations.execute_statement(mock_connection, "INSERT INTO table")
    assert result is True

def test_database_operations_hive_execute_statement(database_operations):
    """Tests the hive_execute_statement method."""
    mock_hiveclient = MagicMock()
    mock_result = MagicMock()
    mock_hiveclient.sql.return_value = mock_result
    mock_result.collect.return_value = [{"col1": "val1"}]
    result = database_operations.hive_execute_statement(mock_hiveclient, "SELECT * FROM table")
    assert isinstance(result, list)
    assert result == [{"col1": "val1"}]

def test_database_operations_hive_execute_statement_resultset(database_operations):
    """Tests the hive_execute_statement method with resultset."""
    mock_hiveclient = MagicMock()
    mock_result = MagicMock()
    mock_hiveclient.sql.return_value = mock_result
    result = database_operations.hive_execute_statement(mock_hiveclient, "SELECT * FROM table", str_return_type="resultset")
    assert result == mock_result

def test_database_operations_hive_execute_statement_boolean(database_operations):
    """Tests the hive_execute_statement method to return boolean."""
    mock_hiveclient = MagicMock()
    mock_result = MagicMock()
    mock_result.count.return_value = 1
    mock_hiveclient.sql.return_value = mock_result
    result = database_operations.hive_execute_statement(mock_hiveclient, "INSERT INTO table")
    assert result is True

def test_database_operations_execute_query_from_file(database_operations, tmpdir):
    """Tests the execute_query_from_file method."""
    # Create a temporary SQL file
    sql_file = tmpdir.join("test_query.sql")
    sql_file.write("SELECT * FROM test_table;")

    # Mock the database connection and result
    mock_connection = MagicMock()
    mock_result = MagicMock()
    mock_connection.execute.return_value = mock_result

    # Execute the query from file
    result = database_operations.execute_query_from_file(mock_connection, str(sql_file))

    # Assertions
    mock_connection.execute.assert_called_once_with("SELECT * FROM test_table;")
    assert result == mock_result

def test_database_operations_close(database_operations):
    """Tests the close method."""
    mock_connection = MagicMock()
    database_operations.close(mock_connection)
    mock_connection.close.assert_called_once()

def test_database_operations_check_table_exists(database_operations):
    """Tests the check_table_exists method."""
    mock_connection = MagicMock()
    mock_result = MagicMock()
    mock_result.rowcount = 1
    mock_connection.execute.return_value = mock_result
    exists = database_operations.check_table_exists(mock_connection, "testdb", "testtable")
    assert exists is True

def test_database_operations_cassandra_resultset_to_list(database_operations):
    """Tests the cassandra_resultset_to_list method."""
    mock_resultset = MagicMock()
    mock_resultset.__iter__.return_value = ["val1", "val2"]
    result = database_operations.cassandra_resultset_to_list(mock_resultset)
    assert isinstance(result, list)
    assert result == ["val1", "val2"]

def test_database_operations_is_rowcount_zero(database_operations):
    """Tests the is_rowcount_zero method."""
    assert database_operations.is_rowcount_zero([]) is True
    assert database_operations.is_rowcount_zero([1, 2, 3]) is False

def test_database_operations_get_rowcount(database_operations):
    """Tests the get_rowcount method."""
    assert database_operations.get_rowcount([1, 2, 3]) == 3

def test_database_operations_get_headers(database_operations):
    """Tests the get_headers method."""
    data = [{"col1": "val1", "col2": "val2"}]
    headers = database_operations.get_headers(data)
    assert isinstance(headers, list)
    assert set(headers) == {"col1", "col2"}

def test_database_operations_resultset_to_list(database_operations):
    """Tests the resultset_to_list method."""
    mock_resultset = MagicMock()
    mock_resultset.__iter__.return_value = iter([{"col1": "val1", "col2": "val2"}])
    result = database_operations.resultset_to_list(mock_resultset)
    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], list)
    assert isinstance(result[1], dict)

def test_database_operations_check_value_exists_in_column(database_operations):
    """Tests the check_value_exists_in_column method."""
    data = [{"col1": "val1", "col2": "val2"}, {"col1": "val3", "col2": "val4"}]
    assert database_operations.check_value_exists_in_column(data, "col1", "val1") is True
    assert database_operations.check_value_exists_in_column(data, "col1", "val5") is False

def test_database_operations_check_value_not_exists_in_column(database_operations):
    """Tests the check_value_not_exists_in_column method."""
    data = [{"col1": "val1", "col2": "val2"}, {"col1": "val3", "col2": "val4"}]
    assert database_operations.check_value_not_exists_in_column(data, "col1", "val5") is True
    assert database_operations.check_value_not_exists_in_column(data, "col1", "val1") is False

def test_database_operations_get_column_data(database_operations):
    """Tests the get_column_data method."""
    data = [{"col1": "val1", "col2": "val2"}, {"col1": "val3", "col2": "val4"}]
    column_data = database_operations.get_column_data(data, "col1")
    assert isinstance(column_data, list)
    assert column_data == ["val1", "val3"]

def test_database_operations_compare_resultlists(database_operations):
    """Tests the compare_resultlists method."""
    list1 = [{"col1": "val1", "col2": "val2"}, {"col1": "val3", "col2": "val4"}]
    list2 = [{"col1": "val3", "col2": "val4"}, {"col1": "val5", "col2": "val6"}]
    comparison = database_operations.compare_resultlists(list1, list2)
    assert isinstance(comparison, dict)
    assert "only_in_list1" in comparison
    assert "only_in_list2" in comparison
    assert "in_both" in comparison

@pytest.fixture
def sample_dataframes():
     """Fixture for sample dataframes."""
     df1 = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
     df2 = pd.DataFrame({'col1': [3, 4, 5], 'col2': ['c', 'd', 'e']})
     return df1, df2

def test_database_operations_data_frame_diff(database_operations, sample_dataframes):
     """Tests the data_frame_diff method."""
     df1, df2 = sample_dataframes
     diff = database_operations.data_frame_diff(df1, df2)
     assert isinstance(diff, pd.DataFrame)
     assert len(diff) == 4

def test_database_operations_dataframe_to_resultset(database_operations, sample_dataframes):
     """Tests the dataframe_to_resultset method."""
     df1, _ = sample_dataframes
     result_set = database_operations.dataframe_to_resultset(df1)
     assert isinstance(result_set, list)
     assert len(result_set) == 3
     assert isinstance(result_set[0], dict)

def test_database_operations_file_to_resultlist_csv(database_operations, tmpdir):
     """Tests the file_to_resultlist method with CSV."""
     csv_file = tmpdir.join("test.csv")
     csv_file.write("col1,col2\n1,a\n2,b")
     result_list = database_operations.file_to_resultlist(str(csv_file), pstr_filetype="csv")
     assert isinstance(result_list, list)
     assert len(result_list) == 2

def test_database_operations_file_to_resultlist_excel(database_operations, tmpdir):
     """Tests the file_to_resultlist method with excel."""
     excel_file = tmpdir.join("test.xlsx")
     df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
     df.to_excel(str(excel_file), index=False)
     result_list = database_operations.file_to_resultlist(str(excel_file), pstr_filetype="excel")
     assert isinstance(result_list, list)
     assert len(result_list) == 2

def test_database_operations_file_to_resultlist_json(database_operations, tmpdir):
     """Tests the file_to_resultlist method with JSON."""
     json_file = tmpdir.join("test.json")
     data = [{'col1': 1, 'col2': 'a'}, {'col1': 2, 'col2': 'b'}]
     json_file.write(json.dumps(data))
     result_list = database_operations.file_to_resultlist(str(json_file), pstr_filetype="json")
     assert isinstance(result_list, list)
     assert len(result_list) == 2

def test_database_operations_file_to_resultlist_unsupported(database_operations, tmpdir):
     """Tests the file_to_resultlist method with unsupported file type."""
     with pytest.raises(Exception) as exc_info:
          txt_file = tmpdir.join("test.txt")
          txt_file.write("col1,col2\n1,a\n2,b")
          database_operations.file_to_resultlist(str(txt_file), pstr_filetype="txt")
     assert "Unsupported file type" in str(exc_info.value)

def test_database_operations_resultlist_to_csv(database_operations, tmpdir):
     """Tests the resultlist_to_csv method."""
     csv_file = tmpdir.join("test.csv")
     data = [{'col1': 1, 'col2': 'a'}, {'col1': 2, 'col2': 'b'}]
     database_operations.resultlist_to_csv(data, str(csv_file))
     assert os.path.exists(str(csv_file))

def test_database_operations_dataframe_to_csv(database_operations, sample_dataframes, tmpdir):
     """Tests the dataframe_to_csv method."""
     csv_file = tmpdir.join("test.csv")
     df1, _ = sample_dataframes
     database_operations.dataframe_to_csv(df1, str(csv_file))
     assert os.path.exists(str(csv_file))

def test_database_operations_list_to_dataframe(database_operations):
     """Tests the list_to_dataframe method."""
     data = [{'col1': 1, 'col2': 'a'}, {'col1': 2, 'col2': 'b'}]
     df = database_operations.list_to_dataframe(data)
     assert isinstance(df, pd.DataFrame)
     assert len(df) == 2

def test_database_operations_compare_dataframes_distinct(database_operations, sample_dataframes):
     """Tests the compare_dataframes_distinct method."""
     df1, df2 = sample_dataframes
     diff = database_operations.compare_dataframes_distinct(df1, df2)
     assert isinstance(diff, pd.DataFrame)
     assert len(diff) == 4

def test_database_operations_check_data_in_column(database_operations):
     """Tests the check_data_in_column method."""
     data = [{'col1': 1, 'col2': 'a'}, {'col1': 2, 'col2': 'b'}]
     assert database_operations.check_data_in_column(data, 1) is True
     assert database_operations.check_data_in_column(data, 3) is False

def test_database_operations_check_headers_in_resultlist(database_operations):
     """Tests the check_headers_in_resultlist method."""
     data = [{'col1': 1, 'col2': 'a'}, {'col1': 2, 'col2': 'b'}]
     headers = ['col1', 'col3']
     missing_headers = database_operations.check_headers_in_resultlist(data, headers)
     assert isinstance(missing_headers, list)
     assert 'col3' in missing_headers
     assert 'col1' not in missing_headers

def test_database_operations_spark_execute_statement(database_operations):
     """Tests the spark_execute_statement method."""
     mock_sparkclient = MagicMock()
     mock_result = MagicMock()
     mock_sparkclient.sql.return_value = mock_result
     mock_result.collect.return_value = [{"col1": "val1"}]
     result = database_operations.spark_execute_statement(mock_sparkclient, "SELECT * FROM table", True, "name")
     assert isinstance(result, list)
     assert result == [{"col1": "val1"}]

def test_database_operations_check_db_exists(database_operations):
    """Tests the check_db_exists method."""
    mock_connection = MagicMock()
    mock_connection.engine.name = "postgresql"
    mock_result = MagicMock()
    mock_result.rowcount = 1
    mock_connection.execute.return_value = mock_result
    exists = database_operations.check_db_exists(mock_connection, "testdb")
    assert exists is True

def test_database_operations_verify_column_metadata(database_operations):
     """Tests the verify_column_metadata method."""
     mock_connection = MagicMock()
     mock_connection.engine.name = "postgresql"
     with patch.object(database_operations, '_check_column_existence', return_value=True):
          result = database_operations.verify_column_metadata(mock_connection, "db", "table", "col", bln_col_existence=True)
     assert result == {'bln_col_existence': True}

def test_database_operations_modify_sql_query(database_operations, tmpdir):
     """Tests the modify_sql_query method."""
     sql_file = tmpdir.join("test_query.sql")
     sql_file.write("SELECT * FROM test_table WHERE id = <id>;")
     data_dictionary = {"<id>": "123"}
     modified_query = database_operations.modify_sql_query(str(sql_file), data_dictionary)
     assert modified_query == "SELECT * FROM test_table WHERE id = 123;"

def test_modify_sql_query_json_key_missing(database_operations, tmpdir):
    """Tests modify_sql_query with JSON file and missing key."""
    json_file = tmpdir.join("test_query.json")
    data = {"query": "SELECT * FROM test_table WHERE id = <id>;"}
    json_file.write(json.dumps(data))

    with pytest.raises(Exception) as exc_info:
        database_operations.modify_sql_query(str(json_file), {"<id>": "123"})
    assert "Error-->Key missing from parameters for json file" in str(exc_info.value)
