"""Append one Note to a ticket and set its Updated line.

Run from context_compass/:  python3 artifacts/correctness_defects_20261017/scripts/append_note.py <NOW> <note> <ticket>
The note file uses <NOW> for its DATETIME; it is inserted at the end of the ticket's `## Notes` section (before the
next `## ` heading), separated by one blank line. Lines over 120 characters are refused unless they hold a path.
"""
import pathlib
import re
import sys

now, note_path, ticket_path = sys.argv[1], pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
note = note_path.read_text(encoding="utf-8").replace("<NOW>", now).rstrip("\n") + "\n"
long = [line for line in note.splitlines() if len(line) > 120 and "/" not in line]
assert not long, long
raw = ticket_path.read_bytes().decode("utf-8")
nl = "\r\n" if "\r\n" in raw else "\n"
text = raw.replace(nl, "\n")
start = text.index("\n## Notes\n") + len("\n## Notes\n")
end = text.index("\n## ", start)
section = text[start:end].rstrip("\n")
text = text[:start] + section + "\n\n" + note + text[end:]
text, count = re.subn(r"(?m)^- Updated: \S+$", "- Updated: " + now, text, count=1)
assert count == 1
ticket_path.write_bytes(text.replace("\n", nl).encode("utf-8"))
print("appended", note_path.name, "to", ticket_path, "at", now)
