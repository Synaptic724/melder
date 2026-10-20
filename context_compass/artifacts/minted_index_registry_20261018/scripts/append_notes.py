"""Append drafted Notes to the S4 story, before "## Closure Confirmation", and stamp "- Updated:".

The drafts carry "{ts}" where the UTC timestamp goes. Every drafted line must stay within 120 characters, the
anchor must occur once, and the file must be LF. An
evidence entry that is a single path token is exempt from the cap (an unbreakable token). Usage: append_notes.py <note_file> [<note_file> ...] --check|--apply
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
STORY = ROOT / "tickets/stories/2026-10-17_minted_index_missing_from_frame_registry_story.md"
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
            # An evidence entry that is one unbreakable path token may run past the cap.
            if stripped.startswith("- ") and " " not in stripped[2:]:
                continue
            if len(line) > 120:
                raise SystemExit("%s: line over 120 chars (%d): %s" % (name, len(line), line))
        blocks.append(draft.rstrip("\n") + "\n")
    raw = STORY.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in the story")
    text = raw.decode("utf-8")
    if text.count(ANCHOR) != 1:
        raise SystemExit("anchor found %d times" % text.count(ANCHOR))
    insert = "".join("\n" + block for block in blocks)
    text = text.replace(ANCHOR, insert + ANCHOR)
    text, count = re.subn(r"^- Updated: \S+$", "- Updated: " + now, text, count=1, flags=re.M)
    if count != 1:
        raise SystemExit("no Updated line")
    print("notes:", len(blocks), "lines now:", text.count("\n"), "ts:", now)
    if apply:
        STORY.write_bytes(text.encode("utf-8"))
        if STORY.read_bytes().decode("utf-8") != text:
            raise SystemExit("read-back mismatch")
        print("applied")


main()
