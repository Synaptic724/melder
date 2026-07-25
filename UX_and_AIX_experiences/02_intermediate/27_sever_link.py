"""
TIER: intermediate (27)
GOAL: sever_link - the UNDO of the whole dynamic arc. Contracts ride
      links, so when the link dies, everything shared across it dies
      with it: the borrower loses resolution of every pulled spell on
      its very next meld. Nothing is torn down eagerly - the owner's
      live instances stay alive in the owner's world; what the borrower
      loses is the RIGHT TO RESOLVE them. Severing an already-severed
      pair refuses (there is no contract left to remove).
SURFACE EXERCISED: sever_link, post-sever meld refusal
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
    owner = owner_book.conjure(dynamic=True, name="sever-owner")   # settles
    borrower = dynamic_spellbook().conjure(name="sever-borrower")  # inherits

    # The full sharing cycle from lesson 21...
    owner.link(borrower)
    borrower.add_spell_to_contract(spell_id=spell_id, conduit=owner,
                                   permissions="create")
    shared = borrower.meld(spell=SharedDirectory)
    print("while linked, the borrower resolves:", shared.lookup())

    # ...and the undo. The contract dies WITH the link.
    owner.sever_link(borrower)
    try:
        borrower.meld(spell=SharedDirectory)
        print("post-sever meld unexpectedly resolved")
    except Exception as err:
        print("post-sever meld refused:", type(err).__name__,
              "(the borrower lost the right to resolve, not the owner's object)")

    # The owner's world never noticed - its instance is untouched.
    still_alive = owner.meld(spell=SharedDirectory)
    print("owner still resolves its own spell:", still_alive is shared)

    # Severing again refuses: there is no contract left to remove.
    try:
        owner.sever_link(borrower)
        print("double sever unexpectedly succeeded")
    except Exception as err:
        print("double sever refused:", type(err).__name__)


if __name__ == "__main__":
    main()
