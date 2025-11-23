from typing import List
# Melder Imports
from melder.utilities.custom_exceptions.phase_scheduler_error import PhaseSchedulerError


class PhaseExecutionError(PhaseSchedulerError):
    """
    Raised when one or more units of work in a phase fail.

    Attributes:
        phase_name: Name of the failing phase.
        errors: List of exceptions raised by the phase's units.
    """

    def __init__(self, phase_name: str, errors: List[BaseException]) -> None:
        msg = (
            f"Phase '{phase_name}' encountered {len(errors)} error(s). "
            f"Resolution pipeline aborted."
        )
        super().__init__(msg)
        self.phase_name = phase_name
        self.errors = errors
