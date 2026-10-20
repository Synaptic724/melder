"""Consume M0-177 (melder_0's landing NOTICE): Notes first, then delete the message, clear its alert, update the
roster's last_checked; route the board row to the landing (melder_1).

usage (from context_compass/): python <this script> <UTC now> [--check]
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md")
BOARD = pathlib.Path("attention_board.md")
MAILBOX = pathlib.Path("mailbox_board.md")
ART = "context_compass/artifacts/meld_contract_scan_20261015"

MESSAGE = """- TO: melder_1
  FROM: melder_0
  DATETIME: 2026-10-16T16:06:21Z
  TYPE: NOTICE
  CLAIM: M0-177. TASK-2026-10-16-public_notch_target_for_staged_versions landed as 0.2.8249 and is closed:
"""
ALERT = "- NEW MESSAGE for melder_1 (from melder_0, 2026-10-16T16:06:21Z)\n"

NOTE = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: melder_0's HANDOFF (M0-177, consumed): TASK-2026-10-16-public_notch_target_for_staged_versions landed as
    0.2.8249 and is closed - `notch_spell`, `add_to_spell_index` and `remove_from_spell_index` take `spell_id=` (the
    owner's extension went into the same notch) - and conduit.py is melder_1's; rule 2's notch goes above 0.2.8249.
    melder_0 runs the rebuild last and then holds no file; its closed-anchor row says "Rebuilt last, both checks
    OK". Its FYI: spellbook.py's `_notch_spell` and `_apply_notch` docstrings say the notch claims the Book INTENT,
    while the notch strategy's seal (`_seal_scope_keys`) claims every listed spellbook and conduit and the binding
    key EXCLUSIVE - a stale docstring in a file rule 2 edits, corrected with the landing. Messaging stays the
    mailbox (codex_mcp off by the owner).
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-10-16_public_notch_target_for_staged_versions_task.md:1-20
  - src/melder/aether/spellbook/spellbook.py:3775-3838
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/notch_transaction_strategy.py:239-269
  - context_compass/attention_board.md:212-212
  IMPACT: D5's last condition is met: D3 can land, so the whole change set lands in one notch; the real-tree copy
    waits only for melder_0's rebuild to finish, so that rebuild does not pick up half of rule 2.
  NEXT: Confirm melder_0's rebuild is done, compare the baselines with the real tree, refresh the scratch copy from
    it and re-apply the build there with --check first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""


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


out = {}
text = read(TICKET)
assert "melder_0's HANDOFF (M0-177, consumed)" not in text
lines = [l for l in text.split("\n") if l.startswith("- Updated: ")]
assert len(lines) == 1, lines
text = text.replace(lines[0], f"- Updated: {NOW}", 1)
anchor = "\n## Context / Handoff Summary\n"
text = replace_once(text, anchor, "\n" + NOTE.rstrip("\n") + "\n" + anchor, TICKET)
check_lengths(text, TICKET)
out[TICKET] = text

mail = read(MAILBOX)
start = mail.index(MESSAGE)
assert mail.count(MESSAGE) == 1
end = mail.index("  ACK_REQUESTED: false\n", start) + len("  ACK_REQUESTED: false\n")
block = mail[start:end]
assert block.count("- TO: ") == 1, block
mail = mail[:start] + mail[end:]
row = [l for l in mail.split("\n") if l.startswith("| melder_1 | claude | ")]
assert len(row) == 1, row
cells = row[0].split("|")
cells[4] = f" {NOW} "
mail = replace_once(mail, row[0], "|".join(cells), MAILBOX)
out[MAILBOX] = mail

board = read(BOARD)
board = replace_once(board, ALERT, "", BOARD)
brow = [l for l in board.split("\n") if l.startswith("| meld_contract_scan |")]
assert len(brow) == 1, brow
new = replace_once(brow[0], "| conduit.py held by melder_0's notch-target task (D3's lines only; HANDOFF asked in M1-20) |",
                   "| none |", BOARD)
new = replace_once(new, "| Build D3 on the scratch copy; after melder_0 lands and hands conduit.py over, copy the build to "
                        "the real tree and run the suites. |",
                   "| Refresh the scratch copy from the real tree (melder_0 landed), re-apply the build with D3 and "
                   "run the suites; then the real tree. |", BOARD)
stamp = [c.strip() for c in brow[0].split("|")][-3]
new = replace_once(new, f"| {stamp} | REQUIRED |", f"| {NOW} | REQUIRED |", BOARD)
board = replace_once(board, brow[0], new, BOARD)
out[BOARD] = board

for path, content in out.items():
    print(("CHECK " if CHECK else "WRITE ") + str(path), len(content.split("\n")))
    if not CHECK:
        path.write_bytes(content.encode("utf-8"))
