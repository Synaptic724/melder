"""Refresh the ticket's resume view, the board row and two artifact rows after the scratch validation (melder_1)."""
import pathlib
import sys

NOW = sys.argv[1]
CC = pathlib.Path("context_compass")
T = CC / "tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md"
TICKET = "tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md"

SUMMARY = f"""## Context / Handoff Summary
In progress ({NOW}). Rule 1, Option A (approved): `register_index` writes `SpellState.non_resolvable`
from the caller's capability and mirrors it in the registry's published set `non_resolvable_index_ids`, which
RiskManager's Book-flag distillation reads with one subset test; patch docs under
system_docs/patches/active/meld_state_gate_2026_10_15/ (amended for the set and the five test doubles).
Built and validated on the scratch tree /tmp/cc_res/nonres/tree only (base 0.2.8246; nothing in the real tree):
apply_state_model.py and apply_risk_manager.py write the four melder_1 files, apply_call_sites.py the four call-site
keywords and five test doubles (CRLF kept where a file was CRLF); tests A (34), B (11), C (the stub) and D (9) exist
in the scratch tree only. Every chunk is green with the GIL off and on; mutations of each part fail tests; probe: a
warm meld with a definition 14-16 us -> 0.24-0.77 us, nothing else slower beyond noise (a refresh 2 -> 36 us at 1000
definitions). The three scripts' --check pass on the real tree.
Holds: the call sites and five test files are melder_0's - handoff through the owner; items (2)-(3) (the contract
check; a borrower SpellContract consumer still costs about 2 ms a meld) await the owner. Not run: the asset and bundle
checks (landing only).
Next: (1) the owner's handoff answer; (2) landing: --check, the scripts on the real tree, A/B/D and the stub copied in
(test_risk_manager.py kept CRLF), the suites with the GIL off and on; (3) src_architecture, src_components, the
SpellState graph descriptor, the release-note entry, the notch, closure, rebuild last.
"""


def one(text: str, old: str, new: str) -> str:
    """Replace exactly one occurrence."""
    assert text.count(old) == 1, (text.count(old), old[:60])
    return text.replace(old, new, 1)


def main() -> None:
    """Rewrite the resume view in place; move the board row and two artifact rows."""
    for line in SUMMARY.splitlines():
        assert len(line) <= 120, line
    text = T.read_text(encoding="utf-8")
    start = text.index("## Context / Handoff Summary\n")
    end = text.index("\n## Project-Specific Additions")
    text = text[:start] + SUMMARY + text[end:]
    s = text.index("- Updated: ")
    e = text.index("\n", s)
    text = text[:s] + f"- Updated: {NOW}" + text[e:]
    T.write_bytes(text.encode("utf-8"))

    board = CC / "attention_board.md"
    bt = board.read_text(encoding="utf-8")
    i = bt.index("| meld_contract_scan | in_progress |")
    j = bt.index("\n", i)
    cells = bt[i:j].split(" | ")
    assert cells[0] == "| meld_contract_scan" and cells[9] == TICKET, cells
    cells[2] = "validation"
    cells[5] = "owner handoff of melder_0's call sites"
    cells[6] = ("Owner: hand over melder_0's four call-site lines and five test doubles (or melder_0 applies them); "
                "then land.")
    cells[10] = NOW
    bt = bt[:i] + " | ".join(cells) + bt[j:]
    board.write_bytes(bt.encode("utf-8"))

    art = CC / "artifact_board.md"
    at = art.read_text(encoding="utf-8")
    at = one(at,
             "| The four register_index keywords in melder_0's files (bind, notch, transfer flip and rollback); pending the "
             "handoff. | 2026-10-15T21:01:43Z | REQUIRED |",
             "| The four register_index keywords in melder_0's files (bind, notch, transfer flip and rollback) and the five "
             f"test doubles they reach; pending the handoff. | {NOW} | REQUIRED |")
    at = one(at,
             "| Git-history and ticket-search logs, the gate probes and their runs (the predecessor's trace), and the open "
             "and closure scripts; the fix lane's probes join them. | 2026-10-15T18:46:58Z | REQUIRED |",
             "| Git-history and ticket-search logs, the gate probes and their runs (the predecessor's trace), the open and "
             "closure scripts; the fix lane's apply scripts (apply_*.py, CRLF-preserving), probes (design, borrower "
             f"notch-back, before/after), suite, mutation and probe runs (runs/), and Note scripts. | {NOW} | REQUIRED |")
    art.write_bytes(at.encode("utf-8"))
    print("refreshed", NOW)


if __name__ == "__main__":
    main()
