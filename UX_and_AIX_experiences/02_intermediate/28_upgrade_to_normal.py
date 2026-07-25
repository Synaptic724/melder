"""
TIER: intermediate (28)
GOAL: upgrade_to_normal - a lesser conduit GROWS UP in place. Lessers
      are unnamed child scopes (lesson 07); in a dynamic world one can
      be promoted to a full named citizen: registered in the world,
      discoverable by name in the cloud, able to do everything a normal
      conduit does. The promotion KEEPS what the child already built -
      its creations ride through the upgrade untouched. Dynamic-only
      verb: in a static world the same call refuses.
SURFACE EXERCISED: create_lesser_conduit, upgrade_to_normal,
                   cloud name lookup after promotion
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # local helper (see _dynamic_world)
from _dynamic_world import dynamic_spellbook

import melder as md


class Workbench:
    pass


def main() -> None:
    book = dynamic_spellbook()
    book.bind(spell=Workbench, existence="unique_per_conduit")
    root = book.conjure(dynamic=True, name="factory-floor")   # settles

    # An unnamed child scope, working away...
    worker = root.create_lesser_conduit()
    bench_before = worker.meld(spell=Workbench)

    # ...promoted in place. Name granted, world registration performed.
    worker.upgrade_to_normal(name="worker")

    # It KEPT its stuff: the per-conduit bench survives the promotion.
    bench_after = worker.meld(spell=Workbench)
    assert bench_after is bench_before
    print("promotion kept the child's creations:", type(bench_after).__name__)

    # And it is now a discoverable citizen of the world.
    cloud = root.get_conduit_cloud()
    assert cloud.get_conduit_by_name("worker") is worker
    print("promoted conduit found by name:", worker.name)


if __name__ == "__main__":
    main()
