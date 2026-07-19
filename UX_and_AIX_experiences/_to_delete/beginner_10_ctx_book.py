"""
TIER: beginner (10)
GOAL: The tidy ending - Spellbook is a context manager, so the whole
      bind/conjure/meld session can live in a with-block and clean up
      on exit. The guard behavior after exit is printed honestly.
SURFACE EXERCISED: with md.Spellbook() as book, cleanup guards
"""
import melder as md


class ScopedService:
    pass


def main() -> None:
    with md.Spellbook() as book:
        book.bind(spell=ScopedService, existence="unique")
        conduit = book.conjure()
        service = conduit.meld(spell=ScopedService)
        assert isinstance(service, ScopedService)
        print("inside the with-block: bound, conjured, melded")

    try:
        book.bind(spell=ScopedService, existence="unique")
        print("post-exit bind unexpectedly succeeded")
    except Exception as err:
        print("post-exit bind guarded:", type(err).__name__)


if __name__ == "__main__":
    main()
