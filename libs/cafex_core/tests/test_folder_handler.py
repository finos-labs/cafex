import unittest
import os
import shutil
from datetime import datetime
from unittest.mock import patch, MagicMock
from cafex_core.handlers.folder_handler import FolderHandler


class TestFolderHandler(unittest.TestCase):

    def setUp(self):
        self.test_dir = "test_dir"
        self.test_subdir = "subdir"
        self.test_file = "test_file.txt"
        self.test_filepath = os.path.join(self.test_dir, self.test_file)
        os.makedirs(self.test_dir, exist_ok=True)
        with open(self.test_filepath, "w") as f:
            f.write("test content")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_delete_files_in_folder(self):
        FolderHandler.delete_files_in_folder(self.test_dir)
        self.assertFalse(os.path.exists(self.test_filepath))

    @patch('os.remove')
    def test_delete_files_in_folder_oserror(self, mock_remove):
        mock_remove.side_effect = OSError("Mocked OSError")
        FolderHandler.delete_files_in_folder(self.test_dir)
        mock_remove.assert_called_once_with(self.test_filepath)

    @patch('shutil.rmtree')
    def test_delete_files_in_folder_with_subdir_oserror(self, mock_rmtree):
        subdir_path = os.path.join(self.test_dir, "subdir")
        os.makedirs(subdir_path, exist_ok=True)
        mock_rmtree.side_effect = OSError("Mocked OSError")
        FolderHandler.delete_files_in_folder(self.test_dir)
        mock_rmtree.assert_called_once_with(subdir_path)

    def test_delete_files_in_folder_with_subdir(self):
        os.makedirs(os.path.join(self.test_dir, self.test_subdir), exist_ok=True)
        FolderHandler.delete_files_in_folder(self.test_dir)
        self.assertFalse(os.path.exists(self.test_filepath))
        self.assertFalse(os.path.exists(os.path.join(self.test_dir, self.test_subdir)))

    @patch('shutil.rmtree')
    def test_delete_folder_exception(self, mock_rmtree):
        mock_rmtree.side_effect = Exception("Mocked Exception")
        FolderHandler.delete_folder(self.test_dir)
        mock_rmtree.assert_called_once_with(self.test_dir)

    def test_create_folder(self):
        new_folder = FolderHandler.create_folder(self.test_dir, "new_folder")
        self.assertTrue(os.path.exists(new_folder))

    def test_delete_folder(self):
        FolderHandler.delete_folder(self.test_dir)
        self.assertFalse(os.path.exists(self.test_dir))

    @patch('cafex_core.handlers.folder_handler.stop_server')
    def test_reorganize_result_folders(self, mock_stop_server):
        result_dir = os.path.join(self.test_dir, "result")
        history_dir = os.path.join(result_dir, "history")
        os.makedirs(result_dir, exist_ok=True)
        for i in range(12):
            subdir = os.path.join(result_dir, f"subdir_{i}")
            os.makedirs(subdir, exist_ok=True)
            with open(os.path.join(subdir, "file.txt"), "w") as f:
                f.write("test content")
            os.utime(subdir, (datetime.now().timestamp() - i * 86400, datetime.now().timestamp() - i * 86400))

        current_execution_uuid = "current_execution"
        os.makedirs(os.path.join(result_dir, current_execution_uuid), exist_ok=True)

        FolderHandler.reorganize_result_folders(self.test_dir, current_execution_uuid)

        self.assertTrue(os.path.exists(history_dir))
        history_subdirs = [d for d in os.listdir(history_dir) if os.path.isdir(os.path.join(history_dir, d))]
        current_year = datetime.now().year
        self.assertTrue(all(d.startswith(str(current_year)) for d in history_subdirs))

    @patch('cafex_core.handlers.folder_handler.stop_server')
    def test_reorganize_result_folders_with_timestamped_subdir(self, mock_stop_server):
        result_dir = os.path.join(self.test_dir, "result")
        history_dir = os.path.join(result_dir, "history")
        os.makedirs(result_dir, exist_ok=True)

        # Create a subdirectory with a timestamped name
        timestamped_subdir = os.path.join(result_dir, "20230101_000000_subdir")
        os.makedirs(timestamped_subdir, exist_ok=True)
        with open(os.path.join(timestamped_subdir, "file.txt"), "w") as f:
            f.write("test content")
        os.utime(timestamped_subdir, (datetime.now().timestamp(), datetime.now().timestamp()))

        current_execution_uuid = "current_execution"
        os.makedirs(os.path.join(result_dir, current_execution_uuid), exist_ok=True)

        FolderHandler.reorganize_result_folders(self.test_dir, current_execution_uuid)

        self.assertTrue(os.path.exists(history_dir))
        history_subdirs = [d for d in os.listdir(history_dir) if os.path.isdir(os.path.join(history_dir, d))]
        self.assertIn("20230101_000000_subdir", history_subdirs)


if __name__ == '__main__':
    unittest.main()
