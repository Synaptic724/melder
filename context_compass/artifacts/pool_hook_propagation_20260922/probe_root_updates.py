"""Characterize current root-update visibility without modifying runtime source."""

import json
from pathlib import Path
import sys
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from melder.aether.conduit.spell_space.spell_space import SpellSpace

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from tests.component.melder.aether.conduit.test_conduit_graduation_ownership_regression import GraduationWorld


def reset_world() -> None:
    """Reset process-local test owners before each independent characterization case."""
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()
    Conduit._aether = Aether()


def observe(scope: Union[Conduit, SpellSpace], spell_id: str, events: list[str]) -> list[str]:
    """Return callbacks actually invoked for one public Meld request."""
    events.clear()
    scope.meld(spell_id=spell_id)
    return list(events)


def characterize(*, seeded: bool, mode: str) -> dict[str, object]:
    """Compare existing, fresh and recycled scopes after one real root API call.

    Contract:
        register uses the public Conduit facade. reference_install uses the
        existing internal Meld setter's create_local_hooks=False mode; it does
        not claim that this is a supported public root-propagation API.
    """
    reset_world()
    events: list[str] = []

    def initial(*args: object) -> None:
        """Identify a hook supplied by initial configuration."""
        events.append("initial")

    def added(*args: object) -> None:
        """Identify the hook added or installed after consumers already exist."""
        events.append("added")

    config = SpellbookConfiguration("graduation-regression").with_defaults()
    if seeded:
        config.with_hooks(on_meld_pre_resolve=initial)
    world = GraduationWorld(shared_configuration=False, configuration=config)
    existing_space = world.root.create_spellspace()
    try:
        observe(world.child, world.parent_id, events)
        observe(existing_space, world.parent_id, events)
        before = {
            "root_has_seed_map": world.root._meld_hooks is not None,
            "root_effective_is_seed": world.root._meld._meld_hooks is world.root._meld_hooks,
            "child_effective_is_root_effective": world.child._meld._meld_hooks is world.root._meld._meld_hooks,
            "space_effective_is_root_effective": existing_space._meld._meld_hooks is world.root._meld._meld_hooks,
        }
        if mode == "register":
            world.root.register_conduit_hooks({"on_meld_pre_resolve": added})
        else:
            world.root._meld.set_meld_hooks(
                {"on_meld_pre_resolve": [added]}, create_local_hooks=False,
            )
        fresh_child = world.root.create_lesser_conduit()
        fresh_space = world.root.create_spellspace()
        outcomes = {
            "root": observe(world.root, world.parent_id, events),
            "existing_lesser": observe(world.child, world.parent_id, events),
            "fresh_lesser": observe(fresh_child, world.parent_id, events),
            "existing_space": observe(existing_space, world.parent_id, events),
            "fresh_space": observe(fresh_space, world.parent_id, events),
        }
        existing_space.cleanup()
        recycled = world.root.create_spellspace()
        assert recycled is existing_space
        outcomes["recycled_space"] = observe(recycled, world.parent_id, events)
        return {"seeded": seeded, "mode": mode, "before_aliases": before, "callbacks": outcomes}
    finally:
        world.cleanup()
        reset_world()


def main() -> None:
    """Run four finite cases, retain a JSON report and emit the same observed data."""
    results = [
        characterize(seeded=False, mode="register"),
        characterize(seeded=True, mode="register"),
        characterize(seeded=False, mode="reference_install"),
        characterize(seeded=True, mode="reference_install"),
    ]
    report = json.dumps(results, indent=2)
    Path(__file__).with_name("root_update_results.json").write_text(report, encoding="utf-8")
    sys.stdout.write(report + "\n")


if __name__ == "__main__":
    main()
