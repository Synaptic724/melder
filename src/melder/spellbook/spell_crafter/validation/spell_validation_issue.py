from typing import Optional, Dict, Any

from mypy_extensions import mypyc_attr

# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
@mypyc_attr(native_class=True)
class SpellValidationIssue(Cleanable):
    """
    Single validation issue (error or warning) produced by a strategy.

    Purpose:
        Represent one validation finding with optional attribution and context.
    Contract:
        - "severity" must be ""error"" or ""warning"".
        - "code" and "message" must be non-empty strings.
        - "source" is optional and used for strategy attribution.
    Attributes
    ----------
    severity:
        Either ""error"" or ""warning"".
    code:
        Machine-readable identifier for the issue (e.g. "DANGLING_DEPENDENCY").
    message:
        Human-readable message explaining the issue.
    source:
        Optional strategy identifier that produced the issue.
    details:
        Optional extra context for tooling (parameter name, cycle, etc.).
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "severity",
        "code",
        "message",
        "source",
        "details",
    ]

    def __init__(
            self,
            severity: str,
            code: str,
            message: str,
            details: Optional[Dict[str, Any]] = None,
            source: Optional[str] = None,
    ) -> None:
        """
        Purpose:
            Construct a single validation issue for a spell.
        Contract:
            - Accepts only "error" or "warning" for severity.
            - Requires non-empty code and message values.
            - Preserves provided details and source metadata for diagnostics.
        Args:
            severity: Either "error" or "warning".
            code: Machine-readable issue identifier.
            message: Human-readable explanation of the issue.
            details: Optional structured context for tooling.
            source: Optional strategy identifier for attribution.
        Returns:
            None.
        Raises:
            ValueError: If severity is invalid or code/message are empty.
        """
        super().__init__()

        if severity not in ("error", "warning"):
            raise ValueError("severity must be 'error' or 'warning'.")
        if not code:
            raise ValueError("code cannot be empty.")
        if not message:
            raise ValueError("message cannot be empty.")

        self.severity: str = severity
        self.code: str = code
        self.message: str = message
        self.source: Optional[str] = source
        self.details: Dict[str, Any] = details or {}

    def cleanup(self) -> None:
        """
        Deterministically detach any heavy references held in `details`.

        This clears the details mapping and marks the issue as cleaned.
        """
        if self._cleaned:
            return

        # Clear user-attached context to help GC.
        try:
            self.details.clear()
        except Exception:
            # Never let diagnostics cleanup explode callers.
            pass

        self._cleaned = True
