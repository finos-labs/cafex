# test_database_handler.py
import pytest
from unittest.mock import patch, MagicMock
from cafex_db.database_handler import DatabaseConnection
from cafex_db.db_exceptions import DBExceptions

@pytest.fixture
def db_connection():
    return DatabaseConnection()

def test_create_db_connection_mssql(db_connection):
    with patch.object('mssql', return_value=MagicMock()) as mock_mssql:
        conn = db_connection.create_db_connection('mssql', 'server_name', username='user', password='pass')
        assert conn is not None
        mock_mssql.assert_called_once()

def test_create_db_connection_mysql(db_connection):
    with patch.object('mysql', return_value=MagicMock()) as mock_mysql:
        conn = db_connection.create_db_connection('mysql', 'server_name', username='user', password='pass')
        assert conn is not None
        mock_mysql.assert_called_once()

def test_create_db_connection_oracle(db_connection):
    with patch.object('oracle', return_value=MagicMock()) as mock_oracle:
        conn = db_connection.create_db_connection('oracle', 'server_name', username='user', password='pass', sid='sid')
        assert conn is not None
        mock_oracle.assert_called_once()

def test_create_db_connection_hive(db_connection):
    with patch.object( 'hive_connection', return_value=MagicMock()) as mock_hive:
        conn = db_connection.create_db_connection('hive', 'server_name', username='user', pem_file='path/to/pem')
        assert conn is not None
        mock_hive.assert_called_once()

def test_create_db_connection_postgresql(db_connection):
    with patch.object( 'postgres', return_value=MagicMock()) as mock_postgres:
        conn = db_connection.create_db_connection('PostgreSQL', 'server_name', username='user', password='pass')
        assert conn is not None
        mock_postgres.assert_called_once()

def test_create_db_connection_cassandra(db_connection):
    with patch.object( 'cassandra_connection', return_value=MagicMock()) as mock_cassandra:
        conn = db_connection.create_db_connection('cassandra', 'server_name', username='user', password='pass')
        assert conn is not None
        mock_cassandra.assert_called_once()