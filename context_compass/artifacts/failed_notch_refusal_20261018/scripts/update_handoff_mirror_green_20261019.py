"""Rewrite the S8 story's handoff State and Next bullets in place: the rollback is green on the mirror.

Usage: update_handoff_mirror_green_20261019.py --check|--apply. The old State bullet must start the span once and
the old Next bullet must end it once; every new line stays within 120 characters; the file stays LF; the Updated
stamp moves to now.
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
STORY = ROOT / "tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md"
START = "- State: in_progress (melder_1), implementation: the owner lifted his hold and gave the go (chat 2026-10-19:\n"
END = "  the probes re-run, docs, the release note, the next free notch, closure, the rebuild last.\n"
NEW = """- State: in_progress (melder_1), implementation: the owner lifted his hold and gave the go (chat 2026-10-19:
  "it should roll back properly"; DECISION note of 2026-10-19T11:07:22Z) after the proof that the half-switch
  happens for any failing check, not only a self-dependency (MEASURE notes of 2026-10-19T10:48:29Z and 10:54:06Z).
  The rollback is built and green on the mirror (0.2.8260 plus apply_s8_rollback.py): the patch docs carry the
  shared-address refinement, the preface's line-break refusal and the dependency restore (PLAN and FACT notes of
  11:31:31Z and 11:41:48Z); S8's 25 tests and the whole tree pass with the GIL off and on (MEASURE note of
  11:59:46Z), and the probes show the refusal with nothing moved (MEASURE note of 12:04:23Z). melder_0 holds
  spellbook.py and conduit.py for S3 (0.2.8261, no rebuild) and hands them over by NOTICE when S3 lands (M0-210;
  FACT note of 11:58:42Z); S8 applies all five of its files in one pass then.
- Next: (1) on melder_0's NOTICE: apply_s8_rollback.py on the repository (check, then apply), then S8's tests and
  the whole tree on S3's tree; (2) the system documents with their indexes, the graph, the release note, the next
  free notch above 0.2.8261; (3) closure, then the rebuild last, for S3 and S8.
"""


def main() -> None:
    """Replace the State..Next span and stamp Updated; write only with --apply."""
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        raise SystemExit(__doc__)
    for line in NEW.split("\n"):
        if len(line) > 120:
            raise SystemExit("line over 120 chars: " + line)
    raw = STORY.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in the story")
    text = raw.decode("utf-8")
    if text.count(START) != 1 or text.count(END) != 1:
        raise SystemExit("anchors: start %d, end %d" % (text.count(START), text.count(END)))
    start = text.index(START)
    end = text.index(END, start) + len(END)
    text = text[:start] + NEW + text[end:]
    now = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    text, count = re.subn(r"^- Updated: \S+$", "- Updated: " + now, text, count=1, flags=re.M)
    if count != 1:
        raise SystemExit("no Updated line")
    print("lines now:", text.count("\n"), "updated:", now)
    if sys.argv[1] == "--apply":
        STORY.write_bytes(text.encode("utf-8"))
        if STORY.read_bytes().decode("utf-8") != text:
            raise SystemExit("read-back mismatch")
        print("applied")


main()
