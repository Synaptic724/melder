"""Record the landing of rule 1 in the real tree and its validation there (melder_1, 2026-10-16).

Usage (from the repository's context_compass folder): python <this script> <UTC timestamp>
Inserts one Note after the last Note (before the resume view); refuses a missing or repeated anchor; keeps LF/CRLF.
"""
import pathlib
import sys

TS = sys.argv[1]
TICKET = pathlib.Path("tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md")
NOTE = f"""- DATETIME: {TS}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Rule 1 is landed in the real tree and validated there. Before the edit the real tree's src matched the
    pristine 0.2.8246 copy except six generated system-document assets from melder_0's S7 rebuild; the three apply
    scripts' --check found every anchor and the scripts applied the eleven edits (the four melder_1 src files, the
    four keywords in spellbook.py and transfer_of_ownership.py, the doubles in five test files; CRLF kept for the six
    files whose working copy is CRLF throughout); tests A, B and D were copied in as new files and the stub C
    written CRLF. After it, src and tests equal the validated scratch tree file for file (CR ignored), except those
    six assets and test-written .meldercache files. A fresh copy of the landed tree (context_compass and docs linked
    read-only, nothing run in the real tree) passes all 23 chunks with the GIL off and on at the scratch counts
    (unit_aether 4466, comp_aether 1386 + 1 xfailed, int_aether 785 + 5 xfailed, int_cryst 276 + 3 xfailed, ...).
    Probe on that copy, GIL off: a warm meld with a definition 15.09 -> 0.26 us (automatic), 16.38 -> 0.73 us
    (dynamic), 15.48 -> 0.41 us (override consumer); plain worlds 0.25 / 0.79 us; the borrower contract consumer
    2206 us (unchanged; items (2)-(3)); conjure of 200 spells 32.5-36.0 ms with 401 refreshes; a late bind plus its
    first meld 2269-2934 us.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/runs/landed_gil0.txt:1-23
  - context_compass/artifacts/meld_contract_scan_20261015/runs/landed_gil1.txt:1-23
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_before_after_landed_gil0.txt:1-13
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_before_after_before_gil0.txt:1-13
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:324-466
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:500-620
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:703-738
  IMPACT: The code and its tests are in place and green in both modes; docs, the release note, the notch, closure
    and the rebuild remain.
  NEXT: Amend src_architecture and src_components (and their indexes), the tests docs and the graph descriptors.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""


def main() -> None:
    raw = TICKET.read_bytes().decode("utf-8")
    crlf = raw.count("\r\n") > 0 and raw.count("\r\n") == raw.count("\n")
    text = raw.replace("\r\n", "\n")
    anchor = "  SCORE_0_TO_10: 9\n\n## Context / Handoff Summary\n"
    if text.count(anchor) != 1:
        raise SystemExit(f"anchor found {text.count(anchor)} times")
    text = text.replace(anchor, "  SCORE_0_TO_10: 9\n" + NOTE + "\n## Context / Handoff Summary\n")
    old_updated = [line for line in text.split("\n") if line.startswith("- Updated: ")]
    if len(old_updated) != 1:
        raise SystemExit("Updated field not unique")
    text = text.replace(old_updated[0], f"- Updated: {TS}")
    TICKET.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    print("noted", TS)


main()
