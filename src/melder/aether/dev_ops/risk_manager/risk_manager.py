from threading import RLock
from typing import Dict, Optional, Set, List

from mypy_extensions import mypyc_attr

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.ispell import ISpell
from melder.utilities.interfaces.ispellbook import ISpellbook
from melder.utilities.interfaces.ispellsystemstates import ISpellSystemStates

@mypyc_attr(native_class=True)
class _ConduitRiskState:
    """
    Per-conduit bucket of risk-tracking state.

    The outer `RiskManager` keeps one of these for each registered conduit so it
    can separate:
    - which lineages the conduit currently knows about
    - which of those lineages are structurally risky
    - which are resolution-risky for that specific conduit
    - which spellbook should have its validation-required flag updated
    """
    __slots__ = [
        "spellbook",
        "lineages",
        "risky_structural",
        "risky_resolution",
    ]

    def __init__(self, spellbook: ISpellbook) -> None:
        """
        Initialize one conduit-local risk bucket.

        Args:
            spellbook: Owning Spellbook used to toggle validation-required state.

        Contract:
        - Starts with empty lineage and risk sets.
        - Retains the live spellbook reference so later risk refreshes can push
          validation-required state back onto the conduit owner.
        """
        self.spellbook: ISpellbook = spellbook
        self.lineages: Set[str] = set()
        self.risky_structural: Set[str] = set()
        self.risky_resolution: Set[str] = set()

@mypyc_attr(native_class=True)
class RiskManager(Cleanable):
    """
    DevOps risk tracking for meld validation gating.

    `RiskManager` is the conduit-local risk aggregator that feeds back into the
    spellbook-level "validation required" signal used by Meld-facing runtime
    flows. It does not validate spells itself. Instead, it watches validity
    state changes and folds them into one operational question per conduit:

    "Does this conduit currently own or see any lineage whose state means meld
    should not be trusted without another validation pass?"

    Risk model:
    - structural risk is tracked by lineage id
    - resolution risk is tracked by conduit-local lineage or spell id key
    - any non-`SpellValidity.valid` state is treated as risky
    - if either risk set is non-empty, the owning spellbook is marked as
      requiring validation

    Operational role:
    - register conduits and the spells they currently expose
    - react to structural and per-conduit resolution validity changes
    - keep conduit-local risk buckets current
    - push one distilled validation-required flag back onto each spellbook

    Threading:
    - Internal state is guarded by an `RLock`.
    - Callers may invoke methods concurrently across conduits; updates are
      folded into conduit-local buckets under the manager lock.

    Lifecycle:
    - Owned by `DevOpsManager` and cleaned from that ownership boundary.
    - After cleanup, public methods fail through `check_cleaned()`.
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

        Contract:
        - Starts with empty conduit-state and lineage-to-conduit indexes.
        - Treats `spell_system_states` as the source of truth for structural and
          resolution validity lookups.
        - Does not snapshot spell state; all risk evaluation stays live against
          the supplied `SpellSystemStates` registry.
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
        Finalize the RiskManager and drop all tracking state.

        Contract:
        - Idempotent and lock-guarded.
        - Clears conduit and lineage indexes before dropping the
          `SpellSystemStates` reference.
        - Leaves future callers to fail through `check_cleaned()`.
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
            del self._spell_system_states
        del self._lock

    def register_conduit(self, conduit_id: str, spellbook: ISpellbook) -> None:
        """
        Register a conduit with its Spellbook and initialize risk state.

        Contract:
        - Replaces any existing conduit risk state.
        - Seeds the conduit bucket from every spell currently visible through
          the spellbook, including contracted visibility.
        - Refreshes the spellbook validation-required flag after seeding so the
          spellbook immediately reflects current conduit risk.

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
        - Removes the conduit from every lineage-to-conduit reverse index it
          currently participates in.
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
        - Recomputes both structural and resolution risk for the spell based on
          live `SpellSystemStates` data.
        - Clears any stale resolution key for the spell's current version id
          before recomputing conduit-local risk.
        - Refreshes the spellbook validation-required flag after the update.

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
        - Clears both structural and resolution risk markers tied to that
          lineage.
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
        - Applies the same validity transition to every conduit bucket that has
          registered that lineage.
        - Refreshes the spellbook validation-required flag after each conduit
          update.

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
        - Treats resolution risk as conduit-local even when the same lineage is
          visible elsewhere.
        - Prefers lineage id tracking when the current spell id can be folded
          back onto a known lineage; otherwise falls back to a spell-version key.
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
        Collect all spells currently visible through the spellbook.

        The result intentionally includes both locally owned and contracted
        spells so initial conduit risk registration starts from the same visible
        surface that meld can later observe.
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
        Resolve the stable lineage id for a spell, if available.

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
        Resolve a lineage id from a current spell version id.

        This is the reverse lookup used when callers only have a current spell
        id but risk tracking needs to fold the event back onto the owning
        lineage.

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
        Return the spell's current structural validity classification.

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
        Return the spell's current per-conduit resolution validity.

        Structural validity is frame-wide, but resolution validity is conduit-
        local. This helper hides that lookup so the risk model can treat the two
        axes consistently.

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

        spell_id = spell.spell_index.current
        if spell_id is None:
            return SpellValidity.unknown

        return resolution_state.get_spell_validity(spell_id)


    def _update_structural_risk(
            self,
            conduit_id: str,
            lineage_id: str,
            validity: Optional[SpellValidity],
    ) -> None:
        """
        Update the structural-risk set for one conduit/lineage pair.

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
        Update the resolution-risk set for one conduit-local key.

        Resolution risk is tracked separately from structural risk because a
        lineage can be structurally fine but still need conduit-local
        revalidation before meld may proceed.

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
        Push the current conduit risk state back onto the owning spellbook.

        The spellbook-facing `validation_required` flag is the outward signal of
        this manager. If either structural or resolution risk exists for the
        conduit, the flag is set; otherwise it is cleared.
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
        Normalize the "is this validity risky?" decision.

        Args:
            validity: SpellValidity or None.
        Returns:
            bool: True when validity is None or not SpellValidity.valid.
        """
        if validity is None:
            return True
        return validity is not SpellValidity.valid
