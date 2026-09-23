"""Named scopes retire discovery before pooled reuse without changing root ownership."""

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from typing import Optional

import pytest

from melder.aether.aetheric_frame.conduit_cloud import ConduitCloud
from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_pool import ConduitPool
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.spellbook_creation_system import SpellbookCreationSystem
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration
from tests.component.melder.aether.conduit import test_conduit_graduation_ownership_regression as support

isolated_graduation_roots = support.isolated_graduation_roots


def _make_root(name: str = "root", frame: str = "named-lessers", dynamic: bool = True) -> Conduit:
    """Build a real empty root with one worker and no runtime cache writes.

    Contract:
        The caller owns returned-root cleanup; no fixture simulates registration.
    """
    configuration = SpellbookConfiguration(frame).with_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    book = Spellbook(aetheric_frame=frame, configuration=configuration)
    if not book._aetheric_frame_configuration._frozen:
        posture = configure_frame_posture_for_spellbook_configuration(configuration, dynamic=dynamic)
        posture.with_system_caching_enabled(False)
    try:
        return book.conjure(name=name, dynamic=dynamic)
    except Exception:
        book.cleanup()
        raise


@pytest.fixture
def root() -> Iterator[Conduit]:
    """Own one dynamic root and clean all its descendants after each test."""
    conduit = _make_root()
    try:
        yield conduit
    finally:
        conduit.permanent_cleanup()


@pytest.mark.parametrize("dynamic", [False, True], ids=["automatic", "dynamic"])
@pytest.mark.parametrize("prewarm", [False, True], ids=["fresh", "pooled"])
def test_named_lesser_is_discoverable_without_becoming_a_root(dynamic: bool, prewarm: bool) -> None:
    """Name/id/list/count discovery must agree for both acquisition paths and modes."""
    parent = _make_root(dynamic=dynamic)
    try:
        if prewarm:
            parent.prewarm_lesser_conduits(1)
        child = parent.create_lesser_conduit(name="request")
        cloud = parent.get_conduit_cloud()
        assert child.name == "request"
        assert cloud.get_conduit("request") is child
        assert cloud.get_conduit_by_name("request") is child
        assert cloud.get_conduit_by_id(child.id) is child
        assert cloud.find_conduit_id_by_name("request") == child.id
        assert cloud.has_conduit_id(child.id)
        assert cloud.has_conduit_name("request")
        assert set(cloud.list_conduit_ids()) == {parent.id, child.id}
        assert set(cloud.list_conduit_names()) == {"root", "request"}
        assert set(cloud.list_cloud_names()) == {"root", "request"}
        assert cloud.count_conduits() == 2
        assert set(parent._aetheric_frame._conduits) == {parent.id}
        assert child._spellbook is parent._spellbook
        assert child._conduit_state is ConduitState.lesser
    finally:
        parent.permanent_cleanup()


def test_return_retires_name_before_idle_publication(root: Conduit, monkeypatch: pytest.MonkeyPatch) -> None:
    """Pool publication must never expose a shell still reachable by its previous name."""
    child = root.create_lesser_conduit(name="old")
    cloud = root.get_conduit_cloud()
    original = ConduitPool.return_lesser_conduit
    observed: list[str] = []

    def publish(pool: ConduitPool, conduit: Conduit) -> None:
        """Inspect the observable lifetime boundary immediately before deque publication."""
        assert conduit.name is None
        assert not cloud.has_conduit_name("old")
        assert not cloud.has_conduit_id(conduit.id)
        observed.append(conduit.id)
        original(pool, conduit)

    monkeypatch.setattr(ConduitPool, "return_lesser_conduit", publish)
    child.cleanup()
    assert observed == [child.id]
    assert cloud.count_conduits() == 1


def test_same_shell_can_be_named_a_then_b_then_unnamed(root: Conduit) -> None:
    """Neither names nor directory entries may leak from one pooled use into the next."""
    cloud = root.get_conduit_cloud()
    first = root.create_lesser_conduit(name="A")
    identity = first.id
    first.cleanup()
    second = root.create_lesser_conduit(name="B")
    assert second is first
    assert second.id == identity
    assert not cloud.has_conduit_name("A")
    assert cloud.get_conduit("B") is second
    second.cleanup()
    unnamed = root.create_lesser_conduit()
    assert unnamed is first
    assert unnamed.name is None
    assert cloud.list_conduit_names() == ("root",)
    assert not cloud.has_conduit_id(identity)


def test_unnamed_cycles_never_call_directory_mutation(root: Conduit, monkeypatch: pytest.MonkeyPatch) -> None:
    """Even prewarming and reuse must bypass named registration and removal entirely."""
    def forbidden(*args: object, **kwargs: object) -> None:
        """Fail if unnamed lifecycle work enters the named directory."""
        pytest.fail("Unnamed scope entered the named directory")

    with monkeypatch.context() as patch:
        patch.setattr(ConduitCloud, "_register_named_conduit", forbidden)
        patch.setattr(ConduitCloud, "_unregister_named_conduit", forbidden)
        root.prewarm_lesser_conduits(2)
        for _ in range(3):
            child = root.create_lesser_conduit()
            child.cleanup()
    assert root.get_conduit_cloud().list_conduit_names() == ("root",)


@pytest.mark.parametrize("existing_name", ["root", "request"])
def test_duplicate_name_preserves_existing_owner(root: Conduit, existing_name: str) -> None:
    """Lesser names share the root namespace and collision cleanup cannot evict the winner."""
    existing = root if existing_name == "root" else root.create_lesser_conduit(name="request")
    with pytest.raises(ValueError, match="already exists"):
        root.create_lesser_conduit(name=existing_name)
    assert root.get_conduit_cloud().get_conduit(existing_name) is existing
    child = root.create_lesser_conduit(name="free")
    assert child.name == "free"


def test_new_root_cannot_take_an_active_lesser_name(root: Conduit) -> None:
    """Root admission must consult the same name authority as lesser acquisition."""
    child = root.create_lesser_conduit(name="request")
    with pytest.raises(ValueError, match="already exists"):
        _make_root(name="request")
    assert root.get_conduit_cloud().get_conduit("request") is child
    assert set(root._aetheric_frame._conduits) == {root.id}


@pytest.mark.parametrize("name, error", [("", ValueError), (12, TypeError), (False, TypeError)])
def test_invalid_name_fails_before_creation_hooks(root: Conduit, name: object, error: type[Exception]) -> None:
    """Invalid name input must not acquire a shell or invoke application hooks."""
    calls: list[Conduit] = []
    root.register_conduit_hooks({"on_conduit_pre_created": calls.append})
    with pytest.raises(error):
        root.create_lesser_conduit(name=name)
    assert calls == []
    assert root.get_conduit_cloud().list_conduit_names() == ("root",)


@pytest.mark.parametrize("named", [False, True])
def test_lesser_cannot_be_named_or_renamed_after_creation(root: Conduit, named: bool) -> None:
    """Only the creation API may assign a lesser name, including to prewarmed shells."""
    child = root.create_lesser_conduit(name="first" if named else None)
    with pytest.raises(RuntimeError, match="creation"):
        child.name = "later"
    child.cleanup()
    with pytest.raises(RuntimeError, match="creation"):
        child.name = "idle"
    assert not root.get_conduit_cloud().has_conduit_name("later")


def test_parent_cleanup_retires_nested_names(root: Conduit) -> None:
    """A named descendant under unnamed ancestry retires with that immediate parent."""
    parent = root.create_lesser_conduit()
    child = parent.create_lesser_conduit(name="nested")
    grandchild = child.create_lesser_conduit(name="deep")
    cloud = root.get_conduit_cloud()
    parent.cleanup()
    assert child.name is None
    assert grandchild.name is None
    assert cloud.list_conduit_names() == ("root",)


def test_root_cleanup_retires_descendants_without_affecting_other_roots(root: Conduit) -> None:
    """Hard teardown must clear owned names while the shared frame remains alive."""
    survivor = _make_root(name="survivor")
    cloud = survivor.get_conduit_cloud()
    try:
        child = root.create_lesser_conduit(name="child")
        child.create_lesser_conduit(name="grandchild")
        root.cleanup()
        assert cloud.list_conduit_names() == ("survivor",)
    finally:
        survivor.cleanup()


def test_permanent_cleanup_and_overflow_leave_no_named_entries(root: Conduit) -> None:
    """Both direct hard cleanup and pool overflow must release names for later acquisition."""
    child = root.create_lesser_conduit(name="direct")
    child.permanent_cleanup()
    assert not root.get_conduit_cloud().has_conduit_name("direct")
    root._conduit_pool._target_idle = 0
    overflow = root.create_lesser_conduit(name="overflow")
    overflow.cleanup()
    assert not root.get_conduit_cloud().has_conduit_name("overflow")
    assert overflow._cleaned


def test_named_lesser_cannot_join_a_cluster(root: Conduit) -> None:
    """Discovery grants neither root ownership nor cluster membership."""
    child = root.create_lesser_conduit(name="request")
    cloud = root.get_conduit_cloud()
    cloud.create_cluster("group")
    with pytest.raises(RuntimeError, match="normal conduit"):
        cloud.add_conduit_to_cluster(child, "group")
    assert cloud.get_clusters_for_conduit(child.id) == []


def test_identical_names_are_isolated_between_frames(root: Conduit) -> None:
    """Each frame's directory can independently publish the same exact scope name."""
    other = _make_root(frame="other-frame")
    try:
        left = root.create_lesser_conduit(name="Request")
        right = other.create_lesser_conduit(name="Request")
        assert root.get_conduit_cloud().get_conduit("Request") is left
        assert other.get_conduit_cloud().get_conduit("Request") is right
        assert not root.get_conduit_cloud().has_conduit_name("request")
    finally:
        other.cleanup()


def test_concurrent_name_claims_publish_one_lesser(root: Conduit) -> None:
    """Contending acquisitions must admit one winner without leaking failed shells or aliases."""
    root.prewarm_lesser_conduits(5)
    barrier = Barrier(5)

    def synchronize(conduit: Conduit) -> None:
        """Hold all candidates after early name checks but before atomic publication."""
        barrier.wait(timeout=5)

    root.register_conduit_hooks({"on_conduit_activated": synchronize})

    def acquire() -> Optional[Conduit]:
        """Attempt the same name after all workers reach the admission race."""
        try:
            return root.create_lesser_conduit(name="contended")
        except ValueError:
            return None

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(lambda _: acquire(), range(5)))
    winners = [conduit for conduit in results if conduit is not None]
    assert len(winners) == 1
    assert root.get_conduit_cloud().get_conduit("contended") is winners[0]
    assert root.get_conduit_cloud().count_conduits() == 2


@pytest.mark.parametrize("old_name,new_name", [(None, "normal"), ("same", "same"), ("old", "new")])
def test_promotion_keeps_one_current_name(root: Conduit, old_name: Optional[str], new_name: str) -> None:
    """Promotion retains identity and publishes exactly the requested normal-root name."""
    child = root.create_lesser_conduit(name=old_name)
    identity = child.id
    cloud = root.get_conduit_cloud()
    try:
        child.upgrade_to_normal(name=new_name)
        assert cloud.get_conduit(new_name) is child
        assert cloud.get_conduit_by_id(identity) is child
        assert cloud.count_conduits() == 2
        assert child._spellbook is not root._spellbook
        assert child._spellbook.conduit is child
        assert child._conduit_ward._parent_conduit is None
        if old_name is not None and old_name != new_name:
            assert not cloud.has_conduit_name(old_name)
    finally:
        child.permanent_cleanup()
    assert cloud.list_conduit_names() == ("root",)


def test_promotion_collision_keeps_both_lesser_entries(root: Conduit) -> None:
    """Reject another lesser's name before changing the upgrading scope or its Book."""
    child = root.create_lesser_conduit(name="mine")
    other = root.create_lesser_conduit(name="occupied")
    with pytest.raises(ValueError, match="already exists"):
        child.upgrade_to_normal(name="occupied")
    assert child.name == "mine"
    assert child._conduit_state is ConduitState.lesser
    assert child._spellbook is root._spellbook
    assert root.get_conduit_cloud().get_conduit("mine") is child
    assert root.get_conduit_cloud().get_conduit("occupied") is other


def test_failed_promotion_preserves_old_name_and_releases_requested_name(
    root: Conduit, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A pre-attachment phase failure must retain the original lesser discovery entry."""
    child = root.create_lesser_conduit(name="before")
    cloud = root.get_conduit_cloud()

    def refuse(**kwargs: object) -> None:
        """Fail before Book attachment, after proving the destination name is reserved."""
        assert cloud.get_conduit("before") is child
        assert not cloud.has_conduit_name("after")
        with pytest.raises(ValueError, match="already exists"):
            root.create_lesser_conduit(name="after")
        raise RuntimeError("before attachment")

    with monkeypatch.context() as patch:
        patch.setattr(SpellbookCreationSystem, "run_resolution_phases_for_conduit", staticmethod(refuse))
        with pytest.raises(RuntimeError, match="before attachment"):
            child.upgrade_to_normal(name="after")
    assert child.name == "before"
    assert child._conduit_state is ConduitState.lesser
    assert child._conduit_ward._parent_conduit is root
    assert cloud.get_conduit("before") is child
    replacement = root.create_lesser_conduit(name="after")
    assert cloud.get_conduit("after") is replacement


def test_post_attachment_failure_is_removed_by_normal_cleanup(
    root: Conduit, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A registration-tail failure keeps its new owner until caller cleanup retires discovery."""
    child = root.create_lesser_conduit(name="before")

    def refuse(conduit: Conduit) -> None:
        """Raise only after the normal root and new name are actually registered."""
        assert root.get_conduit_cloud().get_conduit("after") is conduit
        raise RuntimeError("after attachment")

    monkeypatch.setattr(Conduit, "_add_spells_to_aether", refuse)
    try:
        with pytest.raises(RuntimeError, match="after attachment"):
            child.upgrade_to_normal(name="after")
        assert child._conduit_state is ConduitState.normal
        assert not root.get_conduit_cloud().has_conduit_name("before")
    finally:
        child.permanent_cleanup()
    assert root.get_conduit_cloud().list_conduit_names() == ("root",)


@pytest.mark.parametrize("prewarm", [False, True])
def test_hooks_observe_name_then_linked_discovery_and_remain_advisory(root: Conduit, prewarm: bool) -> None:
    """Activation sees the assigned name; post-created sees the directory entry despite hook errors."""
    if prewarm:
        root.prewarm_lesser_conduits(1)
    cloud = root.get_conduit_cloud()
    events: list[tuple[str, Optional[str], bool]] = []

    def activated(child: Conduit) -> None:
        """Record pre-publication state, then exercise existing advisory failure semantics."""
        events.append(("activation", child.name, cloud.has_conduit_name("hooked")))
        raise RuntimeError("advisory")

    def completed(parent: Conduit, child: Conduit) -> None:
        """Record discovery after attachment without relying on swallowed assertions."""
        events.append(("post", child.name, cloud.get_conduit("hooked") is child))

    root.register_conduit_hooks({"on_conduit_activated": activated, "on_conduit_post_created": completed})
    child = root.create_lesser_conduit(name="hooked")
    assert events == [("activation", "hooked", False), ("post", "hooked", True)]
    child.cleanup()
    assert not cloud.has_conduit_name("hooked")


def test_activation_cleanup_does_not_publish_a_pooled_named_shell(root: Conduit) -> None:
    """A hook may retire an unpublished candidate; named linking must not resurrect it."""
    root.register_conduit_hooks({"on_conduit_activated": Conduit.cleanup})
    with pytest.raises(RuntimeError, match="retired"):
        root.create_lesser_conduit(name="retired")
    assert root.get_conduit_cloud().list_conduit_names() == ("root",)
    root.set_conduit_hooks({"on_conduit_activated": []})
    child = root.create_lesser_conduit(name="next")
    assert root.get_conduit_cloud().get_conduit("next") is child


def test_activation_hard_cleanup_does_not_resurrect_a_named_shell(root: Conduit) -> None:
    """The attachment state check must reject a callback-destroyed candidate before dereferencing its ward."""
    root.register_conduit_hooks({"on_conduit_activated": Conduit.permanent_cleanup})
    with pytest.raises(RuntimeError, match="retired.*cleaned"):
        root.create_lesser_conduit(name="destroyed")
    assert root.get_conduit_cloud().list_conduit_names() == ("root",)
    root.set_conduit_hooks({"on_conduit_activated": []})
    child = root.create_lesser_conduit(name="next")
    assert root.get_conduit_cloud().get_conduit("next") is child


def test_public_upgrade_refuses_a_permanently_cleaned_lesser(root: Conduit) -> None:
    """Public promotion retains cleaned-state refusal after private helpers stop repeating it."""
    child = root.create_lesser_conduit(name="ended")
    child.permanent_cleanup()
    with pytest.raises(RuntimeError, match="cleaned"):
        child.upgrade_to_normal("must-not-appear")
    assert root.get_conduit_cloud().list_conduit_names() == ("root",)


def test_parent_cleanup_during_activation_does_not_publish_the_orphan(root: Conduit) -> None:
    """Named acquisition must hard-retire an unlinked shell after its parent has been destroyed."""
    cloud = root.get_conduit_cloud()

    def close_parent(child: Conduit) -> None:
        """Retire the parent between shell allocation and the attachment window."""
        root.cleanup()

    root.register_conduit_hooks({"on_conduit_activated": close_parent})
    with pytest.raises(RuntimeError, match="cleaned"):
        root.create_lesser_conduit(name="orphan")
    assert cloud.count_conduits() == 0


class FailingDisposal:
    """Creation whose first and only retained disposal attempt raises visibly."""

    def __init__(self) -> None:
        """Initialize an observable disposal count without dependencies."""
        self.calls = 0

    def cleanup(self) -> None:
        """Increment before failure so the test can distinguish retry from duplicate disposal."""
        self.calls += 1
        raise RuntimeError("disposal failed")


def test_disposal_failure_leaves_name_until_pool_reset_completes(root: Conduit) -> None:
    """Failed store disposal does not falsely advertise a completed scope retirement."""
    with root.transaction("bind"):
        spell_id = root.bind(spell=FailingDisposal, existence=Existence.many, disposal_method_names=["cleanup"])
    child = root.create_lesser_conduit(name="disposal")
    instance = child.meld(spell_id=spell_id)
    with pytest.raises(ExceptionGroup):
        child.cleanup()
    assert instance.calls == 1
    assert root.get_conduit_cloud().get_conduit("disposal") is child
    assert child._conduit_state is ConduitState.lesser
    # Existing Creations semantics detach failed-disposal entries before raising.
    child.cleanup()
    assert instance.calls == 1
    assert child.name is None
    assert not root.get_conduit_cloud().has_conduit_name("disposal")


def test_unnamed_return_does_not_acquire_the_cloud_lock(root: Conduit) -> None:
    """A forbidden lock distinguishes one local name check from even a no-op Cloud call."""
    child = root.create_lesser_conduit()
    cloud = root.get_conduit_cloud()
    original_lock = cloud._lock

    class ForbiddenLock:
        """Fail loudly if the unnamed return path reaches the directory lock."""

        def __enter__(self) -> None:
            """Reject a hidden directory read or write during unnamed cleanup."""
            pytest.fail("Unnamed return acquired the Cloud lock")

        def __exit__(self, *args: object) -> None:
            """Satisfy the context-manager shape; entry must never be reached."""

    try:
        cloud._lock = ForbiddenLock()
        child.cleanup()
    finally:
        cloud._lock = original_lock
    assert root.create_lesser_conduit() is child


def test_pooled_parent_cannot_publish_a_named_child(root: Conduit) -> None:
    """An idle shell is capacity, not an active owner of discoverable descendants."""
    parent = root.create_lesser_conduit()
    parent.cleanup()
    with pytest.raises(RuntimeError, match="active parent"):
        parent.create_lesser_conduit(name="orphan")
    assert root.get_conduit_cloud().list_conduit_names() == ("root",)


def test_parent_returned_during_activation_cannot_publish_a_named_child(root: Conduit) -> None:
    """Soft return in a hook must be rechecked at named attachment, not only at entry."""
    parent = root.create_lesser_conduit()

    def return_parent(child: Conduit) -> None:
        """Return the immediate owner before its new named child has been linked."""
        parent.cleanup()

    parent.register_conduit_hooks({"on_conduit_activated": return_parent})
    with pytest.raises(RuntimeError, match="active parent"):
        parent.create_lesser_conduit(name="orphan")
    assert root.get_conduit_cloud().list_conduit_names() == ("root",)


def test_failed_root_registration_cleans_original_lesser_alias(
    root: Conduit, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Failure after Book attachment but before root publication must not strand the old name."""
    child = root.create_lesser_conduit(name="before")

    def refuse(frame: AethericFrame, conduit: Conduit) -> None:
        """Fail root publication after the receiving Book has been installed."""
        raise RuntimeError("root publication failed")

    monkeypatch.setattr(AethericFrame, "register_root_conduit", refuse)
    try:
        with pytest.raises(RuntimeError, match="root publication failed"):
            child.upgrade_to_normal(name="after")
        assert child._conduit_state is ConduitState.normal
        assert child._spellbook is not root._spellbook
    finally:
        child.permanent_cleanup()
    assert root.get_conduit_cloud().list_conduit_names() == ("root",)
