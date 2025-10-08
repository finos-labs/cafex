"""This module contains the PytestRunTestSetup class which is used to handle
the setup of a test run in Pytest.

It includes methods to initialize the class and run the setup.
"""

import inspect

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.singletons_.session_ import SessionStore
from cafex_core.utils.date_time_utils import DateTimeActions
from cafex_core.utils.item_attribute_accessor import ItemAttributeAccessor


class PytestRunTestSetup:
    """A class that handles the setup of a test run in Pytest.

    Attributes:
        item_ (Item): The pytest item object.
        logger (Logger): The logger object.
        item_attribute_accessor (ItemAttributeAccessor): An attribute accessor for the item.
        session_store (SessionStore): The session store object.

    Methods:
        __init__: Initializes the PytestRunTestSetup class.
        run_setup: Runs the setup.
    """

    def __init__(self, item_):
        """Initialize the PytestRunTestSetup class.

        Args:
            item_: The pytest item object.
        """
        self.item_ = item_
        self.logger = CoreLogger(name=__name__).get_logger()
        self.item_attribute_accessor = None
        self.session_store = SessionStore()
        self.date_time_util = DateTimeActions()

    def run_setup(self):
        """Runs the setup.

        It logs the setup event, the node ID, the tags, and whether the
        item is a BDD scenario. It also updates the reporting attribute
        of the session store.
        """
        self.item_attribute_accessor = ItemAttributeAccessor(self.item_)

        test_name = self.item_.name
        node_id = self.item_.nodeid
        tags = list(self.item_attribute_accessor.tags)
        test_type = self.item_attribute_accessor.test_type
        self.logger.info(f"Running test : {test_name}")
        self.logger.info(f"Node Id : {node_id}")
        self.logger.info(f"tags : {tags}")
        self.logger.info(f"Test Type : {test_type}")

        # Set the current_test in the session store
        self.session_store.current_test = node_id

        # Initialize basic test data structure for all tests
        if node_id not in self.session_store.reporting["tests"]:
            test_data = {
                "name": test_name,
                "testType": test_type,
                "nodeId": node_id,
                "testStatus": "Not Executed",
                "startTime": self.date_time_util.get_current_date_time(),
                "endTime": None,
                "duration": None,
                "durationSeconds": None,
                "isDataDriven": False,
                "isOutline": False,
                "example": None,
                "tags": tags,
                "steps": [],
                "evidence": {"screenshots": [], "exceptions": [], "errorMessages": []},
            }

            if test_type == "pytest":
                is_parametrized = hasattr(self.item_, "callspec") and self.item_.callspec.params
                test_data.update(
                    {
                        "isDataDriven": True if is_parametrized else False,
                        "isOutline": False,  # Regular pytest tests are never outlines
                        "example": str(self.item_.callspec.params) if is_parametrized else None,
                    }
                )
            if test_type == "unittest":
                # Check if the test method uses subTest
                test_method = getattr(self.item_.cls, self.item_.name)
                if "self.subTest" in inspect.getsource(test_method):
                    test_data.update(
                        {
                            "isDataDriven": True,
                            "isOutline": False,
                            "example": "unittest with subTest",
                        }
                    )

            self.session_store.reporting["tests"][node_id] = test_data

        if hasattr(self.item_.function, "pytestmark"):
            for marker in self.item_.function.pytestmark:
                if marker.name == "ui_web" and not self.item_attribute_accessor.is_scenario:
                    from cafex_ui.web_client.ui_web_driver_initializer import (
                        WebDriverInitializer,
                    )
                    self.logger.info("Setting up web driver for non-BDD test.")
                    self.session_store.ui_scenario = True
                    WebDriverInitializer().initialize_driver()
                if marker.name == "playwright_web" and not self.item_attribute_accessor.is_scenario:
                    from cafex_ui.web_client.ui_web_driver_initializer import (
                        WebDriverInitializer,
                    )
                    self.logger.info("Setting up playwright web driver for non-BDD test.")
                    self.session_store.playwright_ui_scenario = True
                    WebDriverInitializer().initialize_playwright_driver()
                if marker.name == "mobile_app" and not self.item_attribute_accessor.is_scenario:
                    from cafex_ui.mobile_client.mobile_driver_initializer import (
                        MobileDriverInitializer,
                    )
                    self.logger.info("Setting up mobile driver for non-BDD test.")
                    self.session_store.mobile_ui_scenario = True
                    MobileDriverInitializer().initialize_driver()
                if marker.name == "ui_desktop_client" and not self.item_attribute_accessor.is_scenario:
                    from cafex_desktop.desktop_client.desktop_client_driver_initializer \
                        import DesktopClientDriverInitializer
                    self.logger.info("Setting up Desktop Client Handler for non-BDD test.")
                    self.session_store.ui_desktop_client_scenario = True
                    DesktopClientDriverInitializer().initialize_driver()
