import unittest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path, PosixPath
from cafex_core.reporting_._report_viewer._server_scripts._server_generator import _save_server_info, \
    create_server_script


class TestServerScripts(unittest.TestCase):

    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_generator.open', new_callable=mock_open)
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_generator.json.dump')
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_generator.logger.warning')
    def test_save_server_info_success(self, mock_warning, mock_json_dump, mock_open):
        directory = Path('/fake/dir')
        port = 8080
        _save_server_info(directory, port)
        mock_open.assert_called_once_with(directory / ".server_info", "w")
        mock_json_dump.assert_called_once_with({"port": port}, mock_open())

    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_generator.open',
           side_effect=Exception("File error"))
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_generator.logger.warning')
    def test_save_server_info_failure(self, mock_warning, mock_open):
        directory = Path('/fake/dir')
        port = 8080
        _save_server_info(directory, port)
        mock_open.assert_called_once_with(directory / ".server_info", "w")
        mock_warning.assert_called_once_with("Could not save server info: File error")

    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_generator._save_server_info')
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_generator.open', new_callable=mock_open)
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_generator.os.name', 'nt')
    def test_create_server_script_windows(self, mock_open, mock_save_server_info):
        directory = Path('/fake/dir')
        port = 8080
        script_path = create_server_script(directory, port)
        expected_script_content = f"""@echo off
echo Starting server...
cd /d "{directory}"
echo.
echo Server running at http://localhost:{port}
echo.
echo To stop the server, close this window
echo.
python -m http.server {port} --bind localhost --directory "{directory}"
del /f .server_info
"""
        mock_open.assert_called_once_with(directory / "start_report_server.bat", "w", newline="\n")
        mock_open().write.assert_called_once_with(expected_script_content)
        self.assertEqual(script_path, directory / "start_report_server.bat")

    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_generator._save_server_info')
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_generator.open', new_callable=mock_open)
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_generator.os.name', 'posix')
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_generator.os.chmod')
    @patch('pathlib.Path', new_callable=lambda: PosixPath)
    def test_create_server_script_unix(self, mock_path, mock_chmod, mock_open, mock_save_server_info):
        directory = Path('/fake/dir')
        port = 8080
        script_path = create_server_script(directory, port)
        expected_script_content = f"""#!/bin/bash
echo "Starting server..."
cd "{directory}"
echo "Server running at http://localhost:{port}"
echo ""
echo "To stop the server, press Ctrl+C"
python3 -m http.server {port} --bind localhost --directory "{directory}"
rm -f .server_info
"""
        mock_open.assert_called_once_with(directory / "start_report_server.sh", "w", newline="\n")
        mock_open().write.assert_called_once_with(expected_script_content)
        mock_chmod.assert_called_once_with(directory / "start_report_server.sh", 0o755)
        self.assertEqual(script_path, directory / "start_report_server.sh")

    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_generator._save_server_info',
           side_effect=Exception("Save error"))
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_generator.logger.error')
    def test_create_server_script_save_info_failure(self, mock_error, mock_save_server_info):
        directory = Path('/fake/dir')
        port = 8080
        with self.assertRaises(Exception) as context:
            create_server_script(directory, port)
        self.assertEqual(str(context.exception), "Save error")
        mock_error.assert_called_once_with("Error creating server script: Save error")


if __name__ == '__main__':
    unittest.main()
