"""Append one structured note (read from a file) to a ticket's Notes, before a marker heading; update Updated.

Run from the context_compass root:
    python append_note.py <NOW> <note file> <ticket path> [marker heading]
The marker defaults to "## Context / Handoff Summary" (the heading that follows ## Notes in the task template).
"<NOW>" in the note file is replaced by NOW. The ticket's line endings are kept (bytes in, bytes out).
"""
import pathlib
import sys


def main() -> None:
    """Insert the note before the marker heading and set the ticket's Updated line to NOW."""
    now = sys.argv[1]
    note_text = pathlib.Path(sys.argv[2]).read_text(encoding="utf-8").replace("<NOW>", now)
    ticket = pathlib.Path(sys.argv[3])
    heading = sys.argv[4] if len(sys.argv) > 4 else "## Context / Handoff Summary"
    text = ticket.read_bytes().decode("utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    marker = newline + heading
    if text.count(marker) != 1:
        raise SystemExit(f"{ticket}: marker {heading!r} found {text.count(marker)} times")
    note = note_text.rstrip("\n").replace("\n", newline)
    text = text.replace(marker, newline + note + newline + marker, 1)
    lines = text.split(newline)
    updated = [i for i, line in enumerate(lines) if line.startswith("- Updated: ")]
    if len(updated) != 1:
        raise SystemExit(f"{ticket}: {len(updated)} Updated lines")
    lines[updated[0]] = "- Updated: " + now
    ticket.write_bytes(newline.join(lines).encode("utf-8"))
    long_lines = [ln for ln in note_text.splitlines() if len(ln) > 120]
    print("note appended to", ticket.name, "; lines over 120:", len(long_lines))


if __name__ == "__main__":
    main()
