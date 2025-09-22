import unittest
import os
import json
from cafex_core.handlers.file_handler import FileHandler

class TestFileHandler(unittest.TestCase):

    def setUp(self):
        self.test_dir = "test_dir"
        self.test_file = "test_file.json"
        self.test_filepath = os.path.join(self.test_dir, self.test_file)
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.test_filepath):
            os.remove(self.test_filepath)
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def test_create_json_file(self):
        data = {"key": "value"}
        FileHandler.create_json_file(self.test_dir, self.test_file, data)
        self.assertTrue(os.path.exists(self.test_filepath))
        with open(self.test_filepath, "r") as file:
            content = json.load(file)
        self.assertEqual(content, data)

    def test_create_json_file_no_data(self):
        FileHandler.create_json_file(self.test_dir, self.test_file)
        self.assertTrue(os.path.exists(self.test_filepath))
        with open(self.test_filepath, "r") as file:
            content = json.load(file)
        self.assertEqual(content, {})

    def test_delete_file(self):
        FileHandler.create_json_file(self.test_dir, self.test_file)
        self.assertTrue(os.path.exists(self.test_filepath))
        FileHandler.delete_file(self.test_filepath)
        self.assertFalse(os.path.exists(self.test_filepath))

    def test_delete_nonexistent_file(self):
        self.assertFalse(os.path.exists(self.test_filepath))
        FileHandler.delete_file(self.test_filepath)  # Should not raise an exception

    def test_add_data_to_json_file(self):
        initial_data = {"key1": "value1"}
        additional_data = {"key2": "value2"}
        FileHandler.create_json_file(self.test_dir, self.test_file, initial_data)
        FileHandler.add_data_to_json_file(self.test_filepath, additional_data)
        with open(self.test_filepath, "r") as file:
            content = json.load(file)
        self.assertEqual(content, {"key1": "value1", "key2": "value2"})

    def test_read_data_from_json_file(self):
        data = {"key": "value"}
        FileHandler.create_json_file(self.test_dir, self.test_file, data)
        read_data = FileHandler.read_data_from_json_file(self.test_filepath)
        self.assertEqual(read_data, data)

    def test_read_data_from_nonexistent_file(self):
        with self.assertRaises(FileNotFoundError):
            FileHandler.read_data_from_json_file(self.test_filepath)

    def test_read_data_from_invalid_json_file(self):
        with open(self.test_filepath, "w") as file:
            file.write("Invalid JSON")
        with self.assertRaises(ValueError):
            FileHandler.read_data_from_json_file(self.test_filepath)

if __name__ == '__main__':
    unittest.main()