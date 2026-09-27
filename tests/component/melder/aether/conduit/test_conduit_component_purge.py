"""Contracts for scoped purge, native disposal and creation-writer synchronization."""

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from threading import Event, RLock, Thread, get_ident
from types import TracebackType
from typing import Optional, Self

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from tests.component.melder.aether.conduit.test_conduit_component_creations import (
    _make_spellbook,
)


class PurgeResource:
    """
    Purpose:
        Expose creation inputs and disposal count through an application object.
    Contract:
        Owns only an integer marker and counter; cleanup keeps both inspectable.
        No external resource or runtime object is owned by this fixture.
    """

    def __init__(self, marker: int = 0) -> None:
        """
        Purpose: Capture constructor input for recreation/override assertions.
        Args: marker: Plain constructor value, retained unchanged.
        Contract: Each new object starts with zero cleanup calls.
        Returns: None.
        """
        self.marker = marker
        self.cleanup_calls = 0

    def cleanup(self) -> None:
        """
        Purpose: Make every explicit disposal attempt observable.
        Contract: Increment the counter once without clearing assertion state.
        Returns: None.
        """
        self.cleanup_calls += 1


class PurgeOther(PurgeResource):
    """
    Purpose: Represent an unrelated binding beside the purge target.
    Contract: Declare its own cleanup method so binding records disposal.
    """

    def cleanup(self) -> None:
        """
        Purpose: Expose disposal in this class's binding profile.
        Contract: Delegate exactly once to the inherited observable counter.
        Returns: None.
        """
        super().cleanup()


class PurgePlain:
    """
    Purpose: Supply a factory result without a disposal method.
    Contract: Many instances remain untracked; each carries a distinct marker.
    """

    def __init__(self) -> None:
        """
        Purpose: Provide an explicit zero-argument application constructor.
        Contract: Allocate one marker per instance without external resources.
        Returns: None.
        """
        self.marker = object()


@pytest.fixture(autouse=True)
def isolated_purge_world() -> Iterator[None]:
    """
    Purpose: Isolate every purge test from earlier bindings and singleton state.
    Contract: Reset Nexus/Aether and rebind test class references before and after use.
    Yields: None while the test owns its temporary runtime.
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


@pytest.mark.parametrize("dynamic", [False, True])
@pytest.mark.parametrize(
    "existence",
    [
        Existence.unique,
        Existence.unique_per_conduit,
        Existence.unique_per_conduit_lineage,
        Existence.unique_per_spell_space,
        Existence.many,
    ],
)
def test_purge_retires_only_target_and_reuses_the_compiled_context(
    existence: Existence,
    dynamic: bool,
) -> None:
    """
    Purpose: Prove targeted retirement and subsequent reuse of the compiled context.
    Contract: Dispose each target once, preserve another binding, return zero on
        repeat purge, and allow a new instance with fresh constructor overrides.
    Args:
        existence: Storage lifetime under test.
        dynamic: Whether the runtime uses dynamic creation gates.
    Returns: None; assertions fail on wrong-scope removal or context replacement.
    """
    book = _make_spellbook(dynamic=dynamic, disposal=True)
    target_id = book.bind(
        spell=PurgeResource, existence=existence, permissions="create"
    )
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
def test_lesser_purge_preserves_root_and_sibling_creations(
    existence: Existence,
) -> None:
    """
    Purpose: Prove local conduit retirement with a shared Spellbook.
    Contract: Purging one lesser disposes its target only; root/sibling objects survive.
    Args: existence: Many or per-conduit lifetime under test.
    Returns: None.
    """
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


@pytest.mark.parametrize(
    "existence", [Existence.many, Existence.unique_per_spell_space]
)
def test_spellspace_purge_preserves_other_scopes(existence: Existence) -> None:
    """
    Purpose: Protect nested SpellSpace isolation during purge.
    Contract: Inner purge preserves outer/root creations and the active stack;
        ordinary context exit still disposes the remaining local objects.
    Args: existence: Many or per-SpellSpace lifetime under test.
    Returns: None.
    """
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


@pytest.mark.parametrize(
    "existence", [Existence.unique, Existence.unique_per_conduit_lineage]
)
def test_lesser_cannot_use_resolution_root_identity_to_purge(
    existence: Existence,
) -> None:
    """
    Purpose: Separate a lesser's lookup access from root purge authority.
    Contract: Lesser purge raises before disposal; the actual root retires once.
    Args: existence: Unique or lineage lifetime under test.
    Returns: None.
    """
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


@pytest.mark.parametrize(
    "existence",
    [
        Existence.unique,
        Existence.unique_per_conduit,
        Existence.unique_per_conduit_lineage,
        Existence.unique_per_conduit_cluster,
    ],
)
def test_spellspace_never_delegates_purge_to_broader_stores(
    existence: Existence,
) -> None:
    """
    Purpose: Keep SpellSpace authority strictly local.
    Contract: Broader lifetimes are refused even when the space belongs to a root.
    Args: existence: Broader lifetime that this space must not purge.
    Returns: None.
    """
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
    """
    Purpose: Prevent ambient-scope substitution at the conduit purge entry point.
    Contract: Conduit purge refuses; the explicit active space can retire its object.
    Returns: None.
    """
    book = _make_spellbook(disposal=True)
    spell_id = book.bind(
        spell=PurgeResource,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )
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


@pytest.mark.parametrize("selector", ["id", "name", "class", "frame", "instance"])
def test_purge_accepts_normal_meld_selectors(selector: str) -> None:
    """
    Purpose: Preserve normal Meld selector behavior for purge.
    Contract: Each supported selector reaches the same named binding and disposes once.
    Args: selector: Id, logical name, class, frame or instance selector.
    Returns: None.
    """
    book = _make_spellbook(disposal=True)
    spell_id = book.bind(
        spell=PurgeResource,
        existence=Existence.unique,
        permissions="create",
        binding_name="blue",
    )
    root = book.conjure(name="selector-root")
    try:
        obj = root.meld(spell_id=spell_id)
        if selector == "id":
            count = root.purge(spell_id=spell_id)
        elif selector == "name":
            count = root.purge(
                book._spells_by_id[spell_id].spell_name, binding_name="blue"
            )
        elif selector == "class":
            count = root.purge(PurgeResource, binding_name="blue")
        elif selector == "frame":
            count = root.purge(spellframe=PurgeResource, binding_name="blue")
        else:
            count = root.purge(obj, binding_name="blue")
        assert count == 1
        assert obj.cleanup_calls == 1
    finally:
        root.permanent_cleanup()


@pytest.mark.parametrize("value", [None, False, 0, [], [1, 2], {}, {"x": 1}])
def test_native_purge_counts_singleton_values_by_existence(value: object) -> None:
    """
    Purpose: Distinguish singleton presence/multiplicity from application value shape.
    Contract: None, falsey values, lists and dictionaries count as one entry and
        remain unmodified as Python objects after removal.
    Args: value: Application value placed in one singleton slot.
    Returns: None.
    """
    book = _make_spellbook()
    spell_id = book.bind(
        spell=PurgePlain, existence=Existence.unique, permissions="create"
    )
    root = book.conjure(name="value-root")
    try:
        expected = (
            list(value)
            if isinstance(value, list)
            else dict(value)
            if isinstance(value, dict)
            else value
        )
        root._creations.add_creation(spell_id, value)
        assert root._creations.purge(book._spells_by_id[spell_id]) == 1
        assert root._creations.purge(book._spells_by_id[spell_id]) == 0
        assert value == expected
    finally:
        root.permanent_cleanup()


def test_non_disposable_many_has_no_retained_objects_to_purge() -> None:
    """
    Purpose: Preserve untracked many behavior.
    Contract: Purge reports zero; subsequent resolution still constructs a fresh object.
    Returns: None.
    """
    book = _make_spellbook(disposal=True)
    spell_id = book.bind(
        spell=PurgePlain, existence=Existence.many, permissions="create"
    )
    root = book.conjure(name="untracked-root")
    try:
        first = root.meld(spell_id=spell_id)
        assert root.purge(spell_id=spell_id) == 0
        assert root.meld(spell_id=spell_id) is not first
    finally:
        root.permanent_cleanup()


@pytest.mark.parametrize("spellspace", [False, True])
def test_instance_purge_selects_single_or_all_retained_many_entries(
    spellspace: bool,
) -> None:
    """
    Purpose: Exercise the instance shortcut with both retirement modes.
    Contract: False removes only the supplied object; default True removes the
        remaining entries for its binding without disposing the first one twice.
    Args: spellspace: Select the SpellSpace facade instead of the conduit facade.
    Returns: None.
    """
    book = _make_spellbook(disposal=True)
    spell_id = book.bind(
        spell=PurgeResource, existence=Existence.many, permissions="create"
    )
    root = book.conjure(name="single-many-root")
    space = root.create_spellspace()
    try:
        caller = space if spellspace else root
        first = caller.meld(spell_id=spell_id)
        second = caller.meld(spell_id=spell_id)
        third = caller.meld(spell_id=spell_id)
        assert caller.purge(second, purge_all=False) == 1
        assert second.cleanup_calls == 1
        assert first.cleanup_calls == third.cleanup_calls == 0
        assert caller.purge(second, purge_all=False) == 0
        assert caller.purge(first) == 2
        assert first.cleanup_calls == second.cleanup_calls == third.cleanup_calls == 1
        replacement = caller.meld(spell_id=spell_id)
        assert caller.purge(replacement, purge_all=False) == 1
        assert caller.purge(replacement, purge_all=False) == 0
    finally:
        space.cleanup()
        root.permanent_cleanup()
    assert first.cleanup_calls == second.cleanup_calls == third.cleanup_calls == 1
    assert replacement.cleanup_calls == 1


@pytest.mark.parametrize("spellspace", [False, True])
def test_purge_many_preserves_disposal_order_and_aggregates_failures(
    spellspace: bool,
) -> None:
    """
    Purpose: Preserve the existing Creations disposal contract during targeted purge.
    Contract: Many runs newest-first; methods run in order. Failures from multiple
        objects are collected while successful objects still complete. Unrelated
        creations survive, and final cleanup does not repeat target disposal.
    Args: spellspace: Select the local SpellSpace instead of conduit storage.
    Returns: None; both expected failures are captured in one ExceptionGroup.
    """
    events: list[tuple[int, str]] = []

    class OrderedResource:
        """
        Purpose: Record ordered disposal events for one many instance.
        Contract: Marker two fails its first method; marker four fails its second.
            Other markers complete both methods.
        """

        def __init__(self, marker: int = 0) -> None:
            """
            Purpose: Associate disposal events with their creation.
            Args: marker: Value attached to every recorded event.
            Returns: None.
            """
            self.marker = marker

        def first(self) -> None:
            """
            Purpose: Exercise first-method failure without stopping other objects.
            Contract: Record the event before raising for marker two.
            Raises: ValueError when marker is two.
            Returns: None otherwise.
            """
            events.append((self.marker, "first"))
            if self.marker == 2:
                raise ValueError("first disposal failed for marker 2")

        def second(self) -> None:
            """
            Purpose: Reveal whether execution continued after the first method.
            Contract: Record the event before raising for marker four.
            Raises: ValueError when marker is four.
            Returns: None otherwise.
            """
            events.append((self.marker, "second"))
            if self.marker == 4:
                raise ValueError("second disposal failed for marker 4")

    book = _make_spellbook(
        disposal=True, disposal_methods=["first", "second", "cleanup"]
    )
    spell_id = book.bind(
        spell=OrderedResource, existence=Existence.many, permissions="create"
    )
    other_id = book.bind(
        spell=PurgeOther, existence=Existence.many, permissions="create"
    )
    root = book.conjure(name="ordered-root")
    space = root.create_spellspace()
    caller = space if spellspace else root
    try:
        other = caller.meld(spell_id=other_id)
        for marker in (1, 2, 3, 4):
            caller.meld(spell_id=spell_id, override={"marker": marker})
        with pytest.raises(ExceptionGroup) as failure:
            caller.purge(spell_id=spell_id)
        assert len(failure.value.exceptions) == 2
        assert "second disposal failed for marker 4" in str(failure.value.exceptions[0])
        assert "first disposal failed for marker 2" in str(failure.value.exceptions[1])
        assert events == [
            (4, "first"),
            (4, "second"),
            (3, "first"),
            (3, "second"),
            (2, "first"),
            (1, "first"),
            (1, "second"),
        ]
        assert caller.purge(spell_id=spell_id) == 0
        assert other.cleanup_calls == 0
        assert book._spells_by_id[spell_id].disposal_method_names == ["first", "second"]
    finally:
        space.cleanup()
        root.permanent_cleanup()
    assert len(events) == 7
    assert other.cleanup_calls == 1


class ObservedLock:
    """
    Purpose: Observe a real writer lock without replacing its synchronization.
    Contract: Borrow the test's trace list, own one temporary RLock/Event, and
        signal the watched thread before it blocks. Tests restore original locks
        and join workers before discarding this instrumentation.
    """

    def __init__(self, name: str, trace: list[str]) -> None:
        """
        Purpose: Initialize deterministic lock-boundary instrumentation.
        Args: name: Trace label; trace: Borrowed event list owned by the test.
        Contract: No thread is watched until its identity is explicitly assigned.
        Returns: None.
        """
        self.lock = RLock()
        self.name = name
        self.trace = trace
        self.watched_thread: Optional[int] = None
        self.attempted = Event()

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        """
        Purpose: Expose an acquisition attempt before ordinary RLock blocking.
        Args: blocking: RLock blocking policy; timeout: RLock acquisition bound.
        Contract: Record entry only after the real lock is acquired.
        Returns: bool indicating whether acquisition succeeded.
        """
        if get_ident() == self.watched_thread:
            self.attempted.set()
        acquired = self.lock.acquire(blocking, timeout)
        if acquired:
            self.trace.append(self.name + ":enter")
        return acquired

    def release(self) -> None:
        """
        Purpose: Preserve observable exit order at the real lock boundary.
        Contract: Record exit, then release one RLock acquisition.
        Returns: None.
        """
        self.trace.append(self.name + ":exit")
        self.lock.release()

    def __enter__(self) -> Self:
        """
        Purpose: Support the production context-manager locking pattern.
        Contract: Acquire the same underlying RLock.
        Returns: Self after successful acquisition.
        """
        self.acquire()
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """
        Purpose: Release after normal or exceptional protected execution.
        Contract: Never suppress the protected operation's exception.
        Args: exc_type, exc, traceback: Context-manager exception state.
        Returns: None.
        """
        self.release()


@pytest.mark.parametrize("purge_all", [False, True])
@pytest.mark.parametrize("existence", list(Existence))
def test_native_purge_mirrors_creation_lock_family_and_order(
    existence: Existence,
    purge_all: bool,
) -> None:
    """
    Purpose: Verify the writer-lock family for all six lifetimes.
    Contract: Unique acquires Spell then store; the other slotted lifetimes
        acquire the store's slot guard then the store lock (the build lock
        their creation holds since 2026-09-25); many acquires only the store
        lock. Restore original locks before runtime teardown.
    Args:
        existence: Lifetime determining the native retirement lock family.
        purge_all: Select whole-target or single-object retirement.
    Returns: None.
    """
    book = _make_spellbook(dynamic=True)
    spell_id = book.bind(spell=PurgeResource, existence=existence, permissions="create")
    root = book.conjure(dynamic=True, name="lock-root")
    spell = book._spells_by_id[spell_id]
    store = root._creations
    original_spell_lock, original_store_lock = spell._lock, store._lock
    trace: list[str] = []
    creation = object()
    try:
        if existence is Existence.many:
            store.add_many_creations(spell_id, creation)
        else:
            store.add_creation(spell_id, creation)
        spell._lock = ObservedLock("spell", trace)
        store._lock = ObservedLock("store", trace)
        store._slot_guards[spell_id] = ObservedLock("guard", trace)
        assert store.purge(spell, purge_all=purge_all, creation=creation) == 1
        expected = ["store:enter", "store:exit"]
        if existence is Existence.unique:
            expected = ["spell:enter", *expected, "spell:exit"]
        elif existence is not Existence.many:
            expected = ["guard:enter", *expected, "guard:exit"]
        assert trace == expected
    finally:
        spell._lock, store._lock = original_spell_lock, original_store_lock
        store._slot_guards.pop(spell_id, None)
        root.permanent_cleanup()


@pytest.mark.parametrize(
    "existence",
    [
        Existence.unique,
        Existence.unique_per_conduit,
        Existence.unique_per_conduit_lineage,
        Existence.unique_per_spell_space,
    ],
)
def test_purge_waits_for_the_actual_singleton_constructor_lock(
    existence: Existence,
) -> None:
    """
    Purpose: Exercise purge against a real constructor holding its writer lock.
    Contract: Observe the blocked acquisition, release construction, and verify
        the published object is retired once and can be created again.
    Args: existence: Singleton lifetime selecting the actual writer/store.
    Returns: None; worker failures propagate through their futures.
    """
    entered, finish = Event(), Event()

    class BlockingResource(PurgeResource):
        """
        Purpose: Pause a real generated creation inside its constructor.
        Contract: Borrow test-owned Events; declare disposal directly for binding.
        """

        def __init__(self) -> None:
            """
            Purpose: Hold the creation lock until the test releases construction.
            Contract: Signal entry before waiting; initialize ordinary disposal state.
            Raises: RuntimeError if the bounded release wait expires.
            Returns: None on release.
            """
            super().__init__()
            entered.set()
            if not finish.wait(5):
                raise RuntimeError("Constructor release timed out.")

        def cleanup(self) -> None:
            """
            Purpose: Ensure binding records the disposal used by this race.
            Contract: Increment the inherited cleanup counter once.
            Returns: None.
            """
            super().cleanup()

    book = _make_spellbook(disposal=True)
    spell_id = book.bind(
        spell=BlockingResource, existence=existence, permissions="create"
    )
    root = book.conjure(name="race-root")
    space = root.create_spellspace()
    caller = space if existence is Existence.unique_per_spell_space else root
    store = (
        space._creations
        if existence is Existence.unique_per_spell_space
        else root._creations
    )
    spell = book._spells_by_id[spell_id]
    observed = ObservedLock("writer", [])
    # The constructor's build lock: Spell._lock for unique, otherwise the
    # store's slot guard (since 2026-09-25 the store lock is only a leaf).
    if existence is Existence.unique:
        original_lock = spell._lock
        spell._lock = observed
    else:
        store._slot_guards[spell_id] = observed

    def run_purge() -> int:
        """
        Purpose: Observe the purging worker's real lock attempt.
        Contract: Mark its thread identity before invoking the public purge facade.
        Returns: int removed by that purge.
        """
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
        if existence is Existence.unique:
            spell._lock = original_lock
        else:
            store._slot_guards.pop(spell_id, None)
        space.cleanup()
        root.permanent_cleanup()


def test_disposal_runs_outside_locks_and_keeps_callback_replacement() -> None:
    """
    Purpose: Prove callbacks run after removal locks are released.
    Contract: Another thread can acquire both locks during disposal, and the
        callback's replacement remains live until ordinary final cleanup.
    Returns: None.
    """
    book = _make_spellbook(disposal=True)
    spell_id = book.bind(
        spell=PurgeResource, existence=Existence.unique, permissions="create"
    )
    root = book.conjure(name="callback-root")
    spell = book._spells_by_id[spell_id]
    store = root._creations
    replacement = PurgeResource()
    available = Event()

    class ReplacingResource:
        """
        Purpose: Exercise user disposal that coordinates with another thread.
        Contract: Borrow the test's store/Spell and publish one replacement entry.
        """

        def cleanup(self) -> None:
            """
            Purpose: Check removal-lock release and replacement preservation.
            Contract: Wait boundedly for another thread to acquire the locks,
                then register the replacement under the retired key.
            Raises: AssertionError if a removal lock remains held.
            Returns: None.
            """

            def check_locks() -> None:
                """
                Purpose: Prove both unique writer locks are externally available.
                Contract: Acquire Spell then store and signal only while holding both.
                Returns: None.
                """
                with spell._lock, store._lock:
                    available.set()

            worker = Thread(target=check_locks, daemon=True)
            worker.start()
            assert available.wait(3), "Disposal retained a removal lock."
            worker.join(timeout=3)
            store.add_creation(
                spell_id,
                replacement,
                has_disposal_methods=True,
                disposal_methods=["cleanup"],
            )

    try:
        store.add_creation(
            spell_id,
            ReplacingResource(),
            has_disposal_methods=True,
            disposal_methods=["cleanup"],
        )
        assert root.purge(spell_id=spell_id) == 1
        assert root.meld(spell_id=spell_id) is replacement
        assert replacement.cleanup_calls == 0
    finally:
        root.permanent_cleanup()
    assert replacement.cleanup_calls == 1


def test_cluster_leader_can_purge_a_spell_owned_by_another_member() -> None:
    """
    Purpose: Verify leader authority when another member owns the binding.
    Contract: Owner/lesser refusals preserve the object; the leader disposes once
        and every linked member subsequently observes the same replacement.
    Returns: None.
    """
    book = _make_spellbook(dynamic=True, disposal=True)
    spell_id = book.bind(
        spell=PurgeResource,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    owner = book.conjure(dynamic=True, name="binding-owner")
    leader = Spellbook(aetheric_frame=owner._aetheric_frame_name).conjure(
        dynamic=True, name="leader"
    )
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
    """
    Purpose: Separate borrowed resolution access from unique purge ownership.
    Contract: Borrower refusal leaves the object live; the owner can retire it.
    Returns: None.
    """
    book = _make_spellbook(dynamic=True, disposal=True)
    spell_id = book.bind(
        spell=PurgeResource, existence=Existence.unique, permissions="create"
    )
    owner = book.conjure(dynamic=True, name="unique-owner")
    borrower = Spellbook(aetheric_frame=owner._aetheric_frame_name).conjure(
        dynamic=True, name="borrower"
    )
    try:
        owner.link(borrower)
        borrower.add_spell_to_contract(
            spell_id=spell_id, conduit=owner, permissions="create"
        )
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
def test_singleton_instance_purge_removes_only_the_retained_reference(spellspace: bool) -> None:
    """
    Purpose: Exercise single-object retirement for the singleton storage shape.
    Contract: An unretained reference removes nothing; the retained object disposes
        once, and a later meld can create its replacement.
    Args: spellspace: Choose an explicit space instead of the owning conduit.
    Returns: None.
    """
    book = _make_spellbook(disposal=True)
    existence = Existence.unique_per_spell_space if spellspace else Existence.unique
    spell_id = book.bind(spell=PurgeResource, existence=existence, permissions="create")
    root = book.conjure(name="exact-root")
    space = root.create_spellspace()
    caller = space if spellspace else root
    try:
        obj = caller.meld(spell_id=spell_id)
        assert caller.purge(PurgeResource(), purge_all=False) == 0
        assert obj.cleanup_calls == 0
        assert caller.purge(obj, purge_all=False) == 1
        assert obj.cleanup_calls == 1
        assert caller.purge(obj, purge_all=False) == 0
        assert caller.meld(spell_id=spell_id) is not obj
    finally:
        space.cleanup()
        root.permanent_cleanup()


def test_purge_selector_errors_do_not_mutate_the_live_store() -> None:
    """
    Purpose: Protect live entries from malformed or unsupported purge requests.
    Contract: Missing/conflicting selectors, invalid bools and unspecified single targets
        fail before removal; normal type discovery still retires the full bucket.
    Returns: None.
    """
    book = _make_spellbook(disposal=True)
    spell_id = book.bind(
        spell=PurgeResource, existence=Existence.many, permissions="create"
    )
    root = book.conjure(name="errors-root")
    try:
        first = root.meld(spell_id=spell_id)
        second = root.meld(spell_id=spell_id)
        with pytest.raises(ValueError):
            root.purge()
        with pytest.raises(ValueError):
            root.purge(PurgeResource, spell_id=spell_id)
        with pytest.raises(ValueError, match="instance"):
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
    """
    Purpose: Prevent duplicate retirement under competing purge calls.
    Contract: One caller removes the entry/bucket, the other reports zero, and
        each retained object is disposed exactly once.
    Args: existence: Unique or many storage shape under contention.
    Returns: None; worker failures propagate through their futures.
    """
    book = _make_spellbook(disposal=True)
    spell_id = book.bind(spell=PurgeResource, existence=existence, permissions="create")
    root = book.conjure(name="competing-purge-root")
    try:
        first = root.meld(spell_id=spell_id)
        second = root.meld(spell_id=spell_id)
        expected = 2 if existence is Existence.many else 1
        with ThreadPoolExecutor(max_workers=2) as workers:
            futures = [workers.submit(root.purge, spell_id=spell_id) for _ in range(2)]
            assert sorted(future.result(timeout=5) for future in futures) == [
                0,
                expected,
            ]
        assert first.cleanup_calls == second.cleanup_calls == 1
    finally:
        root.permanent_cleanup()


@pytest.mark.parametrize("spellspace", [False, True])
def test_instance_discovery_inspects_class_and_preserves_other_bindings(
    spellspace: bool,
) -> None:
    """
    Purpose: Prove the shortcut inspects the class before normal spell lookup.
    Contract: An instance's unrelated __name__ cannot redirect its purge target.
        The shortcut disposes the same binding as an explicit class selector.
    Args: spellspace: Select the local space instead of the conduit.
    Returns: None; both scopes are explicitly cleaned.
    """
    book = _make_spellbook(disposal=True)
    target_id = book.bind(spell=PurgeResource, existence=Existence.many)
    other_id = book.bind(spell=PurgeOther, existence=Existence.many)
    root = book.conjure()
    space = root.create_spellspace()
    try:
        caller = space if spellspace else root
        target = caller.meld(spell_id=target_id)
        sibling = caller.meld(spell_id=target_id)
        other = caller.meld(spell_id=other_id)
        target.__name__ = "PurgeOther"
        assert caller.purge(target) == 2
        assert target.cleanup_calls == sibling.cleanup_calls == 1
        assert other.cleanup_calls == 0
    finally:
        space.cleanup()
        root.permanent_cleanup()


@pytest.mark.parametrize("spellspace", [False, True])
def test_instance_purge_uses_the_selected_scope_only(spellspace: bool) -> None:
    """
    Purpose: Keep object-based discovery separate from scope authority.
    Contract: A foreign reference cannot select one local creation, while whole-
        binding purge still targets the caller's local bucket through its class.
    Args: spellspace: Compare two spaces instead of two lesser conduits.
    Returns: None.
    """
    book = _make_spellbook(disposal=True)
    spell_id = book.bind(spell=PurgeResource, existence=Existence.many)
    root = book.conjure()
    left = root.create_spellspace() if spellspace else root.create_lesser_conduit()
    right = root.create_spellspace() if spellspace else root.create_lesser_conduit()
    try:
        original = left.meld(spell_id=spell_id)
        local = right.meld(spell_id=spell_id)
        assert right.purge(original, purge_all=False) == 0
        assert original.cleanup_calls == local.cleanup_calls == 0
        assert right.purge(original) == 1
        assert local.cleanup_calls == 1
        assert original.cleanup_calls == 0
    finally:
        left.cleanup()
        right.cleanup()
        root.permanent_cleanup()


@pytest.mark.parametrize("spellspace", [False, True])
def test_single_many_purge_failure_leaves_other_entries_for_later_disposal(
    spellspace: bool,
) -> None:
    """
    Purpose: Preserve removal and disposal boundaries when one selected object fails.
    Contract: Single purge detaches only that object before its callback; a failure
        does not roll it back or dispose peers. Later full purge cleans the peers.
    Args: spellspace: Select the local space instead of the conduit.
    Returns: None; the expected ExceptionGroup is consumed by the test.
    """
    events: list[int] = []

    class FailingResource:
        """
        Purpose: Record attempts for the selected and surviving many creations.
        Contract: Own no external resources; borrow the test's event list.
        """

        def __init__(self, marker: int = 0) -> None:
            """
            Purpose: Identify this object's disposal event.
            Args: marker: Value recorded during cleanup.
            Contract: Construction performs no disposal or external work.
            Returns: None.
            """
            self.marker = marker

        def cleanup(self) -> None:
            """
            Purpose: Exercise failure after one observable disposal attempt.
            Contract: Record the marker before any error; other markers succeed.
            Raises: ValueError when this is the selected marker two.
            Returns: None otherwise.
            """
            events.append(self.marker)
            if self.marker == 2:
                raise ValueError("single disposal failed")

    book = _make_spellbook(disposal=True)
    spell_id = book.bind(spell=FailingResource, existence=Existence.many)
    root = book.conjure()
    space = root.create_spellspace()
    try:
        caller = space if spellspace else root
        first = caller.meld(spell_id=spell_id, override={"marker": 1})
        failing = caller.meld(spell_id=spell_id, override={"marker": 2})
        caller.meld(spell_id=spell_id, override={"marker": 3})
        with pytest.raises(ExceptionGroup) as failure:
            caller.purge(failing, purge_all=False)
        assert len(failure.value.exceptions) == 1
        assert "single disposal failed" in str(failure.value.exceptions[0])
        assert events == [2]
        assert caller.purge(failing, purge_all=False) == 0
        assert caller.purge(first) == 2
        assert events == [2, 3, 1]
    finally:
        space.cleanup()
        root.permanent_cleanup()
    assert events == [2, 3, 1]


def test_single_many_purge_preserves_sparse_disposal_records() -> None:
    """
    Purpose: Retire a live entry when not every entry has disposal metadata.
    Contract: Removing an undisposable entry does not remove the next object's
        metadata; later single/full purges dispose the correct objects exactly once.
    Returns: None; the native store remains reusable after its last entry is purged.
    """
    book = _make_spellbook()
    spell_id = book.bind(spell=PurgeResource, existence=Existence.many)
    root = book.conjure()
    try:
        spell = book._spells_by_id[spell_id]
        first, second, third = PurgeResource(), PurgeResource(), PurgeResource()
        root._creations.add_many_creations(spell_id, first)
        root._creations.add_many_creations(
            spell_id, second, has_disposal_methods=True, disposal_methods=["cleanup"],
        )
        root._creations.add_many_creations(
            spell_id, third, has_disposal_methods=True, disposal_methods=["cleanup"],
        )
        assert root._creations.purge(spell, purge_all=False, creation=first) == 1
        assert first.cleanup_calls == second.cleanup_calls == third.cleanup_calls == 0
        assert root.purge(second, purge_all=False) == 1
        assert second.cleanup_calls == 1
        assert third.cleanup_calls == 0
        assert root.purge(third) == 1
        assert third.cleanup_calls == 1
        assert root.purge(third) == 0
    finally:
        root.permanent_cleanup()


@pytest.mark.parametrize("spellspace", [False, True])
def test_concurrent_single_many_purges_leave_the_other_instance(spellspace: bool) -> None:
    """
    Purpose: Verify that competing single-object purges retire one entry once.
    Contract: Both calls use the same object; one returns one and the other zero.
        A second many creation remains retained for a later full purge.
    Args: spellspace: Use the explicit space facade instead of the conduit.
    Returns: None; worker errors propagate through their futures.
    """
    book = _make_spellbook(disposal=True)
    spell_id = book.bind(spell=PurgeResource, existence=Existence.many)
    root = book.conjure()
    space = root.create_spellspace()
    try:
        caller = space if spellspace else root
        target = caller.meld(spell_id=spell_id)
        other = caller.meld(spell_id=spell_id)
        with ThreadPoolExecutor(max_workers=2) as workers:
            futures = [workers.submit(caller.purge, target, purge_all=False) for _ in range(2)]
            assert sorted(future.result(timeout=5) for future in futures) == [0, 1]
        assert target.cleanup_calls == 1
        assert other.cleanup_calls == 0
        assert caller.purge(other) == 1
        assert target.cleanup_calls == other.cleanup_calls == 1
    finally:
        space.cleanup()
        root.permanent_cleanup()


@pytest.mark.parametrize("spellspace", [False, True])
@pytest.mark.parametrize("purge_all", [False, True])
def test_instance_shortcut_can_use_explicit_frame_and_binding_selectors(
    spellspace: bool,
    purge_all: bool,
) -> None:
    """
    Purpose: Exercise the explicit address path alongside an instance shortcut.
    Contract: The caller supplies frame/name qualifiers when choosing that binding;
        the same address supports single-object and whole-target removal.
    Args: spellspace: Select the local space; purge_all: Select retirement multiplicity.
    Returns: None.
    """
    book = _make_spellbook(disposal=True)
    spell_id = book.bind(
        spell=PurgeResource, existence=Existence.many,
        spellframe="resources", binding_name="blue",
    )
    root = book.conjure()
    space = root.create_spellspace()
    try:
        caller = space if spellspace else root
        first = caller.meld(spell_id=spell_id)
        second = caller.meld(spell_id=spell_id)
        assert caller.purge(
            first, spellframe="resources", binding_name="blue", purge_all=purge_all,
        ) == (2 if purge_all else 1)
        assert first.cleanup_calls == 1
        assert second.cleanup_calls == (1 if purge_all else 0)
        assert caller.purge(spellframe="resources", binding_name="blue") == (0 if purge_all else 1)
    finally:
        space.cleanup()
        root.permanent_cleanup()


@pytest.mark.parametrize("spellspace", [False, True])
def test_single_instance_purge_does_not_invoke_application_equality(spellspace: bool) -> None:
    """
    Purpose: Keep single removal safe for unhashable objects with custom equality.
    Contract: Discovery uses the class, and removal selects the supplied reference
        without calling application equality or disposing its same-type peer.
    Args: spellspace: Select the local space instead of the conduit.
    Returns: None.
    """
    class ReferenceOnlyResource(PurgeResource):
        """
        Purpose: Refuse comparisons so an accidental equality search fails visibly.
        Contract: Instances are unhashable; disposal remains explicitly discoverable.
        """

        def __eq__(self, other: object) -> bool:
            """
            Purpose: Detect application equality during discovery or retirement.
            Args: other: Any candidate presented by a mistaken value comparison.
            Raises: AssertionError whenever equality is invoked.
            Returns: Never returns normally.
            """
            raise AssertionError("Purge must not call application equality.")

        def cleanup(self) -> None:
            """
            Purpose: Expose disposal in this class's binding profile.
            Contract: Increment the inherited cleanup counter exactly once per call.
            Returns: None.
            """
            super().cleanup()

    book = _make_spellbook(disposal=True)
    spell_id = book.bind(spell=ReferenceOnlyResource, existence=Existence.many)
    root = book.conjure()
    space = root.create_spellspace()
    try:
        caller = space if spellspace else root
        first = caller.meld(spell_id=spell_id)
        second = caller.meld(spell_id=spell_id)
        with pytest.raises(TypeError):
            hash(second)
        assert caller.purge(second, purge_all=False) == 1
        assert second.cleanup_calls == 1
        assert first.cleanup_calls == 0
        assert caller.purge(first) == 1
    finally:
        space.cleanup()
        root.permanent_cleanup()
