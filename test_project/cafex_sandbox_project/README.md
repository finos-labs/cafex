# CAFEX Test Project

This directory contains the reference test automation project for the CAFEX monorepo. It is designed to help QA engineers and automation developers quickly set up, configure, and execute comprehensive tests across web UI, API, database, desktop, and mobile platforms using the CAFEX framework.

## Overview

- **cafex_sandbox_project** is a fully functional example project demonstrating best practices for organizing, configuring, and running tests with CAFEX.
- Use this project as a template for your own automation initiatives or as a starting point for exploring CAFEX capabilities.

## Getting Started

### 1. Clone the Repository

Clone the CAFEX monorepo and navigate to the test project directory:

```cmd
cd cafex\test_project\cafex_sandbox_project
```

### 2. Install Dependencies

Ensure you have Python 3.12.10 and pip 24+ installed.

#### Install Only What You Need

- **For UI Testing Only:**
  - With pip:
    ```cmd
    pip install cafex-ui
    ```
  - With uv:
    ```cmd
    pip install uv
    uv pip install cafex-ui
    ```
- **For DB Testing Only:**
  - With pip:
    ```cmd
    pip install cafex-db
    ```
  - With uv:
    ```cmd
    pip install uv
    uv pip install cafex-db
    ```
- **For Desktop Testing Only:**
  - With pip:
    ```cmd
    pip install cafex-desktop
    ```
  - With uv:
    ```cmd
    pip install uv
    uv pip install cafex-desktop
    ```
- **For API Testing Only:**
  - With pip:
    ```cmd
    pip install cafex-api
    ```
  - With uv:
    ```cmd
    pip install uv
    uv pip install cafex-api
    ```

- **For All CAFEX Features (UI, API, DB, Desktop):**
  - With pip:
    ```cmd
    pip install cafex
    ```
  - With uv:
    ```cmd
    pip install uv
    uv pip install cafex
    ```

### 3. Project Structure

```
cafex_sandbox_project/
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
├── config.yml                  # Main configuration
├── conftest.py                 # Pytest configuration
├── pytest.ini                  # Pytest settings
└── README.md                   # Project documentation
```

### 4. Configuration

Edit `config.yml` to set up your environment, browser, base URLs, credentials, and other settings. Example:

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

## Writing and Running Tests

### BDD Tests
- Place `.feature` files in `features/tests/pytest_bdd_feature/`.
- Implement step definitions using CAFEX APIs in Python.

### Pytest/Unittest Tests
- Add regular tests in `features/tests/pytest_testsuite/` and `features/tests/unittest_testsuite/`.
- Use pytest markers for test categorization (e.g., `@pytest.mark.ui_web`, `@pytest.mark.api`).

### Business Logic
- Organize reusable UI, API, and DB logic in `features/forms/`, `features/services/`, and `features/queries/`.

### Running Tests

```cmd
cafex run                # Run all tests
pytest -m ui_web         # Run only web UI tests
pytest -m api            # Run only API tests
pytest features/tests/pytest_bdd_feature/ -v  # Run BDD tests
```

### Viewing Reports

```cmd
cafex report             # Open the latest HTML report in your browser
```

## Playwright Integration

- For browser automation, install Playwright:

```cmd
set NODE_TLS_REJECT_UNAUTHORIZED=0
playwright install
```

- Generate Playwright code:

```cmd
playwright codegen https://example.com
```

## Support & Documentation

- For CAFEX CLI help: `cafex help`
- For advanced usage, see the CAFEX package READMEs in the `libs/` directory.
- Use this sandbox project as a reference for structuring your own automation projects.

## License

This project is distributed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).

---

For questions or contributions, please refer to the main repository's [CONTRIBUTING.md](../../CONTRIBUTING.md).
