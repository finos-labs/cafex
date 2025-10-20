"""Compatibility wrapper around the new SessionContext."""

from __future__ import annotations

import warnings
from dataclasses import fields
from typing import Any

from cafex_core.context import SessionContext, get_session_context

_ALLOWED_FIELD_NAMES = {field_.name for field_ in fields(SessionContext)}


class SessionStore:
    """Backward-compatible facade that proxies to the shared SessionContext.

    This preserves the previous import surface while enforcing an allowlist of
    known attributes. Attempting to write to an unknown attribute now raises
    an AttributeError so callers discover missing context plumbing during
    migration.
    """

    _instance: "SessionStore | None" = None

    def __new__(cls) -> "SessionStore":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _context() -> SessionContext:
        return get_session_context()

    # ------------------------------------------------------------------ getattr
    def __getattr__(self, name: str) -> Any:
        context = self._context()
        if hasattr(context, name):
            return getattr(context, name)
        raise AttributeError(
            f"'SessionStore' object has no attribute '{name}'. "
            "Update SessionContext or use context.extras for ad-hoc data."
        )

    # ------------------------------------------------------------------ setattr
    def __setattr__(self, name: str, value: Any) -> None:
        # Allow normal attribute handling for private attributes
        if name.startswith("_"):
            super().__setattr__(name, value)
            return

        if name == "storage":
            raise AttributeError(
                "SessionStore.storage is deprecated and cannot be reassigned. "
                "Store arbitrary data in SessionContext.extras instead."
            )

        if name in _ALLOWED_FIELD_NAMES:
            setattr(self._context(), name, value)
            return

        raise AttributeError(
            f"'SessionStore' does not allow setting unknown attribute '{name}'. "
            "Add it to SessionContext or use context.extras."
        )

    # ---------------------------------------------------------------- properties
    @property
    def storage(self) -> dict:
        warnings.warn(
            "SessionStore.storage is deprecated. Use SessionContext.extras instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._context().extras

    # --------------------------------------------------------------- convenience
    def __dir__(self) -> list[str]:
        # Provide better autocomplete in IDEs
        return sorted(set(super().__dir__()) | _ALLOWED_FIELD_NAMES)

