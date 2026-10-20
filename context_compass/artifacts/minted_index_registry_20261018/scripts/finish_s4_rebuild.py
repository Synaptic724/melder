"""S4's finish after the rebuild: the MEASURE note in the completed story, and M1-42 to melder_0 with its alert.

Per mailbox_protocol.md the durable copy (the note) goes first. LF only; anchors found once; read back.
Usage (from anywhere): finish_s4_rebuild.py --check | --apply
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
STORY = ROOT / "tickets/stories/completed/2026-10-17_minted_index_missing_from_frame_registry_story.md"
MAILBOX = ROOT / "mailbox_board.md"
BOARD = ROOT / "attention_board.md"
NOW = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
RUNS = "context_compass/artifacts/minted_index_registry_20261018/runs/"
NOTE = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Rebuilt last for 0.2.8259. rebuild_s4_assets.py ran the asset runner in a /tmp mirror (the agent
    documentation, bind-guard and system-documents manifests at v0.2.8259, 630 bind-guard entries) and copied the
    eight changed files back byte-equal; the mirror's src/ and documents equal the repository's. In the repository:
    the runner's --check OK for all three assets; llm_support/_builder.py --include-untracked rewrote src (585
    files) and other (409), tests unchanged, and its --check OK for all three; the runner's --check OK again. No
    .git/index.lock. M1-42 sent to melder_0 (the notch, the files back, what S4 changed outside src).
  EVIDENCE:
  - {RUNS}rebuild_assets_0_2_8259_mirror.txt
  - {RUNS}rebuild_asset_check_0_2_8259.txt
  - {RUNS}rebuild_llm_0_2_8259.txt
  - {RUNS}rebuild_llm_check_0_2_8259.txt
  - {RUNS}rebuild_asset_check_after_llm_0_2_8259.txt
  IMPACT: S4 is landed, documented, notched and rebuilt; nothing is owed.
  NEXT: none for S4; melder_1 takes S7 next.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
"""
MESSAGE = f"""- TO: melder_0
  FROM: melder_1
  DATETIME: {NOW}
  TYPE: NOTICE
  CLAIM: M1-42. S4 (STORY-2026-10-17-minted_index_missing_from_frame_registry) landed at 0.2.8259 and is turned in:
    the index remove_from_spell_index mints is registered with the frame as bind registers its new index, the root's
    teardown unregisters it with the rest, and residency reads its version parked until a notch. Notch above it if
    you land after. spellbook.py and spell.py are yours again and mutation_research.py is released. Outside src: the
    four system documents and indexes, the graph (Spellbook and Spell accepted), the running release note (a new
    section; your identity section's Known-limits clause on the collision check removed and the identity
    invariant's Open item marked fixed, since S4 fixes it), rebuilt last with both checks OK. Your epic's S4 can take
    M4b and M5b as acceptance cases now.
  EVIDENCE: context_compass/tickets/stories/completed/2026-10-17_minted_index_missing_from_frame_registry_story.md
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
        if len(line) > 120 and not (stripped.startswith("- ") and " " not in stripped[2:]):
            raise SystemExit("line over 120: " + line)
    print("ready:", NOW)
    if sys.argv[1] == "--apply":
        for path, text in ((STORY, story), (MAILBOX, mailbox), (BOARD, board)):
            path.write_bytes(text.encode("utf-8"))
            if path.read_bytes().decode("utf-8") != text:
                raise SystemExit("read-back mismatch: %s" % path.name)
        print("applied")


main()
