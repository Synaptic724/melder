"""
TIER: intermediate (06)
GOAL: Spell metadata via bind kwargs (landed 2026-07-19): any extra
      keyword on bind() threads into the Spell's own kwargs channel and
      lands on spell.metadata - tag your registrations with ownership,
      tiers, or agent breadcrumbs. Native bind values are unstealable:
      declared parameters capture their names before **kwargs collects.
SURFACE EXERCISED: bind(**extras) -> Spell.metadata, find_spell_by_id
"""
import melder as md


class PaymentsApi:
    pass


def main() -> None:
    book = md.Spellbook()
    spell_id = book.bind(
        spell=PaymentsApi, existence="unique",
        owner_team="payments", tier="gold", reviewed="2026-07-19",
    )
    spell = book.find_spell_by_id(spell_id)
    assert spell.metadata == {
        "owner_team": "payments", "tier": "gold", "reviewed": "2026-07-19",
    }
    print("spell born with metadata:", spell.metadata)

    try:
        book.bind(spell=PaymentsApi, existence="unique", spell_id="jacked")
        print("collision unexpectedly accepted")
    except TypeError as err:
        print("native Spell params stay sovereign:", type(err).__name__)


if __name__ == "__main__":
    main()
