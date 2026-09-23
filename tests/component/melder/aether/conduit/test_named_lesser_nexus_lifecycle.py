"""Named scope publication retires names before reuse without observing anonymous pool cycles."""

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

import pytest

from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_pool import ConduitPool
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from tests._codegen_system_support import reset_runtime_singletons
from tests._frame_posture_test_support import (
    configure_frame_posture_for_spellbook_configuration,
)

if TYPE_CHECKING:
    from melder.nexus.frame_descriptor.frame_descriptor import FrameDescriptor


@pytest.fixture(autouse=True)
def isolated_world() -> Iterator[None]:
    """Retire real singleton ownership before and after every publication scenario."""
    reset_runtime_singletons()
    try:
        yield
    finally:
        reset_runtime_singletons()


def _root(dynamic: bool = True, publish: bool = True) -> Conduit:
    """Conjure a real empty Book with passive publication and no cache writes."""
    configuration = SpellbookConfiguration("named-nexus").with_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    posture = configure_frame_posture_for_spellbook_configuration(
        configuration, dynamic=dynamic, rift_enabled=publish,
    )
    posture.with_system_caching_enabled(False)
    return Spellbook(aetheric_frame="named-nexus", configuration=configuration).conjure(
        name="root", dynamic=dynamic,
    )


def _descriptor() -> FrameDescriptor:
    """Read the real passive record owner; tests do not simulate publication."""
    return Nexus()._get_required_frame_descriptor("named-nexus")


@pytest.mark.parametrize("dynamic", [False, True])
@pytest.mark.parametrize("prewarm", [False, True])
def test_named_acquisition_publishes_name_parent_and_cloud_summary(dynamic: bool, prewarm: bool) -> None:
    """Fresh and pooled named scopes publish exact topology without changing root accounting."""
    root = _root(dynamic)
    if prewarm:
        root.prewarm_lesser_conduits(1)
    child = root.create_lesser_conduit(name="request")
    record = _descriptor().conduit_records_by_id[child.id]
    assert record.payload.conduit_name == "request"
    assert record.payload.conduit_state is ConduitState.lesser
    assert record.payload.parent_conduit_id == root.id
    assert record.payload.lineage_depth == 1
    assert record.root_conduit_id == root.id
    overview = _descriptor().frame_overview.payload
    assert overview.root_conduit_ids == (root.id,)
    assert set(overview.conduit_cloud_names) == {"root", "request"}
    assert overview.conduit_cloud_entry_count == 2


def test_named_retirement_is_published_before_shell_is_idle(monkeypatch: pytest.MonkeyPatch) -> None:
    """A pool consumer must never receive a shell whose published record retains its former name."""
    root = _root()
    child = root.create_lesser_conduit(name="request")
    child_id = child.id
    original = ConduitPool.return_lesser_conduit
    observed: list[str] = []

    def publish_idle(pool: ConduitPool, conduit: Conduit) -> None:
        """Assert the public record/Cloud boundary before allowing actual deque publication."""
        record = _descriptor().conduit_records_by_id[child_id]
        assert record.payload.conduit_name is None
        assert record.payload.conduit_state is ConduitState.pooled_lesser
        assert record.payload.parent_conduit_id is None
        assert record.payload.lineage_depth == 0
        assert record.payload.peer_conduit_ids == ()
        assert record.root_conduit_id == root.id
        assert _descriptor().frame_overview.payload.conduit_cloud_names == ("root",)
        assert not root.get_conduit_cloud().has_conduit_name("request")
        observed.append(conduit.id)
        original(pool, conduit)

    monkeypatch.setattr(ConduitPool, "return_lesser_conduit", publish_idle)
    child.cleanup()
    assert observed == [child_id]


def test_same_id_named_reuse_replaces_parent_and_never_resurrects_old_name() -> None:
    """Name A, pooled retirement, name B and an anonymous acquisition cannot retain A or B."""
    root = _root()
    old_parent = root.create_lesser_conduit()
    new_parent = root.create_lesser_conduit()
    child = old_parent.create_lesser_conduit(name="old")
    child_id = child.id
    child.cleanup()
    reused = new_parent.create_lesser_conduit(name="new")
    assert reused is child
    record = _descriptor().conduit_records_by_id[child_id]
    assert record.payload.conduit_name == "new"
    assert record.payload.parent_conduit_id == new_parent.id
    assert record.payload.lineage_depth == 2
    assert set(_descriptor().frame_overview.payload.conduit_cloud_names) == {"root", "new"}
    reused.cleanup()
    assert root.create_lesser_conduit() is child
    assert _descriptor().conduit_records_by_id[child_id].payload.conduit_name is None


def test_post_created_can_recycle_same_shell_without_late_name_publication() -> None:
    """Post-created sees the published name and cannot be followed by stale outer publication."""
    root = _root()
    observed: list[str] = []

    def recycle(parent: Conduit, child: Conduit) -> None:
        """Replace the first lease inside the advisory callback after observing publication."""
        record = _descriptor().conduit_records_by_id[child.id]
        observed.append(record.payload.conduit_name)
        if child.name == "first":
            child.cleanup()
            assert parent.create_lesser_conduit(name="second") is child

    root.register_conduit_hooks({"on_conduit_post_created": recycle})
    child = root.create_lesser_conduit(name="first")
    assert observed == ["first", "second"]
    assert _descriptor().conduit_records_by_id[child.id].payload.conduit_name == "second"


@pytest.mark.parametrize("failure_stage", ["conduit", "frame"])
def test_failed_named_retirement_keeps_owner_and_can_retry(
    monkeypatch: pytest.MonkeyPatch, failure_stage: str,
) -> None:
    """Failed sinks cannot publish an idle shell or discard the retained cleanup route."""
    root = _root()
    child = root.create_lesser_conduit(name="request")
    child_id = child.id
    method = "_publish_conduit_record" if failure_stage == "conduit" else "_publish_frame_record"

    def fail(*_args: object, **_kwargs: object) -> bool:
        """Inject an unavailable publication sink at the external subsystem boundary."""
        raise RuntimeError("publication unavailable")

    with monkeypatch.context() as patch:
        patch.setattr(Nexus, method, fail)
        with pytest.raises(RuntimeError, match="publication unavailable"):
            child.cleanup()
    assert child.name == "request"
    assert child._conduit_ward._parent_conduit is root
    assert child_id in root._conduit_ward._lesser_conduits
    assert child not in root._conduit_pool._idle
    child.cleanup()
    assert _descriptor().conduit_records_by_id[child_id].payload.conduit_name is None
    assert root.create_lesser_conduit(name="retry") is child


def test_nested_named_retirement_and_hard_cleanup_refresh_cloud_summary() -> None:
    """Soft nesting retains cleared records; hard deletion removes the record and its Cloud name."""
    root = _root()
    parent = root.create_lesser_conduit(name="parent")
    child = parent.create_lesser_conduit(name="child")
    ids = (parent.id, child.id)
    parent.cleanup()
    for conduit_id in ids:
        assert _descriptor().conduit_records_by_id[conduit_id].payload.conduit_name is None
    assert _descriptor().frame_overview.payload.conduit_cloud_names == ("root",)
    hard = root.create_lesser_conduit(name="hard")
    hard_id = hard.id
    hard.permanent_cleanup()
    assert hard_id not in _descriptor().conduit_records_by_id
    assert _descriptor().frame_overview.payload.conduit_cloud_names == ("root",)


@pytest.mark.parametrize("publish", [False, True])
def test_unnamed_pool_return_never_enters_nexus(publish: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    """No new publication or directory work is permitted on ordinary anonymous pool return."""
    root = _root(publish=publish)
    child = root.create_lesser_conduit()

    def forbidden(*_args: object, **_kwargs: object) -> None:
        """Make any publication/removal attempt on the hot return path fail visibly."""
        pytest.fail("Unnamed return entered Nexus")

    with monkeypatch.context() as patch:
        patch.setattr(Nexus, "_publish_conduit_record", forbidden)
        patch.setattr(Nexus, "_publish_frame_record", forbidden)
        patch.setattr(Nexus, "_remove_conduit_record", forbidden)
        child.cleanup()
    assert root.create_lesser_conduit() is child


def test_failed_first_publication_does_not_create_a_ghost_pool_record(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cleanup of an unpublished named candidate must not invent a Nexus record for its shell."""
    root = _root()
    original = Nexus._publish_conduit_record

    def fail_active(nexus: Nexus, conduit: Conduit, *, pooled: bool = False) -> bool:
        """Fail initial active publication while retaining the real pooled-retirement behavior."""
        if not pooled:
            raise RuntimeError("initial publication failed")
        return original(nexus, conduit, pooled=pooled)

    with monkeypatch.context() as patch:
        patch.setattr(Nexus, "_publish_conduit_record", fail_active)
        with pytest.raises(RuntimeError, match="initial publication failed"):
            root.create_lesser_conduit(name="failed")
    assert not root.get_conduit_cloud().has_conduit_name("failed")
    assert set(_descriptor().conduit_records_by_id) == {root.id}
    child = root.create_lesser_conduit(name="recovered")
    assert _descriptor().conduit_records_by_id[child.id].payload.conduit_name == "recovered"


def test_non_publishable_named_cycles_never_call_nexus(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cloud naming works when Rift publication is disabled, with no Nexus sink calls."""
    root = _root(publish=False)

    def forbidden(*_args: object, **_kwargs: object) -> None:
        """Reject publication when the frame's cached publication flag is disabled."""
        pytest.fail("Non-publishable scope entered Nexus")

    with monkeypatch.context() as patch:
        patch.setattr(Nexus, "_publish_conduit_record", forbidden)
        patch.setattr(Nexus, "_publish_frame_record", forbidden)
        child = root.create_lesser_conduit(name="request")
        assert root.get_conduit_cloud().get_conduit("request") is child
        child.cleanup()
        assert not root.get_conduit_cloud().has_conduit_name("request")


def test_concurrent_named_cycles_leave_only_root_names() -> None:
    """Writer interleavings must converge to cleared shell records and a current Cloud summary."""
    root = _root()

    def cycle(index: int) -> None:
        """Acquire and retire one uniquely named scope through the actual locks and sinks."""
        child = root.create_lesser_conduit(name=f"request-{index}")
        assert root.get_conduit_cloud().get_conduit(f"request-{index}") is child
        child.cleanup()

    with ThreadPoolExecutor(max_workers=4) as workers:
        list(workers.map(cycle, range(32)))
    assert _descriptor().frame_overview.payload.conduit_cloud_names == ("root",)
    assert all(
        record.payload.conduit_name is None
        for conduit_id, record in _descriptor().conduit_records_by_id.items()
        if conduit_id != root.id
    )


def test_hard_cleanup_finishes_when_frame_summary_publication_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    """An observational summary failure cannot prevent permanent resource/discovery retirement."""
    root = _root()
    child = root.create_lesser_conduit(name="request")
    child_id = child.id

    def unavailable(*_args: object, **_kwargs: object) -> bool:
        """Fail only the summary sink, preserving the existing record-removal contract."""
        raise RuntimeError("summary unavailable")

    with monkeypatch.context() as patch:
        patch.setattr(Nexus, "_publish_frame_record", unavailable)
        child.permanent_cleanup()
    assert child.cleaned
    assert child_id not in _descriptor().conduit_records_by_id
    assert not root.get_conduit_cloud().has_conduit_name("request")
    replacement = root.create_lesser_conduit(name="request")
    assert root.get_conduit_cloud().get_conduit("request") is replacement
