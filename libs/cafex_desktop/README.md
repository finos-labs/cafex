# CAFE-DESKTOP

CAFE-DESKTOP is a Python package that provides tools and utilities for desktop application testing. It is part of the CAFEX (Centralized Automation Framework Enabler) monorepo.

### Features

CAFE-DESKTOP offers the following features:

- **Window management:** Supports interaction with desktop application windows, including opening, closing, and switching between windows.
- **Element interaction:** Provides methods to interact with desktop application elements, such as clicking, typing, and retrieving text.
- **Assertions:** Includes assertion methods specifically designed for desktop application testing, allowing for efficient validation of UI elements and behaviors.
- **Data-driven testing:** Supports data-driven testing approaches to execute tests with different data sets.
- **Reporting:** Integrates with CAFE's reporting capabilities to generate comprehensive test reports with screenshots and detailed logs.

### Getting Started

#### **Prerequisites**

- Python 3.12 or later
- pip 24 or later (Python package manager)

#### **Installation**

1. Install CAFE-DESKTOP using pip:

   ```
   pip install cafex-desktop
   ```

### Usage

CAFE-DESKTOP provides a set of intuitive methods and classes to facilitate desktop application testing. Here's a basic example for desktop application testing:

```python
from cafex_desktop import desktop_client_actions

# Create a desktop client actions object
desktop_actions = desktop_client_actions.DesktopClientActions()

# Launch a desktop application
desktop_actions.launch_application("C:\\Program Files\\ExampleApp\\ExampleApp.exe")

# Find an element and click on it
element = desktop_actions.get_desktop_element("name=SubmitButton")
desktop_actions.click(element)

# Validate the window title
assert desktop_actions.get_window_title() == "Success Window"