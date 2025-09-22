import unittest
from unittest import mock
from pathlib import Path
from unittest.mock import patch, mock_open

from cafex_core.reporting_.report_generator import ReportGenerator


class TestReportGenerator(unittest.TestCase):

    @patch('cafex_core.reporting_.report_generator.Path.exists', return_value=True)
    def test_validate_paths_success(self, mock_exists):
        result_dir = Path('/mock/result')
        viewer_source = Path('/mock/viewer')
        with mock.patch('cafex_core.reporting_.report_generator.ReportGenerator.REQUIRED_FILES', new=['index.html', 'styles.css', 'app.js']):
            ReportGenerator._validate_paths(result_dir, viewer_source)

    def test_validate_paths_missing_result_dir(self):
        with mock.patch('cafex_core.reporting_.report_generator.Path.exists', return_value=False):
            with self.assertRaises(FileNotFoundError):
                ReportGenerator._validate_paths(Path('/mock/result'), Path('/mock/viewer'))

    @patch('builtins.open', new_callable=mock.mock_open, read_data='{"key": "value"}')
    def test_read_file_success(self, mock_file):
        content = ReportGenerator._read_file(Path('/mock/file.json'))
        self.assertEqual(content, '{"key": "value"}')

    def test_find_free_port_success(self):
        with mock.patch('socket.socket.connect_ex', return_value=1):  # Simulate port available
            port = ReportGenerator._find_free_port(8000)
            self.assertEqual(port, 8000)

    def test_find_free_port_failure(self):
        with mock.patch('socket.socket.connect_ex', return_value=0):  # Simulate all ports occupied
            with self.assertRaises(RuntimeError):
                ReportGenerator._find_free_port(8000)

    @patch('cafex_core.reporting_.report_generator.open', new_callable=mock.mock_open)
    def test_create_html_report(self, mock_file):
        html_template = "<html><!-- STYLE_PLACEHOLDER --><!-- SCRIPT_PLACEHOLDER --></html>"
        css_content = "body { color: red; }"
        js_content = "console.log('test');"
        result_data = {"key": "value"}
        report = ReportGenerator._create_html_report(html_template, css_content, js_content, result_data)
        self.assertIn('<style>\nbody { color: red; }\n</style>', report)
        self.assertIn('const reportData = {\n  "key": "value"\n};', report)

    @patch('cafex_core.reporting_.report_generator.open', new_callable=mock.mock_open)
    def test_write_report_success(self, mock_file):
        ReportGenerator._write_report('report content', Path('/mock/report.html'))
        mock_file().write.assert_called_once_with('report content')

    @patch('cafex_core.reporting_.report_generator.Path.exists', return_value=True)
    @patch('cafex_core.reporting_.report_generator.Path.glob', return_value=[Path('/mock/logs/log_1234.log')])
    @patch('builtins.open', new_callable=mock.mock_open, read_data='log content')
    def test_get_log_files_success(self, mock_file, mock_glob, mock_exists):
        logs = ReportGenerator._get_log_files(Path('/mock/result'))
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]['name'], 'log_1234.log')

    def test_prepare_report_viewer_failure(self):
        with mock.patch('cafex_core.reporting_.report_generator.ReportGenerator._validate_paths', side_effect=FileNotFoundError):
            result = ReportGenerator.prepare_report_viewer('/mock/result')
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()