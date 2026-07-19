"""
TIER: beginner (10)
GOAL: `with book:` holds the Spellbook's LOCK - an atomic registration
      batch, not auto-cleanup (source truth: __exit__ releases the lock,
      nothing else). Cleanup stays an explicit verb: book.cleanup().
SURFACE EXERCISED: with md.Spellbook() as book (lock batch), cleanup()
"""
import melder as md


class ScopedService:
    pass


def main() -> None:
    book = md.Spellbook()
    with book:  # every bind in this block happens under the book lock
        book.bind(spell=ScopedService, existence="unique")
    conduit = book.conjure()
    service = conduit.meld(spell=ScopedService)
    assert isinstance(service, ScopedService)
    print("bound atomically under the lock, melded after")

    book.cleanup()  # teardown is explicit and yours to call
    try:
        book.bind(spell=ScopedService, existence="unique")
        print("post-cleanup bind unexpectedly succeeded")
    except Exception as err:
        print("post-cleanup bind guarded:", type(err).__name__)


if __name__ == "__main__":
    main()
