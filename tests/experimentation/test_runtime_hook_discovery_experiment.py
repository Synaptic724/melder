"""Preserve scoped hook semantics and regressions discovered during lifecycle research."""

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.crystal_analysis.preflight.configuration_loss_strategy import (
    ConfigurationLossStrategy,
)
from melder.nexus.nexus import Nexus
from melder.utilities.custom_exceptions.hook_execution_error import HookExecutionError
from tests.component.melder.aether.conduit.test_conduit_component_creations import (
    _make_spellbook,
)
from tests.integration.melder.crystallizer.test_crystallizer_restore_integration import (
    _fresh_boot,
)

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell


class HookDependency:
    """Dependency-free target; construction owns no external resources."""


class HookConsumer:
    """Consumer used to distinguish root resolution from inline dependency construction."""

    def __init__(self, dependency: HookDependency) -> None:
        """Retain the normally injected dependency for identity and type assertions."""
        self.dependency = dependency


@pytest.fixture(autouse=True)
def isolated_runtime_hook_world() -> Iterator[None]:
    """
    Purpose: Keep singleton and callback references isolated between discovery cases.
    Contract: Reset roots before/after; cases clean all scopes they created.
    Yields: None for the test's isolated world.
    """
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()
    Conduit._aether = Aether()
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()
    Conduit._aether = Aether()


def test_local_conduit_event_shadows_lineage_and_clearing_reveals_it() -> None:
    """
    Purpose: Establish the actual local-versus-lineage lifecycle dispatch rule.
    Contract: A local list shadows the shared event; removing it restores inheritance.
    Returns: None. Empty lifecycle replacement restores shared event inheritance.
    """
    events: list[str] = []

    def shared(_parent: object, _child: object) -> None:
        """Record the lineage callback without changing the scopes."""
        events.append("shared")

    def local(_parent: object, _child: object) -> None:
        """Record the local override separately from the lineage callback."""
        events.append("local")

    book = _make_spellbook()
    book.get_configuration().add_hook(book.id, "on_conduit_post_created", shared)
    root = book.conjure()
    children: list[Conduit] = []
    try:
        events.clear()
        root.register_conduit_hooks({"on_conduit_post_created": local})
        child = root.create_lesser_conduit()
        children.append(child)
        assert events == ["local"]
        children.append(child.create_lesser_conduit())
        assert events == ["local", "shared"]
        root.set_conduit_hooks({"on_conduit_post_created": []})
        children.append(root.create_lesser_conduit())
        assert events == ["local", "shared", "shared"]
    finally:
        for child in reversed(children):
            child.cleanup()
        root.permanent_cleanup()


def test_local_meld_merges_a_snapshot_while_lessers_follow_the_lineage_seed() -> None:
    """
    Purpose: Contrast Meld's copied merge with lifecycle hook shadowing.
    Contract: Root local callbacks stay local; runtime containers are detached from configuration.
    Returns: None. Unsupported direct seed edits cannot mutate runtime maps.
    """
    events: list[str] = []

    def shared(_spell: Spell) -> None:
        """Identify the initial shared callback."""
        events.append("shared")

    def local(_spell: Spell) -> None:
        """Identify the root-local callback."""
        events.append("local")

    def later(_spell: Spell) -> None:
        """Identify a later controlled change to the live shared table."""
        events.append("later")

    book = _make_spellbook()
    configuration = book.get_configuration()
    configuration.add_hook(book.id, "on_meld_pre_resolve", shared)
    spell_id = book.bind(spell=HookDependency, existence="unique")
    root = book.conjure()
    left = root.create_lesser_conduit()
    root.register_conduit_hooks({"on_meld_pre_resolve": local})
    right = root.create_lesser_conduit()
    try:
        root.meld(spell_id=spell_id)
        left.meld(spell_id=spell_id)
        right.meld(spell_id=spell_id)
        assert events == ["shared", "local", "shared", "shared"]
        events.clear()
        configuration.get_meld_hooks(book.id)["on_meld_pre_resolve"].append(later)
        root.meld(spell_id=spell_id)
        left.meld(spell_id=spell_id)
        right.meld(spell_id=spell_id)
        assert events == ["shared", "local", "shared", "shared"]
    finally:
        right.cleanup()
        left.cleanup()
        root.permanent_cleanup()


def test_pooled_lesser_clears_local_meld_and_lifecycle_callbacks() -> None:
    """
    Purpose: Guard the repaired hook leak across lesser leases.
    Contract: Returning/reacquiring the same shell clears both local hook families.
    Returns: None; shared callbacks and reusable shell identity are preserved.
    """
    book = _make_spellbook()
    spell_id = book.bind(spell=HookDependency, existence="unique_per_conduit")
    root = book.conjure()
    child = root.create_lesser_conduit()
    meld_calls: list[object] = []
    lifecycle_calls: list[str] = []

    def lifecycle(_parent: object, _child: object) -> None:
        """Record the child-local lifecycle event."""
        lifecycle_calls.append("local")

    child.register_conduit_hooks({
        "on_meld_pre_resolve": meld_calls.append,
        "on_conduit_post_created": lifecycle,
    })
    grandchild = child.create_lesser_conduit()
    grandchild.cleanup()
    child.meld(spell_id=spell_id)
    child.cleanup()
    reused = root.create_lesser_conduit()
    try:
        assert reused is child
        reused.meld(spell_id=spell_id)
        assert len(meld_calls) == 1
        grandchild = reused.create_lesser_conduit()
        grandchild.cleanup()
        assert lifecycle_calls == ["local"]
    finally:
        reused.cleanup()
        root.permanent_cleanup()


@pytest.mark.parametrize("seeded", [False, True])
def test_pooled_spaces_adopt_owner_local_updates_on_the_next_lease(seeded: bool) -> None:
    """
    Purpose: Measure callback visibility on old, fresh and recycled SpellSpaces.
    Contract: Active Spaces keep their captured source; fresh and recycled Spaces use the current owner.
    Args: seeded: Whether the original shared table already contains a callback.
    Returns: None.
    """
    book = _make_spellbook()
    shared_calls: list[object] = []
    local_calls: list[object] = []
    if seeded:
        book.get_configuration().add_hook(book.id, "on_meld_pre_resolve", shared_calls.append)
    spell_id = book.bind(spell=HookDependency, existence="unique")
    root = book.conjure()
    old = root.create_spellspace()
    root.register_conduit_hooks({"on_meld_pre_resolve": local_calls.append})
    fresh = root.create_spellspace()
    try:
        old.meld(spell_id=spell_id)
        assert local_calls == []
        fresh.meld(spell_id=spell_id)
        assert len(local_calls) == 1
        old.cleanup()
        reused = root.create_spellspace()
        assert reused is old
        reused.meld(spell_id=spell_id)
        assert len(local_calls) == 2
        assert len(shared_calls) == (3 if seeded else 0)
    finally:
        fresh.cleanup()
        old.cleanup()
        root.permanent_cleanup()


def test_mixed_runtime_registration_refuses_invalid_batches_without_partial_updates() -> None:
    """
    Purpose: Guard validation before either hook family is mutated.
    Contract: An invalid Meld callback prevents the lifecycle half from being installed too.
    Returns: None; failure leaves both registries unchanged.
    """
    book = _make_spellbook()
    root = book.conjure()
    events: list[str] = []

    def lifecycle(_parent: object, _child: object) -> None:
        """Record whether the valid half of the rejected batch was installed."""
        events.append("installed")

    invalid: Any = [object()]
    try:
        with pytest.raises(TypeError):
            root.register_conduit_hooks({
                "on_conduit_post_created": lifecycle,
                "on_meld_pre_resolve": invalid,
            })
        child = root.create_lesser_conduit()
        child.cleanup()
        assert events == []
    finally:
        root.permanent_cleanup()


def test_meld_activation_dispatch_exists_but_public_registration_rejects_its_name() -> None:
    """
    Purpose: Verify the admitted event names against the actual Meld dispatcher.
    Contract: Both public setters reject on_meld_activation; internal map installation can fire it.
    Returns: None.
    """
    book = _make_spellbook()
    events: list[tuple[object, object]] = []

    def activation(spell: Spell, instance: object) -> None:
        """Record the dispatcher subject pair for a newly constructed object."""
        events.append((spell, instance))

    with pytest.raises(ValueError, match="Unknown hook name"):
        book.get_configuration().add_hook(book.id, "on_meld_activation", activation)
    spell_id = book.bind(spell=HookDependency, existence="many")
    root = book.conjure()
    try:
        with pytest.raises(ValueError, match="Unknown hook name"):
            root.register_conduit_hooks({"on_meld_activation": activation})
        root._meld.set_meld_hooks({"on_meld_activation": [activation]}, create_local_hooks=True)
        instance = root.meld(spell_id=spell_id)
        assert events == [(book.find_spell_by_id(spell_id), instance)]
    finally:
        root.permanent_cleanup()


def test_conduit_lifecycle_errors_are_suppressed_but_meld_errors_abort() -> None:
    """
    Purpose: Keep the existing two error policies visible in the proposed adjustment design.
    Contract: Lifecycle callbacks continue after failure; Meld wraps the error and stops its chain.
    Returns: None.
    """
    book = _make_spellbook()
    spell_id = book.bind(spell=HookDependency, existence="unique")
    root = book.conjure()
    events: list[str] = []

    def fail(*_subjects: object) -> None:
        """Raise a known application error from either callback family."""
        raise ValueError("callback failed")

    def good(*_subjects: object) -> None:
        """Record whether the remaining callback chain continued."""
        events.append("continued")

    try:
        root.register_conduit_hooks({"on_conduit_post_created": [fail, good]})
        child = root.create_lesser_conduit()
        child.cleanup()
        assert events == ["continued"]
        events.clear()
        root.register_conduit_hooks({"on_meld_pre_resolve": [fail, good]})
        with pytest.raises(HookExecutionError) as raised:
            root.meld(spell_id=spell_id)
        assert isinstance(raised.value.original_exception, ValueError)
        assert events == []
    finally:
        root.permanent_cleanup()


@pytest.mark.parametrize("spellspace", [False, True])
def test_internal_spell_hook_replacement_updates_warm_resolution_without_recompilation(spellspace: bool) -> None:
    """
    Purpose: Verify existing live-update machinery for the directly requested Spell.
    Contract: Pre/post apply to reuse, activation only to new creation; empty lists clear hooks.
    Args: spellspace: Use the Space front door and its unique-per-space store.
    Returns: None; the compiled context remains the same object throughout.
    """
    book = _make_spellbook()
    existence = "unique_per_spell_space" if spellspace else "unique"
    spell_id = book.bind(spell=HookDependency, existence=existence)
    root = book.conjure()
    space = root.create_spellspace()
    caller = space if spellspace else root
    events: list[str] = []
    activations: list[object] = []
    try:
        original = caller.meld(spell_id=spell_id)
        assert caller.meld(spell_id=spell_id) is original
        spell = book.find_spell_by_id(spell_id)
        context = spell._creation_context
        spell._set_hooks(
            pre_hooks=[lambda: events.append("pre")],
            activation_hooks=[activations.append],
            post_hooks=[lambda: events.append("post")],
        )
        assert caller.meld(spell_id=spell_id) is original
        assert events == ["pre", "post"] and activations == []
        caller.purge(spell_id=spell_id)
        replacement = caller.meld(spell_id=spell_id)
        assert activations == [replacement] and replacement is not original
        spell._set_hooks(pre_hooks=[], activation_hooks=[], post_hooks=[])
        before = list(events)
        assert caller.meld(spell_id=spell_id) is replacement
        assert events == before and activations == [replacement]
        assert spell._creation_context is context
    finally:
        space.cleanup()
        root.permanent_cleanup()


@pytest.mark.parametrize("root_hooks", [False, True])
def test_dependency_creation_hooks_are_not_dispatched_as_separate_root_melds(root_hooks: bool) -> None:
    """
    Purpose: Determine whether per-Spell callbacks observe inline dependency construction.
    Contract: Characterize current root versus dependency dispatch, including the hooks-aware lane.
    Args: root_hooks: Enable an activation callback on the requested consumer too.
    Returns: None; a direct dependency meld proves its callback itself is valid.
    """
    book = _make_spellbook()
    dependency_calls: list[object] = []
    root_calls: list[object] = []
    dependency_id = book.bind(
        spell=HookDependency, existence="many", activation_hooks=[dependency_calls.append],
    )
    consumer_id = book.bind(
        spell=HookConsumer, existence="many",
        activation_hooks=[root_calls.append] if root_hooks else [],
    )
    root = book.conjure()
    try:
        instance = root.meld(spell_id=consumer_id)
        assert isinstance(instance.dependency, HookDependency)
        assert dependency_calls == []
        assert root_calls == ([instance] if root_hooks else [])
        direct = root.meld(spell_id=dependency_id)
        assert dependency_calls == [direct]
    finally:
        root.permanent_cleanup()


def test_clearing_spell_hooks_during_pre_changes_the_same_calls_post_stage() -> None:
    """
    Purpose: Characterize current in-flight mutation semantics separately from bind snapshots.
    Contract: Private replacement during pre suppresses the current operation's later post stage.
    Returns: None; this is evidence for choosing a future public operation contract.
    """
    book = _make_spellbook()
    spell_id = book.bind(spell=HookDependency, existence="unique")
    spell = book.find_spell_by_id(spell_id)
    events: list[str] = []

    def pre() -> None:
        """Clear subsequent stages while the current pre callback remains in progress."""
        events.append("pre")
        spell._set_hooks(pre_hooks=[], activation_hooks=[], post_hooks=[])

    spell._set_hooks(pre_hooks=[pre], post_hooks=[lambda: events.append("post")])
    root = book.conjure()
    try:
        root.meld(spell_id=spell_id)
        assert events == ["pre"]
    finally:
        root.permanent_cleanup()


def test_spell_hooks_are_shared_by_version_across_direct_scope_requests() -> None:
    """
    Purpose: Establish whether per-Spell hooks are conduit-local or version-wide.
    Contract: Root, lesser and Space direct requests observe the same Spell hook updates.
    Returns: None; clearing the selected version affects all three callers.
    """
    book = _make_spellbook()
    calls: list[object] = []
    spell_id = book.bind(spell=HookDependency, existence="many", activation_hooks=[calls.append])
    root = book.conjure()
    lesser = root.create_lesser_conduit()
    space = root.create_spellspace()
    try:
        for caller in (root, lesser, space):
            assert caller.meld(spell_id=spell_id) is calls[-1]
        assert len(calls) == 3
        book.find_spell_by_id(spell_id)._set_hooks(activation_hooks=[])
        for caller in (root, lesser, space):
            caller.meld(spell_id=spell_id)
        assert len(calls) == 3
    finally:
        space.cleanup()
        lesser.cleanup()
        root.permanent_cleanup()


def test_lesser_cleanup_events_fire_for_hard_teardown_not_pool_return() -> None:
    """
    Purpose: Separate the physical Conduit lifecycle from reusable scope leases.
    Contract: Pool return fires neither cleanup event; permanent cleanup fires both.
    Returns: None.
    """
    book = _make_spellbook()
    starts: list[object] = []
    completes: list[object] = []
    configuration = book.get_configuration()
    configuration.add_hook(book.id, "on_conduit_cleanup_start", starts.append)
    configuration.add_hook(book.id, "on_conduit_cleanup_complete", completes.append)
    root = book.conjure()
    child = root.create_lesser_conduit()
    try:
        child.cleanup()
        assert starts == [] and completes == []
        reused = root.create_lesser_conduit()
        assert reused is child
        reused.permanent_cleanup()
        assert starts == [child] and completes == [child]
    finally:
        root.permanent_cleanup()


def test_recorded_hook_shortfalls_omit_runtime_local_and_per_spell_callbacks() -> None:
    """
    Purpose: Identify current persistence coverage before adding runtime setters.
    Contract: Preflight reports the configuration seed, but not live local or per-Spell callbacks.
    Returns: None; callback code itself remains intentionally unserialized.
    """
    crystallizer = _fresh_boot()
    book = _make_spellbook(dynamic=True)
    configuration = book.get_configuration()
    configuration.add_hook(book.id, "on_meld_pre_resolve", lambda _spell: None)
    configuration.finalize()
    activations: list[object] = []
    book.bind(spell=HookDependency, existence="unique", activation_hooks=[activations.append])
    root = book.conjure(dynamic=True)
    try:
        root.register_conduit_hooks({
            "on_meld_post_resolve": lambda _spell: None,
            "on_conduit_post_created": lambda _parent, _child: None,
        })
        checkpoint_id = crystallizer.create_checkpoint()
        window = crystallizer.checkpoint_replay_data(checkpoint_id)
        assert window["payloads"]["spellbook"][book.id]["hook_names"] == [
            "meld:on_meld_pre_resolve",
        ]
        findings = ConfigurationLossStrategy().analyze(window["payloads"])
        hook_findings = [row for row in findings if "hook " in row["detail"]]
        assert len(hook_findings) == 1
        assert "on_meld_pre_resolve" in hook_findings[0]["detail"]
    finally:
        root.permanent_cleanup()
