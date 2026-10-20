"""Consume one mailbox message addressed to melder_1, per mailbox_protocol.md (melder_1; S4 lane).

Order: (1) append the drafted note (append_notes.py's rules) to the S4 story - the durable copy first; (2) delete
the message block (header TO: melder_1 / FROM / DATETIME, through its ACK_REQUESTED line) from the messages region;
(3) clear its alert line; (4) refresh melder_1's `last_checked`. LF only, each write read back.
Usage: consume_message.py --from <agent> --datetime <ISO> --id <M0-n> --note <draft> --check|--apply
"""
import datetime
import pathlib
import re
import subprocess
import sys

LANE = pathlib.Path(__file__).resolve().parents[1]
ROOT = pathlib.Path(__file__).resolve().parents[3]
MAILBOX = ROOT / "mailbox_board.md"
BOARD = ROOT / "attention_board.md"
ROW = re.compile(r"^\| melder_1 \| claude \| 2026-09-26T17:46:30Z \| (\S+) \| active \|$", re.M)


def read_lf(path: pathlib.Path) -> str:
    """Return the file's text, refusing CRLF."""
    raw = path.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in %s" % path.name)
    return raw.decode("utf-8")


def write_back(path: pathlib.Path, text: str) -> None:
    """Write `text` and verify it by reading it back."""
    path.write_bytes(text.encode("utf-8"))
    if path.read_bytes().decode("utf-8") != text:
        raise SystemExit("read-back mismatch: %s" % path.name)


def main() -> None:
    """Parse the arguments, then run the four steps; write only with --apply."""
    args = sys.argv[1:]
    if len(args) != 9 or args[0] != "--from" or args[2] != "--datetime" or args[4] != "--id" or args[6] != "--note" \
            or args[8] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    sender, stamp, message_id, note, mode = args[1], args[3], args[5], args[7], args[8]
    apply = mode == "--apply"
    header = "- TO: melder_1\n  FROM: %s\n  DATETIME: %s\n" % (sender, stamp)
    alert = "- NEW MESSAGE for melder_1 (from %s, %s)\n" % (sender, stamp)
    mailbox = read_lf(MAILBOX)
    if mailbox.count(header) != 1:
        raise SystemExit("message header found %d times" % mailbox.count(header))
    start = mailbox.index(header)
    end = mailbox.index("\n  ACK_REQUESTED: ", start)
    end = mailbox.index("\n", end + 1) + 1
    block = mailbox[start:end]
    if message_id not in block or block.count("- TO: ") != 1:
        raise SystemExit("unexpected block:\n" + block)
    board = read_lf(BOARD)
    if board.count(alert) != 1:
        raise SystemExit("alert found %d times" % board.count(alert))
    done = subprocess.run([sys.executable, str(LANE / "scripts/append_notes.py"), note, mode],
                          capture_output=True, text=True)
    print(done.stdout.strip())
    if done.returncode != 0:
        raise SystemExit("append_notes failed: %s" % done.stderr.strip())
    now = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    mailbox = read_lf(MAILBOX)
    start = mailbox.index(header)
    mailbox = mailbox[:start] + mailbox[start + len(block):]
    if len(ROW.findall(mailbox)) != 1:
        raise SystemExit("melder_1 row not found once")
    mailbox = ROW.sub("| melder_1 | claude | 2026-09-26T17:46:30Z | %s | active |" % now, mailbox)
    board = read_lf(BOARD).replace(alert, "")
    print("%s: block of %d lines removed, alert cleared, last_checked %s" % (message_id, block.count("\n"), now))
    if apply:
        write_back(MAILBOX, mailbox)
        write_back(BOARD, board)
        print("applied")


main()
