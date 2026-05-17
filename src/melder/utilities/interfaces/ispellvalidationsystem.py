from typing import Any, Optional, Protocol, runtime_checkable

from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.ispell import ISpell


@runtime_checkable
class ISpellValidationSystem(ICleanable, Protocol):
    """
    Interface for the spell-level validation service owned by `Spellbook` and
    borrowed by `SpellCrafter`.

    The concrete runtime owns strategy registration and validation execution,
    but collaborators outside that module boundary only need the ability to
    validate one spell and to participate in cleanup/lifecycle contracts.
    """

    def cleanup(self) -> None:
        """
        Deterministically clean the validation-system surface.
        """
        ...

    def validate_spell(
            self,
            *,
            spell: ISpell,
            requirements: Optional[Any],
            symbolic_graph: Optional[Any],
            resolution_frame: Optional[Any],
            cancel_event: Optional[Any] = None,
    ) -> Any:
        """
        Validate one spell and return the aggregate validation result.

        Args:
            spell: Spell being validated.
            requirements: Phase 1 requirements artifact, when present.
            symbolic_graph: Phase 2 symbolic graph artifact, when present.
            resolution_frame: Phase 3 resolution-frame artifact, when present.
            cancel_event: Optional cancellation token.

        Returns:
            Any: Concrete validation result object returned by the implementation.
        """
        ...
