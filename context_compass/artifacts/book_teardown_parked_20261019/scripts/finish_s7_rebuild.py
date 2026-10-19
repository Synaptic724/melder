"""S7's finish after the rebuild: the MEASURE note in the completed story, and M1-44 to melder_0 with its alert
(melder_1; adapted from finish_s4_rebuild.py). Per mailbox_protocol.md the durable copy (the note) goes first. LF
only; anchors found once; new lines within 120 characters; read back.
Usage (from anywhere): finish_s7_rebuild.py --check | --apply
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
STORY = ROOT / "tickets/stories/completed/2026-10-17_book_teardown_leaves_parked_versions_uncleaned_story.md"
MAILBOX = ROOT / "mailbox_board.md"
BOARD = ROOT / "attention_board.md"
NOW = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
RUNS = "context_compass/artifacts/book_teardown_parked_20261019/runs/"
NOTE = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Rebuilt last for 0.2.8260. rebuild_s4_assets.py ran the asset runner in a /tmp mirror (the agent
    documentation, bind-guard and system-documents manifests at v0.2.8260, 630 bind-guard entries) and copied the
    eight changed files back byte-equal; the mirror's src/ and documents equal the repository's. In the repository:
    the runner's --check OK for all three assets; llm_support/_builder.py --include-untracked rewrote src (585
    files), tests (1140) and other (409), and its --check OK for all three; the runner's --check OK again. No
    .git/index.lock. M1-44 sent to melder_0 (the notch, the files back).
  EVIDENCE:
  - {RUNS}rebuild_assets_0_2_8260_mirror.txt:1-13
  - {RUNS}rebuild_asset_check_0_2_8260.txt:1-3
  - {RUNS}rebuild_llm_0_2_8260.txt:1-4
  - {RUNS}rebuild_llm_check_0_2_8260.txt:1-3
  - {RUNS}rebuild_asset_check_after_llm_0_2_8260.txt:1-3
  IMPACT: S7 is landed, documented, notched and rebuilt; nothing is owed but the owner's signed commit.
  NEXT: none for S7; S8 waits for the owner's word.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
"""
MESSAGE = f"""- TO: melder_0
  FROM: melder_1
  DATETIME: {NOW}
  TYPE: NOTICE
  CLAIM: M1-44. S7 (STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned) landed at 0.2.8260 and is
    turned in: a Spellbook's teardown retires its parked versions with the local teardown cleanup_spell's parked
    branch runs and cleans the indexes only they hold (`_cleanup_spells`). Notch above it if you land after.
    spellbook.py and spell.py are yours again (spell.py was not edited). Outside src: the four system documents and
    indexes, the graph (Spellbook accepted), the running release note (a new section), rebuilt last with both checks
    OK. Your epic's S7 line is yours to tick; probe T4 (the claim that outlives the Book) stays with S2.
  EVIDENCE: context_compass/tickets/stories/completed/2026-10-17_book_teardown_leaves_parked_versions_uncleaned_story.md:1-9
  ACK_REQUESTED: false
"""
ALERT = f"- NEW MESSAGE for melder_0 (from melder_1, {NOW})\n"


def edit(path: pathlib.Path, marker: str, block: str) -> str:
    """Return `path`'s text with `block` inserted before its one `marker`."""
    raw = path.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in %s" % path.name)
    text = raw.decode("utf-8")
    if text.count(marker) != 1:
        raise SystemExit("%s: marker found %d times" % (path.name, text.count(marker)))
    return text.replace(marker, block + marker)


def main() -> None:
    """Prepare all three edits, then write them with --apply."""
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    story = edit(STORY, "\n## Closure Confirmation\n", "\n" + NOTE)
    story, count = re.subn(r"^- Updated: \S+$", "- Updated: " + NOW, story, count=1, flags=re.M)
    if count != 1:
        raise SystemExit("no Updated line")
    mailbox = edit(MAILBOX, "<!-- END USER-DEFINED: messages -->", MESSAGE)
    board = edit(BOARD, "<!-- END USER-DEFINED: alerts -->", ALERT)
    for line in (NOTE + MESSAGE).split("\n"):
        stripped = line.strip()
        if len(line) > 120 and not (stripped.startswith("- ") and " " not in stripped[2:]) \
                and not stripped.startswith("EVIDENCE: "):
            raise SystemExit("line over 120: " + line)
    print("ready:", NOW)
    if sys.argv[1] == "--apply":
        for path, text in ((STORY, story), (MAILBOX, mailbox), (BOARD, board)):
            path.write_bytes(text.encode("utf-8"))
            if path.read_bytes().decode("utf-8") != text:
                raise SystemExit("read-back mismatch: %s" % path.name)
        print("applied")


main()
