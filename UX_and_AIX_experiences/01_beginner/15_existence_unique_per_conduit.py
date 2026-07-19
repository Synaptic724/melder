"""
TIER: beginner (15)
GOAL: unique_per_conduit - each conduit scope holds its OWN single instance;
      stable inside the scope, separate across scopes.
SURFACE EXERCISED: md.Existence.unique_per_conduit
"""
import melder as md


class ScopeLocalSession:
    pass


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=ScopeLocalSession, existence="unique_per_conduit")
    root = book.conjure()
    child_a = root.create_lesser_conduit()
    child_b = root.create_lesser_conduit()

    a1, a2 = child_a.meld(spell=ScopeLocalSession), child_a.meld(spell=ScopeLocalSession)
    b1 = child_b.meld(spell=ScopeLocalSession)
    r1 = root.meld(spell=ScopeLocalSession)
    assert a1 is a2
    assert len({id(a1), id(b1), id(r1)}) == 3
    print("unique_per_conduit: stable within a scope, three scopes = three instances")


if __name__ == "__main__":
    main()
