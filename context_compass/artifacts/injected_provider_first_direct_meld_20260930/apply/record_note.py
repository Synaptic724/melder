"""Insert one note (read from a file) before the task's handoff summary and bump its Updated stamp.

Usage: python record_note.py <context_compass root> <note file> <UTC timestamp>
The note file holds the entry with a literal {NOW} where the timestamp goes; every line must fit 120 characters.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(sys.argv[1])
NOTE = pathlib.Path(sys.argv[2]).read_text(encoding="utf-8").replace("{NOW}", sys.argv[3])
TICKET = ROOT / "tickets/tasks/2026-09-30_resolve_injected_provider_on_first_direct_meld_task.md"
long = [line for line in NOTE.split("\n") if len(line) > 120]
if long:
    raise SystemExit(f"long note lines: {long}")
raw = TICKET.read_bytes()
assert b"\r\n" not in raw
text = raw.decode("utf-8")
anchor = "## Context / Handoff Summary\n"
assert text.count(anchor) == 1
text = text.replace(anchor, NOTE.rstrip("\n") + "\n\n" + anchor)
text, n = re.subn(r"^- Updated: \S+$", f"- Updated: {sys.argv[3]}", text, count=1, flags=re.M)
assert n == 1
TICKET.write_bytes(text.encode("utf-8"))
print("noted", sys.argv[3])
