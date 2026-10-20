"""Record the owner's pick of the refusal on S9 (a DECISION note and the sections it changes), send M1-37 to
melder_0 (S9 lands first; spell_index.py released) and refresh S9's board row.

Each file is re-read right before it is written; every anchor must occur exactly once; LF kept; read back.
Usage: record_owner_refusal_pick.py --check | --apply
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


def swap_between(text: str, start: str, end: str, new: str, label: str) -> str:
    """Replace text[start-anchor .. end-anchor) with `new`; both anchors must occur exactly once."""
    if text.count(start) != 1 or text.count(end) != 1:
        raise SystemExit("anchors for %s not found once" % label)
    i = text.index(start)
    j = text.index(end)
    if j <= i:
        raise SystemExit("anchors for %s out of order" % label)
    return text[:i] + new + text[j:]


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
  CLAIM: The owner chose the refusal (chat 2026-10-18), shown its costs (TRADEOFF note) and that Book teardown never
    meets it (FACT note): asked which rule S9 should use when an agent cleans up an index's active version while
    parked versions remain, he picked "Refusal (Recommended)" - "All three cleanup calls refuse with a message naming
    the remedies (notch first, clean the parked ones, or move them out). Book teardown is unaffected. Small change;
    lands before S1." The hole rule of the DECISION note of 2026-10-18T15:04:57Z is withdrawn unmade. So
    `cleanup_and_remove_spell` - and a direct `Spell.cleanup()` through it - refuses the active member of an index
    that also holds parked versions before anything is unregistered, as `cleanup_spell` refuses it; both refusals
    name the three remedies (`_dispose_spell`'s message is reworded to match); SpellIndex, `cleanup_spell`'s
    behaviour and every other reader stay as they are. The PLAN note's patch and red tests stand, updated for the
    remedies' wording, `cleanup_spell`'s message and the third remedy. S9 lands before S1 and hands spellbook.py
    and spell.py back to melder_0 after it (M1-37); spell_index.py is released now.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:602-748
  - src/melder/aether/spellbook/spellbook.py:4363-4425
  - src/melder/aether/spellbook/spellbook.py:4427-4568
  - src/melder/aether/spellbook/spell.py:581-763
  - context_compass/system_docs/patches/active/direct_cleanup_refusal_2026_10_18/architecture_patch.md:1-49
  IMPACT: S9's scope is the removal path plus one reworded message and three docstrings in spellbook.py and spell.py;
    no file of the identity epic is needed. The exact edits go to the owner before the first one.
  NEXT: Update the patch docs and the red tests; then the exact edits to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
""".replace("{NOW}", NOW)

OLD_BOUNDARY = """- EXECUTION_BOUNDARY: `Spellbook.cleanup_and_remove_spell` (the multi-member check `_dispose_spell` makes, before
  anything is unregistered), and so a direct `Spell.cleanup()`, which routes there; regression tests; the system
  documents (the Spellbook Core component, a failure mode) with their indexes and the graph; the release note; one
  notch; the rebuild last.
"""
NEW_BOUNDARY = """- EXECUTION_BOUNDARY: `Spellbook.cleanup_and_remove_spell` (the multi-member check `_dispose_spell` makes, before
  anything is unregistered), and so a direct `Spell.cleanup()`, which routes there; `_dispose_spell`'s refusal
  message, reworded to name the same remedies (owner, 2026-10-18); the docstrings of the three (`cleanup_spell`'s
  Contract, `cleanup_and_remove_spell`'s Contract, Raises and Threading, `Spell.cleanup`'s Raises); regression
  tests; the system documents (the Spellbook Core component, a failure mode) with their indexes and the graph; the
  release note; one notch; the rebuild last.
"""
OLD_REQ = """- `Spellbook.cleanup_and_remove_spell` - and a direct `Spell.cleanup()` through it - refuses the active member of
  an index that also holds parked versions before anything is unregistered, with the error `cleanup_spell` raises
  ("... is the active member of a multi-member index; notch away from it before disposing it.").
"""
NEW_REQ = """- `Spellbook.cleanup_and_remove_spell` - and a direct `Spell.cleanup()` through it - refuses the active member of
  an index that also holds parked versions before anything is unregistered, as `cleanup_spell` does (owner,
  2026-10-18). Both refusals name the remedies: "... is the active member of a multi-member index, and disposing it
  would leave the index's parked versions without an active one. Notch the index to one of them, dispose them with
  cleanup_spell, or move them out with remove_from_spell_index first."
"""
OLD_ACC = """- With English active and French parked on its index: `English.cleanup()` and `cleanup_and_remove_spell(English)`
  raise the multi-member RuntimeError, and afterwards the index, English, French, the frame registry and the
  borrower are as before.
- English alone on its index is still removed by either call.
"""
NEW_ACC = """- With English active and French parked on its index: `English.cleanup()` and `cleanup_and_remove_spell(English)`
  raise the multi-member RuntimeError, and afterwards the index, English, French, the frame registry and the
  borrower are as before; `cleanup_spell(English)` raises its refusal naming the same remedies.
- After a refusal each remedy works: a notch to French, then `cleanup_spell(English)`; `cleanup_spell(French)`, then
  `English.cleanup()`; `remove_from_spell_index(French)`, then `English.cleanup()` (French stays parked, alone in a
  fresh index).
- English alone on its index is still removed by either call.
"""
OLD_VAL = """- Regression tests named for the symptom, e.g. `test_direct_cleanup_of_an_active_member_with_parked_siblings_refuses`
  and `test_cleanup_and_remove_spell_refuses_a_member_with_parked_siblings`; GIL off and on; the probe re-run. Not
  run: no fix exists yet.
"""
NEW_VAL = """- Regression tests named for the symptom - `test_direct_cleanup_of_an_active_member_with_parked_siblings_refuses`,
  `test_cleanup_and_remove_spell_refuses_a_member_with_parked_siblings`, `cleanup_spell`'s message and the three
  remedies; GIL off and on; the probe re-run. Red on 0.2.8255 (PLAN note); green not run: no fix exists yet.
"""
OLD_RISK = """- A caller that relies on the direct route to drop a whole lineage gets an error; the remedy is the documented one:
  notch away first, or dispose the parked versions with `cleanup_spell`.
"""
NEW_RISK = """- A caller that relies on the direct route to drop a whole lineage gets an error; the remedy is the documented one:
  notch the index to a parked version first, dispose the parked versions with `cleanup_spell`, or move them out
  with `remove_from_spell_index`.
"""
OLD_OPEN = """- Refusal or the hole rule? The owner reopened it after the DECISION note of 2026-10-18T15:04:57Z (chat 2026-10-18:
  "refusing a cleanup makes sense too maybe we just go that route?"); what each costs is in the TRADEOFF note of
  2026-10-18T15:27:07Z. The exact edits still go to him before any src edit.
"""
NEW_OPEN = """- None open. The owner chose the refusal (DECISION note of {NOW}); the exact edits still go to him
  before any src edit.
""".replace("{NOW}", NOW)
DECISION_LOG_ADD = """  `cleanup_spell` no longer refuses (DECISION note).
- {NOW}: the owner chose the refusal on all three doors, the messages naming the remedies; the hole
  rule is withdrawn unmade (DECISION note).

## Artifact Links (Optional)
""".replace("{NOW}", NOW)
NEW_STATE = """- State: in_progress (melder_1), discovery; filed by melder_0 under EPIC-2026-10-17-correctness_defects; the owner
  scheduled it on 2026-10-18 (DECISION note). Re-verified on 0.2.8255 and the removal path read whole (MEASURE and
  FACT notes). After weighing a hole rule (an index kept with parked versions and nothing active: the DECISION note
  of 15:04:57Z, the lane's notes/no_active_spell_map.md, the TRADEOFF note) the owner chose the refusal (DECISION
  note of {NOW}): all three cleanup doors refuse the active member of an index that holds parked
  versions, the messages naming the remedies; Book teardown never meets it (FACT note). The PLAN note's patch and
  red tests stand, updated for the remedies. spellbook.py and spell.py are melder_1's until S9 lands, then go back
  to melder_0 for S1 (M1-36, M1-37); spell_index.py is released (M1-37). No src edit made.
""".replace("{NOW}", NOW)
NEW_NEXT = """- Next: (1) the patch docs and the red tests updated for the remedies' wording, `cleanup_spell`'s message and the
  third remedy; (2) the exact edits to the owner, and his word; (3) the fix, green with the GIL off and on, the probe
  re-run, docs, the release note, the next free notch (0.2.8256 unless it moved), closure, the rebuild last; then a
  message hands spellbook.py and spell.py back to melder_0.
"""
ROW_NEXT_OLD = ("The owner's pick: refusal on all three doors, or the hole rule (S9's TRADEOFF note); then M1-37 and "
                "the patch.")
ROW_NEXT_NEW = "Update S9's patch docs and red tests for the remedies; then the exact edits to the owner."
ROW_OUTCOME_OLD = ("One rule for disposing an index's active version on all three doors; no parked version is left on "
                   "a cleaned index.")
ROW_OUTCOME_NEW = ("All three cleanup doors refuse an index's active version while parked versions remain, naming the "
                   "remedies; no parked version is left on a cleaned index.")
M1_37 = """- TO: melder_0
  FROM: melder_1
  DATETIME: {NOW}
  TYPE: NOTICE
  CLAIM: M1-37, re M0-196 (M1-36). The owner chose the refusal for S9 (chat 2026-10-18): all three cleanup doors
    refuse the active member of an index that holds parked versions, the messages naming the remedies; Book
    teardown is unaffected. S9 lands first, after his word on the exact edits: spellbook.py
    (`cleanup_and_remove_spell`'s check and docstring, `_dispose_spell`'s refusal text, `cleanup_spell`'s
    docstring) and spell.py (`Spell.cleanup`'s Raises entry) only. I hand both back by message right after its
    landing, rebuild included; S1 notches above it. spell_index.py is yours again now: the refusal does not touch
    it, nor conduit.py.
  EVIDENCE: context_compass/tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md
  ACK_REQUESTED: false
""".replace("{NOW}", NOW)


def edit_story(text: str) -> str:
    """The DECISION note and every section the pick changes; stamp Updated."""
    new_blocks = NOTE + NEW_BOUNDARY + NEW_REQ + NEW_ACC + NEW_VAL + NEW_RISK + NEW_OPEN + DECISION_LOG_ADD
    check_widths(new_blocks + NEW_STATE + NEW_NEXT, "story")
    text = swap(text, "\n## Closure Confirmation\n", "\n" + NOTE.rstrip("\n") + "\n\n## Closure Confirmation\n",
                "closure")
    text = swap(text, OLD_BOUNDARY, NEW_BOUNDARY, "boundary")
    text = swap(text, OLD_REQ, NEW_REQ, "requirements")
    text = swap(text, OLD_ACC, NEW_ACC, "acceptance")
    text = swap(text, OLD_VAL, NEW_VAL, "validation")
    text = swap(text, OLD_RISK, NEW_RISK, "risks")
    text = swap(text, OLD_OPEN, NEW_OPEN, "open questions")
    text = swap(text, "  `cleanup_spell` no longer refuses (DECISION note).\n\n## Artifact Links (Optional)\n",
                DECISION_LOG_ADD, "decision log")
    text = swap_between(text, "- State: in_progress (melder_1), discovery;", "- Next: (1) the owner's pick:", NEW_STATE,
                        "state")
    text = swap_between(text, "- Next: (1) the owner's pick:", "\n## Project-Specific Additions", NEW_NEXT, "next")
    text, count = re.subn(r"^- Updated: \S+$", "- Updated: " + NOW, text, count=1, flags=re.M)
    if count != 1:
        raise SystemExit("no Updated line")
    return text


def edit_attention(text: str) -> str:
    """Add melder_0's alert; refresh S9's row."""
    text = swap(text, "<!-- END USER-DEFINED: alerts -->",
                "- NEW MESSAGE for melder_0 (from melder_1, " + NOW + ")\n<!-- END USER-DEFINED: alerts -->", "alerts")
    pattern = re.compile(r"^(\| direct_cleanup_refusal \| in_progress \| discovery \| claude \| melder_1 \| none \| )"
                         + re.escape(ROW_NEXT_OLD) + r" \| " + re.escape(ROW_OUTCOME_OLD)
                         + r"( \| [^\n]*?)\| (\S+) \| REQUIRED \|$", re.M)
    if len(pattern.findall(text)) != 1:
        raise SystemExit("S9 row not found once")
    return pattern.sub(lambda m: m.group(1) + ROW_NEXT_NEW + " | " + ROW_OUTCOME_NEW + m.group(2) + "| " + NOW
                       + " | REQUIRED |", text)


def edit_mailbox(text: str) -> str:
    """Append M1-37; refresh melder_1's last_checked (the board was read in this pass)."""
    check_widths(M1_37, "M1-37")
    roster = re.compile(r"^(\| melder_1 \| claude \| 2026-09-26T17:46:30Z \| )(\S+)( \| active \|)$", re.M)
    if len(roster.findall(text)) != 1:
        raise SystemExit("melder_1 roster row not found once")
    text = roster.sub(lambda m: m.group(1) + NOW + m.group(3), text)
    if "\n- TO: melder_1\n" in text:
        raise SystemExit("a message for melder_1 arrived; consume it first")
    return swap(text, "<!-- END USER-DEFINED: messages -->", M1_37 + "<!-- END USER-DEFINED: messages -->",
                "messages end")


def main() -> None:
    """Re-read each file, edit it in memory, and write it only with --apply (LF kept, read back)."""
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    plan = [(ROOT / STORY_REL, edit_story), (ROOT / "attention_board.md", edit_attention),
            (ROOT / "mailbox_board.md", edit_mailbox)]
    results = []
    for path, edit in plan:
        raw = path.read_bytes()
        if b"\r\n" in raw:
            raise SystemExit("CRLF in %s" % path.name)
        results.append((path, edit(raw.decode("utf-8"))))
    print("all anchors found; NOW =", NOW)
    if sys.argv[1] == "--apply":
        for path, text in results:
            path.write_bytes(text.encode("utf-8"))
            if path.read_bytes().decode("utf-8") != text:
                raise SystemExit("read-back mismatch in %s" % path.name)
        print("applied")


main()
