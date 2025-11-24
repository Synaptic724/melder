from typing import Optional, Dict, Any
# Melder imports
from melder.utilities.general_base.cleanable import Cleanable


class SpellValidationIssue(Cleanable):
    """
    Single validation issue (error or warning) produced by a strategy.

    Attributes
    ----------
    severity:
        Either ``"error"`` or ``"warning"``.
    code:
        Machine-readable identifier for the issue (e.g. "DANGLING_DEPENDENCY").
    message:
        Human-readable message explaining the issue.
    details:
        Optional extra context for tooling (parameter name, cycle, etc.).
    """

    __slots__ = Cleanable.__slots__ + [
        "severity",
        "code",
        "message",
        "details",
    ]

    def __init__(
            self,
            severity: str,
            code: str,
            message: str,
            details: Optional[Dict[str, Any]] = None,
    ) -> None:
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
