"""
TIER: intermediate (25)
GOAL: Clusters - named groups of dynamic conduits that AUTO-SHARE
      cluster-scoped spells. unique_per_conduit_cluster finally comes
      alive: one instance per cluster, shared by every member. (This
      completes the declaration parked in the expert tier's example 01.)
SURFACE EXERCISED: create_cluster, add_conduit_to_cluster,
                   existence="unique_per_conduit_cluster"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # local helper (see _dynamic_world)
from _dynamic_world import dynamic_spellbook

import melder as md


class ClusterBus:
    pass


def main() -> None:
    owner_book = dynamic_spellbook()
    owner_book.bind(spell=ClusterBus,
                    existence="unique_per_conduit_cluster")
    owner = owner_book.conjure(dynamic=True, name="cluster-owner")
    member = dynamic_spellbook().conjure(dynamic=True, name="cluster-member")

    cloud = owner.get_conduit_cloud()
    cloud.create_cluster("workers")
    cloud.add_conduit_to_cluster(owner, "workers")
    cloud.add_conduit_to_cluster(member, "workers")

    bus_a = owner.meld(spell=ClusterBus)
    bus_b = member.meld(spell=ClusterBus)
    print("one bus per cluster, shared by members:", bus_a is bus_b)


if __name__ == "__main__":
    main()
