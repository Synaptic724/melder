"""
The one error type this plane defines.

WHY THIS IS NOT IN `melder/utilities/custom_exceptions/` with every other
custom exception in the repo: `test_plane_depends_on_nothing_but_utilities`
asserts that this package has EXACTLY ONE external melder dependency -
`melder.utilities.general_base.cleanable`. That guard exists so coupling
cannot drift in quietly, and it is doing its job: putting this type in the
shared exceptions directory added a second dependency and the test caught it
immediately.

Following repo convention would have meant weakening a live design guard to
accommodate a file placement. The guard is the stronger signal, and this type
is plane-specific anyway - it describes a transaction outcome and means
nothing outside this package.
"""



class UnwindConflictError(RuntimeError):
    """
    Purpose:
        Signal that a transaction failed, was asked to UNWIND, and COULD NOT -
        so the world was left exactly as the failure found it and the fact was
        recorded rather than papered over.

        The name is deliberate. This is the one thing a scope-claim plane
        genuinely cannot resolve: claims serialise access, they do not reverse
        effects. When there is no inverse to run, or an inverse itself fails,
        there is nothing left to arbitrate - only something to report.

    Raised When:
        A transaction under `OutcomePolicy.UNWIND` reaches `fail(...)` and
        either

        - NO inverse was ever registered, so unwinding would restore nothing; or
        - one or more registered inverses raised, so the world is now partly
          restored and partly not.

        Both are the same condition from the caller's side: the prior shape was
        not recovered.

    What To Do About It:
        Do not retry blindly and do not treat it as an abort. An abort means the
        world was returned toward its prior shape; this means it was not. Read
        `unwound` and `failed` to see exactly how far the reversal got, then
        repair deliberately - the plane's `AGENT_REPAIR` transaction exists so
        an agent can CLAIM that wreckage before touching it, rather than
        reaching into a damaged world unmediated.

        If you are the author of the failing transaction and you expected an
        unwind, the bug is upstream: nobody registered an inverse. A plane
        cannot author one for you, because writing an inverse means touching the
        subsystem objects the plane is forbidden to import.

    Contract:
        - Subclasses `RuntimeError`, so a caller that only knows about runtime
          failures still catches it.
        - IMMUTABLE after construction. Every field is read-only; the record is
          evidence and evidence does not get edited.
        - `unwound` and `failed` are value-only tuples of strings - the
          DESCRIPTIONS registered alongside each inverse, never the callables.
          A record that held live closures could not be logged, shipped or
          retained after the world it describes is gone.
        - Raising is the CALLER's choice, not the session's. `fail(...)` records
          the conflict and returns it; it does not raise, because it is already
          the failure path and raising there would mask the original error in
          every `finally` block that calls it. This type exists so a caller that
          wants to escalate has something precise to raise and to catch.

    Threading:
        Immutable after construction; safe to share across threads.

    Registration:
        MELDER KERNEL - guarded. A value-only error type; never bound.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. Raised when a failed transaction could not be unwound -
        the world was left as the failure found it. Read `unwound` and `failed`
        to see how far reversal got, then repair through an AGENT_REPAIR
        transaction rather than reaching in directly.
    """

    __slots__ = ("_failed", "_reason", "_request_id", "_unwound")

    def __init__(
            self,
            *,
            request_id: str,
            reason: str,
            unwound: tuple[str, ...] = (),
            failed: tuple[str, ...] = (),
    ) -> None:
        """
        Build one unwind-conflict record.

        Args:
            request_id:
                The transaction whose unwind could not complete.
            reason:
                The ORIGINAL failure reason, carried forward. The conflict is
                the consequence; this is the cause, and losing it would leave a
                reader with a symptom and no diagnosis.
            unwound:
                Descriptions of the inverses that DID run successfully, newest
                first. Empty when nothing ran.
            failed:
                Descriptions of the inverses that raised, each with its error.
                Empty when nothing was registered to run.

        Returns:
            None.
        """
        self._request_id = request_id
        self._reason = reason
        self._unwound = tuple(unwound)
        self._failed = tuple(failed)
        if failed:
            detail = f"{len(self._unwound)} inverse(s) ran, {len(self._failed)} failed"
        else:
            detail = "no inverse was registered, so nothing could be reversed"
        super().__init__(
            f"transaction {request_id!r} failed ({reason}) and could not be unwound: {detail}. "
            "The world was left as the failure found it."
        )

    @property
    def request_id(self) -> str:
        """Return the transaction whose unwind could not complete."""
        return self._request_id

    @property
    def reason(self) -> str:
        """Return the ORIGINAL failure reason that started the unwind."""
        return self._reason

    @property
    def unwound(self) -> tuple[str, ...]:
        """Return descriptions of the inverses that ran successfully."""
        return self._unwound

    @property
    def failed(self) -> tuple[str, ...]:
        """Return descriptions of the inverses that raised, with their errors."""
        return self._failed

    def describe(self) -> dict:
        """
        Return a detached, value-only view of this conflict.

        Returns:
            dict: `request_id`, `reason`, `unwound`, `failed`.
        """
        return {
            "request_id": self._request_id,
            "reason": self._reason,
            "unwound": self._unwound,
            "failed": self._failed,
        }
