"""Record S9's map of "no active spell" (a FACT note) and point the handoff and the board at the owner's pick.

Each file is re-read right before it is written and every anchor must occur exactly once.
Usage: record_no_active_map.py --check | --apply
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
  TYPE: FACT
  CLAIM: The map of "no active spell" (the owner asked for it, chat 2026-10-18: a hole object, a broken index, or a
    reserved "no_active_spell" id with a flag), read on 0.2.8255 and written to the lane's
    notes/no_active_spell_map.md. `selected_spell_id` appears 143 times in 52 files outside spell_index.py and the
    build assets; about 70 read it through an active spell and can never meet an index with nothing active; 14
    readers take an index directly (the map's table). Nine of those already guard for None - raise, skip or fall
    back - and the record's index crystal types it Optional[str], though no index can hold None today. A reserved
    id would slip past every one of those guards (truthy, not None) and be registered, gated and recorded as a
    spell; a hole object in the active slot would be treated as a spell everywhere; a broken mark over the old
    pointer would be read as the removed spell. Recommended: None plus a flag (`has_active_spell`). The fix then
    needs the pointer Optional and a clear-selection method; the removal keeping a non-empty index (frame
    registry, crystal re-emitted); `cleanup_spell` without its refusal, sending the member-removed emission;
    `Conduit.notch_spell`'s borrower fan-out when nothing was active; `_apply_add_to_index`'s ownership proven by a
    member; IndexDetail's head Optional; the hole's message naming the index.
  EVIDENCE:
  - context_compass/artifacts/direct_cleanup_refusal_20261018/notes/no_active_spell_map.md:1-136
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:437-441
  - src/melder/aether/conduit/meld/meld.py:1243-1248
  - src/melder/crystallizer/crystals/spell_index_crystal.py:79-106
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2271-2321
  - src/melder/aether/conduit/conduit.py:5735-5787
  - src/melder/aether/spellbook/spellbook.py:4155-4167
  IMPACT: The representation is the owner's call; the map gives him what each idea breaks. Open beside it: the
    minted index's selection (one state, not two), the direct doors' silence to borrowers, `cleanup_spell` being
    dynamic-only for an active version, and restore of such an index (S5).
  NEXT: The owner's pick; then the patch, the tests, the Requirements and the Acceptance for it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
""".replace("{NOW}", NOW)
OLD_NEXT = """- Next: (1) inventory the readers of `selected_spell_id` that can meet an index with nothing active; (2) the
  patch, the tests, the Requirements, the Acceptance and the EXECUTION_BOUNDARY for the owner's rule, and his word
  on the exact edits; (3) the fix, green with the GIL off and on, docs, the release note, the next free notch,
  closure, the rebuild last.
"""
NEW_NEXT = """- Next: (1) the owner's pick of how an index says "no active spell" (the lane's notes/no_active_spell_map.md:
  None plus a flag recommended); (2) the patch, the tests, the Requirements, the Acceptance and the
  EXECUTION_BOUNDARY for it, and his word on the exact edits; (3) the fix, green with the GIL off and on, docs, the
  release note, the next free notch, closure, the rebuild last.
"""
ROW_OLD = "| Inventory the readers that can meet an index with nothing active; then S9's patch for the owner's rule. |"
ROW_NEW = ("| The owner's pick of how an index says no active spell (S9's map: None plus a flag); then the patch. |")


def edit_story(text: str) -> str:
    """Add the FACT note and the new Next; stamp Updated."""
    check_widths(NOTE + NEW_NEXT, "story")
    text = swap(text, "\n## Closure Confirmation\n", "\n" + NOTE.rstrip("\n") + "\n\n## Closure Confirmation\n",
                "closure")
    text = swap(text, OLD_NEXT, NEW_NEXT, "next")
    text, count = re.subn(r"^- Updated: \S+$", "- Updated: " + NOW, text, count=1, flags=re.M)
    if count != 1:
        raise SystemExit("no Updated line")
    return text


def edit_attention(text: str) -> str:
    """Refresh the S9 row's next and updated_at."""
    pattern = re.compile(r"^(\| direct_cleanup_refusal \| in_progress \| discovery \| claude \| melder_1 \| none )"
                         + re.escape(ROW_OLD) + r"( [^\n]*?)\| (\S+) \| REQUIRED \|$", re.M)
    if len(pattern.findall(text)) != 1:
        raise SystemExit("S9 row not found once")
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
