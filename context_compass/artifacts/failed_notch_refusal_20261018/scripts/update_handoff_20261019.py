"""Rewrite the S8 story's handoff State and Next bullets in place (the one current resume view).

Usage: update_handoff_20261019.py --check|--apply. The old State bullet must start the anchor once and the old Next
bullet must end it once; every new line stays within 120 characters; the file stays LF.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
STORY = ROOT / "tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md"
START = "- State: blocked (melder_1): on hold by the owner since 2026-10-18T13:38:59Z (DECISION note)."
END = "  was made, so nothing is owed meanwhile.\n"
NEW = """- State: in_progress (melder_1), implementation: the owner lifted his hold and gave the go (chat 2026-10-19:
  "it should roll back properly"; DECISION note of 2026-10-19T11:07:22Z) after the proof that the half-switch
  happens for any failing check, not only a self-dependency (MEASURE notes of 2026-10-19T10:48:29Z and 10:54:06Z).
  The patch docs stand with one refinement to add - a shared address is left to the reversal's promotion (FACT
  note of 2026-10-18T13:11:11Z). Red set on 0.2.8260: 20 failed, 1 passed, the GIL off and on. melder_0 is
  editing spellbook.py, conduit.py and conduit_ward.py for S3 (CONFLICT notes of 2026-10-19), so S8 is built and
  tested in the mirror on 0.2.8260 and applied by anchored edits after melder_0 lands; M1-45, the four-file
  claim, waits for melder_0's answer.
- Next: (1) the refinement and the preface's line-break refusal in the patch docs; (2) the rollback in the
  mirror, green with the GIL off and on, then the whole tree; (3) on melder_0's hand-back: the repository edits,
  the probes re-run, docs, the release note, the next free notch, closure, the rebuild last.
"""


def main() -> None:
    """Replace the State..Next span; write only with --apply."""
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        raise SystemExit(__doc__)
    for line in NEW.split("\n"):
        if len(line) > 120:
            raise SystemExit("line over 120 chars: " + line)
    raw = STORY.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in the story")
    text = raw.decode("utf-8")
    if text.count(START) != 1:
        raise SystemExit("start anchor found %d times" % text.count(START))
    begin = text.index(START)
    end = text.index(END, begin)
    if text.count(END) != 1:
        raise SystemExit("end anchor found %d times" % text.count(END))
    end += len(END)
    text = text[:begin] + NEW + text[end:]
    print("replaced", end - begin, "chars with", len(NEW))
    if sys.argv[1] == "--apply":
        STORY.write_bytes(text.encode("utf-8"))
        if STORY.read_bytes().decode("utf-8") != text:
            raise SystemExit("read-back mismatch")
        print("applied")


main()
