"""Check in after the re-onboarding and consume M0-199 (melder_1), per mailbox_protocol.md.

Order: (1) refresh melder_1's check-in row (`last_checked`), the first authorized action; (2) append the FACT note
drafted in notes/s4_note_m0_199.md to the S4 story through append_notes.py's rules; (3) delete M0-199 from the
messages region; (4) clear its alert line. LF only; every write read back. Usage: --check | --apply
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
TS = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
ROW = re.compile(r"^\| melder_1 \| claude \| 2026-09-26T17:46:30Z \| (\S+) \| active \|$", re.M)
HEADER = "- TO: melder_1\n  FROM: melder_0\n  DATETIME: 2026-10-18T18:08:26Z\n"
ALERT = "- NEW MESSAGE for melder_1 (from melder_0, 2026-10-18T18:08:26Z)\n"


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
    """Run the four steps in order; write only with --apply."""
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    apply = sys.argv[1] == "--apply"
    mailbox = read_lf(MAILBOX)
    rows = ROW.findall(mailbox)
    if len(rows) != 1:
        raise SystemExit("melder_1 row found %d times" % len(rows))
    mailbox = ROW.sub("| melder_1 | claude | 2026-09-26T17:46:30Z | %s | active |" % TS, mailbox)
    print("check-in: last_checked %s -> %s" % (rows[0], TS))
    if apply:
        write_back(MAILBOX, mailbox)
        print("check-in: applied")
    note = LANE / "notes/s4_note_m0_199.md"
    mode = "--apply" if apply else "--check"
    done = subprocess.run([sys.executable, str(LANE / "scripts/append_notes.py"), str(note), mode],
                          capture_output=True, text=True)
    print(done.stdout.strip())
    if done.returncode != 0:
        raise SystemExit("append_notes failed: %s" % done.stderr.strip())
    mailbox = read_lf(MAILBOX)
    if mailbox.count(HEADER) != 1:
        raise SystemExit("M0-199 header found %d times" % mailbox.count(HEADER))
    start = mailbox.index(HEADER)
    end = mailbox.index("\n  ACK_REQUESTED: false\n", start) + len("\n  ACK_REQUESTED: false\n")
    block = mailbox[start:end]
    if "M0-199" not in block or block.count("- TO: ") != 1:
        raise SystemExit("unexpected block:\n" + block)
    mailbox = mailbox[:start] + mailbox[end:]
    print("message: M0-199 block of %d lines removed" % block.count("\n"))
    board = read_lf(BOARD)
    if board.count(ALERT) != 1:
        raise SystemExit("alert found %d times" % board.count(ALERT))
    board = board.replace(ALERT, "")
    print("alert: cleared")
    if apply:
        write_back(MAILBOX, mailbox)
        write_back(BOARD, board)
        print("message and alert: applied (%s)" % TS)


main()
