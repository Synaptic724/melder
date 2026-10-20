"""Record the full-tree runs, the before/after probe and the published-set refinement (melder_1, 2026-10-15)."""
import pathlib
import sys

NOW = sys.argv[1]
CC = pathlib.Path("context_compass")
T = CC / "tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md"
A = "context_compass/artifacts/meld_contract_scan_20261015"
AP = CC / "artifacts/meld_contract_scan_20261015"


def lines_of(rel: str) -> int:
    """Line count of one artifact file, for an exact evidence range."""
    return len((AP / rel).read_text(encoding="utf-8").splitlines())


SUITES = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Every chunk of the test tree passes on the scratch tree with the GIL off and on (23 chunks, the same counts
    in both modes): unit_aether 4460, unit_sb 2560, unit_cryst 607, unit_mr 277, unit_util 826 + 2 skipped + 7
    xfailed, unit_build 116, unit_top 146, unit_llm 28, unit_arch 18, unit_gh 491; comp_aether 1386 + 1 xfailed,
    comp_sb 819, comp_cryst 110, comp_mr 40, comp_util 41 + 23 skipped; int_aether 785 + 5 xfailed, int_conduit 335,
    int_sb 619 + 2 skipped + 2 xpassed, int_mt 54, int_cryst 276 + 3 xfailed, int_mr 67, int_live 1 + 1 xfailed;
    experimentation 250 + 4 skipped. Against the six chunks run on the pristine copy the only change is the new
    tests (unit_aether 4421 -> 4460, comp_aether 1377 -> 1386). unit_gh's first GIL-off run failed 2 tests because
    the scratch copy lacked `.readthedocs.yaml` and `codecov.yml` (a copy omission); with both copied in it passed.
  EVIDENCE:
  - {A}/runs/full_gil0.txt:1-{lines_of("runs/full_gil0.txt")}
  - {A}/runs/full_gil1.txt:1-{lines_of("runs/full_gil1.txt")}
  - {A}/runs/baseline_gil0.txt:1-{lines_of("runs/baseline_gil0.txt")}
  - {A}/run_chunks.sh:1-{lines_of("run_chunks.sh")}
  IMPACT: The change, its four call sites and the corrected doubles break nothing in the tree in either mode.
  NEXT: The before/after probe.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
"""

PROBE = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Before/after probe, GIL off (before: a copy of the real tree's src at 0.2.8246; after: the scratch tree;
    caching off, nothing written to either tree). Warm meld: an automatic Book with one Protocol definition 15.09 ->
    0.24 us, dynamic 16.38 -> 0.71 us, a consumer fed a class definition by override 15.48 -> 0.53 us (gate entries
    1 -> 0 per meld, Book flag up -> down); without a definition unchanged (0.26 -> 0.26, 0.84 -> 0.70 us); the
    borrower SpellContract consumer unchanged (2154 -> 2158 us: its flag is held by the borrowed provider, a
    resolvable lineage - items (2)-(3)). Conjure of 200 spells with 0, 20 and 100 definitions: medians within 2 ms
    either way over 2 x 9 runs a side, register_conduit unchanged, one refresh instead of one per visible spell (401
    instead of 601-701). The regression: with only definitions risky, `_has_unexcluded_risk` probes every key
    through `index_has_flag` (two locks, about 0.5 us a key), so a refresh costs 1.4 -> 2.6 us with no definition,
    1.7 -> 11.2 us with 20, 1.8 -> 43.8 us with 100 and 1.8 -> 521 us (max 1.6 ms) with 1000; in a dynamic Book with
    1000 definitions a late bind plus its first meld (4 refreshes) goes 6.9 -> 9.2 ms, while warm melds go 12.5 ->
    0.70 us.
  EVIDENCE:
  - {A}/probe_before_after.py:1-{lines_of("probe_before_after.py")}
  - {A}/runs/probe_before_after_before_gil0.txt:1-{lines_of("runs/probe_before_after_before_gil0.txt")}
  - {A}/runs/probe_before_after_after_gil0.txt:1-{lines_of("runs/probe_before_after_after_gil0.txt")}
  - {A}/runs/probe_before_after_conjure_gil0.txt:1-{lines_of("runs/probe_before_after_conjure_gil0.txt")}
  - {A}/runs/probe_before_after_d1000_gil0.txt:1-{lines_of("runs/probe_before_after_d1000_gil0.txt")}
  - {A}/apply_risk_manager.py:134-206
  IMPACT: The meld path improves as designed and nothing else moves except the flag refresh, whose cost now grows
    with the number of definitions - an event-path regression for bind- and notch-heavy Books with many of them.
  NEXT: Make the exclusion check independent of per-key Python work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

DECISION = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Refinement inside Option A (the same flag and reader; RiskManager keeps no state of its own): the registry
    publishes the ids of the lineages whose state carries `SpellState.non_resolvable` as a frozenset
    (`SpellSystemStates.non_resolvable_index_ids`), replaced whole under the registry lock wherever that membership
    can change - `register_index` reconciles the lineage with its flag right after `_record_selected_capability`,
    before the gate publishes; `unregister_index` drops it; cleanup leaves an empty set as a tombstone for readers
    racing it - and read without a lock. `RiskManager._has_unexcluded_risk` becomes one subset test of the risky
    keys against it (a `spell:` key or a removed lineage is never in it, as before), so a refresh takes no registry
    lock and does no Python work per key. `index_has_flag` stays as the per-lineage read. Tests: A gains the set
    (each registration path, unregister, cleanup, replacement rather than mutation, agreement with the flag); the
    stub C answers it; the component helper asserts the set agrees with the flag at every check; patch docs and the
    apply scripts follow, and the four melder_1 files on the scratch tree are regenerated from pristine copies.
  EVIDENCE:
  - {A}/runs/probe_before_after_d1000_gil0.txt:1-{lines_of("runs/probe_before_after_d1000_gil0.txt")}
  - {A}/apply_risk_manager.py:134-206
  - {A}/apply_state_model.py:319-363
  - {A}/apply_state_model.py:366-456
  IMPACT: A refresh's cost no longer grows with Python work per definition; the meld path, the flag's meaning and
    every existing test expectation stay as they are.
  NEXT: Apply it on the scratch tree, rerun A-D and every chunk with the GIL off and on, then the probe both modes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""


def one(text: str, old: str, new: str) -> str:
    """Replace exactly one occurrence."""
    assert text.count(old) == 1, (text.count(old), old[:60])
    return text.replace(old, new, 1)


def main() -> None:
    """Append the three Notes, stamp the ticket and move the board row."""
    for block in (SUITES, PROBE, DECISION):
        for line in block.splitlines():
            stripped = line.lstrip()
            assert len(line) <= 120 or stripped.startswith(("- src/", "- tests/", "- context_compass/")), line
    text = T.read_text(encoding="utf-8")
    text = one(text, "  SCORE_0_TO_10: 9\n\n## Context / Handoff Summary\n",
               "  SCORE_0_TO_10: 9\n" + SUITES + PROBE + DECISION + "\n## Context / Handoff Summary\n")
    start = text.index("- Updated: ")
    end = text.index("\n", start)
    text = text[:start] + f"- Updated: {NOW}" + text[end:]
    T.write_bytes(text.encode("utf-8"))
    board = CC / "attention_board.md"
    bt = board.read_text(encoding="utf-8")
    bt = one(bt, "| Every chunk with the GIL off and on on the scratch tree, then the probe before and after. |",
             "| Publish the flagged-lineage set so a refresh is one subset test; rerun the tests, chunks and probe. |")
    i = bt.index("| meld_contract_scan | in_progress |")
    j = bt.index("\n", i)
    cells = bt[i:j].split(" | ")
    cells[-2] = NOW
    bt = bt[:i] + " | ".join(cells) + bt[j:]
    board.write_bytes(bt.encode("utf-8"))
    print("recorded", NOW)


if __name__ == "__main__":
    main()
