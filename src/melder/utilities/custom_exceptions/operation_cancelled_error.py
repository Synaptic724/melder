
class OperationCancelledError(RuntimeError):
    """
    Raised when a unit of work observes that cancellation has been requested
    and chooses to abort its execution.

    This is intentionally a simple subclass of RuntimeError so callers can:
        * Catch this specific type to distinguish cooperative cancellations
          from other failures, or
        * Treat it as a normal runtime failure if they do not care.

    In Melder / CommandOps, this is expected to surface from worker threads
    running resolution / compilation tasks when the shared cancellation
    event has been signalled.
    """
