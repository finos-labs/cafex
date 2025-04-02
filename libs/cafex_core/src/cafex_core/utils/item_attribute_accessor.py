"""This module contains the ItemAttributeAccessor class which is used to access
various attributes of a pytest item.

It includes methods and properties to get the scenario, check if the
item is a scenario, get the tags, get the node ID, get the name, and get
all properties.
"""

import unittest


class ItemAttributeAccessor:
    """A class that accesses various attributes of a pytest item.

    Attributes:
        item (Item): The pytest item object.
        properties_names (set): A set of property names.

    Properties:
        scenario: Returns the scenario attribute of the item.
        is_scenario: Returns a boolean indicating if the item is a scenario.
        tags: Returns a list of tags of the scenario.
        node_id: Returns the node ID of the item.
        name: Returns the name of the item.

    Methods:
        __init__: Initializes the ItemAttributeAccessor class.
        get_properties: Returns a dictionary of all properties.
    """

    def __init__(self, item):
        """Initialize the ItemAttributeAccessor class.

        Args:
            item: The pytest item object.
        """
        self.item = item
        self.properties_names = {"name", "node_id", "tags", "test_type"}

    @property
    def scenario(self):
        """Returns the scenario attribute of the item.

        Returns:
            Scenario: The scenario attribute of the item.
        """
        return getattr(self.item.obj, "__scenario__", None)

    @property
    def is_scenario(self):
        """Returns a boolean indicating if the item is a scenario.

        Returns:
            bool: True if the item is a scenario, False otherwise.
        """
        return bool(getattr(self.item.obj, "__scenario__", False))

    @property
    def tags(self):
        """Returns a list of tags of the scenario."""
        if self.is_scenario:
            # For pytest-bdd scenarios
            return list(getattr(self.scenario, "tags", set()))
        return [marker.name for marker in self.item.iter_markers()]

    @property
    def node_id(self):
        """Returns the node ID of the item.

        Returns:
            str: The node ID of the item.
        """
        return self.item.nodeid

    @property
    def name(self):
        """Returns the name of the item.

        Returns:
            str: The name of the item.
        """
        return self.item.name

    @property
    def test_type(self):
        """Returns the type of the test."""
        if self.is_scenario:
            return "pytestBdd"
        if (
            hasattr(self.item, "cls")
            and self.item.cls is not None
            and isinstance(self.item.cls, type)
            and issubclass(self.item.cls, unittest.TestCase)
        ):
            return "unittest"
        return "pytest"

    def get_properties(self):
        """Returns a dictionary of all properties.

        Returns:
            dict: A dictionary of all properties.
        """
        properties = {
            "name": self.name,
            "nodeId": self.node_id,
            "tags": self.tags,
            "testType": self.test_type,
        }
        return properties

    @property
    def extended_properties(self):
        """Returns additional test metadata."""
        props = self.get_properties()

        # Add location info
        props.update(
            {
                "location": {
                    "file": self.item.location[0],
                    "line": self.item.location[1],
                    "module": self.item.location[2] if len(self.item.location) > 2 else None,
                }
            }
        )

        # Add parametrization info if available
        if hasattr(self.item, "callspec"):
            props["parameters"] = dict(self.item.callspec.params)

        # Add function docstring if available
        if self.item.function.__doc__:
            props["description"] = self.item.function.__doc__.strip()

        return props
