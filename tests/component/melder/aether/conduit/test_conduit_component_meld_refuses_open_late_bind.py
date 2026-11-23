"""
Component tests: while a late bind's window is open, a meld on another thread that reaches one of its spells is
refused at once; the binding thread's own melds build.

WHY THIS EXISTS. Story #330 (STORY-2026-11-16-failed_late_bind_is_undone, GitHub #330), the owner's decisions of
2026-11-22 and 2026-11-23, patch failed_late_bind_unwind_2026_11_22 (component_patch_meld_resolution_runtime). A late
bind publishes its spell into the Book maps before its window commits, and the commit may still refuse the window and
undo it. On 0.2.8315 a meld on another thread inside that window compiled the staged spell, or recompiled a consumer
whose new plan resolved it, and built from a spell whose bind had not committed - which the commit then skipped or the
unwind would remove. After the fix such a meld raises MeldExecutionError saying the spell "is being late-bound by
another thread" before it compiles or builds anything from it, and its caller melds again once the bind finishes; the
thread that holds the window melds what it binds as before, so a window can use its own spells.

These are failing-first pins written on 0.2.8315, before the fix: the three refusal tests fail there at their first
assertion of the new behaviour, and the binding thread's own meld passes there and after the fix. Each test runs in a
fresh Aether with its own dynamic frame and creation caching off and asserts through public calls; the second thread
is started and joined inside the window with a bound, and the test asserts that it finished.
"""
import threading
from collections.abc import Iterator
from typing import ClassVar, List, Optional, Protocol

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError


class GoodX:
    """A late-bound spell with no dependencies: its own structural phases always pass."""


class Greeter(Protocol):
    """The contract every greeter is bound under, as a Protocol spellframe."""

    def greet(self) -> str:
        """Return a greeting."""
        ...


class EnglishGreeter:
    """Bound before conjure under Greeter, binding name "english"."""

    def greet(self) -> str:
        """
        Return the English greeting.

        Returns:
            str: "hello".
        """
        return "hello"


class SpanishGreeter:
    """Bound after conjure under Greeter, binding name "spanish", in a window that commits."""

    def greet(self) -> str:
        """
        Return the Spanish greeting.

        Returns:
            str: "hola".
        """
        return "hola"


class FrenchGreeter:
    """Bound after conjure under Greeter, binding name "french", in the window another thread melds into."""

    def greet(self) -> str:
        """
        Return the French greeting.

        Returns:
            str: "bonjour".
        """
        return "bonjour"


class GreeterChoir:
    """A consumer bound before conjure that gathers every spell bound under Greeter."""

    def __init__(self, greeters: list[Greeter]) -> None:
        """
        Keep the gathered greeters.

        Args:
            greeters (list[Greeter]): Every greeter bound under Greeter when the plan was compiled.
        """
        self.greeters = greeters


class LateBindContract:
    """
    The text and the bound these tests rely on, kept on one class rather than at module scope.

    Contract:
        - LATE_BOUND: the words of the meld refusal a thread meets while another thread's late bind is open.
        - JOIN_TIMEOUT_SECONDS: how long a test waits for a thread it started - a bound against a hang, not a timing
          check.
    """

    LATE_BOUND: ClassVar[str] = "is being late-bound by another thread"
    JOIN_TIMEOUT_SECONDS: ClassVar[float] = 30.0


class MeldOnAnotherThread:
    """
    Run one `Conduit.meld` on a thread of its own and keep its outcome for the test's assertions.

    Contract:
        - `run_and_join()` starts the thread and joins it within `LateBindContract.JOIN_TIMEOUT_SECONDS`; it returns
          whether the thread finished, and every caller asserts that it did.
        - Records the object the meld built in `built`, or the meld refusal it raised in `error` - MeldExecutionError
          or SpellbookValidationError, the refusals these tests expect. Any other error escapes the thread, pytest
          reports it as an unhandled thread exception, and both fields stay None.
        - Owns only its thread; the conduit and the target are borrowed.

    Threading:
        `built` and `error` are written by the worker thread before it ends and read only after `run_and_join`
        returned True, so the join orders the write before the read. The thread is a daemon only so that a hang,
        which the test then reports, can never keep the interpreter alive.
    """

    def __init__(self, root: Conduit, target: type) -> None:
        """
        Prepare the thread without starting it.

        Args:
            root (Conduit): The conduit to meld through (borrowed).
            target (type): The class to meld.
        """
        self._root = root
        self._target = target
        self.built: Optional[object] = None
        self.error: Optional[RuntimeError] = None
        self._thread = threading.Thread(target=self._meld, name=f"meld-{target.__name__}", daemon=True)

    def _meld(self) -> None:
        """
        The thread body: meld the target once and record the result or the expected refusal.

        Returns:
            None.
        """
        try:
            self.built = self._root.meld(self._target)
        except (MeldExecutionError, SpellbookValidationError) as error:
            self.error = error

    def run_and_join(self) -> bool:
        """
        Start the thread and wait for it within the bound.

        Returns:
            bool: True when the thread finished within `LateBindContract.JOIN_TIMEOUT_SECONDS`.
        """
        self._thread.start()
        self._thread.join(timeout=LateBindContract.JOIN_TIMEOUT_SECONDS)
        return not self._thread.is_alive()

    def describe(self) -> str:
        """
        Name the outcome for an assertion message.

        Returns:
            str: "built <Type>", "raises <ErrorType>: <first line of its text>" or "no outcome recorded".
        """
        if self.error is not None:
            lines = str(self.error).splitlines()
            return f"raises {type(self.error).__name__}: {lines[0] if lines else ''}"
        if self.built is not None:
            return f"built {type(self.built).__name__}"
        return "no outcome recorded"


@pytest.fixture(autouse=True)
def reset_aether_for_open_late_bind() -> Iterator[None]:
    """
    Purpose:
        Give each test a clean Aether singleton and frame registry.

    Contract:
        - Resets before and after, so no frame, Book or claim leaks between tests.

    Returns:
        Iterator[None]: The generator pytest drives (yields None).
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


def _book(frame_name: str) -> Spellbook:
    """
    Purpose:
        Return a Book on its own frame, settled dynamic with creation caching off, not yet conjured.

    Args:
        frame_name (str): The frame the Book lives on; each test uses its own.

    Returns:
        Spellbook: The Book.
    """
    book = Spellbook(aetheric_frame=frame_name, configuration=SpellbookConfiguration(frame_name).with_defaults())
    book.configure_aether_frame(
        system_state="dynamic",
        disposal=None,
        disposal_method_names=None,
        system_caching_enabled=False,
    )
    return book


def _named(spell_name: str, spell_id: str) -> str:
    """
    Purpose:
        Return how the refusal names the late-bound spell.

    Args:
        spell_name (str): The spell's name.
        spell_id (str): Its spell_id.

    Returns:
        str: "'<Name>' (spell_id <id>)".
    """
    return f"'{spell_name}' (spell_id {spell_id})"


def _greeter_names(choir: GreeterChoir) -> List[str]:
    """
    Purpose:
        Return the class names of the greeters a choir was built with, sorted.

    Args:
        choir (GreeterChoir): A built choir.

    Returns:
        List[str]: The greeters' class names.
    """
    return sorted(type(greeter).__name__ for greeter in choir.greeters)


def test_another_threads_meld_of_a_late_bound_spell_is_refused_until_its_bind_commits() -> None:
    """
    Purpose:
        A meld on another thread of a spell whose late bind has not committed is refused at once; after the commit
        the same meld builds.

    Contract:
        - Inside `with book.transaction("bind")` that binds GoodX, a second thread started and joined there melds
          GoodX and raises MeldExecutionError for GoodX's spell_id, saying "'GoodX' (spell_id <id>) is being
          late-bound by another thread".
        - After the window commits, a meld of GoodX on another thread builds it.
        - On 0.2.8315 the second thread compiled and built GoodX inside the window.

    Returns:
        None.
    """
    book = _book("late-bound-spell")
    root = book.conjure(dynamic=True, name="late-bound-spell-root")
    good_id = Bind.spell_id_inspector(GoodX)
    inside = MeldOnAnotherThread(root, GoodX)

    with book.transaction("bind"):
        assert book.bind(spell=GoodX, existence=Existence.many) == good_id
        finished = inside.run_and_join()

    assert finished, "the meld thread did not finish within the bound"
    assert isinstance(inside.error, MeldExecutionError), inside.describe()
    assert inside.error.spell_id == good_id
    assert f"{_named('GoodX', good_id)} {LateBindContract.LATE_BOUND}" in str(inside.error)

    after = MeldOnAnotherThread(root, GoodX)
    assert after.run_and_join(), "the meld thread did not finish within the bound"
    assert isinstance(after.built, GoodX), after.describe()


def test_another_threads_meld_of_a_consumer_whose_new_plan_resolves_a_late_bound_spell_is_refused() -> None:
    """
    Purpose:
        A meld on another thread of a consumer whose recompiled plan would resolve a spell another thread is
        late-binding is refused before the plan is built; after the commit the consumer builds with it.

    Contract:
        - EnglishGreeter is bound before conjure under the Protocol spellframe Greeter (binding name "english") and
          GreeterChoir(greeters: list[Greeter]) before conjure. A first window, committed, binds SpanishGreeter under
          Greeter, which re-gates GreeterChoir.
        - A second window binds FrenchGreeter under Greeter; a second thread started and joined there melds
          GreeterChoir and raises MeldExecutionError naming FrenchGreeter and saying it "is being late-bound by
          another thread".
        - After the second window commits, GreeterChoir melds with all three greeters.
        - On 0.2.8315 the second thread's meld recompiled the choir inside the window; the assertion message records
          what it returned.

    Returns:
        None.
    """
    book = _book("greeter-choir")
    book.bind(spell=EnglishGreeter, existence=Existence.many, spellframe=Greeter, binding_name="english")
    book.bind(spell=GreeterChoir, existence=Existence.many)
    root = book.conjure(dynamic=True, name="greeter-choir-root")
    book.bind(spell=SpanishGreeter, existence=Existence.many, spellframe=Greeter, binding_name="spanish")
    french_id = Bind.spell_id_inspector(FrenchGreeter)
    inside = MeldOnAnotherThread(root, GreeterChoir)

    with book.transaction("bind"):
        bound = book.bind(spell=FrenchGreeter, existence=Existence.many, spellframe=Greeter, binding_name="french")
        assert bound == french_id
        finished = inside.run_and_join()

    assert finished, "the meld thread did not finish within the bound"
    outcome = inside.describe()
    if isinstance(inside.built, GreeterChoir):
        outcome = f"{outcome} with greeters {_greeter_names(inside.built)}"
    assert isinstance(inside.error, MeldExecutionError), f"the second thread's meld inside the window: {outcome}"
    message = str(inside.error)
    assert LateBindContract.LATE_BOUND in message
    assert "'FrenchGreeter'" in message

    built = root.meld(GreeterChoir)
    assert isinstance(built, GreeterChoir)
    assert _greeter_names(built) == ["EnglishGreeter", "FrenchGreeter", "SpanishGreeter"]


def test_another_threads_meld_is_refused_after_the_binding_thread_melded_the_spell_inside_its_window() -> None:
    """
    Purpose:
        The binding thread's own meld inside its window does not open the spell to other threads: the Book's
        validation flag stays up while the late bind is open, so another thread's meld still reaches the refusal.

    Contract:
        - The Book holds nothing else, so no other risk keeps its validation flag up. Inside `with
          book.transaction("bind")` that binds GoodX, the binding thread melds GoodX first and builds it; that meld
          publishes GoodX's verdicts, which would let the flag drop and the next meld skip the validation lane
          (and the warm door serve it) if the window did not pin the flag.
        - A second thread started and joined inside the window then melds GoodX and raises MeldExecutionError for
          GoodX's spell_id, saying it "is being late-bound by another thread".
        - After the window commits, a meld of GoodX on another thread builds it.
        - On 0.2.8315 the second thread built GoodX inside the window.

    Returns:
        None.
    """
    book = _book("pinned-flag")
    root = book.conjure(dynamic=True, name="pinned-flag-root")
    good_id = Bind.spell_id_inspector(GoodX)
    inside = MeldOnAnotherThread(root, GoodX)

    with book.transaction("bind"):
        assert book.bind(spell=GoodX, existence=Existence.many) == good_id
        assert isinstance(root.meld(GoodX), GoodX)
        finished = inside.run_and_join()

    assert finished, "the meld thread did not finish within the bound"
    assert isinstance(inside.error, MeldExecutionError), inside.describe()
    assert inside.error.spell_id == good_id
    assert f"{_named('GoodX', good_id)} {LateBindContract.LATE_BOUND}" in str(inside.error)

    after = MeldOnAnotherThread(root, GoodX)
    assert after.run_and_join(), "the meld thread did not finish within the bound"
    assert isinstance(after.built, GoodX), after.describe()


def test_binding_threads_own_meld_inside_its_window_builds() -> None:
    """
    Purpose:
        The thread that holds a late bind's window melds the spells it binds, inside the window.

    Contract:
        - Inside `with book.transaction("bind")` that binds GoodX, a meld of GoodX on the same thread builds it.
        - The window commits and GoodX stays bound.
        - Passes on 0.2.8315 as well: the refusal must not reach the binding thread.

    Returns:
        None.
    """
    book = _book("own-meld")
    root = book.conjure(dynamic=True, name="own-meld-root")
    good_id = Bind.spell_id_inspector(GoodX)

    with book.transaction("bind"):
        assert book.bind(spell=GoodX, existence=Existence.many) == good_id
        assert isinstance(root.meld(GoodX), GoodX)

    assert book.find_spell_by_spell_id(good_id) is not None
