"""Insert one note (read from a file) before a ticket's handoff summary and bump its Updated stamp.

Usage: python add_note.py <ticket path> <note file> <UTC timestamp>
The note file holds the entry with a literal {NOW} where the timestamp goes; every line must fit 120 characters.
Keeps the ticket's line endings (CRLF or LF).
"""
import pathlib
import re
import sys

TICKET = pathlib.Path(sys.argv[1])
NOTE = pathlib.Path(sys.argv[2]).read_text(encoding="utf-8").replace("{NOW}", sys.argv[3])
long = [line for line in NOTE.split("\n") if len(line) > 120
        and not (line.strip().startswith("- ") and " " not in line.strip()[2:])]  # unbreakable paths
if long:
    raise SystemExit(f"long note lines: {long}")
raw = TICKET.read_bytes()
crlf = b"\r\n" in raw
text = raw.decode("utf-8").replace("\r\n", "\n")
anchor = "\n## Context / Handoff Summary\n"
if text.count(anchor) != 1:
    raise SystemExit("handoff anchor not unique")
head, tail = text.split(anchor)
head = head.rstrip("\n") + "\n\n" if not head.endswith("## Notes") else head + "\n"
text = head + NOTE.rstrip("\n") + "\n" + anchor + tail
text, n = re.subn(r"^- Updated: \S+$", f"- Updated: {sys.argv[3]}", text, count=1, flags=re.M)
if n != 1:
    raise SystemExit("no Updated line")
TICKET.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
print("noted", sys.argv[3])
