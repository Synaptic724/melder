"""
Fair-matrix diagnostics for the Spellbook.find_spell_by_id repairs (melder_1, 2026-10-10).

Ticket: context_compass/tickets/tasks/2026-10-10_investigate_spell_lookup_by_id_race_task.md

Not part of the suite: it runs from scratch `git archive` exports of 3d184cac and of each candidate.

Fair means every party runs on its own thread
    The lookup ("probe") and the change ("writer") each run on a named thread. A Book's `_lock` is replaced by a
    watch that delegates to the real RLock and reports a thread that finds it held before it blocks. So a
    candidate whose lookup holds the Book lock is judged with its writers blocked behind the lookup, as they
    would be in production, instead of deadlocking a writer that runs on the test thread.

Two orchestrations, both ordered by threading.Event handshakes (the waits carry a watchdog timeout only)
    probe paused  - the probe pauses inside the find_spell_by_id walk at one chosen SpellIndex (first touch, or
                    after its probe released the index lock); the writer then runs until it finishes or blocks on
                    a Book lock; the probe is released; both must finish.
    writer paused - the writer pauses inside its own critical section (a notch between its pop and its insert);
                    the probe then runs until it finishes or blocks; the writer is released.
    bind window   - a bind pauses past its earlier Book-lock use (in AethericFrame.claim_lookup, after
                    _add_hooks_to_spell released the lock and before the active-map insert); the probe enters its
                    walk and pauses; the bind is released until it finishes or blocks; then the probe is released.
                    This is the window the reviewer's negative control used: a reader lock alone does not keep
                    bind's insert out of the walk.

What each test asserts
    The lookup contract: a spell that stays registered is found, nothing is raised, and a spell whose lineage
    stays registered somewhere in the Book resolves to an active spell of that lineage, never None. Every test
    also asserts that its interleaving happened (pause reached, change landed), so none passes vacuously.
"""

import threading
from typing import Any, Callable, Dict, Iterator, Optional, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_ward.transfer.transfer_of_ownership import TransferOfOwnership
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import set_frame_system_state_for_spellbook_configuration

WATCHDOG_SECONDS: float = 30.0
PROBE: str = "fair-probe"
WRITER: str = "fair-writer"


class Visited:
    """Bound first: the walk reaches its index before the searched spell's."""


class Searched:
    """The spell most lookups search for; never changed by a test."""


class Other:
    """Bound after Searched; removed, notched, transferred or moved by the writer."""


class LateBound:
    """Bound by the writer while the lookup is paused."""


class Filler1:
    """Fourth entry of the five-spell worlds (resize modes)."""


class Filler2:
    """Fifth entry of the five-spell worlds (resize modes)."""


class Staged:
    """Parked into an existing index with bind_inactive, then notched or moved."""


class Resident:
    """The target Book's own spell in the transfer worlds."""


# ---------------------------------------------------------------------------------------------------------------
# Parties, the Book-lock watch and the pauses
# ---------------------------------------------------------------------------------------------------------------

class Party:
    """
    One named thread running one action.

    Contract:
        - `result` / `error` hold the action's outcome; the test asserts on both, so nothing raised is lost.
        - `progress` is set when the thread finishes or when the Book-lock watch reports it blocked.
    """

    def __init__(self, name: str, action: Callable[[], Any]) -> None:
        self.name = name
        self._action = action
        self.result: Any = None
        self.error: Optional[BaseException] = None
        self.finished = threading.Event()
        self.blocked = threading.Event()
        self.progress = threading.Event()
        self._thread = threading.Thread(target=self._run, name=name, daemon=True)

    def _run(self) -> None:
        """Thread body: record the outcome."""
        try:
            self.result = self._action()
        except BaseException as error:  # the exception is the evidence under test
            self.error = error
        finally:
            self.finished.set()
            self.progress.set()

    def note_blocked(self) -> None:
        """Called by the Book-lock watch when this thread finds a Book lock held."""
        self.blocked.set()
        self.progress.set()

    def start(self) -> None:
        """Start the thread."""
        self._thread.start()

    def join(self) -> bool:
        """Wait for the thread (watchdog-bounded); return whether it finished."""
        self._thread.join(WATCHDOG_SECONDS)
        return not self._thread.is_alive()

    def state(self) -> str:
        """'finished' if the action completed, otherwise 'blocked' (only meaningful after `progress`)."""
        return "finished" if self.finished.is_set() else "blocked"


class BookLockWatch:
    """
    Stand-in for a Spellbook's RLock that reports a registered party finding the lock held.

    Contract:
        - Delegates acquire/release to the real RLock, so ownership and reentrancy are the real lock's.
        - A blocking acquire first tries without blocking; if that fails, the calling party (when registered) is
          reported blocked and the acquire then blocks as before.
    """

    def __init__(self, real: Any, parties: Dict[str, Party]) -> None:
        self._real = real
        self._parties = parties

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        """Acquire, reporting a registered party that has to wait."""
        if not blocking:
            return bool(self._real.acquire(False))
        if self._real.acquire(False):
            return True
        party = self._parties.get(threading.current_thread().name)
        if party is not None:
            party.note_blocked()
        return bool(self._real.acquire(True, timeout))

    def release(self) -> None:
        """Release the real lock."""
        self._real.release()

    def __enter__(self) -> "BookLockWatch":
        """Acquire (reporting a wait)."""
        self.acquire()
        return self

    def __exit__(self, *exc_info: Any) -> None:
        """Release; never suppresses an exception."""
        self._real.release()


def watch_books(monkeypatch: pytest.MonkeyPatch, parties: Dict[str, Party], *books: Spellbook) -> None:
    """Replace each Book's `_lock` with a watch (undone after the test)."""
    for book in books:
        monkeypatch.setattr(book, "_lock", BookLockWatch(book._lock, parties))


class _Depth(threading.local):
    """Per-thread nesting depth of a wrapped method."""

    def __init__(self) -> None:
        self.value: int = 0


class Marker:
    """Mark the threads inside one wrapped Spellbook method, so a pause fires only inside that walk."""

    def __init__(self) -> None:
        self._depth = _Depth()

    def inside(self) -> bool:
        """Return whether the calling thread is inside the wrapped method."""
        return self._depth.value > 0

    def install(self, monkeypatch: pytest.MonkeyPatch, method_name: str) -> None:
        """Wrap Spellbook.<method_name>; behaviour is unchanged, only the nesting depth is counted."""
        real = getattr(Spellbook, method_name)
        depth = self._depth

        def wrapped(book: Spellbook, *args: Any, **kwargs: Any) -> Any:
            depth.value += 1
            try:
                return real(book, *args, **kwargs)
            finally:
                depth.value -= 1

        monkeypatch.setattr(Spellbook, method_name, wrapped)


class Pause:
    """
    One-shot pause of one named thread at one chosen object.

    Contract:
        - `hit(obj)` returns at once unless the caller is `thread_name`, `obj` is the chosen object, the optional
          `gate()` holds, and the pause has not fired; then it sets `reached` and waits for `release`.
    """

    def __init__(self, thread_name: str, target: Any, gate: Callable[[], bool]) -> None:
        self.reached = threading.Event()
        self.release = threading.Event()
        self.target = target
        self._thread_name = thread_name
        self._gate = gate
        self._fired = False
        self._fire_lock = threading.Lock()

    def hit(self, obj: Any) -> None:
        """Pause here when this is the chosen thread at the chosen object, once."""
        if threading.current_thread().name != self._thread_name or obj is not self.target or not self._gate():
            return
        with self._fire_lock:
            if self._fired:
                return
            self._fired = True
        self.reached.set()
        if not self.release.wait(WATCHDOG_SECONDS):
            raise AssertionError("the paused party was never released")


class IndexLockProbe:
    """Stand-in for one SpellIndex's RLock that reports lock requests and releases to a Pause."""

    def __init__(self, real: Any, pause: Pause, on_enter: bool, on_exit: bool) -> None:
        self._real = real
        self._pause = pause
        self._on_enter = on_enter
        self._on_exit = on_exit

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        """Report, then acquire the real lock."""
        if self._on_enter:
            self._pause.hit(self._pause.target)
        return bool(self._real.acquire(blocking, timeout))

    def release(self) -> None:
        """Release the real lock, then report."""
        self._real.release()
        if self._on_exit:
            self._pause.hit(self._pause.target)

    def __enter__(self) -> "IndexLockProbe":
        """Report, then acquire the real lock."""
        if self._on_enter:
            self._pause.hit(self._pause.target)
        self._real.acquire()
        return self

    def __exit__(self, *exc_info: Any) -> None:
        """Release the real lock, then report; never suppresses an exception."""
        self._real.release()
        if self._on_exit:
            self._pause.hit(self._pause.target)


def pause_probe_at(
        monkeypatch: pytest.MonkeyPatch,
        index: SpellIndex,
        *,
        where: str,
) -> Pause:
    """
    Pause the probe inside the find_spell_by_id walk at `index`.

    `where` is "first touch" (has_spell called on it or its lock requested, whichever comes first), "lock enter"
    (its lock requested) or "after probe" (its lock released, the probe has its answer).
    """
    marker = Marker()
    marker.install(monkeypatch, "find_spell_by_id")
    pause = Pause(PROBE, index, marker.inside)
    if where == "first touch":
        real_has_spell = SpellIndex.has_spell

        def has_spell(spell_index: SpellIndex, spell_id: str) -> bool:
            pause.hit(spell_index)
            return real_has_spell(spell_index, spell_id)

        monkeypatch.setattr(SpellIndex, "has_spell", has_spell)
    on_enter = where in ("first touch", "lock enter")
    on_exit = where == "after probe"
    monkeypatch.setattr(index, "_lock", IndexLockProbe(index._lock, pause, on_enter, on_exit))
    return pause


def run_probe_paused(probe: Party, writer: Party, pause: Pause) -> str:
    """Probe to the pause, writer until it finishes or blocks, release, join both; return the writer's state."""
    probe.start()
    assert pause.reached.wait(WATCHDOG_SECONDS), "the probe never reached the pause point"
    writer.start()
    assert writer.progress.wait(WATCHDOG_SECONDS), "the writer neither finished nor blocked on a Book lock"
    writer_state = writer.state()
    pause.release.set()
    assert probe.join(), "DEADLOCK: the probe did not finish after release"
    assert writer.join(), "DEADLOCK: the writer did not finish after the probe"
    return writer_state


def run_writer_paused(probe: Party, writer: Party, pause: Pause) -> str:
    """Writer to the pause, probe until it finishes or blocks, release, join both; return the probe's state."""
    writer.start()
    assert pause.reached.wait(WATCHDOG_SECONDS), "the writer never reached the pause point"
    probe.start()
    assert probe.progress.wait(WATCHDOG_SECONDS), "the probe neither finished nor blocked on a Book lock"
    probe_state = probe.state()
    pause.release.set()
    assert writer.join(), "DEADLOCK: the writer did not finish after release"
    assert probe.join(), "DEADLOCK: the probe did not finish after the writer"
    return probe_state


def pause_bind_past_its_earlier_locking(monkeypatch: pytest.MonkeyPatch) -> Pause:
    """Pause the writer's bind in AethericFrame.claim_lookup: past _add_hooks_to_spell, before the insert."""
    pause = Pause(WRITER, WRITER, lambda: True)
    real_claim = AethericFrame.claim_lookup

    def claim_lookup(frame: AethericFrame, *args: Any, **kwargs: Any) -> Any:
        pause.hit(threading.current_thread().name)
        return real_claim(frame, *args, **kwargs)

    monkeypatch.setattr(AethericFrame, "claim_lookup", claim_lookup)
    return pause


def run_bind_window(probe: Party, writer: Party, writer_pause: Pause, probe_pause: Pause) -> str:
    """Bind to its window, probe into its walk, bind on until it finishes or blocks, then the probe; join both."""
    writer.start()
    assert writer_pause.reached.wait(WATCHDOG_SECONDS), "the bind never reached its window"
    probe.start()
    assert probe_pause.reached.wait(WATCHDOG_SECONDS), "the probe never reached its walk"
    writer_pause.release.set()
    assert writer.progress.wait(WATCHDOG_SECONDS), "the bind neither finished nor blocked on a Book lock"
    writer_state = writer.state()
    probe_pause.release.set()
    assert probe.join(), "DEADLOCK: the probe did not finish after release"
    assert writer.join(), "DEADLOCK: the bind did not finish after the probe"
    return writer_state


# ---------------------------------------------------------------------------------------------------------------
# Worlds
# ---------------------------------------------------------------------------------------------------------------

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
    """A Spellbook on a frame posture of `system_state` ("automatic" or "dynamic"), one phase worker."""
    configuration = SpellbookConfiguration()
    set_frame_system_state_for_spellbook_configuration(configuration, system_state)
    configuration.load_default_dictionary()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
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
    """Visited, Searched, Other (and with `five`, Filler1, Filler2) bound in order; optionally a dynamic root."""

    def __init__(self, *, dynamic: bool = False, five: bool = False, root_name: str = "owner") -> None:
        self.book = _book("dynamic" if dynamic else "automatic")
        self.ids: Dict[str, str] = {}
        classes = [Visited, Searched, Other] + ([Filler1, Filler2] if five else [])
        for cls in classes:
            self.ids[cls.__name__] = _bind(self.book, cls)
        self.conduit: Optional[Conduit] = (
            self.book.conjure(name=root_name, dynamic=True) if dynamic else None
        )
        self.spells: Dict[str, Spell] = {name: _live(self.book, sid) for name, sid in self.ids.items()}
        self.index: Dict[str, SpellIndex] = {name: spell.spell_index for name, spell in self.spells.items()}
        assert list(self.book.spells) == [self.index[cls.__name__] for cls in classes]

    def stage_into(self, name: str) -> Spell:
        """Park Staged into `name`'s index with bind_inactive and return the parked spell."""
        assert self.conduit is not None
        staged_id = self.conduit.bind_inactive(
            spell=Staged, spell_index=self.index[name], existence=Existence.many, permissions="create",
        )
        return self.book._inactive_spells[staged_id]

    def close(self) -> None:
        """Tear the root down, if any."""
        if self.conduit is not None:
            self.conduit.permanent_cleanup()


def _assert_found(probe: Party, expected: Spell) -> None:
    """The lookup contract for a spell nobody changed."""
    assert probe.error is None, f"the lookup raised {probe.error!r} for a spell nobody changed"
    assert probe.result is expected, f"the lookup answered {probe.result!r} for a registered spell"


def _parties(probe: Callable[[], Any], writer: Callable[[], Any]) -> Tuple[Party, Party, Dict[str, Party]]:
    """The two parties and the registry the Book-lock watch reports to."""
    p = Party(PROBE, probe)
    w = Party(WRITER, writer)
    return p, w, {PROBE: p, WRITER: w}


# ---------------------------------------------------------------------------------------------------------------
# The original seven, made fair
# ---------------------------------------------------------------------------------------------------------------

def test_a1_bind_during_the_walk(monkeypatch: pytest.MonkeyPatch) -> None:
    """(a1) Another spell is bound while the walk is paused at Visited."""
    world = World()
    probe, writer, parties = _parties(
        lambda: world.book.find_spell_by_id(world.ids["Searched"]), lambda: _bind(world.book, LateBound),
    )
    watch_books(monkeypatch, parties, world.book)
    pause = pause_probe_at(monkeypatch, world.index["Visited"], where="first touch")
    run_probe_paused(probe, writer, pause)
    assert writer.error is None and world.book.find_spell_by_id(writer.result) is not None, "the bind did not land"
    _assert_found(probe, world.spells["Searched"])


def test_a2_removal_during_the_walk(monkeypatch: pytest.MonkeyPatch) -> None:
    """(a2) Another spell is removed while the walk is paused at Visited."""
    world = World()
    probe, writer, parties = _parties(
        lambda: world.book.find_spell_by_id(world.ids["Searched"]),
        lambda: world.book.cleanup_and_remove_spell(world.ids["Other"]),
    )
    watch_books(monkeypatch, parties, world.book)
    pause = pause_probe_at(monkeypatch, world.index["Visited"], where="first touch")
    run_probe_paused(probe, writer, pause)
    assert writer.error is None and world.index["Other"].cleaned, "the removal did not land"
    _assert_found(probe, world.spells["Searched"])


def test_b_cleanup_as_the_probe_requests_the_index_lock(monkeypatch: pytest.MonkeyPatch) -> None:
    """(b) The probed index is removed and cleaned as the probe requests its lock."""
    world = World()
    probe, writer, parties = _parties(
        lambda: world.book.find_spell_by_id(world.ids["Searched"]),
        lambda: world.book.cleanup_and_remove_spell(world.ids["Visited"]),
    )
    watch_books(monkeypatch, parties, world.book)
    pause = pause_probe_at(monkeypatch, world.index["Visited"], where="lock enter")
    run_probe_paused(probe, writer, pause)
    assert writer.error is None and world.index["Visited"].cleaned, "the removal did not land"
    _assert_found(probe, world.spells["Searched"])


def test_c_cleanup_before_the_probe(monkeypatch: pytest.MonkeyPatch) -> None:
    """(c) The index the walk is about to probe is removed and cleaned first."""
    world = World()
    probe, writer, parties = _parties(
        lambda: world.book.find_spell_by_id(world.ids["Searched"]),
        lambda: world.book.cleanup_and_remove_spell(world.ids["Visited"]),
    )
    watch_books(monkeypatch, parties, world.book)
    pause = pause_probe_at(monkeypatch, world.index["Visited"], where="first touch")
    run_probe_paused(probe, writer, pause)
    assert writer.error is None and world.index["Visited"].cleaned, "the removal did not land"
    _assert_found(probe, world.spells["Searched"])


def test_p_public_lookup_with_a_late_bind_on_a_dynamic_root(monkeypatch: pytest.MonkeyPatch) -> None:
    """(p) Conduit.get_spell_by_id on a dynamic root while another spell is bound there."""
    world = World(dynamic=True)
    try:
        conduit = world.conduit
        assert conduit is not None
        probe, writer, parties = _parties(
            lambda: conduit.get_spell_by_id(world.ids["Searched"]),
            lambda: _bind(world.book, LateBound, binding_name="late"),
        )
        watch_books(monkeypatch, parties, world.book)
        pause = pause_probe_at(monkeypatch, world.index["Visited"], where="first touch")
        run_probe_paused(probe, writer, pause)
        assert writer.error is None and world.book.find_spell_by_id(writer.result) is not None, "no late bind"
        _assert_found(probe, world.spells["Searched"])
    finally:
        world.close()


def test_d_removal_and_bind_resize_during_the_walk(monkeypatch: pytest.MonkeyPatch) -> None:
    """(d) After Visited's probe, Visited is removed and LateBound bound: same size, but the dict resizes."""
    world = World(five=True)

    def remove_then_bind() -> str:
        world.book.cleanup_and_remove_spell(world.ids["Visited"])
        return _bind(world.book, LateBound)

    probe, writer, parties = _parties(lambda: world.book.find_spell_by_id(world.ids["Searched"]), remove_then_bind)
    watch_books(monkeypatch, parties, world.book)
    pause = pause_probe_at(monkeypatch, world.index["Visited"], where="after probe")
    run_probe_paused(probe, writer, pause)
    assert writer.error is None and len(world.book.spells) == 5, "the removal and the bind did not both land"
    _assert_found(probe, world.spells["Searched"])


def test_a3_bind_past_its_earlier_locking_publishes_during_the_walk(monkeypatch: pytest.MonkeyPatch) -> None:
    """(a3) A bind already past _add_hooks_to_spell publishes while the walk is paused at Visited."""
    world = World()
    probe, writer, parties = _parties(
        lambda: world.book.find_spell_by_id(world.ids["Searched"]), lambda: _bind(world.book, LateBound),
    )
    watch_books(monkeypatch, parties, world.book)
    writer_pause = pause_bind_past_its_earlier_locking(monkeypatch)
    probe_pause = pause_probe_at(monkeypatch, world.index["Visited"], where="first touch")
    run_bind_window(probe, writer, writer_pause, probe_pause)
    assert writer.error is None and world.book.find_spell_by_id(writer.result) is not None, "the bind did not land"
    _assert_found(probe, world.spells["Searched"])


def test_self_removal_answers_the_spell_or_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """The SEARCHED spell is removed as the probe requests its lock: None or the spell, never an exception."""
    world = World()
    searched = world.spells["Searched"]
    probe, writer, parties = _parties(
        lambda: world.book.find_spell_by_id(world.ids["Searched"]),
        lambda: world.book.cleanup_and_remove_spell(world.ids["Searched"]),
    )
    watch_books(monkeypatch, parties, world.book)
    pause = pause_probe_at(monkeypatch, world.index["Searched"], where="lock enter")
    run_probe_paused(probe, writer, pause)
    assert writer.error is None and world.index["Searched"].cleaned, "the removal did not land"
    assert probe.error is None, f"the lookup raised {probe.error!r}"
    assert probe.result is None or probe.result is searched


# ---------------------------------------------------------------------------------------------------------------
# Notch, transfer, rollback and membership
# ---------------------------------------------------------------------------------------------------------------

def test_n1_notch_of_another_index_during_the_walk(monkeypatch: pytest.MonkeyPatch) -> None:
    """(n1) Other's index is notched to a staged member while the walk is paused at Visited."""
    world = World(dynamic=True)
    try:
        conduit = world.conduit
        assert conduit is not None
        staged = world.stage_into("Other")
        probe, writer, parties = _parties(
            lambda: world.book.find_spell_by_id(world.ids["Searched"]),
            lambda: conduit.notch_spell(spell_index=world.index["Other"], spell=staged),
        )
        watch_books(monkeypatch, parties, world.book)
        pause = pause_probe_at(monkeypatch, world.index["Visited"], where="first touch")
        run_probe_paused(probe, writer, pause)
        assert writer.error is None and world.book.spells[world.index["Other"]] is staged, "the notch did not land"
        _assert_found(probe, world.spells["Searched"])
    finally:
        world.close()


def test_n2_notch_of_a_visited_index_resizes_the_dict(monkeypatch: pytest.MonkeyPatch) -> None:
    """(n2) After Visited's probe, Visited's index is notched: pop plus insert at the end resizes the dict."""
    world = World(dynamic=True, five=True)
    try:
        conduit = world.conduit
        assert conduit is not None
        staged = world.stage_into("Visited")
        probe, writer, parties = _parties(
            lambda: world.book.find_spell_by_id(world.ids["Searched"]),
            lambda: conduit.notch_spell(spell_index=world.index["Visited"], spell=staged),
        )
        watch_books(monkeypatch, parties, world.book)
        pause = pause_probe_at(monkeypatch, world.index["Visited"], where="after probe")
        run_probe_paused(probe, writer, pause)
        assert writer.error is None and world.book.spells[world.index["Visited"]] is staged, "no notch"
        _assert_found(probe, world.spells["Searched"])
    finally:
        world.close()


def test_g1_lookup_inside_a_notch_between_pop_and_insert(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    (g1) The notch writer pauses between its pop and its insert (inside _apply_notch's Book-lock region); a lookup
    of the notched lineage's outgoing id then runs. The lineage is registered throughout, so the answer must be
    an active spell of it (the outgoing one or the incoming one), never None.
    """
    world = World(dynamic=True)
    try:
        conduit = world.conduit
        assert conduit is not None
        staged = world.stage_into("Other")
        outgoing = world.spells["Other"]
        other_index = world.index["Other"]
        pause = Pause(WRITER, outgoing, lambda: other_index not in world.book._spells)
        real_cleanup_context = Spell._cleanup_creation_context

        def cleanup_creation_context(spell: Spell) -> None:
            pause.hit(spell)
            real_cleanup_context(spell)

        monkeypatch.setattr(Spell, "_cleanup_creation_context", cleanup_creation_context)
        probe, writer, parties = _parties(
            lambda: world.book.find_spell_by_id(world.ids["Other"]),
            lambda: conduit.notch_spell(spell_index=other_index, spell=staged),
        )
        watch_books(monkeypatch, parties, world.book)
        run_writer_paused(probe, writer, pause)
        assert writer.error is None and world.book.spells[other_index] is staged, "the notch did not land"
        assert probe.error is None, f"the lookup raised {probe.error!r}"
        assert probe.result is outgoing or probe.result is staged, (
            f"the lookup answered {probe.result!r} for a lineage registered throughout the notch"
        )
    finally:
        world.close()


def _transfer_worlds(five: bool) -> Tuple[World, Spellbook, Conduit]:
    """The owner world (dynamic root "owner") and a target Book with its own dynamic root "target"."""
    world = World(dynamic=True, five=five, root_name="owner")
    target_book = _book("dynamic")
    _bind(target_book, Resident)
    target = target_book.conjure(name="target", dynamic=True)
    return world, target_book, target


def test_t1_transfer_of_another_spell_during_the_walk(monkeypatch: pytest.MonkeyPatch) -> None:
    """(t1) Other is transferred to another Book while the walk over the owner Book is paused at Visited."""
    world, target_book, target = _transfer_worlds(five=False)
    try:
        conduit = world.conduit
        assert conduit is not None
        probe, writer, parties = _parties(
            lambda: world.book.find_spell_by_id(world.ids["Searched"]),
            lambda: conduit.transfer_spell_ownership(spell=world.ids["Other"], target_conduit=target),
        )
        watch_books(monkeypatch, parties, world.book, target_book)
        pause = pause_probe_at(monkeypatch, world.index["Visited"], where="first touch")
        run_probe_paused(probe, writer, pause)
        assert writer.error is None, f"the transfer failed: {writer.error!r}"
        assert target_book.find_spell_by_id(world.ids["Other"]) is world.spells["Other"], "no transfer"
        _assert_found(probe, world.spells["Searched"])
    finally:
        target.permanent_cleanup()
        world.close()


def test_t2_transfer_with_forced_rollback_resizes_the_dict(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    (t2) After Visited's probe, Visited is transferred and the transfer is forced to fail after its flip: the
    rollback pops it from the target and re-inserts it into the owner at the end, which resizes the owner dict.
    """
    world, target_book, target = _transfer_worlds(five=True)
    try:
        conduit = world.conduit
        assert conduit is not None

        def failing_teardown(transfer: TransferOfOwnership, spell_obj: Any) -> None:
            raise RuntimeError("forced failure after the ownership flip")

        monkeypatch.setattr(TransferOfOwnership, "_teardown_creations", failing_teardown)
        probe, writer, parties = _parties(
            lambda: world.book.find_spell_by_id(world.ids["Searched"]),
            lambda: conduit.transfer_spell_ownership(spell=world.ids["Visited"], target_conduit=target),
        )
        watch_books(monkeypatch, parties, world.book, target_book)
        pause = pause_probe_at(monkeypatch, world.index["Visited"], where="after probe")
        run_probe_paused(probe, writer, pause)
        assert isinstance(writer.error, RuntimeError) and "forced failure" in str(writer.error), (
            f"the transfer did not fail as forced: {writer.error!r}"
        )
        assert world.book.find_spell_by_id(world.ids["Visited"]) is world.spells["Visited"], "no rollback"
        assert target_book.find_spell_by_id(world.ids["Visited"]) is None, "the target kept the spell"
        _assert_found(probe, world.spells["Searched"])
        for book in (world.book, target_book):
            assert book._lock.acquire(True, 5.0), "a Book lock was left held"
            book._lock.release()
    finally:
        target.permanent_cleanup()
        world.close()


def test_m1_membership_move_after_the_probe_passed_the_target_index(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    (m1) A staged member of Other's index is moved into Visited's index after the walk probed Visited. Its id
    is owned by a live index of this Book throughout, so the answer must be Other's or Visited's active spell.
    """
    world = World(dynamic=True)
    try:
        conduit = world.conduit
        assert conduit is not None
        staged = world.stage_into("Other")
        probe, writer, parties = _parties(
            lambda: world.book.find_spell_by_id(staged.spell_id),
            lambda: conduit.add_to_spell_index(spell=staged, target_index=world.index["Visited"]),
        )
        watch_books(monkeypatch, parties, world.book)
        pause = pause_probe_at(monkeypatch, world.index["Visited"], where="after probe")
        run_probe_paused(probe, writer, pause)
        assert writer.error is None and world.index["Visited"].has_spell(staged.spell_id), "the move did not land"
        assert probe.error is None, f"the lookup raised {probe.error!r}"
        assert probe.result is world.spells["Other"] or probe.result is world.spells["Visited"], (
            f"the lookup answered {probe.result!r} for an id a live index owned throughout"
        )
    finally:
        world.close()


# ---------------------------------------------------------------------------------------------------------------
# Callbacks and other Book-locked walkers
# ---------------------------------------------------------------------------------------------------------------

def _foreign_lookup_from_callback(book: Spellbook, spell_id: str, outcome: Dict[str, Any]) -> None:
    """From inside a callback: start a thread that looks `spell_id` up, wait for it (bounded), record."""
    done = threading.Event()

    def lookup() -> None:
        try:
            outcome["result"] = book.find_spell_by_id(spell_id)
        except BaseException as error:
            outcome["error"] = error
        finally:
            done.set()

    threading.Thread(target=lookup, name="foreign-lookup", daemon=True).start()
    outcome["finished_while_waiting"] = done.wait(5.0)
    outcome["done"] = done


def test_h1_post_bind_callback_waits_on_a_foreign_thread_lookup() -> None:
    """(h1) A post-bind registration callback can wait for another thread's lookup of a registered spell."""
    world = World()
    outcome: Dict[str, Any] = {}
    world.book.add_bind_hooks(
        post=[lambda _spell: _foreign_lookup_from_callback(world.book, world.ids["Searched"], outcome)],
    )
    _bind(world.book, LateBound)
    assert outcome["done"].wait(WATCHDOG_SECONDS), "the foreign lookup never finished"
    assert outcome.get("error") is None and outcome.get("result") is world.spells["Searched"]
    assert outcome["finished_while_waiting"], "the foreign lookup could not finish while the callback waited"


def test_h2_conduit_lifecycle_hook_waits_on_a_foreign_thread_lookup() -> None:
    """(h2) A post-created conduit hook (run inside conjure) can wait for another thread's lookup."""
    book = _book("automatic")
    searched_id = _bind(book, Searched)
    outcome: Dict[str, Any] = {}
    book.get_configuration().add_hooks(
        book._id,
        on_conduit_post_created=lambda _conduit: _foreign_lookup_from_callback(book, searched_id, outcome),
    )
    root = book.conjure(name="root")
    try:
        assert outcome["done"].wait(WATCHDOG_SECONDS), "the foreign lookup never finished"
        assert outcome.get("error") is None and outcome.get("result") is not None
        assert outcome["finished_while_waiting"], "the foreign lookup could not finish while the hook waited"
    finally:
        root.cleanup()


def test_l1_book_locked_index_id_walk_survives_a_bind(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    (l1) get_spell_by_index_id walks the map under the Book lock today. A bind already past _add_hooks_to_spell
    publishes while that walk is paused at Visited; the walk must still answer.
    """
    world = World()
    searched_index_id = world.index["Searched"].id
    marker = Marker()
    marker.install(monkeypatch, "_find_spell_index_by_index_id")
    probe_pause = Pause(PROBE, world.index["Visited"], marker.inside)
    real_id = SpellIndex.id

    def index_id(spell_index: SpellIndex) -> str:
        probe_pause.hit(spell_index)
        return real_id.fget(spell_index)

    monkeypatch.setattr(SpellIndex, "id", property(index_id))
    probe, writer, parties = _parties(
        lambda: world.book.get_spell_by_index_id(searched_index_id), lambda: _bind(world.book, LateBound),
    )
    watch_books(monkeypatch, parties, world.book)
    writer_pause = pause_bind_past_its_earlier_locking(monkeypatch)
    run_bind_window(probe, writer, writer_pause, probe_pause)
    assert writer.error is None and world.book.find_spell_by_id(writer.result) is not None, "the bind did not land"
    _assert_found(probe, world.spells["Searched"])
