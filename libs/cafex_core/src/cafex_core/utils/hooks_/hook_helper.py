# This file contains the HookHelper class which is responsible for initializing the hooks and creating the folders
from ...singletons_.session_ import SessionStore
from .hook_util import HookUtil
from .pytest_add_option_hook import PytestAddOptionHook
from .pytest_after_scenario_hook import PytestAfterScenario
from .pytest_after_step_hook import PytestBddAfterStep
from .pytest_bdd_before_step import PytestBddBeforeStep
from .pytest_bdd_step_error import PytestBDDStepError
from .pytest_before_scenario_hook import PytestBeforeScenario
from .pytest_collection_finish_hook import PytestCollectionFinish
from .pytest_configure_hook import PytestConfiguration
from .pytest_run_test_logreport import PytestRunLogReport
from .pytest_run_test_make_report import PytestRunTestMakeReport
from .pytest_run_test_setup import PytestRunTestSetup
from .pytest_session_finish_ import PytestSessionFinish
from .pytest_session_start_hook import PytestSessionStart


class HookHelper:
    """Doc String for Hook Helper."""

    def __init__(self, conf_cwd):
        """Constructor for HookHelper class."""
        self.conf_cwd = conf_cwd
        self.hook_util = HookUtil()
        self.session_store = SessionStore()
        self.execution_uuid = self.hook_util.get_or_create_execution_uuid()

        context = self.session_store.context
        context.paths.conf_dir = self.conf_cwd
        context.paths.execution_uuid = self.execution_uuid
        self._init_hook()

    def _init_hook(self):
        if self.hook_util.is_master_process():
            self.hook_util.create_folders(self.conf_cwd)
            self.hook_util.folder_handler.reorganize_result_folders(
                self.conf_cwd, self.execution_uuid
            )
        self.hook_util.set_paths_from_env()

    @staticmethod
    def pytest_add_option_(parser_):
        PytestAddOptionHook(parser_).add_option_hook()

    @staticmethod
    def pytest_configure_(config):
        PytestConfiguration(config).configure_hook()

    @staticmethod
    def pytest_collection_finish_(session):
        PytestCollectionFinish(session).collection_finish_hook()

    @staticmethod
    def pytest_session_start_(session, sys_arg):
        PytestSessionStart(session, sys_arg).session_start_hook()

    @staticmethod
    def pytest_before_scenario_(feature, scenario_, request, args):
        PytestBeforeScenario(feature, scenario_, request, args).before_scenario_hook()

    @staticmethod
    def pytest_before_step(scenario_, step_):
        PytestBddBeforeStep(scenario_, step_).before_step_hook()

    @staticmethod
    def pytest_after_step(step_):
        PytestBddAfterStep(step_).after_step_hook()

    @staticmethod
    def pytest_after_scenario(scenario, sys_args, feature):
        PytestAfterScenario(scenario, sys_args, feature).after_scenario_hook()

    @staticmethod
    def pytest_run_test_setup(item_):
        PytestRunTestSetup(item_).run_setup()

    @staticmethod
    def pytest_run_test_make_report(report_):
        PytestRunTestMakeReport(report_).run_make_report()

    @staticmethod
    def pytest_run_test_log_report(report):
        PytestRunLogReport(report).run_log_report()

    @staticmethod
    def pytest_bdd_step_error(step):
        PytestBDDStepError(step).bdd_step_error()

    @staticmethod
    def pytest_session_finish_(session):
        PytestSessionFinish(session).session_finish_()
