"""S6: append one structured note (read from a file) to the S6 story before Closure Confirmation; update Updated.

Run from the repository root: python s6_append_note.py <NOW> <note file>
"""
import pathlib
import sys

NOW = sys.argv[1]
NOTE = pathlib.Path(sys.argv[2]).read_text(encoding="utf-8").replace("<NOW>", NOW)
STORY = pathlib.Path("context_compass/tickets/stories/2026-10-15_managed_ownership_transfer_story.md")
text = STORY.read_text(encoding="utf-8")
marker = "\n## Closure Confirmation"
assert text.count(marker) == 1
text = text.replace(marker, "\n" + NOTE.rstrip("\n") + "\n" + marker, 1)
lines = text.split("\n")
updated = [i for i, line in enumerate(lines) if line.startswith("- Updated: ")]
assert len(updated) == 1
lines[updated[0]] = "- Updated: " + NOW
text = "\n".join(lines)
STORY.write_text(text, encoding="utf-8")
long_lines = [ln for ln in NOTE.splitlines() if len(ln) > 120 and not ln.lstrip().startswith(("- ", "|"))]
print("note appended; long prose lines:", len(long_lines))
