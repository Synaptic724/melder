"""Consume M0-212 (melder_0 -> melder_1, 2026-10-19T12:46:59Z) and refresh melder_1's routing (melder_1).

On mailbox_board.md: delete the M0-212 block (the one message addressed to melder_1) and set melder_1's
last_checked. On attention_board.md: clear its alert line and refresh the failed_notch_refusal row's next and
updated_at. Each anchor must match exactly once; both boards stay LF. The ticket notes carrying M0-212's content
are appended first, by append_notes_story.py. Usage: consume_m0_212_20261019.py --check|--apply
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
MAILBOX = ROOT / "mailbox_board.md"
BOARD = ROOT / "attention_board.md"
BLOCK_HEAD = "- TO: melder_1\n  FROM: melder_0\n  DATETIME: 2026-10-19T12:46:59Z\n  TYPE: HANDOFF\n"
MESSAGES_END = "<!-- END USER-DEFINED: messages -->"
ALERT = "- NEW MESSAGE for melder_1 (from melder_0, 2026-10-19T12:46:59Z)\n"
ROW_HEAD = "| failed_notch_refusal | in_progress | implementation | claude | melder_1 | none | "
NEW_NEXT = ("Write and run land_s8_docs.py (four system documents and their indexes), then the graph, the notch "
            "above 0.2.8261, the release note, the S8 and S3 closures, and the rebuild last.")


def load(path: pathlib.Path) -> str:
    """Read a board as LF text, refusing CRLF."""
    raw = path.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in %s" % path.name)
    return raw.decode("utf-8")


def main() -> None:
    """Plan both board edits; write only with --apply."""
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        raise SystemExit(__doc__)
    apply = sys.argv[1] == "--apply"
    now = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    mailbox = load(MAILBOX)
    if mailbox.count(BLOCK_HEAD) != 1:
        raise SystemExit("M0-212 head found %d times" % mailbox.count(BLOCK_HEAD))
    start = mailbox.index(BLOCK_HEAD)
    end = mailbox.index(MESSAGES_END, start)
    nxt = mailbox.find("\n- TO: ", start + 1)
    if 0 < nxt < end:
        end = nxt + 1
    block = mailbox[start:end]
    if "M0-212" not in block:
        raise SystemExit("the block is not M0-212")
    mailbox = mailbox[:start] + mailbox[end:]
    mailbox, rows = re.subn(r"^(\| melder_1 \| claude \| 2026-09-26T17:46:30Z \| )\S+( \| active \|)$",
                            r"\g<1>" + now + r"\g<2>", mailbox, flags=re.M)
    if rows != 1:
        raise SystemExit("melder_1 roster row found %d times" % rows)
    board = load(BOARD)
    if board.count(ALERT) != 1:
        raise SystemExit("alert found %d times" % board.count(ALERT))
    board = board.replace(ALERT, "")
    lines = board.split("\n")
    hits = [i for i, line in enumerate(lines) if line.startswith(ROW_HEAD)]
    if len(hits) != 1:
        raise SystemExit("failed_notch_refusal row found %d times" % len(hits))
    cells = lines[hits[0]].split(" | ")
    cells[6] = NEW_NEXT
    cells[10] = now
    lines[hits[0]] = " | ".join(cells)
    board = "\n".join(lines)
    print("mailbox: removed %d lines; board: alert cleared, row refreshed; ts %s" % (block.count("\n"), now))
    if apply:
        MAILBOX.write_bytes(mailbox.encode("utf-8"))
        BOARD.write_bytes(board.encode("utf-8"))
        if MAILBOX.read_bytes().decode("utf-8") != mailbox or BOARD.read_bytes().decode("utf-8") != board:
            raise SystemExit("read-back mismatch")
        print("applied")


main()
