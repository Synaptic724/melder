"""
TIER: beginner (34)
GOAL: unique vs unique_per_conduit in the SAME conduit tree - the
      side-by-side that makes scope reach click.
SURFACE EXERCISED: md.Existence.unique vs unique_per_conduit contrast
"""
import melder as md


class GlobalRegistry:
    pass


class ScopeCache:
    pass


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=GlobalRegistry, existence="unique")
    book.bind(spell=ScopeCache, existence="unique_per_conduit")
    root = book.conjure()
    child = root.create_lesser_conduit()
    grandchild = child.create_lesser_conduit()

    registries = {id(c.meld(spell=GlobalRegistry))
                  for c in (root, child, grandchild)}
    caches = {id(c.meld(spell=ScopeCache))
              for c in (root, child, grandchild)}
    assert len(registries) == 1 and len(caches) == 3
    print("same tree: 1 shared registry, 3 scope-local caches")


if __name__ == "__main__":
    main()
