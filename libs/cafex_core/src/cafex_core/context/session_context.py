"""Typed session context and helpers for managing execution state."""

from __future__ import annotations

import contextlib
from dataclasses import dataclass, field, fields
from threading import RLock
from typing import Any, Dict, List, Optional, Set


@dataclass
class SessionContext:
    """Holds execution state that used to live in the SessionStore singleton."""

    # Configuration and execution metadata
    base_config: Optional[Dict[str, Any]] = None
    mobile_config: Dict[str, Any] = field(default_factory=dict)
    browserstack_web_configuration: Dict[str, Any] = field(default_factory=dict)
    browserstack_app_uploaded: bool = False
    conf_dir: Optional[str] = None
    execution_uuid: Optional[str] = None
    result_dir: Optional[str] = None
    execution_dir: Optional[str] = None
    logs_dir: Optional[str] = None
    screenshots_dir: Optional[str] = None
    temp_dir: Optional[str] = None
    temp_execution_dir: Optional[str] = None
    worker_id: str = "master"
    workers_count: int = 0
    is_parallel: Optional[bool] = None
    is_report: Optional[bool] = None
    config: Optional[Any] = None

    # Runtime flags
    ui_scenario: bool = False
    playwright_ui_scenario: bool = False
    mobile_ui_scenario: bool = False
    ui_desktop_client_scenario: bool = False

    # Driver/session objects
    driver: Any = None
    mobile_driver: Any = None
    handler: Any = None
    playwright_browser: Any = None
    playwright_context: Any = None
    playwright_page: Any = None

    # Reporting/test tracking
    reporting: Dict[str, Any] = field(default_factory=lambda: {"tests": {}})
    current_test: Optional[str] = None
    current_step: Optional[str] = None
    current_step_details: Optional[Dict[str, Any]] = None
    error_messages: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    failed_tests: Set[str] = field(default_factory=set)
    counter: int = 1
    datadriven: int = 1
    rowcount: int = 1

    # Miscellaneous shared state
    globals: Dict[str, Any] = field(default_factory=dict)
    global_dict: Dict[str, Any] = field(default_factory=dict)
    collection_details: Dict[str, Any] = field(default_factory=dict)
    extras: Dict[str, Any] = field(default_factory=dict)

    # Exception handling context
    exception_type: Optional[str] = None
    exception_message: Optional[str] = None
    all_frames: List[str] = field(default_factory=list)
    trimmed_frames: List[str] = field(default_factory=list)

    def add_error_message(self, error_info: Dict[str, Any]) -> None:
        """Add error message for the current test, if one is active."""
        if not self.current_test:
            return
        self.error_messages.setdefault(self.current_test, []).append(error_info)

    def get_error_messages(self, test_id: str) -> List[Dict[str, Any]]:
        """Return captured error messages for a specific test."""
        return list(self.error_messages.get(test_id, []))

    def clear_error_messages(self, test_id: str) -> None:
        """Remove tracked error messages for the provided test id."""
        self.error_messages.pop(test_id, None)

    def mark_test_failed(self) -> None:
        """Mark the current test as failed."""
        if self.current_test:
            self.failed_tests.add(self.current_test)

    def is_current_test_failed(self) -> bool:
        """Return True if the current test is flagged as failed."""
        return bool(self.current_test and self.current_test in self.failed_tests)

    def clear_current_test_status(self) -> None:
        """Clear tracked failure state for the current test."""
        if self.current_test:
            self.failed_tests.discard(self.current_test)

    @property
    def allowed_fields(self) -> Set[str]:
        """Expose the known mutable attributes for guard rails."""
        return {f.name for f in fields(self)}


# Global registry ----------------------------------------------------------

_context_lock = RLock()
_current_context: Optional[SessionContext] = None


def get_session_context() -> SessionContext:
    """Return the process-wide session context, creating it if needed."""
    global _current_context
    with _context_lock:
        if _current_context is None:
            _current_context = SessionContext()
        return _current_context


def set_session_context(context: SessionContext) -> None:
    """Replace the active session context."""
    if not isinstance(context, SessionContext):
        raise TypeError("context must be an instance of SessionContext")

    global _current_context
    with _context_lock:
        _current_context = context


def reset_session_context() -> SessionContext:
    """Reset to a fresh session context and return it."""
    fresh_context = SessionContext()
    set_session_context(fresh_context)
    return fresh_context


class SessionContextManager(contextlib.AbstractContextManager):
    """Context manager that temporarily swaps in a provided session context."""

    def __init__(self, context: Optional[SessionContext] = None):
        self._replacement = context or SessionContext()
        self._previous: Optional[SessionContext] = None

    def __enter__(self) -> SessionContext:
        global _current_context
        with _context_lock:
            self._previous = _current_context
            _current_context = self._replacement
        return get_session_context()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        global _current_context
        with _context_lock:
            _current_context = self._previous
        return None

