"""Record the owner's word on S9's exact edits E1-E7 (a DECISION note) before the first src edit; stamp Updated.

The story is re-read right before it is written; the anchor must occur exactly once; LF kept; read back.
Usage: record_owner_go.py --check | --apply
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
STORY_REL = "tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md"
NOW = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
NOTE = """- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner gave his word on the exact edits (chat 2026-10-18): shown E1-E7 (the check in
    `cleanup_and_remove_spell` with its message, `cleanup_spell`'s reworded message, the docstrings), the red tests
    and the mirror preview, and asked "Go ahead with these S9 edits as listed (the check, the reworded cleanup_spell
    message, the docstrings)?", he chose "Go (Recommended)" - "Apply the edits, run the tests and probe in the repo,
    then docs, release note, notch 0.2.8256, closure and rebuild; hand the files to melder_0." The ENTRY_GATE is met;
    the landing follows the contribution guide's order, closure included on this word.
  EVIDENCE: context_compass/artifacts/direct_cleanup_refusal_20261018/scripts/apply_s9_refusal.py:1-200
  IMPACT: E1-E7 are applied as previewed, nothing else in src/ beyond the notch.
  NEXT: Apply E1-E7; the tests and the probe in the repository, GIL off and on.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
""".replace("{NOW}", NOW)


def main() -> None:
    """Re-read the story, add the note before Closure Confirmation, stamp Updated; write only with --apply."""
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    script_lines = len((ROOT / "artifacts/direct_cleanup_refusal_20261018/scripts/apply_s9_refusal.py")
                       .read_text(encoding="utf-8").splitlines())
    note = NOTE.replace("apply_s9_refusal.py:1-200", "apply_s9_refusal.py:1-%d" % script_lines)
    for line in note.split("\n"):
        if len(line) > 120:
            raise SystemExit("line over 120 chars: " + line)
    path = ROOT / STORY_REL
    raw = path.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in story")
    text = raw.decode("utf-8")
    anchor = "\n## Closure Confirmation\n"
    if text.count(anchor) != 1:
        raise SystemExit("closure anchor not found once")
    text = text.replace(anchor, "\n" + note.rstrip("\n") + "\n\n## Closure Confirmation\n")
    text, count = re.subn(r"^- Updated: \S+$", "- Updated: " + NOW, text, count=1, flags=re.M)
    if count != 1:
        raise SystemExit("no Updated line")
    print("anchor found; NOW =", NOW)
    if sys.argv[1] == "--apply":
        path.write_bytes(text.encode("utf-8"))
        if path.read_bytes().decode("utf-8") != text:
            raise SystemExit("read-back mismatch")
        print("applied")


main()
