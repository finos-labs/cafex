"""This module contains the PytestConfiguration class which is used to handle
the configuration of a pytest session.

It includes methods to initialize the configuration, get the worker ID,
get the number of nodes, and execute the configuration hook.
"""

import os

from dotenv import load_dotenv

from cafex_core.logging.logger_ import CoreLogger
from cafex_core.singletons_.session_ import SessionStore


class PytestConfiguration:
    """A class that handles the configuration of a pytest session.

    Attributes:
        logger (Logger): The logging object.
        config (Config): The pytest config object.
        worker_id (str): The worker ID.
        session_store (SessionStore): The session store object.

    Methods:
        __init__: Initializes the PytestConfiguration class.
        __init_configure: Initializes the configuration.
        worker: Returns the worker ID.
        nodes: Returns the number of nodes.
        configure_hook: Executes the configuration hook.
    """

    def __init__(self, config_):
        """Initialize the PytestConfiguration class.

        Args:
            config_: The pytest config object.
        """
        self.logger = None
        self.config = config_
        self.worker_id = self.worker
        self.workers_count = self.worker_nodes_count
        self.session_store = None
        self.__init_configure()

    def __init_configure(self):
        """Initialize the configuration by setting up the necessary components.

        Initialize the configuration by setting up the necessary
        components.
        """
        self.session_store = SessionStore()
        session_context = self.session_store.context
        session_context.metadata.worker_id = self.worker_id
        session_context.metadata.workers_count = self.workers_count
        self.logger_class = CoreLogger(name=None)
        self.logger = self.logger_class.get_logger()
        self.logger_class.initialize(True, session_context.paths.logs_dir, self.worker_id)

    @property
    def worker(self):
        """Returns the worker ID.

        Returns:
            str: The worker ID.
        """
        worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")
        return worker_id

    @property
    def worker_nodes_count(self):
        """Returns the worker nodes.

        Returns:
            int: The worker ID.
        """
        nodes_ = self.config.getoption("numprocesses")
        num_nodes_ = 0 if nodes_ is None else nodes_
        os.environ["numprocesses"] = str(num_nodes_)
        return num_nodes_

    def configure_hook(self):
        """Executes the configuration hook.

        It logs the configuration event, sets the session store
        attributes, and initializes a defaultdict for the globalDict
        attribute.
        """
        self.logger.info("PytestConfigure")
        metadata = self.session_store.context.metadata
        drivers = self.session_store.context.drivers

        drivers.driver = None
        drivers.mobile_driver = None
        metadata.counter = 1
        metadata.datadriven = 1
        metadata.rowcount = 1
        metadata.is_parallel = None
        metadata.globals = {}
        drivers.ui_scenario = False
        drivers.mobile_ui_scenario = False
        env_path = os.path.join(self.session_store.context.paths.conf_dir, ".env")
        load_dotenv(env_path)
