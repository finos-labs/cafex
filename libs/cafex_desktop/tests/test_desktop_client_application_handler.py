import unittest
from unittest.mock import MagicMock, patch
from pywinauto import Application

from cafex_desktop.desktop_client.desktop_application_handler import DesktopApplicationHandler


class TestDesktopClientApplicationHandler(unittest.TestCase):
    def setUp(self):
        # Create an instance of the handler with mocked dependencies
        self.handler = DesktopApplicationHandler()
        self.handler.desktop_client_config = {}
        self.handler.launch = MagicMock()
        self.handler.logger = MagicMock()
        self.handler.connect_to_app = MagicMock()
        self.mock_app = MagicMock(spec=Application)

    def test_get_handler_with_app_path(self):
        # Test when app_path is provided
        self.handler.desktop_client_config = {"app_path": "path/to/app"}
        self.handler.launch.return_value = "Mocked Application"

        result = self.handler.get_handler(app_path="path/to/app")
        self.handler.launch.assert_called_once_with("path/to/app")
        self.assertEqual(result, "Mocked Application")

    def test_get_handler_with_application_name(self):
        # Test when application_name is provided
        self.handler.launch_application = MagicMock()
        self.handler.desktop_client_config = {"application_name": "notepad"}
        self.handler.launch_application.return_value = "Mocked Application"

        result = self.handler.get_handler(application_name="notepad")
        self.handler.launch_application.assert_called_once_with("notepad")
        self.assertEqual(result, "Mocked Application")

    def test_get_handler_with_config_values(self):
        # Test when values are taken from the configuration
        self.handler.desktop_client_config = {
            "application_name": "excel",
            "app_path": "path/to/excel",
        }
        self.handler.launch.return_value = "Mocked Application"

        result = self.handler.get_handler()
        self.handler.launch.assert_called_once_with("path/to/excel")
        self.assertEqual(result, "Mocked Application")

    @patch('psutil.process_iter')
    def test_launch_new_application(self, mock_process_iter):
        # Simulate a process that needs to be killed
        mock_proc = MagicMock()
        mock_proc.name.return_value = "excel.exe"
        mock_process_iter.return_value = [mock_proc]

        mock_app = MagicMock()
        mock_window = MagicMock()
        mock_app.window.return_value = mock_window
        self.handler.connect_to_app.return_value = mock_app

        result = self.handler.launch_application(
            application_name="excel",
            connect_to_open_app=False,
            process_name="excel.exe",
            app_path="path/to/excel"
        )

        mock_proc.kill.assert_called_once()
        self.handler.launch.assert_called_once_with("path/to/excel")
        self.handler.connect_to_app.assert_called_once_with(title_re="excel", control_type="Window", timeout=300)
        mock_window.maximize.assert_called_once()
        self.assertEqual(result, mock_app)

    def test_connect_to_existing_application(self):
        mock_app = MagicMock()
        mock_window = MagicMock()
        mock_app.window.return_value = mock_window
        self.handler.connect_to_app.return_value = mock_app

        result = self.handler.launch_application(
            application_name="notepad",
            connect_to_open_app=True,
            process_name="notepad.exe",
            app_path="unused"
        )

        self.handler.connect_to_app.assert_called_once_with(title_re="notepad", control_type="Window", timeout=60)
        mock_window.maximize.assert_called_once()
        self.assertEqual(result, mock_app)

    @patch('psutil.process_iter')
    def test_launch_with_config_fallbacks(self, mock_process_iter):
        self.handler.desktop_client_config = {
            "connect_to_open_app": False,
            "process_name": "excel.exe",
            "app_path": "fallback/path/excel.exe"
        }

        mock_proc = MagicMock()
        mock_proc.name.return_value = "excel.exe"
        mock_process_iter.return_value = [mock_proc]

        mock_app = MagicMock()
        mock_window = MagicMock()
        mock_app.window.return_value = mock_window
        self.handler.connect_to_app.return_value = mock_app

        result = self.handler.launch_application(application_name="excel")

        mock_proc.kill.assert_called_once()
        self.handler.launch.assert_called_once_with("fallback/path/excel.exe")
        self.handler.connect_to_app.assert_called_once()
        self.assertEqual(result, mock_app)


if __name__ == "__main__":
    unittest.main()
