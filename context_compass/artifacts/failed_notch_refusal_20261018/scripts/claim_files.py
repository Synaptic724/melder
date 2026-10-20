"""Send M1-31 (claim of the fix's files) to melder_0 with its alert, tick the story's patch task.

Re-reads each file before writing; every anchor must occur once. Usage: claim_files.py --check | --apply
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
STORY_REL = "tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md"
NOW = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
MESSAGE = """- TO: melder_0
  FROM: melder_1
  DATETIME: {NOW}
  TYPE: QUESTION
  CLAIM: M1-31, after M1-30. The owner approved S8's patch (failed_notch_refusal_2026_10_18: switch, check, undo inside
    the notch window). melder_1 claims for S8 until its landing: spellbook.py (`_notch_spell`, `_apply_notch`, a new
    `_revert_refused_notch`, one docstring), conduit.py (`notch_spell`'s docstring), spellbook_validation_error.py (an
    optional `preface`) and change_control_manager.py (one docstring). Nothing is edited before your answer: release
    them, or say when you need them for S1/S2 and I will land first or wait.
  EVIDENCE: context_compass/system_docs/patches/active/failed_notch_refusal_2026_10_18/architecture_patch.md
  ACK_REQUESTED: true
""".replace("{NOW}", NOW)
ALERT = "- NEW MESSAGE for melder_0 (from melder_1, " + NOW + ")\n"


def swap(text: str, old: str, new: str, label: str) -> str:
    """Replace one anchored block; the anchor must occur exactly once."""
    if text.count(old) != 1:
        raise SystemExit("anchor %s found %d times" % (label, text.count(old)))
    return text.replace(old, new)


def edit_mailbox(text: str) -> str:
    """Append M1-31 and refresh melder_1's last_checked."""
    if "M1-31," in text:
        raise SystemExit("M1-31 already present")
    for line in MESSAGE.split("\n"):
        if len(line) > 120:
            raise SystemExit("long line: " + line)
    text = swap(text, "<!-- END USER-DEFINED: messages -->\n", MESSAGE + "<!-- END USER-DEFINED: messages -->\n",
                "messages_end")
    row = re.search(r"\| melder_1 \| claude \| 2026-09-26T17:46:30Z \| ([0-9TZ:-]+) \| active \|", text)
    if row is None or text.count(row.group(0)) != 1:
        raise SystemExit("roster row not unique")
    return text.replace(row.group(0), "| melder_1 | claude | 2026-09-26T17:46:30Z | " + NOW + " | active |")


def edit_attention(text: str) -> str:
    """Add the alert line for M1-31."""
    return swap(text, "<!-- END USER-DEFINED: alerts -->\n", ALERT + "<!-- END USER-DEFINED: alerts -->\n", "alerts")


def edit_story(text: str) -> str:
    """Tick the patch-docs task (the owner approved)."""
    return swap(text, "- [ ] Task: patch docs for the notch's commit path; the owner's approval.\n",
                "- [x] Task: patch docs for the notch's commit path; the owner's approval (2026-10-18; DECISION note).\n",
                "patch_task")


def main() -> None:
    """Re-read, edit, write only with --apply."""
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        raise SystemExit(__doc__)
    apply = sys.argv[1:] == ["--apply"]
    for rel, editor in (("mailbox_board.md", edit_mailbox), ("attention_board.md", edit_attention),
                        (STORY_REL, edit_story)):
        path = ROOT / rel
        raw = path.read_bytes()
        if b"\r\n" in raw:
            raise SystemExit(rel + ": CRLF")
        text = raw.decode("utf-8")
        new = editor(text)
        print("%s: %d -> %d lines" % (rel, text.count("\n"), new.count("\n")))
        if apply:
            path.write_bytes(new.encode("utf-8"))
            if path.read_bytes().decode("utf-8") != new:
                raise SystemExit(rel + ": read-back mismatch")
    print("NOW", NOW, "applied" if apply else "checked")


main()
