# Reporting Module

## Overview

The CafeX reporting module provides test automation reporting capabilities through two main components:
- `insert_step` method for recording steps and assertions
- `@step` decorator for organizing pytest and unittest test cases in BDD style

## Using insert_step Method

The `insert_step` method is the primary way to record test steps and assertions in your tests. It serves two purposes:

1. When used inside a running step (pytest-bdd step or within @step decorator):
   - Records assertions and evidence within that step
2. When used directly in pytest/unittest tests (without @step):
   - Creates a new step and records assertions within it

### Basic Usage:
```python
from cafex_core.reporting_.reporting import Reporting

# Initialize reporting
reporting = Reporting()

# Record a step/assertion
reporting.insert_step(
    expected_message="Click on Forgot Password link",  # What should happen
    actual_message="Forgot Password is found",         # What actually happened
    status="Pass"                                      # "Pass" or "Fail"
)
```
### Example in pytest-bdd Step Definition:
```python
from cafex_core.reporting_.reporting import Reporting
from pytest_bdd import when

# Initialize reporting
reporting = Reporting()

@when('user clicks forgot password')
def click_forgot_password(login_page):
    try:
        if login_page.is_element_displayed("forgot_password"):
            login_page.click("forgot_password")
            # Records assertion within the BDD step
            reporting.insert_step(
                "Click on Forgot Password link",
                "Forgot Password is found",
                "Pass"
            )
            return True
        else:
            reporting.insert_step(
                "Click on Forgot Password link",
                "Forgot Password could not be found",
                "Fail"
            )
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
```
### Example Creating Standalone Step:
```python
from cafex_core.reporting_.reporting import Reporting

def test_login_flow():
    reporting = Reporting()
    
    # Creates a new step in the report
    reporting.insert_step(
        expected_message="Webpage should launch",
        actual_message="Webpage launched",
        status="Pass",
        take_screenshot=True
    )
```
## Using @step Decorator

The `@step` decorator provides BDD-style organization for pytest and unittest test cases. It creates a structured step in the report with its own timing and evidence collection.

**Note:** The @step decorator is only for pytest and unittest tests. Do not use it with pytest-bdd tests, as pytest-bdd handles steps automatically.

### Basic Usage:

```python
from cafex_core.reporting_.step_decorator import step
from cafex_core.reporting_.reporting import Reporting
import pytest

class TestLoginPytest:
    @pytest.mark.login
    def test_login_flow(self):
        reporting = Reporting()
        
        # First record a standalone step
        reporting.insert_step(
            "Webpage should launch", 
            "Webpage launched",
            "Pass", 
            take_screenshot=True
        )
        
        # Then use @step for organized test steps
        @step("User is on login page")
        def verify_login_page():
            # Any insert_step calls here will be recorded within this step
            reporting.insert_step(
                "Login page should be visible",
                "Login page displayed",
                "Pass"
            )
            
        @step("User enters credentials")
        def enter_credentials():
            reporting.insert_step(
                "Credentials should be entered",
                "Username and password entered",
                "Pass"
            )
            
        # Execute the steps
        verify_login_page()
        enter_credentials()
```
### Full Example with All Features:
```python
from cafex_core.reporting_.step_decorator import step
from cafex_core.reporting_.reporting import Reporting
import pytest
@pytest.mark.mobile_app
def test_forgot_password_flow():
    """Test forgot password functionality."""
    reporting = Reporting()
    obj_mobile = Mobile_Common()

    # Standalone step - creates new step in report
    reporting.insert_step(
        "Webpage should launch", 
        "Webpage launched",
        "Pass", 
        take_screenshot=True
    )

    @step("Background: User is on App Landing page")
    def background():
        # This insert_step will be recorded within the "Background" step
        assert obj_mobile.kill_and_relaunch_app()

    @step("When user clicks Forgot Password on login screen")
    def go_to_forgot_password():
        # This insert_step will be part of "When user clicks..." step
        assert obj_mobile.click_forgot_password_link()

    @step("Then user should see Forgot Password on app")
    def verify_forgot_password():
        assert obj_mobile.check_forgot_password_page()

    # Execute steps in sequence
    background()
    go_to_forgot_password()
    verify_forgot_password()
```

### How Steps Appear in Reports

When using @step decorator, each step appears in the report with:

 - Step name (from decorator description)
 - Start and end time
 - Duration
 - Status (Pass/Fail)
 - Screenshots
 - Any assertions made using insert_step
 - Any exceptions that occurred

Example from report.json:

```json
{
  "stepName": "When user clicks Forgot Password on login screen",
  "stepStatus": "P",
  "stepStartTime": "2024-11-20T19:31:34.670",
  "stepEndTime": "2024-11-20T19:31:39.439",
  "stepDurationSeconds": 4,
  "stepDuration": "4 seconds",
  "asserts": [
    {
      "name": "Assert When user clicks Forgot Password on login screen: Click on Forgot Password link: Forgot Password is found",
      "expected": "Click on Forgot Password link",
      "actual": "Forgot Password is found",
      "status": "P",
      "type": "step",
      "timestamp": "2024-11-20T19:31:37.037"
    }
  ],
  "evidence": {
    "screenshots": {
      "screenshot_name": "screenshot_path"
    }
  }
}
```
## Reporting Structure

The framework automatically generates comprehensive test execution reports with the following components:

### 1. Directory Structure
```
test_project/
└── result/
├── {execution-uuid}/         # Current execution results
│   ├── logs/                # Execution logs
│   │   └── master_{timestamp}.log
│   ├── screenshots/         # Test screenshots
│   └── result.json         # Test execution details
└── history/                # Previous execution results
└── {timestamp}_{execution-uuid}/
```

### 2. Result.json Structure

The result.json contains all test execution details:

```json
{
    "collectionInfo": {
        "testCount": 1,
        "pytestCount": 1,
        "pytestBddCount": 0,
        "unittestCount": 0,
        "collectionStartTime": "2024-11-20T19:30:39.303",
        "collectionEndTime": "2024-11-20T19:30:39.305",
        "collectionDurationSeconds": 0,
        "collectionDuration": "0 seconds",
        "uniqueTags": ["mobile_app", "test_exceptions"],
        "tagStatistics": {
            "test_exceptions": 1,
            "mobile_app": 1
        }
    },
    "executionInfo": {
        "executionId": "uuid",
        "executionStatus": "P",
        "executionStartTime": "timestamp",
        "executionEndTime": "timestamp",
        "totalPassed": 1,
        "totalFailed": 0,
        "environment": "prod",
        "isParallel": false
    },
    "tests": {
        "pytestBdd": [],
        "pytest": [
            {
                "name": "test_name",
                "testType": "pytest",
                "testStatus": "P",
                "steps": [
                    {
                        "stepName": "Step description",
                        "stepStatus": "P",
                        "stepStartTime": "timestamp",
                        "stepEndTime": "timestamp",
                        "stepDurationSeconds": 4,
                        "asserts": [],
                        "evidence": {
                            "screenshots": {},
                            "exceptions": []
                        }
                    }
                ]
            }
        ],
        "unittest": []
    }
}
```
### 3. Log Files
The framework generates detailed logs showing test execution flow:
```
2024-11-20 19:30:38,073 - INFO - PytestConfigure
2024-11-20 19:30:38,161 - INFO - STARTED EXECUTION OF SESSION
2024-11-20 19:30:39,336 - INFO - Running test: test_check_forgot_password_in_login_page_steps
2024-11-20 19:31:26,909 - INFO - Executing step: Background: User is on App Landing page
2024-11-20 19:31:34,666 - INFO - Step Execution Complete
```

### 4. Evidence Collection
The framework automatically collects:
1. Screenshots:
   - On step completion
   - When failures occur
   - When exception is encountered
   - When an assertion is performed
   
2. Exceptions:
   - Full stack traces
   - Error messages
   - Failure context
   - Exception Screenshots

3. Step Details
   - Start and end times
   - Duration
   - Status
   - All assertions made
   - Evidence collected

### 5. History

Previous test executions are automatically archived in the history folder:

- Organized by timestamp
- Contains complete execution data
- Maintains screenshots and logs
- Preserves result.json

Test results can be accessed from:
- Current execution folder: `result/{execution-uuid}/`
- History folder: `result/history/{timestamp}_{execution-uuid}/`