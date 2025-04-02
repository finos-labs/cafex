"""This module contains the PytestAddOptionHook class which is used to add
custom options to the pytest command line.

These options can be used to customize the behavior of the pytest
framework for specific test runs.
"""


class PytestAddOptionHook:
    """A class that adds custom options to the pytest command line.

    Attributes:
        parser_obj (Parser): The parser object used to add options.

    Methods:
        add_option_hook: Adds the custom options to the pytest command line.
    """

    def __init__(self, parser_obj):
        """Initialize the PytestAddOptionHook class.

        Args:
            parser_obj: The parser object used to add options.
        """
        self.parser_obj = parser_obj

    def add_option_hook(self):
        """Adds the custom options to the pytest command line.

        The options include environment settings, selenium grid
        settings, browser settings, user credentials, custom parameters,
        reporting settings, and Jenkins settings.
        """

        self.parser_obj.addoption("--environment", action="store", default=None)
        self.parser_obj.addoption("--environment_type", action="store", default=None)
        self.parser_obj.addoption("--execution_environment", action="store", default=None)

        self.parser_obj.addoption("--selenium_grid_ip", action="store", default=None)
        self.parser_obj.addoption("--selenium_grid_port", action="store", default=None)
        self.parser_obj.addoption("--browser", action="store", default=None)
        self.parser_obj.addoption("--chrome_options", action="store", default=None)
        self.parser_obj.addoption("--firefox_options", action="store", default=None)
        self.parser_obj.addoption("--edge_options", action="store", default=None)
        self.parser_obj.addoption("--ie_options", action="store", default=None)
        self.parser_obj.addoption("--safari_options", action="store", default=None)

        self.parser_obj.addoption(
            "--mobile_os", action="store", default=None, help="Mobile OS: ios/android"
        )
        self.parser_obj.addoption(
            "--mobile_platform",
            action="store",
            default=None,
            help="Mobile Platform: browserstack/device/simulator",
        )
        self.parser_obj.addoption("--ios_device_json", action="store", default=None)
        self.parser_obj.addoption("--android_device_json", action="store", default=None)
        self.parser_obj.addoption("--username", action="store", default=None)
        self.parser_obj.addoption("--password", action="store", default=None)
        self.parser_obj.addoption("--default_db_user__username", action="store", default=None)
        self.parser_obj.addoption("--default_db_user__password", action="store", default=None)

        self.parser_obj.addoption("--custom_params", action="store", default=None)
        self.parser_obj.addoption("--config_keys", action="store", default=None)
        self.parser_obj.addoption("--kibana_reporting", action="store", default=None)
        self.parser_obj.addoption("--auto_dashboard_report", action="store", default=None)
        self.parser_obj.addoption("--default_keys", action="store", default=None)
        self.parser_obj.addoption("--default_values", action="store", default=None)

        self.parser_obj.addoption("--triggeredby", action="store", default=None)
        self.parser_obj.addoption("--jenkinsslavename", action="store", default=None)
        self.parser_obj.addoption("--reponame", action="store", default=None)
        self.parser_obj.addoption("--branchname", action="store", default=None)
        self.parser_obj.addoption("--devbuildnumber", action="store", default=None)
        self.parser_obj.addoption("--jenkins_build", action="store", default=None)
