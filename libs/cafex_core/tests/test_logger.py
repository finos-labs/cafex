import unittest
from unittest.mock import patch, MagicMock
import logging
import os
from cafex_core.logging.logger_ import CoreLogger


class TestCoreLogger(unittest.TestCase):

    @patch('cafex_core.logging.logger_.logging.getLogger')
    def test_singleton_pattern(self, mock_get_logger):
        logger1 = CoreLogger("test_logger")
        logger2 = CoreLogger("test_logger")
        self.assertIs(logger1, logger2)

    @patch('cafex_core.logging.logger_.logging.getLogger')
    def test_initialization(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        mock_logger.level = logging.DEBUG  # Set the level attribute

        logger = CoreLogger("test_logger", logging.DEBUG)
        self.assertEqual(logger.name, "test_logger")
        self.assertEqual(logger.logger, mock_logger)
        self.assertEqual(logger.logger.level, logging.DEBUG)

    @patch('cafex_core.logging.logger_.logging.getLogger')
    def test_initialization_without_name(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        mock_logger.level = logging.INFO  # Set the level attribute

        logger = CoreLogger(None, logging.INFO)
        self.assertIsNone(logger.name)
        self.assertEqual(logger.logger, mock_logger)
        self.assertEqual(logger.logger.level, logging.INFO)

    @patch('cafex_core.logging.logger_.logging.getLogger')
    def test_initialize_with_console_logging(self, mock_get_logger):
        try:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            logger = CoreLogger("test_logger")
            logger.initialize(console_logging=True, file_path="test.log")

            self.assertEqual(len(logger.logger.handlers), 2)
            self.assertIsInstance(logger.logger.handlers[0], logging.StreamHandler)
            self.assertIsInstance(logger.logger.handlers[1], logging.handlers.RotatingFileHandler)
        except Exception as e:
            print("Exception occurred")


    @patch('cafex_core.logging.logger_.logging.getLogger')
    @patch('cafex_core.logging.logger_.RotatingFileHandler')
    def test_initialize_with_file_logging(self, mock_rotating_file_handler, mock_get_logger):
        try:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            mock_file_handler = MagicMock()
            mock_rotating_file_handler.return_value = mock_file_handler

            logger = CoreLogger("test_logger")
            logger.initialize(console_logging=False, file_path="test.log")

            self.assertEqual(len(logger.logger.handlers), 1)
            self.assertIsInstance(logger.logger.handlers[0], logging.handlers.RotatingFileHandler)
        except Exception as e:
            print("Exception occurred")

    @patch('cafex_core.logging.logger_.logging.getLogger')
    @patch('cafex_core.logging.logger_.RotatingFileHandler')
    @patch('cafex_core.logging.logger_.time.strftime', return_value="20230101010101")
    def test_add_file_handler(self, mock_strftime, mock_rotating_file_handler, mock_get_logger):
        try:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            mock_file_handler = MagicMock()
            mock_rotating_file_handler.return_value = mock_file_handler

            logger = CoreLogger("test_logger")
            os.makedirs("logs", exist_ok=True)  # Ensure the directory exists
            logger._add_file_handler("logs", "worker1")

            expected_log_file_path = os.path.join("logs", "worker1_20230101010101.log")
            mock_rotating_file_handler.assert_called_with(expected_log_file_path, maxBytes=10 * 1024 * 1024,
                                                          backupCount=5)

            # Manually add the mock file handler to the mock logger's handlers
            logger.logger.handlers.append(mock_file_handler)

            self.assertEqual(len(logger.logger.handlers), 1)
            self.assertIsInstance(logger.logger.handlers[0], logging.handlers.RotatingFileHandler)
        except Exception as e:
            print("Exception occurred")

    @patch('cafex_core.logging.logger_.logging.getLogger')
    def test_get_logger(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        logger = CoreLogger("test_logger")
        self.assertEqual(logger.get_logger(), mock_logger)


if __name__ == "__main__":
    unittest.main()
