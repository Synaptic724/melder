from __future__ import annotations

from enum import Enum, auto
from typing import Any, Dict, Optional

from melder.utilities.general_base.cleanable import Cleanable


class SystemDiagnosticSeverity(Enum):
    """Severity bucket for system-level validation diagnostics."""

    ERROR = auto()
    WARNING = auto()


class SystemDiagnostic(Cleanable):
    """
    Structured diagnostic produced by system-level validation strategies.

    Uses the Cleanable pattern so cached diagnostics can be deterministically
    torn down when no longer needed.
    """

    __slots__ = Cleanable.__slots__ + [
        "_code",
        "_message",
        "_severity",
        "_spell_id",
        "_root_id",
        "_details",
    ]

    def __init__(
            self,
            code: str,
            message: str,
            *,
            severity: SystemDiagnosticSeverity = SystemDiagnosticSeverity.ERROR,
            spell_id: Optional[str] = None,
            root_id: Optional[str] = None,
            details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        if not code:
            raise ValueError("code must not be empty.")
        if message is None:
            raise ValueError("message must not be None.")
        if severity is None:
            raise ValueError("severity must not be None.")

        self._code: str = code
        self._message: str = message
        self._severity: SystemDiagnosticSeverity = severity
        self._spell_id: Optional[str] = spell_id
        self._root_id: Optional[str] = root_id
        self._details: Optional[Dict[str, Any]] = dict(details) if details else None

    def cleanup(self) -> None:
        if self._cleaned:
            return
        self._cleaned = True
        self._code = None
        self._message = None
        self._severity = None
        self._spell_id = None
        self._root_id = None
        if self._details is not None:
            self._details.clear()
        self._details = None

    @property
    def code(self) -> str:
        self.check_cleaned()
        return self._code

    @property
    def message(self) -> str:
        self.check_cleaned()
        return self._message

    @property
    def severity(self) -> SystemDiagnosticSeverity:
        self.check_cleaned()
        return self._severity

    @property
    def spell_id(self) -> Optional[str]:
        self.check_cleaned()
        return self._spell_id

    @property
    def root_id(self) -> Optional[str]:
        self.check_cleaned()
        return self._root_id

    @property
    def details(self) -> Optional[Dict[str, Any]]:
        self.check_cleaned()
        if self._details is None:
            return None
        return dict(self._details)

    def __repr__(self) -> str:
        return (
            f"SystemDiagnostic(code={self._code!r}, severity={self._severity!r}, "
            f"spell_id={self._spell_id!r}, root_id={self._root_id!r})"
        )
