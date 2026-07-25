from typing import Optional, Dict, Any, ClassVar



# Melder imports
from melder.utilities.general_base.cleanable import Cleanable

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

    Registration:
        MELDER KERNEL - guarded. A compiler diagnostic value; not user-bindable.

    Subsystem Context:
        The unit of the `validation` package: strategies emit these into
        `SpellValidationContext.issues`, and `SpellValidationResult` aggregates
        them into split error/warning views.

    System Context:
        Phase 4 (validation) of the conjure pipeline. A structural diagnostic
        only - but an `error`-severity issue is what ultimately makes a spell
        "broken" and raises `SpellbookValidationError` at the Spellbook boundary.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. One Phase-4 validation finding: severity ('error'|'warning'), code, "
        "message, optional source (emitting strategy) and details. The unit strategies append "
        "into the context's issues list."
    )
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
