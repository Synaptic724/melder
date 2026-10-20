"""Apply the RiskManager distillation change (patch meld_state_gate_2026_10_15; melder_1's file).

usage: python apply_risk_manager.py <tree root> [--check]
Edits src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py by exact text and method rewrites;
refuses when any anchor is missing or repeated.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from apply_lib import apply  # the helper beside this script

ROOT = pathlib.Path(sys.argv[1])
CHECK = "--check" in sys.argv[2:]
REL = "src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py"

REGISTER_CONDUIT = '''    def register_conduit(self, conduit_id: str, spellbook: Spellbook) -> None:
        """
        Register a conduit with its Spellbook and initialize risk state.

        Contract:
        - Replaces any existing conduit risk state.
        - Seeds the conduit bucket from every spell currently visible through
          the spellbook, including contracted visibility.
        - Refreshes the spellbook validation-required flag once, after seeding
          (`_register_spell_risk` per spell, no refresh per spell), so the
          spellbook immediately reflects current conduit risk and a conjure
          does not distil the flag once per visible spell.

        Args:
            conduit_id: Conduit identifier to track.
            spellbook: Spellbook whose spells should be registered.
        Raises:
            RuntimeError: If this RiskManager has been cleaned.

        Returns:
            None.
        """
        if not conduit_id or spellbook is None:
            return
        self.unregister_conduit(conduit_id)
        with self._lock:
            state = _ConduitRiskState(spellbook)
            self._conduit_states[conduit_id] = state

        # Register all known spells so initial risk is accurate, then refresh
        # once: nobody can meld through this conduit before conjure returns it.
        for spell in self._iter_spellbook_spells(spellbook):
            self._register_spell_risk(conduit_id, spell)

        self._refresh_spellbook_flag(conduit_id)

'''

REGISTER_SPELL = '''    def register_spell(self, conduit_id: str, spell: Spell) -> None:
        """
        Register a spell into a conduit's risk tracking.

        Contract:
        - Adds the spell lineage to the conduit risk state.
        - Recomputes both structural and resolution risk for the spell based on
          live `SpellSystemStates` data.
        - Clears any stale resolution key for the spell's current version id
          before recomputing conduit-local risk.
        - Refreshes the spellbook validation-required flag after the update;
          the tracking itself is `_register_spell_risk`, and nothing is
          refreshed when it tracked nothing.

        Args:
            conduit_id: Conduit identifier to update.
            spell: Spell instance to register.
        Raises:
            RuntimeError: If this RiskManager has been cleaned.

        Returns:
            None.
        """
        if self._register_spell_risk(conduit_id, spell):
            self._refresh_spellbook_flag(conduit_id)

'''

REGISTER_SPELL_RISK = '''    def _register_spell_risk(self, conduit_id: str, spell: Spell) -> bool:
        """
        Track one spell's lineage in a conduit's risk bucket without refreshing the Book flag.

        The body of `register_spell` before its refresh, shared with
        `register_conduit`, which seeds every visible spell and refreshes once.

        Contract:
            - Adds the lineage to the bucket and to the lineage-to-conduit index,
              drops a stale `spell:<id>` key for the selected version, and
              recomputes the lineage's structural and resolution risk from the
              live registry - what `register_spell` always did.
            - Returns False and changes nothing when the conduit id or the spell
              is missing, the spell has no lineage (cleaned), or the conduit has
              no bucket.

        Args:
            conduit_id: Conduit whose bucket is updated.
            spell: Spell whose lineage is tracked.

        Returns:
            bool: True when the bucket tracked the lineage, so a refresh is due.
        """
        if not conduit_id or spell is None:
            return False

        lineage_id = self._resolve_lineage_id(spell)
        if not lineage_id:
            return False

        with self._lock:
            state = self._conduit_states.get(conduit_id)
            if state is None:
                return False
            if lineage_id not in state.lineages:
                state.lineages.add(lineage_id)
                conduits = self._lineage_conduits.setdefault(lineage_id, set())
                conduits.add(conduit_id)
            try:
                spell_id = spell.spell_index.selected_spell_id
            except Exception:
                spell_id = None
            if spell_id:
                state.risky_resolution.discard(f"spell:{spell_id}")

        self._update_structural_risk(conduit_id, lineage_id, self._get_structural_validity(spell))
        self._update_resolution_risk(conduit_id, lineage_id, self._get_resolution_validity(conduit_id, spell))
        return True

'''

REFRESH = '''    def _refresh_spellbook_flag(self, conduit_id: str) -> None:
        """
        Push the current conduit risk state back onto the owning spellbook.

        The spellbook-facing `validation_required` flag is the outward signal of
        this manager. It is set while the conduit holds a risky key that is not
        excluded - a `spell:<id>` key, or a lineage whose registered state does
        not carry `SpellState.non_resolvable` (`_has_unexcluded_risk`) - and
        cleared otherwise.

        Contract:
            - The risk sets are read, never changed: a flagged lineage stays in
              them, so it counts again the moment a registration clears its flag.
            - The sets are snapshotted under the manager lock; the registry's
              published set of flagged lineages is read outside it, with no lock
              at all: the registry calls this manager under the registry lock, so
              the manager never takes the registry lock.
            - With both sets empty nothing else is read.
            - The Book's setter runs outside every lock; its failure is
              contained, as before.

        Threading:
            Two concurrent refreshes of one conduit can land their writes out of
            order - pre-existing: the value is computed, then written outside the
            lock. The subset test adds no lock and little time to that window.
        """
        with self._lock:
            state = self._conduit_states.get(conduit_id)
            if state is None or state.spellbook is None:
                return
            risky_keys: Optional[Set[str]] = None
            if state.risky_structural or state.risky_resolution:
                risky_keys = state.risky_structural | state.risky_resolution
            spellbook = state.spellbook
        required = risky_keys is not None and self._has_unexcluded_risk(risky_keys)
        try:
            spellbook._set_spellbook_validation_required(required)
        except Exception:
            pass

    def _has_unexcluded_risk(self, risky_keys: Set[str]) -> bool:
        """
        Return whether any risky key still calls for validation.

        A lineage whose registered state carries `SpellState.non_resolvable` is
        excluded: its selected version is a resolvable=False definition, which
        owes no resolution verdict and is refused at every meld door before the
        validation gate, so its risk says nothing about whether a meld may skip
        the gate. A `spell:<id>` key (a verdict not folded onto a lineage) and a
        lineage with no registered state (removed, and not yet dropped by
        `unregister_spell`) are never excluded.

        The registry publishes the flagged lineages as one immutable set
        (`SpellSystemStates.non_resolvable_index_ids`), so the answer is one
        subset test, with no Python work per key however many definitions the
        Book holds.

        Args:
            risky_keys: Snapshot of the conduit's structural and resolution risk
                keys.

        Returns:
            bool: True when some key is not in the published set; False when
            every key is a flagged lineage.

        Raises:
            RuntimeError: If the frame's registry has been cleaned.

        Threading:
            Called without the manager lock; takes no lock. The registry replaces
            the set under its lock before it publishes the event that runs a
            refresh, so a refresh caused by a registration reads the set that
            registration wrote.
        """
        return not risky_keys <= self._spell_system_states.non_resolvable_index_ids

'''

STEPS = [
    ("one",
     "    - any non-`SpellValidity.valid` state is treated as risky\n"
     "    - if either risk set is non-empty, the owning spellbook is marked as\n"
     "      requiring validation\n",
     "    - any non-`SpellValidity.valid` state is treated as risky\n"
     "    - the owning spellbook is marked as requiring validation while either risk\n"
     "      set holds a key that is not excluded; a lineage whose state carries\n"
     "      `SpellState.non_resolvable` (its selected version is a resolvable=False\n"
     "      definition) is excluded, and its risk stays tracked in the sets\n",
     ""),
    ("one",
     "        `SpellSystemStates.unregister_lineage` notifies this manager to FORCE\n"
     "        validation gating - removing a lineage must never leave a stale \"valid\"\n"
     "        verdict behind that meld could still act on.\n",
     "        `SpellSystemStates.unregister_index` notifies this manager to FORCE\n"
     "        validation gating - removing a lineage must never leave a stale \"valid\"\n"
     "        verdict behind that meld could still act on.\n"
     "        The one exclusion is declared, not inferred. A lineage whose selected\n"
     "        version was bound resolvable=False carries `SpellState.non_resolvable`,\n"
     "        written by `SpellSystemStates.register_index`: it owes no resolution\n"
     "        verdict, so its `unknown` never resolves, and every meld door refuses it\n"
     "        before the gate. Counting it held its Book's flag up for good. The\n"
     "        exclusion applies where the sets are distilled, never where they are\n"
     "        filled, so a registration that clears the flag counts the kept risk\n"
     "        again at once.\n",
     ""),
    ("between", "    def register_conduit(self, conduit_id: str, spellbook: Spellbook) -> None:\n",
     "    def unregister_conduit(self, conduit_id: str) -> None:\n", REGISTER_CONDUIT),
    ("between", "    def register_spell(self, conduit_id: str, spell: Spell) -> None:\n",
     "    def unregister_spell(self, conduit_id: str, spell: Spell) -> None:\n", REGISTER_SPELL),
    ("one",
     "    def _iter_spellbook_spells(self, spellbook: Spellbook) -> List[Spell]:\n",
     REGISTER_SPELL_RISK + "    def _iter_spellbook_spells(self, spellbook: Spellbook) -> List[Spell]:\n",
     ""),
    ("between", "    def _refresh_spellbook_flag(self, conduit_id: str) -> None:\n",
     "    @staticmethod\n    def _is_risky(", REFRESH),
]

apply(ROOT, REL, STEPS, CHECK)
