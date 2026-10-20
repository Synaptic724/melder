"""Append one prepared Note to the lane ticket and refresh its Updated stamp.

melder_1 (synaptic_python_developer), 2026-10-17. The Note text lives in a file under ../notes/; every "{ts}" in it is
replaced by the current UTC time, which also becomes the ticket's Updated stamp. The Note is inserted at the end of
`## Notes`, just before `## Context / Handoff Summary`. Anchors must match exactly once; prose lines over 120
characters (evidence path lines excepted) refuse. Run with --check first, then --apply.

Usage: python append_note.py <note_file> --check|--apply
"""
import datetime
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
TICKET = ROOT / "tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md"


def main() -> None:
    """Validate the Note, then print what would change (--check) or write it and read it back (--apply)."""
    if len(sys.argv) != 3 or sys.argv[2] not in ("--check", "--apply"):
        raise SystemExit("usage: append_note.py <note_file> --check|--apply")
    note_file = pathlib.Path(sys.argv[1])
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    body = note_file.read_text(encoding="utf-8").replace("{ts}", ts).rstrip("\n") + "\n"
    if not body.startswith("- DATETIME: "):
        raise SystemExit("the note must start with '- DATETIME: ' - refusing")
    long = [ln for ln in body.split("\n") if len(ln) > 120 and not ln.lstrip().startswith("- ")]
    if long:
        raise SystemExit("lines over 120 chars: %r - refusing" % long)
    raw = TICKET.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("the ticket has CRLF line endings - refusing")
    text = raw.decode("utf-8")
    marker = "\n- Updated: "
    if text.count(marker) != 1:
        raise SystemExit("Updated stamp found %d times - refusing" % text.count(marker))
    start = text.index(marker) + len(marker)
    end = text.index("\n", start)
    text = text[:start] + ts + text[end:]
    heading = "\n## Context / Handoff Summary\n"
    if text.count(heading) != 1:
        raise SystemExit("handoff heading not found exactly once - refusing")
    text = text.replace(heading, "\n" + body + heading)
    print("ts", ts, "note lines", body.count("\n"), "longest", max(len(ln) for ln in body.split("\n")))
    if sys.argv[2] == "--check":
        print("check only - nothing written")
        return
    TICKET.write_bytes(text.encode("utf-8"))
    if TICKET.read_bytes().decode("utf-8") != text:
        raise SystemExit("read-back mismatch")
    print("applied and read back")


if __name__ == "__main__":
    main()
