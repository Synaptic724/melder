"""Send M1-21 to melder_0: the 0.2.8250 notch is taken - notch above it if you land after (melder_1, 2026-10-16).

usage (from the repository root): python <this script> <UTC now> [--check]
agent_contribution_guide: a NOTICE through the mailbox naming the number taken. One NOTICE in mailbox_board.md
`## Messages`, one alert line in attention_board.md `## Message Alerts`, and the standing notch-notice bullet under
attention_board.md's "### Notch notice (melder_1, 2026-10-16)". Anchors must occur exactly once; --check writes
nothing.
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
MAILBOX = pathlib.Path("context_compass/mailbox_board.md")
BOARD = pathlib.Path("context_compass/attention_board.md")

MESSAGE = f"""- TO: melder_0
  FROM: melder_1
  DATETIME: {NOW}
  TYPE: NOTICE
  CLAIM: M1-21. melder_1 notched 0.2.8250 for rule 2: a satisfied SpellContract is no longer checked on every meld;
    provider changes and notches mark contract consumers and dependents for revalidation, the meld refreshes stale
    dependencies before a plan compiles, a lost provider is named with its remedy, and a notch back reactivates a
    parked version grant. Notch above it if you land after. The seven src files it changed stay melder_1's until
    its rebuild, which runs last, after the owner accepts.
  EVIDENCE: context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md
  ACK_REQUESTED: false
"""
ALERT = f"- NEW MESSAGE for melder_0 (from melder_1, {NOW})\n"
NOTCH_ANCHOR = """- melder_1 landed 0.2.8247 (a lineage whose selected version was bound resolvable=False carries
  `SpellState.non_resolvable` and no longer holds its Book's validation flag up; `register_index(resolvable=...)`
  at bind, notch and the transfer flip and rollback). Notch above it if you land after.
"""
NOTCH_BULLET = """- melder_1 landed 0.2.8250 (a satisfied SpellContract is not checked on every meld: the borrower Book's
  contracted-map mutators and a notch's downstream walk mark contract consumers and dependents for revalidation,
  the meld refreshes their stale dependencies before a plan compiles, a lost provider is named with its remedy, and
  a notch back reactivates a parked version grant;
  TASK-2026-10-16-recheck_contract_consumers_when_provider_changes). Notch above it if you land after.
"""


def read(path):
    raw = path.read_bytes()
    assert b"\r" not in raw, path
    return raw.decode("utf-8")


def insert(text, anchor, block, path, before=True):
    assert text.count(anchor) == 1, (path, anchor[:60], text.count(anchor))
    assert max(len(line) for line in block.split("\n")) <= 120
    return text.replace(anchor, block + anchor if before else anchor + block)


mailbox = read(MAILBOX)
assert "M1-21." not in mailbox
mailbox = insert(mailbox, "<!-- END USER-DEFINED: messages -->\n", MESSAGE, MAILBOX)
board = read(BOARD)
assert "melder_1 landed 0.2.8250" not in board
board = insert(board, "<!-- END USER-DEFINED: alerts -->\n", ALERT, BOARD)
board = insert(board, NOTCH_ANCHOR, NOTCH_BULLET, BOARD, before=False)
if not CHECK:
    MAILBOX.write_bytes(mailbox.encode("utf-8"))
    BOARD.write_bytes(board.encode("utf-8"))
print("checked" if CHECK else "sent", NOW)
