from melder.utilities.custom_exceptions.phase_scheduler_error import PhaseSchedulerError


class PhaseTimeoutError(PhaseSchedulerError):
    """
    Raised when a phase exceeds its configured barrier timeout.
    """

    def __init__(self, phase_name: str, timeout_ms: int) -> None:
        msg = (
            f"Phase '{phase_name}' exceeded barrier timeout "
            f"({timeout_ms} ms). Resolution pipeline aborted."
        )
        super().__init__(msg)
        self.phase_name = phase_name
        self.timeout_ms = timeout_ms
