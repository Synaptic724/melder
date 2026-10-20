"""Fold the published flagged-lineage set into the lane's apply scripts (melder_1, 2026-10-15).

The DECISION Note of 2026-10-15T22:12:54Z: SpellSystemStates publishes the lineages flagged
SpellState.non_resolvable as one frozenset and RiskManager's exclusion becomes one subset test. This script edits
apply_state_model.py and apply_risk_manager.py by exact text (each anchor must occur once); the scripts then
regenerate the four melder_1 files from pristine copies.
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent


def one(text: str, old: str, new: str, where: str) -> str:
    """Replace exactly one occurrence of `old`."""
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{where}: expected one occurrence, found {count}: {old[:90]!r}")
    return text.replace(old, new, 1)


STATE_MODEL_EDITS = [
    # has_flag: who reads it now.
    ('''            A membership probe without the copy `flags` makes, for readers that
            ask about one flag: RiskManager asks about `SpellState.non_resolvable`
            (through `SpellSystemStates.index_has_flag`) each time it distils a
            Book's validation flag.
''',
     '''            A membership probe without the copy `flags` makes, for readers that
            ask about one flag: `SpellSystemStates.index_has_flag` answers
            through it, and `SpellSystemStates.register_index` reads
            `SpellState.non_resolvable` through it to keep the registry's
            published set of flagged lineages (`non_resolvable_index_ids`) in
            step with this state.
'''),
    # SpellSystemState class docstring bullet.
    ('''     "        - `SpellState.non_resolvable` is written only through `update_flags`,\\n"
     "          by the owning registry's `register_index`; it changes no validity and\\n"
     "          `clear_dirty` keeps it.\\n",
''',
     '''     "        - `SpellState.non_resolvable` is written only through `update_flags`,\\n"
     "          by the owning registry's `register_index`, which mirrors it in the\\n"
     "          registry's published `non_resolvable_index_ids`; it changes no\\n"
     "          validity and `clear_dirty` keeps it.\\n",
'''),
    # register_index docstring: the new bullet after the re-publication bullet.
    ('''          lineage refreshes its Book flag with the new flag - a borrower whose
          copy came back by reactivation is never re-registered with RiskManager.

        This is intended to be called from Spellbook.bind(...) or equivalent.
''',
     '''          lineage refreshes its Book flag with the new flag - a borrower whose
          copy came back by reactivation is never re-registered with RiskManager.
        - Keep the published set of flagged lineages in step with the flag
          (`_publish_non_resolvable_membership_locked`), also before the gate
          publishes, so the refresh that event runs reads the new set.

        This is intended to be called from Spellbook.bind(...) or equivalent.
'''),
    # The membership helper after _record_selected_capability.
    ('''        if resolvable is True or not selection_kept:
            return state.update_flags(flags_to_remove=(SpellState.non_resolvable,))
        return False
\'\'\'
''',
     '''        if resolvable is True or not selection_kept:
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
\'\'\'
'''),
    # index_has_flag: purpose and threading, and the published-set property after it.
    ('''        Purpose:
            RiskManager's probe for `SpellState.non_resolvable` when it distils a
            Book's validation flag. It reads the registry rather than a held state
            reference, so a lineage removed meanwhile answers False.
''',
     '''        Purpose:
            The per-lineage flag read. It reads the registry rather than a held
            state reference, so a lineage removed meanwhile answers False.
            RiskManager does not probe per key: for `SpellState.non_resolvable` it
            reads the set this registry publishes (`non_resolvable_index_ids`).
'''),
    ('''        Threading:
            Registry lock, then the state's lock - the registry's only order. It
            is called from RiskManager callbacks that run under the registry lock;
            the lock is reentrant.
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
\'\'\'
''',
     '''        Threading:
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
\'\'\'
'''),
    # The class docstring sentence on the reader.
    ('''     "        capability as `SpellState.non_resolvable`, which RiskManager reads\\n"
     "        through `index_has_flag` to leave a declared non-resolvable definition\\n"
     "        out of its Book's validation flag.\\n",
''',
     '''     "        capability as `SpellState.non_resolvable` and publishes the flagged\\n"
     "        lineages as one immutable set (`non_resolvable_index_ids`), which\\n"
     "        RiskManager reads without a lock to leave a declared non-resolvable\\n"
     "        definition out of its Book's validation flag.\\n",
'''),
    # register_index body: reconcile the membership right after the flag write.
    ('''     "            flag_changed = self._record_selected_capability(state, resolvable, selection_kept)\\n"
     "            gate_was_closed = state.validity is SpellValidity.gated\\n"
''',
     '''     "            flag_changed = self._record_selected_capability(state, resolvable, selection_kept)\\n"
     "            self._publish_non_resolvable_membership_locked(\\n"
     "                index_id, state.has_flag(SpellState.non_resolvable)\\n"
     "            )\\n"
     "            gate_was_closed = state.validity is SpellValidity.gated\\n"
'''),
]

NEW_STATES_STEPS = '''    ("one",
     "from typing import TYPE_CHECKING, Callable, Dict, Iterable, Iterator, List, Mapping, Optional, Sequence, Set, "
     "Tuple, \\\\\\n"
     "    ClassVar\\n",
     "from typing import TYPE_CHECKING, Callable, Dict, Iterable, Iterator, List, Mapping, Optional, Sequence, Set, "
     "Tuple, \\\\\\n"
     "    ClassVar, FrozenSet\\n",
     ""),
    ("one",
     "        dependency indices, per-Spellbook SpellContract consumer indices, and\\n"
     "        per-conduit `ConduitResolutionState` keyed by conduit_id.\\n",
     "        dependency indices, per-Spellbook SpellContract consumer indices,\\n"
     "        per-conduit `ConduitResolutionState` keyed by conduit_id, and the\\n"
     "        published set of lineages flagged `SpellState.non_resolvable`.\\n",
     ""),
    ("one",
     "        consumption is drain-shaped rather than read-only: taking a worklist\\n"
     "        clears it.\\n",
     "        consumption is drain-shaped rather than read-only: taking a worklist\\n"
     "        clears it. `non_resolvable_index_ids` is replaced whole under the lock\\n"
     "        and read without it.\\n",
     ""),
    ("one",
     "        \\"_risk_manager\\",\\n"
     "    ]\\n",
     "        \\"_risk_manager\\",\\n"
     "        \\"_non_resolvable_index_ids\\",\\n"
     "    ]\\n",
     ""),
    ("one",
     "        self._risk_manager: Optional[RiskManager] = None\\n",
     "        self._risk_manager: Optional[RiskManager] = None\\n"
     "        # The lineages whose state carries SpellState.non_resolvable, replaced\\n"
     "        # whole under `_lock` (`_publish_non_resolvable_membership_locked`) and\\n"
     "        # read without it (`non_resolvable_index_ids`), so it is never mutated.\\n"
     "        self._non_resolvable_index_ids: FrozenSet[str] = frozenset()\\n",
     ""),
    ("one",
     "            del self._index_owner_spellbook_id\\n",
     "            del self._index_owner_spellbook_id\\n"
     "            # A tombstone, not a delete: `non_resolvable_index_ids` is read without\\n"
     "            # the lock, so a read racing this cleanup must still find a set.\\n"
     "            self._non_resolvable_index_ids = frozenset()\\n",
     ""),
    ("one",
     "        - Remove the spell index from `_dirty_indexes`.\\n",
     "        - Remove the spell index from `_dirty_indexes`.\\n"
     "        - Take the lineage out of the published set of flagged lineages.\\n",
     ""),
    ("one",
     "            current_spell_id = removed_state.current_spell_id\\n",
     "            current_spell_id = removed_state.current_spell_id\\n"
     "            # A removed lineage is never in the published flagged set.\\n"
     "            self._publish_non_resolvable_membership_locked(index_id, False)\\n",
     ""),
'''

RISK_EDITS = [
    # Drop the SpellState import step: RiskManager no longer names the member in code.
    ('''    ("one",
     "from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity\\n",
     "from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state import SpellState\\n"
     "from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity\\n",
     ""),
''', ''),
    ('''            - The sets are snapshotted under the manager lock and the registry is
              probed outside it: the registry calls this manager under the
              registry lock, so the manager never calls the registry under its
              own.
            - With both sets empty no probe is made.
''',
     '''            - The sets are snapshotted under the manager lock; the registry's
              published set of flagged lineages is read outside it, with no lock
              at all: the registry calls this manager under the registry lock, so
              the manager never takes the registry lock.
            - With both sets empty nothing else is read.
'''),
    ('''            order - pre-existing: the value is computed, then written outside the
            lock - and the probes widen that window by their cost.
''',
     '''            order - pre-existing: the value is computed, then written outside the
            lock. The subset test adds no lock and little time to that window.
'''),
    ('''        `unregister_spell`) are never excluded.

        Args:
''',
     '''        `unregister_spell`) are never excluded.

        The registry publishes the flagged lineages as one immutable set
        (`SpellSystemStates.non_resolvable_index_ids`), so the answer is one
        subset test, with no Python work per key however many definitions the
        Book holds.

        Args:
'''),
    ('''        Returns:
            bool: True at the first key that is not excluded; False when every
            key is a flagged lineage.

        Threading:
            Called without the manager lock; each probe takes the registry lock,
            then one state lock.
        """
        states = self._spell_system_states
        for key in risky_keys:
            if key.startswith("spell:"):
                return True
            if not states.index_has_flag(key, SpellState.non_resolvable):
                return True
        return False
''',
     '''        Returns:
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
'''),
]


def main() -> None:
    """Edit both apply scripts in place."""
    path = HERE / "apply_state_model.py"
    text = path.read_text(encoding="utf-8")
    for old, new in STATE_MODEL_EDITS:
        text = one(text, old, new, path.name)
    text = one(text, "SPELL_SYSTEM_STATES = [\n", "SPELL_SYSTEM_STATES = [\n" + NEW_STATES_STEPS,
               path.name)
    path.write_bytes(text.encode("utf-8"))
    path = HERE / "apply_risk_manager.py"
    text = path.read_text(encoding="utf-8")
    for old, new in RISK_EDITS:
        text = one(text, old, new, path.name)
    path.write_bytes(text.encode("utf-8"))
    print("edited both apply scripts")


if __name__ == "__main__":
    main()
