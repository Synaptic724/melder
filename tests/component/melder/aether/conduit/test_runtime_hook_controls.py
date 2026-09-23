"""Runtime hook controls preserve scope ownership through mutation and pooling."""

import weakref
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from typing import TYPE_CHECKING, Optional, Union

import pytest

from melder.aether.spellbook.existence.existence import Existence
from tests.component.melder.aether.conduit import (
    test_conduit_graduation_ownership_regression as graduation_support,
)
from tests.component.melder.aether.conduit.test_conduit_graduation_ownership_regression import (
    GraduationWorld,
)

if TYPE_CHECKING:
    from melder.aether.conduit.conduit import Conduit
    from melder.aether.conduit.spell_space.spell_space import SpellSpace

isolated_graduation_roots = graduation_support.isolated_graduation_roots
graduation_world = graduation_support.graduation_world


class HookRecorder:
    """Borrow an event list and record which selected callback actually executes.

    Contract:
        Callback invocation appends one label; no resources are owned. Its
        cleanup method detects any incorrect disposal of borrowed callbacks.
    """

    def __init__(self, events: list[str], label: str) -> None:
        """Retain the test's event sink and initialize disposal accounting."""
        self.events = events
        self.label = label
        self.cleanup_count = 0

    def __call__(self, *args: object) -> None:
        """Record one invocation independently of the event's argument shape."""
        self.events.append(self.label)

    def cleanup(self) -> None:
        """Detect forbidden ownership of this borrowed application callback."""
        self.cleanup_count += 1


class DisposalHookProbe:
    """Run a test observation during Melder's ordinary creation disposal.

    Contract:
        The callback is installed after construction; cleanup invokes it once
        per request from the creation store. The probe owns no external resource.
    """

    def __init__(self) -> None:
        """Start without a disposal observer; tests install the scope observation."""
        self.on_dispose: Optional[Callable[[], None]] = None

    def cleanup(self) -> None:
        """Invoke the optional observer during the existing disposal pipeline."""
        if self.on_dispose is not None:
            self.on_dispose()


def test_lifecycle_shared_updates_preserve_local_event_shadowing(
    graduation_world: GraduationWorld,
) -> None:
    """Shared replace/clear/re-add reaches lessers without changing local shadowing.

    Contract:
        Replacing a local event with an empty list reveals the current shared
        event. Shared updates do not replace another scope's explicit overlay.
    """
    world = graduation_world
    events: list[str] = []
    first = HookRecorder(events, "first")
    second = HookRecorder(events, "second")
    local = HookRecorder(events, "local")
    root_hooks = [first]
    world.root.register_conduit_hooks(
        {"on_conduit_post_created": root_hooks}, create_local_hooks=False,
    )
    root_hooks.append(second)
    world.child.create_lesser_conduit().cleanup()
    assert events == ["first"]
    world.child.register_conduit_hooks({"on_conduit_post_created": local})
    world.root.set_conduit_hooks(
        {"on_conduit_post_created": second}, create_local_hooks=False,
    )
    events.clear()
    world.root.create_lesser_conduit().cleanup()
    world.child.create_lesser_conduit().cleanup()
    assert events == ["second", "local"]
    world.child.set_conduit_hooks({"on_conduit_post_created": []})
    events.clear()
    world.child.create_lesser_conduit().cleanup()
    assert events == ["second"]
    world.root.set_conduit_hooks({}, create_local_hooks=False)
    events.clear()
    world.child.create_lesser_conduit().cleanup()
    assert events == []
    world.root.register_conduit_hooks(
        {"on_conduit_post_created": first}, create_local_hooks=False,
    )
    world.child.create_lesser_conduit().cleanup()
    assert events == ["first"]
    assert not world.root.hooks_modified
    assert not world.child.hooks_modified


def test_setting_one_family_preserves_the_other_and_empty_setting_clears_both(
    graduation_world: GraduationWorld,
) -> None:
    """Set replaces selected families; empty replacement selects both.

    Contract:
        Meld registration remains additive unless overwrite is requested.
        Inputs are copied so later caller-container edits do not change hooks.
    """
    world = graduation_world
    events: list[str] = []
    life = HookRecorder(events, "life")
    first = HookRecorder(events, "first")
    second = HookRecorder(events, "second")
    callbacks = [first]
    world.root.register_conduit_hooks({
        "on_conduit_post_created": life,
        "on_meld_pre_resolve": callbacks,
    })
    callbacks.clear()
    world.root.set_conduit_hooks({"on_meld_pre_resolve": second}, overwrite=False)
    world.root.meld(spell_id=world.parent_id)
    assert events == ["first", "second"]
    world.root.set_conduit_hooks({"on_meld_pre_resolve": second})
    events.clear()
    world.root.meld(spell_id=world.parent_id)
    world.root.create_lesser_conduit().cleanup()
    assert events == ["second", "life"]
    world.root.set_conduit_hooks({})
    events.clear()
    world.root.meld(spell_id=world.parent_id)
    world.root.create_lesser_conduit().cleanup()
    assert events == []
    world.root.register_conduit_hooks({"on_meld_pre_resolve": first})
    world.root.meld(spell_id=world.parent_id)
    assert events == ["first"]
    assert world.root.hooks_modified


@pytest.mark.parametrize("scope", ["lesser", "space"])
def test_direct_meld_registration_adds_replaces_and_resets_local_callbacks(
    graduation_world: GraduationWorld, scope: str,
) -> None:
    """Direct Meld controls retain order and reset after the owning lease ends.

    Args:
        scope: Runtime owner whose cleanup must restore the root baseline.
    """
    world = graduation_world
    target = world.child if scope == "lesser" else world.child.create_spellspace()
    events: list[str] = []
    first = HookRecorder(events, "first")
    second = HookRecorder(events, "second")
    target._meld.register_meld_hooks({})
    assert not target._meld.hooks_modified
    target._meld.register_meld_hooks({"on_meld_pre_resolve": first})
    target._meld.register_meld_hooks({"on_meld_pre_resolve": (second,)})
    target.meld(spell_id=world.parent_id)
    assert events == ["first", "second"]
    target._meld.register_meld_hooks({"on_meld_pre_resolve": second}, overwrite=True)
    events.clear()
    target.meld(spell_id=world.parent_id)
    assert events == ["second"]
    target._meld.register_meld_hooks({}, overwrite=True)
    events.clear()
    target.meld(spell_id=world.parent_id)
    assert events == []
    assert target._meld.hooks_modified
    target.cleanup()
    assert not target._meld.hooks_modified
    assert first.cleanup_count == second.cleanup_count == 0


@pytest.mark.parametrize("surface", ["conduit", "lesser-meld", "space-meld"])
def test_shared_mutation_requires_a_normal_root(
    graduation_world: GraduationWorld, surface: str,
) -> None:
    """A lesser or SpellSpace cannot edit its root's shared baseline.

    Contract:
        Refusal precedes any mutation or callback invocation.
    """
    world = graduation_world
    events: list[str] = []
    callback = HookRecorder(events, "forbidden")
    space = world.child.create_spellspace()
    try:
        register = {
            "conduit": world.child.register_conduit_hooks,
            "lesser-meld": world.child._meld.register_meld_hooks,
            "space-meld": space._meld.register_meld_hooks,
        }[surface]
        with pytest.raises(RuntimeError, match="normal root"):
            register({"on_meld_pre_resolve": callback}, create_local_hooks=False)
        world.root.meld(spell_id=world.parent_id)
        world.child.meld(spell_id=world.parent_id)
        space.meld(spell_id=world.parent_id)
        assert events == []
        assert not world.child.hooks_modified
        assert not space._meld.hooks_modified
    finally:
        space.cleanup()


@pytest.mark.parametrize("direct", [False, True], ids=["conduit", "meld"])
@pytest.mark.parametrize("payload,error", [
    ({"unknown": []}, ValueError),
    ({"on_meld_pre_resolve": [None]}, TypeError),
    ({"on_meld_pre_resolve": 42}, TypeError),
    (42, TypeError),
])
def test_invalid_replacement_preserves_existing_callbacks(
    graduation_world: GraduationWorld, direct: bool,
    payload: object, error: type[Exception],
) -> None:
    """Rejected batches cannot erase the previously registered hook family.

    Args:
        direct: Exercise Meld registration instead of the Conduit facade.
        payload: Deliberately invalid external input.
        error: Documented exception for that malformed input.
    """
    world = graduation_world
    events: list[str] = []
    original = HookRecorder(events, "original")
    register = world.root._meld.register_meld_hooks if direct else world.root.register_conduit_hooks
    register({"on_meld_pre_resolve": original}, create_local_hooks=False)
    with pytest.raises(error):
        register(payload, create_local_hooks=False, overwrite=True)
    world.child.meld(spell_id=world.parent_id)
    assert events == ["original"]
    assert not world.root.hooks_modified


@pytest.mark.parametrize("muted", [False, True])
def test_internal_reference_installation_is_temporary_and_never_broadcasts(
    graduation_world: GraduationWorld, muted: bool,
) -> None:
    """The legacy reference setter remains distinct from shared publication.

    Contract:
        A borrowed replacement, including None, affects this lease only and
        returns to the live root baseline when the lesser is recycled.
    """
    world = graduation_world
    events: list[str] = []
    baseline = HookRecorder(events, "baseline")
    temporary = HookRecorder(events, "temporary")
    world.root.register_conduit_hooks({"on_meld_pre_resolve": baseline}, create_local_hooks=False)
    world.child._meld.set_meld_hooks(None if muted else {"on_meld_pre_resolve": [temporary]})
    assert world.child.hooks_modified
    world.child.meld(spell_id=world.parent_id)
    assert events == ([] if muted else ["temporary"])
    events.clear()
    world.root.meld(spell_id=world.parent_id)
    assert events == ["baseline"]
    world.child.cleanup()
    assert world.root.create_lesser_conduit() is world.child
    events.clear()
    world.child.meld(spell_id=world.parent_id)
    assert events == ["baseline"]
    assert not world.child.hooks_modified


def test_permanent_space_cleanup_retires_its_meld_and_releases_callbacks(
    graduation_world: GraduationWorld,
) -> None:
    """Retaining the retired Meld cannot keep a former Space callback alive.

    Contract:
        Permanent Space teardown cleans the owned runtime, and later mutation
        is refused. Borrowed callbacks are released without calling cleanup.
    """
    space = graduation_world.root.create_spellspace()
    runtime = space._meld
    callback = HookRecorder([], "temporary")
    retained = weakref.ref(callback)
    runtime.register_meld_hooks({"on_meld_pre_resolve": callback})
    space.permanent_cleanup()
    assert runtime.cleaned
    assert callback.cleanup_count == 0
    del callback
    assert retained() is None
    with pytest.raises(RuntimeError):
        runtime.register_meld_hooks({})


@pytest.mark.parametrize("scope", ["lesser", "manual", "managed"])
def test_hook_restoration_happens_after_creation_disposal(
    graduation_world: GraduationWorld, scope: str,
) -> None:
    """Disposal observes current-lease hook state, then pool return restores it.

    Args:
        scope: Lesser or one of the two Space return paths.
    """
    world = graduation_world
    spell_id = world.root.bind(
        spell=DisposalHookProbe,
        existence=Existence.unique_per_conduit if scope == "lesser" else Existence.unique_per_spell_space,
        disposal_method_names=["cleanup"],
    )
    target: Union[Conduit, SpellSpace] = world.child
    if scope == "manual":
        target = world.child.create_spellspace()
    elif scope == "managed":
        target = world.child.enter_spellspace()
    callback = HookRecorder([], "temporary")
    target._meld.register_meld_hooks({"on_meld_pre_resolve": callback})
    probe = target.meld(spell_id=spell_id)
    states: list[bool] = []

    def observe() -> None:
        """Record the diagnostic flag while the store invokes cleanup."""
        states.append(target._meld.hooks_modified)

    probe.on_dispose = observe
    if scope == "managed":
        target.__exit__(None, None, None)
    else:
        target.cleanup()
    assert states == [True]
    assert not target._meld.hooks_modified


def test_concurrent_shared_registration_loses_no_callbacks(
    graduation_world: GraduationWorld,
) -> None:
    """Conduit and direct Meld writers serialize shared additive publication.

    Contract:
        Every accepted registration fires exactly once when a lesser later
        resolves. Worker failures propagate to the test and waits are bounded.
    """
    world = graduation_world
    events: list[str] = []
    callback = HookRecorder(events, "shared")
    barrier = Barrier(4, timeout=5)

    def register(index: int) -> None:
        """Append through alternating entrypoints against the same root map."""
        barrier.wait()
        method = world.root.register_conduit_hooks if index % 2 else world.root._meld.register_meld_hooks
        for _ in range(50):
            method({"on_meld_pre_resolve": callback}, create_local_hooks=False)

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(register, index) for index in range(4)]
        for future in futures:
            future.result(timeout=5)
    world.child.meld(spell_id=world.parent_id)
    assert events == ["shared"] * 200
    assert not world.root.hooks_modified


def test_root_publication_can_overlap_space_localization_and_pool_return(
    graduation_world: GraduationWorld,
) -> None:
    """Shared dict edits cannot break local copying or leak a previous Space lease.

    Contract:
        Each worker owns its managed Space. Root publication may occur between
        event selections; the final lease must use only the final shared hooks.
    """
    world = graduation_world
    world.root.prewarm_spellspaces(3)
    world.root.meld(spell_id=world.parent_id)
    events: list[str] = []
    shared = HookRecorder(events, "shared")
    local = HookRecorder(events, "local")
    barrier = Barrier(3, timeout=5)

    def publish() -> None:
        """Replace and clear shared event entries while other scopes localize."""
        barrier.wait()
        for _ in range(300):
            world.root.set_conduit_hooks({"on_meld_pre_resolve": shared}, create_local_hooks=False)
            world.root.set_conduit_hooks({}, create_local_hooks=False)

    def lease() -> None:
        """Copy inherited events, resolve and recycle on one confined worker."""
        barrier.wait()
        for _ in range(150):
            with world.root.enter_spellspace() as space:
                space._meld.register_meld_hooks({"on_meld_post_resolve": local})
                space.meld(spell_id=world.parent_id)

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(publish), executor.submit(lease), executor.submit(lease)]
        for future in futures:
            future.result(timeout=5)
    final = HookRecorder(events, "final")
    world.root.set_conduit_hooks({"on_meld_pre_resolve": final}, create_local_hooks=False)
    events.clear()
    with world.root.enter_spellspace() as space:
        space.meld(spell_id=world.parent_id)
    assert events == ["final"]
