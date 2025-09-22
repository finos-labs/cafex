"""Typed execution context used by :mod:`cafex_core.singletons_.session_`.

This module provides data classes that collect the mutable state Cafex keeps
while executing a test session.  The goal is to make the implicit structure in
``SessionStore`` explicit so that future code can rely on typed attributes
instead of scattering free-form dictionary assignments.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class TestContext:
    """Holds state related to the currently running test."""

    current_test: Optional[str] = None
    current_step: Optional[str] = None
    current_step_details: Optional[Dict[str, Any]] = None
    failed_tests: Set[str] = field(default_factory=set)
    error_messages: Dict[str, List[dict]] = field(default_factory=dict)

    def add_error_message(self, test_id: str, error_info: dict) -> None:
        """Store an error message for ``test_id``."""
        self.error_messages.setdefault(test_id, []).append(error_info)

    def get_error_messages(self, test_id: str) -> List[dict]:
        """Return the collected error messages for ``test_id``."""
        return self.error_messages.get(test_id, [])

    def clear_error_messages(self, test_id: str) -> None:
        """Drop the stored error messages for ``test_id``."""
        self.error_messages.pop(test_id, None)

    def mark_failed(self, test_id: Optional[str]) -> None:
        """Mark ``test_id`` as failed if it is provided."""
        if test_id:
            self.failed_tests.add(test_id)

    def clear_failure(self, test_id: Optional[str]) -> None:
        """Remove ``test_id`` from the failed tests set if it exists."""
        if test_id:
            self.failed_tests.discard(test_id)

    def is_failed(self, test_id: Optional[str]) -> bool:
        """Return ``True`` if ``test_id`` is registered as failed."""
        return bool(test_id and test_id in self.failed_tests)


@dataclass
class PathsContext:
    """File-system paths used during a test execution."""

    conf_dir: Optional[str] = None
    execution_uuid: Optional[str] = None
    result_dir: Optional[str] = None
    execution_dir: Optional[str] = None
    logs_dir: Optional[str] = None
    screenshots_dir: Optional[str] = None
    temp_dir: Optional[str] = None
    temp_execution_dir: Optional[str] = None


@dataclass
class DriversContext:
    """Driver objects and flags that describe UI usage."""

    driver: Any = None
    mobile_driver: Any = None
    ui_scenario: bool = False
    mobile_ui_scenario: bool = False


@dataclass
class MetadataContext:
    """Execution metadata (workers, counters, configuration snapshots)."""

    worker_id: Optional[str] = None
    workers_count: int = 0
    is_parallel: Optional[bool] = None
    counter: int = 1
    datadriven: int = 1
    rowcount: int = 1
    collection_details: Dict[str, Any] = field(default_factory=dict)
    globals: Dict[str, Any] = field(default_factory=dict)
    global_dict: Dict[str, Any] = field(default_factory=dict)
    base_config: Optional[Dict[str, Any]] = None
    mobile_config: Optional[Dict[str, Any]] = None
    browserstack_web_configuration: Optional[Dict[str, Any]] = None
    is_report: Optional[bool] = None


@dataclass
class SessionContext:
    """Aggregates all mutable execution state used across the framework."""

    storage: Dict[str, Any] = field(default_factory=dict)
    reporting: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {"tests": {}})
    test: TestContext = field(default_factory=TestContext)
    paths: PathsContext = field(default_factory=PathsContext)
    drivers: DriversContext = field(default_factory=DriversContext)
    metadata: MetadataContext = field(default_factory=MetadataContext)

    def reset(self) -> None:
        """Reset the context to a pristine state."""
        self.storage.clear()
        self.reporting = {"tests": {}}
        self.test = TestContext()
        self.paths = PathsContext()
        self.drivers = DriversContext()
        self.metadata = MetadataContext()

