from typing import Dict, List, Mapping, Optional, Protocol, Sequence, runtime_checkable
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.spellbook.spell_crafter.system.system_diagnostic import SystemDiagnostic
from melder.utilities.interfaces.icleanable import ICleanable

@runtime_checkable
class IConduitResolutionState(ICleanable, Protocol):
    """
    Per-conduit resolution validity container.

    This protocol mirrors the ConduitResolutionState API used to track
    Phases 5-7 validity and diagnostics for a specific conduit.
    """

    _conduit_id: str

    def get_spell_validity(self, spell_id: str) -> Optional['SpellValidity']:
        """
        Return the stored resolution validity for one spell id.
        """
        ...

    def snapshot_spell_validity(self) -> Dict[str, 'SpellValidity']:
        """
        Return a snapshot copy of per-spell resolution validity.
        """
        ...

    def set_spell_validity(
            self,
            spell_id: str,
            validity: 'SpellValidity',
            *,
            change_reason: Optional['SpellStateChangeReason'] = None,
    ) -> None:
        """
        Set resolution validity for one spell id.

        Returns:
            None.
        """
        ...

    def bulk_set_spell_validity(
            self,
            validity_map: Mapping[str, 'SpellValidity'],
            *,
            change_reason: Optional['SpellStateChangeReason'] = None,
    ) -> None:
        """
        Bulk update resolution validity for spell ids.

        Returns:
            None.
        """
        ...

    def get_root_validity(self, root_id: str) -> Optional['SpellValidity']:
        """
        Return the stored resolution validity for one root id.
        """
        ...

    def snapshot_root_validity(self) -> Dict[str, 'SpellValidity']:
        """
        Return a snapshot copy of per-root resolution validity.
        """
        ...

    def set_root_validity(
            self,
            root_id: str,
            validity: 'SpellValidity',
            *,
            change_reason: Optional['SpellStateChangeReason'] = None,
    ) -> None:
        """
        Set resolution validity for one root id.

        Returns:
            None.
        """
        ...

    def bulk_set_root_validity(
            self,
            validity_map: Mapping[str, 'SpellValidity'],
            *,
            change_reason: Optional['SpellStateChangeReason'] = None,
    ) -> None:
        """
        Bulk update resolution validity for root ids.

        Returns:
            None.
        """
        ...

    def record_diagnostics(self, diagnostics: Sequence['SystemDiagnostic']) -> None:
        """
        Record per-conduit system diagnostics, replacing on signature change.

        Returns:
            None.
        """
        ...

    def clear_diagnostics(self) -> None:
        """
        Clear stored diagnostics.

        Returns:
            None.
        """
        ...

    def list_diagnostics(self) -> List['SystemDiagnostic']:
        """
        Return a snapshot list of stored diagnostics.
        """
        ...

    def has_errors(self) -> bool:
        """
        Return whether any stored diagnostic has ERROR severity.
        """
        ...

    def has_warnings(self) -> bool:
        """
        Return whether any stored diagnostic has WARNING severity.
        """
        ...

    def is_dirty(self) -> bool:
        """
        Return whether this conduit-resolution state currently requires revalidation.
        """
        ...

    def mark_dirty(self, change_reason: Optional['SpellStateChangeReason'] = None) -> None:
        """
        Mark this resolution state as dirty.

        Returns:
            None.
        """
        ...

    def clear_dirty(self, validated_at: float) -> None:
        """
        Mark this resolution state as clean after validation.

        Returns:
            None.
        """
        ...

    def _set_risk_manager(self, risk_manager: Optional[object]) -> None:
        """
        Internal

        Attach or replace the conduit-local risk-manager collaborator.

        Returns:
            None.
        """
        ...

    def last_validated_at(self) -> Optional[float]:
        """
        Return the last successful validation timestamp.
        """
        ...

    def cleanup(self) -> None:
        """
        Clean up the resolution state and release references.
        """
        ...
