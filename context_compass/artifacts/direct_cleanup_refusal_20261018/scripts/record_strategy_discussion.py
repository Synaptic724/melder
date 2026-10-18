"""Record S9's STRATEGY_DISCUSSION (the owner asked to talk through the removal's behaviour).

Each file is re-read right before it is written and every anchor must occur exactly once:
- the S9 story: the STRATEGY_DISCUSSION note, the Open Questions line, the handoff's Next, "- Updated:";
- attention_board.md: the S9 row's next, outcome and updated_at.
Usage: record_strategy_discussion.py --check | --apply
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
STORY_REL = "tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md"
NOW = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def swap(text: str, old: str, new: str, label: str) -> str:
    """Replace one anchored block; the anchor must occur exactly once."""
    count = text.count(old)
    if count != 1:
        raise SystemExit("anchor %s found %d times" % (label, count))
    return text.replace(old, new)


def check_widths(block: str, label: str) -> None:
    """Refuse a written line over the 120-character cap (a single path token is exempt)."""
    for line in block.split("\n"):
        stripped = line.strip()
        if stripped.startswith("- ") and " " not in stripped[2:]:
            continue
        if len(line) > 120:
            raise SystemExit("%s: line over 120 chars (%d): %s" % (label, len(line), line))


NOTE = """- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: STRATEGY_DISCUSSION
  CLAIM: The owner asked to talk through what cleaning up an index's active version should do while parked
    versions remain (chat 2026-10-18: "perhaps cleaning up a spell thats active with inactive spells in it should do
    something else ... lets talk about it"). Facts, read whole: a SpellIndex cannot say "nothing active" -
    `selected_spell_id` is always a str, and `remove_member` of the selected id leaves it naming a non-member
    ("Callers retiring the head must select a new one"); the index `remove_from_spell_index` mints selects its
    parked member while the Book holds it parked (the owner's S10 ruling: activation takes a notch). Readers take the
    selection for the active version: `_apply_add_to_index` proves the Book owns a target index by
    `selected_spell_id in _spell_ids` (a stale selection refuses `add_to_spell_index` and `bind_inactive` onto it),
    the record captures it and a graft binds it active, and ReleaseManagedSpell prefers its pool. Options: (A) remove
    that version; the index stays with its parked versions and nothing active, its selection repointed at a parked
    member as in a minted index; the index's consumers and borrowers have no provider until someone notches. (B)
    Remove it and notch to a parked version in the same call: which one when several are parked, and S8's failure
    when that version fails its check. (C) Remove the whole index with every version. (D) Refuse - today's
    `cleanup_spell`; rejected by the owner. (E) The caller may name a successor (`successor_spell_id=`) and gets B;
    without one, A. Recommended: A - the owner's stated rule - with E only if agents ask for it; whichever is chosen,
    `cleanup_spell` and the two direct doors follow the one rule.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/spell_index.py:83-116
  - src/melder/aether/spellbook/bind/spell_index.py:143-205
  - src/melder/aether/spellbook/bind/spell_index.py:241-275
  - src/melder/aether/spellbook/bind/spell_index.py:361-392
  - src/melder/aether/spellbook/spellbook.py:4101-4195
  - src/melder/aether/spellbook/spellbook.py:4276-4361
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:725-752
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:797-812
  IMPACT: The pick decides the patch; nothing is written for S9 until the owner chooses.
  NEXT: The owner's pick; then the patch, the tests, the Requirements and the Acceptance for it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
""".replace("{NOW}", NOW)
OLD_OPEN = ("- Should `cleanup_spell` stop refusing the active member of a multi-member index too, so every removal keeps a\n"
            "  non-empty index the same way? Asked of the owner on 2026-10-18; its refusal rests on the rule he rejected\n"
            "  (DECISION note).\n")
NEW_OPEN = ("- What should removing an index's active version do while parked versions remain: (A) keep the index with nothing\n"
            "  active, (B) notch to a parked version in the same call, (C) remove the whole index, or (E) B when the caller\n"
            "  names a successor, else A? Under discussion with the owner (STRATEGY_DISCUSSION note, 2026-10-18); whichever\n"
            "  he picks, `cleanup_spell` and the two direct doors follow one rule.\n")
OLD_NEXT = """- Next: (1) read what an index with no active version touches; rewrite the patch, the tests, the Requirements and
  the Acceptance; (2) the owner's answer on `cleanup_spell` (Open Questions) and his word on the new edits; (3) the
  fix, green with the GIL off and on, docs, the release note, the next free notch, closure, the rebuild last.
"""
NEW_NEXT = """- Next: (1) the owner's pick among A, B, C and E (STRATEGY_DISCUSSION note); (2) the patch, the tests, the
  Requirements and the Acceptance for it, and his word on the exact edits; (3) the fix, green with the GIL off and
  on, docs, the release note, the next free notch, closure, the rebuild last.
"""
ROW_OLD = ("| Rewrite S9's patch and tests for the owner's rule (a non-empty index stays); his answer on cleanup_spell. |"
           " Removing an index's active version keeps the index while it holds other versions, with no active one; only"
           " an emptied index is destroyed. |")
ROW_NEW = ("| The owner's pick for removing an index's active version (S9's STRATEGY_DISCUSSION note); then the patch. |"
           " Removing an index's active version never strands its parked versions; what it does instead is the"
           " owner's pick. |")


def edit_story(text: str) -> str:
    """Add the note, the open question and the new Next; stamp Updated."""
    check_widths(NOTE + NEW_OPEN + NEW_NEXT, "story")
    text = swap(text, "\n## Closure Confirmation\n", "\n" + NOTE.rstrip("\n") + "\n\n## Closure Confirmation\n",
                "closure")
    text = swap(text, OLD_OPEN, NEW_OPEN, "open_questions")
    text = swap(text, OLD_NEXT, NEW_NEXT, "next")
    text, count = re.subn(r"^- Updated: \S+$", "- Updated: " + NOW, text, count=1, flags=re.M)
    if count != 1:
        raise SystemExit("no Updated line")
    return text


def edit_attention(text: str) -> str:
    """Refresh the S9 row's next, outcome and updated_at."""
    pattern = re.compile(r"^(\| direct_cleanup_refusal \| in_progress \| discovery \| claude \| melder_1 \| none )"
                         + re.escape(ROW_OLD) + r"( [^\n]*?)\| (\S+) \| REQUIRED \|$", re.M)
    found = pattern.findall(text)
    if len(found) != 1:
        raise SystemExit("S9 row found %d times" % len(found))
    return pattern.sub(lambda m: m.group(1) + ROW_NEW + m.group(2) + "| " + NOW + " | REQUIRED |", text)


def main() -> None:
    """Re-read each file, edit it in memory, and write it only with --apply (LF kept, read back)."""
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    apply = sys.argv[1] == "--apply"
    plan = [(ROOT / STORY_REL, edit_story), (ROOT / "attention_board.md", edit_attention)]
    results = []
    for path, edit in plan:
        raw = path.read_bytes()
        if b"\r\n" in raw:
            raise SystemExit("CRLF in %s" % path.name)
        results.append((path, edit(raw.decode("utf-8"))))
    print("all anchors found; NOW =", NOW)
    if apply:
        for path, text in results:
            path.write_bytes(text.encode("utf-8"))
            if path.read_bytes().decode("utf-8") != text:
                raise SystemExit("read-back mismatch in %s" % path.name)
        print("applied")


main()
