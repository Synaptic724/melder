"""
TIER: beginner (36)
GOAL: One book conjures ONE conduit, ever (probe-proven: a second
      conjure raises RuntimeError). Multiple scopes come from lesser
      conduits; multiple roots come from multiple books.
SURFACE EXERCISED: the single-conjure law, lesser conduits, second book
"""
import melder as md


class WorldState:
    pass


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=WorldState, existence="unique")
    root = book.conjure()

    try:
        book.conjure(name="second")
        print("second conjure unexpectedly succeeded")
    except RuntimeError as err:
        print("single-conjure law held:", str(err).split(".")[0])

    # scopes within the world: lesser conduits
    child = root.create_lesser_conduit()
    assert root.meld(spell=WorldState) is child.meld(spell=WorldState)
    print("scopes via lesser conduits; roots via separate books")


if __name__ == "__main__":
    main()
