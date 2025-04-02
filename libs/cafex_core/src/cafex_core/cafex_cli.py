"""
Command-line interface for the Cafex automation framework.

This module provides the CLI functionality for Cafex, making it easy to
initialize, create, run, and manage automation projects.
"""

import argparse
import os
import subprocess
import sys


def cafex_help():
    """Print the help message for cafex."""
    print(r"""

   _____          ______ ________   __ 
  / ____|   /\   |  ____|  ____\ \ / / 
 | |       /  \  | |__  | |__   \ V /  
 | |      / /\ \ |  __| |  __|   > <   
 | |____ / ____ \| |    | |____ / . \  
  \_____/_/    \_\_|    |______/_/ \_\ 
                                       
Cafex - Python Test Automation Framework

Usage: cafex <command> [options]

Available Commands:

  help           Show this help message.  (cafex or cafex help)
  init           Initialize a new automation project.
  create <type>  Create a new test suite, test case, or page object.
  run            Run the tests. (Options for selecting tests to run)
  report         Generate a test report.
  list           List available test suites, test cases, or page objects.
  config         View or modify project configuration.
  version        Show the version of Cafex.

Detailed Command Help:

  To get detailed help for a specific command, use:
  cafex <command> --help  (e.g., cafex create --help)

Examples:

  cafex init my_project
  cafex create testsuite LoginTests
  cafex run
  cafex report
""")


def cafex_init(project_name):
    """Initialize a new automation project.

    Args:
        project_name: Name of the project to initialize
    """
    print(f"Initializing new project: {project_name}")
    try:
        # Create directory structure
        os.makedirs(os.path.join(project_name, "features", "tests", "pytest_bdd_feature"), exist_ok=True)
        os.makedirs(os.path.join(project_name, "features", "services"), exist_ok=True)
        os.makedirs(os.path.join(project_name, "features", "forms"), exist_ok=True)
        os.makedirs(os.path.join(project_name, "features", "configuration"), exist_ok=True)
        os.makedirs(os.path.join(project_name, "result"), exist_ok=True)

        # Create config.yml
        with open(os.path.join(project_name, "config.yml"), "w") as f:
            f.write("""# Cafex Configuration File

# Environment settings
execution_environment: dev
environment_type: cloud
use_grid: false
selenium_grid_ip: "localhost"
current_execution_browser: chrome

# Directory paths
service_description: services/service_description
service_payloads: services/payloads

# Environment configurations
env:
  dev:
    cloud:
      base_url: "https://jsonplaceholder.typicode.com"
      default_user:
        username: ""
        password: ""
  staging:
    cloud:
      base_url: "https://jsonplaceholder.typicode.com"
      default_user:
        username: ""
        password: ""
  prod:
    cloud:
      base_url: "https://jsonplaceholder.typicode.com"
      default_user:
        username: ""
        password: ""
""")

        # Create a sample feature file
        feature_path = os.path.join(project_name, "features", "tests", "pytest_bdd_feature", "sample.feature")
        with open(feature_path, "w") as f:
            f.write("""Feature: Sample feature

  @sample
  Scenario: Sample test scenario
    Given the user is on the homepage
    When the user clicks on the login button
    Then the login form should be displayed
""")

        # Create sample step definitions
        steps_path = os.path.join(project_name, "features", "tests", "pytest_bdd_feature", "test_sample.py")
        with open(steps_path, "w") as f:
            f.write("""from pytest_bdd import (
    given,
    scenario,
    then,
    when,
)

@scenario('sample.feature', 'Sample test scenario')
def test_sample_scenario():
    \"\"\"Sample test scenario.\"\"\"
    pass

@given("the user is on the homepage")
def user_on_homepage():
    \"\"\"User is on the homepage.\"\"\"
    print("User is on the homepage")

@when("the user clicks on the login button")
def user_clicks_login():
    \"\"\"User clicks login button.\"\"\"
    print("User clicks login button")

@then("the login form should be displayed")
def login_form_displayed():
    \"\"\"Login form is displayed.\"\"\"
    print("Login form is displayed")
    assert True  # This would be a real assertion in a real test
""")

        # Create conftest.py
        conftest_path = os.path.join(project_name, "conftest.py")
        with open(conftest_path, "w") as f:
            f.write("""import pytest

def pytest_configure(config):
    \"\"\"Configure pytest.\"\"\"
    pass

def pytest_addoption(parser):
    \"\"\"Add command line options to pytest.\"\"\"
    parser.addoption("--browser", action="store", default="chrome", help="Browser to use for UI tests")
""")

        # Create pytest.ini
        pytest_ini_path = os.path.join(project_name, "pytest.ini")
        with open(pytest_ini_path, "w") as f:
            f.write("""[pytest]
markers =
    sample: marks tests as sample tests
""")

        # Create .gitignore
        gitignore_path = os.path.join(project_name, ".gitignore")
        with open(gitignore_path, "w") as f:
            f.write("""# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Virtual environment
venv/
ENV/

# Testing
.coverage
htmlcov/
.pytest_cache/
result/
reports/

# IDE specific files
.idea/
.vscode/
*.swp
*.swo
""")

        print(f"Project '{project_name}' initialized successfully.")
        print(f"\nTo get started, navigate to your project directory:")
        print(f"  cd {project_name}")
        print(f"\nRun the sample test with:")
        print(f"  pytest features/tests/pytest_bdd_feature/test_sample.py -v")

    except OSError as e:
        print(f"Error initializing project: {e}")


def cafex_create(item_type, item_name):
    """Create a new test suite, test case, or page object.

    Args:
        item_type: Type of item to create (testsuite, testcase, pageobject)
        item_name: Name of the item to create
    """
    print(f"Creating {item_type}: {item_name}")

    if item_type == "testsuite":
        # Create a new test suite with feature file and step definitions
        feature_dir = os.path.join("features", "tests", "pytest_bdd_feature")
        if not os.path.exists(feature_dir):
            try:
                os.makedirs(feature_dir)
            except OSError as e:
                print(f"Error creating directory: {e}")
                return

        # Create feature file
        feature_path = os.path.join(feature_dir, f"{item_name.lower()}.feature")
        try:
            with open(feature_path, "w") as f:
                f.write(f"""Feature: {item_name}

  @{item_name.lower()}
  Scenario: {item_name} scenario example
    Given a precondition
    When an action is performed
    Then a result should be observed
""")
        except OSError as e:
            print(f"Error creating feature file: {e}")
            return

        # Create step definitions
        steps_path = os.path.join(feature_dir, f"test_{item_name.lower()}.py")
        try:
            with open(steps_path, "w") as f:
                f.write(f"""from pytest_bdd import (
    given,
    scenario,
    then,
    when,
)

@scenario('{item_name.lower()}.feature', '{item_name} scenario example')
def test_{item_name.lower()}_scenario():
    \"\"\"{item_name} scenario example.\"\"\"
    pass

@given("a precondition")
def a_precondition():
    \"\"\"Define your precondition.\"\"\"
    print("Precondition is set up")

@when("an action is performed")
def an_action():
    \"\"\"Define your action.\"\"\"
    print("Action is performed")

@then("a result should be observed")
def a_result():
    \"\"\"Define your expected result.\"\"\"
    print("Result is observed")
    assert True  # Replace with actual assertion
""")
            print(f"Test suite '{item_name}' created successfully.")
            print(f"- Feature file: {feature_path}")
            print(f"- Step definitions: {steps_path}")
            print(f"\nRun your test with: pytest {steps_path} -v")
        except OSError as e:
            print(f"Error creating step definitions: {e}")

    elif item_type == "testcase":
        # Add a scenario to an existing feature file
        feature_dir = os.path.join("features", "tests", "pytest_bdd_feature")

        # List existing feature files
        try:
            feature_files = [f for f in os.listdir(feature_dir) if f.endswith(".feature")]
        except FileNotFoundError:
            print(f"Error: Directory '{feature_dir}' not found. Make sure you're in a cafex project.")
            return

        if not feature_files:
            print("No feature files found. Create a test suite first with 'cafex create testsuite <name>'.")
            return

        print("Available feature files:")
        for i, file in enumerate(feature_files):
            print(f"{i + 1}. {file}")

        try:
            selection = int(input("\nSelect a feature file (number): ")) - 1
            if selection < 0 or selection >= len(feature_files):
                print("Invalid selection.")
                return
        except ValueError:
            print("Invalid input. Please enter a number.")
            return

        selected_file = feature_files[selection]
        feature_path = os.path.join(feature_dir, selected_file)

        # Add scenario to feature file
        try:
            with open(feature_path, "a") as f:
                f.write(f"""
  @{item_name.lower()}
  Scenario: {item_name}
    Given a precondition for {item_name}
    When a specific action for {item_name} is performed
    Then a specific result for {item_name} should be observed
""")
            print(f"Test case '{item_name}' added to feature file '{selected_file}'.")
            print("Don't forget to add corresponding step definitions to your test file.")
        except OSError as e:
            print(f"Error updating feature file: {e}")

    elif item_type == "pageobject":
        # Create a page object
        pages_dir = os.path.join("features", "forms")
        if not os.path.exists(pages_dir):
            try:
                os.makedirs(pages_dir)
            except OSError as e:
                print(f"Error creating directory: {e}")
                return

        page_path = os.path.join(pages_dir, f"{item_name.lower()}.py")
        try:
            with open(page_path, "w") as f:
                f.write(f"""from cafex_ui.web_client.web_client_actions import WebClientActions

class {item_name}:
    \"\"\"Page object for {item_name} page.\"\"\"

    def __init__(self):
        \"\"\"Initialize {item_name} page object.\"\"\"
        self.web_client = WebClientActions()

        # Define your locators here
        self.locators = {{
            "example_element": "//div[@id='example']",
            # Add more locators as needed
        }}

    def navigate_to_page(self, url):
        \"\"\"Navigate to the page.

        Args:
            url: URL to navigate to

        Returns:
            bool: True if navigation was successful
        \"\"\"
        return self.web_client.navigate_to_url(url)

    def is_page_loaded(self):
        \"\"\"Check if the page is loaded.

        Returns:
            bool: True if the page is loaded
        \"\"\"
        return self.web_client.is_element_visible(self.locators["example_element"])

    # Add more methods as needed
""")
            print(f"Page object '{item_name}' created at {page_path}")
        except OSError as e:
            print(f"Error creating page object: {e}")
    else:
        print(f"Invalid item type: {item_type}. Must be 'testsuite', 'testcase', or 'pageobject'.")


def cafex_run(args):
    """Run the tests.

    Args:
        args: Additional arguments to pass to pytest
    """
    print("Running tests...")
    try:
        pytest_args = ["pytest"]

        # Add common options
        if not any(arg.startswith('-v') for arg in args):
            pytest_args.append("-v")  # Add verbose by default if not specified

        # Add any additional arguments
        pytest_args.extend(args)

        print(f"Executing: {' '.join(pytest_args)}")
        result = subprocess.run(pytest_args, check=False)

        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ Tests failed with return code: {result.returncode}")

    except FileNotFoundError:
        print("Error: pytest not found. Please install pytest: pip install pytest")
    except Exception as e:
        print(f"Error running tests: {e}")


def cafex_report():
    """Generate a test report."""
    print("Generating test report...")

    # Check if result directory exists and contains reports
    result_dir = "result"
    if not os.path.exists(result_dir):
        print("No test results found. Run tests first with 'cafex run'.")
        return

    # Find the most recent result directory
    try:
        result_dirs = [d for d in os.listdir(result_dir) if os.path.isdir(os.path.join(result_dir, d))]
        if not result_dirs:
            print("No test results found. Run tests first with 'cafex run'.")
            return

        # Sort by modification time (most recent first)
        result_dirs.sort(key=lambda d: os.path.getmtime(os.path.join(result_dir, d)), reverse=True)
        latest_dir = os.path.join(result_dir, result_dirs[0])

        # Check if report exists
        report_path = os.path.join(latest_dir, "report.html")
        if not os.path.exists(report_path):
            print("No HTML report found in the latest results directory.")
            return

        # Open the report in the default browser
        print(f"Opening report: {report_path}")
        if sys.platform == 'win32':
            os.startfile(report_path)
        elif sys.platform == 'darwin':  # macOS
            subprocess.run(['open', report_path], check=True)
        else:  # Linux
            subprocess.run(['xdg-open', report_path], check=True)

    except Exception as e:
        print(f"Error generating/opening report: {e}")


def cafex_list(item_type):
    """List available test suites, test cases, or page objects.

    Args:
        item_type: Type of items to list (testsuites, testcases, pageobjects)
    """
    print(f"Listing {item_type}...")

    if item_type == "testsuites":
        feature_dir = os.path.join("features", "tests", "pytest_bdd_feature")
        try:
            feature_files = [f for f in os.listdir(feature_dir) if f.endswith(".feature")]
            if feature_files:
                print("\nAvailable Test Suites:")
                for file in feature_files:
                    print(f"- {file[:-8]}")  # Remove '.feature' extension
            else:
                print("No test suites found.")
        except FileNotFoundError:
            print(f"Error: Directory '{feature_dir}' not found. Make sure you're in a cafex project.")

    elif item_type == "testcases":
        feature_dir = os.path.join("features", "tests", "pytest_bdd_feature")
        try:
            feature_files = [f for f in os.listdir(feature_dir) if f.endswith(".feature")]
            if not feature_files:
                print("No feature files found.")
                return

            print("\nTest Cases by Feature:")
            for file in feature_files:
                feature_path = os.path.join(feature_dir, file)
                try:
                    with open(feature_path, "r") as f:
                        content = f.read()
                        scenarios = [line.strip() for line in content.split("\n") if
                                     line.strip().startswith("Scenario:")]
                        if scenarios:
                            print(f"\n{file}:")
                            for scenario in scenarios:
                                print(f"  - {scenario[9:].strip()}")  # Remove 'Scenario: ' prefix
                except OSError as e:
                    print(f"Error reading {file}: {e}")
        except FileNotFoundError:
            print(f"Error: Directory '{feature_dir}' not found. Make sure you're in a cafex project.")

    elif item_type == "pageobjects":
        pages_dir = os.path.join("features", "forms")
        try:
            page_files = [f for f in os.listdir(pages_dir) if f.endswith(".py") and not f.startswith("__")]
            if page_files:
                print("\nAvailable Page Objects:")
                for file in page_files:
                    print(f"- {file[:-3]}")  # Remove '.py' extension
            else:
                print("No page objects found.")
        except FileNotFoundError:
            print(f"Error: Directory '{pages_dir}' not found. Make sure you're in a cafex project.")

    else:
        print(f"Invalid item type: {item_type}. Must be 'testsuites', 'testcases', or 'pageobjects'.")


def cafex_config():
    """View or modify project configuration."""
    print("Configuration management...")

    config_file = "config.yml"
    if not os.path.exists(config_file):
        print(f"Configuration file '{config_file}' not found. Make sure you're in a cafex project.")
        return

    try:
        # Read the configuration file
        with open(config_file, "r") as f:
            config_content = f.read()

        print(f"\nCurrent configuration ({config_file}):")
        print("-" * 40)
        print(config_content)
        print("-" * 40)

        # Ask if user wants to edit
        edit = input("\nDo you want to edit the configuration? (y/n): ").lower()
        if edit == 'y':
            # Determine which editor to use
            if 'EDITOR' in os.environ:
                editor = os.environ['EDITOR']
            elif sys.platform == 'win32':
                editor = 'notepad'
            else:
                editor = 'nano'  # Default for Unix-like systems

            try:
                subprocess.run([editor, config_file], check=True)
                print(f"\nConfiguration file '{config_file}' has been updated.")
            except Exception as e:
                print(f"Error opening editor: {e}")
    except Exception as e:
        print(f"Error handling configuration: {e}")


def cafex_version():
    """Show the version of Cafex."""
    try:
        from cafex_core import __version__
        print(f"Cafex version {__version__}")
    except ImportError:
        print("Cafex version information not available.")


def main():
    """Main entry point of the cafex program."""
    parser = argparse.ArgumentParser(
        description="Cafex - Python Test Automation Framework",
        usage="cafex <command> [options]"
    )
    parser.add_argument(
        "command",
        help="Command to execute",
        nargs='?'
    )
    parser.add_argument(
        "extra_args",
        nargs="*",
        help="Extra arguments for the command"
    )

    args = parser.parse_args()

    if not args.command:
        cafex_help()
        return

    if args.command == "help":
        cafex_help()
    elif args.command == "init":
        if len(args.extra_args) != 1:
            print("Usage: cafex init <project_name>")
            return
        cafex_init(args.extra_args[0])
    elif args.command == "create":
        if len(args.extra_args) != 2:
            print("Usage: cafex create <type> <name>")
            print("  <type> can be: testsuite, testcase, pageobject")
            return
        cafex_create(args.extra_args[0], args.extra_args[1])
    elif args.command == "run":
        cafex_run(args.extra_args)
    elif args.command == "report":
        cafex_report()
    elif args.command == "list":
        if len(args.extra_args) != 1:
            print("Usage: cafex list <type>")
            print("  <type> can be: testsuites, testcases, pageobjects")
            return
        cafex_list(args.extra_args[0])
    elif args.command == "config":
        cafex_config()
    else:
        print(f"Unknown command: {args.command}")
        cafex_help()


if __name__ == "__main__":
    main()