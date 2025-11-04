# CAFEX

CAFEX is a Python package that provides tools and utilities for UI, API and DB testing. It is part of the CAFEX (Centralized Automation Framework Enabler) monorepo.

## Features

### CAFEX offers four packages:
- **cafex-ui**
- **cafex-api**
- **cafex-db**
- **cafex-core**

### CAFEX-UI Package
- **Driver management:** Supports various web browsers (Chrome, Firefox, Edge, etc.) and mobile platforms (iOS, Android).
- **Element interaction:** Provides methods to interact with web elements and mobile app elements, such as clicking, typing, and retrieving text.
- **Assertions:** Includes assertion methods specifically designed for UI testing, allowing for efficient validation of UI elements and behaviors.
- **Data-driven testing:** Supports data-driven testing approaches to execute tests with different data sets.
- **Reporting:** Integrates with CAFE's reporting capabilities to generate comprehensive test reports with screenshots and detailed logs.

### CAFEX-API Package
- **Request building:** Simplifies the creation of API requests with various methods and parameters.
- **Response parsing:** Provides methods to parse JSON and XML responses and extract relevant data.
- **Assertions:** Includes assertion methods specifically designed for API testing, allowing for efficient validation of response data.
- **Data-driven testing:** Supports data-driven testing approaches to execute tests with different data sets.
- **Reporting:** Integrates with CAFE's reporting capabilities to generate comprehensive test reports.

### CAFEX-DB Package
- **Database connection:** Supports connections to various databases, including MSSQL, MySQL, Oracle, Hive, Postgres, and Cassandra.
- **Query execution:** Provides methods to execute SQL queries and retrieve data.
- **Result set comparison:** Offers methods to compare result sets, allowing for efficient validation of database data.
- **Data-driven testing:** Supports data-driven testing approaches to execute tests with different data sets.
- **Reporting:** Integrates with CAFE's reporting capabilities to generate comprehensive test reports.

### CAFEX-CORE Package
- **Reduce code duplication:** By providing reusable components and utilities, CAFEX-CORE minimizes the need for repetitive code across test scripts.
- **Improve maintainability:** The modular design and clear structure of CAFEX-CORE make test scripts easier to understand and maintain.
- **Enhance efficiency:** CAFEX-CORE offers various features and functionalities that accelerate test development and execution.
- **Promote collaboration:** The framework facilitates collaboration among team members by providing a standardized approach to automation.

## Getting Started

### **Prerequisites**

- Python 3.12 or later
- pip (Python package manager)

### **Installation**

1. Install CAFEX using pip:

   ```
   pip install cafex
   ```

## CAFEX-UI Usage

CAFEX-UI provides a set of intuitive methods and classes to facilitate UI testing. Here's a basic example for web UI testing:

```python
from cafex_ui.web_client import web_client_actions

# Create a web client actions object
web_actions = web_client_actions.WebClientActions()

# Navigate to a website
web_actions.navigate("https://www.example.com")

# Find an element and click on it
element = web_actions.get_web_element("xpath=//button[text()='Submit']")
web_actions.click(element)

# Validate the page title
assert web_actions.get_title() == "Success Page"

```

## CAFEX-API Usage

CAFEX-API provides a set of intuitive methods and classes to facilitate API testing. Here's a basic example:

```python
from cafex_api import request_builder
from cafex_core.parsers import json_parser

# Build an API request
request = request_builder.RequestBuilder().get(url="https://api.example.com/users")

# Send the request and get the response
response = request.send()

# Parse the JSON response
parsed_response = json_parser.ParseJsonData().get_dict(response.text)

# Validate the response data
assert parsed_response["status"] == "success"

```

## CAFEX-DB Usage

CAFEX-DB provides a set of intuitive methods and classes to facilitate database testing. Here's a basic example:

```python
from cafex_db import database_handler

# Create a database connection
db_handler = database_handler.DatabaseHandler()
connection = db_handler.create_db_connection(db_type="mssql", server="dbserver", database="testdb")

# Execute a query
result_set = db_handler.execute_statement(connection, "SELECT * FROM users")

# Convert the result set to a list
result_list = db_handler.resultset_to_list(result_set)

# Validate the data
assert result_list[0][1] == "John Doe"
```