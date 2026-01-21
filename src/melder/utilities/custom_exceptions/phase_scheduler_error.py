class PhaseSchedulerError(RuntimeError):
    """
    Base exception for PhaseScheduler-related failures.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)