from melder.utilities.custom_exceptions.phase_scheduler_error import PhaseSchedulerError
from mypy_extensions import mypyc_attr

@mypyc_attr(native_class=False)
class PhaseTimeoutError(PhaseSchedulerError):
    """
    Raised when one scheduled phase exceeds its configured barrier timeout.

    Contract:
        - Identifies the phase that timed out.
        - Preserves the configured timeout value in milliseconds for callers,
          logs, and higher-level scheduler diagnostics.
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
