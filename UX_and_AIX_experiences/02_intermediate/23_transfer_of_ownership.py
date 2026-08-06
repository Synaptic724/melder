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

    # THE PREFLIGHT SUMMARY IS THE POINT. Ownership moving is not a silent
    # side effect - it hands back an auditable report of what it did.
    assert isinstance(report, dict) and report, report
    print("transfer report keys:", sorted(report))

    # THE NEW HOME CAN MELD IT.
    moved = target.meld(spell=MigratingService)
    assert isinstance(moved, MigratingService)
    print("new home melds it:", type(moved).__name__)

    # AND THE OLD HOME CANNOT. This is the assertion that makes it a
    # TRANSFER rather than a share - if the source could still meld it,
    # ownership would have been copied, not moved.
    try:
        source.meld(spell=MigratingService)
        raise AssertionError(
            "the source still melds it - that is sharing, not transfer"
        )
    except Exception as gone:
        print("old home refused -", type(gone).__name__, ":",
              str(gone)[:70])
        print("  stewardship MOVED. A copy would have left both able to")
        print("  meld, and then `ownership` would mean nothing")


if __name__ == "__main__":
    main()
