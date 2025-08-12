import logging
import os
import time
from logging.handlers import RotatingFileHandler


class CoreLogger:
    """A singleton logging class for consistent logging across an application.

    Provides the flexibility to initialize with console and rotating
    file handlers.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Enforces the singleton pattern.

        Returns:
            SingletonLogger: The single instance of the logging class.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, name, level=logging.INFO):
        """Initializes the logging instance.

        Args:
            name (str, optional): The name of the logging.
            level (int, optional): The logging level. Defaults to logging.INFO.
        """
        self.name = name
        if self.name is not None:
            self.logger = logging.getLogger(self.name)
        else:
            self.logger = logging.getLogger()
        self.logger.setLevel(level)
        self.file_handler = None

    def initialize(self, console_logging, file_path, worker_id="master"):
        """Initializes the logging with console and/or file handlers.

        Args:
            console_logging (bool, optional): Whether to enable console logging.
                Defaults to True.
            file_path (str, optional): The path to the log file. Defaults to "app.log".
            worker_id (str, optional): worker id (gwo, gw1) - master in case of non-parallel.
        """
        if console_logging:
            self._add_console_handler()

        self._add_file_handler(file_path, worker_id)

    def _add_console_handler(self):
        """Adds a console handlers to the logging."""
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(f"%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _add_file_handler(self, logs_dir, worker_id):
        """Adds a rotating file handlers to the logging.

        Args:
            logs_dir (str): The directory to the log file.
            worker_id (str): worker id ('master' in case of non-parallel)
        """
        timestamp = time.strftime("%Y%m%d%H%M%S")
        _log_file_path = os.path.join(logs_dir, f"{worker_id}_{timestamp}.log")
        self.file_handler = RotatingFileHandler(
            _log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.file_handler.setFormatter(formatter)
        self.logger.addHandler(self.file_handler)

    def get_logger(self):
        """Returns the logging instance.

        Returns:
            logging.Logger: The configured logging object.
        """
        return self.logger
