"""Reword the Conduit node's notch responsibility to spell_id and append the index moves' (no --accept).

Run from context_compass/. Edits the descriptor's JSON text in place (one string replaced, one appended after it),
then checks the file still parses and the node now carries both lines.
"""
import json
import pathlib

DESCRIPTOR = pathlib.Path("system_docs/graph/melder/aether/conduit/conduit.json")
OLD = ("names a notch's target by spell_id - the id bind or bind_inactive returned - or by spell, exactly one; "
       "resolves an id through the Book's _get_owned_spell to the exact owned version, active or parked; and refuses "
       "a version the Book does not own or one of another index before the notch transaction and again inside its "
       "seal, so a refused notch moves nothing (notch_spell, _resolve_notch_target, _owned_notch_target, 0.2.8249)")
NEW = ("names a notch's target by spell_id - the spell_id bind or bind_inactive returned - or by spell, exactly one; "
       "resolves a spell_id through the Book's _get_owned_spell to the exact owned version, active or parked; and "
       "refuses a version the Book does not own or one of another index before the notch transaction and again "
       "inside its seal, so a refused notch moves nothing (notch_spell, _resolve_notch_target, _owned_notch_target, "
       "0.2.8249)")
ADDED = ("names the parked spell add_to_spell_index and remove_from_spell_index move by spell_id or by spell, exactly "
         "one, under the notch's argument rules; resolves a spell_id through the Book's _get_owned_spell and refuses "
         "one the Book does not own before the transaction, leaving the rest to the Spellbook seams "
         "(_resolve_spell_to_move, _check_spell_argument, _owned_spell_by_id, 0.2.8249)")


def main() -> None:
    """Apply the two edits to the descriptor text and verify them."""
    raw = DESCRIPTOR.read_text(encoding="utf-8")
    old_json = json.dumps(OLD, ensure_ascii=False)
    assert raw.count(old_json) == 1
    raw = raw.replace(old_json, json.dumps(NEW, ensure_ascii=False) + ",\n    " + json.dumps(ADDED, ensure_ascii=False), 1)
    DESCRIPTOR.write_text(raw, encoding="utf-8")
    node = json.loads(raw)["nodes"]["melder.aether.conduit.conduit.Conduit"]
    assert node["responsibilities"][-2:] == [NEW, ADDED]
    print("ok; responsibilities:", len(node["responsibilities"]))


if __name__ == "__main__":
    main()
