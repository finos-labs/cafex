import os
import sys
import pytest
from cafex_core.singletons_.session_ import SessionStore
from cafex_core.utils.hooks_.hook_helper import HookHelper
from cafex_core.singletons_.request_ import RequestSingleton

HOOK_HELPER_ = HookHelper(os.path.dirname(os.path.abspath(__file__)))
session_store = SessionStore()


@pytest.fixture(autouse=True)
def set_singleton(request):
    singleton = RequestSingleton()
    singleton.request = request


@pytest.hookimpl()
def pytest_addoption(parser):
    HOOK_HELPER_.pytest_add_option_(parser)


@pytest.hookimpl()
def pytest_configure(config):
    HOOK_HELPER_.pytest_configure_(config)


@pytest.hookimpl()
def pytest_collection_finish(session):
    HOOK_HELPER_.pytest_collection_finish_(session)


@pytest.hookimpl()
def pytest_sessionstart(session):
    HOOK_HELPER_.pytest_session_start_(session, sys.argv)


def pytest_bdd_before_scenario(request, feature, scenario):
    HOOK_HELPER_.pytest_before_scenario_(feature, scenario, request, sys.argv)


def pytest_bdd_before_step(scenario, step):
    HOOK_HELPER_.pytest_before_step(scenario, step)


def pytest_bdd_after_step(step):
    HOOK_HELPER_.pytest_after_step(step)


def pytest_bdd_after_scenario(feature, scenario):
    HOOK_HELPER_.pytest_after_scenario(scenario, sys.argv, feature)


@pytest.hookimpl()
def pytest_runtest_setup(item):
    HOOK_HELPER_.pytest_run_test_setup(item)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport():
    HOOK_HELPER_.pytest_run_test_make_report((yield).get_result())


@pytest.hookimpl()
def pytest_runtest_logreport(report):
    HOOK_HELPER_.pytest_run_test_log_report(report)


def pytest_bdd_step_error(step):
    print(f"Step which is failed: {step.name}")
    HOOK_HELPER_.pytest_bdd_step_error(step)


def pytest_bdd_step_func_lookup_error(step):
    print(f"No matching step definition found for: {step.name}")


@pytest.hookimpl()
def pytest_sessionfinish(session):
    HOOK_HELPER_.pytest_session_finish_(session)
