"""Record rule 2's graph pass and the patch promotion; resync the handoff Next, its Patch line and the board row
(melder_1, 2026-10-16).

usage (from context_compass/): python <this script> <UTC now> [--check]
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md")
BOARD = pathlib.Path("attention_board.md")
ART = "context_compass/artifacts/meld_contract_scan_20261015"
PATCH = "context_compass/system_docs/patches/completed/contract_recheck_on_notch_2026_10_16"

NOTES = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The graph and the patch promotion carry the landing. `extract_graph.py --strict` on Python 3.14.7t: 591
    descriptors, 1227 nodes, 451 of 451 `specializes` targets resolved, skipped 0, new 0, orphaned 0. The authored
    prose of the seven nodes this change touches was re-read against their source and edited where it described the
    retired scan or missed a new duty (`graph_semantics_rule2_2026_10_16.py`, authored fields only, each edit
    refusing an unexpected old value): SpellSystemStates (the binding key per lineage and the downstream walk;
    `_binding_key_by_index` owned), Meld (the recheck replaces the scan's signature read; the catch-up),
    ContractProviderPresenceStrategy (the snapshot walk; the remedy), SpellbookValidationError (a gating warning
    shown as the reason), Spellbook (the contracted-map marks; the notch's binding key and walk), Conduit
    (`_activate_borrowed_spell`), ConduitWard (a version grant's copy); then all seven were accepted. Walker:
    SEMANTICS_STALE 148 -> 141 and AUTHORED 1070 -> 1077 of 1232 nodes (9 unsemantic, 5 retired); the 141 left
    predate this landing, and the packages of the seven changed files that still show a stale node show only nodes
    outside them. `assemble_graph.py`: src_graph.md 28075 lines, 591 sections, 1227 nodes, 1415 edges, index 618
    lines, every range verified against its header; `--check` the same with no writes. The seven patch docs
    (architecture, five component, one code description) moved with `mv -n` from patches/active/ to
    patches/completed/contract_recheck_on_notch_2026_10_16/; the artifact board's seven active patch rows became one
    cleared promote_to_documentation row, and the ticket's Artifact Links name the archived folder.
  EVIDENCE:
  - {ART}/runs/extract_graph_rule2_2026_10_16.txt:1-46
  - {ART}/runs/graph_walker_report_rule2_2026_10_16.txt:1-111
  - {ART}/graph_semantics_rule2_2026_10_16.py:1-140
  - {ART}/runs/graph_accept_rule2_2026_10_16.txt:1-9
  - {ART}/runs/graph_walker_report_after_accept_rule2_2026_10_16.txt:1-109
  - {ART}/runs/assemble_graph_rule2_2026_10_16.txt:1-4
  - {ART}/runs/assemble_graph_check_rule2_2026_10_16.txt:1-4
  - {ART}/sync_patch_promotion_rule2_2026_10_16.py:1-58
  - {PATCH}/architecture_patch.md:1-224
  - context_compass/artifact_board.md:103-103
  IMPACT: Every documentation surface the patch framework names is current; what remains is the notch, NOTICE M1-21,
    the release-note entry, the owner's acceptance, closure and the rebuild last.
  NEXT: Read `__version__` again and notch it to 0.2.8250; send NOTICE M1-21 to melder_0 through the mailbox.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

OLD_PATCH = """Patch: system_docs/patches/active/contract_recheck_on_notch_2026_10_16/
(architecture, five component patches, the code description)."""
NEW_PATCH = """Patch: system_docs/patches/completed/contract_recheck_on_notch_2026_10_16/
(architecture, five component patches, the code description; archived at promotion)."""

OLD_NEXT_START = "Next: rule 2 with D3 is applied to the real tree"
OLD_NEXT_END = "\n\n## Project-Specific Additions"
NEW_NEXT = """Next: rule 2 with D3 is applied to the real tree - 18 files, byte-identical to the fresh tree that passed every
suite chunk with the GIL off and on; the race test is xfail naming
TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout (the owner's decision B). The four system docs
and their indexes (rubric 83 / 83 / 83 / 77, band B) and the graph (seven nodes re-authored and accepted,
reassembled) carry it, and the patch docs are archived. Remaining, in the turn-in order: (1) one notch above
0.2.8249 and NOTICE M1-21; (2) the release-note entry, its example verified on the tree; (3) the owner's
acceptance, closure and board sync, then the rebuild and its checks last."""

ROW_PREFIX = "| meld_contract_scan | in_progress | implementation | claude | melder_1 | none | "
ROW_NEXT = ("Notch to 0.2.8250 and send NOTICE M1-21; then the release-note entry, owner acceptance, closure, "
            "rebuild last.")


def read(path):
    raw = path.read_bytes()
    assert b"\r" not in raw, path
    return raw.decode("utf-8")


def replace_once(text, old, new, path):
    assert text.count(old) == 1, (str(path), old[:80], text.count(old))
    return text.replace(old, new)


def check_lengths(text, path):
    bad = [l for l in text.split("\n")
           if len(l) > 120 and not l.startswith("|") and not (l.startswith("  - ") and " " not in l[4:])]
    assert not bad, (path, bad)


text = read(TICKET)
assert "The graph and the patch promotion carry the landing." not in text
lines = [l for l in text.split("\n") if l.startswith("- Updated: ")]
assert len(lines) == 1, lines
text = text.replace(lines[0], f"- Updated: {NOW}", 1)
anchor = "\n## Context / Handoff Summary\n"
text = replace_once(text, anchor, "\n" + NOTES.rstrip("\n") + "\n" + anchor, TICKET)
text = replace_once(text, OLD_PATCH, NEW_PATCH, TICKET)
i = text.index(OLD_NEXT_START)
j = text.index(OLD_NEXT_END, i)
assert text.count(OLD_NEXT_START) == 1
text = text[:i] + NEW_NEXT + text[j:]
check_lengths(text, TICKET)

board = read(BOARD)
rows = [l for l in board.split("\n") if l.startswith(ROW_PREFIX)]
assert len(rows) == 1, rows
cells = rows[0].split(" | ")
assert cells[9] == "tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md", cells[9]
cells[6] = ROW_NEXT
cells[10] = NOW
board = board.replace(rows[0], " | ".join(cells), 1)

print(("CHECK " if CHECK else "WRITE ") + str(TICKET), len(text.split("\n")))
print(("CHECK " if CHECK else "WRITE ") + str(BOARD))
if not CHECK:
    TICKET.write_bytes(text.encode("utf-8"))
    BOARD.write_bytes(board.encode("utf-8"))
