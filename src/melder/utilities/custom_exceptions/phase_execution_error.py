from typing import List
# Melder Imports
from melder.utilities.custom_exceptions.phase_scheduler_error import PhaseSchedulerError



class PhaseExecutionError(PhaseSchedulerError):
    """

    Purpose:
        Signal that one or more units of work inside a scheduled phase raised,
        aborting the resolution pipeline. Aggregates the whole failure set
        rather than surfacing only the first error.

    Raised When:
        Any unit of work in a phase raises. The scheduler runs a phase's units
        in parallel across workers, so several may fail in the same pass; all
        collected failures travel together on this one error.

    What To Do About It:
        Read `errors` for the real causes - the rendered message summarizes only
        the first three plus a count, so a bare log line is not the full story.
        `phase_name` tells you where in the pipeline it broke: phases 1-4 are
        structural, 5-7 foundational resolution, 8-11 plan resolution.

    Contract:
        - Preserves the phase name that failed.
        - Preserves the collected error list so callers can inspect the full
          failure set after the summary message is built.
        - The summary is truncated at three errors with a "+N more" suffix;
          `errors` is never truncated.
        - Subclasses `PhaseSchedulerError`.

    Owned State:
        - `phase_name`: the failing phase identifier.
        - `errors`: the original list of exceptions raised by that phase's
          units of work, unmodified.

    Registration:
        USER-BINDABLE - deliberately unguarded. Exception types are values users
        catch and may legitimately register.

    Subsystem Context:
        One of the 11 `utilities/custom_exceptions/` types and one of two
        concrete children of `PhaseSchedulerError`. Its sibling
        `PhaseTimeoutError` means the work never reported; this one means it ran
        and raised.

    System Context:
        Fires during conjure. Broken spells surfacing here are what
        `SpellbookValidationError` reports at the Spellbook boundary, so a user
        typically sees the validation error while this one carries the
        underlying per-unit detail.
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
