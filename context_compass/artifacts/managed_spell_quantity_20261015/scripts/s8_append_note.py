"""S8: append one structured note (read from a file) to a ticket before Closure Confirmation; update Updated.

Run from the repository root:
    python s8_append_note.py <NOW> <note file> <ticket path>
The ticket's line endings are kept (bytes in, bytes out).
"""
import pathlib
import sys

NOW = sys.argv[1]
NOTE = pathlib.Path(sys.argv[2]).read_text(encoding="utf-8").replace("<NOW>", NOW)
TICKET = pathlib.Path(sys.argv[3])
text = TICKET.read_bytes().decode("utf-8")
newline = "\r\n" if "\r\n" in text else "\n"
marker = newline + "## Closure Confirmation"
assert text.count(marker) == 1, text.count(marker)
note = NOTE.rstrip("\n").replace("\n", newline)
text = text.replace(marker, newline + note + newline + marker, 1)
lines = text.split(newline)
updated = [i for i, line in enumerate(lines) if line.startswith("- Updated: ")]
assert len(updated) == 1, len(updated)
lines[updated[0]] = "- Updated: " + NOW
TICKET.write_bytes(newline.join(lines).encode("utf-8"))
long_lines = [ln for ln in NOTE.splitlines() if len(ln) > 120 and not ln.lstrip().startswith(("- ", "|"))]
print("note appended to", TICKET.name, "; long prose lines:", len(long_lines))
