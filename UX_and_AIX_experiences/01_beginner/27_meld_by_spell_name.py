"""
TIER: beginner (27)
GOAL: The third address form - spell_name resolves by the spell's own
      name. The printed outcome documents the exact contract on 3.14t.
SURFACE EXERCISED: md.Conduit.meld(spell_name=...)
"""
import melder as md


class ReportBuilder:
    pass


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=ReportBuilder, existence="unique")
    conduit = book.conjure()

    try:
        by_name = conduit.meld(spell_name="ReportBuilder")
        print("meld(spell_name=...) answered:",
              type(by_name).__name__ if by_name is not None else None)
    except Exception as err:
        print("meld(spell_name=...) raised:", type(err).__name__, "-", err)


if __name__ == "__main__":
    main()
