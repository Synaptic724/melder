from threading import RLock
from typing import Dict, Optional, Set, List

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import ISpell, ISpellbook, ISpellSystemStates


class _ConduitRiskState:
    __slots__ = [
        "spellbook",
        "lineages",
        "risky_structural",
        "risky_resolution",
    ]

    def __init__(self, spellbook: ISpellbook) -> None:
        self.spellbook: ISpellbook = spellbook
        self.lineages: Set[str] = set()
        self.risky_structural: Set[str] = set()
        self.risky_resolution: Set[str] = set()


class RiskManager(Cleanable):
    """
    DevOps risk tracking for meld validation gating.

    Purpose:
        Track per-conduit risk based on spell validity. If any risky spell
        exists for a conduit, the owning Spellbook is flagged as requiring
        validation. Risk is defined as any validity that would trigger
        revalidation in Meld (unknown/gated/invalid/disabled).
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_spell_system_states",
        "_conduit_states",
        "_lineage_conduits",
    ]

    def __init__(self, spell_system_states: ISpellSystemStates) -> None:
        super().__init__()
        if spell_system_states is None:
            raise ValueError("spell_system_states cannot be None")
        self._lock: RLock = RLock()
        self._spell_system_states: ISpellSystemStates = spell_system_states
        self._conduit_states: Dict[str, _ConduitRiskState] = {}
        self._lineage_conduits: Dict[str, Set[str]] = {}

    def cleanup(self) -> None:
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if self._conduit_states is not None:
                self._conduit_states.clear()
            if self._lineage_conduits is not None:
                self._lineage_conduits.clear()
            self._spell_system_states = None
        self._lock = None

    def register_conduit(self, conduit_id: str, spellbook: ISpellbook) -> None:
        """
        Register a conduit with its Spellbook and initialize risk state.
        """
        self.check_cleaned()
        if not conduit_id or spellbook is None:
            return
        self.unregister_conduit(conduit_id)
        with self._lock:
            state = _ConduitRiskState(spellbook)
            self._conduit_states[conduit_id] = state

        for spell in self._iter_spellbook_spells(spellbook):
            self.register_spell(conduit_id, spell)

        self._refresh_spellbook_flag(conduit_id)

    def unregister_conduit(self, conduit_id: str) -> None:
        """
        Remove conduit tracking and clear lineage mappings.
        """
        self.check_cleaned()
        if not conduit_id:
            return

        with self._lock:
            state = self._conduit_states.pop(conduit_id, None)
            if state is None:
                return
            lineages = list(state.lineages)
            for lineage_id in lineages:
                conduits = self._lineage_conduits.get(lineage_id)
                if conduits is None:
                    continue
                conduits.discard(conduit_id)
                if not conduits:
                    self._lineage_conduits.pop(lineage_id, None)

    def register_spell(self, conduit_id: str, spell: ISpell) -> None:
        """
        Register a spell into a conduit's risk tracking.
        """
        self.check_cleaned()
        if not conduit_id or spell is None:
            return

        lineage_id = self._resolve_lineage_id(spell)
        if not lineage_id:
            return

        with self._lock:
            state = self._conduit_states.get(conduit_id)
            if state is None:
                return
            if lineage_id not in state.lineages:
                state.lineages.add(lineage_id)
                conduits = self._lineage_conduits.setdefault(lineage_id, set())
                conduits.add(conduit_id)
            try:
                spell_id = spell.spell_index.current
            except Exception:
                spell_id = None
            if spell_id:
                state.risky_resolution.discard(f"spell:{spell_id}")

        self._update_structural_risk(conduit_id, lineage_id, self._get_structural_validity(spell))
        self._update_resolution_risk(conduit_id, lineage_id, self._get_resolution_validity(conduit_id, spell))
        self._refresh_spellbook_flag(conduit_id)

    def unregister_spell(self, conduit_id: str, spell: ISpell) -> None:
        """
        Remove a spell from a conduit's risk tracking.
        """
        self.check_cleaned()
        if not conduit_id or spell is None:
            return

        lineage_id = self._resolve_lineage_id(spell)
        if not lineage_id:
            return

        with self._lock:
            state = self._conduit_states.get(conduit_id)
            if state is None:
                return
            state.lineages.discard(lineage_id)
            state.risky_structural.discard(lineage_id)
            state.risky_resolution.discard(lineage_id)
            conduits = self._lineage_conduits.get(lineage_id)
            if conduits is not None:
                conduits.discard(conduit_id)
                if not conduits:
                    self._lineage_conduits.pop(lineage_id, None)

        self._refresh_spellbook_flag(conduit_id)

    def on_structural_validity_change(self, lineage_id: str, validity: Optional[SpellValidity]) -> None:
        """
        Update risk when structural validity changes for a lineage.
        """
        self.check_cleaned()
        if not lineage_id:
            return
        with self._lock:
            conduits = list(self._lineage_conduits.get(lineage_id, ()))
        for conduit_id in conduits:
            self._update_structural_risk(conduit_id, lineage_id, validity)
            self._refresh_spellbook_flag(conduit_id)

    def on_resolution_validity_change(
            self,
            conduit_id: str,
            spell_id: str,
            validity: Optional[SpellValidity],
    ) -> None:
        """
        Update risk when per-conduit resolution validity changes.
        """
        self.check_cleaned()
        if not conduit_id or not spell_id:
            return
        lineage_id = self._resolve_lineage_id_from_spell_id(spell_id)
        key = lineage_id if lineage_id else f"spell:{spell_id}"
        self._update_resolution_risk(conduit_id, key, validity)
        self._refresh_spellbook_flag(conduit_id)

    # ------------------------------------------------------------------ #
    # Internal helpers                                                   #
    # ------------------------------------------------------------------ #
    def _iter_spellbook_spells(self, spellbook: ISpellbook) -> List[ISpell]:
        spells: List[ISpell] = []
        try:
            if spellbook._spells is not None:
                spells.extend(spellbook._spells.values())
            if spellbook._contracted_spells is not None:
                for spell_map in spellbook._contracted_spells.values():
                    spells.extend(spell_map.values())
        except Exception:
            pass
        return spells

    def _resolve_lineage_id(self, spell: ISpell) -> Optional[str]:
        try:
            spell_index = spell.spell_index
        except Exception:
            return None
        if spell_index is None:
            return None
        return spell_index.id

    def _resolve_lineage_id_from_spell_id(self, spell_id: str) -> Optional[str]:
        states = self._spell_system_states
        if states is None:
            return None
        try:
            state = states.get_by_spell_id(spell_id)
        except Exception:
            return None
        if state is None:
            return None
        return state.spell_index_id

    def _get_structural_validity(self, spell: ISpell) -> Optional[SpellValidity]:
        try:
            state = spell.system_state
        except Exception:
            return SpellValidity.unknown
        if state is None:
            return SpellValidity.unknown
        return state.validity

    def _get_resolution_validity(self, conduit_id: str, spell: ISpell) -> Optional[SpellValidity]:
        states = self._spell_system_states
        if states is None:
            return SpellValidity.unknown
        try:
            resolution_state = states.get_conduit_resolution_state(conduit_id)
        except Exception:
            return SpellValidity.unknown
        if resolution_state is None:
            return SpellValidity.unknown
        try:
            spell_id = spell.spell_index.current
        except Exception:
            return SpellValidity.unknown
        try:
            return resolution_state.get_spell_validity(spell_id)
        except Exception:
            return SpellValidity.unknown

    def _update_structural_risk(
            self,
            conduit_id: str,
            lineage_id: str,
            validity: Optional[SpellValidity],
    ) -> None:
        with self._lock:
            state = self._conduit_states.get(conduit_id)
            if state is None:
                return
            if self._is_risky(validity):
                state.risky_structural.add(lineage_id)
            else:
                state.risky_structural.discard(lineage_id)

    def _update_resolution_risk(
            self,
            conduit_id: str,
            lineage_key: str,
            validity: Optional[SpellValidity],
    ) -> None:
        with self._lock:
            state = self._conduit_states.get(conduit_id)
            if state is None:
                return
            if self._is_risky(validity):
                state.risky_resolution.add(lineage_key)
            else:
                state.risky_resolution.discard(lineage_key)

    def _refresh_spellbook_flag(self, conduit_id: str) -> None:
        with self._lock:
            state = self._conduit_states.get(conduit_id)
            if state is None or state.spellbook is None:
                return
            required = bool(state.risky_structural or state.risky_resolution)
            spellbook = state.spellbook
        try:
            spellbook._set_spellbook_validation_required(required)
        except Exception:
            pass

    @staticmethod
    def _is_risky(validity: Optional[SpellValidity]) -> bool:
        if validity is None:
            return True
        return validity is not SpellValidity.valid
