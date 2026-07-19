"""
TIER: beginner (36)
GOAL: One book can conjure MANY conduits - unique still means one
      instance across all of them (the book is the world), while
      unique_per_conduit gives each conjured root its own.
SURFACE EXERCISED: repeated conjure(), world-wide vs per-conduit reach
"""
import melder as md


class WorldState:
    pass


class RootLocal:
    pass


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=WorldState, existence="unique")
    book.bind(spell=RootLocal, existence="unique_per_conduit")
    conduit_one = book.conjure()
    conduit_two = book.conjure()

    assert conduit_one.meld(spell=WorldState) is conduit_two.meld(spell=WorldState)
    assert conduit_one.meld(spell=RootLocal) is not conduit_two.meld(spell=RootLocal)
    print("two conduits, one world: shared WorldState, separate RootLocals")


if __name__ == "__main__":
    main()
