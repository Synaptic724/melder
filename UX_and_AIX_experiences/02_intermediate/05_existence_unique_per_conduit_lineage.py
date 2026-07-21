"""
TIER: intermediate (05)
GOAL: unique_per_conduit_lineage - one instance per FAMILY: the root and
      every lesser descendant share the same object. A second family
      would need its own book (one book conjures ONE root - beginner
      law), so the lineage boundary IS the book boundary.
SURFACE EXERCISED: md.Existence.unique_per_conduit_lineage,
                   create_lesser_conduit
"""
import melder as md


class FamilyLedger:
    pass


def main() -> None:
    book = md.Spellbook()
    book.bind(
        spell=FamilyLedger,
        existence=md.Existence.unique_per_conduit_lineage,
    )
    # ONE conjure per book; the family GROWS from the root instead.
    root = book.conjure()
    child = root.create_lesser_conduit()
    grandchild = child.create_lesser_conduit()

    ledgers = [root.meld(spell=FamilyLedger),
               child.meld(spell=FamilyLedger),
               grandchild.meld(spell=FamilyLedger)]
    assert ledgers[0] is ledgers[1] is ledgers[2]
    print("three generations, one ledger:", type(ledgers[0]).__name__)
    print("a sibling family = a second book with its own root (one "
          "book, one conduit)")


if __name__ == "__main__":
    main()
