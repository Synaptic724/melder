from typing import List

from mypy_extensions import mypyc_attr

# Melder Imports
from melder.utilities.custom_exceptions.phase_scheduler_error import PhaseSchedulerError

@mypyc_attr(native_class=True)
class PhaseExecutionError(PhaseSchedulerError):
    """
    Raised when one or more units of work in a phase fail.

    Contract:
        - Preserves the phase name that failed.
        - Preserves the collected error list so callers can inspect the full
          failure set after the summary message is built.
    """

    def __init__(self, phase_name: str, errors: List[BaseException]) -> None:
        """
        Purpose:
            Initialize a PhaseExecutionError with phase metadata and context.
        Contract:
            - Message includes the phase name and error count.
            - Message includes a short summary of underlying errors when present.
            - The original error list is preserved on the instance.
        Args:
            phase_name: Name of the failing phase.
            errors: Exceptions raised by the phase's units of work.
        Returns:
            None.

        Preserved state:
            - `phase_name` stores the failing phase identifier.
            - `errors` stores the original list passed to the constructor.
        """
        summary_parts: List[str] = []
        for err in errors[:3]:
            try:
                detail = str(err)
            except Exception:
                detail = "<unrepr>"
            summary_parts.append(f"{type(err).__name__}: {detail}")
        summary = "; ".join(summary_parts)
        if len(errors) > 3:
            summary = f"{summary}; +{len(errors) - 3} more"

        msg = (
            f"Phase '{phase_name}' encountered {len(errors)} error(s). "
            f"Resolution pipeline aborted."
        )
        if summary:
            msg = f"{msg} Errors: {summary}"
        super().__init__(msg)
        self.phase_name = phase_name
        self.errors = errors
