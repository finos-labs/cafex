# Exceptions Module

## Overview

The CafeX exceptions module provides structured exception handling capabilities through three main components:
- CoreExceptions: Base exception handling functionality
- APIExceptions: Specialized exceptions for API operations
- DBExceptions: Specialized exceptions for database operations

The module ensures:
- Consistent exception formatting
- Automatic evidence collection
- Integration with reporting
- Test status management

## Core Exceptions

### raise_generic_exception Method

The primary method for raising and handling exceptions:

```python
def raise_generic_exception(
    message: str,              # Exception message
    insert_report: bool = True,  # Add to test report
    trim_log: bool = True,     # Use trimmed stack trace
    log_local: bool = True,    # Enable local traces
    fail_test: bool = True     # Mark test as failed
) -> None:
```

Usage:
```python
from cafex_core.utils.exceptions import CoreExceptions

exceptions = CoreExceptions()

# Basic usage - fails the test
exceptions.raise_generic_exception(
    message="Database connection failed"
)

# Usage without failing test
exceptions.raise_generic_exception(
    message="Non-critical error occurred",
    fail_test=False
)

# Usage with custom logging options
exceptions.raise_generic_exception(
    message="Complex error",
    trim_log=True,      # Show relevant stack frames only
    log_local=True,     # Enable local traces
    fail_test=True      # Mark test as failed
)
```
When an exception is raised, it appears in the report with:
- Detailed message
- Stack trace
- Test context
- Any associated evidence

## API Exceptions

APIExceptions extends CoreExceptions to provide specialized handling for API-related errors. All methods include standard parameters:
- `insert_report: bool = True` - Add to test report
- `trim_log: bool = True` - Use trimmed stack trace
- `log_local: bool = True` - Enable local traces
- `fail_test: bool = True` - Mark test as failed

### Available Methods

```python
from cafex_api.api_exceptions import APIExceptions

exceptions = APIExceptions()

# Handle null response object
exceptions.raise_null_response_object()

# Handle invalid response format
exceptions.raise_invalid_response_format("expected format")

# Handle missing required field
exceptions.raise_missing_required_field("field_name")

# Handle invalid status code
exceptions.raise_invalid_status_code(500, 200)

# Handle null value
exceptions.raise_null_value("Got null value")

# Handle invalid value
exceptions.raise_invalid_value("Got invalid value")

# Handle invalid file path
exceptions.raise_file_not_found("file_path")
```
### Usage Examples

- Basic API Response Validation:
```python
from cafex_api.api_exceptions import APIExceptions

exceptions = APIExceptions()

def validate_user_response(response):
    if response is None:
        exceptions.raise_null_response_object(fail_test=True)
        
    if response.status_code != 200:
        exceptions.raise_invalid_status_code(
            status_code=response.status_code,
            expected_code=200
        )
        
    if "user_id" not in response.json():
        exceptions.raise_missing_required_field(
            field_name="user_id"
        )
```

- Response Format Validation:
```python
from cafex_api.api_exceptions import APIExceptions

exceptions = APIExceptions()

def validate_user_response(response):
    if response is None:
        exceptions.raise_null_response_object(fail_test=True)
        
    if response.status_code != 200:
        exceptions.raise_invalid_status_code(
            status_code=response.status_code,
            expected_code=200
        )
        
    if "user_id" not in response.json():
        exceptions.raise_missing_required_field(
            field_name="user_id"
        )
```
### How Exceptions Appear in Report
API exceptions are recorded in the test report with:

- Exception type and message
- Stack trace
- Test context
- Any associated evidence

Example report entry:

```json
{
    "evidence": {
        "exceptions": [{
            "message": "CAFEX Exception --> API returned null response",
            "type": "APIException",
            "timestamp": "2024-11-20T19:31:37.037",
            "phase": "step",
            "stackTrace": "Cafex Stack Trace:\nat ...",
            "context": {
                "current_test": "test_api_validation",
                "current_step": "Validate API Response"
            }
        }]
    }
}
```

## DB Exceptions

DBExceptions extends CoreExceptions to provide specialized handling for database-related errors. Like other exception types, all methods support standard parameters:
- `insert_report: bool = True` - Add to test report
- `trim_log: bool = True` - Use trimmed stack trace
- `log_local: bool = True` - Enable local traces
- `fail_test: bool = True` - Mark test as failed

### Connection Related Exceptions

```python
from cafex_db.db_exceptions import DBExceptions

exceptions = DBExceptions()

# Handle null server name
exceptions.raise_null_server_name()

# Handle null database type
exceptions.raise_null_database_type()

# Handle missing credentials
exceptions.raise_null_password()

# Handle missing security keys
exceptions.raise_null_secret_key()

# Handle invalid database type
exceptions.raise_invalid_database_type()

# Handle null service name
exceptions.raise_null_service_name()
```

### Object State Exceptions
```python
from cafex_db.db_exceptions import DBExceptions

exceptions = DBExceptions()

# Handle null database object
exceptions.raise_null_database_object()

# Handle null Hive client
exceptions.raise_null_hive_object()

# Handle null database name
exceptions.raise_null_database_name()

# Handle null table name
exceptions.raise_null_table_name()
```

### Data Operation Exceptions
```python
from cafex_db.db_exceptions import DBExceptions

exceptions = DBExceptions()

# Handle null query string
exceptions.raise_null_query()

# Handle missing file path
exceptions.raise_null_filepath()

# Handle null result list
exceptions.raise_null_result_list()

# Handle null result set
exceptions.raise_null_result_set()

# Handle missing columns
exceptions.raise_null_column_header()

# Handle null DataFrame
exceptions.raise_null_dataframe()
```
### Usage Examples

- Database Connection Setup:
```python
from cafex_db.db_exceptions import DBExceptions

exceptions = DBExceptions()

def setup_database_connection(config):
    try:
        if not config.get('server_name'):
            exceptions.raise_null_server_name()
            
        if not config.get('database_type'):
            exceptions.raise_null_database_type()
            
        if not config.get('password'):
            exceptions.raise_null_password()
            
        # Continue with connection setup...
            
    except Exception as e:
        exceptions.raise_generic_exception(
            f"Failed to setup database connection: {str(e)}"
        )
```

- Query Execution:
```python
from cafex_db.db_exceptions import DBExceptions

exceptions = DBExceptions()

def execute_query(query, database):
    try:
        if not database:
            exceptions.raise_null_database_object()
            
        if not query or not query.strip():
            exceptions.raise_null_query()
            
        result = database.execute(query)
        if not result:
            exceptions.raise_null_result_set()
            
        return result
            
    except Exception as e:
        exceptions.raise_generic_exception(
            f"Query execution failed: {str(e)}"
        )
```


- DataFrame Operations:

```python
from cafex_db.db_exceptions import DBExceptions

exceptions = DBExceptions()

def process_dataframe(df, required_columns):
    try:
        if df is None or df.empty:
            exceptions.raise_null_dataframe()
            
        missing_cols = [col for col in required_columns 
                       if col not in df.columns]
        if missing_cols:
            exceptions.raise_null_column_header()
            
        # Process DataFrame...
            
    except Exception as e:
        exceptions.raise_generic_exception(
            f"DataFrame processing failed: {str(e)}"
        )
```
### How DB Exceptions Appear in Reports
DB exceptions are recorded in the test report with detailed context:

```json
{
    "evidence": {
        "exceptions": [{
            "message": "CAFEX Exception --> Database connection failed: Password cannot be null",
            "type": "DBException",
            "timestamp": "2024-11-20T19:31:37.037",
            "phase": "step",
            "stackTrace": "Cafex Stack Trace:\nat ...",
            "context": {
                "current_test": "test_database_connection",
                "current_step": "Connect to Database"
            }
        }]
    }
}
```

# Best Practices for Exception Handling

## 1. Exception Granularity

### Use specific exceptions for clearer error identification
- Choose the most appropriate exception type (Core/API/DB)
- Use descriptive exception names that indicate the error type
- Avoid generic exceptions when specific ones are available

### Include relevant context in exception messages
- Add details about what operation was being performed
- Include relevant parameter values
- Reference specific components or services involved 

### Consider impact on test flow when setting fail_test flag
- Set `fail_test=True` for critical errors that should halt test execution
- Use `fail_test=False` for non-critical errors that should be logged but not fail the test
- Document rationale for fail_test decisions in code comments

## 2. Reporting Integration

### Set appropriate fail_test flags based on error severity
```python
from cafex_db.db_exceptions import DBExceptions
exceptions = DBExceptions()

# Critical error - fails test
exceptions.raise_null_database_object(fail_test=True)

# Non-critical error - logs but continues
exceptions.raise_null_result_set(fail_test=False)
```

### Add meaningful context to exception messages
```python
from cafex_core.utils.exceptions import CoreExceptions
exceptions = CoreExceptions()

# Bad
exceptions.raise_generic_exception("Query failed")

# Good 
query_name = "invalid query"
table_name = "invalid table"
exceptions.raise_generic_exception(
    f"Failed to execute query '{query_name}' on table '{table_name}': {str(e)}"
)
```

