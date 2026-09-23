"""
TIER: intermediate (28)
GOAL: upgrade_to_normal - a lesser conduit GROWS UP in place. Lessers
      are unnamed child scopes (lesson 07); in a dynamic world one can
      be promoted to a full named citizen: registered in the world,
      discoverable by name in the cloud, able to do everything a normal
      conduit does. The promotion retains what the child already built
      for disposal, but owns a NEW EMPTY Spellbook: former definitions
      are no longer visible. Bind the new root's definitions explicitly.
      Dynamic-only verb: in a static world the same call refuses.
SURFACE EXERCISED: create_lesser_conduit, upgrade_to_normal,
                   cloud name lookup after promotion
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # local helper (see _dynamic_world)
from _dynamic_world import dynamic_spellbook

import melder as md


class Workbench:
    """Track disposal of an object created before promotion."""

    def __init__(self) -> None:
        """Start with no cleanup calls so promotion can prove retention."""
        self.cleanup_calls = 0

    def cleanup(self) -> None:
        """Record disposal by the scope retaining this creation."""
        self.cleanup_calls += 1


class IndependentWorkbench:
    """A definition owned only by the newly graduated root's Book."""


def main() -> None:
    """Promote in place, register independent definitions and prove disposal ownership."""
    book = dynamic_spellbook()
    book.bind(spell=Workbench, existence="unique_per_conduit", disposal_method_names=["cleanup"])
    root = book.conjure(dynamic=True, name="factory-floor")   # settles

    # An unnamed child scope, working away...
    worker = root.create_lesser_conduit()
    bench_before = worker.meld("Workbench")

    try:
        # ...promoted in place. Its new empty Book is already conjured.
        worker.upgrade_to_normal(name="worker")

        # It KEPT its object for disposal, without inheriting the old definition.
        assert bench_before.cleanup_calls == 0
        try:
            worker.meld("Workbench")
        except KeyError:
            print("new Book has no former Workbench definition")
        else:
            raise AssertionError("Graduation must start with an empty Book.")
        worker.bind(spell=IndependentWorkbench, existence="unique_per_conduit")
        assert isinstance(worker.meld("IndependentWorkbench"), IndependentWorkbench)
        print("new root can bind and meld its own definitions")

        # And it is now a discoverable citizen of the world.
        cloud = root.get_conduit_cloud()
        assert cloud.get_conduit_by_name("worker") is worker
        print("promoted conduit found by name:", worker.name)
        worker.cleanup()
        assert bench_before.cleanup_calls == 1
        assert isinstance(root.meld("Workbench"), Workbench)
        print("new root disposed its retained bench; former root still works")
    finally:
        worker.cleanup()
        root.cleanup()
        book.cleanup()


if __name__ == "__main__":
    main()
