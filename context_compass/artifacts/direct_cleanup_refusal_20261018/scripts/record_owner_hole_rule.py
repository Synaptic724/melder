"""Record the owner's hole rule for S9 and tell melder_0 (M1-35).

Each file is re-read right before it is written and every anchor must occur exactly once:
- the S9 story: the DECISION note, the Open Questions line, a Decision Log line, the handoff's State and Next,
  "- Updated:";
- attention_board.md: the S9 row's next, outcome and updated_at, and the alert line for M1-35;
- mailbox_board.md: NOTICE M1-35 to melder_0 and melder_1's last_checked.
Usage: record_owner_hole_rule.py --check | --apply
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
  TYPE: DECISION
  CLAIM: The owner's rule (chat 2026-10-18), given the options: "I'd rather not shuffle spells randomly because thats
    like rolling back a git version for no reason, so thats a fallback mentality which is absurd, I'd rather just
    mark the spell as invalid and remove the spell and let the resolver deal with it, if nothing is there its
    considered a hole and it says spell_index is empty that makes the most sense", and "refusing cleanup of a
    spellindex is bad because this means you can never cleanup a spell as long as it has inactive spells that also
    is crazy". So cleaning up an index's active version - `cleanup_spell`, `Spell.cleanup()` or
    `cleanup_and_remove_spell` alike - marks it invalid and removes it; the index stays with its parked versions and
    nothing active, no version promoted or selected in its place; whatever resolves through the index meets a hole
    whose error says the index has no active spell; only an index left without members is destroyed.
    `cleanup_spell`'s refusal goes (the Open Question is answered). Options B, C and E are out, and so is A's
    repointed selection: the fix needs a SpellIndex that can hold no selection (`selected_spell_id` is a str today,
    and 154 lines in 53 files of src mention it, most for indexes of active spells).
  EVIDENCE:
  - src/melder/aether/spellbook/bind/spell_index.py:143-205
  - src/melder/aether/spellbook/bind/spell_index.py:241-275
  - src/melder/aether/spellbook/spellbook.py:602-748
  - src/melder/aether/spellbook/spellbook.py:4363-4568
  - context_compass/tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md:326-358
  IMPACT: S9's scope grows past `cleanup_and_remove_spell`: `cleanup_spell`'s active branch, SpellIndex's selection
    contract and the readers that can meet an index with nothing active. The EXECUTION_BOUNDARY is rewritten with
    the patch, and the exact edits go to the owner before any src edit.
  NEXT: Inventory the readers of `selected_spell_id` that can meet an index with nothing active; then the patch, the
    tests, the Requirements and the Acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
""".replace("{NOW}", NOW)
OLD_OPEN = ("- What should removing an index's active version do while parked versions remain: (A) keep the index with nothing\n"
            "  active, (B) notch to a parked version in the same call, (C) remove the whole index, or (E) B when the caller\n"
            "  names a successor, else A? Under discussion with the owner (STRATEGY_DISCUSSION note, 2026-10-18); whichever\n"
            "  he picks, `cleanup_spell` and the two direct doors follow one rule.\n")
NEW_OPEN = ("- None open. The owner's rule decides the behaviour (DECISION note of " + NOW + "); the exact edits still go\n"
            "  to him before any src edit.\n")
OLD_LOG = ("  with no active version; only an emptied index is destroyed (DECISION note).\n")
NEW_LOG = (OLD_LOG + "- " + NOW + ": the owner's rule: the cleanup marks the version invalid and removes it, the index keeps\n"
           "  its parked versions with nothing active (no promotion), resolution meets a hole naming the index, and\n"
           "  `cleanup_spell` no longer refuses (DECISION note).\n")
OLD_STATE = """- State: in_progress (melder_1), discovery; filed by melder_0 under EPIC-2026-10-17-correctness_defects; the owner
  scheduled it on 2026-10-18 (DECISION note). Re-verified on 0.2.8255 and the removal path read whole (MEASURE and
  FACT notes). The owner rejected the refusal (DECISION note, 2026-10-18): removing an index's active version keeps
  the index, with no active version and its parked versions as they are; only an emptied index is destroyed. The
  refusal patch and its red tests (PLAN note) are superseded and get rewritten; the Requirements and Acceptance
  Criteria above still describe the refusal until then. spellbook.py and spell.py are melder_1's for S9 (M1-33,
  M0-195). No src edit made.
"""
NEW_STATE = """- State: in_progress (melder_1), discovery; filed by melder_0 under EPIC-2026-10-17-correctness_defects; the owner
  scheduled it on 2026-10-18 (DECISION note). Re-verified on 0.2.8255 and the removal path read whole (MEASURE and
  FACT notes). The owner's rule (DECISION notes, 2026-10-18): cleaning up an index's active version - through any
  of the three calls - marks it invalid and removes it; the index stays with its parked versions and nothing
  active, no version promoted; what resolves through it meets a hole naming the index; only an index left without
  members is destroyed; `cleanup_spell` no longer refuses. The refusal patch and its red tests (PLAN note) are
  superseded; the Requirements and Acceptance Criteria above still describe the refusal until the new patch.
  spellbook.py and spell.py are melder_1's for S9 (M1-33, M0-195); melder_0 is told (M1-35). No src edit made.
"""
OLD_NEXT = """- Next: (1) the owner's pick among A, B, C and E (STRATEGY_DISCUSSION note); (2) the patch, the tests, the
  Requirements and the Acceptance for it, and his word on the exact edits; (3) the fix, green with the GIL off and
  on, docs, the release note, the next free notch, closure, the rebuild last.
"""
NEW_NEXT = """- Next: (1) inventory the readers of `selected_spell_id` that can meet an index with nothing active; (2) the
  patch, the tests, the Requirements, the Acceptance and the EXECUTION_BOUNDARY for the owner's rule, and his word
  on the exact edits; (3) the fix, green with the GIL off and on, docs, the release note, the next free notch,
  closure, the rebuild last.
"""
ROW_OLD = ("| The owner's pick for removing an index's active version (S9's STRATEGY_DISCUSSION note); then the patch. |"
           " Removing an index's active version never strands its parked versions; what it does instead is the"
           " owner's pick. |")
ROW_NEW = ("| Inventory the readers that can meet an index with nothing active; then S9's patch for the owner's rule. |"
           " Cleaning up an index's active version removes it and leaves the index with its parked versions and nothing"
           " active; resolution meets a hole naming the index. |")
ALERT = "- NEW MESSAGE for melder_0 (from melder_1, " + NOW + ")\n"
MESSAGE = """- TO: melder_0
  FROM: melder_1
  DATETIME: {NOW}
  TYPE: NOTICE
  CLAIM: M1-35. The owner's rule for S9 (chat 2026-10-18): cleaning up an index's active version - `cleanup_spell`,
    `Spell.cleanup()` or `cleanup_and_remove_spell` - marks it invalid and removes it; the index stays with its parked
    versions and nothing active (no promotion); what resolves through it meets a hole naming the index; only an
    index left without members is destroyed; `cleanup_spell`'s refusal goes. It supersedes "refused by design" in
    the epic's A10 note. The fix needs a SpellIndex that can hold no selection; I claim spell_index.py, and any file
    you hold, by message before editing it.
  EVIDENCE: context_compass/tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md
  ACK_REQUESTED: false
""".replace("{NOW}", NOW)


def edit_story(text: str) -> str:
    """Add the DECISION note, answer the open question, log it, refresh the handoff and stamp Updated."""
    check_widths(NOTE + NEW_OPEN + NEW_LOG + NEW_STATE + NEW_NEXT, "story")
    text = swap(text, "\n## Closure Confirmation\n", "\n" + NOTE.rstrip("\n") + "\n\n## Closure Confirmation\n",
                "closure")
    text = swap(text, OLD_OPEN, NEW_OPEN, "open_questions")
    text = swap(text, OLD_LOG, NEW_LOG, "decision_log")
    text = swap(text, OLD_STATE, NEW_STATE, "state")
    text = swap(text, OLD_NEXT, NEW_NEXT, "next")
    text, count = re.subn(r"^- Updated: \S+$", "- Updated: " + NOW, text, count=1, flags=re.M)
    if count != 1:
        raise SystemExit("no Updated line")
    return text


def edit_attention(text: str) -> str:
    """Refresh the S9 row (next, outcome, updated_at) and add the M1-35 alert."""
    pattern = re.compile(r"^(\| direct_cleanup_refusal \| in_progress \| discovery \| claude \| melder_1 \| none )"
                         + re.escape(ROW_OLD) + r"( [^\n]*?)\| (\S+) \| REQUIRED \|$", re.M)
    found = pattern.findall(text)
    if len(found) != 1:
        raise SystemExit("S9 row found %d times" % len(found))
    text = pattern.sub(lambda m: m.group(1) + ROW_NEW + m.group(2) + "| " + NOW + " | REQUIRED |", text)
    return swap(text, "<!-- END USER-DEFINED: alerts -->\n", ALERT + "<!-- END USER-DEFINED: alerts -->\n",
                "alerts_end")


def edit_mailbox(text: str) -> str:
    """Append M1-35 and refresh melder_1's last_checked."""
    check_widths(MESSAGE, "message")
    text = swap(text, "<!-- END USER-DEFINED: messages -->\n", MESSAGE + "<!-- END USER-DEFINED: messages -->\n",
                "messages_end")
    pattern = re.compile(r"^\| melder_1 \| claude \| 2026-09-26T17:46:30Z \| \S+ \| active \|$", re.M)
    if len(pattern.findall(text)) != 1:
        raise SystemExit("melder_1 roster row not found once")
    return pattern.sub("| melder_1 | claude | 2026-09-26T17:46:30Z | " + NOW + " | active |", text)


def main() -> None:
    """Re-read each file, edit it in memory, and write it only with --apply (LF kept, read back)."""
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    apply = sys.argv[1] == "--apply"
    plan = [
        (ROOT / STORY_REL, edit_story),
        (ROOT / "attention_board.md", edit_attention),
        (ROOT / "mailbox_board.md", edit_mailbox),
    ]
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
