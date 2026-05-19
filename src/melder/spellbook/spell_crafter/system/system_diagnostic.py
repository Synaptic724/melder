from enum import Enum, auto
from typing import Any, Dict, Optional

from mypy_extensions import mypyc_attr

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable

@mypyc_attr(native_class=True)
class SystemDiagnosticSeverity(Enum):
    """Severity bucket for system-level validation diagnostics."""
    __melder_internal__ = _mrg.sentinel
    ERROR = auto()
    WARNING = auto()

@mypyc_attr(native_class=True)
class SystemDiagnostic(Cleanable):
    """
    Structured diagnostic produced by system-level validation strategies.

    Uses the Cleanable pattern so cached diagnostics can be deterministically
    torn down when no longer needed.

    Purpose:
        Represent one system-level validation finding with optional attribution.
    Contract:
        - code and ``message`` are required and non-empty.
        - ``severity`` is always a ``SystemDiagnosticSeverity`` value.
        - ``source`` is optional and used for strategy attribution.
    Attributes:
        code: Machine-readable identifier for the diagnostic.
        message: Human-readable description of the issue.
        severity: Severity bucket for the diagnostic.
        spell_id: Optional spell id associated with the diagnostic.
        root_id: Optional root id associated with the diagnostic.
        source: Optional strategy identifier that produced the diagnostic.
        details: Optional structured payload for tooling.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_code",
        "_message",
        "_severity",
        "_spell_id",
        "_root_id",
        "_source",
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
            source: Optional[str] = None,
            details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Purpose:
            Initialize a system-level validation diagnostic.
        Contract:
            - Requires non-empty code and non-None message/severity.
            - Preserves optional spell/root ids, source attribution, and details.
        Args:
            code: Machine-readable diagnostic identifier.
            message: Human-readable explanation of the diagnostic.
            severity: Severity bucket for the diagnostic.
            spell_id: Optional spell id associated with the diagnostic.
            root_id: Optional root id associated with the diagnostic.
            source: Optional strategy identifier for attribution.
            details: Optional structured context for tooling.
        Returns:
            None.
        Raises:
            ValueError: If code is empty or message/severity are None.
        """
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
        self._source: Optional[str] = source
        self._details: Optional[Dict[str, Any]] = dict(details) if details else None

    def cleanup(self) -> None:
        """
        Deterministically release diagnostic payload state.

        Contract:
            - Idempotent: safe to call multiple times.
            - Clears detail payloads before dropping references.
        """
        if self._cleaned:
            return
        self._cleaned = True
        if self._details is not None:
            self._details.clear()

        del self._code
        del self._message
        del self._severity
        del self._spell_id
        del self._root_id
        del self._source
        del self._details

    @property
    def code(self) -> str:
        """Return the machine-readable diagnostic code."""
        self.check_cleaned()
        return self._code

    @property
    def message(self) -> str:
        """Return the human-readable diagnostic message."""
        self.check_cleaned()
        return self._message

    @property
    def severity(self) -> SystemDiagnosticSeverity:
        """Return the diagnostic severity bucket."""
        self.check_cleaned()
        return self._severity

    @property
    def spell_id(self) -> Optional[str]:
        """Return the optional spell id associated with this diagnostic."""
        self.check_cleaned()
        return self._spell_id

    @property
    def root_id(self) -> Optional[str]:
        """Return the optional root id associated with this diagnostic."""
        self.check_cleaned()
        return self._root_id

    @property
    def source(self) -> Optional[str]:
        """Return the optional producing strategy/source identifier."""
        self.check_cleaned()
        return self._source

    @property
    def details(self) -> Optional[Dict[str, Any]]:
        """Return a defensive copy of the optional structured detail payload."""
        self.check_cleaned()
        if self._details is None:
            return None
        return dict(self._details)

    def __repr__(self) -> str:
        """Return a compact debug representation of the diagnostic identity."""
        return (
            f"SystemDiagnostic(code={self._code!r}, severity={self._severity!r}, "
            f"spell_id={self._spell_id!r}, root_id={self._root_id!r}, "
            f"source={self._source!r})"
        )
