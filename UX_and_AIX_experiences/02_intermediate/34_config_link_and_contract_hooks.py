"""
TIER: intermediate (34)
GOAL: SpellbookConfiguration hooks, families 3+4: LINKING and
      CONTRACTS - the dynamic arc becomes observable. Register on the
      owner book and watch its side of the story:
        on_conduit_post_link    - a link opened
        on_contract_created     - a spell entered a contract
        on_contract_removed     - it left
        on_conduit_post_unlink  - the link died (lesson 27's sever)
      This closes the loop: everything lessons 21-27 DO, these hooks
      SEE.
SURFACE EXERCISED: linking + contract hooks across link -> pull ->
                   sever
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # local helper (see _dynamic_world)
from _dynamic_world import dynamic_spellbook

import melder as md


class SharedThing:
    pass


def main() -> None:
    seen = []

    owner_book = dynamic_spellbook()
    config = owner_book.get_configuration()
    for name in ("on_conduit_post_link", "on_contract_created",
                 "on_contract_removed", "on_conduit_post_unlink"):
        config.add_hook(owner_book.id, name,
                        (lambda n: lambda *a, **k: seen.append(n))(name))

    spell_id = owner_book.bind(spell=SharedThing, existence="unique")
    owner = owner_book.conjure(dynamic=True, name="hook-owner")
    borrower = dynamic_spellbook().conjure(name="hook-borrower")

    owner.link(borrower)
    borrower.add_spell_to_contract(spell_id=spell_id, conduit=owner,
                                   permissions="create")
    owner.sever_link(borrower)

    print("the dynamic arc, observed:", seen)
    assert "on_conduit_post_link" in seen
    print("link/contract hooks fired - the arc is watchable end to end")


if __name__ == "__main__":
    main()
