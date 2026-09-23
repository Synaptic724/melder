"""Pool leases discard temporary hooks and inherit live root baselines cheaply."""

import weakref

import pytest

from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from tests.component.melder.aether.conduit import (
    test_conduit_graduation_ownership_regression as graduation_support,
)
from tests.component.melder.aether.conduit.test_conduit_graduation_ownership_regression import (
    GraduatedService,
    GraduationWorld,
)

isolated_graduation_roots = graduation_support.isolated_graduation_roots
graduation_world = graduation_support.graduation_world


def test_lesser_pool_return_discards_local_meld_hooks(graduation_world: GraduationWorld) -> None:
    """A reused lesser must stop invoking callbacks from its former lease."""
    world = graduation_world
    events: list[str] = []

    def local(*args: object) -> None:
        """Observe actual Meld dispatch on the temporary lease."""
        events.append("local")

    world.child.register_conduit_hooks({"on_meld_pre_resolve": local})
    world.child.meld(spell_id=world.parent_id)
    assert events == ["local"]
    world.child.cleanup()
    assert world.root.create_lesser_conduit() is world.child
    events.clear()
    world.child.meld(spell_id=world.parent_id)
    assert events == []


@pytest.mark.parametrize("managed", [False, True], ids=["manual", "managed"])
def test_space_inheriting_temporary_owner_hooks_resets_on_lesser_return(
    graduation_world: GraduationWorld, managed: bool,
) -> None:
    """A Space need not mutate itself to retain an old localized owner map."""
    world = graduation_world
    events: list[str] = []

    def local(*args: object) -> None:
        """Mark the owner's temporary Meld callback."""
        events.append("owner-local")

    world.child.register_conduit_hooks({"on_meld_pre_resolve": local})
    space = world.child.enter_spellspace() if managed else world.child.create_spellspace()
    space.meld(spell_id=world.parent_id)
    assert events == ["owner-local"]
    if managed:
        space.__exit__(None, None, None)
    else:
        space.cleanup()
    world.child.cleanup()
    assert world.root.create_lesser_conduit() is world.child
    again = world.child.enter_spellspace() if managed else world.child.create_spellspace()
    try:
        assert again is space
        events.clear()
        again.meld(spell_id=world.parent_id)
        assert events == []
    finally:
        if managed:
            again.__exit__(None, None, None)
        else:
            again.cleanup()


@pytest.mark.parametrize("seeded", [False, True])
def test_shared_root_updates_reach_inheritors_and_leave_localized_maps_alone(seeded: bool) -> None:
    """Empty-to-hooks, replacement and clearing propagate without per-scope updates."""
    events: list[str] = []

    def initial(*args: object) -> None:
        """Identify configuration seeds."""
        events.append("initial")

    def updated(*args: object) -> None:
        """Identify a shared runtime replacement."""
        events.append("updated")

    def local(*args: object) -> None:
        """Identify an isolated local copy."""
        events.append("local")

    config = SpellbookConfiguration("graduation-regression").with_defaults()
    if seeded:
        config.with_hooks(on_meld_pre_resolve=initial)
    world = GraduationWorld(shared_configuration=False, configuration=config)
    existing_space = world.root.create_spellspace()
    localized = world.root.create_lesser_conduit()
    localized.register_conduit_hooks({"on_meld_pre_resolve": local})
    try:
        world.root.set_conduit_hooks({"on_meld_pre_resolve": updated}, create_local_hooks=False)
        for scope in (world.root, world.child, existing_space):
            events.clear()
            scope.meld(spell_id=world.parent_id)
            assert events == ["updated"]
        events.clear()
        localized.meld(spell_id=world.parent_id)
        assert events == (["initial", "local"] if seeded else ["local"])
        world.root.set_conduit_hooks({"on_meld_pre_resolve": []}, create_local_hooks=False)
        events.clear()
        world.child.meld(spell_id=world.parent_id)
        assert events == []
        world.root.register_conduit_hooks({"on_meld_pre_resolve": updated}, create_local_hooks=False)
        existing_space.cleanup()
        assert world.root.create_spellspace() is existing_space
        events.clear()
        existing_space.meld(spell_id=world.parent_id)
        assert events == ["updated"]
        assert config.get_meld_hooks(world.book.id) == (
            {"on_meld_pre_resolve": [initial]} if seeded else {}
        )
    finally:
        world.cleanup()


def test_mixed_invalid_hook_batch_changes_neither_family(graduation_world: GraduationWorld) -> None:
    """Validation failure must not install a lifecycle callback before Meld rejects its input."""
    calls: list[object] = []
    with pytest.raises(TypeError):
        graduation_world.child.register_conduit_hooks({
            "on_conduit_activated": calls.append,
            "on_meld_pre_resolve": [42],
        })
    descendant = graduation_world.child.create_lesser_conduit()
    descendant.cleanup()
    assert calls == []
    assert not graduation_world.child.hooks_modified


@pytest.mark.parametrize("managed", [False, True])
def test_idle_spaces_adopt_current_owner_local_hooks_when_acquired(
    graduation_world: GraduationWorld, managed: bool,
) -> None:
    """Previously idle empty Spaces must agree with fresh Spaces after owner localization."""
    root = graduation_world.root
    root.prewarm_spellspaces(2)
    events: list[str] = []

    def local(*args: object) -> None:
        """Observe the later owner-local map."""
        events.append("later")

    root.register_conduit_hooks({"on_meld_pre_resolve": local})
    space = root.enter_spellspace() if managed else root.create_spellspace()
    try:
        space.meld(spell_id=graduation_world.parent_id)
        assert events == ["later"]
        assert space._meld.hooks_modified
    finally:
        if managed:
            space.__exit__(None, None, None)
        else:
            space.cleanup()
    assert not space._meld.hooks_modified


def test_pool_reset_releases_callback_objects(graduation_world: GraduationWorld) -> None:
    """Idle lesser and nested Space runtimes must not retain temporary callback objects."""
    class Callback:
        """Weak-referenceable callback with no resources or reference cycles."""

        def __call__(self, *args: object) -> None:
            """Provide an inert callable for retention assertions."""

    callback = Callback()
    retained = weakref.ref(callback)
    child = graduation_world.child
    child.register_conduit_hooks({"on_meld_pre_resolve": callback})
    space = child.create_spellspace()
    del callback
    space.cleanup()
    child.cleanup()
    assert retained() is None


@pytest.mark.parametrize("managed", [False, True], ids=["manual", "managed"])
def test_prewarming_does_not_retain_a_temporary_owner_hook_map(
    graduation_world: GraduationWorld, managed: bool,
) -> None:
    """Prewarming must publish idle Spaces with the root baseline selected.

    Contract:
        A lesser may prewarm while using local hooks and return without ever
        entering those Spaces. Its next lease must not recover the old map.
    """
    events: list[str] = []

    def temporary(*args: object) -> None:
        """Identify a callback belonging only to the previous lesser lease."""
        events.append("temporary")

    child = graduation_world.child
    child.register_conduit_hooks({"on_meld_pre_resolve": temporary})
    child.prewarm_spellspaces(2)
    child.cleanup()
    assert graduation_world.root.create_lesser_conduit() is child
    space = child.enter_spellspace() if managed else child.create_spellspace()
    try:
        space.meld(spell_id=graduation_world.parent_id)
        assert events == []
    finally:
        if managed:
            space.__exit__(None, None, None)
        else:
            space.cleanup()


def test_graduated_root_shared_updates_leave_frame_configuration_and_old_root_unchanged() -> None:
    """Graduation installs an independently mutable root baseline despite shared policy."""
    calls: list[str] = []

    def configured(*args: object) -> None:
        """Identify callbacks deliberately seeded from canonical frame policy."""
        calls.append("configured")

    def added(*args: object) -> None:
        """Identify a runtime change owned only by the graduated root."""
        calls.append("new-root")

    config = SpellbookConfiguration("graduation-regression").with_defaults()
    config.with_hooks(on_meld_pre_resolve=configured)
    world = GraduationWorld(shared_configuration=True, configuration=config)
    space = world.child.create_spellspace()
    space.cleanup()
    try:
        world.graduate()
        new_id = world.child.bind(spell=GraduatedService, existence=Existence.many)
        world.child._meld.register_meld_hooks(
            {"on_meld_pre_resolve": added}, create_local_hooks=False, overwrite=True,
        )
        space = world.child.create_spellspace()
        calls.clear()
        space.meld(spell_id=new_id)
        assert calls == ["new-root"]
        space.cleanup()
        calls.clear()
        world.root.meld(spell_id=world.parent_id)
        assert calls == ["configured"]
        assert config.get_meld_hooks(world.book.id)["on_meld_pre_resolve"] == [configured]
    finally:
        world.cleanup()
