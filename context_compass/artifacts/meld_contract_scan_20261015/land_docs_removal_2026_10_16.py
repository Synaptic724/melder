"""Promote the removal fix (contracted_copy_removal_by_version_2026_10_16, 0.2.8251) into the system docs.

melder_1 (synaptic_python_developer), 2026-10-16. Edits src_architecture.md, src_components.md and tests_components.md
under <system_docs dir>: the remap of every live numeric citation into spellbook.py after the method (+7 lines, each
checked by line-text identity before this script was written), new invariant / failure-mode / component / test
entries, code-map records and handoff entries. Every anchor must match the stated number of times.
usage: python land_docs_removal_2026_10_16.py <system_docs dir> --check | --apply
"""
import datetime
import pathlib
import sys

TS = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
SB = "spellbook/spellbook.py:"

ARCH_INVARIANT = """- One version, one copy (2026-10-16, 0.2.8251; the owner's rule: "you remove that spell if its not active, you look
  in inactive"): a borrower Book holds each borrowed copy, by spell_id, either among its active contracted copies or
  among its parked ones, and `Spellbook._remove_contracted_spell` removes exactly the copy of the spell_id it is
  given - the active copy only when that copy's own spell_id is it, otherwise the parked copy - and raises
  RuntimeError "Spell version <id> not found for conduit ID <peer>." with nothing changed when it holds neither. It
  never reads the index's member set, so every caller gets the copy it names: an index unlink, destroy or member
  removal (`ConduitWard._uncontract_member_spell`, once per member, in the member set's order), a root's dependency
  fallout (`_remove_root_from_contracts`) and a version uncontract (`_remove_spell_from_contract`). Rule 2's mark
  stays on an active removal; the set of borrowed spell_ids keeps its per-index handling (an active removal drops
  every member id of a live index, a parked one its own id). No lock changes: the walk and the pops stay under the
  Book lock, the mark and the RiskManager call after it.
  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook._remove_contracted_spell` and
  `src/melder/aether/conduit/conduit_ward/conduit_ward.py:ConduitWard._uncontract_member_spell`,
  `ConduitWard._remove_index_from_contract`, `ConduitWard._remove_root_from_contracts` and
  `ConduitWard._remove_spell_from_contract`.
"""

ARCH_FAILURE = """- Fixed in 0.2.8251: a borrower that held a parked copy of one version of an index beside the active copy of
  another - an index link after the owner notched it, or two version grants across a notch - lost the wrong copy
  when the parked version was removed: `_remove_contracted_spell` matched an active copy by index membership, so it
  removed the index's active copy under the parked version's spell_id. `remove_index_from_contract` uncontracts the
  members in the member set's order, which follows the hash seed, so in about half of all processes (seeds 3, 4, 6,
  8 and 9 of 0-9) an unlink after a notch raised RuntimeError "Spell version <id> not found for conduit ID
  <owner>." for the active member and left the parked copy behind for good (a retry returned normally and kept
  it); removing an old version's grant took the new version's active copy, so its consumers lost their provider.
  Each version's own copy goes now, in any order.
  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook._remove_contracted_spell` and
  `src/melder/aether/conduit/conduit_ward/conduit_ward.py:ConduitWard._remove_index_from_contract`.
"""

ARCH_HANDOFF = """2026-10-16 one version, one copy (0.2.8251; the owner's rule for removing a borrowed copy):
`_remove_contracted_spell` matches an active copy by its own spell_id, never by index membership, so an unlink after
a notch completes in any member order and a removal never takes another version's copy. A new operational
invariant, a failure mode (fixed) and the code map carry it; the component map carries the per-component contract.
Every numeric citation into spellbook.py after the method moved seven lines and was remapped; the two inner
citations of the settle-then-inherit evidence (`:6823-6835`, `:6836`), stale since an earlier lane, now point at
the settlement block and its return.

"""

COMP_SPELLBOOK = """One version, one copy (2026-10-16, 0.2.8251; contracted_copy_removal_by_version): `_remove_contracted_spell(spell_id,
conduit_id)` removes the copy of exactly the spell_id it is given. Under the Book lock it walks the peer's active map
(index -> copy) for the copy whose own `spell_id` is `spell_id`, for a live or a cleaned index alike, taking the
index from the map key, so neither a cleaned index's member set nor a cleaned copy's deleted `spell_index` is read;
found, it unregisters the by-id entry and pops the index entry and the lookup key; otherwise it pops the spell_id's
parked copy; with neither it raises RuntimeError "Spell version <id> not found for conduit ID <peer>." before
anything changes. Until 0.2.8251 a live index was matched by membership (`spell_id in idx._spells_in_index`), so
asked for a parked version beside another version's active copy it removed the active copy, and the later removal of
that version raised. The existence set `_contracted_spell_ids` keeps its per-index handling (an active removal drops
every member id of a live index, a parked one its own id; the add paths record every member id) and rule 2's mark
stays on the active branch.
EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook._remove_contracted_spell`,
`Spellbook._add_contracted_spell` and `Spellbook._add_inactive_contracted_spell`.

"""

COMP_WARD = """- An index's members leave a borrower one by one (0.2.8251): `_remove_index_from_contract` and `_emit_index_destroy`
  call `_uncontract_member_spell` for each member in the member set's order - a set, ordered by the process's hash
  seed - and each asks the borrower Book to remove that member's own copy (`Spellbook._remove_contracted_spell`). An
  index link holds a copy of every member (`_contract_member_spell`: active for the active member, parked for the
  rest), so the unlink completes in any order; until 0.2.8251 a parked member visited first took the active
  member's copy, the active member's removal then raised, and the IndexDetail cleanup and the borrower's untrack
  after the loop never ran.
"""

COMP_HANDOFF = """2026-10-16 one version, one copy (0.2.8251): Spellbook Core carries `_remove_contracted_spell`'s match by the
copy's own spell_id, its parked fallback and its raise; ConduitWard and Contracts carries the member-by-member unlink
that now completes in any order. Every numeric citation into spellbook.py after the method moved seven lines and was
remapped, and the code map remeasures the file.

"""

TESTS_UNIT = """- one version, one copy (0.2.8251; three tests in `test_spellbook.py`, one parametrized): removing a parked
  version beside the active copy of another version of its index removes only the parked copy and marks nothing,
  and removing the active version then marks its consumers; a spell_id the Book holds no copy of raises the
  not-found RuntimeError and leaves the active copy; both versions removed in either order leave no copy, active
  or parked, and an empty set of borrowed spell_ids
"""

TESTS_COMP = """- contracted-copy removal by spell_id (0.2.8251; `test_spellbook_component_contracts.py`): the removal test now
  names the active copy by its own spell_id and still finds every member id of the live index dropped; it used to
  name a member with no copy and rely on the membership match the fix removed
"""

TESTS_INTEG = """- one version, one copy (0.2.8251; `test_spell_index_meld_and_contract_lifecycle.py`, 3 tests): after the owner
  notches a linked index to a version staged on it, `remove_index_from_contract` removes both members' copies and
  untracks the index whichever member it visits first (the order fixed through `SpellIndex.spells_in_index`); a
  borrower granted a version and then the version notched in keeps the new version's active copy, and melds it,
  when the old version's grant is removed by its Spell
"""

TESTS_RECORD = f"""- path: `tests/integration/melder/aether/conduit/test_spell_index_meld_and_contract_lifecycle.py`
  start_line: 1
  end_line: 271
  loc: 271
  verified_at: {TS}
  note: meld and contract lifecycle on real dynamic conduits; one version, one copy - the unlink after a notch in
    either member order and the removal of a parked version's grant (0.2.8251).
"""

TESTS_HANDOFF = """2026-10-16 one version, one copy (0.2.8251): the Spellbook Runtime And Binding Unit Cluster names the three
removal tests in `test_spellbook.py`, the Component Cluster the contracts test that now removes the active copy by
its own spell_id, and the Spellbook Integration Cluster the unlink after a notch in either member order and the
grant removal, with `test_spell_index_meld_and_contract_lifecycle.py` as a key file and a new code-map record; the
records of `test_spellbook.py` and `test_spellbook_component_contracts.py` are remeasured.

"""

HANDOFF = "## Context / Handoff Summary\n\n"

EDITS = {
    "src_architecture.md": [
        (SB + "3884-3886", SB + "3891-3893", 1),
        (SB + "4056 (`_add_to_spell_index` entry)", SB + "4063 (`_add_to_spell_index` entry)", 1),
        (SB + "4089 (`_apply_add_to_index` seam)", SB + "4096 (`_apply_add_to_index` seam)", 1),
        (SB + "3899-4349 (the three seams, remeasured 2026-10-16)",
         SB + "3906-4356 (the three seams, remeasured 2026-10-16 at 0.2.8251)", 1),
        (SB + "3899-4054\n", SB + "3906-4061\n", 1),
        (SB + "4089-4183\n", SB + "4096-4190\n", 1),
        (SB + "4264-4349\n", SB + "4271-4356\n", 1),
        (SB + "6934-6977\n    (`Spellbook._settle_or_inherit_conjure_mode`; in-place settle :6823-6835,\n"
              "    effective-mode return :6836; remeasured 2026-10-16 at 0.2.8248)",
         SB + "6941-6984\n    (`Spellbook._settle_or_inherit_conjure_mode`; in-place settle :6971-6983,\n"
              "    effective-mode return :6984; remeasured 2026-10-16 at 0.2.8251)", 1),
        (SB + "7190\n", SB + "7197\n", 1),
        ("## Operational Invariants\n", "## Operational Invariants\n" + ARCH_INVARIANT, 1),
        ("## Failure Modes and Error Paths\n", "## Failure Modes and Error Paths\n" + ARCH_FAILURE, 1),
        ("- path: `src/melder/aether/spellbook/spellbook.py`\n  start_line: 1\n  end_line: 7759\n  loc: 7759\n"
         "  verified_at: 2026-10-16T16:48:16Z\n",
         "- path: `src/melder/aether/spellbook/spellbook.py`\n  start_line: 1\n  end_line: 7766\n  loc: 7766\n"
         f"  verified_at: {TS}\n", 1),
        ("    and `_apply_notch` marks everything downstream of the notched lineage (0.2.8250).\n",
         "    and `_apply_notch` marks everything downstream of the notched lineage (0.2.8250);\n"
         "    `_remove_contracted_spell` removes the copy of the spell_id it is given, matched by the copy's own\n"
         "    spell_id (0.2.8251).\n", 1),
        (HANDOFF, HANDOFF + ARCH_HANDOFF, 1),
    ],
    "src_components.md": [
        (SB + "3844, 3899 (", SB + "3851, 3906 (", 1),
        (SB + "4056, 4089 (", SB + "4063, 4096 (", 1),
        (SB + "4232, 4264 (", SB + "4239, 4271 (", 1),
        (SB + "3884-3886", SB + "3891-3893", 2),
        (SB + "7553-7574", SB + "7560-7581", 1),
        (SB + "3899-4054", SB + "3906-4061", 1),
        (SB + "4089-4183", SB + "4096-4190", 1),
        (SB + "4264-4349", SB + "4271-4356", 1),
        (SB + "6034-6039", SB + "6041-6046", 1),
        (SB + "5562-5578", SB + "5569-5585", 1),
        (SB + "3899, 4089, 4264", SB + "3906, 4096, 4271", 1),
        (SB + "6866`", SB + "6873`", 1),
        ("### Component: Spellbook Core (Binding and Conjure)\nContract consumers marked on a provider change",
         "### Component: Spellbook Core (Binding and Conjure)\n" + COMP_SPELLBOOK
         + "Contract consumers marked on a provider change", 1),
        ("  ward locks, and the listing held the ward lock while it waited for the conduit lock - the two deadlocked.\n",
         "  ward locks, and the listing held the ward lock while it waited for the conduit lock - the two deadlocked.\n"
         + COMP_WARD, 1),
        ("- path: `src/melder/aether/spellbook/spellbook.py`\n  start_line: 1\n  end_line: 7759\n  loc: 7759\n"
         "  verified_at: 2026-10-16T16:51:53Z\n",
         "- path: `src/melder/aether/spellbook/spellbook.py`\n  start_line: 1\n  end_line: 7766\n  loc: 7766\n"
         f"  verified_at: {TS}\n", 1),
        (HANDOFF, HANDOFF + COMP_HANDOFF, 1),
    ],
    "tests_components.md": [
        ("  that lane\nKey Files (C1):\n- `tests/unit/melder/spellbook/test_spellbook.py`\n",
         "  that lane\n" + TESTS_UNIT + "Key Files (C1):\n- `tests/unit/melder/spellbook/test_spellbook.py`\n", 1),
        ("  after the notch back\nKey Files (C1):\n- `tests/component/melder/spellbook/test_spellbook_component_bind.py`\n",
         "  after the notch back\n" + TESTS_COMP
         + "Key Files (C1):\n- `tests/component/melder/spellbook/test_spellbook_component_bind.py`\n", 1),
        ("  selection, members and melds intact\nKey Files (C1):\n"
         "- `tests/integration/melder/spellbook/test_spellbook_integration_core.py`\n",
         "  selection, members and melds intact\n" + TESTS_INTEG + "Key Files (C1):\n"
         "- `tests/integration/melder/spellbook/test_spellbook_integration_core.py`\n", 1),
        ("- `tests/integration/melder/aether/conduit/test_index_moves_by_spell_id_integration.py` (2026-10-16)\n",
         "- `tests/integration/melder/aether/conduit/test_index_moves_by_spell_id_integration.py` (2026-10-16)\n"
         "- `tests/integration/melder/aether/conduit/test_spell_index_meld_and_contract_lifecycle.py` (2026-10-16)\n",
         1),
        ("- path: `tests/unit/melder/spellbook/test_spellbook.py`\n  start_line: 1\n  end_line: 5511\n  loc: 5511\n"
         "  verified_at: 2026-10-16T17:07:35Z\n",
         "- path: `tests/unit/melder/spellbook/test_spellbook.py`\n  start_line: 1\n  end_line: 5605\n  loc: 5605\n"
         f"  verified_at: {TS}\n", 1),
        ("- path: `tests/component/melder/spellbook/test_spellbook_component_contracts.py`\n  start_line: 1\n"
         "  end_line: 749\n  loc: 749\n  verified_at: 2026-09-26T22:11:36Z\n",
         "- path: `tests/component/melder/spellbook/test_spellbook_component_contracts.py`\n  start_line: 1\n"
         f"  end_line: 752\n  loc: 752\n  verified_at: {TS}\n", 1),
        ("  note: add and remove by spell_id in a dynamic world; the refusals leave both indexes intact (0.2.8249).\n",
         "  note: add and remove by spell_id in a dynamic world; the refusals leave both indexes intact (0.2.8249).\n"
         + TESTS_RECORD, 1),
        ("- `tests/component/melder/spellbook/test_spellbook_component_structural_snapshot_parity.py`\n",
         "- `tests/component/melder/spellbook/test_spellbook_component_structural_snapshot_parity.py`\n"
         "- `tests/integration/melder/aether/conduit/test_spell_index_meld_and_contract_lifecycle.py`\n", 1),
        (HANDOFF, HANDOFF + TESTS_HANDOFF, 1),
    ],
}

BANNED = ("context_compass/", "agent_onboarding/", "tools/system_documents/", "system_docs/", "patches/active/",
          "index_document.py")


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[2] not in ("--check", "--apply"):
        raise SystemExit("usage: <system_docs dir> --check | --apply")
    root = pathlib.Path(sys.argv[1])
    out = {}
    for name, edits in EDITS.items():
        text = (root / name).read_text(encoding="utf-8")
        before = text
        for old, new, count in edits:
            n = text.count(old)
            if n != count:
                raise SystemExit(f"{name}: anchor {old[:70]!r} found {n} times, expected {count} - refusing")
            text = text.replace(old, new)
        added = [ln for ln in text.split("\n") if ln not in set(before.split("\n"))]
        long = [ln for ln in added if len(ln) > 120]
        leaks = [ln for ln in added if any(b in ln for b in BANNED)]
        if long or leaks:
            raise SystemExit(f"{name}: long {long} leaks {leaks} - refusing")
        out[name] = text
        print(name, "lines", before.count("\n"), "->", text.count("\n"), "added lines", len(added))
    if sys.argv[2] == "--check":
        print("check only - nothing written")
        return
    for name, text in out.items():
        (root / name).write_text(text, encoding="utf-8")
        assert (root / name).read_text(encoding="utf-8") == text
    print("applied and read back")


if __name__ == "__main__":
    main()
