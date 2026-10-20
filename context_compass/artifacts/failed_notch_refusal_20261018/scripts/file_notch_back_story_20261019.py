"""File STORY-2026-10-19-notch_back_keeps_outgoing_dependencies from its draft (melder_1, 2026-10-19).

The draft carries "{ts}" where the UTC timestamp goes; every line stays within 120 characters (a lone path token
excepted); the story file must not exist yet. Usage: file_notch_back_story_20261019.py --check|--apply
"""
import datetime
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DRAFT = HERE.parent / "notes" / "notch_back_story_draft_20261019.md"
STORY = ROOT / "tickets/stories/2026-10-19_notch_back_keeps_outgoing_dependencies_story.md"


def main() -> None:
    """Render the draft with the current UTC time; write only with --apply, never over an existing file."""
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        raise SystemExit(__doc__)
    if STORY.exists():
        raise SystemExit("story exists already: " + STORY.name)
    now = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    text = DRAFT.read_bytes().decode("utf-8")
    if "\r\n" in text:
        raise SystemExit("CRLF in the draft")
    text = text.replace("{ts}", now)
    for number, line in enumerate(text.split("\n"), 1):
        stripped = line.strip()
        if len(line) > 120 and not (stripped.startswith("- ") and " " not in stripped[2:]):
            raise SystemExit("line %d over 120 chars" % number)
    print("story lines:", text.count("\n"), "ts:", now)
    if sys.argv[1] == "--apply":
        STORY.write_bytes(text.encode("utf-8"))
        if STORY.read_bytes().decode("utf-8") != text:
            raise SystemExit("read-back mismatch")
        print("filed", STORY.name)


main()
