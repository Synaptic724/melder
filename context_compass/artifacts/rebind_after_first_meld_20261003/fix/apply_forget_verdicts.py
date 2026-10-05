"""
Apply the rebind_after_first_meld_2026_10_03 source change to a Melder tree.

Usage: python apply_forget_verdicts.py <repo_root> [--check]

Edits (byte-level, CRLF-preserving, exact anchors, refuses on any mismatch):
  1. conduit_resolution_state.py: new verb ConduitResolutionState.forget_spell(...).
  2. spell_system_states.py: new verbs SpellSystemStates.forget_spell_resolution_verdicts(...)
     and SpellSystemStates._forget_resolution_verdicts_locked(...); register_index and
     unregister_index call the locked helper; docstrings updated.
"""
import pathlib
import sys

NL = "\r\n"


def crlf(text: str) -> str:
    return text.replace("\n", NL)


def patch(path: pathlib.Path, edits: list[tuple[str, str]], check: bool) -> None:
    raw = path.read_bytes().decode("utf-8")
    for old, new in edits:
        old_c, new_c = crlf(old), crlf(new)
        count = raw.count(old_c)
        if count != 1:
            raise SystemExit(f"{path.name}: anchor found {count} times (expected 1):\n{old!r}")
        raw = raw.replace(old_c, new_c)
    if check:
        print(f"OK (check) {path}")
        return
    path.write_bytes(raw.encode("utf-8"))
    print(f"patched {path}")


CRS_OLD_1 = """    # ------------------------------------------------------------------ #
    # Diagnostics                                                        #
    # ------------------------------------------------------------------ #
    def record_diagnostics(self, diagnostics: Sequence[SystemDiagnostic]) -> None:
"""
CRS_NEW_1 = """    # ------------------------------------------------------------------ #
    # Verdict retirement                                                 #
    # ------------------------------------------------------------------ #
    def forget_spell(
            self,
            spell_id: str,
            *,
            change_reason: Optional[SpellStateChangeReason] = None,
    ) -> bool:
        \"\"\"
        Retire every verdict this conduit holds for one spell id.

        Purpose:
            A spell id leaves or re-enters the frame: its definition was cleaned
            up (`SpellSystemStates.unregister_index`), or a definition was bound
            under the same content-stable id (`SpellSystemStates.register_index`,
            which a rebind of the same class at the same address, a notch and an
            ownership transfer all reach). The verdicts this conduit recorded for
            that id describe a version that is no longer the one a meld will
            build, so they are dropped rather than carried forward.

        Contract:
            - Pops the spell-level and the root-level verdict for `spell_id`.
              Other ids, the diagnostics snapshot and `last_validated_at` are
              untouched.
            - After the call `get_spell_validity(spell_id)` and
              `get_root_validity(spell_id)` answer `initial_validity` again,
              exactly as for an id this conduit never resolved, so
              `Meld._ensure_resolution_resolvable` reruns phases 5-11 for this
              conduit before it builds the id again.
            - Marks the state dirty with `change_reason` only when a verdict was
              actually removed; a miss changes nothing.
            - Does NOT notify the `RiskManager`. Forgetting is a change of
              scope, not of verdict: lineage membership in the risk model is
              owned by `RiskManager.register_spell` / `unregister_spell`, which
              the Spellbook calls on bind and on removal and which recompute
              risk from the live verdict. A callback from here would leave a
              risky key behind in every conduit that never registers the
              lineage again (a peer that resolved the id through a contract).

        Args:
            spell_id:
                Versioned spell id whose verdicts are retired.
            change_reason:
                Reason recorded on the state when a verdict was removed.

        Returns:
            bool:
                True when this conduit held a spell-level or root-level verdict
                for the id, False when there was nothing to forget.

        Raises:
            ValueError:
                If spell_id is empty.
            RuntimeError:
                If this state has been cleaned.

        Threading:
            Acquires the internal lock; takes no other lock and runs no
            callback, so the owning registry may hold its own lock across the
            call.
        \"\"\"
        self.check_cleaned()
        if not spell_id:
            raise ValueError("spell_id cannot be empty.")
        with self._lock:
            had_spell_verdict = self._spell_validity.pop(spell_id, None) is not None
            had_root_verdict = self._root_validity.pop(spell_id, None) is not None
            forgotten = had_spell_verdict or had_root_verdict
            if forgotten:
                self.mark_dirty(change_reason=change_reason)
        return forgotten

    # ------------------------------------------------------------------ #
    # Diagnostics                                                        #
    # ------------------------------------------------------------------ #
    def record_diagnostics(self, diagnostics: Sequence[SystemDiagnostic]) -> None:
"""

SSS_OLD_DOC = """    Lifecycle / Cleanup:
        One instance per `AethericFrame`, initialized alongside DevOpsManager.
        Unregistering a lineage notifies `RiskManager` to force validation
        gating, so a removed spell cannot leave a stale "valid" verdict behind.
"""
SSS_NEW_DOC = """    Lifecycle / Cleanup:
        One instance per `AethericFrame`, initialized alongside DevOpsManager.
        Unregistering a lineage notifies `RiskManager` to force validation
        gating and retires the removed spell id's per-conduit resolution
        verdicts in every registered `ConduitResolutionState`, so a removed
        spell cannot leave a stale "valid" verdict behind on either axis.
        Registering an index retires any verdict already held for the version
        id it publishes, because spell ids are content-stable: a rebind of the
        same class at the same address mints the same id for a new Spell with
        no compiler artifact, and a verdict carried across that boundary would
        send the first meld of the replacement straight to the context builder
        with no plan to build from (the rebind-after-first-meld defect).
"""

SSS_OLD_REG_DOC = """        - Mark the spell index as structurally gated with reason
          SpellStateChangeReason.register_or_rebind and add it to the dirty set.

        This is intended to be called from Spellbook.bind(...) or equivalent.
        \"\"\"
"""
SSS_NEW_REG_DOC = """        - Mark the spell index as structurally gated with reason
          SpellStateChangeReason.register_or_rebind and add it to the dirty set.
        - Retire every per-conduit resolution verdict already held for
          `spell_index.selected_spell_id` (`_forget_resolution_verdicts_locked`),
          so a version id that re-enters the frame - a rebind of the same
          class at the same address after `cleanup_spell`, a notch back to a
          member that was active before, a transfer - is resolved again by each
          conduit before it is built there. A first-time id has no verdict and
          nothing happens.

        This is intended to be called from Spellbook.bind(...) or equivalent.
        \"\"\"
"""

SSS_OLD_REG_BODY = """            # Refresh the spell-id index as well
            self._states_by_spell_id[current_id] = state

            if owner_spellbook_id is not None and self._index_owner_spellbook_id is not None:
"""
SSS_NEW_REG_BODY = """            # Refresh the spell-id index as well
            self._states_by_spell_id[current_id] = state

            # The version id is (re)entering the frame: no conduit may keep a
            # resolution verdict recorded for an earlier life of the same id.
            self._forget_resolution_verdicts_locked(
                current_id,
                change_reason=SpellStateChangeReason.register_or_rebind,
            )

            if owner_spellbook_id is not None and self._index_owner_spellbook_id is not None:
"""

SSS_OLD_UNREG_DOC = """        - Detach this spell index from reverse-dependency edges.
        - Notify RiskManager so spellbooks referencing this spell index require validation.
        - Cleanup the removed SpellSystemState.
"""
SSS_NEW_UNREG_DOC = """        - Detach this spell index from reverse-dependency edges.
        - Retire the current spell id's resolution verdicts in every registered
          `ConduitResolutionState` (`_forget_resolution_verdicts_locked`), so no
          conduit answers `valid` for a definition that no longer exists, and a
          later bind under the same content-stable id starts unresolved.
        - Notify RiskManager so spellbooks referencing this spell index require validation.
        - Cleanup the removed SpellSystemState.
"""

SSS_OLD_UNREG_MISSING = """                current_spell_id = spell_index.selected_spell_id
                if current_spell_id and states_by_spell_id.get(current_spell_id) is not None:
                    states_by_spell_id.pop(current_spell_id, None)
                dirty_indexes.discard(index_id)
                return None
"""
SSS_NEW_UNREG_MISSING = """                current_spell_id = spell_index.selected_spell_id
                if current_spell_id and states_by_spell_id.get(current_spell_id) is not None:
                    states_by_spell_id.pop(current_spell_id, None)
                if current_spell_id:
                    self._forget_resolution_verdicts_locked(
                        current_spell_id,
                        change_reason=SpellStateChangeReason.cleaned_up_spell,
                    )
                dirty_indexes.discard(index_id)
                return None
"""

SSS_OLD_UNREG_MAIN = """            dependencies = removed_state.direct_dependencies

            # Detach reverse edges from dependencies that still exist.
"""
SSS_NEW_UNREG_MAIN = """            dependencies = removed_state.direct_dependencies

            # The definition is leaving the frame: retire its per-conduit
            # resolution verdicts so no conduit keeps a stale `valid` under its
            # content-stable id (a rebind would inherit it and skip phases 5-11).
            if current_spell_id:
                self._forget_resolution_verdicts_locked(
                    current_spell_id,
                    change_reason=SpellStateChangeReason.cleaned_up_spell,
                )

            # Detach reverse edges from dependencies that still exist.
"""

SSS_OLD_ITER = """    def iter_conduit_resolution_states(self) -> Iterator[ConduitResolutionState]:
"""
SSS_NEW_ITER = """    def forget_spell_resolution_verdicts(
            self,
            spell_id: str,
            *,
            change_reason: Optional[SpellStateChangeReason] = None,
    ) -> int:
        \"\"\"
        Retire one spell id's resolution verdicts in every registered conduit.

        Purpose:
            The per-conduit axis of lineage retirement. `unregister_index` and
            `register_index` call the locked form of this verb themselves; this
            public form serves callers that retire or re-gate a version id
            without touching the structural registry.

        Contract:
            - Calls `ConduitResolutionState.forget_spell(spell_id, ...)` on every
              live conduit state under the registry lock, so a conduit dropped
              concurrently (`drop_conduit_resolution_state`) is either already
              gone from the registry or still live for the whole call.
            - Leaves every other id's verdicts, the conduit diagnostics and the
              structural `SpellSystemState` registry untouched.
            - Notifies no `RiskManager`; see `ConduitResolutionState.forget_spell`.

        Args:
            spell_id:
                Versioned spell id whose verdicts are retired frame-wide.
            change_reason:
                Reason recorded on each conduit state that held a verdict.

        Returns:
            int:
                Number of conduit states that held a verdict for the id.

        Raises:
            RuntimeError:
                If the registry has been cleaned (`check_cleaned`).

        Threading:
            Holds the registry lock across the per-conduit calls; each state
            takes only its own lock and runs no callback, so the order
            registry -> conduit state is the only one taken.
        \"\"\"
        self.check_cleaned()
        if not spell_id:
            return 0
        with self._lock:
            return self._forget_resolution_verdicts_locked(
                spell_id,
                change_reason=change_reason,
            )

    def _forget_resolution_verdicts_locked(
            self,
            spell_id: str,
            *,
            change_reason: Optional[SpellStateChangeReason],
    ) -> int:
        \"\"\"
        Retire one spell id's verdicts in every live conduit state; caller holds `_lock`.

        Contract:
            - Caller holds `self._lock` and has checked the registry is live.
            - Visits the live `ConduitResolutionState` objects in registry order
              and calls `forget_spell` on each. A state is cleaned only after
              `drop_conduit_resolution_state` or `cleanup` has popped it from
              the registry under this same lock, so every state visited here is
              live; `forget_spell` raising `RuntimeError` would mean that
              invariant broke, and it is left to raise.
            - Returns how many states held a verdict for the id.

        Args:
            spell_id:
                Versioned spell id whose verdicts are retired.
            change_reason:
                Reason recorded on each conduit state that held a verdict.

        Returns:
            int:
                Number of conduit states that held a verdict for the id.
        \"\"\"
        if self._resolution_by_conduit_id is None:
            return 0
        forgotten = 0
        for resolution_state in self._resolution_by_conduit_id.values():
            if resolution_state.forget_spell(spell_id, change_reason=change_reason):
                forgotten += 1
        return forgotten

    def iter_conduit_resolution_states(self) -> Iterator[ConduitResolutionState]:
"""


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check = "--check" in sys.argv
    if len(args) != 1:
        raise SystemExit(__doc__)
    root = pathlib.Path(args[0])
    base = root / "src/melder/aether/aetheric_frame/dev_ops/spell_system_states"
    patch(base / "conduit_resolution_state.py", [(CRS_OLD_1, CRS_NEW_1)], check)
    patch(
        base / "spell_system_states.py",
        [
            (SSS_OLD_DOC, SSS_NEW_DOC),
            (SSS_OLD_REG_DOC, SSS_NEW_REG_DOC),
            (SSS_OLD_REG_BODY, SSS_NEW_REG_BODY),
            (SSS_OLD_UNREG_DOC, SSS_NEW_UNREG_DOC),
            (SSS_OLD_UNREG_MISSING, SSS_NEW_UNREG_MISSING),
            (SSS_OLD_UNREG_MAIN, SSS_NEW_UNREG_MAIN),
            (SSS_OLD_ITER, SSS_NEW_ITER),
        ],
        check,
    )


if __name__ == "__main__":
    main()
