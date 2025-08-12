# CAFEX Monorepo

This monorepo contains the following CAFE packages:

- **cafex-core:** The core package providing foundational functionalities and utilities.
- **cafex-api:** Package for API testing, including request building, response parsing, and assertion methods.
- **cafex-db:** Package for database testing, supporting various databases like MSSQL, MySQL, Oracle, Hive, Postgres, and Cassandra.
- **cafex-ui:** Package for web UI and mobile app testing, including driver management, element interaction, and assertion methods.
- **cafex:** The super package containing all the above packages

## Introduction

CAFE (Core Automation Framework Enhancements) is a Python-based automation framework designed to simplify and streamline various testing tasks. This monorepo structure allows for efficient management and development of all CAFE packages in a single location.

## Who is this project intended to be used by?

CAFEX is designed for **QA engineers, test automation developers, and development teams** who need comprehensive test automation across web UI, mobile, API, and database layers. It's ideal for teams looking to standardize their testing approach with a unified framework.

## What is the intended outcome of using this project?

CAFEX enables teams to achieve **faster, more reliable testing** with reduced manual effort. Users can expect consistent test results, comprehensive reporting with screenshots and logs, faster feedback cycles, and improved product quality through unified automation across multiple testing domains.

## When/Where would this project be run by a user?

CAFEX runs **locally during development** for rapid testing and debugging. It's designed for **CI/CD pipeline integration** for automated testing in continuous deployment workflows. The framework supports both individual developer workflows and enterprise-scale automated testing environments.

## Getting Started

### Prerequisites

- Python 3.12 or later
- pip 24 or later(Python package manager)

### Installation

1. Clone or download the CAFE monorepo.
2. Install the required dependencies using pip: ```pip install -r dev-requirements.txt```

**Dependencies:**
- For UI, API and DB testing: `pip install cafex`
- For UI testing: `pip install cafex-ui`
- For DB testing: `pip install cafex-db`
- For API testing: `pip install cafex-api`
- For Core modules: `pip install cafex-core`

## Package Details

For detailed information about each package, please refer to their respective README files:

- **cafex:** libs/cafex/README.md
- **cafex-api:** libs/cafex_api/README.md
- **cafex-db:** libs/cafex_db/README.md
- **cafex-ui:** libs/cafex_ui/README.md
- **cafex-core:** libs/cafex_core/README.md

## What should a user do after installing the source code and its dependencies?

### Quick Start with Reference Project

The **`cafex_sandbox_project`** included in this repository contains a complete working example with all necessary files and folders. Use it as your reference and starting point.

### 1. Initialize a new project:
```bash
cafex init my_project
cd my_project
```

### 2. Project Structure Overview:
```
my_project/
├── features/
│   ├── configuration/          # Config files (browserstack, mobile, etc.)
│   ├── forms/                  # UI automation business logic
│   ├── services/               # API automation business logic
│   ├── queries/                # Database automation business logic
│   ├── testdata/               # Test data files (JSON/YAML preferred)
│   └── tests/
│       ├── pytest_bdd_feature/ # BDD tests with .feature files
│       ├── pytest_testsuite/   # Regular pytest tests
│       └── unittest_testsuite/ # Unit tests
├── result/                     # Test execution results
└── config.yml                 # Main configuration
```

### 3. Configure your environment in config.yml:
```yaml
current_execution_browser: chrome
environment: https://the-internet.herokuapp.com
execution_environment: dev
default_explicit_wait: 60

env:
  dev:
    web_demo:
      base_url: https://the-internet.herokuapp.com
      default_user:
        username: tomsmith
        password: SuperSecretPassword!
```

### 4. Write BDD Tests (Recommended Approach):

**Create feature files** in `features/tests/pytest_bdd_feature/` with **mandatory tags**:

```gherkin
Feature: Login functionality
  
  @ui_web @smoke
  Scenario: Successful login with valid credentials
    Given the user is on the login page
    When the user enters valid credentials
    And the user clicks the login button
    Then the user should be logged in successfully

  @api @smoke  
  Scenario: Get user details via API
    Given the API is available
    When I send a GET request to "/users/1"
    Then the response status should be 200

  @db @regression
  Scenario: Validate user data in database
    Given the database connection is established
    When I query for user with id 1
    Then the user details should match expected values

  @mobile_app @smoke
  Scenario: Mobile app login
    Given the mobile app is launched
    When the user logs in with valid credentials
    Then the dashboard should be displayed
```

**Implement step definitions** using CAFEX APIs:

```python
from pytest_bdd import given, when, then, scenario
from cafex import CafeXWeb, CafeXAPI, CafeXDB

@scenario('login.feature', 'Successful login with valid credentials')
def test_login():
    pass

@given('the user is on the login page')
def open_login_page():
    CafeXWeb().navigate("https://the-internet.herokuapp.com/login")

@when('the user enters valid credentials')
def enter_credentials():
    CafeXWeb().type("id=username", "tomsmith")
    CafeXWeb().type("id=password", "SuperSecretPassword!")

@when('the user clicks the login button')
def click_login():
    CafeXWeb().click("xpath=//button[@type='submit']")

@then('the user should be logged in successfully')
def verify_login():
    success_message = CafeXWeb().get_web_element("css=.flash.success").text
    assert "You logged into a secure area!" in success_message
```

### 5. Write Regular pytest/unittest Tests:

**For pytest** in `features/tests/pytest_testsuite/` with **pytest markers**:

```python
import pytest
from cafex import CafeXWeb, CafeXAPI

@pytest.mark.ui_web
def test_add_remove_elements():
    CafeXWeb().navigate("https://the-internet.herokuapp.com/")
    CafeXWeb().click("xpath=//a[text()='Add/Remove Elements']")
    CafeXWeb().click("xpath=//button[text()='Add Element']")
    
    delete_button = CafeXWeb().get_web_element("xpath=//button[text()='Delete']")
    assert delete_button.is_displayed()

@pytest.mark.api
def test_api_get_posts():
    response = CafeXAPI().call_request(
        method="GET",
        url="https://jsonplaceholder.typicode.com/posts/1"
    )
    assert response.status_code == 200
    assert "userId" in response.json()

@pytest.mark.db
def test_database_connection():
    from cafex_db import DatabaseHandler
    db = DatabaseHandler()
    # Add your database test logic here
```

### 6. Organize Business Logic:

**UI Methods** in `features/forms/ui_methods/`:
```python
from cafex import CafeXWeb
from cafex_core.reporting_.reporting import Reporting

class LoginPageMethods:
    def __init__(self):
        self.reporting = Reporting()
    
    def perform_login(self, username, password):
        CafeXWeb().type("id=username", username)
        CafeXWeb().type("id=password", password)
        CafeXWeb().click("xpath=//button[@type='submit']")
        self.reporting.insert_step("Login", "User logged in successfully", "Pass")
```

**API Services** in `features/services/`:
```python
from cafex import CafeXAPI
import json

class UserAPI:
    def __init__(self):
        self.base_url = "https://jsonplaceholder.typicode.com"
    
    def create_user(self, user_data):
        return CafeXAPI().call_request(
            method="POST",
            url=f"{self.base_url}/users",
            headers={"Content-Type": "application/json"},
            payload=json.dumps(user_data)
        )
```

### 7. Run Tests:

```bash
# Run all tests
cafex run

# Run specific test types
pytest -m ui_web                    # Web UI tests only
pytest -m api                      # API tests only
pytest -m "ui_web and smoke"       # Web UI smoke tests

# Run BDD tests
pytest features/tests/pytest_bdd_feature/ -v

# Run with specific browser
pytest --browser=firefox -m ui_web
```

### 8. View Reports:
```bash
cafex report  # Opens latest HTML report in browser
```

### Developer Integration:

**For developers** wanting to integrate CAFEX into their workflow:

```python
# Quick API validation in development
from cafex import CafeXAPI

def test_my_endpoint():
    response = CafeXAPI().call_request(
        method="GET", 
        url="http://localhost:8080/api/health"
    )
    assert response.status_code == 200

# Quick UI smoke test
from cafex import CafeXWeb

def test_app_loads():
    CafeXWeb().navigate("http://localhost:3000")
    assert "My App" in CafeXWeb().get_title()
```

**For detailed help and examples:**
- Run `cafex help` for complete CLI documentation
- Explore `cafex_sandbox_project` for working examples
- Check the individual package READMEs for advanced features
