"""This module contains the PytestCollectionFinish class which is used to
handle the collection finish hook in Pytest."""

from collections import Counter

from cafex_core.handlers.file_handler import FileHandler
from cafex_core.logging.logger_ import CoreLogger
from cafex_core.singletons_.request_ import RequestSingleton
from cafex_core.singletons_.session_ import SessionStore
from cafex_core.utils.date_time_utils import DateTimeActions
from cafex_core.utils.item_attribute_accessor import ItemAttributeAccessor

from .hook_util import HookUtil


class PytestCollectionFinish:
    """A class that handles the collection finish hook in Pytest.

    Attributes:
        session_store (SessionStore): The session store object.
        logger (Logger): The logger object.
        file_handler_obj (FileHandler): The file handler object.
        session (Session): The session object.

    Methods:
        __init_collection_finish: Initializes the collection finish hook.
        collection_finish_hook: The collection finish hook method.
    """

    def __init__(self, session):
        self.date_time_util = DateTimeActions()
        self.collection_start_time = self.date_time_util.get_current_date_time()
        self.logger = CoreLogger(name=__name__).get_logger()
        self.file_handler_obj = None
        self.session = session
        self.session_store = SessionStore()
        self.session_context = self.session_store.context
        self.metadata = self.session_context.metadata
        self.paths = self.session_context.paths
        self.request_store = RequestSingleton()
        self.hook_util = HookUtil()
        self.__init_collection_finish()

    def __init_collection_finish(self):
        """Initializes the collection finish hook by setting up the session
        store, logger, and file handler."""
        self.file_handler_obj = FileHandler()

    def collection_finish_hook(self):
        """The collection finish hook method that is called at the end of the
        test collection.

        It logs the collection finish event, retrieves the worker ID,
        gathers scenario details, creates a JSON file with collection
        details, and logs the collection details.
        """
        if self.metadata.worker_id in ["master", "gw0"]:
            self.logger.info(f"Worker ID : {self.metadata.worker_id}")
            test_details = [
                ItemAttributeAccessor(item_).get_properties() for item_ in self.session.items
            ]

            # Count different test types
            test_type_counts = Counter(test["testType"] for test in test_details)

            # Collect all unique tags
            all_tags = [tag for test in test_details for tag in test["tags"]]
            tag_statistics = dict(Counter(all_tags))

            collection_end_time = self.date_time_util.get_current_date_time()
            collection_duration_seconds = self.date_time_util.get_time_difference_seconds(
                collection_end_time, self.collection_start_time
            )

            collection_details = {
                "testCount": len(self.session.items),
                "pytestCount": test_type_counts.get("pytest", 0),
                "pytestBddCount": test_type_counts.get("pytestBdd", 0),
                "unittestCount": test_type_counts.get("unittest", 0),
                "collectionStartTime": self.collection_start_time,
                "collectionEndTime": collection_end_time,
                "collectionDurationSeconds": collection_duration_seconds,
                "collectionDuration": self.date_time_util.seconds_to_human_readable(
                    collection_duration_seconds
                ),
                "uniqueTags": list(set(all_tags)),
                "tagStatistics": tag_statistics,
                "testDetails": test_details,
            }
            self.metadata.collection_details = collection_details
            self.file_handler_obj.create_json_file(
                self.paths.temp_execution_dir, "collection.json", collection_details
            )
