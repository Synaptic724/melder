"""Contracts for scoped purge, native disposal and creation-writer synchronization."""

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from threading import Event, RLock, Thread, get_ident
from types import TracebackType
from typing import Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from tests.component.melder.aether.conduit.test_conduit_component_creations import _make_spellbook


class PurgeResource:
    """Disposable factory result exposing its lifetime without external resources."""

    def __init__(self, marker: int = 0) -> None:
        """Retain constructor input and initialize the explicit disposal count."""
        self.marker = marker
        self.cleanup_calls = 0

    def cleanup(self) -> None:
        """Record disposal while keeping this test object inspectable."""
        self.cleanup_calls += 1


class PurgeOther(PurgeResource):
    """Distinct registration used to prove target-only removal."""

    def cleanup(self) -> None:
        """Declare disposal on this class for bind-time method-name discovery."""
        super().cleanup()


class PurgePlain:
    """Non-disposable result whose many instances must remain untracked."""

    def __init__(self) -> None:
        """Provide an explicit zero-argument application constructor."""
        self.marker = object()


@pytest.fixture(autouse=True)
def isolated_purge_world() -> Iterator[None]:
    """Reset owned runtime singletons around each independent contract test."""
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()
    Conduit._aether = Aether()
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()
    Conduit._aether = Aether()


@pytest.mark.parametrize("dynamic", [False, True])
@pytest.mark.parametrize("existence", [
    Existence.unique,
    Existence.unique_per_conduit,
    Existence.unique_per_conduit_lineage,
    Existence.unique_per_spell_space,
    Existence.many,
])
def test_purge_retires_only_target_and_reuses_the_compiled_context(
    existence: Existence, dynamic: bool,
) -> None:
    """Remove retained target instances, preserve another binding, and re-meld without recompiling."""
    book = _make_spellbook(dynamic=dynamic, disposal=True)
    target_id = book.bind(spell=PurgeResource, existence=existence, permissions="create")
    other_id = book.bind(spell=PurgeOther, existence=existence, permissions="create")
    root = book.conjure(dynamic=dynamic, name="purge-root")
    space = root.create_spellspace()
    try:
        caller = space if existence is Existence.unique_per_spell_space else root
        assert caller.purge(spell_id=target_id) == 0
        first = caller.meld(spell_id=target_id)
        second = caller.meld(spell_id=target_id)
        other = caller.meld(spell_id=other_id)
        context = book._spells_by_id[target_id]._creation_context
        expected = 2 if existence is Existence.many else 1
        assert caller.purge(spell_id=target_id) == expected
        assert first.cleanup_calls == 1
        assert second.cleanup_calls == 1
        assert other.cleanup_calls == 0
        assert caller.purge(spell_id=target_id) == 0
        replacement = caller.meld(spell_id=target_id, override={"marker": 12})
        assert replacement is not first
        assert replacement.marker == 12
        assert book._spells_by_id[target_id]._creation_context is context
    finally:
        space.cleanup()
        root.permanent_cleanup()
    assert first.cleanup_calls == 1
    assert replacement.cleanup_calls == 1


@pytest.mark.parametrize("existence", [Existence.many, Existence.unique_per_conduit])
def test_lesser_purge_preserves_root_and_sibling_creations(existence: Existence) -> None:
    """Each conduit controls its own local creations even when all share one Spellbook."""
    book = _make_spellbook(disposal=True)
    spell_id = book.bind(spell=PurgeResource, existence=existence, permissions="create")
    root = book.conjure(name="local-root")
    left = root.create_lesser_conduit()
    right = root.create_lesser_conduit()
    try:
        root_obj = root.meld(spell_id=spell_id)
        left_obj = left.meld(spell_id=spell_id)
        right_obj = right.meld(spell_id=spell_id)
        assert left.purge(spell_id=spell_id) == 1
        assert left_obj.cleanup_calls == 1
        assert root_obj.cleanup_calls == right_obj.cleanup_calls == 0
        assert left.meld(spell_id=spell_id) is not left_obj
    finally:
        left.cleanup()
        right.cleanup()
        root.permanent_cleanup()


@pytest.mark.parametrize("existence", [Existence.many, Existence.unique_per_spell_space])
def test_spellspace_purge_preserves_other_scopes(existence: Existence) -> None:
    """Nested scopes retire only their own entries and remain usable until ordinary exit."""
    book = _make_spellbook(disposal=True)
    spell_id = book.bind(spell=PurgeResource, existence=existence, permissions="create")
    root = book.conjure(name="space-root")
    try:
        root_obj = root.meld(spell_id=spell_id) if existence is Existence.many else None
        with root.enter_spellspace() as outer:
            outer_obj = outer.meld(spell_id=spell_id)
            with root.enter_spellspace() as inner:
                inner_obj = inner.meld(spell_id=spell_id)
                assert inner.purge(spell_id=spell_id) == 1
                assert inner_obj.cleanup_calls == 1
                assert outer_obj.cleanup_calls == 0
                assert root.get_active_spellspace() is inner
                assert inner.meld(spell_id=spell_id) is not inner_obj
            assert outer_obj.cleanup_calls == 0
        assert outer_obj.cleanup_calls == 1
        if root_obj is not None:
            assert root_obj.cleanup_calls == 0
    finally:
        root.permanent_cleanup()


@pytest.mark.parametrize("existence", [Existence.unique, Existence.unique_per_conduit_lineage])
def test_lesser_cannot_use_resolution_root_identity_to_purge(existence: Existence) -> None:
    """A lesser can resolve shared objects but cannot retire the root's instance."""
    book = _make_spellbook(disposal=True)
    spell_id = book.bind(spell=PurgeResource, existence=existence, permissions="create")
    root = book.conjure(name="authority-root")
    lesser = root.create_lesser_conduit()
    try:
        obj = lesser.meld(spell_id=spell_id)
        with pytest.raises(RuntimeError, match="purge"):
            lesser.purge(spell_id=spell_id)
        assert obj.cleanup_calls == 0
        assert root.purge(spell_id=spell_id) == 1
        assert obj.cleanup_calls == 1
    finally:
        lesser.cleanup()
        root.permanent_cleanup()


@pytest.mark.parametrize("existence", [
    Existence.unique, Existence.unique_per_conduit,
    Existence.unique_per_conduit_lineage, Existence.unique_per_conduit_cluster,
])
def test_spellspace_never_delegates_purge_to_broader_stores(existence: Existence) -> None:
    """Even a root-owned SpellSpace must refuse broader-scope removal before touching storage."""
    book = _make_spellbook(dynamic=True, disposal=True)
    spell_id = book.bind(spell=PurgeResource, existence=existence, permissions="create")
    root = book.conjure(dynamic=True, name="broader-root")
    space = root.create_spellspace()
    try:
        with pytest.raises(RuntimeError, match="SpellSpace"):
            space.purge(spell_id=spell_id)
    finally:
        space.cleanup()
        root.permanent_cleanup()


def test_conduit_cannot_purge_the_active_spellspace() -> None:
    """A conduit never substitutes its thread's active SpellSpace for the actual caller."""
    book = _make_spellbook(disposal=True)
    spell_id = book.bind(spell=PurgeResource, existence=Existence.unique_per_spell_space, permissions="create")
    root = book.conjure(name="ambient-root")
    try:
        with root.enter_spellspace() as space:
            obj = space.meld(spell_id=spell_id)
            with pytest.raises(RuntimeError, match="SpellSpace"):
                root.purge(spell_id=spell_id)
            assert obj.cleanup_calls == 0
            assert space.purge(spell_id=spell_id) == 1
    finally:
        root.permanent_cleanup()


@pytest.mark.parametrize("selector", ["id", "name", "class", "frame"])
def test_purge_accepts_normal_meld_selectors(selector: str) -> None:
    """Logical names, classes, frames and explicit ids all select the same named binding."""
    book = _make_spellbook(disposal=True)
    spell_id = book.bind(spell=PurgeResource, existence=Existence.unique, permissions="create", binding_name="blue")
    root = book.conjure(name="selector-root")
    try:
        obj = root.meld(spell_id=spell_id)
        if selector == "id":
            count = root.purge(spell_id=spell_id)
        elif selector == "name":
            count = root.purge(book._spells_by_id[spell_id].spell_name, binding_name="blue")
        elif selector == "class":
            count = root.purge(PurgeResource, binding_name="blue")
        else:
            count = root.purge(spellframe=PurgeResource, binding_name="blue")
        assert count == 1
        assert obj.cleanup_calls == 1
    finally:
        root.permanent_cleanup()


@pytest.mark.parametrize("value", [None, False, 0, [], [1, 2], {}, {"x": 1}])
def test_native_purge_counts_singleton_values_by_existence(value: object) -> None:
    """Falsey or container-shaped application values are one singleton, never a many bucket."""
    book = _make_spellbook()
    spell_id = book.bind(spell=PurgePlain, existence=Existence.unique, permissions="create")
    root = book.conjure(name="value-root")
    try:
        expected = list(value) if isinstance(value, list) else dict(value) if isinstance(value, dict) else value
        root._creations.add_creation(spell_id, value)
        assert root._creations.purge(book._spells_by_id[spell_id]) == 1
        assert root._creations.purge(book._spells_by_id[spell_id]) == 0
        assert value == expected
    finally:
        root.permanent_cleanup()


def test_non_disposable_many_has_no_retained_objects_to_purge() -> None:
    """Purge does not introduce retention for transient results with no disposal methods."""
    book = _make_spellbook(disposal=True)
    spell_id = book.bind(spell=PurgePlain, existence=Existence.many, permissions="create")
    root = book.conjure(name="untracked-root")
    try:
        first = root.meld(spell_id=spell_id)
        assert root.purge(spell_id=spell_id) == 0
        assert root.meld(spell_id=spell_id) is not first
    finally:
        root.permanent_cleanup()


@pytest.mark.parametrize("spellspace", [False, True])
def test_instance_purge_is_explicitly_deferred_without_removing_entries(spellspace: bool) -> None:
    """Deferred reference/False calls fail before mutation; normal selectors purge the full bucket."""
    book = _make_spellbook(disposal=True)
    spell_id = book.bind(spell=PurgeResource, existence=Existence.many, permissions="create")
    root = book.conjure(name="single-many-root")
    space = root.create_spellspace()
    try:
        caller = space if spellspace else root
        first = caller.meld(spell_id=spell_id)
        second = caller.meld(spell_id=spell_id)
        third = caller.meld(spell_id=spell_id)
        with pytest.raises(NotImplementedError, match="purge_all=False"):
            caller.purge(second, purge_all=False)
        with pytest.raises(NotImplementedError, match="Instance-reference"):
            caller.purge(second)
        assert first.cleanup_calls == second.cleanup_calls == third.cleanup_calls == 0
        assert caller.purge(PurgeResource) == 3
        assert first.cleanup_calls == second.cleanup_calls == third.cleanup_calls == 1
    finally:
        space.cleanup()
        root.permanent_cleanup()


def test_purge_disposes_many_in_reverse_and_keeps_existing_method_failure_semantics() -> None:
    """Reuse newest-first disposal, method order, per-object failure stop and error aggregation."""
    events: list[tuple[int, str]] = []

    class OrderedResource:
        """Expose the existing two-method disposal contract for a many bucket."""

        def __init__(self, marker: int = 0) -> None:
            """Retain the per-instance test marker."""
            self.marker = marker

        def first(self) -> None:
            """Record the first method, failing on one selected instance."""
            events.append((self.marker, "first"))
            if self.marker == 2:
                raise ValueError("selected disposal failure")

        def second(self) -> None:
            """Record the second method only when the first completed."""
            events.append((self.marker, "second"))

    book = _make_spellbook(disposal=True, disposal_methods=["first", "second"])
    spell_id = book.bind(spell=OrderedResource, existence=Existence.many, permissions="create")
    root = book.conjure(name="ordered-root")
    try:
        for marker in (1, 2, 3):
            root.meld(spell_id=spell_id, override={"marker": marker})
        with pytest.raises(ExceptionGroup) as failure:
            root.purge(spell_id=spell_id)
        assert len(failure.value.exceptions) == 1
        assert events == [(3, "first"), (3, "second"), (2, "first"), (1, "first"), (1, "second")]
        assert root.purge(spell_id=spell_id) == 0
        assert book._spells_by_id[spell_id].disposal_method_names == ["first", "second"]
    finally:
        root.permanent_cleanup()
    assert len(events) == 5


class ObservedLock:
    """Real RLock wrapper exposing acquisition attempts/order at the synchronization boundary."""

    def __init__(self, name: str, trace: list[str]) -> None:
        """Own the underlying lock and test-only acquisition signal."""
        self.lock = RLock()
        self.name = name
        self.trace = trace
        self.watched_thread: Optional[int] = None
        self.attempted = Event()

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        """Signal a watched attempt before blocking on the real lock."""
        if get_ident() == self.watched_thread:
            self.attempted.set()
        acquired = self.lock.acquire(blocking, timeout)
        if acquired:
            self.trace.append(self.name + ":enter")
        return acquired

    def release(self) -> None:
        """Record the release before waking another waiter."""
        self.trace.append(self.name + ":exit")
        self.lock.release()

    def __enter__(self) -> ObservedLock:
        """Acquire the real synchronization boundary."""
        self.acquire()
        return self

    def __exit__(
        self, exc_type: Optional[type[BaseException]], exc: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """Release independently of the protected operation's result."""
        self.release()


@pytest.mark.parametrize("existence", list(Existence))
def test_native_purge_mirrors_creation_lock_family_and_order(existence: Existence) -> None:
    """Unique takes Spell then store; all other storage modes take only their store lock."""
    book = _make_spellbook(dynamic=True)
    spell_id = book.bind(spell=PurgeResource, existence=existence, permissions="create")
    root = book.conjure(dynamic=True, name="lock-root")
    spell = book._spells_by_id[spell_id]
    store = root._creations
    original_spell_lock, original_store_lock = spell._lock, store._lock
    trace: list[str] = []
    try:
        if existence is Existence.many:
            store.add_many_creations(spell_id, object())
        else:
            store.add_creation(spell_id, object())
        spell._lock = ObservedLock("spell", trace)
        store._lock = ObservedLock("store", trace)
        assert store.purge(spell) == 1
        expected = ["store:enter", "store:exit"]
        if existence is Existence.unique:
            expected = ["spell:enter", *expected, "spell:exit"]
        assert trace == expected
    finally:
        spell._lock, store._lock = original_spell_lock, original_store_lock
        root.permanent_cleanup()


@pytest.mark.parametrize("existence", [
    Existence.unique, Existence.unique_per_conduit,
    Existence.unique_per_conduit_lineage, Existence.unique_per_spell_space,
])
def test_purge_waits_for_the_actual_singleton_constructor_lock(existence: Existence) -> None:
    """A purge racing real construction waits on the same lock and retires the published object."""
    entered, finish = Event(), Event()

    class BlockingResource(PurgeResource):
        """Hold the real generated creation path inside its constructor."""

        def __init__(self) -> None:
            """Announce entry and wait for deterministic test release."""
            super().__init__()
            entered.set()
            if not finish.wait(5):
                raise RuntimeError("Constructor release timed out.")

        def cleanup(self) -> None:
            """Declare disposal directly so the race also checks tracked cleanup."""
            super().cleanup()

    book = _make_spellbook(disposal=True)
    spell_id = book.bind(spell=BlockingResource, existence=existence, permissions="create")
    root = book.conjure(name="race-root")
    space = root.create_spellspace()
    caller = space if existence is Existence.unique_per_spell_space else root
    store = space._creations if existence is Existence.unique_per_spell_space else root._creations
    spell = book._spells_by_id[spell_id]
    lock_owner = spell if existence is Existence.unique else store
    original_lock = lock_owner._lock
    observed = ObservedLock("writer", [])
    lock_owner._lock = observed

    def run_purge() -> int:
        """Mark this thread so the test observes entry into the actual writer lock."""
        observed.watched_thread = get_ident()
        return caller.purge(spell_id=spell_id)

    try:
        with ThreadPoolExecutor(max_workers=2) as workers:
            creation_future = workers.submit(caller.meld, spell_id=spell_id)
            try:
                assert entered.wait(5)
                purge_future = workers.submit(run_purge)
                assert observed.attempted.wait(5)
                assert not purge_future.done()
            finally:
                finish.set()
            obj = creation_future.result(timeout=5)
            assert purge_future.result(timeout=5) == 1
            assert obj.cleanup_calls == 1
            assert caller.meld(spell_id=spell_id) is not obj
    finally:
        finish.set()
        lock_owner._lock = original_lock
        space.cleanup()
        root.permanent_cleanup()


def test_disposal_runs_outside_locks_and_keeps_callback_replacement() -> None:
    """Disposal can acquire writer locks from another thread and publish an untouched replacement."""
    book = _make_spellbook(disposal=True)
    spell_id = book.bind(spell=PurgeResource, existence=Existence.unique, permissions="create")
    root = book.conjure(name="callback-root")
    spell = book._spells_by_id[spell_id]
    store = root._creations
    replacement = PurgeResource()
    available = Event()

    class ReplacingResource:
        """Retained entry whose disposal inspects lock boundaries and adds a replacement."""

        def cleanup(self) -> None:
            """Require external lock access before replacing the detached entry."""
            def check_locks() -> None:
                """Acquire in normal unique writer order from an independent thread."""
                with spell._lock:
                    with store._lock:
                        available.set()

            worker = Thread(target=check_locks, daemon=True)
            worker.start()
            assert available.wait(3), "Disposal retained a removal lock."
            worker.join(timeout=3)
            store.add_creation(spell_id, replacement, has_disposal_methods=True, disposal_methods=["cleanup"])

    try:
        store.add_creation(spell_id, ReplacingResource(), has_disposal_methods=True, disposal_methods=["cleanup"])
        assert root.purge(spell_id=spell_id) == 1
        assert root.meld(spell_id=spell_id) is replacement
        assert replacement.cleanup_calls == 0
    finally:
        root.permanent_cleanup()
    assert replacement.cleanup_calls == 1


def test_cluster_leader_can_purge_a_spell_owned_by_another_member() -> None:
    """Cluster authority follows the elected store, not the binding owner or a lesser."""
    book = _make_spellbook(dynamic=True, disposal=True)
    spell_id = book.bind(spell=PurgeResource, existence=Existence.unique_per_conduit_cluster, permissions="create")
    owner = book.conjure(dynamic=True, name="binding-owner")
    leader = Spellbook(aetheric_frame=owner._aetheric_frame_name).conjure(dynamic=True, name="leader")
    lesser = leader.create_lesser_conduit()
    try:
        owner.link(leader)
        cloud = owner.get_conduit_cloud()
        cloud.create_cluster("purge-cluster")
        cloud.add_conduit_to_cluster(owner, "purge-cluster")
        cloud.add_conduit_to_cluster(leader, "purge-cluster")
        cloud.refresh_cluster_shares_for_conduit(owner)
        cloud.get_cluster("purge-cluster").elect_leader(leader.id)
        obj = owner.meld(spell_id=spell_id)
        assert lesser.meld(spell_id=spell_id) is obj
        with pytest.raises(RuntimeError, match="leader"):
            owner.purge(spell_id=spell_id)
        with pytest.raises(RuntimeError, match="leader"):
            lesser.purge(spell_id=spell_id)
        assert obj.cleanup_calls == 0
        assert leader.purge(spell_id=spell_id) == 1
        assert obj.cleanup_calls == 1
        replacement = owner.meld(spell_id=spell_id)
        assert replacement is not obj
        assert leader.meld(spell_id=spell_id) is replacement
    finally:
        lesser.cleanup()
        leader.permanent_cleanup()
        owner.permanent_cleanup()


def test_borrower_cannot_purge_an_owners_unique_creation() -> None:
    """Visibility through a contract never confers unique creation ownership."""
    book = _make_spellbook(dynamic=True, disposal=True)
    spell_id = book.bind(spell=PurgeResource, existence=Existence.unique, permissions="create")
    owner = book.conjure(dynamic=True, name="unique-owner")
    borrower = Spellbook(aetheric_frame=owner._aetheric_frame_name).conjure(dynamic=True, name="borrower")
    try:
        owner.link(borrower)
        borrower.add_spell_to_contract(spell_id=spell_id, conduit=owner, permissions="create")
        obj = borrower.meld(spell_id=spell_id)
        with pytest.raises(RuntimeError, match="spell-owning"):
            borrower.purge(spell_id=spell_id)
        assert obj.cleanup_calls == 0
        assert owner.purge(spell_id=spell_id) == 1
        assert obj.cleanup_calls == 1
    finally:
        borrower.permanent_cleanup()
        owner.permanent_cleanup()


@pytest.mark.parametrize("spellspace", [False, True])
def test_singleton_instance_purge_is_deferred(spellspace: bool) -> None:
    """Reference-targeting is deferred for singleton scopes too, without touching their entry."""
    book = _make_spellbook(disposal=True)
    existence = Existence.unique_per_spell_space if spellspace else Existence.unique
    spell_id = book.bind(spell=PurgeResource, existence=existence, permissions="create")
    root = book.conjure(name="exact-root")
    space = root.create_spellspace()
    caller = space if spellspace else root
    try:
        obj = caller.meld(spell_id=spell_id)
        with pytest.raises(NotImplementedError, match="purge_all=False"):
            caller.purge(obj, purge_all=False)
        assert obj.cleanup_calls == 0
        assert caller.purge(spell_id=spell_id) == 1
        assert obj.cleanup_calls == 1
    finally:
        space.cleanup()
        root.permanent_cleanup()


def test_purge_selector_errors_do_not_mutate_the_live_store() -> None:
    """Invalid/deferred inputs fail before retirement; normal type lookup selects the binding."""
    book = _make_spellbook(disposal=True)
    spell_id = book.bind(spell=PurgeResource, existence=Existence.many, permissions="create")
    root = book.conjure(name="errors-root")
    try:
        first = root.meld(spell_id=spell_id)
        second = root.meld(spell_id=spell_id)
        with pytest.raises(ValueError):
            root.purge()
        with pytest.raises(ValueError):
            root.purge(PurgeResource, spell_id=spell_id)
        with pytest.raises(NotImplementedError, match="purge_all=False"):
            root.purge(PurgeResource, purge_all=False)
        with pytest.raises(TypeError, match="bool"):
            root.purge(first, purge_all=1)
        with pytest.raises(KeyError):
            root.purge("not-registered")
        assert first.cleanup_calls == second.cleanup_calls == 0
        assert root.purge(PurgeResource) == 2
        assert first.cleanup_calls == second.cleanup_calls == 1
    finally:
        root.permanent_cleanup()


@pytest.mark.parametrize("existence", [Existence.unique, Existence.many])
def test_concurrent_purges_detach_each_creation_once(existence: Existence) -> None:
    """Competing callers serialize retirement and cannot both dispose the same detached entries."""
    book = _make_spellbook(disposal=True)
    spell_id = book.bind(spell=PurgeResource, existence=existence, permissions="create")
    root = book.conjure(name="competing-purge-root")
    try:
        first = root.meld(spell_id=spell_id)
        second = root.meld(spell_id=spell_id)
        expected = 2 if existence is Existence.many else 1
        with ThreadPoolExecutor(max_workers=2) as workers:
            futures = [workers.submit(root.purge, spell_id=spell_id) for _ in range(2)]
            assert sorted(future.result(timeout=5) for future in futures) == [0, expected]
        assert first.cleanup_calls == second.cleanup_calls == 1
    finally:
        root.permanent_cleanup()
