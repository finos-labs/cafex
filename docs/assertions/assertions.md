# Assertions Module

## Overview

The Assertions module provides a robust way to perform test validations with integrated reporting. It supports two main types of validations:
- Assertions (`assert_*`) - Stop test execution on failure
- Verifications (`verify_*`) - Continue execution after failure

Key features:
- Integration with test reporting
- Automatic screenshot capture
- Support for both BDD and non-BDD tests
- Custom failure messages
- Conditional assertions

## Basic Usage

```python
from cafex_core.utils.assertions import Assertions
from cafex_ui import CafeXMobile

assertions = Assertions()

# Basic assertion
button = CafeXMobile().get_web_element("xpath=//*@content-desc='Button']")
assertions.assert_true(
    expected_message="Button should be enabled",
    actual_message="Button is enabled",
    condition=button.is_enabled()
)

# Basic verification
element = CafeXMobile().get_web_element("xpath=//*@content-desc='element']")
assertions.verify_true(
    expected_message="Element should be visible",
    actual_message="Element is visible",
    condition=element.is_displayed()
)
```
## Available Methods

### True/False Validations
 - assert_true
```
assertions.assert_true(
    expected_message: str,  # What should happen
    actual_message: str,    # What actually happened
    condition: Any = None   # Optional condition to evaluate
)
```

 - verify_true
```
assertions.verify_true(
    expected_message: str,  # What should happen
    actual_message: str,    # What actually happened
    condition: Any = None   # Optional condition to evaluate
) 
```

 - assert_false
```
assertions.assert_false(
    expected_message: str,  # What should not happen
    actual_message: str,    # What actually happened
    condition: Any = None   # Optional condition to evaluate
)
```

 - verify_false
```
assertions.verify_false(
    expected_message: str,  # What should not happen
    actual_message: str,    # What actually happened
    condition: Any = None   # Optional condition to evaluate
)
)
```

### Equality Validations

 - assert_equal
```
assertions.assert_equal(
    actual: Any,                  # Actual value
    expected: Any,                # Expected value
    expected_message: str = None, # Custom expected message
    actual_message: str = None,   # Custom actual message
    actual_message_on_pass: str = None,  # Message when equal
    actual_message_on_fail: str = None   # Message when not equal
)
```

 - verify_equal
```
result = assertions.verify_equal(
    actual: Any,                  # Actual value
    expected: Any,                # Expected value
    expected_message: str = None, # Custom expected message
    actual_message: str = None,   # Custom actual message
    actual_message_on_pass: str = None,  # Message when equal
    actual_message_on_fail: str = None   # Message when not equal
) -> bool
```

## Usage in Different Test Types

### In BDD Tests
```
@when('user clicks login button')
def click_login():
    assertions.verify_true(
        "Button should be clickable",
        "Button is clickable",
        login_button.is_enabled()
    )
    assertions.assert_true(
        "Login initiated",
        "Login process started",
        login_button.click()
    )
```

### In pytest Tests
```
def test_login_process():
    # Standalone assertion
    assertions.verify_true(
        "Page loaded",
        "Login page displayed",
        login_page.is_displayed()
    )
    
    # Assertion within @step
    @step("Enter credentials")
    def enter_credentials():
        assertions.assert_true(
            "Credentials entered",
            "Username and password input successful",
            login_page.enter_credentials()
        )
```

### In unittest Tests
```
def test_login_validation(self):
    assertions.verify_equal(
        actual=login_page.get_error_message(),
        expected="Invalid credentials",
        expected_message="Error message should match",
        actual_message_on_pass="Correct error displayed",
        actual_message_on_fail="Unexpected error message"
    )
```
## How Assertions Appear in Reports

### Passing Assertion
```json
{
    "name": "Assert User clicks login: Button click successful",
    "expected": "Button click successful",
    "actual": "Click performed",
    "status": "P",
    "type": "assert",
    "timestamp": "2024-11-22T13:42:22.802",
    "screenshot": "path/to/screenshot.png"
}
```

### Failing Assertion
```json
{
    "name": "Assert Login validation: Invalid credentials",
    "expected": "Credentials valid",
    "actual": "Invalid username",
    "status": "F",
    "type": "assert",
    "timestamp": "2024-11-22T13:42:37.061",
    "screenshot": "path/to/error_screenshot.png",
    "exceptionDetail": "Assertion failed: Invalid credentials"
}
```

## Best Practices

### Assertion Messages

- Use clear, descriptive messages
- Include relevant context
- Be specific about expected vs actual results

### Choosing Between Assert and Verify

- Use assert_* for critical conditions that should stop test execution
- Use verify_* for non-critical validations that shouldn't stop the test

### Report Integration

- Assertions automatically integrate with reporting
- Screenshots are captured for both passes and failures
- Within steps, assertions are grouped under the step

