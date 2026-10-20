"""
Component tests: a direct `Spell.cleanup()` against Book teardown, conjure and a second direct cleanup, and
`Spellbook.cleanup_and_remove_spell` against a Book torn down while it waits (direct_spell_cleanup_lock_order,
0.2.8233).

- A direct `Spell.cleanup()` of a live spell held the spell lock while `cleanup_and_remove_spell` took the Book lock,
  frame locks and the Nexus record. Book teardown (`Spellbook._cleanup_spells`, reached from root and frame teardown)
  and conjure's ownership stamping (`define_conduit_into_spells`) take the spell lock under the Book lock, so the two
  hung each other. The removal now runs outside the spell lock, serialized per spell by its removal lock.
- `cleanup_and_remove_spell` checked the Book before taking its lock and read the id maps under it, so a call that
  waited while the Book was torn down failed with AttributeError. It now re-checks under the lock.

Each interleaving parks the removing thread in the Book's own cleaned check, the first thing
`cleanup_and_remove_spell` runs - after the real check, so nothing is skipped - and drives the other operation through
its public call. Where the old lock order would hang, the test reads whether the parked thread holds the spell lock
first and fails there without starting the other operation, so a regression fails instead of hanging the run.
"""

import threading
from typing import Callable, Dict, Iterator, List, Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spellbook import Spellbook

from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


class _Doomed:
    """Spell removed by the direct cleanup under test."""


class _Keeper:
    """Spell that stays bound beside the removed one and must still resolve."""


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_direct_spell_cleanup() -> Iterator[None]:
    """
    Purpose:
        Give each test a clean Aether singleton and frame registry.
    Returns:
        Iterator[None]: Control returns to the test between the two resets.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_book() -> Spellbook:
    """
    Purpose:
        A Spellbook in the dynamic posture, with one phase worker.
    Returns:
        Spellbook: The new Book.
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=configuration)


def _bind(book: Spellbook, spell: type, name: str) -> str:
    """
    Purpose:
        Bind one class as a unique, creatable spell.
    Returns:
        str: The spell id.
    """
    return book.bind(spell=spell, existence=Existence.unique, permissions="create", binding_name=name)


def _run_on_other_thread(work: Callable[[], None]) -> None:
    """
    Purpose:
        Run `work` to completion on another thread and fail the test if it does not finish or raises.
    Raises:
        AssertionError: When the work did not finish within 30 seconds, or raised.
    """
    outcome: Dict[str, BaseException] = {}

    def run() -> None:
        try:
            work()
        except BaseException as exc:
            outcome["error"] = exc

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    thread.join(timeout=30)
    assert not thread.is_alive(), "the concurrent operation never finished"
    assert "error" not in outcome, outcome.get("error")


class _ParkedRemoval:
    """
    A removal running on a daemon thread, parked in the Book's cleaned check - the first statement of
    `Spellbook.cleanup_and_remove_spell` - with what it held there recorded.

    Attributes:
        spell_lock_held (bool): Whether the parked thread held the spell's lock at the parking point.
    """

    def __init__(
            self,
            monkeypatch: pytest.MonkeyPatch,
            book: Spellbook,
            spell: Spell,
            removal: Callable[[], None],
    ) -> None:
        """
        Purpose:
            Patch the Book's cleaned check to park the removing thread right after the real check passes, start
            `removal` on a daemon thread, and wait until it is parked.
        Args:
            monkeypatch (pytest.MonkeyPatch): Restores the patched check after the test.
            book (Spellbook): The Book whose check parks the removal.
            spell (Spell): The spell whose lock ownership is recorded at the parking point.
            removal (Callable[[], None]): The removal to run (a direct `Spell.cleanup()` or a Book call).
        Raises:
            AssertionError: When the removal does not reach the parking point within 30 seconds.
        """
        self._parked = threading.Event()
        self._release = threading.Event()
        self._outcome: Dict[str, BaseException] = {}
        self._thread: Optional[threading.Thread] = None
        self.spell_lock_held = False
        real_check_cleaned = Spellbook.check_cleaned

        def parking(target: Spellbook) -> None:
            real_check_cleaned(target)
            if target is book and threading.current_thread() is self._thread and not self._parked.is_set():
                self.spell_lock_held = spell._lock._is_owned()
                self._parked.set()
                assert self._release.wait(timeout=30)

        monkeypatch.setattr(Spellbook, "check_cleaned", parking)

        def run() -> None:
            try:
                removal()
            except BaseException as exc:
                self._outcome["error"] = exc

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()
        assert self._parked.wait(timeout=30), "the removal never reached the Book"

    def finish(self) -> Dict[str, BaseException]:
        """
        Purpose:
            Release the parked removal and wait for it.
        Returns:
            Dict[str, BaseException]: {"error": exc} when the removal raised, else {}.
        Raises:
            AssertionError: When the removal does not finish within 30 seconds.
        """
        self._release.set()
        self._thread.join(timeout=30)
        assert not self._thread.is_alive(), "the removal never finished"
        return self._outcome


def _fail_if_the_spell_lock_is_held(parked: _ParkedRemoval, what: str) -> None:
    """
    Purpose:
        Fail the test - after letting the parked removal finish alone - when it held the spell lock at its Book call,
        before `what` is started against it, because that operation would then hang on the old lock order.
    Raises:
        pytest.fail.Exception: When the spell lock was held.
    """
    if parked.spell_lock_held:
        parked.finish()
        pytest.fail(f"a direct Spell.cleanup() holds the spell lock at its Book call; {what} would hang against it")


def test_direct_spell_cleanup_reaches_its_book_with_the_spell_lock_free(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    A direct `Spell.cleanup()` of a live spell calls into its Book without holding the spell's lock, and the removal
    then completes: the spell is cleaned and the Book no longer finds it. Before 0.2.8233 the spell lock was held
    across the whole removal.
    """
    book = _make_book()
    spell_id = _bind(book, _Doomed, "doomed")
    book.conjure(dynamic=True, name="owner")
    spell = book.find_spell_by_spell_id(spell_id)

    parked = _ParkedRemoval(monkeypatch, book, spell, spell.cleanup)
    held = parked.spell_lock_held
    outcome = parked.finish()

    assert held is False
    assert "error" not in outcome, outcome.get("error")
    assert spell._cleaned is True
    assert book.find_spell_by_spell_id(spell_id) is None


def test_root_teardown_finishes_while_a_direct_spell_cleanup_waits_for_the_book(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    The owning root is torn down while a direct `Spell.cleanup()` has passed the Book's cleaned check and not yet
    taken the Book lock - the window that hung: the teardown runs to the end and cleans the spell, and the direct call
    then returns without error. Before 0.2.8233 the teardown waited for the spell lock the direct call held while the
    direct call waited for the Book lock the teardown held.
    """
    book = _make_book()
    spell_id = _bind(book, _Doomed, "doomed")
    root = book.conjure(dynamic=True, name="owner")
    spell = book.find_spell_by_spell_id(spell_id)

    parked = _ParkedRemoval(monkeypatch, book, spell, spell.cleanup)
    _fail_if_the_spell_lock_is_held(parked, "a root teardown")

    _run_on_other_thread(root.cleanup)
    assert book._cleaned is True
    assert spell._cleaned is True
    outcome = parked.finish()

    assert "error" not in outcome, outcome.get("error")


def test_conjure_finishes_while_a_direct_spell_cleanup_waits_for_the_book(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    The Book is conjured while a direct `Spell.cleanup()` of one of its spells waits at its Book call: conjure stamps
    ownership into every spell (taking each spell's lock under the Book lock) and finishes, then the direct call
    removes its spell from the conjured Book, and the other spell still melds. Before 0.2.8233 the stamping waited for
    the spell lock the direct call held while the direct call waited for the Book lock.
    """
    book = _make_book()
    doomed_id = _bind(book, _Doomed, "doomed")
    keeper_id = _bind(book, _Keeper, "keeper")
    spell = book.find_spell_by_spell_id(doomed_id)

    parked = _ParkedRemoval(monkeypatch, book, spell, spell.cleanup)
    _fail_if_the_spell_lock_is_held(parked, "a conjure of its Book")

    roots: List[Conduit] = []
    _run_on_other_thread(lambda: roots.append(book.conjure(dynamic=True, name="owner")))
    outcome = parked.finish()

    assert "error" not in outcome, outcome.get("error")
    assert spell._cleaned is True
    assert book.find_spell_by_spell_id(doomed_id) is None
    assert isinstance(roots[0].meld(spell_id=keeper_id), _Keeper)


def test_two_direct_cleanups_of_one_spell_run_the_book_removal_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    A second direct `Spell.cleanup()` started while the first is inside its Book removal waits for it and returns:
    the removal runs once, neither call raises, and the spell ends cleaned and gone from the Book. This held before
    0.2.8233 through the spell lock and holds now through the removal lock. The second call is given a bounded half
    second to show it is not waiting; one that started late would only make this test pass vacuously, never fail.
    """
    book = _make_book()
    spell_id = _bind(book, _Doomed, "doomed")
    book.conjure(dynamic=True, name="owner")
    spell = book.find_spell_by_spell_id(spell_id)
    entries: List[str] = []
    first_inside, release = threading.Event(), threading.Event()
    real_remove = Spellbook.cleanup_and_remove_spell

    def counting(self: Spellbook, target: object) -> None:
        entries.append(threading.current_thread().name)
        if len(entries) == 1:
            first_inside.set()
            assert release.wait(timeout=30)
        return real_remove(self, target)

    monkeypatch.setattr(Spellbook, "cleanup_and_remove_spell", counting)
    outcomes: Dict[str, BaseException] = {}

    def run(label: str) -> None:
        try:
            spell.cleanup()
        except BaseException as exc:
            outcomes[label] = exc

    first = threading.Thread(target=run, args=("first",), name="first", daemon=True)
    second = threading.Thread(target=run, args=("second",), name="second", daemon=True)
    first.start()
    assert first_inside.wait(timeout=30)
    second.start()
    second.join(timeout=0.5)
    entered_while_first_ran = list(entries)
    release.set()
    first.join(timeout=30)
    second.join(timeout=30)

    assert not first.is_alive() and not second.is_alive()
    assert entered_while_first_ran == ["first"]
    assert entries == ["first"]
    assert outcomes == {}
    assert spell._cleaned is True
    assert book.find_spell_by_spell_id(spell_id) is None


def test_cleanup_and_remove_spell_that_waited_through_a_book_teardown_returns_for_the_spell_it_cleaned(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    `cleanup_and_remove_spell(spell)` passes the Book's cleaned check, then the root is torn down before it takes the
    Book lock: the teardown cleaned the spell, so the call returns. Before 0.2.8233 it read the deleted id maps and
    raised AttributeError.
    """
    book = _make_book()
    spell_id = _bind(book, _Doomed, "doomed")
    root = book.conjure(dynamic=True, name="owner")
    spell = book.find_spell_by_spell_id(spell_id)

    parked = _ParkedRemoval(monkeypatch, book, spell, lambda: book.cleanup_and_remove_spell(spell))
    _run_on_other_thread(root.cleanup)
    outcome = parked.finish()

    assert "error" not in outcome, outcome.get("error")
    assert spell._cleaned is True


def test_cleanup_and_remove_spell_by_id_that_waited_through_a_book_teardown_raises_the_cleaned_error(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    `cleanup_and_remove_spell(spell_id)` passes the Book's cleaned check, then the root is torn down before it takes
    the Book lock: an id names no Spell the teardown can be seen to have cleaned, so the call raises the cleaned-Book
    RuntimeError a call made after the teardown raises. Before 0.2.8233 it raised AttributeError.
    """
    book = _make_book()
    spell_id = _bind(book, _Doomed, "doomed")
    root = book.conjure(dynamic=True, name="owner")
    spell = book.find_spell_by_spell_id(spell_id)

    parked = _ParkedRemoval(monkeypatch, book, spell, lambda: book.cleanup_and_remove_spell(spell_id))
    _run_on_other_thread(root.cleanup)
    outcome = parked.finish()

    assert isinstance(outcome.get("error"), RuntimeError), outcome.get("error")
    assert "Spellbook has already been cleaned" in str(outcome["error"])
