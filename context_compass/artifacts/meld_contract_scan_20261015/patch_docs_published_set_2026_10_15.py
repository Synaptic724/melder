"""Amend the meld_state_gate patch docs: the published flagged-lineage set and the five test doubles (melder_1)."""
import pathlib
import sys

NOW = sys.argv[1]
P = pathlib.Path("context_compass/system_docs/patches/active/meld_state_gate_2026_10_15")

EDITS = {
    "architecture_patch.md": [
        ("| SpellSystemStates | `register_index(..., *, resolvable=None)` records the selected version's capability before "
         "it gates; `index_has_flag` | melder_1 |\n",
         "| SpellSystemStates | `register_index(..., *, resolvable=None)` records the selected version's capability before "
         "it gates; `index_has_flag`; `non_resolvable_index_ids`, the flagged lineages as one immutable set | melder_1 |\n"),
        ("| RiskManager | `_refresh_spellbook_flag` ignores flagged lineages; `register_conduit` refreshes once after "
         "seeding | melder_1 |\n",
         "| RiskManager | `_refresh_spellbook_flag` ignores flagged lineages (one subset test against the published set); "
         "`register_conduit` refreshes once after seeding | melder_1 |\n"),
        ("6. Locks: the flag is written under the registry lock, then the state lock (`register_index`'s existing order);\n"
         "   RiskManager reads it through the registry without holding its own lock, as its validity reads already do. No new\n"
         "   lock and no new lock-order edge.\n"
         "7. Cost: no read on any meld path; one registry probe per risky key per refresh, stopping at the first unflagged key;\n"
         "   conjure's seeding refreshes once instead of once per spell.\n",
         "6. Locks: the flag is written under the registry lock, then the state lock (`register_index`'s existing order), and\n"
         "   the registry mirrors it, under the same registry lock and before the gate publishes, into one immutable set of\n"
         "   flagged lineages (`non_resolvable_index_ids`), replaced whole and never mutated. RiskManager reads that set with\n"
         "   no lock at all. No new lock and no new lock-order edge.\n"
         "7. Cost: no read on any meld path; one subset test of a refresh's risky keys against the published set (C-level,\n"
         "   no lock, no Python work per key); conjure's seeding refreshes once instead of once per spell. The first build\n"
         "   probed the registry per key (two locks, about 0.5 us a key: 0.5 ms a refresh in a Book with 1000\n"
         "   definitions); the set replaced it (ticket DECISION 2026-10-15T22:12:54Z).\n"),
        ("  `SpellSystemStates.register_index(spell_index, owner_spellbook_id=None, *, resolvable=None)` (TypeError for a\n"
         "  non-bool) and `SpellSystemStates.index_has_flag(index_id, flag)`; two private RiskManager helpers.\n",
         "  `SpellSystemStates.register_index(spell_index, owner_spellbook_id=None, *, resolvable=None)` (TypeError for a\n"
         "  non-bool), `SpellSystemStates.index_has_flag(index_id, flag)` and the read-only property\n"
         "  `SpellSystemStates.non_resolvable_index_ids` (a frozenset) with its private writer\n"
         "  `_publish_non_resolvable_membership_locked`; two private RiskManager helpers.\n"),
        ("| 7 | the probe (us per meld, conjure-end seeding) before and after; unit: register_conduit refreshes once |\n",
         "| 7 | the probe (us per meld, conjure, late binds with 0 to 1000 definitions, refresh cost) before and after; unit: "
         "register_conduit refreshes once |\n"
         "| 6, 7 | unit: the published set follows every registration path, unregister and cleanup, is replaced rather than "
         "mutated and agrees with each flag; component: every flag check asserts that agreement |\n"),
        ("  refreshes can land out of order. The registry probes run in that window, so it grows by their cost; the race class\n"
         "  is unchanged.\n",
         "  refreshes can land out of order. The subset test runs in that window and adds no lock and little time; the race\n"
         "  class is unchanged.\n"),
        ("- DECISION_REQUEST (owner): the four call-site keywords sit in melder_0's files (spellbook.py, and\n"
         "  transfer_of_ownership.py inside its S6 lane); the handoff goes through the owner.\n",
         "- DECISION_REQUEST (owner): the four call-site keywords sit in melder_0's files (spellbook.py, and\n"
         "  transfer_of_ownership.py inside its S6 lane), and five test doubles in melder_0's test lanes mirror the old\n"
         "  signature (component_patch_registration_call_sites.md); the handoff goes through the owner.\n"),
        ("- What remains: the scratch-tree build and validation, the handoff, the landing.\n",
         "- Amended 2026-10-15T22:12:54Z: RiskManager's exclusion reads the registry's published set of flagged lineages\n"
         "  (invariants 6-7) after the probe showed the per-key registry probe growing with the definition count.\n"
         "- What remains: the handoff, the landing (the scratch tree is built and validated).\n"),
    ],
    "component_patch_spell_state_model.md": [
        ("  - `SpellSystemStates.index_has_flag(index_id, flag) -> bool`: under the registry lock, False for an empty id or an\n"
         "    unregistered index, otherwise the state's `has_flag`. A state held in the registry is live while that lock is\n"
         "    held: `unregister_index` pops a state before it cleans it, and the registry's own cleanup cleans under the lock.\n",
         "  - `SpellSystemStates.index_has_flag(index_id, flag) -> bool`: under the registry lock, False for an empty id or an\n"
         "    unregistered index, otherwise the state's `has_flag`. A state held in the registry is live while that lock is\n"
         "    held: `unregister_index` pops a state before it cleans it, and the registry's own cleanup cleans under the lock.\n"
         "    It is the per-lineage read; RiskManager reads the published set below instead.\n"
         "  - `SpellSystemStates.non_resolvable_index_ids -> FrozenSet[str]` (read-only property): the registered lineages\n"
         "    whose state carries the flag, as one immutable set read without a lock. `register_index` puts the lineage in\n"
         "    or out (`_publish_non_resolvable_membership_locked`) right after the capability write and before\n"
         "    `mark_structural_change`, so the refresh its event runs reads the new set; `unregister_index` takes the lineage\n"
         "    out after it pops the state; the set is replaced whole, never mutated (nothing is replaced when the membership\n"
         "    already matches). Cleanup leaves an empty set as a documented tombstone, so a lock-free read racing it finds a\n"
         "    set; after cleanup the property raises the cleaned-registry RuntimeError.\n"),
        ("- Outputs: `has_flag` and `index_has_flag` return bools; `update_flags` returns None.\n",
         "- Outputs: `has_flag` and `index_has_flag` return bools; `update_flags` returns whether the flag set changed;\n"
         "  `non_resolvable_index_ids` returns a frozenset.\n"),
        ("- Owned state: one more possible member in `SpellSystemState._flags`; no new field.\n",
         "- Owned state: one more possible member in `SpellSystemState._flags`; the registry gains one field,\n"
         "  `_non_resolvable_index_ids` (a frozenset replaced whole under its lock, emptied as a tombstone at cleanup).\n"),
        ("2. Lock order: registry lock, then state lock - `register_index`'s existing order; `index_has_flag` takes the same.\n",
         "2. Lock order: registry lock, then state lock - `register_index`'s existing order; `index_has_flag` takes the same.\n"
         "   The published set is written under the registry lock and read under none.\n"),
        ("  new flag, and an unchanged flag publishes none.\n",
         "  new flag, and an unchanged flag publishes none; the published set follows every registration path, unregister\n"
         "  and cleanup, is replaced rather than mutated, agrees with each lineage's flag, and is already right when the\n"
         "  gate's callback runs.\n"),
        ("- What changed: written before any edit; amended 2026-10-15T21:20:19Z with `_republish_validity` and the result of\n"
         "  `update_flags`.\n",
         "- What changed: written before any edit; amended 2026-10-15T21:20:19Z with `_republish_validity` and the result of\n"
         "  `update_flags`, and 2026-10-15T22:12:54Z with the published set `non_resolvable_index_ids`.\n"),
    ],
    "component_patch_risk_manager.md": [
        ("    `_has_unexcluded_risk`: the flag is up when some key is a `spell:` key, names a lineage with no live state, or\n"
         "    names a lineage whose state lacks `SpellState.non_resolvable` (`SpellSystemStates.index_has_flag`); a set made only\n"
         "    of flagged lineages leaves it down. With both sets empty no read is made.\n",
         "    `_has_unexcluded_risk`: the flag is up when some key is not in the registry's published set of flagged lineages\n"
         "    (`SpellSystemStates.non_resolvable_index_ids`) - a `spell:` key, a lineage with no live state or one whose\n"
         "    state lacks `SpellState.non_resolvable` never is - and a set made only of flagged lineages leaves it down. It\n"
         "    is one subset test with no lock and no Python work per key. With both sets empty nothing else is read.\n"),
        ("- Inputs and outputs: unchanged public methods; the collaborator contract gains one call,\n"
         "  `SpellSystemStates.index_has_flag(index_id, flag)`.\n"
         "- Error semantics: unchanged. A registry that raises in the probe raises out of the refresh, where every caller already\n"
         "  contains it (`set_validity` and `set_spell_validity` swallow callback failures; the Spellbook logs its calls).\n",
         "- Inputs and outputs: unchanged public methods; the collaborator contract gains one read, the\n"
         "  `SpellSystemStates.non_resolvable_index_ids` property.\n"
         "- Error semantics: unchanged. A cleaned registry raises on that read and the error leaves the refresh, where every\n"
         "  caller already contains it (`set_validity` and `set_spell_validity` swallow callback failures; the Spellbook\n"
         "  logs its calls).\n"),
        ("   already do: the registry calls this manager under the registry lock, so the manager must never call the registry\n"
         "   under its own.\n",
         "   already do: the registry calls this manager under the registry lock, so the manager must never call the registry\n"
         "   under its own. The published set is read without any lock.\n"),
        ("- The existing RiskManager unit tests stay green; their registry stub gains `index_has_flag` (False: nothing flagged).\n",
         "- The existing RiskManager unit tests stay green; their registry stub gains `non_resolvable_index_ids` (empty:\n"
         "  nothing flagged).\n"),
        ("- What changed: written before any edit.\n",
         "- What changed: written before any edit; amended 2026-10-15T22:12:54Z: the exclusion reads the registry's published\n"
         "  set (one subset test) instead of a registry probe per key, whose cost grew with the definition count.\n"),
    ],
    "code_description_patch_risk_distillation.md": [
        ("- Components: SpellSystemStates.register_index, SpellSystemStates.index_has_flag, RiskManager\n",
         "- Components: SpellSystemStates.register_index, SpellSystemStates.non_resolvable_index_ids, RiskManager\n"),
        ("   `non_resolvable`; True -> remove; None -> remove unless the selection was kept. No publication; note whether\n"
         "   the flag set changed and whether the validity is already `gated`.\n",
         "   `non_resolvable`; True -> remove; None -> remove unless the selection was kept. No publication; note whether\n"
         "   the flag set changed and whether the validity is already `gated`. Then put the lineage in or out of the\n"
         "   published set (`_publish_non_resolvable_membership_locked`, reading the flag back with `has_flag`): the set is\n"
         "   replaced whole, never mutated, and nothing is replaced when the membership already matches.\n"),
        ("2. `_has_unexcluded_risk(snapshot)`: for each key - `spell:` prefix -> True; else\n"
         "   `index_has_flag(key, non_resolvable)` (registry lock, then state lock) False -> True. All flagged -> False.\n",
         "2. `_has_unexcluded_risk(snapshot)`: `not snapshot <= states.non_resolvable_index_ids` - one subset test, no lock;\n"
         "   a `spell:` key or a removed lineage is never in the set, so it counts. All flagged -> False.\n"),
        ("- A removed lineage: `unregister_index` fires `cleaned` after it popped the state, so the probe finds no state and the\n"
         "  lineage counts until `unregister_spell` drops it - unchanged.\n"
         "- A registry probe on a state cleaned by a racing unregister cannot happen: the probe holds the registry lock, and a\n"
         "  state leaves the registry before it is cleaned.\n",
         "- A removed lineage: `unregister_index` takes it out of the set when it pops the state, before it fires `cleaned`,\n"
         "  so the lineage counts until `unregister_spell` drops it - unchanged.\n"
         "- A refresh racing a registration reads the set from before or after it; the refresh that the registration's event\n"
         "  runs reads the new one, because the set is replaced before the event publishes. A refresh racing the registry's\n"
         "  cleanup finds the empty tombstone set, or the cleaned-registry RuntimeError, never a missing attribute.\n"),
        ("- Lock order stays registry -> state and never manager -> registry; no new lock.\n",
         "- The published set equals the registered lineages whose state carries the flag at every release of the registry\n"
         "  lock.\n"
         "- Lock order stays registry -> state and never manager -> registry; no new lock.\n"),
        ("- The gated event sees the new flag (a recording manager's callback reads `index_has_flag`).\n",
         "- The gated event sees the new flag and the new set (a recording manager's callback reads `index_has_flag` and\n"
         "  `non_resolvable_index_ids`).\n"),
        ("- What changed: written before any edit; step 5 added 2026-10-15T21:20:19Z (found while writing the risk tests).\n",
         "- What changed: written before any edit; step 5 added 2026-10-15T21:20:19Z (found while writing the risk tests); the\n"
         "  published set added 2026-10-15T22:12:54Z (the per-key probe's cost grew with the definition count).\n"),
    ],
    "component_patch_registration_call_sites.md": [
        ("  S6 lane). Edited only after the owner hands the four lines over.\n",
         "  S6 lane). Edited only after the owner hands the four lines over.\n"
         "- Tests: five test doubles in melder_0's test lanes that mirror the old signature (below), in the same handoff.\n"),
        ("## Interface deltas\n- None beyond the keyword.",
         "## Test doubles that follow the keyword\n"
         "With only the four keywords applied, 45 unit tests failed: two `register_index` lambdas reject the keyword and two\n"
         "transfer `build_spell` doubles return a SimpleNamespace without `resolvable`. A real Spell always carries\n"
         "`resolvable` (default True) and the real registry takes the keyword, so the doubles are corrected to mirror that;\n"
         "no production fallback is added.\n"
         "- `tests/unit/melder/spellbook/test_spellbook.py`: both lambdas take `resolvable=None`; the bind one records\n"
         "  `(spell_index, new_spell, resolvable)` and the test asserts that bind passes True.\n"
         "- `tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py` and\n"
         "  `test_transfer_of_ownership_contracts.py`: the fake `register_index` takes `*, resolvable: Optional[bool] = None`\n"
         "  (its stale `spell:` Args line corrected) and `build_spell` sets `resolvable=True`.\n"
         "- `tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py` and\n"
         "  `test_spellbook_component_spellbook.py`: the fake `register_index` takes `*, resolvable: object = None`, with an\n"
         "  Args line.\n"
         "The apply script `apply_call_sites.py` in the lane's artifact folder writes the four keywords and these doubles;\n"
         "its `--check` finds every anchor in the real tree.\n"
         "\n"
         "## Interface deltas\n- None beyond the keyword."),
        ("- DECISION_REQUEST (owner): hand these four lines to melder_1, or have melder_0 add the keyword in its lane.\n",
         "- DECISION_REQUEST (owner): hand these four lines and the five test files to melder_1, or have melder_0 apply\n"
         "  them (apply_call_sites.py) in its lane.\n"),
        ("- What changed: written before any edit; the change is built and validated on a scratch tree first.\n",
         "- What changed: written before any edit; the change is built and validated on a scratch tree first; amended\n"
         "  2026-10-15T22:12:54Z with the five test doubles.\n"),
    ],
}


def main() -> None:
    """Apply every edit by exact text, check line widths, stamp Updated."""
    for name, edits in EDITS.items():
        path = P / name
        text = path.read_text(encoding="utf-8")
        for old, new in edits:
            count = text.count(old)
            assert count == 1, (name, count, old[:70])
            text = text.replace(old, new, 1)
        for line in text.splitlines():
            assert len(line) <= 120 or line.startswith("|"), (name, len(line), line)
        start = text.index("- Updated: ")
        end = text.index("\n", start)
        text = text[:start] + f"- Updated: {NOW}" + text[end:]
        path.write_bytes(text.encode("utf-8"))
        print("amended", name)


if __name__ == "__main__":
    main()
