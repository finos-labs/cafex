# pylint: disable=redefined-outer-name, protected-access
from unittest.mock import MagicMock, patch
import pytest


from cafex_db.database_handler import DatabaseConnection


@pytest.fixture(autouse=True)
def mock_core_logger():
    """Mocks the CoreLogger class to prevent actual logging."""
    with patch("cafex_core.logging.logger_.CoreLogger") as mock_logger:
        yield mock_logger

# --- database_handler.py Tests ---
@pytest.fixture
def database_connection():
    """Fixture for creating a DatabaseConnection instance."""
    return DatabaseConnection()

@patch("cafex_db.database_handler.DatabaseConnection._create_mssql_connection")
def test_database_connection_create_db_connection_mssql(mock_create_mssql, database_connection):
    """Tests create_db_connection with MSSQL."""
    database_connection.create_db_connection("mssql", "testserver", database_name="testdb", username="user", password="password")
    mock_create_mssql.assert_called_once()

@patch("cafex_db.database_handler.DatabaseConnection._create_mysql_connection")
def test_database_connection_create_db_connection_mysql(mock_create_mysql, database_connection):
    """Tests create_db_connection with MySQL."""
    database_connection.create_db_connection("mysql", "testserver", database_name="testdb", username="user", password="password")
    mock_create_mysql.assert_called_once()

@patch("cafex_db.database_handler.DatabaseConnection._create_oracle_connection")
def test_database_connection_create_db_connection_oracle(mock_create_oracle, database_connection):
    """Tests create_db_connection with Oracle."""
    database_connection.create_db_connection("oracle", "testserver", database_name="testdb", username="user", password="password", sid="sid")
    mock_create_oracle.assert_called_once()

@patch("cafex_db.database_handler.DatabaseConnection._create_hive_connection")
def test_database_connection_create_db_connection_hive(mock_create_hive, database_connection):
    """Tests create_db_connection with Hive."""
    database_connection.create_db_connection("hive", "testserver", username="user", password="password")
    mock_create_hive.assert_called_once()

@patch("cafex_db.database_handler.DatabaseConnection._create_postgresql_connection")
def test_database_connection_create_db_connection_postgresql(mock_create_postgresql, database_connection):
    """Tests create_db_connection with PostgreSQL."""
    database_connection.create_db_connection("postgresql", "testserver", database_name="testdb", username="user", password="password")
    mock_create_postgresql.assert_called_once()

def test_create_mssql_connection_exception(database_connection):
    """Tests _create_mssql_connection raises exception."""
    with patch("cafex_db.db_security.DBSecurity.mssql", side_effect=Exception("MSSQL connection failed")):
        with pytest.raises(Exception) as exc_info:
            database_connection._create_mssql_connection("testserver", database_name="testdb", username="user", password="password")
        assert "MSSQL connection failed" in str(exc_info.value)

def test_database_connection_invalid_database_type(database_connection):
    """Tests create_db_connection when called with an invalid database_type."""
    with pytest.raises(ValueError) as exc_info:
        database_connection.create_db_connection("invalid_db", "testserver")
    assert "Database type is invalid" in str(exc_info.value)
