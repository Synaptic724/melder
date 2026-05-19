from mypy_extensions import mypyc_attr

@mypyc_attr(native_class=True)
class OperationCancelledError(RuntimeError):
    """
    Raised when cooperative cancellation has been observed and execution stops.

    Contract:
        - Signals that work stopped because a shared cancellation source was
          tripped, not because the underlying operation failed semantically.
        - Remains a `RuntimeError` subclass so callers can either catch the
          specific cooperative-cancellation case or treat it as a general
          runtime abort.

    Typical source:
        Worker threads and staged runtime helpers raise this when a shared
        cancellation event has been signalled and the current unit of work
        chooses to abort promptly.
    """
