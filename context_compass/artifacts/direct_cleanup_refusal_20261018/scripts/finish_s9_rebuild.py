"""Record S9's rebuild and send M1-38: the story's MEASURE note and resume view, the artifact row, the message.

One UTC timestamp serves the note, the story's "- Updated:", the message and its alert. Every anchor must occur
exactly once and every file must be LF; drafted lines stay within 120 characters (a single path token is exempt).
Nothing is written with --check. Usage: finish_s9_rebuild.py --check|--apply
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
STORY = ROOT / "tickets/stories/completed/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md"
MAILBOX = ROOT / "mailbox_board.md"
ATTENTION = ROOT / "attention_board.md"
ARTIFACTS = ROOT / "artifact_board.md"
RUNS = "context_compass/artifacts/direct_cleanup_refusal_20261018/runs/"

NOTE = """- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Rebuilt last at 0.2.8256, from the repository root on Python 3.14.7t, after the notch, the release note,
    the Notes and the closure. The asset runner ran whole in a /tmp mirror of src/ and the system documents,
    because its system-documents writer unlinks its payloads and the connected folder refuses deletes: all three
    assets at v0.2.8256 (468, 628 and 4 entries). It changed eight files under src/melder/_build_assets - five
    manifests and the src_architecture, src_components and src_graph payloads - and nothing else; each was copied
    over its original and compared byte-equal, the mirror's src/ and system documents then equal to the
    repository's (only melder_0's patch docs under patches/active/ had changed since the copy), and the asset
    --check on the repository printed only OK lines. The LLM bundles (--include-untracked) rewrote src (583
    files), tests (1132) and other (400) and the manifest; their --check printed only OK lines, and so did the
    asset --check run again after them. The other bundle lists four files fewer than the one committed at HEAD:
    release_docs/0.2.43.md, 0.2.50.md, 0.2.77.md and 0.2.82.md are gone from the working tree and the git index,
    not by this lane (HEAD still holds them). No .git/index.lock.
  EVIDENCE:
  - {runs}rebuild_assets_0_2_8256_mirror.txt:1-12
  - {runs}rebuild_assets_0_2_8256_check.txt:1-3
  - {runs}rebuild_llm_0_2_8256.txt:1-8
  - {runs}rebuild_llm_0_2_8256_check.txt:1-7
  - {runs}rebuild_assets_0_2_8256_check_after_llm.txt:1-7
  IMPACT: 0.2.8256 is landed whole; nothing is committed (the owner commits). spellbook.py and spell.py go back to
    melder_0 with M1-38.
  NEXT: M1-38 to melder_0 and the report to the owner; then S4, re-verified on the current tree before any change.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
"""

MESSAGE = """- TO: melder_0
  FROM: melder_1
  DATETIME: {ts}
  TYPE: NOTICE
  CLAIM: M1-38. S9 landed at 0.2.8256 and is turned in, rebuilt last with both checks OK: notch above it. spellbook.py
    and spell.py are yours again. M0-198: S9 edited none of your listed files (E1-E7 in those two, the notch only).
    Your landing re-reads what S9 changed outside src: the four system docs and indexes, the spellbook.json and
    spell.json descriptors (accepted) and the graph, the release note (header, new section, packaging lines).
    Your epic still records the hole rule (your 15:15:34Z note); S9 took the refusal. melder_1 takes S4 next.
  EVIDENCE: context_compass/tickets/stories/completed/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md
  ACK_REQUESTED: false
"""

ALERT = "- NEW MESSAGE for melder_0 (from melder_1, {ts})\n"

STATE_OLD = "the notch and the release-note section (FACT note); the rebuild follows this closure.\n"
STATE_NEW = "the notch and the release-note section (FACT note); rebuilt last, both checks OK\n  (MEASURE note).\n"
NEXT_OLD = "- Next: none here; spellbook.py and spell.py go back to melder_0 for S1 (M1-38); melder_1 takes S4 next.\n"
NEXT_NEW = "- Next: none here; spellbook.py and spell.py went back to melder_0 for S1 (M1-38); melder_1 takes S4 next.\n"
ROW_OLD = ("the release-note probe, the no-active-spell map and every script (apply, docs, graph prose, release note,"
           " closure);")
ROW_NEW = ("the release-note probe, the rebuild logs, the no-active-spell map and every script (apply, docs, graph"
           " prose, release note, closure, the rebuild record and M1-38);")


def check_width(name: str, text: str) -> None:
    """Refuse a drafted line over 120 characters unless it is one unbreakable path token."""
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("- ") and " " not in stripped[2:]:
            continue
        if stripped.startswith("EVIDENCE: ") and " " not in stripped[len("EVIDENCE: "):]:
            continue
        if len(line) > 120:
            raise SystemExit("%s: line over 120 chars (%d): %s" % (name, len(line), line))


def read_lf(path: pathlib.Path) -> str:
    """Read a board or ticket as text, refusing CRLF."""
    raw = path.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in %s" % path.name)
    return raw.decode("utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    """Replace one exact occurrence, refusing zero or several."""
    count = text.count(old)
    if count != 1:
        raise SystemExit("%s: anchor found %d times" % (label, count))
    return text.replace(old, new)


def main() -> None:
    """Build every change in memory, then write and read back each file with --apply."""
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    apply = sys.argv[1] == "--apply"
    ts = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    note = NOTE.replace("{ts}", ts).replace("{runs}", RUNS)
    message = MESSAGE.replace("{ts}", ts)
    alert = ALERT.replace("{ts}", ts)
    check_width("note", note)
    check_width("message", message)
    check_width("state", STATE_NEW)
    check_width("next", NEXT_NEW)
    story = read_lf(STORY)
    story = replace_once(story, "\n## Closure Confirmation\n", "\n" + note + "\n## Closure Confirmation\n", "story notes")
    story = replace_once(story, STATE_OLD, STATE_NEW, "story state")
    story = replace_once(story, NEXT_OLD, NEXT_NEW, "story next")
    story, count = re.subn(r"^- Updated: \S+$", "- Updated: " + ts, story, count=1, flags=re.M)
    if count != 1:
        raise SystemExit("story: no Updated line")
    mailbox = read_lf(MAILBOX)
    mailbox = replace_once(mailbox, "<!-- END USER-DEFINED: messages -->",
                           message + "<!-- END USER-DEFINED: messages -->", "mailbox messages")
    attention = read_lf(ATTENTION)
    attention = replace_once(attention, "<!-- END USER-DEFINED: alerts -->",
                             alert + "<!-- END USER-DEFINED: alerts -->", "attention alerts")
    artifacts = read_lf(ARTIFACTS)
    artifacts = replace_once(artifacts, ROW_OLD, ROW_NEW, "artifact row")
    print("ts:", ts)
    if not apply:
        print("check: all anchors found")
        return
    for path, text in ((STORY, story), (MAILBOX, mailbox), (ATTENTION, attention), (ARTIFACTS, artifacts)):
        path.write_bytes(text.encode("utf-8"))
        if path.read_bytes().decode("utf-8") != text:
            raise SystemExit("read-back mismatch: %s" % path.name)
        print("applied", path.name)


main()
