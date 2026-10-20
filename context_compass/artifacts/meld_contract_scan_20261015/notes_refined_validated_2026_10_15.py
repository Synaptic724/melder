"""Record the validated published-set refinement and the line-ending finding (melder_1, 2026-10-15)."""
import pathlib
import sys

NOW = sys.argv[1]
CC = pathlib.Path("context_compass")
T = CC / "tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md"
A = "context_compass/artifacts/meld_contract_scan_20261015"
AP = CC / "artifacts/meld_contract_scan_20261015"


def rng(rel: str) -> str:
    """`path:1-N` for one artifact file."""
    return f"{A}/{rel}:1-{len((AP / rel).read_text(encoding='utf-8').splitlines())}"


MEASURE = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The published set, built and validated on the scratch tree. The old apply scripts were first shown to
    reproduce the four scratch files byte for byte from pristine copies; the amended scripts then regenerated them,
    and all three scripts' --check find every anchor in the real tree. Tests: A 34 (6 new: every registration path,
    unregister, replacement rather than mutation, agreement with the flag, the cleanup tombstone), B 11, C 21 (the
    stub answers the set), D 9 (each flag check asserts the set agrees) - green with the GIL off and on. Mutations:
    register_index not publishing the membership fails 6 A, 7 B and 7 D; unregister_index keeping it fails 2 A and
    1 B. Every chunk is green in both modes with the earlier counts plus the 6 new tests (unit_aether 4466). Probe
    after the refinement: a warm meld with a definition 14.4-16.4 -> 0.24-0.77 us in both modes, plain worlds and
    conjure unchanged within noise; a refresh costs 2.3 / 3.8 / 6-8 / 36 us with 0 / 20 / 100 / 1000 definitions
    (1.3-2.7 us before the change; 521 us at 1000 with the per-key probe); a late bind plus its first meld at 1000
    definitions 7437 -> 7360 us (GIL off) and 7613 -> 6951 us (GIL on); interleaved, 5 x 60 late binds a side:
    medians 2499 -> 2313 us with no definition and 3590 -> 2886 us with 100.
  EVIDENCE:
  - {rng("runs/refine_gil0.txt")}
  - {rng("runs/refine_gil1.txt")}
  - {rng("runs/mutation_published_set_gil0.txt")}
  - {rng("runs/full_refined_gil0.txt")}
  - {rng("runs/full_refined_gil1.txt")}
  - {rng("runs/probe_before_after_after_refined_gil0.txt")}
  - {rng("runs/probe_before_after_after_refined_gil1.txt")}
  - {rng("runs/probe_before_after_before_gil1.txt")}
  - {rng("runs/probe_before_after_d1000_refined.txt")}
  - {rng("runs/probe_before_after_late_bind_interleaved_gil0.txt")}
  - {rng("refine_published_set_2026_10_15.py")}
  - {rng("patch_docs_published_set_2026_10_15.py")}
  IMPACT: Rule 1 is built, tested and measured; the event path no longer pays per definition, and the meld path
    keeps the win. What remains is the landing.
  NEXT: Make the apply scripts keep each file's line endings (next Note), then ask the owner for the handoff.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

FACT = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The apply helper rewrites every file it touches with LF line endings (`read_text` translates CRLF and
    `write_bytes` writes LF). Of the ten files the landing edits, git stores three test files with CRLF in the
    index - test_spellbook_component_spell_crafter.py, test_transfer_of_ownership.py and
    test_transfer_of_ownership_contracts.py (i/crlf w/crlf) - so an LF rewrite would commit as a whole-file change;
    the others are stored LF (risk_manager.py, spell_state.py, spell_system_state.py and test_risk_manager.py are
    CRLF only in the owner's working copy, three files are mixed, spellbook.py and transfer_of_ownership.py are LF).
    The scratch tree's copies are LF; Python reads both alike, so no run is affected.
  EVIDENCE:
  - {rng("runs/eol_listing_2026_10_15.txt")}
  - {rng("apply_lib.py")}
  IMPACT: Landed as is, the three CRLF test files (melder_0's lanes) would carry a whole-file diff. The helper
    must write CRLF back to a file that was CRLF throughout; mixed and LF files stay LF (their index form).
  NEXT: Fix apply_lib.apply, regenerate the scratch files with it, confirm the content is unchanged.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""


def one(text: str, old: str, new: str) -> str:
    """Replace exactly one occurrence."""
    assert text.count(old) == 1, (text.count(old), old[:60])
    return text.replace(old, new, 1)


def main() -> None:
    """Append both Notes and stamp the ticket."""
    for block in (MEASURE, FACT):
        for line in block.splitlines():
            stripped = line.lstrip()
            assert len(line) <= 120 or stripped.startswith(("- src/", "- tests/", "- context_compass/")), line
    text = T.read_text(encoding="utf-8")
    text = one(text, "  SCORE_0_TO_10: 9\n\n## Context / Handoff Summary\n",
               "  SCORE_0_TO_10: 9\n" + MEASURE + FACT + "\n## Context / Handoff Summary\n")
    start = text.index("- Updated: ")
    end = text.index("\n", start)
    text = text[:start] + f"- Updated: {NOW}" + text[end:]
    T.write_bytes(text.encode("utf-8"))
    print("recorded", NOW)


if __name__ == "__main__":
    main()
