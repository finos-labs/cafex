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


# Mocking cafex_core.logging.logger_ to avoid actual logging during tests
@pytest.fixture(autouse=True)
def mock_core_logger():
    """Mocks the CoreLogger class to prevent actual logging."""
    with patch("cafex_core.logging.logger_.CoreLogger") as mock_logger:
        yield mock_logger


# --- db_security.py Tests ---
@pytest.fixture
def db_security():
    """Fixture for creating a DBSecurity instance."""
    return DBSecurity()

def test_dbsecurity_encode_password(db_security):
    """Tests the encode_password method."""
    assert db_security.encode_password("test password") == "test+password"
    assert db_security.encode_password(None) is None

@patch("cafex_core.utils.core_security.use_secured_password", return_value=False)
def test_dbsecurity_mssql_connection(mock_use_secured_password, db_security):
    """Tests the mssql method."""
    # Mock the sqlalchemy create_engine and connection
    mock_engine = MagicMock()
    mock_connection = MagicMock()
    mock_engine.connect.return_value = mock_connection
    with patch("sqlalchemy.create_engine", return_value=mock_engine):
        db_security.mssql(server_name="testserver", database_name="testdb", username="user", password="password", port_number=1433)
    mock_engine.connect.assert_called_once()

@patch("cafex_core.utils.core_security.use_secured_password", return_value=False)
def test_dbsecurity_mysql_connection(mock_use_secured_password, db_security):
    """Tests the mysql method."""
    # Mock the sqlalchemy create_engine and connection
    mock_engine = MagicMock()
    mock_connection = MagicMock()
    mock_engine.connect.return_value = mock_connection
    with patch("sqlalchemy.create_engine", return_value=mock_engine):
        db_security.mysql(server_name="testserver", database_name="testdb", username="user", password="password", port_number=3306)
    mock_engine.connect.assert_called_once()

@patch("cafex_core.utils.core_security.use_secured_password", return_value=False)
def test_dbsecurity_postgres_connection(mock_use_secured_password, db_security):
    """Tests the postgres method."""
    # Mock the sqlalchemy create_engine and connection
    mock_engine = MagicMock()
    mock_connection = MagicMock()
    mock_engine.connect.return_value = mock_connection
    with patch("sqlalchemy.create_engine", return_value=mock_engine):
        db_security.postgres(server_name="testserver", database_name="testdb", username="user", password="password", port_number=5432)
    mock_engine.connect.assert_called_once()

@patch("cafex_core.utils.core_security.use_secured_password", return_value=False)
def test_dbsecurity_oracle_connection(mock_use_secured_password, db_security):
    """Tests the oracle method."""
    with patch("cafex_db.db_security.cx_Oracle") as mock_cx_oracle:
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_engine.connect.return_value = mock_connection
        with patch("sqlalchemy.create_engine", return_value=mock_engine):
            db_security.oracle(server_name="testserver", username="user", password="password", port_number=1521, sid="sid")
        mock_engine.connect.assert_called_once()

@patch("cafex_core.utils.core_security.use_secured_password", return_value=False)
def test_dbsecurity_oracle_connection_no_sid_service(mock_use_secured_password, db_security):
     """Tests the oracle method."""
     with pytest.raises(ValueError) as exc_info:
          db_security.oracle(server_name="testserver", username="user", password="password", port_number=1521)
     assert "SID or SERVICE_NAME is required for Oracle connection." in str(exc_info.value)

@patch("cafex_core.utils.core_security.use_secured_password", return_value=False)
def test_dbsecurity_oracle_connection_no_username_password(mock_use_secured_password, db_security):
     """Tests the oracle method."""
     with patch("cafex_db.db_security.cx_Oracle"):
          with pytest.raises(ValueError) as exc_info:
               db_security.oracle(server_name="testserver", port_number=1521, sid="sid")
          assert "Username and password are required for Oracle connection." in str(exc_info.value)

#Need to install cassandra library to run cassandra_connection test case
@pytest.mark.skip(reason="Need to install Cassandra Library")
def test_dbsecurity_cassandra_connection(db_security):
    """Tests the cassandra_connection method."""
    with patch("cafex_db.db_security.Cluster") as MockCluster:
        db_security.cassandra_connection(server_name="testserver", username="user", password="password")
    MockCluster.assert_called_once()

#Need to install paramiko library to run hive_connection test case
@pytest.mark.skip(reason="Need to install Paramiko Library")
def test_dbsecurity_hive_connection_password(db_security):
    """Tests the hive_connection method with password authentication."""
    with patch("paramiko.SSHClient") as MockSSHClient:
        mock_ssh_client = MockSSHClient.return_value
        db_security.hive_connection(server_name="testserver", username="user", password="password")
        mock_ssh_client.connect.assert_called_once()

#Need to install paramiko library to run hive_connection test case
@pytest.mark.skip(reason="Need to install Paramiko Library")
def test_dbsecurity_hive_connection_pemfile(db_security):
    """Tests the hive_connection method with pem_file authentication."""
    with patch("paramiko.SSHClient") as MockSSHClient:
        mock_ssh_client = MockSSHClient.return_value
        db_security.hive_connection(server_name="testserver", username="user", pem_file="/path/to/pem")
        mock_ssh_client.connect.assert_called_once()

def test_dbsecurity_hive_connection_no_username(db_security):
     """Tests the hive_connection method when username is not given."""
     with pytest.raises(ValueError) as exc_info:
          db_security.hive_connection(server_name="testserver", password="password")
     assert "Username is required." in str(exc_info.value)

def test_dbsecurity_hive_connection_password_pemfile(db_security):
     """Tests the hive_connection method when password and pemfile are given."""
     with pytest.raises(ValueError) as exc_info:
          db_security.hive_connection(server_name="testserver", username="username", password="password", pem_file="/path/to/pem")
     assert "Specify either password or pem_file, not both." in str(exc_info.value)

def test_dbsecurity_hive_connection_no_password_pemfile(db_security):
     """Tests the hive_connection method when password and pemfile are not given."""
     with pytest.raises(ValueError) as exc_info:
          db_security.hive_connection(server_name="testserver", username="username")
     assert "Either password or pem_file is required." in str(exc_info.value)

@patch("cafex_core.utils.core_security.use_secured_password", return_value=False)
def test_dbsecurity_establish_mongodb_connection(mock_use_secured_password, db_security):
    """Tests the establish_mongodb_connection method."""
    with patch("cafex_db.db_security.MongoClient") as MockMongoClient:
        db_security.establish_mongodb_connection(username="user", password="password", cluster_url="cluster", database_name="db")
    MockMongoClient.assert_called_once()
