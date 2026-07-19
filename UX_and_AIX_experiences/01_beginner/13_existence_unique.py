"""
TIER: beginner (13)
GOAL: unique, studied closely - ONE instance for the whole world:
      root conduit, child scopes, everywhere. The widest sharing mode.
SURFACE EXERCISED: md.Existence.unique
"""
import melder as md


class WorldClock:
    pass


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=WorldClock, existence="unique")
    root = book.conjure()
    child = root.create_lesser_conduit()
    grandchild = child.create_lesser_conduit()

    instances = {root.meld(spell=WorldClock), child.meld(spell=WorldClock),
                 grandchild.meld(spell=WorldClock)}
    assert len(instances) == 1
    print("unique: one WorldClock across three scopes")


if __name__ == "__main__":
    main()
