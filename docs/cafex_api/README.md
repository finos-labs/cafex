# CAFE-API

CAFEX-API is a Python package that provides tools and utilities for API testing. It is part of the CAFEX (Centralized Automation Framework Enabler) monorepo.

### Features

CAFEX-API offers the following features:

- **Request building:** Simplifies the creation of API requests with various methods and parameters.
- **Response parsing:** Provides methods to parse JSON and XML responses and extract relevant data.
- **Assertions:** Includes assertion methods specifically designed for API testing, allowing for efficient validation of response data.
- **Data-driven testing:** Supports data-driven testing approaches to execute tests with different data sets.
- **Reporting:** Integrates with CAFE's reporting capabilities to generate comprehensive test reports.

### Getting Started

#### **Prerequisites**

- Python 3.12 or later
- pip (Python package manager)

#### **Installation**

1. Install CAFEX-API using pip:

   ```
   pip install cafex-api
   ```

### Usage

CAFE-API provides a set of intuitive methods and classes to facilitate API testing. Here's a basic example:

```python
from cafex_api import request_builder
from cafex_api import response_parser_json

# Build an API request
request = request_builder.RequestBuilder().get(url="https://api.example.com/users")

# Send the request and get the response
response = request.send()

# Parse the JSON response
parsed_response = response_parser_json.ParseJsonData().get_dict(response.text)

# Validate the response data
assert parsed_response["status"] == "success"