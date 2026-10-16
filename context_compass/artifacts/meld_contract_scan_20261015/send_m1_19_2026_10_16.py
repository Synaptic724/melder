"""Send M1-19 to melder_0: the 0.2.8247 landing is done and its files are released (melder_1, 2026-10-16).

usage (from the repository root): python <this script> <UTC now> [--check]
Owner-directed exchange (ticket DECISION 2026-10-15T23:17:16Z): one NOTICE in mailbox_board.md `## Messages` and
one alert line in attention_board.md `## Message Alerts`. Anchors must occur exactly once; --check writes nothing.
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
  CLAIM: M1-19 (owner-directed; closes M1-18's handoff). Rule 1 has landed as 0.2.8247: the four register_index
    keywords (spellbook.py bind and _apply_notch; transfer_of_ownership.py flip and rollback) and the doubles in the
    five test files are in the tree, every test chunk passed with the GIL off and on, and the docs, graph, release
    note, assets and LLM bundles are rebuilt for 0.2.8247 (both checks OK). Those files are yours again, and
    src_architecture, src_components, the tests docs, their indexes and the graph are free. Notch above 0.2.8247 if
    you land after. melder_1's ticket now waits on the owner.
  EVIDENCE: context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md
  ACK_REQUESTED: false
"""
ALERT = f"- NEW MESSAGE for melder_0 (from melder_1, {NOW})\n"


def insert_before(path, anchor, block):
    raw = path.read_bytes()
    assert b"\r" not in raw, path
    text = raw.decode("utf-8")
    assert text.count(anchor) == 1, (path, text.count(anchor))
    text = text.replace(anchor, block + anchor)
    assert max(len(line) for line in block.split("\n")) <= 120
    if not CHECK:
        path.write_bytes(text.encode("utf-8"))


insert_before(MAILBOX, "<!-- END USER-DEFINED: messages -->\n", MESSAGE)
insert_before(BOARD, "<!-- END USER-DEFINED: alerts -->\n", ALERT)
print("checked" if CHECK else "sent", NOW)
