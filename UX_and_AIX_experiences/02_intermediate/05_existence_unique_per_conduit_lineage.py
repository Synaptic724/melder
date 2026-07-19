"""
TIER: intermediate (05)
GOAL: unique_per_conduit_lineage - one instance per FAMILY: a root and all
      its lesser descendants share; a sibling family gets its own.
SURFACE EXERCISED: md.Existence.unique_per_conduit_lineage
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
    family_one = book.conjure()
    one_child = family_one.create_lesser_conduit()
    one_grandchild = one_child.create_lesser_conduit()
    family_two = book.conjure()

    shared = {family_one.meld(spell=FamilyLedger),
              one_child.meld(spell=FamilyLedger),
              one_grandchild.meld(spell=FamilyLedger)}
    other = family_two.meld(spell=FamilyLedger)
    print("lineage one shares one ledger:", len(shared) == 1)
    print("lineage two holds its own:", other not in shared)


if __name__ == "__main__":
    main()
