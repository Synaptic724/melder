"""
TIER: intermediate (07)
GOAL: Lesser conduits - lightweight CHILD SCOPES grown from a root with
      create_lesser_conduit(). A lesser conduit rides its root's world:
      it resolves the same spells without being a second root (one book
      still conjures ONE root). Lessers are unnamed by design; naming
      and upgrade_to_normal() belong to dynamic mode (lesson 21+).
      Teardown stays an explicit verb - cleanup() is yours to call.
SURFACE EXERCISED: create_lesser_conduit, meld through a child scope,
                   explicit cleanup()
"""
import melder as md


class ScopedService:
    pass


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=ScopedService, existence="unique")
    root = book.conjure()

    # A child scope: no second conjure, no second book - the family
    # grows downward from the one root.
    child = root.create_lesser_conduit()

    # "unique" is a world singleton, so the child resolves the SAME
    # instance the root does.
    from_root = root.meld(spell=ScopedService)
    from_child = child.meld(spell=ScopedService)
    assert from_root is from_child
    print("child scope melds the root's world:", type(from_child).__name__)

    # Teardown is explicit and top-down: cleaning the root conduit tears
    # its family down with it; the book guards further use.
    root.cleanup()
    book.cleanup()
    try:
        book.bind(spell=ScopedService, existence="unique")
        print("post-cleanup bind unexpectedly succeeded")
    except Exception as err:
        print("post-cleanup bind guarded:", type(err).__name__)


if __name__ == "__main__":
    main()
