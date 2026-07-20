


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
        USER-BINDABLE - deliberately unguarded. Exception types are values users
        catch and may legitimately register. Note this class IS a base class,
        but the MRO concern does not apply: the sentinel is what must not be
        inherited, and no exception in this family carries one.

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
    """

    def __init__(self, message: str) -> None:
        """
        Build a scheduler-scoped runtime error.

        Args:
            message (str): Human-readable diagnostic message describing the
                scheduler failure.
        """
        super().__init__(message)
