"""
TIER: intermediate (22)
GOAL: Permissions LIVE - they are the sharing policy on a contract.
      "create" lets the borrower construct/resolve fully; "read" is
      resolve-only across the link. This is where the vocabulary from
      the cheatsheet finally does something.
SURFACE EXERCISED: add_spell_to_contract(permissions="read"/"create")
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # local helper (see _dynamic_world)
from _dynamic_world import dynamic_spellbook

import melder as md


class OpenService:
    pass


class GuardedService:
    pass


def main() -> None:
    owner_book = dynamic_spellbook()
    open_id = owner_book.bind(spell=OpenService, existence="unique")
    guarded_id = owner_book.bind(spell=GuardedService, existence="unique")
    owner = owner_book.conjure(dynamic=True, name="perm-owner")
    borrower = dynamic_spellbook().conjure(dynamic=True, name="perm-borrower")
    owner.link(borrower)

    owner.add_spell_to_contract(spell_id=open_id, conduit=borrower,
                                permissions="create")
    owner.add_spell_to_contract(spell_id=guarded_id, conduit=borrower,
                                permissions="read")

    print("create-shared meld:", type(borrower.meld(spell=OpenService)).__name__)
    try:
        result = borrower.meld(spell=GuardedService)
        print("read-shared meld answered:", type(result).__name__,
              "(read = resolve-only; construction rights stay with the owner)")
    except Exception as err:
        print("read-shared meld refused:", type(err).__name__)


if __name__ == "__main__":
    main()
