"""
The admission verdict for one transaction request on the mediator plane.

Dependency-free beyond the standard library by design.

Mirrors `ChangeControlAdmissionResult`, including the property that matters
most: admission returns EVIDENCE, NOT A BOOL. A refused request must be able to
say which scope stopped it and who held that scope, or the caller cannot retry
intelligently and an operator cannot see why anything is stuck.
"""

from enum import StrEnum
from typing import Tuple

from melder.utilities.general_base.cleanable import Cleanable


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


class AdmissionResult(Cleanable):
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
        Value fields only - one bool and three tuples of strings. Holds no
        reference to the table, the session, or any holder.

    Lifecycle / Cleanup:
        `Cleanable`. OWNER RULING, 2026-08-01, and it REVERSES the position an
        earlier revision of this docstring argued at length. That argument -
        that a verdict has no owner and no moment, so a cleanup contract would
        be ceremony - is recorded here rather than deleted, because the reader
        who wonders why a four-field value object carries a lifecycle deserves
        the actual history:

            the verdict has an owner and a moment after all, and naming them
            forced them to be looked for rather than assumed absent.

        THE OWNER IS THE ADMISSION LOOP; THE MOMENT IS WHEN IT LETS GO:
          - `Mediator._admit_with_wait` builds one verdict per attempt. A
            refused verdict is finished the instant the loop has harvested
            what it needs and is about to park - so it is cleaned there,
            before the next attempt allocates its replacement. Under real
            contention that loop can spin many times, which makes this the
            hot path for accumulation rather than a rare one.
          - `Mediator.begin` cleans the verdict it received once it has read
            the outcome - after rendering the refusal message, in the refused
            case, because the message is the last thing anyone needs from it.

        NOTHING RETAINS A VERDICT past that: it is never stored on the
        session, the orchestrator, or the registry, and the refusal path turns
        it into an error message string rather than keeping the object. So
        every `cleanup()` call is made by the code that is demonstrably done
        with it, which is the discriminator the repo actually uses.

    Threading:
        Immutable; safe to share across threads without synchronisation. No
        lock: a verdict is built by one thread, read by that same thread, and
        cleaned by it.

    Registration:
        MELDER KERNEL - guarded. Produced by admission; never user-built.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Immutable admission verdict carrying refusal reasons,
        contended scope keys, and rendered blocking evidence.
    """

    # Slotted rather than dict-backed: a verdict is allocated on every refused
    # admission attempt, so the per-instance dict is real cost on the one path
    # that is by definition already contended.
    __slots__ = Cleanable.__slots__ + [
        "_admitted", "_reasons", "_blocked_scopes", "_evidence",
    ]

    def __init__(
            self,
            *,
            admitted: bool,
            reasons: Tuple[AdmissionReason, ...] = (),
            blocked_scopes: Tuple[str, ...] = (),
            evidence: Tuple[str, ...] = (),
    ) -> None:
        """
        Build one immutable verdict.

        Contract:
            Prefer the `granted()` and `refused(...)` factories - `refused`
            enforces the non-empty-reason rule that makes a refusal legal.
            Tuples are immutable, so the empty-tuple defaults are safe to
            share across every instance.

        Args:
            admitted: Whether the request was admitted.
            reasons: Machine-readable refusal codes; empty when admitted.
            blocked_scopes: Contended scope keys, for programmatic retry.
            evidence: Rendered blocking lines, for a human or agent.

        Returns:
            None.
        """
        super().__init__()
        self._admitted: bool = admitted
        self._reasons: Tuple[AdmissionReason, ...] = reasons
        self._blocked_scopes: Tuple[str, ...] = blocked_scopes
        self._evidence: Tuple[str, ...] = evidence

    def cleanup(self) -> None:
        """
        Idempotently drop this verdict once its reader is finished with it.

        Contract:
            Called by the admission loop that owns it - `_admit_with_wait` for
            each superseded attempt, `begin` for the one it received. Read the
            outcome and render any message BEFORE cleaning; both callers do.

            Idempotent, so `begin` may clean a verdict `_admit_with_wait`
            already released without checking first.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._admitted
        del self._reasons
        del self._blocked_scopes
        del self._evidence

    @property
    def admitted(self) -> bool:
        """
        Report whether the request was admitted.

        Returns:
            bool: True when the claims are held on return from admission.

        Raises:
            RuntimeError: If the verdict has been cleaned.
        """
        self.check_cleaned()
        return self._admitted

    @property
    def reasons(self) -> Tuple[AdmissionReason, ...]:
        """
        Return the machine-readable refusal codes.

        Returns:
            Tuple[AdmissionReason, ...]: Empty when admitted; otherwise at
                least one code, because a refusal without a reason is not a
                legal verdict.

        Raises:
            RuntimeError: If the verdict has been cleaned.
        """
        self.check_cleaned()
        return self._reasons

    @property
    def blocked_scopes(self) -> Tuple[str, ...]:
        """
        Return the contended scope keys, for programmatic retry.

        Returns:
            Tuple[str, ...]: Sorted contended keys, empty when admitted.

        Raises:
            RuntimeError: If the verdict has been cleaned.
        """
        self.check_cleaned()
        return self._blocked_scopes

    @property
    def evidence(self) -> Tuple[str, ...]:
        """
        Return the rendered blocking lines, for a reader diagnosing a stall.

        Returns:
            Tuple[str, ...]: One line per block, empty when admitted.

        Raises:
            RuntimeError: If the verdict has been cleaned.
        """
        self.check_cleaned()
        return self._evidence

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
