from threading import RLock
from typing import Dict, Optional, Set, List

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import ISpell, ISpellbook, ISpellSystemStates


class _ConduitRiskState:
    """
    Internal per-conduit risk snapshot.

    Purpose:
        Store the spellbook handle and sets used to track which lineages
        and spell ids are currently considered risky for a conduit.

    Contract:
        - `spellbook` is a live Spellbook reference for validation flag updates.
        - `lineages` contains lineage ids registered for this conduit.
        - `risky_structural` tracks lineage ids with non-valid structural state.
        - `risky_resolution` tracks spell ids (or lineage keys) with non-valid
          resolution state.
    """
    __slots__ = [
        "spellbook",
        "lineages",
        "risky_structural",
        "risky_resolution",
    ]

    def __init__(self, spellbook: ISpellbook) -> None:
        """
        Initialize a conduit risk bucket.

        Args:
            spellbook: Owning Spellbook used to toggle validation-required state.
        """
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
        revalidation in Meld (unknown/gated/invalid/disabled/cleaned).

    Contract:
        - Structural and resolution risk are tracked independently.
        - Any non-valid validity marks the conduit as requiring validation.
        - Risk is recalculated incrementally per lineage change.

    Threading:
        - Internal state is guarded by an RLock.
        - Callers may invoke methods concurrently across conduits.

    Lifecycle:
        - Owned by DevOpsManager and cleaned during DevOpsManager.cleanup().
        - After cleanup, public methods raise via check_cleaned().
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_spell_system_states",
        "_conduit_states",
        "_lineage_conduits",
    ]

    def __init__(self, spell_system_states: ISpellSystemStates) -> None:
        """
        Initialize the RiskManager.

        Args:
            spell_system_states:
                SpellSystemStates registry used to resolve lineage ids and
                per-conduit resolution validity.
        Raises:
            ValueError: If spell_system_states is None.
        """
        super().__init__()
        if spell_system_states is None:
            raise ValueError("spell_system_states cannot be None")
        self._lock: RLock = RLock()
        self._spell_system_states: ISpellSystemStates = spell_system_states
        self._conduit_states: Dict[str, _ConduitRiskState] = {}
        self._lineage_conduits: Dict[str, Set[str]] = {}

    def cleanup(self) -> None:
        """
        Cleanup the RiskManager and drop all tracking state.

        Contract:
            - Idempotent and lock-guarded.
            - Clears conduit and lineage indexes.
            - Drops the SpellSystemStates reference.
        """
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

        Contract:
            - Replaces any existing conduit risk state.
            - Registers all spells currently visible in the Spellbook.
            - Refreshes the spellbook validation-required flag at the end.

        Args:
            conduit_id: Conduit identifier to track.
            spellbook: Spellbook whose spells should be registered.
        Raises:
            RuntimeError: If this RiskManager has been cleaned.
        """
        self.check_cleaned()
        if not conduit_id or spellbook is None:
            return
        self.unregister_conduit(conduit_id)
        with self._lock:
            state = _ConduitRiskState(spellbook)
            self._conduit_states[conduit_id] = state

        # Register all known spells so initial risk is accurate.
        for spell in self._iter_spellbook_spells(spellbook):
            self.register_spell(conduit_id, spell)

        self._refresh_spellbook_flag(conduit_id)

    def unregister_conduit(self, conduit_id: str) -> None:
        """
        Remove conduit tracking and clear lineage mappings.

        Contract:
            - Removes the conduit risk bucket.
            - Removes conduit membership from all lineage indexes.
            - Does not modify SpellSystemStates.

        Args:
            conduit_id: Conduit identifier to remove.
        Raises:
            RuntimeError: If this RiskManager has been cleaned.
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

        Contract:
            - Adds the spell lineage to the conduit risk state.
            - Updates structural and resolution risk for the spell.
            - Refreshes the spellbook validation-required flag.

        Args:
            conduit_id: Conduit identifier to update.
            spell: Spell instance to register.
        Raises:
            RuntimeError: If this RiskManager has been cleaned.
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

        Contract:
            - Removes the spell lineage from the conduit risk state.
            - Clears risk markers for this lineage.
            - Refreshes the spellbook validation-required flag.

        Args:
            conduit_id: Conduit identifier to update.
            spell: Spell instance to unregister.
        Raises:
            RuntimeError: If this RiskManager has been cleaned.
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

        Contract:
            - Updates all conduits currently referencing the lineage.
            - Refreshes validation-required flags per conduit.

        Args:
            lineage_id: Lineage identifier whose structural validity changed.
            validity: New structural validity (None treated as risky).
        Raises:
            RuntimeError: If this RiskManager has been cleaned.
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

        Contract:
            - Tracks risk for a spell id within the conduit.
            - Refreshes the conduit spellbook validation-required flag.

        Args:
            conduit_id: Conduit identifier whose resolution validity changed.
            spell_id: Versioned spell id for the resolution update.
            validity: New resolution validity (None treated as risky).
        Raises:
            RuntimeError: If this RiskManager has been cleaned.
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
        """
        Internal

        Collect all spells visible to a Spellbook.

        Contract:
            - Returns local and contracted spells when available.
            - Returns an empty list if maps are unavailable.

        Notes:
            A list is built to avoid iteration hazards if Spellbook maps
            are mutated during registration.
        """
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
        """
        Internal

        Resolve a lineage id for a spell, if present.

        Args:
            spell: Spell instance to inspect.
        Returns:
            Optional[str]: Lineage id or None if unavailable.
        """
        if spell._cleaned:
            return None
        else:
            return spell.spell_index.id
    def _resolve_lineage_id_from_spell_id(self, spell_id: str) -> Optional[str]:
        """
        Internal

        Resolve a lineage id using a spell version id.

        Args:
            spell_id: Versioned spell id.
        Returns:
            Optional[str]: Lineage id or None if unavailable.
        """
        states = self._spell_system_states
        state = states.get_by_spell_id(spell_id)
        if state is None:
            return None
        return state.spell_index_id

    def _get_structural_validity(self, spell: ISpell) -> Optional[SpellValidity]:
        """
        Internal

        Retrieve structural validity for a spell.

        Args:
            spell: Spell instance to inspect.
        Returns:
            Optional[SpellValidity]:
                Structural validity when available, SpellValidity.cleaned when the
                spell is cleaned, or SpellValidity.unknown when no lineage state
                is available.
        """
        if spell._cleaned:
            return SpellValidity.cleaned
        state = spell.system_state
        if state is None:
            return SpellValidity.unknown
        return state.validity

    def _get_resolution_validity(self, conduit_id: str, spell: ISpell) -> Optional[SpellValidity]:
        """
        Internal

        Retrieve per-conduit resolution validity for a spell.

        Args:
            conduit_id: Conduit identifier for resolution state lookup.
            spell: Spell instance to inspect.
        Returns:
            Optional[SpellValidity]: Resolution validity or unknown when unavailable.
        """
        resolution_state = self._spell_system_states.get_conduit_resolution_state(conduit_id)

        if resolution_state is None:
            return SpellValidity.unknown
        if spell._cleaned:
            return SpellValidity.unknown

        return resolution_state.get_spell_validity(spell.spell_index.current)


    def _update_structural_risk(
            self,
            conduit_id: str,
            lineage_id: str,
            validity: Optional[SpellValidity],
    ) -> None:
        """
        Internal

        Update structural risk tracking for a lineage within a conduit.

        Args:
            conduit_id: Conduit identifier to update.
            lineage_id: Lineage identifier to mark risky or safe.
            validity: Structural validity (None treated as risky).
        """
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
        """
        Internal

        Update resolution risk tracking for a lineage or spell id within a conduit.

        Args:
            conduit_id: Conduit identifier to update.
            lineage_key: Lineage id or spell id key for tracking.
            validity: Resolution validity (None treated as risky).
        """
        with self._lock:
            state = self._conduit_states.get(conduit_id)
            if state is None:
                return
            if self._is_risky(validity):
                state.risky_resolution.add(lineage_key)
            else:
                state.risky_resolution.discard(lineage_key)

    def _refresh_spellbook_flag(self, conduit_id: str) -> None:
        """
        Internal

        Update the Spellbook validation-required flag for a conduit.

        Contract:
            - Required is True when any structural or resolution risk exists.
            - Safe to call even if the spellbook has been cleaned.
        """
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
        """
        Internal

        Normalize risk checks for validity enums.

        Args:
            validity: SpellValidity or None.
        Returns:
            bool: True when validity is None or not SpellValidity.valid.
        """
        if validity is None:
            return True
        return validity is not SpellValidity.valid
