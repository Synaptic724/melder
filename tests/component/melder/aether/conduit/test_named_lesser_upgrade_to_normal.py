"""Named graduation keeps discovery, independent ownership and failure recovery aligned."""

import pytest

from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.synchronization.creation_gate import CreationGate
from tests.component.melder.aether.conduit import test_named_lesser_directory_lifecycle as naming_support
from tests.component.melder.aether.conduit import test_conduit_graduation_ownership_regression as support

root = naming_support.root
isolated_graduation_roots = support.isolated_graduation_roots
graduation_world = support.graduation_world


@pytest.mark.parametrize("promoted_name", ["request", "worker"])
def test_named_graduation_survives_former_parent_and_root_cleanup(root: Conduit, promoted_name: str) -> None:
    """Former lineage teardown must not destroy or unregister the independently promoted root."""
    parent = root.create_lesser_conduit(name="branch")
    child = parent.create_lesser_conduit(name="request")
    cloud = root.get_conduit_cloud()
    try:
        child.upgrade_to_normal(name=promoted_name)
        parent.cleanup()
        root.cleanup()
        assert cloud.get_conduit(promoted_name) is child
        assert cloud.list_conduit_names() == (promoted_name,)
        assert child._spellbook.conduit is child
        # The new root also owns a usable pool after its former lineage dies.
        descendant = child.create_lesser_conduit(name="independent-child")
        assert cloud.get_conduit("independent-child") is descendant
        descendant.cleanup()
    finally:
        child.permanent_cleanup()
    assert cloud.count_conduits() == 0


def test_renamed_graduation_cannot_remove_a_reused_original_name(root: Conduit) -> None:
    """Cleanup must retire the promoted identity's current alias, never a new owner of its old name."""
    root.prewarm_lesser_conduits(1)
    promoted = root.create_lesser_conduit(name="request")
    cloud = root.get_conduit_cloud()
    try:
        promoted.upgrade_to_normal(name="worker")
        replacement = root.create_lesser_conduit(name="request")
        assert replacement is not promoted
        assert cloud.get_conduit("request") is replacement
        promoted.cleanup()
        assert cloud.get_conduit("request") is replacement
        assert not cloud.has_conduit_name("worker")
        nested = replacement.create_lesser_conduit(name="replacement-child")
        assert cloud.get_conduit("replacement-child") is nested
    finally:
        promoted.permanent_cleanup()


@pytest.mark.parametrize("initially_parked", [False, True])
def test_named_upgrade_drain_failure_releases_claim_and_can_retry(
    root: Conduit, monkeypatch: pytest.MonkeyPatch, initially_parked: bool,
) -> None:
    """Failure before Book construction must retain discovery and the caller's admission posture."""
    child = root.create_lesser_conduit(name="before")
    cloud = root.get_conduit_cloud()
    if initially_parked:
        child._creation_gate.close()

    def fail_drain(gate: CreationGate, **kwargs: object) -> None:
        """Model timeout after temporary parking, matching the real gate's failure contract."""
        gate.close()
        raise RuntimeError("drain failed before construction")

    with monkeypatch.context() as patch:
        patch.setattr(CreationGate, "close_and_drain", fail_drain)
        with pytest.raises(RuntimeError, match="drain failed"):
            child.upgrade_to_normal(name="after")
    assert child._conduit_state is ConduitState.lesser
    assert child._spellbook is root._spellbook
    assert child._conduit_ward._parent_conduit is root
    assert child._creation_gate.enabled is not initially_parked
    assert cloud.get_conduit("before") is child
    # A different identity can claim the destination after failure, proving release.
    temporary = root.create_lesser_conduit(name="after")
    temporary.cleanup()
    try:
        child.upgrade_to_normal(name="after")
        assert cloud.get_conduit("after") is child
        assert not cloud.has_conduit_name("before")
        assert child._creation_gate.enabled is not initially_parked
    finally:
        child.permanent_cleanup()


@pytest.mark.parametrize("promoted_name", ["request", "worker"])
def test_named_graduation_keeps_book_hooks_and_disposal_independent(
    graduation_world: support.GraduationWorld, promoted_name: str,
) -> None:
    """Local/shared configuration both retain named promotion's independent Book and creation ownership.

    Contract:
        Existing objects survive the transition, runtime Bind hooks do not cross
        Books, and normal cleanup disposes retained and newly created objects once.
        Frame-wide policy may deliberately be shared while Book registries stay separate.
    """
    world = graduation_world
    world.child.cleanup()
    world.child = world.root.create_lesser_conduit(name="request")
    child = world.child
    retained = child.meld(spell_id=world.parent_id)
    parent_value = world.root.meld(spell_id=world.parent_id)
    original_calls: list[object] = []
    new_calls: list[object] = []
    world.book.add_bind_hooks(pre=[original_calls.append])

    child.upgrade_to_normal(name=promoted_name)
    cloud = world.root.get_conduit_cloud()
    assert cloud.get_conduit(promoted_name) is child
    assert child._spellbook is not world.book
    assert child._spellbook.find_spell_by_id(world.parent_id) is None
    if world.root._aetheric_frame.frame_configuration.shared_framewide_spellbook_configuration:
        assert child._configuration is world.configuration
    else:
        assert child._configuration is not world.configuration

    child.add_bind_hooks(pre=[new_calls.append])
    new_id = child.bind(
        spell=support.GraduatedService,
        existence=Existence.unique_per_conduit,
        disposal_method_names=["cleanup"],
    )
    new_value = child.meld(spell_id=new_id)
    assert original_calls == []
    assert new_calls == [support.GraduatedService]
    assert retained.cleanup_calls == 0
    child.cleanup()
    assert retained.cleanup_calls == 1
    assert new_value.cleanup_calls == 1
    assert parent_value.cleanup_calls == 0
    assert world.root.meld(spell_id=world.parent_id) is parent_value
    assert not cloud.has_conduit_name(promoted_name)
