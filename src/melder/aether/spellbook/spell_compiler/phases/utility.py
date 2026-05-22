from typing import TYPE_CHECKING, Optional



if TYPE_CHECKING:
    from melder.utilities.synchronization.cancellation_event_signal import (
        CancellationEvent,
    )



class CompilerPhaseUtility:
    """
    Shared static generic helper surface for compiler phases.

    Purpose:
        Provide one compiler-side home for small generic helper behavior that
        multiple extracted phase classes can reuse without re-inlining it in
        every phase module.

    Contract:
        - Slot-only static helper surface with no `__init__`.
        - Does not own compiler state, runtime collaborators, or lifecycle.
        - Contains only generic compiler-phase helper behavior.
    """

    __slots__ = ()

    @staticmethod
    def throw_if_cancelled(
            cancel_event: Optional[CancellationEvent],
    ) -> None:
        """
        Raise through the cancellation event when cancellation is signalled.

        Args:
            cancel_event:
                Optional shared cancellation signal used by compiler phases.

        Returns:
            None.
        """
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()
