"""
The admission verdict for one transaction request on the mediator plane.

Dependency-free beyond the standard library by design.

Mirrors `ChangeControlAdmissionResult`, including the property that matters
most: admission returns EVIDENCE, NOT A BOOL. A refused request must be able to
say which scope stopped it and who held that scope, or the caller cannot retry
intelligently and an operator cannot see why anything is stuck.
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Tuple


class AdmissionReason(StrEnum):
    """
    Machine-readable codes explaining one admission outcome.

    Purpose:
        Let callers branch on WHY a request was refused without parsing the
        rendered human-facing evidence lines.

    Contract:
        - Values are stable; they travel into logs and stored evidence.
        - Codes describe the CLASS of refusal. The specific contended scopes
          and holders travel separately on the result, so one code can carry
          many concrete blocks.

    Threading:
        Stateless enum; safe to share across threads.

    Registration:
        MELDER KERNEL - guarded. Diagnostic vocabulary; never bound.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Machine-readable admission refusal codes. Branch on
        these rather than parsing evidence strings.
    """

    SCOPE_CONTENDED = "scope_contended"
    WAIT_TIMEOUT = "wait_timeout"
    PLANE_CLEANED = "plane_cleaned"
    NO_STRATEGY = "no_strategy"
    INVALID_REQUEST = "invalid_request"


@dataclass(frozen=True)
class AdmissionResult:
    """
    The immutable verdict for one admission attempt.

    Purpose:
        Carry the outcome of admission together with enough evidence that a
        refusal is actionable - retryable by a caller, explicable to an
        operator, and reportable by the information layer without reaching
        back into live plane state.

    Contract:
        - IMMUTABLE. Frozen so a verdict cannot be edited after the fact by
          whatever consumes it.
        - EVIDENCE, NOT A BOOL. `admitted=False` always carries at least one
          reason; a bare False is not a legal verdict. This is the same
          property the DevOps plane holds and for the same purpose: a blocked
          transaction should see exactly what stopped it.
        - FULLY DETACHED. Every field is a value or a tuple of values -
          strings, never live `Identity` or `ClaimBlock` references. That
          keeps a verdict safe to log, serialise, ship, or retain after the
          plane has moved on, and matches the DevOps information layer's rule
          that results are detached ids-only payloads.
        - `blocked_scopes` and `evidence` are parallel VIEWS OF THE SAME
          BLOCKS at different fidelity: the first for programmatic retry
          against specific keys, the second for a human or agent reading a
          message.

    Owned State:
        Value fields only. Holds no reference to the table, the session, or
        any holder.

    Threading:
        Immutable; safe to share across threads without synchronisation.

    Registration:
        MELDER KERNEL - guarded. Produced by admission; never user-built.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Immutable admission verdict carrying refusal reasons,
        contended scope keys, and rendered blocking evidence.
    """

    # Every field is a value or a tuple of values. Tuples are immutable, so
    # `= ()` is a safe shared default and `field(default_factory=...)` - which
    # exists to avoid shared MUTABLE defaults - would be noise here.
    admitted: bool
    reasons: Tuple[AdmissionReason, ...] = ()
    blocked_scopes: Tuple[str, ...] = ()
    evidence: Tuple[str, ...] = ()

    @staticmethod
    def granted() -> "AdmissionResult":
        """
        Build the verdict for a successful admission.

        Contract:
            A granted verdict carries no reasons, no blocked scopes, and no
            evidence: there is nothing to explain.

        Returns:
            AdmissionResult: An admitted verdict with empty evidence.
        """
        return AdmissionResult(admitted=True)

    @staticmethod
    def refused(
            *,
            reasons: Tuple[AdmissionReason, ...],
            blocked_scopes: Tuple[str, ...] = (),
            evidence: Tuple[str, ...] = (),
    ) -> "AdmissionResult":
        """
        Build the verdict for a refused admission.

        Args:
            reasons:
                One or more machine-readable refusal codes. Must be non-empty;
                a refusal without a reason is not a legal verdict.
            blocked_scopes:
                The contended scope keys, for programmatic retry.
            evidence:
                Rendered blocking lines, for a human or agent reading the
                failure.

        Returns:
            AdmissionResult: A refused verdict carrying its evidence.

        Raises:
            ValueError: If `reasons` is empty, because a silent refusal is
                exactly the failure this type exists to prevent.
        """
        if not reasons:
            raise ValueError(
                "A refused AdmissionResult requires at least one reason; a "
                "refusal a caller cannot explain is not a legal verdict."
            )
        return AdmissionResult(
            admitted=False,
            reasons=tuple(reasons),
            blocked_scopes=tuple(blocked_scopes),
            evidence=tuple(evidence),
        )

    def describe(self) -> str:
        """
        Render this verdict as one diagnostic line.

        Returns:
            str: `"admitted"`, or a refusal naming its codes and evidence.
        """
        if self.admitted:
            return "admitted"
        codes = ", ".join(reason.value for reason in self.reasons)
        if not self.evidence:
            return "refused [{0}]".format(codes)
        return "refused [{0}]: {1}".format(codes, "; ".join(self.evidence))
