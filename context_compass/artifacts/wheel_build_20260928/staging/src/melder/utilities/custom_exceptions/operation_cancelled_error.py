


class OperationCancelledError(RuntimeError):
    """

    Purpose:
        Signal that work stopped because cooperative cancellation was observed -
        an abort, not a failure. Distinguishes "we were told to stop" from
        "something went wrong".

    Raised When:
        A worker thread or staged runtime helper observes a signalled shared
        cancellation event and chooses to abort promptly rather than finish.
        Cancellation here is COOPERATIVE: nothing is killed, each unit of work
        checks the signal and unwinds itself.

    What To Do About It:
        Usually nothing. This is the expected outcome of a cancelled run, and
        treating it as an error will produce noisy logs for normal shutdown.
        Catch it distinctly from real failures - that separation is the reason
        it has its own type instead of reusing a generic abort.

    Contract:
        - Signals that work stopped because a shared cancellation source was
          tripped, not because the underlying operation failed semantically.
        - Remains a `RuntimeError` subclass so callers can either catch the
          specific cooperative-cancellation case or treat it as a general
          runtime abort.
        - Carries no cancellation-source identity; the signal is shared, so the
          question "who cancelled" is answered by the owning scheduler, not by
          this error.

    Registration:
        Exported on the public root surface; import, raise, and catch freely.

    Subsystem Context:
        One of the 11 `utilities/custom_exceptions/` types, paired with
        `utilities/synchronization/cancellation_event_signal.py`
        (`CancellationEvent`, `CancellationEventSignal`) and consumed by the
        `PhaseScheduler` worker pool.

    System Context:
        Crosses phase and runtime boundaries wherever a shared cancellation
        signal reaches a unit of work. Unlike the scheduler error family, it is
        not a defect report - a cancelled conjure and a failed conjure both end
        without a Conduit, and this type is what tells the caller which one
        happened.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. Raised when a unit of work observes cooperative cancellation; catch it
        distinctly from real failures - it means aborted, not broken.
    """

