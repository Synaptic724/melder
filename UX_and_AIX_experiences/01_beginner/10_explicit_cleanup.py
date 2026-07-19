"""
TIER: beginner (10)
GOAL: Teardown is a verb you own - conduit.cleanup() then book.cleanup(),
      in that order, and a cleaned book refuses further work loudly.
      (Disposal hooks you registered fire during this walk - see 08/35.)
SURFACE EXERCISED: cleanup verbs, post-cleanup guards
"""
import melder as md


class Service:
    pass


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=Service, existence="unique")
    conduit = book.conjure()
    assert isinstance(conduit.meld(spell=Service), Service)

    conduit.cleanup()
    book.cleanup()
    print("world torn down: conduit first, book second")

    try:
        book.bind(spell=Service, existence="unique")
        print("post-cleanup bind unexpectedly succeeded")
    except Exception as err:
        print("cleaned book guards itself:", type(err).__name__)


if __name__ == "__main__":
    main()
