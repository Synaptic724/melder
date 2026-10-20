"""Apply the SpellState.non_resolvable state-model change (patch meld_state_gate_2026_10_15; melder_1's files).

usage: python apply_state_model.py <tree root> [--check]
Edits src/melder/aether/aetheric_frame/dev_ops/spell_system_states/{spell_state,spell_system_state,spell_system_states}.py
by exact text; refuses when any anchor is missing or repeated.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from apply_lib import apply  # the helper beside this script

ROOT = pathlib.Path(sys.argv[1])
CHECK = "--check" in sys.argv[2:]
PKG = "src/melder/aether/aetheric_frame/dev_ops/spell_system_states/"

SPELL_STATE = [
    ("one",
     "    - Flag lifecycle is owned by the subsystem that set the flag. Validation\n"
     "      clears only topology-driven dirt flags; contract, mutation, and ops flags\n"
     "      must be flipped by their own control-plane logic.\n",
     "    - Flag lifecycle is owned by the subsystem that set the flag. Validation\n"
     "      clears only topology-driven dirt flags; contract, mutation, and ops flags\n"
     "      must be flipped by their own control-plane logic.\n"
     "    - `non_resolvable` is the capability flag. `SpellSystemStates.register_index`\n"
     "      sets it when the lineage's selected version was bound resolvable=False and\n"
     "      clears it when a resolvable version (or, with no stated capability, another\n"
     "      version) is selected. Validation never clears it and it changes no\n"
     "      validity; its one reader is RiskManager, which leaves a flagged lineage's\n"
     "      risk out of the Book's validation flag.\n",
     ""),
    ("one",
     "        notch/bind_inactive seams are real. They are vocabulary awaiting a\n"
     "        producer, not dead values.\n",
     "        notch/bind_inactive seams are real. They are vocabulary awaiting a\n"
     "        producer, not dead values.\n"
     "        `non_resolvable` exists because `unknown` means \"work still owed\", and a\n"
     "        resolvable=False definition - an abstract base, a Protocol, a helper\n"
     "        kept so agents can discover, inspect and version it, whose consumers\n"
     "        receive the value by override - owes no resolution verdict at all.\n"
     "        Every meld door refuses such a version before the validation gate, so\n"
     "        its never-filled verdict says nothing about whether a meld may skip the\n"
     "        gate; counted as risk, it kept its Book's validation flag up for the\n"
     "        Book's life. The flag records the declaration on this explanation axis\n"
     "        and leaves the validity axis truthful.\n",
     ""),
    ("one",
     "    transfer_in_progress = auto()    # ownership transfer is actively blocking resolution\n",
     "    transfer_in_progress = auto()    # ownership transfer is actively blocking resolution\n"
     "\n"
     "    # Capability (registration)\n"
     "    non_resolvable = auto()          # selected version bound resolvable=False; owes no resolution verdict\n",
     ""),
]

HAS_FLAG = '''
    def has_flag(self, flag: SpellState) -> bool:
        """
        Return whether this index currently carries one SpellState flag.

        Purpose:
            A membership probe without the copy `flags` makes, for readers that
            ask about one flag: `SpellSystemStates.index_has_flag` answers
            through it, and `SpellSystemStates.register_index` reads
            `SpellState.non_resolvable` through it to keep the registry's
            published set of flagged lineages (`non_resolvable_index_ids`) in
            step with this state.

        Args:
            flag: The SpellState member to look for.

        Returns:
            bool: True when the flag is present.

        Raises:
            RuntimeError: If this state has been cleaned (`check_cleaned`).

        Threading:
            Reads under the state lock, so a concurrent `update_flags` or
            `set_validity` is seen whole.
        """
        self.check_cleaned()
        with self._lock:
            self.check_cleaned()
            return flag in self._flags
'''

UPDATE_FLAGS = '''
    def update_flags(
            self,
            *,
            flags_to_add: Optional[Iterable[SpellState]] = None,
            flags_to_remove: Optional[Iterable[SpellState]] = None,
    ) -> bool:
        """
        Add and remove SpellState flags without touching the validity axis.

        Purpose:
            The flag-only write, for a flag whose owner decides it outside any
            validity transition: `SpellSystemStates.register_index` records the
            selected version's capability (`SpellState.non_resolvable`) through
            it before it gates the index.

        Args:
            flags_to_add: Flags to add; None entries are ignored.
            flags_to_remove: Flags to remove; None entries are ignored.

        Contract:
            - Adds first, then removes - the order `set_validity` uses - so a flag
              named in both ends absent.
            - Leaves validity, the change reason, `transitively_dirty` and
              `last_validated_at` unchanged.
            - Publishes nothing: flag-only updates stay local, as in
              `set_validity`. A caller whose flag RiskManager reads publishes
              through `_republish_validity` when no validity change will.
            - Idempotent: adding a present flag or removing an absent one changes
              nothing and returns False.

        Returns:
            bool: True when the flag set changed.

        Raises:
            RuntimeError: If this state has been cleaned (`check_cleaned`).

        Threading:
            Mutates under the state lock. The owning registry calls it under its
            own lock, so the order is registry -> state, the registry's only one.
        """
        self.check_cleaned()
        with self._lock:
            self.check_cleaned()
            before = frozenset(self._flags)
            if flags_to_add is not None:
                for flag in flags_to_add:
                    if flag is not None:
                        self._flags.add(flag)
            if flags_to_remove is not None:
                for flag in flags_to_remove:
                    if flag is not None:
                        self._flags.discard(flag)
            return self._flags != before

    def _republish_validity(self) -> None:
        """
        Publish the current structural validity to the attached RiskManager again.

        Purpose:
            `set_validity` publishes only a changed validity. When the owning
            registry changes a flag that RiskManager reads
            (`SpellState.non_resolvable`) while this index is already `gated`,
            the gate publishes nothing, and the conduits holding the lineage would
            keep a Book flag distilled from the old flag - a borrower whose copy
            came back by reactivation is never re-registered with RiskManager.
            The registry calls this so every conduit holding the lineage
            refreshes.

        Contract:
            - Reads the validity and the index id under the state lock and
              publishes outside it, as `set_validity` does.
            - Changes nothing on this state; with no RiskManager attached it does
              nothing.
            - A failing callback is contained exactly as `set_validity` contains
              it: this publication stands in for the event `set_validity` would
              have sent, and the registration that called it has completed.

        Returns:
            None.

        Raises:
            RuntimeError: If this state has been cleaned (`check_cleaned`).
        """
        self.check_cleaned()
        with self._lock:
            self.check_cleaned()
            risk_manager = self._risk_manager
            validity = self._validity
            index_id = self._spell_index_id
        if risk_manager is None:
            return
        try:
            risk_manager.on_structural_validity_change(index_id, validity)
        except Exception:
            pass
'''

SPELL_SYSTEM_STATE = [
    ("one",
     "        - `transitively_dirty` marks indirect impact via the\n"
     "          `dependency_changed` closure rather than a direct edit.\n",
     "        - `transitively_dirty` marks indirect impact via the\n"
     "          `dependency_changed` closure rather than a direct edit.\n"
     "        - `SpellState.non_resolvable` is written only through `update_flags`,\n"
     "          by the owning registry's `register_index`, which mirrors it in the\n"
     "          registry's published `non_resolvable_index_ids`; it changes no\n"
     "          validity and `clear_dirty` keeps it.\n",
     ""),
    ("one",
     "            if self._flags is None:\n"
     "                return set()\n"
     "            return set(self._flags)\n"
     "\n"
     "    @property\n"
     "    def change_reason(self) -> Optional[SpellStateChangeReason]:\n",
     "            if self._flags is None:\n"
     "                return set()\n"
     "            return set(self._flags)\n"
     + HAS_FLAG +
     "\n"
     "    @property\n"
     "    def change_reason(self) -> Optional[SpellStateChangeReason]:\n",
     ""),
    ("one",
     "            try:\n"
     "                callback(index_id, validity)\n"
     "            except Exception:\n"
     "                pass\n"
     "\n"
     "    # ------------------------------------------------------------------\n"
     "    # Mutation helpers (used by manager / DevOps layer)\n",
     "            try:\n"
     "                callback(index_id, validity)\n"
     "            except Exception:\n"
     "                pass\n"
     + UPDATE_FLAGS +
     "\n"
     "    # ------------------------------------------------------------------\n"
     "    # Mutation helpers (used by manager / DevOps layer)\n",
     ""),
]

REGISTER_DOC_TAIL = '''          conduit before it is built there. A first-time id has no verdict and
          nothing happens.
        - Record the selected version's resolution capability as the
          `SpellState.non_resolvable` flag (`_record_selected_capability`)
          before the index is gated, so the RiskManager callback that the gate
          publishes already sees it: `resolvable=False` sets the flag,
          `resolvable=True` clears it, and None keeps it only while the index
          still selects the version the state tracked - a new state, or another
          selection with no stated capability, clears it, so an exclusion
          recorded for one version never covers another.
        - When that write changed the flag and the index was already `gated`,
          the gate publishes nothing (`set_validity` publishes only a changed
          validity), so publish the current validity again
          (`SpellSystemState._republish_validity`): every conduit holding the
          lineage refreshes its Book flag with the new flag - a borrower whose
          copy came back by reactivation is never re-registered with RiskManager.
        - Keep the published set of flagged lineages in step with the flag
          (`_publish_non_resolvable_membership_locked`), also before the gate
          publishes, so the refresh that event runs reads the new set.

        This is intended to be called from Spellbook.bind(...) or equivalent.

        Args:
            spell_index:
                The index whose selected version is (re)registered.
            owner_spellbook_id:
                The owning Spellbook's id, recorded for the spellbook-scoped
                collection and contract indices; None leaves the recorded owner
                as it is.
            resolvable:
                The selected version's `Spell.resolvable`, or None when the
                caller does not state it (a registration that keeps the
                selection, such as the ownership transfer's disable step).

        Returns:
            SpellSystemState:
                The lineage's live state.

        Raises:
            TypeError:
                If `resolvable` is neither None nor a bool; nothing is
                registered.
            RuntimeError:
                If the index selects no version.

        Threading:
            Runs under the registry lock. The capability write and the gate take
            the state's lock inside it (registry -> state), and the RiskManager
            callbacks run inside the registry lock, outside the state lock.
        """
        if resolvable is not None and type(resolvable) is not bool:
            raise TypeError(
                "register_index(resolvable=...) takes the selected version's Spell.resolvable (a bool) or None; "
                f"got {type(resolvable).__name__}. Pass spell.resolvable for the version the index selects."
            )
        index_id = spell_index.id
'''

RECORD_CAPABILITY = '''
    @staticmethod
    def _record_selected_capability(
            state: SpellSystemState,
            resolvable: Optional[bool],
            selection_kept: bool,
    ) -> bool:
        """
        Write the selected version's capability as `SpellState.non_resolvable`; caller holds `_lock`.

        Contract:
            - False adds the flag; True removes it.
            - None keeps the flag only when `selection_kept` (the state already
              tracked this version): a new state or another selection removes it,
              so an exclusion recorded for one version never covers another.
            - Flag-only (`SpellSystemState.update_flags`); publishes nothing.

        Args:
            state:
                The lineage's live state.
            resolvable:
                The selected version's `Spell.resolvable`, or None.
            selection_kept:
                Whether the state already tracked the selected version.

        Returns:
            bool:
                True when the flag changed.
        """
        if resolvable is False:
            return state.update_flags(flags_to_add=(SpellState.non_resolvable,))
        if resolvable is True or not selection_kept:
            return state.update_flags(flags_to_remove=(SpellState.non_resolvable,))
        return False

    def _publish_non_resolvable_membership_locked(self, index_id: str, member: bool) -> None:
        """
        Put `index_id` in or out of the published set of flagged lineages; caller holds `_lock`.

        Contract:
            - `member` is whether the lineage's state carries
              `SpellState.non_resolvable` now; the set follows it.
            - The set is replaced, never mutated, so a reader keeps a consistent
              snapshot; nothing is replaced when the membership already matches.

        Args:
            index_id:
                Spell-index id (the lineage id).
            member:
                Whether the lineage belongs in the set.

        Returns:
            None.
        """
        published = self._non_resolvable_index_ids
        if (index_id in published) == member:
            return
        self._non_resolvable_index_ids = (published | {index_id}) if member else (published - {index_id})
'''

INDEX_HAS_FLAG = '''
    def index_has_flag(self, index_id: str, flag: SpellState) -> bool:
        """
        Return whether the lineage registered under `index_id` carries `flag`.

        Purpose:
            The per-lineage flag read. It reads the registry rather than a held
            state reference, so a lineage removed meanwhile answers False.
            RiskManager does not probe per key: for `SpellState.non_resolvable` it
            reads the set this registry publishes (`non_resolvable_index_ids`).

        Contract:
            - False for an empty id or an id with no registered state.
            - Otherwise the state's `has_flag(flag)`, read under the registry
              lock. A state leaves the registry before it is cleaned
              (`unregister_index` pops it first; `cleanup` cleans under this
              lock), so the state read here is live.

        Args:
            index_id:
                Spell-index id (the lineage id).
            flag:
                The SpellState member to look for.

        Returns:
            bool:
                True when the registered state carries the flag.

        Raises:
            RuntimeError:
                If the registry has been cleaned (`check_cleaned`).

        Threading:
            Registry lock, then the state's lock - the registry's only order. The
            registry lock is reentrant, so a caller already holding it may call
            this.
        """
        self.check_cleaned()
        if not index_id:
            return False
        with self._lock:
            self.check_cleaned()
            state = self._states_by_index_id.get(index_id)
            if state is None:
                return False
            return state.has_flag(flag)

    @property
    def non_resolvable_index_ids(self) -> FrozenSet[str]:
        """
        Return the lineages whose state carries `SpellState.non_resolvable`.

        Purpose:
            RiskManager's exclusion set: a risky key in it is left out of its
            Book's validation flag, with one subset test per refresh instead of a
            registry probe per key.

        Contract:
            - Exactly the registered lineages whose state carries the flag:
              `register_index` puts a lineage in or out right after it writes the
              flag and before its gate publishes, and `unregister_index` takes it
              out, so a removed lineage is never in it.
            - The set is replaced whole, never mutated; the caller may keep the
              returned set as a snapshot.

        Returns:
            FrozenSet[str]:
                The published set; empty when nothing is flagged.

        Raises:
            RuntimeError:
                If the registry has been cleaned (`check_cleaned`).

        Threading:
            Lock-free, one reference read. A read racing a registration sees the
            set from before or after it, and the RiskManager refresh that the
            registration publishes reads the new one. A read racing cleanup finds
            the empty tombstone set, never a missing attribute.
        """
        self.check_cleaned()
        return self._non_resolvable_index_ids
'''

SPELL_SYSTEM_STATES = [
    ("one",
     "from typing import TYPE_CHECKING, Callable, Dict, Iterable, Iterator, List, Mapping, Optional, Sequence, Set, "
     "Tuple, \\\n"
     "    ClassVar\n",
     "from typing import TYPE_CHECKING, Callable, Dict, Iterable, Iterator, List, Mapping, Optional, Sequence, Set, "
     "Tuple, \\\n"
     "    ClassVar, FrozenSet\n",
     ""),
    ("one",
     "        dependency indices, per-Spellbook SpellContract consumer indices, and\n"
     "        per-conduit `ConduitResolutionState` keyed by conduit_id.\n",
     "        dependency indices, per-Spellbook SpellContract consumer indices,\n"
     "        per-conduit `ConduitResolutionState` keyed by conduit_id, and the\n"
     "        published set of lineages flagged `SpellState.non_resolvable`.\n",
     ""),
    ("one",
     "        consumption is drain-shaped rather than read-only: taking a worklist\n"
     "        clears it.\n",
     "        consumption is drain-shaped rather than read-only: taking a worklist\n"
     "        clears it. `non_resolvable_index_ids` is replaced whole under the lock\n"
     "        and read without it.\n",
     ""),
    ("one",
     "        \"_risk_manager\",\n"
     "    ]\n",
     "        \"_risk_manager\",\n"
     "        \"_non_resolvable_index_ids\",\n"
     "    ]\n",
     ""),
    ("one",
     "        self._risk_manager: Optional[RiskManager] = None\n",
     "        self._risk_manager: Optional[RiskManager] = None\n"
     "        # The lineages whose state carries SpellState.non_resolvable, replaced\n"
     "        # whole under `_lock` (`_publish_non_resolvable_membership_locked`) and\n"
     "        # read without it (`non_resolvable_index_ids`), so it is never mutated.\n"
     "        self._non_resolvable_index_ids: FrozenSet[str] = frozenset()\n",
     ""),
    ("one",
     "            del self._index_owner_spellbook_id\n",
     "            del self._index_owner_spellbook_id\n"
     "            # A tombstone, not a delete: `non_resolvable_index_ids` is read without\n"
     "            # the lock, so a read racing this cleanup must still find a set.\n"
     "            self._non_resolvable_index_ids = frozenset()\n",
     ""),
    ("one",
     "        - Remove the spell index from `_dirty_indexes`.\n",
     "        - Remove the spell index from `_dirty_indexes`.\n"
     "        - Take the lineage out of the published set of flagged lineages.\n",
     ""),
    ("one",
     "            current_spell_id = removed_state.current_spell_id\n",
     "            current_spell_id = removed_state.current_spell_id\n"
     "            # A removed lineage is never in the published flagged set.\n"
     "            self._publish_non_resolvable_membership_locked(index_id, False)\n",
     ""),
    ("one",
     "    - Spellbook / SpellCrafter call:\n"
     "        * `register_index(...)` when a new SpellIndex+Spell appears\n",
     "    - Spellbook / SpellCrafter call:\n"
     "        * `register_index(..., resolvable=...)` when a new SpellIndex+Spell\n"
     "          appears or an index selects another version (bind, notch, an\n"
     "          ownership transfer), passing the selected version's `Spell.resolvable`\n",
     ""),
    ("one",
     "        send the first meld of the replacement straight to the context builder\n"
     "        with no plan to build from (the rebind-after-first-meld defect).\n",
     "        send the first meld of the replacement straight to the context builder\n"
     "        with no plan to build from (the rebind-after-first-meld defect).\n"
     "        Registering an index also records the selected version's resolution\n"
     "        capability as `SpellState.non_resolvable` and publishes the flagged\n"
     "        lineages as one immutable set (`non_resolvable_index_ids`), which\n"
     "        RiskManager reads without a lock to leave a declared non-resolvable\n"
     "        definition out of its Book's validation flag.\n",
     ""),
    ("one",
     "    def register_index(self, spell_index: SpellIndex, owner_spellbook_id: Optional[str] = None) -> SpellSystemState:\n",
     "    def register_index(\n"
     "            self,\n"
     "            spell_index: SpellIndex,\n"
     "            owner_spellbook_id: Optional[str] = None,\n"
     "            *,\n"
     "            resolvable: Optional[bool] = None,\n"
     "    ) -> SpellSystemState:\n",
     ""),
    ("one",
     "          conduit before it is built there. A first-time id has no verdict and\n"
     "          nothing happens.\n"
     "\n"
     "        This is intended to be called from Spellbook.bind(...) or equivalent.\n"
     "        \"\"\"\n"
     "        index_id = spell_index.id\n",
     REGISTER_DOC_TAIL,
     ""),
    ("one",
     "                self._states_by_index_id[index_id] = state\n"
     "            else:\n"
     "                # Keep current version id in sync\n"
     "                state.update_current_spell_id(current_id)\n",
     "                self._states_by_index_id[index_id] = state\n"
     "                selection_kept = False\n"
     "            else:\n"
     "                # Whether the state already tracked this version decides what a\n"
     "                # registration with no stated capability does to the flag.\n"
     "                selection_kept = state.current_spell_id == current_id\n"
     "                # Keep current version id in sync\n"
     "                state.update_current_spell_id(current_id)\n",
     ""),
    ("one",
     "            # Any (re)binding is treated as structural change.\n"
     "            state.mark_structural_change(change_reason=SpellStateChangeReason.register_or_rebind)\n"
     "            self._dirty_indexes.add(index_id)\n"
     "\n"
     "            return state\n",
     "            # The selected version's capability, written before the gate below\n"
     "            # publishes, so the RiskManager callback it runs already sees it.\n"
     "            flag_changed = self._record_selected_capability(state, resolvable, selection_kept)\n"
     "            self._publish_non_resolvable_membership_locked(\n"
     "                index_id, state.has_flag(SpellState.non_resolvable)\n"
     "            )\n"
     "            gate_was_closed = state.validity is SpellValidity.gated\n"
     "\n"
     "            # Any (re)binding is treated as structural change.\n"
     "            state.mark_structural_change(change_reason=SpellStateChangeReason.register_or_rebind)\n"
     "            self._dirty_indexes.add(index_id)\n"
     "\n"
     "            if flag_changed and gate_was_closed:\n"
     "                # Already gated, so the gate published nothing: tell the conduits\n"
     "                # holding this lineage about the changed flag here.\n"
     "                state._republish_validity()\n"
     "\n"
     "            return state\n"
     + RECORD_CAPABILITY,
     ""),
    ("one",
     "            if self._states_by_spell_id is None:\n"
     "                return None\n"
     "            return self._states_by_spell_id.get(spell_id)\n"
     "\n"
     "    # ------------------------------------------------------------------\n"
     "    # Internal indexing helpers\n",
     "            if self._states_by_spell_id is None:\n"
     "                return None\n"
     "            return self._states_by_spell_id.get(spell_id)\n"
     + INDEX_HAS_FLAG +
     "\n"
     "    # ------------------------------------------------------------------\n"
     "    # Internal indexing helpers\n",
     ""),
]

apply(ROOT, PKG + "spell_state.py", SPELL_STATE, CHECK)
apply(ROOT, PKG + "spell_system_state.py", SPELL_SYSTEM_STATE, CHECK)
apply(ROOT, PKG + "spell_system_states.py", SPELL_SYSTEM_STATES, CHECK)
