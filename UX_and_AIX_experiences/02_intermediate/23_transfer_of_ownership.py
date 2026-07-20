"""
TIER: intermediate (23)
GOAL: Ownership is transferable (dynamic mode) - a spell's stewardship
      moves to another conduit with an auditable preflight summary.
      Creations can move too; contracts unshare; lineage revalidates.
SURFACE EXERCISED: transfer_spell_ownership
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # local helper (see _dynamic_world)
from _dynamic_world import dynamic_spellbook

import melder as md


class MigratingService:
    pass


def main() -> None:
    source_book = dynamic_spellbook()
    spell_id = source_book.bind(spell=MigratingService, existence="unique")
    source = source_book.conjure(dynamic=True, name="old-home")
    target = dynamic_spellbook().conjure(dynamic=True, name="new-home")
    source.link(target)

    report = source.transfer_spell_ownership(
        spell=spell_id, target_conduit=target, move_creations=True,
    )
    print("transfer report keys:", sorted(report))
    moved = target.meld(spell=MigratingService)
    print("new home melds it:", type(moved).__name__)


if __name__ == "__main__":
    main()
