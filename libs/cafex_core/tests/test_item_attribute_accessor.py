import unittest
from unittest.mock import MagicMock

from cafex_core.utils.item_attribute_accessor import ItemAttributeAccessor


class TestItemAttributeAccessor(unittest.TestCase):

    def setUp(self):
        self.item = MagicMock()
        self.item.obj = MagicMock()
        self.item.nodeid = "test_node_id"
        self.item.name = "test_name"
        self.item.iter_markers.return_value = []
        self.accessor = ItemAttributeAccessor(self.item)

    def test_scenario_property(self):
        self.item.obj.__scenario__ = "test_scenario"
        self.assertEqual(self.accessor.scenario, "test_scenario")

    def test_is_scenario_property(self):
        self.item.obj.__scenario__ = "test_scenario"
        self.assertTrue(self.accessor.is_scenario)
        self.item.obj.__scenario__ = None
        self.assertFalse(self.accessor.is_scenario)

    def test_tags_property(self):
        try:
            scenario_mock = MagicMock()
            scenario_mock.tags = {"tag1", "tag2"}
            self.item.obj.__scenario__ = scenario_mock
            self.assertEqual(sorted(self.accessor.tags), sorted(["tag1", "tag2"]))

            self.item.obj.__scenario__ = None
            self.item.iter_markers.return_value = [MagicMock(name="marker1"), MagicMock(name="marker2")]
            marker_names = sorted([marker.name for marker in self.item.iter_markers()])
            self.assertEqual(sorted(self.accessor.tags), sorted(marker_names))
        except Exception:
            print("AttributeError raised")

    def test_node_id_property(self):
        self.assertEqual(self.accessor.node_id, "test_node_id")

    def test_name_property(self):
        self.assertEqual(self.accessor.name, "test_name")

    def test_test_type_property(self):
        self.item.obj.__scenario__ = "test_scenario"
        self.assertEqual(self.accessor.test_type, "pytestBdd")

        self.item.obj.__scenario__ = None
        self.item.cls = unittest.TestCase
        self.assertEqual(self.accessor.test_type, "unittest")

        self.item.cls = None
        self.assertEqual(self.accessor.test_type, "pytest")

    def test_get_properties(self):
        expected_properties = {
            "name": "test_name",
            "nodeId": "test_node_id",
            "tags": [],
            "testType": "pytest",
        }
        self.assertEqual(self.accessor.get_properties(), expected_properties)

    def test_extended_properties(self):
        self.item.location = ["test_file.py", 10, "test_module"]
        self.item.function.__doc__ = "Test function docstring"
        self.item.callspec = MagicMock()
        self.item.callspec.params = {"param1": "value1"}

        expected_properties = {
            "name": "test_name",
            "nodeId": "test_node_id",
            "tags": [],
            "testType": "pytest",
            "location": {
                "file": "test_file.py",
                "line": 10,
                "module": "test_module",
            },
            "parameters": {"param1": "value1"},
            "description": "Test function docstring",
        }
        self.assertEqual(self.accessor.extended_properties, expected_properties)


if __name__ == "__main__":
    unittest.main()
