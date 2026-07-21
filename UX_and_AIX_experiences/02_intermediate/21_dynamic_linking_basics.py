"""
TIER: intermediate (21)
GOAL: Dynamic mode END TO END under the settle-then-inherit law:
      1) A fresh world has no mode yet. The FIRST conjure(dynamic=True)
         SETTLES the world dynamic - and the posture locks.
      2) Every later book just attaches: a plain conjure() INHERITS the
         world's mode. You never repeat the flag to stay dynamic.
      3) link() opens a contract between two named conduits, and
         add_spell_to_contract shares one spell across it.
SURFACE EXERCISED: conjure(dynamic=True) settlement, plain-conjure
                   inheritance, link, add_spell_to_contract, meld
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # local helper (see _dynamic_world)
from _dynamic_world import dynamic_spellbook

import melder as md


class SharedDirectory:
    def lookup(self) -> str:
        return "found"


def main() -> None:
    owner_book = dynamic_spellbook()
    spell_id = owner_book.bind(spell=SharedDirectory, existence="unique")

    # SETTLEMENT - the first conjure on a fresh world carries the world
    # decision: dynamic=True SETTLES the world dynamic, and it locks.
    owner = owner_book.conjure(dynamic=True, name="owner")

    # INHERITANCE - the borrower does not ask. It attaches to a world
    # that is already dynamic; a plain conjure() inherits the mode.
    borrower = dynamic_spellbook().conjure(name="borrower")

    assert owner.link(borrower) is True
    # Sharing is a PULL: the borrower asks, and the conduit it NAMES
    # must OWN the spell being pulled.
    borrower.add_spell_to_contract(spell_id=spell_id, conduit=owner,
                                   permissions="create")
    shared = borrower.meld(spell=SharedDirectory)
    print("borrower melded the owner's spell:", shared.lookup())
    print("settled once at first conjure; every later conduit inherited")


if __name__ == "__main__":
    main()
