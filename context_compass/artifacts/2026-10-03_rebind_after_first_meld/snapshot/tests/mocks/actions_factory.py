"""Concrete action references for native construction and lifetime contract tests."""

from melder_ops.command_center.spectrum.actions.action.action import Action
from melder_ops.command_center.spectrum.actions.action.gather import Gather
from melder_ops.command_center.spectrum.actions.action.distribute import Distribute


class PayloadAction(Action):
    """Borrow an exact payload and report one effective explicit/native cleanup."""

    def __init__(self, payload: object) -> None:
        """Store the supplied object without constructing or adopting its contents."""
        super().__init__()
        self.payload: object = payload
        self.cleanup_count: int = 0

    def execute(self) -> object:
        """Return the exact supplied payload while live."""
        self.check_cleaned()
        return self.payload

    def cleanup(self) -> None:
        """Release the payload once while preserving the observable disposal count."""
        if self._cleaned:
            return
        self._cleaned = True
        self.cleanup_count += 1
        del self.payload


class ExplodingAction(Action):
    """Refuse construction before a product can be admitted into a scope."""

    def __init__(self) -> None:
        """Raise the named constructor error after initializing Cleanable state."""
        super().__init__()
        raise ValueError("action construction refused")

    def cleanup(self) -> None:
        """Retire the empty partial object if its constructor caller still holds it."""
        self._cleaned = True

    def execute(self) -> None:
        """Never run because the constructor always refuses."""
        raise AssertionError("unconstructed action executed")


class ReplacementGather(Gather):
    """Keep Gather's inputs but make alias replacement observable through its result."""

    def execute(self) -> dict[str, object]:
        """Return the configured key instead of reading any agent inventory."""
        return {"replacement": self.key_to_gather}


class FailingGather(Gather):
    """Raise during execution so facade cleanup and cache removal can be observed."""

    def execute(self) -> dict[str, object]:
        """Raise a stable execution error without modifying agent state."""
        raise ValueError("gather execution refused")


class FailingDistribute(Distribute):
    """Raise during broadcast so the facade's failure retirement is exercised."""

    def execute(self) -> bool:
        """Raise a stable execution error without writing inventories."""
        raise ValueError("distribute execution refused")
