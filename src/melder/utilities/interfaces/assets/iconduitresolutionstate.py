from typing import runtime_checkable, Protocol, Optional, List, Mapping, Sequence

from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.utilities.interfaces.assets.icleanable import ICleanable


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
