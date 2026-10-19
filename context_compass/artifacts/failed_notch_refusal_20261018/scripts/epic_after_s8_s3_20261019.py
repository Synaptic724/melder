"""The epic after S8 and S3 are turned in (melder_1): both story bullets checked with their landing, the handoff's
State and Next refreshed, and the epic's board row's next and updated_at. Each old text occurs exactly once; LF.
Run after append_epic_note.py adds the FACT note. Usage (repository root): epic_after_s8_s3_20261019.py --check|--apply
"""
import datetime
import pathlib
import sys

CC = pathlib.Path("context_compass")
EPIC = CC / "tickets/epics/2026-10-17_correctness_defects_epic.md"
BOARD = CC / "attention_board.md"
TS = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
EPIC_EDITS = [
    (
        "  its copy and id with index-link borrowers, past their own unlink (sweep A2). Landed at 0.2.8261 by\n"
        "  melder_0 (every cleanup_spell door releases the version's contracts first), then handed to melder_1 with\n"
        "  the epic on the owner's word (2026-10-19); the rebuild rides S8's landing, the turn-in waits for the owner.\n",
        "  its copy and id with index-link borrowers, past their own unlink (sweep A2). Landed at 0.2.8261 by\n"
        "  melder_0 (every cleanup_spell door releases the version's contracts first), then handed to melder_1 with\n"
        "  the epic on the owner's word; turned in by melder_1 on 2026-10-19, in tickets/stories/completed/; the\n"
        "  rebuild comes last in melder_1's pass.\n",
    ),
    ("- [ ] Story: STORY-2026-10-17-parked_cleanup_leaves_borrower_copies",
     "- [x] Story: STORY-2026-10-17-parked_cleanup_leaves_borrower_copies"),
    (
        "  validation fails keeps its switch and leaves its borrowers behind (sweep A9). melder_1's (the owner-approved\n"
        "  patch failed_notch_refusal_2026_10_18; M1-30, M1-31); the owner lifted its hold on 2026-10-19 and it is in\n"
        "  progress with melder_1, S1, S2 and S5 to follow with it one at a time (M1-45, M1-46).\n",
        "  validation fails keeps its switch and leaves its borrowers behind (sweep A9). Landed by melder_1 at\n"
        "  0.2.8262 (the owner-approved patch failed_notch_refusal_2026_10_18): a notch whose incoming version fails\n"
        "  its structural check is refused with nothing moved, its borrowers untouched; turned in 2026-10-19, in\n"
        "  tickets/stories/completed/.\n",
    ),
    ("- [ ] Story: STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers",
     "- [x] Story: STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers"),
    (
        "S8 in progress with melder_1 (M1-45); S7 done\n"
        "  (0.2.8260; M1-44); S3 in progress with melder_0 on the owner's go (2026-10-19); S1, S2 and S5 go to\n"
        "  melder_1 after S8, one at a time,",
        "S8 done (0.2.8262; turned in\n"
        "  2026-10-19); S7 done (0.2.8260; M1-44); S3 done (0.2.8261, melder_0; turned in by melder_1 2026-10-19);\n"
        "  S1, S2 and S5 go to melder_1 after S8, one at a time,",
    ),
    ("  STORY-2026-10-17-parked_cleanup_leaves_borrower_copies (p2),\n",
     "  STORY-2026-10-17-parked_cleanup_leaves_borrower_copies (p2; done: landed at 0.2.8261, turned in 2026-10-19),\n"),
    ("  STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers (p2; answered: refused with nothing moved),\n",
     "  STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers (p2; done: landed at 0.2.8262, turned in\n"
     "  2026-10-19),\n"),
    (
        "- Next: (1) melder_1 applies S8 on S3's tree, rebuilding for both, and turns S3 in on the owner's word;\n"
        "  (2) S1, S2 and S5 with melder_1, one at a time (M1-45); S4, S7 and S9 landed (M1-38, M1-42, M1-44);\n"
        "  (3) S11 on the owner's scheduling; (4) each fix with the patch gate, its notch and its rebuild; (5) a\n"
        "  fourth tranche on the owner's word.\n",
        "- Done since: S8 landed at 0.2.8262 and is turned in; S3 is turned in by melder_1; both on the owner's word\n"
        "  (DECISION and FACT notes of 2026-10-19).\n"
        "- Next: (1) small fixes melder_1 can prove, one at a time, each from a failing test with its own notch and the\n"
        "  patch gate (the owner's word; S1, S2 and S5 are the candidates); (2) the rebuild once, last in the pass;\n"
        "  (3) S11 on the owner's call; (4) a fourth tranche on the owner's word.\n",
    ),
]
ROW_PREFIX = "| correctness_defects | in_progress | handoff | claude | melder_1 | none | "
ROW_NEXT = ("S8 and S3 are turned in; melder_1 takes small fixes it can prove (S1 first), each from a failing test, "
            "then rebuilds once; S11 waits for the owner.")


def read_lf(path: pathlib.Path) -> str:
    """Return the file's text, refusing CRLF."""
    raw = path.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in " + str(path))
    return raw.decode("utf-8")


def main() -> None:
    """Apply in memory; write only with --apply."""
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        raise SystemExit(__doc__)
    epic = read_lf(EPIC)
    for number, (old, new) in enumerate(EPIC_EDITS, 1):
        if epic.count(old) != 1:
            raise SystemExit("epic edit %d: found %d times" % (number, epic.count(old)))
        for line in new.split("\n"):
            if len(line) > 120:
                raise SystemExit("epic edit %d: line over 120: %s" % (number, line))
        epic = epic.replace(old, new)
    board = read_lf(BOARD)
    lines = board.split("\n")
    hits = [i for i, line in enumerate(lines) if line.startswith(ROW_PREFIX)]
    if len(hits) != 1:
        raise SystemExit("epic row found %d times" % len(hits))
    cells = lines[hits[0]].split(" | ")
    cells[6] = ROW_NEXT
    cells[10] = TS
    lines[hits[0]] = " | ".join(cells)
    board = "\n".join(lines)
    print("epic: %d edits; board row refreshed; ts %s" % (len(EPIC_EDITS), TS))
    if sys.argv[1] == "--apply":
        EPIC.write_bytes(epic.encode("utf-8"))
        BOARD.write_bytes(board.encode("utf-8"))
        if EPIC.read_bytes().decode("utf-8") != epic or BOARD.read_bytes().decode("utf-8") != board:
            raise SystemExit("read-back mismatch")
        print("applied")


main()
