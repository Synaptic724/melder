"""After promoting the patch docs: one cleared artifact row for the archived folder, the seven active patch-doc rows
removed, and the ticket's Artifact Links pointed at the archive (melder_1, 2026-10-16).

usage (from context_compass/): python <this script> <UTC now> [--check]
The folder system_docs/patches/active/contract_recheck_on_notch_2026_10_16/ was moved with `mv -n` to
system_docs/patches/completed/ before this runs.
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
BOARD = pathlib.Path("artifact_board.md")
TICKET = pathlib.Path("tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md")
TICKET_REF = "tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md"
ACTIVE = "system_docs/patches/active/contract_recheck_on_notch_2026_10_16/"
DONE = "system_docs/patches/completed/contract_recheck_on_notch_2026_10_16/"
DOCS = ["architecture_patch.md", "component_patch_borrower_contracted_maps.md", "component_patch_meld_gate.md",
        "component_patch_contract_presence_report.md", "component_patch_notch_reactivation.md",
        "component_patch_dependent_walk.md", "code_description_patch_contract_recheck.md"]
CLEARED_ANCHOR = "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n"
CLEARED_ROW = (
    f"| {TICKET_REF} | {DONE} | promote_to_documentation | Promoted at landing (0.2.8250: rule 2, D1-B, D2 and D3) "
    "to src_architecture, src_components, tests_components and tests_architecture with their indexes, and to the "
    "graph (seven nodes re-authored and accepted); the seven patch docs (architecture, five component, one "
    f"code-description) archived. | {NOW} |\n"
)


def read(path):
    raw = path.read_bytes()
    assert b"\r" not in raw, path
    return raw.decode("utf-8")


assert pathlib.Path(DONE).is_dir() and not pathlib.Path(ACTIVE).exists(), "move the folder first"
assert sorted(p.name for p in pathlib.Path(DONE).iterdir()) == sorted(DOCS)

board = read(BOARD)
lines = board.split("\n")
rows = [l for l in lines if l.startswith(f"| {TICKET_REF} | {ACTIVE}")]
assert len(rows) == 7, len(rows)
assert {r.split(" | ")[1][len(ACTIVE):] for r in rows} == set(DOCS)
lines = [l for l in lines if l not in rows]
board = "\n".join(lines)
assert board.count(CLEARED_ANCHOR) == 1 and DONE not in board
board = board.replace(CLEARED_ANCHOR, CLEARED_ANCHOR + CLEARED_ROW, 1)

ticket = read(TICKET)
old_paths = "".join(f"  - {ACTIVE}{doc}\n" for doc in DOCS)
assert ticket.count(old_paths) == 1
ticket = ticket.replace(old_paths, f"  - {DONE} (the seven patch docs, archived at promotion)\n", 1)

print(("CHECK " if CHECK else "WRITE ") + str(BOARD) + f": -7 active rows, +1 cleared row")
print(("CHECK " if CHECK else "WRITE ") + str(TICKET) + ": Artifact Links point at the archive")
if not CHECK:
    BOARD.write_bytes(board.encode("utf-8"))
    TICKET.write_bytes(ticket.encode("utf-8"))
