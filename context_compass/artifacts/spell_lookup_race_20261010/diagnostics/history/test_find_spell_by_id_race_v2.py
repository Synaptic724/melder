"""
Forced-interleaving diagnostics for Spellbook.find_spell_by_id (melder_1, 2026-10-10).

Ticket: context_compass/tickets/tasks/2026-10-10_investigate_spell_lookup_by_id_race_task.md

Not part of the suite. pyproject's `norecursedirs` excludes context_compass/, and these tests run from a
`git archive` export of the commit under test, so no cache or bytecode lands in the repository.

What is forced
    Each test pauses the lookup thread at one exact point with threading.Event handshakes (no sleeps), changes a
    DIFFERENT spell from the test thread, then releases the lookup:

    (a1) a bind inserts into Spellbook._spells while the lookup walks it;
    (a2) a removal pops from Spellbook._spells while the lookup walks it;
    (b)  a removal cleans the index the lookup is probing, between SpellIndex.has_spell's check_cleaned() and its
         lock - the AttributeError of the MelderOps report;
    (c)  a removal cleans the index the lookup is about to probe, before has_spell's check_cleaned();
    (p)  (a1) through the public path MelderOps uses: Conduit.get_spell_by_id on a dynamic root;
    (d)  a removal and a bind that leave the dict's size unchanged but resize it while the walk is between two
         steps: no exception, the walk silently skips the searched spell and the lookup answers None.

    The searched spell is bound before the lookup starts and is never changed, so find_spell_by_id's contract
    (return the owning spell or None; raise only for a cleaned Spellbook) says the lookup returns it. One more
    contract test removes the searched spell itself during the walk: the lookup may then answer None, never raise.

Two kinds of test
    test_contract_*      assert that contract. RED while the defect exists; a repair must turn them green, and
                         they are the proposed regression tests.
    test_characterize_*  pin the failure the commit under test produces (type and message). GREEN while the
                         defect exists; expected to fail once it is repaired.

    Every test also asserts that the interleaving happened (the pause was reached and the mutation finished), so
    no test can pass without exercising the race.
"""

import threading
from typing import Callable, Iterator, List, Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import set_frame_system_state_for_spellbook_configuration


class Visited:
    """Bound first, so the walk reaches its index before the searched spell's index."""


class Searched:
    """The spell every lookup searches for: bound before the lookup starts and never changed by the tests."""


class Other:
    """Bound after the searched spell; removed while the walk is paused at Visited (mode a2)."""


class LateBound:
    """Bound while the walk is paused (modes a1, p and d)."""


class Filler1:
    """Fourth spell of the five-spell world (mode d)."""


class Filler2:
    """Fifth spell of the five-spell world (mode d)."""


class _WalkDepth(threading.local):
    """Per-thread nesting depth of Spellbook.find_spell_by_id."""

    def __init__(self) -> None:
        self.value: int = 0


class WalkMarker:
    """
    Mark the threads that are inside Spellbook.find_spell_by_id, so a pause fires only there.

    Contract:
        - `install` wraps Spellbook.find_spell_by_id on the class (through pytest's monkeypatch, undone after the
          test); the wrapper calls the real method unchanged and only counts the nesting depth per thread.
        - The frame-level lookup in Aether also calls SpellIndex.has_spell, under the frame lock, before
          find_spell_by_id runs. Pausing there would hold that lock across the pause, so pauses are restricted
          to the find_spell_by_id walk.
    """

    def __init__(self) -> None:
        self._depth = _WalkDepth()

    def inside(self) -> bool:
        """Return whether the calling thread is inside Spellbook.find_spell_by_id."""
        return self._depth.value > 0

    def install(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Wrap Spellbook.find_spell_by_id so the walk is recognisable; behaviour is otherwise unchanged."""
        real = Spellbook.find_spell_by_id
        depth = self._depth

        def find_spell_by_id(book: Spellbook, spell_id: str) -> Optional[Spell]:
            depth.value += 1
            try:
                return real(book, spell_id)
            finally:
                depth.value -= 1

        monkeypatch.setattr(Spellbook, "find_spell_by_id", find_spell_by_id)


class PausePoint:
    """
    One-shot pause of the lookup thread, inside the find_spell_by_id walk, at one chosen SpellIndex.

    Contract:
        - `hit(index)` returns at once unless ALL hold: the caller is the probe thread, the probe is inside
          find_spell_by_id, `index` is the chosen index (identity), and the pause has not fired yet.
        - When it fires it sets `reached`, then blocks until the test thread sets `release`.
        - Ordering comes from the two Events only. The waits carry a safety timeout so a broken handshake fails
          the test with a message instead of hanging the run; no wait is used to order anything.
    """

    TIMEOUT_SECONDS: float = 30.0

    def __init__(self, index: SpellIndex, marker: WalkMarker) -> None:
        self.reached = threading.Event()
        self.release = threading.Event()
        self._index = index
        self._marker = marker
        self._fired = False
        self._fire_lock = threading.Lock()

    def hit(self, index: SpellIndex) -> None:
        """Pause here when this is the probe thread's walk reaching the chosen index for the first time."""
        if threading.current_thread().name != LookupProbe.THREAD_NAME:
            return
        if index is not self._index or not self._marker.inside():
            return
        with self._fire_lock:
            if self._fired:
                return
            self._fired = True
        self.reached.set()
        if not self.release.wait(self.TIMEOUT_SECONDS):
            raise AssertionError("the test thread never released the paused lookup")


class LookupProbe:
    """
    Run one lookup on its own named thread and keep its outcome for the test thread.

    Contract:
        - `run` is the lookup; its return value lands in `result` and any exception in `error`. The test thread
          asserts on both, so nothing raised by the lookup is lost.
        - The thread name is how PausePoint recognises the lookup thread.
    """

    THREAD_NAME: str = "find-spell-by-id-probe"

    def __init__(self, run: Callable[[], Optional[Spell]]) -> None:
        self._run = run
        self.result: Optional[Spell] = None
        self.error: Optional[BaseException] = None
        self._thread = threading.Thread(target=self._target, name=self.THREAD_NAME, daemon=True)

    def _target(self) -> None:
        """Thread body: record the lookup's outcome (the exception object is the evidence under test)."""
        try:
            self.result = self._run()
        except BaseException as error:
            self.error = error

    def start(self) -> None:
        """Start the lookup thread."""
        self._thread.start()

    def join(self, timeout: float) -> bool:
        """Wait for the lookup thread; return whether it finished."""
        self._thread.join(timeout)
        return not self._thread.is_alive()


def pause_before_has_spell(monkeypatch: pytest.MonkeyPatch, pause: PausePoint) -> None:
    """Pause the walk as it calls SpellIndex.has_spell on the chosen index, before has_spell runs (a1, a2, c, p)."""
    real = SpellIndex.has_spell

    def has_spell(index: SpellIndex, spell_id: str) -> bool:
        pause.hit(index)
        return real(index, spell_id)

    monkeypatch.setattr(SpellIndex, "has_spell", has_spell)


def pause_after_has_spell(monkeypatch: pytest.MonkeyPatch, pause: PausePoint) -> None:
    """Pause the walk after has_spell answered for the chosen index, before the walk's next step (d)."""
    real = SpellIndex.has_spell

    def has_spell(index: SpellIndex, spell_id: str) -> bool:
        answer = real(index, spell_id)
        pause.hit(index)
        return answer

    monkeypatch.setattr(SpellIndex, "has_spell", has_spell)


def pause_after_check_cleaned(monkeypatch: pytest.MonkeyPatch, pause: PausePoint) -> None:
    """
    Pause inside SpellIndex.has_spell after its check_cleaned() passed and before it takes the index lock (b).

    has_spell is `self.check_cleaned()` then `with self._lock: return spell_id in self._spells_in_index`, so a
    pause at the end of check_cleaned is exactly the gap between the check and the lock.
    """
    real = SpellIndex.check_cleaned

    def check_cleaned(index: SpellIndex) -> None:
        real(index)
        pause.hit(index)

    monkeypatch.setattr(SpellIndex, "check_cleaned", check_cleaned)


def force(probe: LookupProbe, pause: PausePoint, mutate: Callable[[], None]) -> None:
    """Start the lookup, wait for the pause, run `mutate` on this thread, release, and wait for the lookup."""
    probe.start()
    assert pause.reached.wait(PausePoint.TIMEOUT_SECONDS), "the lookup never reached the pause point"
    try:
        mutate()
    finally:
        pause.release.set()
    assert probe.join(PausePoint.TIMEOUT_SECONDS), "the lookup did not finish after it was released"


def _reset_aether() -> None:
    """Install a fresh Aether singleton, as the component conduit tests do."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def fresh_aether() -> Iterator[None]:
    """A fresh Aether for every test."""
    _reset_aether()
    yield
    _reset_aether()


def _book(system_state: str) -> Spellbook:
    """A Spellbook on a frame posture of `system_state` ("automatic" or "dynamic")."""
    configuration = SpellbookConfiguration()
    set_frame_system_state_for_spellbook_configuration(configuration, system_state)
    configuration.load_default_dictionary()
    return Spellbook(configuration=configuration)


def _bind(book: Spellbook, spell: type, binding_name: Optional[str] = None) -> str:
    """Bind `spell` as a `many` spell and return its spell id."""
    return book.bind(spell=spell, binding_name=binding_name, existence=Existence.many, permissions="create")


def _live(book: Spellbook, spell_id: str) -> Spell:
    """Resolve a spell single-threaded (setup and verification only)."""
    spell = book.find_spell_by_id(spell_id)
    assert spell is not None
    return spell


class World:
    """
    An unconjured Spellbook holding Visited, Searched and Other, bound in that order.

    Contract:
        - The walk order of Spellbook._spells is insertion order; the constructor asserts it, so Visited's index
          is the first one every lookup probes.
    """

    def __init__(self) -> None:
        self.book = _book("automatic")
        self.visited_id = _bind(self.book, Visited)
        self.searched_id = _bind(self.book, Searched)
        self.other_id = _bind(self.book, Other)
        self.visited = _live(self.book, self.visited_id)
        self.searched = _live(self.book, self.searched_id)
        self.other = _live(self.book, self.other_id)
        self.visited_index = self.visited.spell_index
        self.searched_index = self.searched.spell_index
        self.other_index = self.other.spell_index
        assert list(self.book.spells) == [self.visited_index, self.searched_index, self.other_index]


class FiveSpellWorld:
    """
    An unconjured Spellbook holding Visited, Searched, Other, Filler1 and Filler2, bound in that order.

    Contract:
        - Five live entries fill a fresh dict's first table (CPython 3.14: 8 slots, two thirds usable), so the
          next insert resizes it, and a resize compacts the entries left of a deleted one. Mode (d) relies on
          that CPython detail; the plain-dict form of the same skip is recorded in runs/dict_skip_probe.log.
    """

    def __init__(self) -> None:
        self.book = _book("automatic")
        self.visited_id = _bind(self.book, Visited)
        self.searched_id = _bind(self.book, Searched)
        for spell in (Other, Filler1, Filler2):
            _bind(self.book, spell)
        self.visited_index = _live(self.book, self.visited_id).spell_index
        self.searched = _live(self.book, self.searched_id)
        assert len(self.book.spells) == 5
        assert list(self.book.spells)[:2] == [self.visited_index, self.searched.spell_index]


class DynamicWorld:
    """
    A dynamic root conduit owning Visited and Searched (bound before conjure, in that order).

    Contract:
        - Mirrors the MelderOps shape: binds after conjure on a dynamic root, lookups through
          Conduit.get_spell_by_id -> Spellbook._get_spell_by_id_via_aether -> Spellbook.find_spell_by_id.
        - `close` tears the root down.
    """

    def __init__(self) -> None:
        self.book = _book("dynamic")
        self.visited_id = _bind(self.book, Visited)
        self.searched_id = _bind(self.book, Searched)
        self.conduit = self.book.conjure(name="root", dynamic=True)
        self.visited_index = _live(self.book, self.visited_id).spell_index
        self.searched = _live(self.book, self.searched_id)
        assert list(self.book.spells) == [self.visited_index, self.searched.spell_index]

    def close(self) -> None:
        """Tear the root conduit down."""
        self.conduit.permanent_cleanup()


def _lookup(world: World) -> LookupProbe:
    """A probe that searches the stable spell in `world`."""
    return LookupProbe(lambda: world.book.find_spell_by_id(world.searched_id))


def _run_a1(monkeypatch: pytest.MonkeyPatch) -> tuple[World, LookupProbe]:
    """(a1) Pause the walk at Visited, bind LateBound, release."""
    world = World()
    marker = WalkMarker()
    marker.install(monkeypatch)
    pause = PausePoint(world.visited_index, marker)
    pause_before_has_spell(monkeypatch, pause)
    late: List[str] = []
    probe = _lookup(world)
    force(probe, pause, lambda: late.append(_bind(world.book, LateBound)))
    assert len(late) == 1 and world.book.find_spell_by_id(late[0]) is not None, "the bind did not land"
    return world, probe


def _run_a2(monkeypatch: pytest.MonkeyPatch) -> tuple[World, LookupProbe]:
    """(a2) Pause the walk at Visited, remove Other, release."""
    world = World()
    marker = WalkMarker()
    marker.install(monkeypatch)
    pause = PausePoint(world.visited_index, marker)
    pause_before_has_spell(monkeypatch, pause)
    probe = _lookup(world)
    force(probe, pause, lambda: world.book.cleanup_and_remove_spell(world.other_id))
    assert world.book.find_spell_by_id(world.other_id) is None and world.other_index.cleaned, "no removal"
    return world, probe


def _run_b(monkeypatch: pytest.MonkeyPatch) -> tuple[World, LookupProbe]:
    """(b) Pause inside has_spell(Visited) between the cleaned check and the lock, remove Visited, release."""
    world = World()
    marker = WalkMarker()
    marker.install(monkeypatch)
    pause = PausePoint(world.visited_index, marker)
    pause_after_check_cleaned(monkeypatch, pause)
    probe = _lookup(world)
    force(probe, pause, lambda: world.book.cleanup_and_remove_spell(world.visited_id))
    assert world.visited_index.cleaned, "the visited index was not cleaned during the pause"
    return world, probe


def _run_c(monkeypatch: pytest.MonkeyPatch) -> tuple[World, LookupProbe]:
    """(c) Pause the walk at Visited before has_spell runs, remove Visited, release."""
    world = World()
    marker = WalkMarker()
    marker.install(monkeypatch)
    pause = PausePoint(world.visited_index, marker)
    pause_before_has_spell(monkeypatch, pause)
    probe = _lookup(world)
    force(probe, pause, lambda: world.book.cleanup_and_remove_spell(world.visited_id))
    assert world.visited_index.cleaned, "the visited index was not cleaned during the pause"
    return world, probe


def _run_p(monkeypatch: pytest.MonkeyPatch) -> tuple[DynamicWorld, LookupProbe]:
    """(p) On a dynamic root, pause Conduit.get_spell_by_id's walk at Visited, bind LateBound, release."""
    world = DynamicWorld()
    marker = WalkMarker()
    marker.install(monkeypatch)
    pause = PausePoint(world.visited_index, marker)
    pause_before_has_spell(monkeypatch, pause)
    late: List[str] = []
    probe = LookupProbe(lambda: world.conduit.get_spell_by_id(world.searched_id))
    force(probe, pause, lambda: late.append(_bind(world.book, LateBound, binding_name="late")))
    assert len(late) == 1 and world.book.find_spell_by_id(late[0]) is not None, "the late bind did not land"
    return world, probe


def _run_d(monkeypatch: pytest.MonkeyPatch) -> tuple[FiveSpellWorld, LookupProbe]:
    """(d) Pause after the walk probed Visited, remove Visited, bind LateBound (a resize), release."""
    world = FiveSpellWorld()
    marker = WalkMarker()
    marker.install(monkeypatch)
    pause = PausePoint(world.visited_index, marker)
    pause_after_has_spell(monkeypatch, pause)
    late: List[str] = []
    probe = LookupProbe(lambda: world.book.find_spell_by_id(world.searched_id))

    def remove_then_bind() -> None:
        world.book.cleanup_and_remove_spell(world.visited_id)
        late.append(_bind(world.book, LateBound))

    force(probe, pause, remove_then_bind)
    assert world.visited_index.cleaned and len(late) == 1, "the removal and the bind did not both land"
    assert len(world.book.spells) == 5, "the walk's dict must end at its starting size for this mode"
    assert world.book.find_spell_by_id(world.searched_id) is world.searched, "the searched spell must stay"
    return world, probe


def _assert_found(probe: LookupProbe, expected: Spell) -> None:
    """The contract: the stable spell is found and nothing is raised."""
    assert probe.error is None, f"the lookup raised {probe.error!r} for a spell nobody changed"
    assert probe.result is expected


def test_contract_lookup_survives_a_bind_during_the_walk(monkeypatch: pytest.MonkeyPatch) -> None:
    """(a1) Binding another spell while the walk is paused must not break the lookup of a stable spell."""
    world, probe = _run_a1(monkeypatch)
    _assert_found(probe, world.searched)


def test_contract_lookup_survives_a_removal_during_the_walk(monkeypatch: pytest.MonkeyPatch) -> None:
    """(a2) Removing another spell while the walk is paused must not break the lookup of a stable spell."""
    world, probe = _run_a2(monkeypatch)
    _assert_found(probe, world.searched)


def test_contract_lookup_survives_cleanup_between_check_and_lock(monkeypatch: pytest.MonkeyPatch) -> None:
    """(b) Cleaning a probed index between has_spell's check and its lock must not break the lookup."""
    world, probe = _run_b(monkeypatch)
    _assert_found(probe, world.searched)


def test_contract_lookup_survives_cleanup_before_the_probe(monkeypatch: pytest.MonkeyPatch) -> None:
    """(c) Cleaning an index the walk is about to probe must not break the lookup."""
    world, probe = _run_c(monkeypatch)
    _assert_found(probe, world.searched)


def test_contract_public_lookup_survives_a_late_bind_on_a_dynamic_root(monkeypatch: pytest.MonkeyPatch) -> None:
    """(p) Conduit.get_spell_by_id must not fail when another spell is bound on the dynamic root mid-walk."""
    world, probe = _run_p(monkeypatch)
    try:
        _assert_found(probe, world.searched)
    finally:
        world.close()


def test_contract_lookup_survives_a_removal_and_a_bind_during_the_walk(monkeypatch: pytest.MonkeyPatch) -> None:
    """(d) A removal plus a bind between two steps of the walk must not hide a stable spell."""
    world, probe = _run_d(monkeypatch)
    _assert_found(probe, world.searched)


def test_contract_lookup_of_a_spell_removed_during_the_walk_answers_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Removing the SEARCHED spell between the probe's check and lock may make the lookup answer None, never raise.

    The removal finished before the probe read the index, so "no local index claims this id" (None) is the
    linearizable answer; returning the spell would also honour the documented contract. Raising does not.
    """
    world = World()
    marker = WalkMarker()
    marker.install(monkeypatch)
    pause = PausePoint(world.searched_index, marker)
    pause_after_check_cleaned(monkeypatch, pause)
    probe = _lookup(world)
    force(probe, pause, lambda: world.book.cleanup_and_remove_spell(world.searched_id))
    assert world.searched_index.cleaned, "the searched index was not cleaned during the pause"
    assert probe.error is None, f"the lookup raised {probe.error!r}"
    assert probe.result is None or probe.result is world.searched


def test_characterize_bind_during_the_walk_raises_dict_size_change(monkeypatch: pytest.MonkeyPatch) -> None:
    """(a1) Today: the walk's next step raises the dict size-change RuntimeError."""
    _world, probe = _run_a1(monkeypatch)
    assert type(probe.error) is RuntimeError
    assert str(probe.error) == "dictionary changed size during iteration"


def test_characterize_removal_during_the_walk_raises_dict_size_change(monkeypatch: pytest.MonkeyPatch) -> None:
    """(a2) Today: the walk's next step raises the dict size-change RuntimeError."""
    _world, probe = _run_a2(monkeypatch)
    assert type(probe.error) is RuntimeError
    assert str(probe.error) == "dictionary changed size during iteration"


def test_characterize_cleanup_between_check_and_lock_raises_attribute_error(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """(b) Today: has_spell reads the member set cleanup deleted - the AttributeError MelderOps reported."""
    _world, probe = _run_b(monkeypatch)
    assert type(probe.error) is AttributeError
    assert "has no attribute '_spells_in_index'" in str(probe.error)


def test_characterize_cleanup_before_the_probe_raises_cleaned_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """(c) Today: has_spell's check_cleaned raises for the index the walk was about to probe."""
    _world, probe = _run_c(monkeypatch)
    assert type(probe.error) is RuntimeError
    assert str(probe.error) == "SpellIndex has already been cleaned. "


def test_characterize_public_lookup_on_a_dynamic_root_raises_dict_size_change(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """(p) Today: the public path fails exactly as the MelderOps traceback shows."""
    world, probe = _run_p(monkeypatch)
    try:
        assert type(probe.error) is RuntimeError
        assert str(probe.error) == "dictionary changed size during iteration"
    finally:
        world.close()


def test_characterize_removal_and_bind_during_the_walk_skip_the_searched_spell(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """(d) Today: no exception at all - the walk skips the searched spell and the lookup answers None."""
    _world, probe = _run_d(monkeypatch)
    assert probe.error is None
    assert probe.result is None
