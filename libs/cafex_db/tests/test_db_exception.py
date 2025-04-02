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

# --- db_exceptions.py Tests ---
@pytest.fixture
def db_exceptions():
    """Fixture for creating a DBExceptions instance."""
    return DBExceptions()

def test_db_exceptions_raise_null_server_name(db_exceptions):
    """Tests the raise_null_server_name method."""
    with pytest.raises(CoreExceptions) as exc_info:
        db_exceptions.raise_null_server_name()
    assert "Server name can not be null" in str(exc_info.value)

def test_db_exceptions_raise_null_database_type(db_exceptions):
    """Tests the raise_null_database_type method."""
    with pytest.raises(CoreExceptions) as exc_info:
        db_exceptions.raise_null_database_type()
    assert "Database type can not be null" in str(exc_info.value)

def test_db_exceptions_raise_null_password(db_exceptions):
    """Tests the raise_null_password method."""
    with pytest.raises(CoreExceptions) as exc_info:
        db_exceptions.raise_null_password()
    assert "Password can not be null" in str(exc_info.value)

def test_db_exceptions_raise_null_secret_key(db_exceptions):
    """Tests the raise_null_secret_key method."""
    with pytest.raises(CoreExceptions) as exc_info:
        db_exceptions.raise_null_secret_key()
    assert "Secret key can not be null" in str(exc_info.value)

def test_db_exceptions_raise_invalid_database_type(db_exceptions):
    """Tests the raise_invalid_database_type method."""
    with pytest.raises(CoreExceptions) as exc_info:
        db_exceptions.raise_invalid_database_type()
    assert "The database type is invalid" in str(exc_info.value)

def test_db_exceptions_raise_null_database_object(db_exceptions):
    """Tests the raise_null_database_object method."""
    with pytest.raises(CoreExceptions) as exc_info:
        db_exceptions.raise_null_database_object()
    assert "The database object is null" in str(exc_info.value)

def test_db_exceptions_raise_null_hive_object(db_exceptions):
    """Tests the raise_null_hive_object method."""
    with pytest.raises(CoreExceptions) as exc_info:
        db_exceptions.raise_null_hive_object()
    assert "The hive client object is null" in str(exc_info.value)

def test_db_exceptions_raise_null_database_name(db_exceptions):
    """Tests the raise_null_database_name method."""
    with pytest.raises(CoreExceptions) as exc_info:
        db_exceptions.raise_null_database_name()
    assert "Database name cannot be null" in str(exc_info.value)

def test_db_exceptions_raise_null_table_name(db_exceptions):
    """Tests the raise_null_table_name method."""
    with pytest.raises(CoreExceptions) as exc_info:
        db_exceptions.raise_null_table_name()
    assert "Table name cannot be null" in str(exc_info.value)

def test_db_exceptions_raise_null_query(db_exceptions):
    """Tests the raise_null_query method."""
    with pytest.raises(CoreExceptions) as exc_info:
        db_exceptions.raise_null_query()
    assert "Query cannot be null" in str(exc_info.value)

def test_db_exceptions_raise_null_filepath(db_exceptions):
    """Tests the raise_null_filepath method."""
    with pytest.raises(CoreExceptions) as exc_info:
        db_exceptions.raise_null_filepath()
    assert "filepath cannot be null" in str(exc_info.value)

def test_db_exceptions_raise_null_result_list(db_exceptions):
    """Tests the raise_null_result_list method."""
    with pytest.raises(CoreExceptions) as exc_info:
        db_exceptions.raise_null_result_list()
    assert "Result list cannot be null" in str(exc_info.value)

def test_db_exceptions_raise_null_result_set(db_exceptions):
    """Tests the raise_null_result_set method."""
    with pytest.raises(CoreExceptions) as exc_info:
        db_exceptions.raise_null_result_set()
    assert "Result set cannot be null" in str(exc_info.value)

def test_db_exceptions_raise_null_column_header(db_exceptions):
    """Tests the raise_null_column_header method."""
    with pytest.raises(CoreExceptions) as exc_info:
        db_exceptions.raise_null_column_header()
    assert "columns/header names cannot be null" in str(exc_info.value)

def test_db_exceptions_raise_null_dataframe(db_exceptions):
    """Tests the raise_null_dataframe method."""
    with pytest.raises(CoreExceptions) as exc_info:
        db_exceptions.raise_null_dataframe()
    assert "dataframe cannot be null" in str(exc_info.value)

def test_db_exceptions_raise_null_service_name(db_exceptions):
     """Tests the raise_null_service_name method."""
     with pytest.raises(CoreExceptions) as exc_info:
          db_exceptions.raise_null_service_name()
     assert "Service name cannot be null" in str(exc_info.value)
