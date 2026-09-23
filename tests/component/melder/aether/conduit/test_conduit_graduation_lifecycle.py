"""Real lifecycle contracts replacing the obsolete mocked preset/seed upgrade path."""

import pytest

from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.conduit_ward import ConduitWard
from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.synchronization.creation_gate import CreationGate
from tests.component.melder.aether.conduit import (
    test_conduit_graduation_ownership_regression as graduation_support,
)
from tests.component.melder.aether.conduit.test_conduit_graduation_ownership_regression import (
    GraduatedService,
    GraduationWorld,
)

graduation_world = graduation_support.graduation_world
isolated_graduation_roots = graduation_support.isolated_graduation_roots


def test_upgrade_to_normal_transitions_and_registers(graduation_world: GraduationWorld) -> None:
    """Root/cloud/Book registration use the same conduit while stores stay retained."""
    child = graduation_world.child
    old_creations = child._creations
    borrowed_pool = child._conduit_pool
    original_id = child.id
    graduation_world.graduate()
    assert child.id == original_id
    assert child._conduit_state is ConduitState.normal
    assert child._creations is old_creations
    assert child._conduit_pool is not borrowed_pool
    assert child._aetheric_frame.conduit_cloud.get_conduit_by_name("graduated") is child
    assert child._spellbook.conduit is child
    assert child._spellbook.spells == {}
    assert not child._cluster_creations.is_active()


def test_upgrade_to_normal_refreshes_transaction_identity_without_changing_owner_id(
    graduation_world: GraduationWorld,
) -> None:
    """The new root's transaction metadata describes its independent Book and root."""
    child = graduation_world.child
    original_id = child.id
    graduation_world.graduate()
    identity = child._transaction_identity
    assert identity.owner_id == original_id
    for transaction in ("bind", "scan", "link", "transfer_ownership", "mutation", "cluster_link"):
        assert identity.supports_transaction(transaction)
    assert identity.metadata["conduit_state"] == ConduitState.normal.value
    assert identity.metadata["root_conduit_id"] == original_id
    assert identity.metadata["spellbook_id"] == child._spellbook.id
    assert identity.metadata["parent_conduit_id"] is None


def test_upgrade_accepts_default_root_name_when_available(graduation_world: GraduationWorld) -> None:
    """The ordinary default name remains a valid explicit normal-root name."""
    graduation_world.child.upgrade_to_normal("default")
    assert graduation_world.root._aetheric_frame.conduit_cloud.get_conduit_by_name(
        "default",
    ) is graduation_world.child


def test_upgrade_new_lesser_uses_new_book_and_pool(graduation_world: GraduationWorld) -> None:
    """A graduated root creates and recycles its own lesser tree independently."""
    world = graduation_world
    world.graduate()
    spell_id = world.child.bind(spell=GraduatedService, existence=Existence.unique_per_conduit_lineage)
    descendant = world.child.create_lesser_conduit()
    try:
        assert descendant.meld(spell_id=spell_id) is world.child.meld(spell_id=spell_id)
        assert descendant._spellbook is world.child._spellbook
        assert descendant._root_conduit_id == world.child.id
        descendant.cleanup()
        reused = world.child.create_lesser_conduit()
        assert reused is descendant
        assert isinstance(reused.meld(spell_id=spell_id), GraduatedService)
        assert world.book.find_spell_by_id(spell_id) is None
    finally:
        descendant.cleanup()


def test_upgrade_does_not_read_or_copy_former_root_verdicts(
    graduation_world: GraduationWorld, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The new empty Book cannot inherit dirty flags, timestamps or old verdict maps."""
    root_state = graduation_world.root.validate_resolution()

    def forbidden_snapshot(self: object) -> dict[str, object]:
        """Fail if the obsolete resolution-copy path is restored."""
        raise AssertionError("former-root verdicts must not be copied")

    monkeypatch.setattr(type(root_state), "snapshot_spell_validity", forbidden_snapshot)
    monkeypatch.setattr(type(root_state), "snapshot_root_validity", forbidden_snapshot)
    graduation_world.graduate()
    assert graduation_world.child.get_resolution_state() is None
    assert graduation_world.root.get_resolution_state() is root_state


def test_upgrade_detached_shell_refuses_without_consuming_a_pool_entry(
    graduation_world: GraduationWorld,
) -> None:
    """An idle pooled shell must be acquired into a lineage before graduation."""
    child = graduation_world.child
    child.cleanup()
    with pytest.raises(RuntimeError, match="Only lesser"):
        child.upgrade_to_normal("detached")
    assert graduation_world.root.create_lesser_conduit() is child
    graduation_world.graduate()
    assert child._spellbook is not graduation_world.book


def test_upgrade_conversion_failure_restores_original_lesser(
    graduation_world: GraduationWorld, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Preparation failures propagate after restoring status, pool and parent ownership."""
    child = graduation_world.child
    original_pool = child._conduit_pool
    original_book = child._spellbook

    def fail_conversion(self: ConduitWard) -> None:
        """Fault at the ward conversion boundary before its own state changes."""
        raise RuntimeError("convert boom")

    with monkeypatch.context() as patch:
        patch.setattr(ConduitWard, "_convert_to_normal_conduit", fail_conversion)
        with pytest.raises(RuntimeError, match="convert boom"):
            graduation_world.graduate()
    assert child._conduit_state is ConduitState.lesser
    assert child._conduit_pool is original_pool
    assert child._spellbook is original_book
    assert child._conduit_ward._parent_conduit is graduation_world.root
    graduation_world.graduate()
    assert child._conduit_state is ConduitState.normal


def test_upgrade_gate_timeout_preserves_status_and_can_retry(
    graduation_world: GraduationWorld, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Temporary parking failure must restore prior admission before returning an error."""
    gate = graduation_world.child._creation_gate
    original_drain = CreationGate.close_and_drain

    def timeout(self: CreationGate, **kwargs: object) -> None:
        """Use the real drain with a zero deadline while one ticket is held."""
        original_drain(self, timeout=0)

    gate.register_ticket()
    try:
        with monkeypatch.context() as patch:
            patch.setattr(CreationGate, "close_and_drain", timeout)
            with pytest.raises(RuntimeError, match="Timeout"):
                graduation_world.graduate()
    finally:
        gate.unregister_ticket()
    assert graduation_world.child._conduit_state is ConduitState.lesser
    assert gate.enabled
    graduation_world.graduate()


def test_parent_cleanup_does_not_dispose_retained_graduated_objects(
    graduation_world: GraduationWorld,
) -> None:
    """Retained disposal metadata remains valid after the former Book is retired."""
    child = graduation_world.child
    retained = child.meld(spell_id=graduation_world.parent_id)
    graduation_world.graduate()
    graduation_world.root.permanent_cleanup()
    assert retained.cleanup_calls == 0
    child.permanent_cleanup()
    assert retained.cleanup_calls == 1


def test_graduation_supplied_configuration_failure_keeps_parent_alive() -> None:
    """Rejected new local policy cannot retire the old root's configuration or bindings."""
    from melder.aether.spellbook.configuration.spellbook_configuration import (
        SpellbookConfiguration,
    )

    world = GraduationWorld(shared_configuration=False)
    rejected = SpellbookConfiguration("graduation-regression").with_defaults()
    rejected.with_phase_scheduler_workers(1)
    rejected.set_property("phase_scheduler_workers_per_spellbook", 0)
    try:
        with pytest.raises(ValueError, match="positive"):
            world.child.upgrade_to_normal("bad-config", configuration=rejected)
        assert world.child._spellbook is world.book
        assert not world.configuration.cleaned
        assert world.child._creation_gate.enabled
        world.graduate()
    finally:
        rejected.cleanup()
        world.cleanup()


def test_pre_attachment_failure_keeps_gate_parked_until_rollback(
    graduation_world: GraduationWorld, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The public caller restores ownership before it wakes a parked Meld waiter."""
    child = graduation_world.child
    original_restore = Conduit._restore_lesser_after_failed_upgrade
    original_drain = CreationGate.close_and_drain
    drain_calls = 0

    def observe_restore(self: Conduit, *args: object) -> None:
        """Check the gate at the rollback boundary before restoring original state."""
        assert not self._creation_gate.enabled
        original_restore(self, *args)

    def fail_attachment_drain(self: CreationGate, **kwargs: object) -> None:
        """Fail the Book's second drain, after public preparation parked the target."""
        nonlocal drain_calls
        original_drain(self)
        drain_calls += 1
        if drain_calls == 2:
            raise RuntimeError("attachment drain failure")

    with monkeypatch.context() as patch:
        patch.setattr(Conduit, "_restore_lesser_after_failed_upgrade", observe_restore)
        patch.setattr(CreationGate, "close_and_drain", fail_attachment_drain)
        with pytest.raises(RuntimeError, match="attachment drain failure"):
            graduation_world.graduate()
    assert drain_calls == 2
    assert child._creation_gate.enabled
    assert child._spellbook is graduation_world.book
