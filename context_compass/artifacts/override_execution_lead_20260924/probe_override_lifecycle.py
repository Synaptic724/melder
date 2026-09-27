"""Observe override lifecycle effects without changing production code or timing it.

Run from the repository root with .venv_new/Scripts/python.exe. The script writes
lifecycle_observations.json beside itself. Each case owns an isolated Aether world;
class-local constructor and cleanup events demonstrate which objects exist before
and after scope disposal. These observations characterize current behavior and do
not prescribe the future pruning policy.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / "src"))

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook


def observe_case(existence: str, in_space: bool, sibling: bool) -> dict[str, object]:
    """Observe one supplied dependency under a real creation/disposal lifecycle.

    Contract:
        Own an isolated world, disable disk caching, supply an unregistered object
        into a required socket, and record construction, root activation and
        teardown order. A two-socket consumer keeps the other dependency live.
        Cleanup runs even when a runtime error interrupts the observation.

    Args:
        existence: Registered dependency lifetime.
        in_space: Select the SpellSpace rather than the Conduit front door.
        sibling: Whether another socket still requests the registered dependency.

    Returns:
        Plain values describing the observed lifecycle and reference checks.
    """
    events: list[str] = []

    class Dependency:
        """Observable resource whose factory defaults distinguish it from supplied values."""

        def __init__(self, tag: str = "generated") -> None:
            """Record construction and initialize this instance's disposal counter."""
            self.tag = tag
            self.disposed = 0
            events.append(f"construct:{tag}")

        def dispose(self) -> None:
            """Record explicit disposal without destroying the readable diagnostic fields."""
            self.disposed += 1
            events.append(f"dispose:{self.tag}")

    class SingleConsumer:
        """A root with one injectable dependency that is replaced by the caller."""

        def __init__(self, left: Dependency) -> None:
            """Retain the supplied dependency and record root construction."""
            self.left = left
            events.append("construct:root")

    class PairConsumer:
        """A root with another socket that still needs the registered dependency."""

        def __init__(self, left: Dependency, right: Dependency) -> None:
            """Retain both references so shared and occurrence-local behavior is observable."""
            self.left = left
            self.right = right
            events.append("construct:root")

    def on_activation(instance: object) -> None:
        """Record root activation without mutating the supplied object or registration."""
        events.append(f"activate:{type(instance).__name__}")

    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    book = Spellbook()
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    book._aetheric_frame_configuration.with_system_caching_enabled(False)
    conduit = None
    space = None
    try:
        book.bind(spell=Dependency, existence=existence, disposal_method_names=["dispose"])
        root_id = book.bind(
            spell=PairConsumer if sibling else SingleConsumer,
            existence="many",
            activation_hooks=[on_activation],
        )
        supplied = Dependency("external")
        events.clear()
        conduit = book.conjure()
        space = conduit.create_spellspace() if in_space else None
        caller = space if space is not None else conduit
        result = caller.meld(spell_id=root_id, override={"left": supplied})
        observation: dict[str, object] = {
            "existence": existence,
            "door": "spellspace" if in_space else "conduit",
            "sibling": sibling,
            "supplied_identity_preserved": result.left is supplied,
            "sibling_is_generated": result.right.tag == "generated" if sibling else None,
            "after_meld": list(events),
        }
        if space is not None:
            space.cleanup()
            space = None
        observation["after_space_cleanup"] = list(events)
        conduit.cleanup()
        conduit = None
        observation["after_conduit_cleanup"] = list(events)
        observation["supplied_disposal_count"] = supplied.disposed
        return observation
    finally:
        if space is not None:
            space.cleanup()
        if conduit is not None:
            conduit.cleanup()
        Aether._reset_singleton_for_tests()


def main() -> None:
    """Write untimed observations for isolated normal and SpellSpace creation scopes."""
    cases = (
        ("many", False),
        ("many", True),
        ("unique", False),
        ("unique_per_conduit", False),
        ("unique_per_spell_space", True),
    )
    observations = [
        observe_case(existence, in_space, sibling)
        for existence, in_space in cases
        for sibling in (False, True)
    ]
    Path(__file__).with_name("lifecycle_observations.json").write_text(
        json.dumps(observations, indent=2) + "\n", encoding="utf-8",
    )


if __name__ == "__main__":
    main()
