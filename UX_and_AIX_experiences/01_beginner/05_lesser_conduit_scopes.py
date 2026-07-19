"""
TIER: beginner (05)
GOAL: Scopes without ceremony - a lesser conduit is a child resolution
      scope; unique_per_conduit gives each scope its own instance while
      plain unique stays shared across the family.
SURFACE EXERCISED: md.Spellbook, md.Existence.unique_per_conduit,
                   md.Conduit.create_lesser_conduit
"""
import melder as md


class AppWideConfig:
    pass


class PerScopeSession:
    pass


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=AppWideConfig, existence="unique")
    book.bind(spell=PerScopeSession, existence="unique_per_conduit")
    root = book.conjure()
    child = root.create_lesser_conduit()

    assert root.meld(spell=AppWideConfig) is child.meld(spell=AppWideConfig)
    print("unique: shared across root and child")

    root_session = root.meld(spell=PerScopeSession)
    child_session = child.meld(spell=PerScopeSession)
    assert root_session is not child_session
    assert child.meld(spell=PerScopeSession) is child_session
    print("unique_per_conduit: one per scope, stable within it")


if __name__ == "__main__":
    main()
