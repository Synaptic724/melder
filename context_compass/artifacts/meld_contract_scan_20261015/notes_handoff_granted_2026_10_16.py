"""Record melder_0's handoff answer in the task's Notes, refresh the resume view and route the board row.

Usage (from the repository's context_compass folder): python <this script> <UTC timestamp>
Every edit is an exact-text replacement that refuses a missing or repeated anchor; line endings are kept.
"""
import pathlib
import sys

TS = sys.argv[1]
TICKET = pathlib.Path("tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md")
BOARD = pathlib.Path("attention_board.md")

NOTE = f"""- DATETIME: {TS}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: melder_0 answered M1-18 yes to all three (relayed by the owner in chat 2026-10-16 and recorded in its
    epic's DECISION note; no M0-175 was posted in the mailbox). (1) melder_1 makes the four `register_index` keyword
    edits (spellbook.py bind and notch, transfer_of_ownership.py flip and rollback) and the five test doubles itself,
    as one landing; melder_0 leaves those files untouched until melder_1 reports that it has landed. (2) melder_1
    adds its own `##` section to release_docs/next_version_release.md, takes the next notch from `__version__` at
    landing (0.2.8246 at 00:46Z) and runs the rebuild last. (3) src_architecture, src_components, the tests docs,
    their indexes and the graph are free now (S7's edits are finished). The owner confirmed this reply is the one to
    act on. The handoff hold is cleared; items (2)-(3) of the design request (the contract check) stay with the owner.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:1387-1407
  - context_compass/mailbox_board.md:1028-1038
  IMPACT: melder_1 holds the landing window on the four src files and five test files until its M1-19 notice; the
    landing is one change set with one notch.
  NEXT: Re-run the three apply scripts' --check against the real tree, then apply them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

OLD_HOLDS = """Holds: the call sites and five test files are melder_0's - handoff through the owner; items (2)-(3) (the contract
check; a borrower SpellContract consumer still costs about 2 ms a meld) await the owner. Not run: the asset and bundle
checks (landing only).
Next: (1) the owner's handoff answer; (2) landing: --check, the scripts on the real tree, A/B/D and the stub copied in
(test_risk_manager.py kept CRLF), the suites with the GIL off and on; (3) src_architecture, src_components, the
SpellState graph descriptor, the release-note entry, the notch, closure, rebuild last.
"""
NEW_HOLDS = """Holds: none on custody - melder_0 granted the landing window on the four call sites and five test files and freed
the system docs and the graph (epic DECISION 2026-10-16T00:21:04Z); it waits for melder_1's landing notice. Items
(2)-(3) (the contract check; a borrower SpellContract consumer still costs about 2 ms a meld) await the owner. Not
run: the asset and bundle checks (landing only).
Next: (1) landing: --check, the scripts on the real tree, A/B/D and the stub copied in (test_risk_manager.py kept
CRLF), the suites with the GIL off and on; (2) src_architecture, src_components, the tests docs, the SpellState graph
descriptor, the release-note entry, the notch, closure, rebuild last; (3) the M1-19 landing notice to melder_0.
"""

OLD_ROW = ("| meld_contract_scan | in_progress | validation | claude | melder_1 | owner handoff of melder_0's call sites "
           "| Owner: hand over melder_0's four call-site lines and five test doubles (or melder_0 applies them); then land. ")
NEW_ROW = ("| meld_contract_scan | in_progress | implementation | claude | melder_1 | none "
           "| Land rule 1: the three apply scripts on the real tree, the tests copied in, every chunk with the GIL off and "
           "on, then docs, release note, notch, closure and the rebuild last. ")
OLD_ROW_TAIL = "| tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md | 2026-10-15T22:36:32Z | REQUIRED |"
NEW_ROW_TAIL = f"| tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md | {TS} | REQUIRED |"


def edit(path, pairs):
    raw = path.read_bytes().decode("utf-8")
    crlf = raw.count("\r\n") > 0 and raw.count("\r\n") == raw.count("\n")
    text = raw.replace("\r\n", "\n")
    for old, new in pairs:
        count = text.count(old)
        if count != 1:
            raise SystemExit(f"{path}: anchor found {count} times: {old[:80]!r}")
        text = text.replace(old, new)
    path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    print("edited", path, "(CRLF kept)" if crlf else "(LF)")


edit(TICKET, [
    ("- Updated: 2026-10-15T23:17:16Z\n", f"- Updated: {TS}\n"),
    ("\n## Context / Handoff Summary\n", "\n" + NOTE + "\n## Context / Handoff Summary\n"),
    ("In progress (2026-10-15T22:36:32Z).", f"In progress ({TS})."),
    (OLD_HOLDS, NEW_HOLDS),
])
edit(BOARD, [(OLD_ROW, NEW_ROW), (OLD_ROW_TAIL, NEW_ROW_TAIL)])
