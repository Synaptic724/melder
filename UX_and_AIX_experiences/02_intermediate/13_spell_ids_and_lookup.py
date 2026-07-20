"""
TIER: intermediate (13)
GOAL: bind() answers with the spell's id string - keep it, and the book
      will hand the living Spell record back on request.
SURFACE EXERCISED: bind() -> str, md.Spellbook.find_spell_by_id, md.Spell
"""
import melder as md


class Catalogued:
    pass


def main() -> None:
    book = md.Spellbook()
    spell_id = book.bind(spell=Catalogued, existence="unique")
    assert isinstance(spell_id, str) and spell_id
    print("bind returned id:", spell_id[:12], "...")

    record = book.find_spell_by_id(spell_id)
    assert record is not None and isinstance(record, md.Spell)
    print("book answered with a living record:", type(record).__name__)
    missing = book.find_spell_by_id("no-such-spell")
    print("unknown id answers honestly:", missing)


if __name__ == "__main__":
    main()
