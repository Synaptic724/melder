"""Append one structured Note to the S5 story: `python s5_append_note.py <body.txt> [ticket.md]`.

The body file holds the note from `TYPE:` on (indented two spaces, ending with SCORE_0_TO_10); the script prepends
DATETIME/AUTHOR/AUTHOR_ROLE, inserts it before `## Closure Confirmation`, bumps `- Updated:` and checks the 120-char
cap on prose lines (evidence path lines are exempt).
"""
import datetime
import pathlib
import sys

DEFAULT = "context_compass/tickets/stories/2026-10-15_managed_dispense_codegen_story.md"


def main() -> int:
    body = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8").rstrip("\n")
    ticket = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else DEFAULT)
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    note = (
        f"- DATETIME: {now}\n  AUTHOR: melder_0\n  AUTHOR_ROLE: synaptic_python_developer\n{body}\n\n"
    )
    long = [line for line in note.splitlines() if len(line) > 120 and not line.lstrip().startswith("- ")]
    if long:
        print("LINES OVER 120:", *long, sep="\n")
        return 2
    text = ticket.read_text(encoding="utf-8")
    anchor = "## Closure Confirmation"
    if text.count(anchor) != 1:
        print("anchor count", text.count(anchor))
        return 1
    text = text.replace(anchor, note + anchor)
    updated = [line for line in text.splitlines() if line.startswith("- Updated: ")]
    text = text.replace(updated[0], f"- Updated: {now}", 1)
    ticket.write_text(text, encoding="utf-8", newline="")
    print("note appended", now)
    return 0


if __name__ == "__main__":
    sys.exit(main())
