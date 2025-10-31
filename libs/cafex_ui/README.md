# CAFE-UI

CAFE-UI is a Python package that provides tools and utilities for web UI and mobile app testing. It is part of the CAFEX (Centralized Automation Framework Enabler) monorepo.

### Features

CAFE-UI offers the following features:

- **Driver management:** Supports various web browsers (Chrome, Firefox, Edge, etc.) and mobile platforms (iOS, Android).
- **Element interaction:** Provides methods to interact with web elements and mobile app elements, such as clicking, typing, and retrieving text.
- **Assertions:** Includes assertion methods specifically designed for UI testing, allowing for efficient validation of UI elements and behaviors.
- **Data-driven testing:** Supports data-driven testing approaches to execute tests with different data sets.
- **Reporting:** Integrates with CAFE's reporting capabilities to generate comprehensive test reports with screenshots and detailed logs.

### Getting Started

#### **Prerequisites**

- Python 3.12 or later
- pip 24 or later (Python package manager)

#### **Installation**

1. Install CAFE-UI using pip:

   ```
   pip install cafex-ui
   ```

### Usage

CAFE-UI provides a set of intuitive methods and classes to facilitate UI testing. Here's a basic example for web UI testing:

```python
from cafex_ui import web_client_actions

# Create a web client actions object
web_actions = web_client_actions.WebClientActions()

# Navigate to a website
web_actions.navigate("https://www.example.com")

# Find an element and click on it
element = web_actions.get_web_element("xpath=//button[text()='Submit']")
web_actions.click(element)

# Validate the page title
assert web_actions.get_title() == "Success Page"