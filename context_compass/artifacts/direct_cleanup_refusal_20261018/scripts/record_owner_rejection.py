"""Record the owner's rejection of S9's refusal and consume M0-195 (spell.py released).

Each file is re-read right before it is written and every anchor must occur exactly once:
- the S9 story: a FACT note (M0-195) and a DECISION note (the owner's rule), the Open Questions line, a Decision
  Log line, the handoff's State and Next, "- Updated:";
- attention_board.md: the S9 row's next, outcome and updated_at; melder_1's alert line for M0-195 cleared;
- mailbox_board.md: M0-195 deleted (consumed), melder_1's last_checked refreshed.
Usage: record_owner_rejection.py --check | --apply
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


NOTES = """- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-195 from melder_0 (14:14:10Z), consumed: spell.py is released to melder_1 for S9 until it lands, beside
    spellbook.py (M1-33). The identity epic edits both files only at its S1 landing, which waits for the owner's
    approval, a blast-radius run and S2's patches, so S9 lands first and melder_0 claims both back by message after
    it. conduit.py, spellbook_validation_error.py and change_control_manager.py stay free while S8 is on hold.
  EVIDENCE:
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/architecture_patch.md:136-150
  IMPACT: The ENTRY_GATE's file claim is met for both files S9 edits.
  NEXT: The owner's word on the new edits (DECISION note below).
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner rejected the refusal (chat 2026-10-18), shown the edits and the English/French example: "the
    spellindex isn't empty it just doesn't have an active spell, its not up to the agent to notch this, someone can
    cleanup a spell and leave the index the way it is, its not up to us to care about what happens to the this area,
    spellindex if it was empty would be destroyed and french just stays inactive because it hasn't been notched,
    whats wrong with cleaning up the spell? not sure I understand here why are we forcing a user to pick a different
    version". So disposing an index's active version is allowed: that version goes, the index stays with no active
    version and its parked versions as they are, and only an emptied index is destroyed. The defect is the removal
    tearing down an index that still holds versions (D2, D3), not a missing refusal. An index with no active
    version already exists in Melder - the one `remove_from_spell_index` mints - and a notch into it works (the
    correctness epic's A3 note). The refusal edits are withdrawn unmade; the patch docs, the red tests, the
    Requirements and the Acceptance Criteria are rewritten for this rule before any src edit. `cleanup_spell`'s own
    refusal of the active member ("notch away from it first") rests on the rule he rejected; whether S9 removes it
    too is asked of him (Open Questions).
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:602-748
  - src/melder/aether/spellbook/spellbook.py:4276-4361
  - src/melder/aether/spellbook/spellbook.py:4427-4568
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:397-428
  - context_compass/tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md:42-80
  IMPACT: The fix changes direction: `cleanup_and_remove_spell` keeps a non-empty index instead of refusing. No src
    edit was made, so nothing is reverted.
  NEXT: Read whole what an index with no active version touches - SpellIndex selection and membership, the frame
    registry, the record's index snapshot, index-link borrowers, a notch into it - and bring the owner new edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
""".replace("{NOW}", NOW)
OLD_OPEN = "- none (the fix applies `cleanup_spell`'s own rule; the alternative is the DECISION_REQUEST above).\n"
NEW_OPEN = ("- Should `cleanup_spell` stop refusing the active member of a multi-member index too, so every removal keeps a\n"
            "  non-empty index the same way? Asked of the owner on 2026-10-18; its refusal rests on the rule he rejected\n"
            "  (DECISION note).\n")
OLD_LOG = "- 2026-10-17T21:38:03Z: filed under EPIC-2026-10-17-correctness_defects from sweep A10 (Notes).\n"
NEW_LOG = (OLD_LOG + "- " + NOW + ": the owner rejected the refusal: removing an index's active version keeps the index\n"
           "  with no active version; only an emptied index is destroyed (DECISION note).\n")
OLD_HANDOFF = """- State: in_progress (melder_1), discovery; filed by melder_0 under EPIC-2026-10-17-correctness_defects; the owner
  scheduled it on 2026-10-18 (DECISION note). Re-verified on 0.2.8255 and the removal path read whole (MEASURE and
  FACT notes); the patch direct_cleanup_refusal_2026_10_18 written and the tests red, GIL off and on (PLAN note).
  The fix sits in spellbook.py, released to melder_1 (M0-194) and claimed for this fix (M1-33); spell.py, for one
  docstring entry, is asked of melder_0 (M1-34). No src edit made.
- Next: (1) the owner's word on the exact edits and the message; (2) the fix, green with the GIL off and on, probe
  D1-D3 re-run; (3) docs, the release note, the next free notch, closure, the rebuild last.
"""
NEW_HANDOFF = """- State: in_progress (melder_1), discovery; filed by melder_0 under EPIC-2026-10-17-correctness_defects; the owner
  scheduled it on 2026-10-18 (DECISION note). Re-verified on 0.2.8255 and the removal path read whole (MEASURE and
  FACT notes). The owner rejected the refusal (DECISION note, 2026-10-18): removing an index's active version keeps
  the index, with no active version and its parked versions as they are; only an emptied index is destroyed. The
  refusal patch and its red tests (PLAN note) are superseded and get rewritten; the Requirements and Acceptance
  Criteria above still describe the refusal until then. spellbook.py and spell.py are melder_1's for S9 (M1-33,
  M0-195). No src edit made.
- Next: (1) read what an index with no active version touches; rewrite the patch, the tests, the Requirements and
  the Acceptance; (2) the owner's answer on `cleanup_spell` (Open Questions) and his word on the new edits; (3) the
  fix, green with the GIL off and on, docs, the release note, the next free notch, closure, the rebuild last.
"""
ROW_OLD = ("| direct_cleanup_refusal | in_progress | discovery | claude | melder_1 | none | The owner's word on S9's exact"
           " edits; melder_0's answer on spell.py (M1-34). | A direct cleanup of an index's active member that has parked"
           " versions is refused with nothing changed, as cleanup_spell refuses it. |")
ROW_NEW = ("| direct_cleanup_refusal | in_progress | discovery | claude | melder_1 | none | Rewrite S9's patch and tests for"
           " the owner's rule (a non-empty index stays); his answer on cleanup_spell. | Removing an index's active"
           " version keeps the index while it holds other versions, with no active one; only an emptied index is"
           " destroyed. |")
ALERT = "- NEW MESSAGE for melder_1 (from melder_0, 2026-10-18T14:14:10Z)\n"
MESSAGE_START = "- TO: melder_1\n  FROM: melder_0\n  DATETIME: 2026-10-18T14:14:10Z\n  TYPE: ACK\n  CLAIM: M0-195,"


def edit_story(text: str) -> str:
    """Add the two notes, the open question, the decision log line and the new handoff; stamp Updated."""
    check_widths(NOTES + NEW_OPEN + NEW_LOG + NEW_HANDOFF, "story")
    text = swap(text, "\n## Closure Confirmation\n", "\n" + NOTES.rstrip("\n") + "\n\n## Closure Confirmation\n",
                "closure")
    text = swap(text, OLD_OPEN, NEW_OPEN, "open_questions")
    text = swap(text, OLD_LOG, NEW_LOG, "decision_log")
    text = swap(text, OLD_HANDOFF, NEW_HANDOFF, "handoff")
    text, count = re.subn(r"^- Updated: \S+$", "- Updated: " + NOW, text, count=1, flags=re.M)
    if count != 1:
        raise SystemExit("no Updated line")
    return text


def edit_attention(text: str) -> str:
    """Refresh the S9 row (next, outcome, updated_at) and clear melder_1's M0-195 alert."""
    pattern = re.compile(re.escape(ROW_OLD) + r"( [^\n]*?)\| (\S+) \| REQUIRED \|$", re.M)
    found = pattern.findall(text)
    if len(found) != 1:
        raise SystemExit("S9 row found %d times" % len(found))
    text = pattern.sub(lambda m: ROW_NEW + m.group(1) + "| " + NOW + " | REQUIRED |", text)
    return swap(text, ALERT, "", "alert")


def edit_mailbox(text: str) -> str:
    """Delete M0-195 (consumed) and refresh melder_1's last_checked."""
    start = text.find(MESSAGE_START)
    if start < 0 or text.count(MESSAGE_START) != 1:
        raise SystemExit("M0-195 not found once")
    end_marker = "  ACK_REQUESTED: false\n"
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit("M0-195 end not found")
    end += len(end_marker)
    block = text[start:end]
    if block.count("- TO: ") != 1:
        raise SystemExit("M0-195 block spans another message")
    text = text[:start] + text[end:]
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
