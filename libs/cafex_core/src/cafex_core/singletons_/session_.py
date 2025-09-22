"""Singleton state storage used across Cafex test execution."""

from __future__ import annotations

from typing import Any, Tuple

from .execution_context import SessionContext


class SessionStore:
    """A singleton façade over the global :class:`SessionContext`.

    Historically ``SessionStore`` stored arbitrary attributes in a dictionary via
    ``__setattr__``/``__getattr__`` overrides.  The new implementation keeps that
    behaviour for backwards compatibility while providing a typed execution
    context through :pyattr:`context`.
    """

    _instance: "SessionStore" | None = None

    # Mapping of legacy attribute names to their location inside ``SessionContext``.
    _ATTRIBUTE_MAP: dict[str, Tuple[str, str]] = {
        "current_test": ("test", "current_test"),
        "current_step": ("test", "current_step"),
        "current_step_details": ("test", "current_step_details"),
        "failed_tests": ("test", "failed_tests"),
        "error_messages": ("test", "error_messages"),
        "conf_dir": ("paths", "conf_dir"),
        "execution_uuid": ("paths", "execution_uuid"),
        "result_dir": ("paths", "result_dir"),
        "execution_dir": ("paths", "execution_dir"),
        "logs_dir": ("paths", "logs_dir"),
        "screenshots_dir": ("paths", "screenshots_dir"),
        "temp_dir": ("paths", "temp_dir"),
        "temp_execution_dir": ("paths", "temp_execution_dir"),
        "driver": ("drivers", "driver"),
        "mobile_driver": ("drivers", "mobile_driver"),
        "ui_scenario": ("drivers", "ui_scenario"),
        "mobile_ui_scenario": ("drivers", "mobile_ui_scenario"),
        "worker_id": ("metadata", "worker_id"),
        "workers_count": ("metadata", "workers_count"),
        "is_parallel": ("metadata", "is_parallel"),
        "counter": ("metadata", "counter"),
        "datadriven": ("metadata", "datadriven"),
        "rowcount": ("metadata", "rowcount"),
        "collection_details": ("metadata", "collection_details"),
        "globals": ("metadata", "globals"),
        "global_dict": ("metadata", "global_dict"),
        "base_config": ("metadata", "base_config"),
        "mobile_config": ("metadata", "mobile_config"),
        "browserstack_web_configuration": ("metadata", "browserstack_web_configuration"),
        "is_report": ("metadata", "is_report"),
    }

    _PROTECTED_ATTRS = {"_context", "_instance"}

    def __new__(cls) -> "SessionStore":
        """Return the singleton instance."""
        if cls._instance is None:
            instance = super().__new__(cls)
            object.__setattr__(instance, "_context", SessionContext())
            cls._instance = instance
        return cls._instance

    @property
    def context(self) -> SessionContext:
        """Typed execution context shared across the framework."""
        return self._context

    @property
    def storage(self) -> dict[str, Any]:
        return self.context.storage

    @storage.setter
    def storage(self, value: dict[str, Any]) -> None:  # type: ignore[override]
        self.context.storage = value

    @property
    def reporting(self) -> dict[str, Any]:
        return self.context.reporting

    @reporting.setter
    def reporting(self, value: dict[str, Any]) -> None:
        self.context.reporting = value

    # ------------------------------------------------------------------
    # Legacy attribute behaviour
    # ------------------------------------------------------------------
    def __setattr__(self, name: str, value: Any) -> None:  # noqa: D401 - see class docstring
        if name in self._PROTECTED_ATTRS:
            object.__setattr__(self, name, value)
            return

        prop = getattr(type(self), name, None)
        if isinstance(prop, property) and prop.fset is not None:
            prop.fset(self, value)
            return

        if name in self._ATTRIBUTE_MAP:
            self._set_mapped_attribute(name, value)
            return

        self.context.storage[name] = value

    def __getattr__(self, name: str) -> Any:
        if name in self._ATTRIBUTE_MAP:
            return self._get_mapped_attribute(name)
        try:
            return self.context.storage[name]
        except KeyError as exc:  # pragma: no cover - retain legacy error message
            raise AttributeError(name) from exc

    # ------------------------------------------------------------------
    # Convenience helpers backed by the typed context
    # ------------------------------------------------------------------
    def add_error_message(self, error_info: dict) -> None:
        if self.context.test.current_test:
            self.context.test.add_error_message(self.context.test.current_test, error_info)

    def get_error_messages(self, test_id: str) -> list[dict]:
        return self.context.test.get_error_messages(test_id)

    def clear_error_messages(self, test_id: str) -> None:
        self.context.test.clear_error_messages(test_id)

    def mark_test_failed(self) -> None:
        self.context.test.mark_failed(self.context.test.current_test)

    def is_current_test_failed(self) -> bool:
        return self.context.test.is_failed(self.context.test.current_test)

    def clear_current_test_status(self) -> None:
        self.context.test.clear_failure(self.context.test.current_test)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _resolve_context_target(self, name: str):
        path = self._ATTRIBUTE_MAP[name]
        target = self.context
        for attribute in path[:-1]:
            target = getattr(target, attribute)
        return target, path[-1]

    def _set_mapped_attribute(self, name: str, value: Any) -> None:
        target, last = self._resolve_context_target(name)
        setattr(target, last, value)

    def _get_mapped_attribute(self, name: str) -> Any:
        target, last = self._resolve_context_target(name)
        return getattr(target, last)


__all__ = ["SessionStore"]

