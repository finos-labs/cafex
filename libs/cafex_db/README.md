# CAFEX-DB

CAFEX-DB is a Python package that provides tools and utilities for database testing. It is part of the CAFEX (Centralized Automation Framework Enabler) monorepo.

### Features

CAFEX-DB offers the following features:

- **Database connection:** Supports connections to various databases, including MSSQL, MySQL, Oracle, Hive, Postgres, and Cassandra.
- **Query execution:** Provides methods to execute SQL queries and retrieve data.
- **Result set comparison:** Offers methods to compare result sets, allowing for efficient validation of database data.
- **Data-driven testing:** Supports data-driven testing approaches to execute tests with different data sets.
- **Reporting:** Integrates with CAFE's reporting capabilities to generate comprehensive test reports.

### Getting Started

#### **Prerequisites**

- Python 3.12 or later
- pip 24 or later (Python package manager)

#### **Installation**

1. Install CAFEX-DB using pip:

   ```
   pip install cafex-db
   ```

### Usage

CAFEX-DB provides a set of intuitive methods and classes to facilitate database testing. Here's a basic example:

```python
from cafex_db import database_handler

# Create a database connection
db_handler = database_handler.DatabaseHandler()
connection = db_handler.create_connection(db_type="mssql", server="dbserver", database="testdb")

# Execute a query
result_set = db_handler.execute_query(connection, "SELECT * FROM users")

# Convert the result set to a list
result_list = db_handler.resultset_to_list(result_set)

# Validate the data
assert result_list[0][1] == "John Doe"