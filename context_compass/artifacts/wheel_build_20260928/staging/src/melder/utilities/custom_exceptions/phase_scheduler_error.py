


class PhaseSchedulerError(RuntimeError):
    """

    Purpose:
        Base exception for PhaseScheduler failures. One stable parent type so a
        caller can catch "the phase pipeline failed" without enumerating every
        specific cause.

    Raised When:
        Rarely raised directly. Its two in-tree children are the real signals:
        `PhaseExecutionError` (units of work inside a phase failed) and
        `PhaseTimeoutError` (a phase exceeded its barrier timeout). Catch this
        parent when either outcome means the same thing to you.

    What To Do About It:
        Reaching this means the conjure pipeline aborted, so no Conduit was
        produced. Inspect the concrete child for the phase name and either the
        collected errors or the timeout budget.

    Contract:
        - Provides one stable parent type for scheduler admission, execution,
          timeout, and barrier-related failures.
        - Carries the rendered message unchanged so child exceptions can define
          their own higher-level diagnostics.
        - Subclasses `RuntimeError`.

    Registration:
        Exported on the public root surface; import, raise, and catch freely.

    Subsystem Context:
        One of the 11 `utilities/custom_exceptions/` types and the root of the
        scheduler family. It pairs with `utilities/synchronization/
        phase_scheduler.py`, which coordinates phase workers, barriers, and the
        shared cancellation signal.

    System Context:
        Fires during conjure, which runs phases 1-4 (structural), 5-7
        (foundational resolution), and 8-11 (plan resolution) through the
        PhaseScheduler. A failure here aborts before a Conduit exists, so it is
        strictly a build-time error - distinct from `MeldExecutionError`, which
        is the runtime-resolution counterpart.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. Base type for PhaseScheduler failures; catch it to mean 'the conjure
        phase pipeline aborted' without enumerating PhaseExecutionError vs PhaseTimeoutError.
    """


    def __init__(self, message: str) -> None:
        """
        Build a scheduler-scoped runtime error.

        Args:
            message (str): Human-readable diagnostic message describing the
                scheduler failure.

        Contract:
            - PASS-THROUGH constructor: it forwards the message unchanged and adds no
              fields of its own. The type IS the information - it marks a failure as
              originating in phase scheduling rather than in a phase's own work.

        Threading:
            Plain construction; no shared state.

        Lifecycle / Cleanup:
            None - it is an exception value.

        Returns:
            None.
        """
        super().__init__(message)
