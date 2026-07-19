from melder.utilities.custom_exceptions.phase_scheduler_error import PhaseSchedulerError



class PhaseTimeoutError(PhaseSchedulerError):
    """
    Purpose:
        Signal that one scheduled phase exceeded its configured barrier timeout
        and the resolution pipeline was aborted.

    Raised When:
        A phase's units of work do not all report before the barrier deadline.
        The scheduler runs phases behind barriers, so a phase that never
        completes would otherwise stall conjure indefinitely; the timeout turns
        that hang into a diagnosable failure.

    What To Do About It:
        A timeout usually means work is blocked, not slow. Look for a
        constructor that blocks on I/O, a lock held across a phase boundary, or
        a hook waiting on something that never arrives. Raising the timeout
        budget hides the hang rather than fixing it.

    Contract:
        - Identifies the phase that timed out.
        - Preserves the configured timeout value in milliseconds for callers,
          logs, and higher-level scheduler diagnostics.
        - Subclasses `PhaseSchedulerError`, so callers may catch either the
          specific timeout or the whole scheduler family.

    Owned State:
        - `phase_name`: the phase that exceeded its budget.
        - `timeout_ms`: the configured budget, in milliseconds.

    Registration:
        USER-BINDABLE - deliberately unguarded. Exception types are values users
        catch and may legitimately register.

    Subsystem Context:
        One of the 11 `utilities/custom_exceptions/` types and one of two
        concrete children of `PhaseSchedulerError`. Its sibling
        `PhaseExecutionError` means the work RAN and failed; this one means the
        work never reported at all. That distinction is the whole reason both
        types exist.

    System Context:
        Fires during conjure, at a phase barrier. Because it aborts before a
        Conduit exists, nothing has been registered into Aether and no cleanup
        cascade is owed - the failure is total and leaves no partial world.
    """

    def __init__(self, phase_name: str, timeout_ms: int) -> None:
        """
        Build a timeout error for one named phase.

        Args:
            phase_name (str): Name of the scheduler phase that exceeded its
                timeout budget.
            timeout_ms (int): Configured timeout in milliseconds.
        """
        msg = (
            f"Phase '{phase_name}' exceeded barrier timeout "
            f"({timeout_ms} ms). Resolution pipeline aborted."
        )
        super().__init__(msg)
        self.phase_name = phase_name
        self.timeout_ms = timeout_ms
