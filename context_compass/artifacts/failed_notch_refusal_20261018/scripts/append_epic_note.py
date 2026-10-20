"""Append drafted Notes to EPIC-2026-10-17-correctness_defects, before "## Closure Confirmation", and stamp
"- Updated:". Same rules as append_notes.py: "{ts}" is the UTC timestamp, lines within 120 characters (an evidence
entry that is one path token is exempt), the anchor once, LF only. Usage: append_epic_note.py <note_file> ...
--check|--apply
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
EPIC = ROOT / "tickets/epics/2026-10-17_correctness_defects_epic.md"
ANCHOR = "\n## Closure Confirmation\n"


def main() -> None:
    """Insert the notes in the order given; write only with --apply."""
    args = sys.argv[1:]
    if not args or args[-1] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    apply = args[-1] == "--apply"
    now = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    blocks = []
    for name in args[:-1]:
        draft = pathlib.Path(name).read_text(encoding="utf-8").replace("{ts}", now)
        for line in draft.split("\n"):
            stripped = line.strip()
            if stripped.startswith("- ") and " " not in stripped[2:]:
                continue
            if len(line) > 120:
                raise SystemExit("%s: line over 120 chars (%d): %s" % (name, len(line), line))
        blocks.append(draft.rstrip("\n") + "\n")
    raw = EPIC.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in the epic")
    text = raw.decode("utf-8")
    if text.count(ANCHOR) != 1:
        raise SystemExit("anchor found %d times" % text.count(ANCHOR))
    text = text.replace(ANCHOR, "".join("\n" + block for block in blocks) + ANCHOR)
    text, count = re.subn(r"^- Updated: \S+$", "- Updated: " + now, text, count=1, flags=re.M)
    if count != 1:
        raise SystemExit("no Updated line")
    print("notes:", len(blocks), "lines now:", text.count("\n"), "ts:", now)
    if apply:
        EPIC.write_bytes(text.encode("utf-8"))
        if EPIC.read_bytes().decode("utf-8") != text:
            raise SystemExit("read-back mismatch")
        print("applied")


main()
