"""Real named-scope capture and replay, with fresh identities and no saved instance state."""

from pathlib import Path
from typing import TYPE_CHECKING, Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.configuration.crystallizer_configuration import CrystallizerConfiguration
from melder.crystallizer.crystallizer import Crystallizer
from melder.crystallizer.crystals.conduit_crystal import ConduitCrystal
from melder.nexus.nexus import Nexus
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration
from tests.integration.melder.crystallizer import test_crystallizer_restore_integration as support

if TYPE_CHECKING:
    from melder.utilities.general_base.cleanable import Cleanable

reset_world_singletons = support.reset_world_singletons
cache_root = support.cache_root


class ScopedValue:
    """Importable creation whose changed marker must never reappear through structural replay."""

    def __init__(self) -> None:
        """Initialize fresh application state; no state is supplied by the recorder."""
        self.marker = "fresh"


def _activate(parallel: bool = True) -> Crystallizer:
    """Activate real recording with the selected restore driver and a bounded worker pool."""
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.set_property("restore_parallel_enabled", parallel)
    configuration.set_property("restore_scheduler_workers", 2)
    configuration.activate()
    recorder = Crystallizer()
    recorder.activate(configuration)
    return recorder


def _fresh_boot(parallel: bool) -> Crystallizer:
    """Retire the current runtime and activate a fresh recorder against the same test cache."""
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    return _activate(parallel)


def _root() -> Conduit:
    """Conjure an empty dynamic Book whose configuration was finalized before recording."""
    return support._dynamic_book().conjure(dynamic=True, name="owner")


@pytest.mark.parametrize("parallel", [False, True], ids=["sequential", "parallel"])
@pytest.mark.parametrize("shared", [False, True], ids=["local-config", "frame-config"])
def test_public_frame_configuration_records_book_before_named_scope_replay(
    cache_root: Path, parallel: bool, shared: bool,
) -> None:
    """The supported public posture door must not omit the owning Book from a valid checkpoint."""
    recorder = _activate(parallel)
    configuration = SpellbookConfiguration().with_defaults().finalize()
    book = Spellbook(configuration=configuration)
    book.configure_aether_frame(
        system_state="dynamic", disposal=None, disposal_method_names=None,
        rift_enabled=True, shared_framewide_spellbook_configuration=shared,
    )
    book.bind(spell=ScopedValue, existence=Existence.unique_per_conduit)
    root = book.conjure(name="owner")
    child = root.create_lesser_conduit(name="request")
    book_id, child_id = book.id, child.id
    assert recorder.describe_profile()["spellbook_count"] == 1
    checkpoint = recorder.create_checkpoint()
    recorder.flush_checkpoint(checkpoint)
    rebooted = _fresh_boot(parallel)
    rebooted.reload_cached_checkpoint(checkpoint)
    report = rebooted.load_checkpoint(checkpoint)
    restored = Aether().get_conduit_cloud().get_conduit("request")
    assert report["status"] == "complete"
    assert restored.id == report["identity_map"][child_id]
    assert restored._spellbook.id == report["identity_map"][book_id]
    descriptor = Nexus()._get_required_frame_descriptor("default")
    assert descriptor.frame_overview.payload.rift_enabled is True
    assert descriptor.conduit_records_by_id[restored.id].payload.conduit_name == "request"


@pytest.mark.parametrize("parallel", [False, True], ids=["sequential", "parallel"])
def test_restored_named_scopes_publish_current_nexus_hierarchy(cache_root: Path, parallel: bool) -> None:
    """Both replay drivers publish fresh IDs, names and parent edges through ordinary creation."""
    recorder = _activate(parallel)
    configuration = SpellbookConfiguration().with_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configure_frame_posture_for_spellbook_configuration(
        configuration, dynamic=True, rift_enabled=True, ai_native_enabled=True,
    )
    configuration.finalize()
    root = Spellbook(configuration=configuration).conjure(dynamic=True, name="owner")
    parent = root.create_lesser_conduit(name="parent")
    child = parent.create_lesser_conduit(name="child")
    parent_id, child_id = parent.id, child.id
    checkpoint = recorder.create_checkpoint()
    recorder.flush_checkpoint(checkpoint)
    rebooted = _fresh_boot(parallel)
    rebooted.reload_cached_checkpoint(checkpoint)
    report = rebooted.load_checkpoint(checkpoint)
    descriptor = Nexus()._get_required_frame_descriptor("default")
    restored_parent_id = report["identity_map"][parent_id]
    restored_child_id = report["identity_map"][child_id]
    parent_record = descriptor.conduit_records_by_id[restored_parent_id]
    child_record = descriptor.conduit_records_by_id[restored_child_id]
    assert parent_record.payload.conduit_name == "parent"
    assert child_record.payload.conduit_name == "child"
    assert child_record.payload.parent_conduit_id == restored_parent_id
    assert child_record.payload.lineage_depth == 2
    assert set(descriptor.frame_overview.payload.conduit_cloud_names) == {"owner", "parent", "child"}


@pytest.mark.parametrize("parallel", [False, True], ids=["sequential", "parallel"])
def test_round_trip_rebuilds_shared_unnamed_ancestry_without_instance_state(cache_root: Path, parallel: bool) -> None:
    """Both drivers must reconstruct one Book, shared support and named nesting with fresh ids."""
    recorder = _activate(parallel)
    book = support._dynamic_book()
    spell_id = book.bind(spell=ScopedValue, existence=Existence.unique_per_conduit)
    root = book.conjure(dynamic=True, name="owner")
    parent = root.create_lesser_conduit()
    left = parent.create_lesser_conduit(name="left")
    right = parent.create_lesser_conduit(name="right")
    deep = left.create_lesser_conduit(name="deep")
    original = left.meld(spell_id=spell_id)
    original.marker = "must-not-be-saved"
    ids = {scope.id for scope in (root, parent, left, right, deep)}
    parent_id = parent.id
    checkpoint = recorder.create_checkpoint()
    assert recorder.describe_profile()["conduit_count"] == 4
    assert recorder.describe_checkpoint(checkpoint)["captured_counts"]["conduit"] == 4
    recorder.flush_checkpoint(checkpoint)

    rebooted = _fresh_boot(parallel)
    rebooted.reload_cached_checkpoint(checkpoint)
    report = rebooted.load_checkpoint(checkpoint)
    cloud = Aether().get_conduit_cloud()
    restored_root = cloud.get_conduit("owner")
    restored_left = cloud.get_conduit("left")
    restored_right = cloud.get_conduit("right")
    restored_deep = cloud.get_conduit("deep")
    restored_parent = restored_left._conduit_ward._parent_conduit
    assert restored_parent is restored_right._conduit_ward._parent_conduit
    assert restored_parent.name is None
    assert restored_parent.id == report["identity_map"][parent_id]
    assert not cloud.has_conduit_id(restored_parent.id)
    assert restored_parent._conduit_ward._parent_conduit is restored_root
    assert restored_deep._conduit_ward._parent_conduit is restored_left
    assert restored_left._spellbook is restored_root._spellbook
    assert len(restored_root._aetheric_frame._conduits) == 1
    assert report["built_counts"]["spellbook"] == 1
    assert report["built_counts"]["conduit"] == 5
    assert ids <= set(report["identity_map"])
    assert all(report["identity_map"][identity] != identity for identity in ids)
    restored_value = restored_left.meld(spell_id=spell_id)
    assert restored_value is not original
    assert restored_value.marker == "fresh"


@pytest.mark.parametrize("parallel", [False, True], ids=["sequential", "parallel"])
def test_released_scope_disappears_from_later_restore_but_not_earlier_history(cache_root: Path, parallel: bool) -> None:
    """Removing the final named carrier must also stop replaying its unnamed support."""
    recorder = _activate(parallel)
    root = _root()
    parent = root.create_lesser_conduit()
    child = parent.create_lesser_conduit(name="request")
    child_id, parent_id = child.id, parent.id
    earlier = recorder.create_checkpoint()
    recorder.flush_checkpoint(earlier)
    child.cleanup()
    later = recorder.create_checkpoint()
    recorder.flush_checkpoint(later)
    assert recorder.describe_profile()["conduit_count"] == 1

    rebooted = _fresh_boot(parallel)
    rebooted.reload_cached_checkpoint(earlier)
    rebooted.reload_cached_checkpoint(later)
    latest = rebooted.load_checkpoint(later)
    assert Aether().get_conduit_cloud().list_conduit_names() == ("owner",)
    assert child_id not in latest["identity_map"]
    assert parent_id not in latest["identity_map"]
    assert latest["built_counts"]["conduit"] == 1

    historical = _fresh_boot(parallel)
    historical.reload_cached_checkpoint(earlier)
    restored = historical.load_checkpoint(earlier)
    assert Aether().get_conduit_cloud().get_conduit("request").id == restored["identity_map"][child_id]
    assert parent_id in restored["identity_map"]


@pytest.mark.parametrize("split_windows", [False, True])
def test_reused_id_replays_new_name_and_parent_only(cache_root: Path, split_windows: bool) -> None:
    """Pooled-id reuse must replace both its name and its supporting parent snapshot."""
    recorder = _activate()
    root = _root()
    old_parent = root.create_lesser_conduit()
    new_parent = root.create_lesser_conduit()
    child = old_parent.create_lesser_conduit(name="old")
    child_id, old_parent_id, new_parent_id = child.id, old_parent.id, new_parent.id
    checkpoints: list[str] = []
    if split_windows:
        checkpoints.append(recorder.create_checkpoint())
        recorder.flush_checkpoint(checkpoints[-1])
    child.cleanup()
    reused = new_parent.create_lesser_conduit(name="new")
    assert reused is child
    checkpoints.append(recorder.create_checkpoint())
    recorder.flush_checkpoint(checkpoints[-1])

    rebooted = _fresh_boot(True)
    for checkpoint in checkpoints:
        rebooted.reload_cached_checkpoint(checkpoint)
    report = rebooted.load_checkpoint(checkpoints[-1])
    cloud = Aether().get_conduit_cloud()
    restored = cloud.get_conduit("new")
    assert not cloud.has_conduit_name("old")
    assert restored.id == report["identity_map"][child_id]
    assert restored._conduit_ward._parent_conduit.id == report["identity_map"][new_parent_id]
    assert old_parent_id not in report["identity_map"]


@pytest.mark.parametrize("anchor", ["owner", "left"])
def test_formation_contains_required_ancestry_and_only_selected_named_subtree(cache_root: Path, anchor: str) -> None:
    """A named-child formation retains its root but must not pull in unrelated named siblings."""
    recorder = _activate()
    root = _root()
    parent = root.create_lesser_conduit()
    left = parent.create_lesser_conduit(name="left")
    parent.create_lesser_conduit(name="right")
    left.create_lesser_conduit(name="deep")
    recorder.save_formation("selected", conduit_id=root.id if anchor == "owner" else left.id)
    assert recorder.analyze_formation("selected")["verdict"] != "blockers"

    rebooted = _fresh_boot(True)
    report = rebooted.restore_formation("selected", target_frame_name="restored-frame")
    cloud = Aether().get_conduit_cloud("restored-frame")
    expected = {"owner", "left", "deep"}
    if anchor == "owner":
        expected.add("right")
    assert set(cloud.list_conduit_names()) == expected
    assert cloud.get_conduit("deep")._conduit_ward._parent_conduit is cloud.get_conduit("left")
    assert cloud.get_conduit("left")._conduit_ward._parent_conduit.name is None
    assert report["built_counts"]["spellbook"] == 1


def test_promoted_twin_is_independent_of_old_book_removal(cache_root: Path) -> None:
    """Promotion replaces the lesser twin's role/Book instead of leaving an old hierarchy alias."""
    recorder = _activate()
    root = _root()
    child = root.create_lesser_conduit(name="request")
    child_id = child.id
    child.upgrade_to_normal(name="worker")
    new_book_id = child._spellbook._id
    root.cleanup()
    checkpoint = recorder.create_checkpoint()
    payload = recorder.checkpoint_replay_data(checkpoint)["payloads"]["conduit"][child_id]
    assert payload["spellbook_id"] == new_book_id
    assert payload["configuration_payload"]["conduit_state"] == "normal"
    assert "lineage_ancestors" not in payload["configuration_payload"]
    recorder.flush_checkpoint(checkpoint)
    rebooted = _fresh_boot(True)
    rebooted.reload_cached_checkpoint(checkpoint)
    report = rebooted.load_checkpoint(checkpoint)
    restored = Aether().get_conduit_cloud().get_conduit("worker")
    assert restored._conduit_ward._parent_conduit is None
    assert restored.id == report["identity_map"][child_id]
    assert report["built_counts"]["conduit"] == 1


def test_failed_promotion_before_new_twin_is_removed_on_normal_cleanup(
    cache_root: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Normal cleanup must remove a lingering lesser twin whose last record still names the old Book."""
    recorder = _activate()
    root = _root()
    child = root.create_lesser_conduit(name="request")

    def fail(conduit: Conduit) -> None:
        """Fail after Book attachment but before replacement normal-twin emission."""
        raise RuntimeError("before new root twin")

    with monkeypatch.context() as patch:
        patch.setattr(Conduit, "_add_spells_to_aether", fail)
        with pytest.raises(RuntimeError, match="before new root twin"):
            child.upgrade_to_normal(name="worker")
    child.cleanup()
    assert recorder.describe_profile()["conduit_count"] == 1
    checkpoint = recorder.create_checkpoint()
    recorder.flush_checkpoint(checkpoint)
    rebooted = _fresh_boot(True)
    rebooted.reload_cached_checkpoint(checkpoint)
    assert rebooted.load_checkpoint(checkpoint)["built_counts"]["conduit"] == 1
    assert Aether().get_conduit_cloud().list_conduit_names() == ("owner",)


def test_unnamed_prewarm_and_return_never_enter_recording(cache_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """An active recorder must not add calls or hidden support records to ordinary unnamed cycles."""
    recorder = _activate()
    root = _root()
    before = recorder.describe_profile()["emission_sequence"]

    def forbidden(*args: object, **kwargs: object) -> None:
        """Catch any recording work introduced into unnamed scope cycling."""
        pytest.fail("Unnamed scope entered Crystallizer")

    with monkeypatch.context() as patch:
        patch.setattr(Crystallizer, "emit", forbidden)
        patch.setattr(Crystallizer, "emit_conduit_removed", forbidden)
        root.prewarm_lesser_conduits(2)
        for _ in range(3):
            child = root.create_lesser_conduit()
            child.cleanup()
    assert recorder.describe_profile()["emission_sequence"] == before


def test_failed_record_retirement_keeps_parent_ownership_for_retry(
    cache_root: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A retryable record failure must not orphan a still-named scope from its cleanup owner."""
    recorder = _activate()
    root = _root()
    child = root.create_lesser_conduit(name="request")

    def fail(recorder: Crystallizer, conduit_id: str) -> None:
        """Reject retirement before the record owner accepts the event."""
        raise RuntimeError("record retirement unavailable")

    try:
        with monkeypatch.context() as patch:
            patch.setattr(Crystallizer, "emit_conduit_removed", fail)
            with pytest.raises(RuntimeError, match="retirement unavailable"):
                child.cleanup()
            assert child._conduit_ward._parent_conduit is root
            assert root._conduit_ward._lesser_conduits[child.id] is child
            assert root.get_conduit_cloud().get_conduit("request") is child
        child.cleanup()
        assert recorder.describe_profile()["conduit_count"] == 1
        assert not root.get_conduit_cloud().has_conduit_name("request")
    finally:
        child.permanent_cleanup()


@pytest.mark.parametrize("named_parent", [False, True])
def test_parent_cannot_reenter_pool_while_named_descendant_retirement_failed(
    cache_root: Path, monkeypatch: pytest.MonkeyPatch, named_parent: bool,
) -> None:
    """Parents must retain failed children and stay out of the pool until cleanup can complete."""
    recorder = _activate()
    root = _root()
    parent = root.create_lesser_conduit(name="parent" if named_parent else None)
    child = parent.create_lesser_conduit(name="request")
    original = Crystallizer.emit_conduit_removed

    def fail_child(recorder: Crystallizer, conduit_id: str) -> None:
        """Fail only the descendant; unrelated owner cleanup must remain usable."""
        if conduit_id == child.id:
            raise RuntimeError("descendant record unavailable")
        original(recorder, conduit_id)

    try:
        with monkeypatch.context() as patch:
            patch.setattr(Crystallizer, "emit_conduit_removed", fail_child)
            with pytest.raises(ExceptionGroup):
                parent.cleanup()
            assert parent._conduit_ward._parent_conduit is root
            assert child._conduit_ward._parent_conduit is parent
            assert parent._conduit_ward._lesser_conduits[child.id] is child
            assert root.get_conduit_cloud().get_conduit("request") is child
        parent.cleanup()
        assert root.get_conduit_cloud().list_conduit_names() == ("owner",)
        assert recorder.describe_profile()["conduit_count"] == 1
    finally:
        child.permanent_cleanup()
        parent.permanent_cleanup()


@pytest.mark.parametrize("parallel", [False, True])
def test_partial_child_replay_failure_unwinds_every_created_scope(
    cache_root: Path, monkeypatch: pytest.MonkeyPatch, parallel: bool,
) -> None:
    """Both drivers must remove the partially built hierarchy and its re-emitted records."""
    recorder = _activate(parallel)
    root = _root()
    parent = root.create_lesser_conduit()
    parent.create_lesser_conduit(name="left")
    parent.create_lesser_conduit(name="right")
    checkpoint = recorder.create_checkpoint()
    recorder.flush_checkpoint(checkpoint)
    rebooted = _fresh_boot(parallel)
    rebooted.reload_cached_checkpoint(checkpoint)
    original = Conduit.create_lesser_conduit
    created: list[Conduit] = []

    def fail_second(parent: Conduit, logger: object = None, *, name: Optional[str] = None) -> Conduit:
        """Create genuine earlier scopes, then fail the final public creation call."""
        if name == "right":
            raise RuntimeError("stop child replay")
        child = original(parent, logger, name=name)
        created.append(child)
        return child

    monkeypatch.setattr(Conduit, "create_lesser_conduit", fail_second)
    with pytest.raises(RuntimeError, match="restore failed"):
        rebooted.load_checkpoint(checkpoint)
    assert len(created) == 2
    assert all(child.cleaned for child in created)
    assert all(not frame._conduits for frame in Aether()._aetheric_frames.values())
    assert rebooted.describe_profile()["conduit_count"] == 0
    assert rebooted.describe_profile()["spellbook_count"] == 0


@pytest.mark.parametrize("after_record", [False, True])
def test_failed_named_emission_unwinds_discovery_and_record(
    cache_root: Path, monkeypatch: pytest.MonkeyPatch, after_record: bool,
) -> None:
    """Failed publication must retire both a not-yet-recorded and an already-recorded candidate."""
    recorder = _activate()
    root = _root()
    original = Crystallizer.emit

    def fail_named(recorder: Crystallizer, twin: Cleanable) -> None:
        """Inject a sink or post-record failure only for the new named scope."""
        if isinstance(twin, ConduitCrystal) and twin.conduit_name == "broken":
            if after_record:
                original(recorder, twin)
            raise RuntimeError("named emission failed")
        original(recorder, twin)

    with monkeypatch.context() as patch:
        patch.setattr(Crystallizer, "emit", fail_named)
        with pytest.raises(RuntimeError, match="named emission failed"):
            root.create_lesser_conduit(name="broken")
    assert root.get_conduit_cloud().list_conduit_names() == ("owner",)
    assert recorder.describe_profile()["conduit_count"] == 1
    assert root._conduit_ward._lesser_conduits == {}
    recovered = root.create_lesser_conduit(name="recovered")
    assert root.get_conduit_cloud().get_conduit("recovered") is recovered


def test_inactive_recording_keeps_named_lifecycle_operational(cache_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Naming must remain usable without entering any inactive recorder sink."""
    root = _root()

    def forbidden(*args: object, **kwargs: object) -> None:
        """Catch facade calls that should have been gated before payload construction."""
        pytest.fail("Inactive recording was entered")

    with monkeypatch.context() as patch:
        patch.setattr(Crystallizer, "emit", forbidden)
        patch.setattr(Crystallizer, "emit_conduit_removed", forbidden)
        child = root.create_lesser_conduit(name="request")
        assert root.get_conduit_cloud().get_conduit("request") is child
        child.cleanup()
    assert root.get_conduit_cloud().list_conduit_names() == ("owner",)


def test_automatic_names_do_not_expand_dynamic_recording_policy(cache_root: Path) -> None:
    """An active recorder must still exclude automatic scopes while Cloud can discover their names."""
    recorder = _activate()
    configuration = SpellbookConfiguration("automatic-frame").with_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    book = Spellbook(aetheric_frame="automatic-frame", configuration=configuration)
    book._aetheric_frame_configuration.with_system_caching_enabled(False)
    root = book.conjure(name="automatic-owner")
    try:
        child = root.create_lesser_conduit(name="automatic-request")
        assert root.get_conduit_cloud().get_conduit("automatic-request") is child
        assert recorder.describe_profile()["conduit_count"] == 0
        child.cleanup()
        assert recorder.describe_profile()["conduit_count"] == 0
    finally:
        root.cleanup()


def test_named_replay_preserves_lesser_policy_restrictions(cache_root: Path) -> None:
    """Naming and replay must not grant the normal-root-only policy mutation capability."""
    recorder = _activate()
    child = _root().create_lesser_conduit(name="request")
    with pytest.raises(RuntimeError, match="lesser Conduit"):
        child.set_new_policy("block_all")
    checkpoint = recorder.create_checkpoint()
    recorder.flush_checkpoint(checkpoint)
    rebooted = _fresh_boot(True)
    rebooted.reload_cached_checkpoint(checkpoint)
    rebooted.load_checkpoint(checkpoint)
    restored = Aether().get_conduit_cloud().get_conduit("request")
    assert restored.policy.name == "default"
    with pytest.raises(RuntimeError, match="lesser Conduit"):
        restored.set_new_policy("block_all")


def test_skip_existing_drops_only_restored_lesser_name_without_borrowing_host_object(cache_root: Path) -> None:
    """Name collision policy must preserve a fresh child identity and the original host's ownership."""
    recorder = _activate()
    root = _root()
    child = root.create_lesser_conduit(name="taken")
    child.create_lesser_conduit(name="leaf")
    recorded_child_id = child.id
    recorder.save_formation("scoped", conduit_id=child.id)
    rebooted = _fresh_boot(True)
    host = support._dynamic_book().conjure(dynamic=True, name="host")
    host_child = host.create_lesser_conduit(name="taken")
    with pytest.raises(RuntimeError):
        rebooted.restore_formation("scoped")
    assert set(host.get_conduit_cloud().list_conduit_names()) == {"host", "taken"}
    report = rebooted.restore_formation("scoped", skip_existing=True)
    restored_parent = host.get_conduit_cloud().get_conduit("leaf")._conduit_ward._parent_conduit
    assert restored_parent is not host_child
    assert restored_parent.name is None
    assert restored_parent.id == report["identity_map"][recorded_child_id]
    assert host.get_conduit_cloud().get_conduit("taken") is host_child
    assert any(row["reason"] == "lesser_name_taken_built_unnamed" for row in report["shortfalls"])
