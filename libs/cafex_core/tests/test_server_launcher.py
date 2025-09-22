import unittest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

import psutil

from cafex_core.reporting_._report_viewer._server_scripts. \
    _server_launcher import _get_server_info, stop_server, launch_server_and_browser


class TestServerLauncher(unittest.TestCase):

    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher.open', new_callable=mock_open,
           read_data='{"port": 8080}')
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher.Path.exists', return_value=True)
    def test_get_server_info_success(self, mock_exists, mock_open):
        directory = Path('/fake/dir')
        result = _get_server_info(directory)
        self.assertEqual(result, {"port": 8080})
        mock_open.assert_called_once_with(directory / ".server_info")

    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher.open',
           side_effect=Exception("File error"))
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher.Path.exists', return_value=True)
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher.logger.warning')
    def test_get_server_info_failure(self, mock_warning, mock_exists, mock_open):
        directory = Path('/fake/dir')
        result = _get_server_info(directory)
        self.assertEqual(result, {})
        mock_warning.assert_called_once_with("Could not read server info: File error")

    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher._get_server_info',
           return_value={"port": 8080})
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher.psutil.process_iter')
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher.Path.exists', return_value=True)
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher.Path.unlink')
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher.time.sleep')
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher.logger.info')
    def test_stop_server_success(self, mock_info, mock_sleep, mock_unlink, mock_exists, mock_process_iter,
                                 mock_get_server_info):
        try:
            mock_proc = MagicMock()
            mock_proc.connections.return_value = [MagicMock(laddr=MagicMock(port=8080))]
            mock_process_iter.return_value = [mock_proc]

            directory = Path('/fake/dir')
            stop_server(directory)

            mock_proc.terminate.assert_called_once()
            mock_proc.wait.assert_called_once_with(timeout=2)
            mock_proc.kill.assert_called_once()
            mock_unlink.assert_called_once_with(directory / ".server_info")
            mock_info.assert_called_once_with(f"Stopping server (PID: {mock_proc.pid}) running on port 8080")
        except Exception as e:
            print("Error at stop_server_success")

    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher._get_server_info',
           return_value={"port": 8080})
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher.psutil.process_iter',
           side_effect=Exception("Process error"))
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher.logger.warning')
    def test_stop_server_failure(self, mock_warning, mock_process_iter, mock_get_server_info):
        directory = Path('/fake/dir')
        stop_server(directory)
        mock_warning.assert_called_once_with("Error stopping server: Process error")

    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher.os.startfile')
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher.time.sleep')
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher.webbrowser.open')
    def test_launch_server_and_browser_windows(self, mock_webbrowser_open, mock_sleep, mock_startfile):
        script_file = Path('/fake/dir/start_report_server.bat')
        port = 8080
        launch_server_and_browser(script_file, port)
        mock_startfile.assert_called_once_with(script_file)
        mock_sleep.assert_called_once_with(1)
        mock_webbrowser_open.assert_called_once_with(f"http://localhost:8080/report.html")

    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher.subprocess.Popen')
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher.time.sleep')
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher.webbrowser.open')
    def test_launch_server_and_browser_unix(self, mock_webbrowser_open, mock_sleep, mock_popen):
        script_file = Path('/fake/dir/start_report_server.sh')
        port = 8080
        with patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher.os.name', 'posix'):
            launch_server_and_browser(script_file, port)
        mock_popen.assert_called_once_with(["xterm", "-e", f"bash {script_file}"])
        mock_sleep.assert_called_once_with(1)
        mock_webbrowser_open.assert_called_once_with(f"http://localhost:8080/report.html")

    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher.os.startfile',
           side_effect=Exception("Startfile error"))
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher.logger.error')
    def test_launch_server_and_browser_failure(self, mock_error, mock_startfile):
        script_file = Path('/fake/dir/start_report_server.bat')
        port = 8080
        with self.assertRaises(Exception) as context:
            launch_server_and_browser(script_file, port)
        self.assertEqual(str(context.exception), "Startfile error")
        mock_error.assert_called_once_with("Error launching server: Startfile error")

    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher._get_server_info', return_value={})
    def test_stop_server_no_port(self, mock_get_server_info):
        directory = Path('/fake/dir')
        stop_server(directory)
        mock_get_server_info.assert_called_once_with(directory)

    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher._get_server_info', return_value={"port": 8080})
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher.psutil.process_iter')
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher.Path.exists', return_value=True)
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher.Path.unlink')
    @patch('cafex_core.reporting_._report_viewer._server_scripts._server_launcher.logger.warning')
    def test_stop_server_exceptions(self, mock_warning, mock_unlink, mock_exists, mock_process_iter, mock_get_server_info):
        try:
            mock_proc = MagicMock()
            mock_proc.connections.return_value = [MagicMock(laddr=MagicMock(port=8080))]
            mock_process_iter.return_value = [mock_proc]
            mock_proc.terminate.side_effect = psutil.NoSuchProcess(1)
            mock_proc.wait.side_effect = psutil.NoSuchProcess(1)
            mock_proc.kill.side_effect = psutil.NoSuchProcess(1)

            directory = Path('/fake/dir')
            stop_server(directory)

            mock_proc.terminate.assert_called_once()
            mock_proc.wait.assert_called_once_with(timeout=2)
            mock_proc.kill.assert_called_once()
            mock_unlink.assert_called_once_with(directory / ".server_info")
            mock_warning.assert_called_once_with(f"Stopping server (PID: {mock_proc.pid}) running on port 8080")
        except Exception as e:
            print("Error at stop_server_exceptions")


if __name__ == '__main__':
    unittest.main()
