"""Open S8's fix: state transition, board row, M1-45 to melder_0 and its alert line. Usage: open_fix.py --check|--apply"""
import datetime
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
STORY = ROOT / "tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md"
BOARD = ROOT / "attention_board.md"
MAILBOX = ROOT / "mailbox_board.md"
NOW = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

STE_OLD = """- transition_reason: the owner asked for proof that the half-switch happens (chat 2026-10-19; DECISION note);
  the proof resumes the story, the fix waits for his word after it. Earlier: in_progress -> blocked on his hold
  (chat 2026-10-18: "Hold" on the edit list and its refinement; DECISION note). Before that: ready -> in_progress when he scheduled the story and
  assigned melder_1 (DECISION note of 12:30:17Z).
"""
STE_NEW = """- transition_reason: the owner asked for proof that the half-switch happens (chat 2026-10-19; DECISION note of
  10:34:26Z), saw it (MEASURE notes) and gave the go for the fix: "it should roll back properly" (DECISION note of
  %s). Earlier: in_progress -> blocked on his hold (chat 2026-10-18: "Hold" on the edit list and its
  refinement; DECISION note). Before that: ready -> in_progress when he scheduled the story and assigned melder_1
  (DECISION note of 2026-10-18T12:30:17Z).
""" % NOW

ROW_PREFIX = "| failed_notch_refusal | in_progress | discovery | claude | melder_1 | none | Prove the half-switch"
ROW_NEW = ("| failed_notch_refusal | in_progress | implementation | claude | melder_1 | none | Implement the notch "
           "rollback (patch docs first) with spellbook.py, conduit.py, the error and the CCM file claimed by M1-45. "
           "| A notch whose incoming version fails its commit check is refused with nothing moved; lender and "
           "borrowers stay on the outgoing version. | The fix lands with tests, docs, notch and rebuild, or the owner "
           "redirects. | tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md | %s | "
           "REQUIRED |" % NOW)

MESSAGE = """- TO: melder_0
  FROM: melder_1
  DATETIME: %s
  TYPE: NOTICE
  CLAIM: M1-45. The owner's word (chat 2026-10-19): S8 is fixed now - "yes go ahead and fix this ... it should roll
    back properly" - then S1, S3, S2 and S5 of EPIC-2026-10-17-correctness_defects, all with melder_1, one at a
    time, each landed and rebuilt before the next (S3 comes to melder_1 too). For S8 melder_1 claims spellbook.py,
    conduit.py, spellbook_validation_error.py and change_control_manager.py (M1-31's four files) until S8 lands;
    please confirm you hold no edit in them. melder_1 notches above whatever __version__ reads at landing.
  EVIDENCE: context_compass/tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md
  ACK_REQUESTED: true
""" % NOW
ALERT = "- NEW MESSAGE for melder_0 (from melder_1, %s)\n" % NOW


def edit(path: pathlib.Path, pairs, apply: bool) -> None:
    """Apply (old, new) pairs, each old occurring once; LF only; write and read back with --apply."""
    raw = path.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in %s" % path.name)
    text = raw.decode("utf-8")
    for old, new in pairs:
        if text.count(old) != 1:
            raise SystemExit("%s: anchor found %d times: %r" % (path.name, text.count(old), old[:70]))
        text = text.replace(old, new)
    print(path.name, "ok")
    if apply:
        path.write_bytes(text.encode("utf-8"))
        if path.read_bytes().decode("utf-8") != text:
            raise SystemExit("read-back mismatch: %s" % path.name)


def main() -> None:
    """Story transition, board row and alert, mailbox message."""
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        raise SystemExit(__doc__)
    apply = sys.argv[1] == "--apply"
    edit(STORY, [(STE_OLD, STE_NEW)], apply)
    board = BOARD.read_text(encoding="utf-8")
    rows = [line for line in board.split("\n") if line.startswith(ROW_PREFIX)]
    if len(rows) != 1:
        raise SystemExit("board row found %d times" % len(rows))
    edit(BOARD, [(rows[0], ROW_NEW), ("<!-- END USER-DEFINED: alerts -->", ALERT + "<!-- END USER-DEFINED: alerts -->")],
         apply)
    edit(MAILBOX, [("<!-- END USER-DEFINED: messages -->", MESSAGE + "<!-- END USER-DEFINED: messages -->")], apply)
    print("ts", NOW, "applied" if apply else "checked")


main()
