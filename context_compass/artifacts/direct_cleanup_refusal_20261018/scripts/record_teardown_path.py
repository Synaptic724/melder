"""Record on S9 that Book teardown never meets the refusal (a FACT note answering the owner) and stamp Updated.

The story is re-read right before it is written; the anchor must occur exactly once; LF kept; read back.
Usage: record_teardown_path.py --check | --apply
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
  TYPE: FACT
  CLAIM: The owner asked what happens when the Spellbook itself cleans up and the refusal stands in its way (chat
    2026-10-18: "if a spellbook is trying to cleanup something then the spellindex says ... you can't clean ... then
    what happens?"). It never meets the refusal. The SpellIndex refuses nothing: the check is the Spellbook's own,
    made in the removal of one version a caller asks for (`_dispose_spell` today; `cleanup_and_remove_spell` under
    the refusal), and only two src calls reach that removal - `_dispose_spell` for a sole member and a direct
    `Spell.cleanup()` from user code. Book teardown - `Spellbook.cleanup()`, which root and frame teardown reach -
    runs `_cleanup_spells`: for every active spell it unregisters the index, sets `_spellbook_cleanup` so
    `Spell.cleanup()` skips the removal route and tears the spell down locally, and cleans the index; there is no
    membership check on that path, today or under the refusal. What teardown leaves today is S7's defect: the parked
    versions are dropped from `_inactive_spells` uncleaned, and an index holding only parked versions is never
    cleaned.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:370-460
  - src/melder/aether/spellbook/spellbook.py:557-600
  - src/melder/aether/spellbook/spell.py:581-763
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/cleanup_and_remove_spell_callers_0_2_8255.txt:1-41
  IMPACT: The refusal constrains a caller asking to remove one version, never a Book tearing itself down; S7, next
    after S9, is what makes teardown clean the parked versions too.
  NEXT: The owner's pick between the refusal and the hole rule.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
""".replace("{NOW}", NOW)


def check_widths(block: str) -> None:
    """Refuse a written line over the 120-character cap (a single path token is exempt)."""
    for line in block.split("\n"):
        stripped = line.strip()
        if stripped.startswith("- ") and " " not in stripped[2:]:
            continue
        if len(line) > 120:
            raise SystemExit("line over 120 chars (%d): %s" % (len(line), line))


def main() -> None:
    """Re-read the story, add the note before Closure Confirmation, stamp Updated; write only with --apply."""
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    check_widths(NOTE)
    path = ROOT / STORY_REL
    raw = path.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in story")
    text = raw.decode("utf-8")
    anchor = "\n## Closure Confirmation\n"
    if text.count(anchor) != 1:
        raise SystemExit("closure anchor not found once")
    text = text.replace(anchor, "\n" + NOTE.rstrip("\n") + "\n\n## Closure Confirmation\n")
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
