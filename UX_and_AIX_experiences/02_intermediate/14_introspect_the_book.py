"""
TIER: intermediate (14)
GOAL: The book is inspectable - the spells mapping hands back every
      registration as SpellIndex -> Spell, the system's two domain
      nouns, straight off the root namespace.
SURFACE EXERCISED: md.Spellbook.spells, md.SpellIndex, md.Spell
"""
import melder as md


class Alpha:
    pass


class Beta:
    pass


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=Alpha, existence="unique")
    book.bind(spell=Beta, existence="many")

    registry = book.spells
    assert len(registry) >= 2
    for index, spell in registry.items():
        assert isinstance(index, md.SpellIndex)
        assert isinstance(spell, md.Spell)
    print("book holds", len(registry), "spells, typed as SpellIndex -> Spell")


if __name__ == "__main__":
    main()
