from typing import Mapping, Optional, Protocol, Set, runtime_checkable, Dict
import threading

from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.ispell import ISpell
from melder.utilities.interfaces.ispellbook import ISpellbook


@runtime_checkable
class IRiskManager(ICleanable, Protocol):
    """
    DevOps risk tracking for meld validation gating.

    ``RiskManager`` is the conduit-local risk aggregator that feeds back into the
    spellbook-level validation-required signal used by Meld-facing runtime flows.
    It does not validate spells itself and instead watches validity changes to
    fold them into one operational risk posture per conduit.
    """

    _lock: threading.RLock
    _conduit_states: Mapping[str, object]
    _lineage_conduits: Dict[str, Set[str]]

    def register_conduit(self, conduit_id: str, spellbook: ISpellbook) -> None:
        """
        Register a conduit with its Spellbook and initialize risk state.

        Args:
            conduit_id: Conduit identifier to track.
            spellbook: Spellbook whose spells should be registered.
        """
        ...

    def unregister_conduit(self, conduit_id: str) -> None:
        """
        Remove conduit tracking and clear lineage mappings.

        Args:
            conduit_id: Conduit identifier to remove.
        """
        ...

    def register_spell(self, conduit_id: str, spell: ISpell) -> None:
        """
        Register a spell into a conduit's risk tracking.

        Args:
            conduit_id: Conduit identifier to update.
            spell: Spell instance to register.
        """
        ...

    def unregister_spell(self, conduit_id: str, spell: ISpell) -> None:
        """
        Remove a spell from a conduit's risk tracking.

        Args:
            conduit_id: Conduit identifier to update.
            spell: Spell instance to unregister.
        """
        ...

    def on_structural_validity_change(
            self,
            lineage_id: str,
            validity: Optional[SpellValidity],
    ) -> None:
        """
        Update conduit risk when structural validity changes for a lineage.

        Args:
            lineage_id: Lineage identifier whose structural validity changed.
            validity: New structural validity.
        """
        ...

    def on_resolution_validity_change(
            self,
            conduit_id: str,
            spell_id: str,
            validity: Optional[SpellValidity],
    ) -> None:
        """
        Update conduit risk when per-conduit resolution validity changes.

        Args:
            conduit_id: Conduit identifier whose resolution validity changed.
            spell_id: Versioned spell id for the update.
            validity: New resolution validity.
        """
        ...
