"""Normal setup, hook defaults and failure recovery through public graduation."""

from concurrent.futures import ThreadPoolExecutor
from threading import Event

import pytest

from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.spellbook_creation_system import SpellbookCreationSystem
from melder.utilities.synchronization.creation_gate import CreationGate
from tests.component.melder.aether.conduit import (
    test_conduit_graduation_ownership_regression as graduation_support,
)
from tests.component.melder.aether.conduit.test_conduit_graduation_ownership_regression import (
    GraduatedService,
    GraduationWorld,
    LaterParentService,
)
from tests.integration.melder.crystallizer.test_crystallizer_restore_integration import (
    _activate_crystallizer,
)

graduation_world = graduation_support.graduation_world
isolated_graduation_roots = graduation_support.isolated_graduation_roots


def test_upgrade_uses_normal_default_or_frame_owned_configuration(
    graduation_world: GraduationWorld,
) -> None:
    """Local omission creates defaults; shared mode retains its canonical policy."""
    shared = graduation_world.book._is_frame_owned_shared_configuration()
    graduation_world.graduate()
    config = graduation_world.child._spellbook.get_configuration()
    assert (config is graduation_world.configuration) is shared
    assert config.get_property("phase_scheduler_workers_per_spellbook") == (1 if shared else 5)
    assert config._frozen


def test_upgrade_accepts_local_configuration_and_runs_all_configured_hooks() -> None:
    """Prepared policy seeds Bind and normal lifecycle/Meld hooks for the new Book."""
    world = GraduationWorld(shared_configuration=False)
    events: list[object] = []
    bind_calls: list[object] = []
    config = SpellbookConfiguration("graduation-regression").with_defaults()
    config.with_phase_scheduler_workers(2)
    config.with_bind_hooks(pre=[bind_calls.append], activation=[bind_calls.append], post=[bind_calls.append])

    def before() -> None:
        """Observe normal pre-conjure ordering without accessing an unattached Book."""
        events.append("pre")

    def activate(conduit: Conduit) -> None:
        """Reach lookup during activation, while normal CONJURE still owns registration."""
        events.append("activation")
        with pytest.raises(KeyError):
            conduit.meld(spell_id="not-registered")

    def after(conduit: Conduit) -> None:
        """Observe the exact same target at normal post-conjure publication."""
        events.append(conduit)

    def meld_before(*args: object) -> None:
        """Capture configured pre-resolution dispatch."""
        events.append("meld")

    config.with_hooks(
        on_conduit_pre_created=before, on_conduit_activated=activate,
        on_conduit_post_created=after, on_meld_pre_resolve=meld_before,
    )
    try:
        world.child.upgrade_to_normal("configured", configuration=config)
        assert world.child._spellbook.get_configuration() is config
        assert events == ["pre", "activation", world.child]
        spell_id = world.child.bind(spell=GraduatedService, existence=Existence.unique)
        assert isinstance(world.child.meld(spell_id=spell_id), GraduatedService)
        assert events[-1] == "meld"
        assert bind_calls[0] is GraduatedService
        assert bind_calls[1] is bind_calls[2]
        assert bind_calls[1]._spellbook is world.child._spellbook
        assert world.book.find_spell_by_id(bind_calls[1].spell_id) is None
    finally:
        world.cleanup()


@pytest.mark.parametrize("stage", ["pre", "activation", "post"])
def test_shared_config_bind_seeds_do_not_share_runtime_mutations(stage: str) -> None:
    """Shared policy seeds each Book, but child clear/add never mutates root callbacks."""
    calls: list[object] = []
    child_calls: list[object] = []
    config = SpellbookConfiguration("graduation-regression").with_defaults()
    config.with_bind_hooks(**{stage: [calls.append]})
    world = GraduationWorld(shared_configuration=True, configuration=config)
    calls.clear()
    try:
        world.graduate()
        world.child.bind(spell=GraduatedService, existence=Existence.unique)
        assert len(calls) == 1
        world.child.clear_bind_hooks()
        world.child.add_bind_hooks(**{stage: [child_calls.append]})
        world.root.bind(spell=LaterParentService, existence=Existence.unique)
        assert len(calls) == 2
        assert child_calls == []
        assert any(config.get_bind_hooks())
    finally:
        world.cleanup()


def test_upgrade_rejects_old_ids_in_both_conduit_and_retained_space(
    graduation_world: GraduationWorld,
) -> None:
    """Warm lookup caches cannot retain access to the old Book after graduation."""
    child = graduation_world.child
    old = child.meld(spell_id=graduation_world.parent_id)
    space = child.create_spellspace()
    space.meld(spell_id=graduation_world.parent_id)
    try:
        graduation_world.graduate()
        assert child._spellbook.spells == {}
        with pytest.raises(KeyError):
            child.meld(spell_id=graduation_world.parent_id)
        with pytest.raises(KeyError):
            space.meld(spell_id=graduation_world.parent_id)
        child.permanent_cleanup()
        assert old.cleanup_calls == 1
        assert not graduation_world.book.cleaned
    finally:
        space.permanent_cleanup()


@pytest.mark.parametrize("parked", [False, True])
def test_upgrade_reindexes_the_same_gate_under_its_own_root(
    graduation_world: GraduationWorld, parked: bool,
) -> None:
    """No old lineage gate entry remains; an intentional park survives upgrade."""
    child = graduation_world.child
    gate = child._creation_gate
    if parked:
        gate.close_and_drain()
    graduation_world.graduate()
    controller = child._creation_gate_controller
    assert controller.get_conduit_lineage_gates(child.id) == {child.id: gate}
    assert child.id not in controller.get_conduit_lineage_gates(graduation_world.root.id)
    assert gate.enabled is not parked


@pytest.mark.parametrize("bad", ["hooks", "children", "name", "wrong-frame", "config-type"])
def test_invalid_upgrade_preserves_original_book_lineage_and_gate(
    graduation_world: GraduationWorld, bad: str,
) -> None:
    """Every preflight failure leaves a usable lesser without leaked Book identities."""
    world = graduation_world
    child = world.child
    original = child.meld(spell_id=world.parent_id)
    registry = world.root._aetheric_frame.devops_information_registry
    before = registry.describe()["identity_count"]
    extra = None
    config = None
    try:
        if bad == "children":
            extra = child.create_lesser_conduit()
        if bad == "wrong-frame":
            config = SpellbookConfiguration("wrong-frame").with_defaults()
        with pytest.raises((ValueError, RuntimeError, TypeError)):
            if bad == "hooks":
                child.upgrade_to_normal("failed", hooks={"not_a_hook": None})
            elif bad == "name":
                child.upgrade_to_normal("parent")
            elif bad == "config-type":
                child.upgrade_to_normal("failed", configuration=object())
            else:
                child.upgrade_to_normal("failed", configuration=config)
        assert child._conduit_state is ConduitState.lesser
        assert child._spellbook is world.book
        assert child.meld(spell_id=world.parent_id) is original
        assert child._conduit_ward._parent_conduit is world.root
        assert child._creation_gate.enabled
        assert registry.describe()["identity_count"] == before
    finally:
        if extra is not None:
            extra.cleanup()
        if config is not None:
            config.cleanup()
    world.graduate()
    assert child._spellbook is not world.book


def test_explicit_config_cannot_override_frame_policy_or_share_local_ownership(
    graduation_world: GraduationWorld,
) -> None:
    """Shared policy rejects a different object; local policy rejects the borrowed owner."""
    world = graduation_world
    shared = world.book._is_frame_owned_shared_configuration()
    config = (
        SpellbookConfiguration("graduation-regression").with_defaults()
        if shared else world.configuration
    )
    before = world.root._aetheric_frame.devops_information_registry.describe()["identity_count"]
    try:
        with pytest.raises((ValueError, RuntimeError)):
            world.child.upgrade_to_normal("failed", configuration=config)
        assert not world.configuration.cleaned
        assert world.child._spellbook is world.book
        assert world.root._aetheric_frame.devops_information_registry.describe()["identity_count"] == before
        assert world.child.meld(spell_id=world.parent_id) is world.child.meld(spell_id=world.parent_id)
    finally:
        if shared:
            config.cleanup()


def test_phase_failure_restores_lesser_and_allows_retry(
    graduation_world: GraduationWorld, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failed Book pipeline must undo root preparation and retire the failed Book."""
    world = graduation_world
    child = world.child
    old_pool = child._conduit_pool
    books: list[Spellbook] = []

    def reject_phases(*, spellbook: Spellbook, **kwargs: object) -> None:
        """Fail the normal resolution boundary after target promotion has begun."""
        books.append(spellbook)
        raise RuntimeError("resolution failure")

    with monkeypatch.context() as patch:
        patch.setattr(SpellbookCreationSystem, "run_resolution_phases_for_conduit", reject_phases)
        with pytest.raises(RuntimeError, match="resolution failure"):
            world.graduate()
    assert books[0].cleaned
    assert child._conduit_state is ConduitState.lesser
    assert child._conduit_pool is old_pool
    assert child._conduit_ward._parent_conduit is world.root
    assert world.root._conduit_ward._lesser_conduits[child.id] is child
    assert child._creation_gate.enabled
    assert child.id in child._creation_gate_controller.get_conduit_lineage_gates(world.root.id)
    assert world.root._aetheric_frame.devops_information_registry.get_identity(
        owner_kind="conduit_ward", owner_id=child.id,
    ) is None
    world.graduate()
    assert child._spellbook is not world.book


def test_upgrade_drains_active_work_before_status_changes(
    graduation_world: GraduationWorld, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The gate parks first and waits for an active ticket before changing ownership."""
    child = graduation_world.child
    gate = child._creation_gate
    drain_started = Event()
    original_drain = CreationGate.close_and_drain

    def observed_drain(self: CreationGate, timeout: float = 30, interval: float = 0.1) -> None:
        """Expose entry into the real drain without changing its synchronization."""
        if self is gate:
            drain_started.set()
        original_drain(self, timeout=timeout, interval=interval)

    monkeypatch.setattr(CreationGate, "close_and_drain", observed_drain)
    gate.register_ticket()
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(child.upgrade_to_normal, "drained")
        try:
            assert drain_started.wait(3)
            assert child._conduit_state is ConduitState.lesser
            assert not future.done()
        finally:
            gate.unregister_ticket()
        future.result(timeout=5)
    assert child._conduit_state is ConduitState.normal
    assert gate.enabled


def test_graduation_records_new_book_identity_and_configured_hook_presence() -> None:
    """Existing crystal shapes record effective defaults and reference the new Book."""
    events: list[object] = []
    config = SpellbookConfiguration("graduation-regression").with_defaults()
    config.with_bind_hooks(pre=[events.append])
    config.with_hooks(on_conduit_activated=events.append, on_meld_pre_resolve=events.append)
    world = GraduationWorld(shared_configuration=True, configuration=config)
    try:
        recorder = _activate_crystallizer()
        world.graduate()
        book = world.child._spellbook
        checkpoint = recorder.checkpoint_replay_data(recorder.create_checkpoint())
        assert set(checkpoint["payloads"]["spellbook"][book.id]["hook_names"]) == {
            "bind:pre", "conduit:on_conduit_activated", "meld:on_meld_pre_resolve",
        }
        assert checkpoint["payloads"]["conduit"][world.child.id]["spellbook_id"] == book.id
        world.child.clear_bind_hooks()
        checkpoint = recorder.checkpoint_replay_data(recorder.create_checkpoint())
        assert "bind:pre" not in checkpoint["payloads"]["spellbook"][book.id]["hook_names"]
    finally:
        world.cleanup()
