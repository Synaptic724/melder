"""
Component tests: a late bind refused at its commit is undone, so the Book is as it was before its bind window opened.

WHY THIS EXISTS. Story #330 (STORY-2026-11-16-failed_late_bind_is_undone, GitHub #330), the owner's decisions of
2026-11-22 and 2026-11-23, patch failed_late_bind_unwind_2026_11_22. A late bind - a bind after its Book is conjured -
publishes its spell into the Book maps, the frame registries, SpellSystemStates, the RiskManager and the Nexus record
while it binds; the structural phases (1-4) run when its bind window commits. When that commit refused the window
with SpellbookValidationError, nothing undid the registration on 0.2.8315: the refused spell stayed bound, a retry of
the same bind was refused as "Spell ID collision detected", a good spell bound in the same window stayed with it, and
the consumers that came to rely on the window's spells kept plans over them. After the fix the refused window is
undone in the commit's failure path, before its claims are released: every spell it bound - active binds and
bind_inactive mates - leaves every registry, an existing object leaves its store slot without being disposed, a
managed pool the bind composed is discarded, the consumers that relied on a window spell are flagged for
revalidation, and the refusal keeps its type and text and gains a note naming what was undone. An in-window abort (the
window body raises) unwinds nothing, and the commit also refuses a staged spell the binding thread already compiled
broken inside the window.

These are failing-first pins written on 0.2.8315, before the fix: every test except the in-window abort fails there at
its first assertion of the new behaviour. The refusal trigger is HIDDEN_PROVIDER: `ServiceBuilder` is bound after
conjure only under the spellframe "spectrum", so the class lookup of `BrokenX(service_builder: ServiceBuilder)` reaches
no provider bound bare and the commit of BrokenX's window is refused. Each test runs in a fresh Aether with its own
dynamic frame and creation caching off and asserts through public calls; a thread a test starts is joined inside the
test with a bound, and the test asserts that it finished.
"""
import threading
import traceback
from collections.abc import Iterator
from typing import ClassVar, Dict, List, Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.release_managed_spell import ReleaseManagedSpell
from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError


class ServiceBuilder:
    """
    The provider `BrokenX` asks for by class.

    Contract:
        - Bound after conjure only under the spellframe "spectrum", a class lookup reaches no provider bound bare, so
          the commit of a window that binds BrokenX is refused with HIDDEN_PROVIDER.
        - Bound bare, it satisfies BrokenX.
    """


class BrokenX:
    """A late-bound spell whose commit is refused (HIDDEN_PROVIDER) while ServiceBuilder is bound only under a frame."""

    def __init__(self, service_builder: ServiceBuilder) -> None:
        """
        Keep the injected provider.

        Args:
            service_builder (ServiceBuilder): The provider, injected by class lookup.
        """
        self.service_builder = service_builder


class GoodX:
    """A late-bound spell with no dependencies: its own structural phases always pass."""


class Holder:
    """
    An object bound as an existing-object spell, named with `close` as its disposal method.

    Contract:
        - `closed` starts False and only `close()` sets it True, so a test can tell whether anything closed it.
    """

    def __init__(self) -> None:
        """Start open: `closed` stays False until `close()` runs."""
        self.closed = False

    def close(self) -> None:
        """
        The disposal method: record that it ran.

        Returns:
            None.
        """
        self.closed = True


class Pooled:
    """A class bound with existence managed_spell_quantity: its root store holds a pool for it."""


class Impl:
    """Bound before conjure under the category "impl"; its index takes a staged revision."""


class ImplRevision(Impl):
    """New code staged with bind_inactive onto Impl's index, at Impl's address (spellframe "impl")."""

    revision: ClassVar[int] = 2


class Svc:
    """A provider bound bare inside a refused window."""


class Waiter:
    """A consumer bound before conjure, with no Svc bound yet."""

    def __init__(self, svc: Svc) -> None:
        """
        Keep the injected provider.

        Args:
            svc (Svc): The provider, injected by class lookup.
        """
        self.svc = svc


class Svc2:
    """A provider bound inside a refused window under the spellframe "spectrum2", so a class lookup misses it."""


class Waiter2:
    """A consumer bound before conjure, with no Svc2 bound yet; refused HIDDEN_PROVIDER while Svc2 is framed."""

    def __init__(self, svc2: Svc2) -> None:
        """
        Keep the injected provider.

        Args:
            svc2 (Svc2): The provider, injected by class lookup or by an override.
        """
        self.svc2 = svc2


class WindowAbort(Exception):
    """The error a window body raises to abort its own bind window (an in-window abort)."""


class LateBindContract:
    """
    The texts and the bound these tests rely on, kept on one class rather than at module scope.

    Contract:
        - UNDONE_NOTE: the first words of the note a refused late bind's error gains after the fix.
        - COLLISION: the refusal a retry met on 0.2.8315, which the fix removes.
        - HIDDEN_PROVIDER: the refusal trigger's code as the SpellbookValidationError text shows it.
        - REFUSAL_FIRST_LINE: the first line of BrokenX's refusal, which the unwind must leave unchanged.
        - JOIN_TIMEOUT_SECONDS: how long a test waits for a thread it started - a bound against a hang, not a timing
          check.
    """

    UNDONE_NOTE: ClassVar[str] = "The refused bind window was undone:"
    COLLISION: ClassVar[str] = "Spell ID collision detected"
    HIDDEN_PROVIDER: ClassVar[str] = "[HIDDEN_PROVIDER]"
    REFUSAL_FIRST_LINE: ClassVar[str] = "Spellbook validation failed. Broken spells: BrokenX."
    JOIN_TIMEOUT_SECONDS: ClassVar[float] = 30.0


class MeldOnAnotherThread:
    """
    Run one `Conduit.meld` on a thread of its own and keep its outcome for the test's assertions.

    Contract:
        - `run_and_join()` starts the thread and joins it within `LateBindContract.JOIN_TIMEOUT_SECONDS`; it returns
          whether the thread finished, and every caller asserts that it did.
        - Records the object the meld built in `built`, or the meld refusal it raised in `error` - MeldExecutionError
          (UnresolvedInputError is one) or SpellbookValidationError, the refusals these tests expect. Any other error
          escapes the thread, pytest reports it as an unhandled thread exception, and both fields stay None.
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
def reset_aether_for_failed_late_bind() -> Iterator[None]:
    """
    Purpose:
        Give each test a clean Aether singleton and frame registry.

    Contract:
        - Resets before and after, so no frame, Book, pool or claim leaks between tests.

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


def _conjure_with_hidden_provider(book: Spellbook, name: str) -> Conduit:
    """
    Purpose:
        Conjure `book` dynamic, then bind ServiceBuilder late only under the spellframe "spectrum": the world in which
        a late bind of BrokenX is refused at its commit with HIDDEN_PROVIDER.

    Args:
        book (Spellbook): A Book from `_book`, holding what the test binds before conjure.
        name (str): The root conduit's name.

    Returns:
        Conduit: The root conduit.
    """
    root = book.conjure(dynamic=True, name=name)
    book.bind(spell=ServiceBuilder, existence=Existence.many, spellframe="spectrum", binding_name="ServiceBuilder")
    return root


def _named(spell_name: str, spell_id: str) -> str:
    """
    Purpose:
        Return how the undone note names one removed spell.

    Args:
        spell_name (str): The spell's name.
        spell_id (str): Its spell_id.

    Returns:
        str: "'<Name>' (spell_id <id>)".
    """
    return f"'{spell_name}' (spell_id {spell_id})"


def _undone_note(error: BaseException) -> str:
    """
    Purpose:
        Return a refusal's undone note and everything rendered after it, or "" when it has none.

    Contract:
        - Reads the notes through `traceback.format_exception`, which renders an exception's notes after its
          message, so no note attribute is probed.
        - Starts at the note's first words, so a spell name the message itself mentions never passes for the note's.

    Args:
        error (BaseException): The refusal.

    Returns:
        str: The note onward, or "".
    """
    text = "".join(traceback.format_exception(error))
    start = text.find(LateBindContract.UNDONE_NOTE)
    return text[start:] if start >= 0 else ""


def _refused_spell_ids(error: SpellbookValidationError) -> List[str]:
    """
    Purpose:
        Return the spell_ids of the spells a SpellbookValidationError names, from its public `broken_spells`.

    Contract:
        - A Spell keeps its `spell_id` readable after cleanup, so this reads the same before and after an unwind.

    Args:
        error (SpellbookValidationError): The refusal.

    Returns:
        List[str]: The spell_ids, in the order the error holds the spells.
    """
    return [spell.spell_id for spell in error.broken_spells]


def _meld_outcome(root: Conduit, target: type, override: Optional[Dict[str, object]] = None) -> str:
    """
    Purpose:
        Meld `target` on this thread and name the outcome, so an assertion on it shows what happened instead.

    Contract:
        - Catches only the meld refusals these tests expect: MeldExecutionError (UnresolvedInputError is one) and
          SpellbookValidationError. Anything else propagates.

    Args:
        root (Conduit): The conduit to meld through.
        target (type): The class to meld.
        override (Optional[Dict[str, object]]): An override payload for the meld, or None.

    Returns:
        str: "built <Type>" or "raises <ErrorType>".
    """
    try:
        built = root.meld(target, override=override)
    except (MeldExecutionError, SpellbookValidationError) as error:
        return f"raises {type(error).__name__}"
    return f"built {type(built).__name__}"


def _built_or_raised(root: Conduit, target: type) -> object:
    """
    Purpose:
        Meld `target` on this thread inside an open window and return what it built, or the refusal it raised.

    Contract:
        - Catches only MeldExecutionError and SpellbookValidationError, so the window body goes on and the test
          asserts the outcome; anything else propagates and aborts the window.

    Args:
        root (Conduit): The conduit to meld through.
        target (type): The class to meld.

    Returns:
        object: The built object, or the refusal (a MeldExecutionError or SpellbookValidationError).
    """
    try:
        return root.meld(target)
    except (MeldExecutionError, SpellbookValidationError) as error:
        return error


def test_refused_lone_late_bind_leaves_nothing_registered_and_its_retry_is_refused_again() -> None:
    """
    Purpose:
        A lone late bind refused at its commit is undone: the Book holds nothing under its spell_id, the refusal
        names what was undone, and a retry of the same bind is refused the same way.

    Contract:
        - `bind` raises SpellbookValidationError (HIDDEN_PROVIDER) naming BrokenX, whose spell_id is the one
          `Bind.spell_id_inspector(BrokenX)` computes.
        - Afterwards `find_spell_by_spell_id` answers None for that spell_id.
        - The refusal keeps its text and gains a note that starts "The refused bind window was undone:" and names
          "'BrokenX' (spell_id <id>)".
        - A retry is refused with SpellbookValidationError (HIDDEN_PROVIDER) and undone again - never "Spell ID
          collision detected" - and leaves nothing registered.
        - On 0.2.8315 BrokenX stayed bound and the retry raised the collision.

    Returns:
        None.
    """
    book = _book("lone-refusal")
    _conjure_with_hidden_provider(book, "lone-refusal-root")
    broken_id = Bind.spell_id_inspector(BrokenX)

    with pytest.raises(SpellbookValidationError) as refusal:
        book.bind(spell=BrokenX, existence=Existence.many)

    assert _refused_spell_ids(refusal.value) == [broken_id]
    assert str(refusal.value).splitlines()[0] == LateBindContract.REFUSAL_FIRST_LINE
    assert LateBindContract.HIDDEN_PROVIDER in str(refusal.value)
    assert book.find_spell_by_spell_id(broken_id) is None
    assert _named("BrokenX", broken_id) in _undone_note(refusal.value)

    with pytest.raises(SpellbookValidationError) as retry:
        book.bind(spell=BrokenX, existence=Existence.many)

    assert LateBindContract.COLLISION not in "".join(traceback.format_exception(retry.value))
    assert str(retry.value).splitlines()[0] == LateBindContract.REFUSAL_FIRST_LINE
    assert LateBindContract.HIDDEN_PROVIDER in str(retry.value)
    assert _named("BrokenX", broken_id) in _undone_note(retry.value)
    assert book.find_spell_by_spell_id(broken_id) is None


def test_refused_late_bind_binds_once_its_cause_is_fixed() -> None:
    """
    Purpose:
        After a refused late bind is undone, fixing its cause lets the same bind succeed.

    Contract:
        - The refused BrokenX leaves nothing registered.
        - With the framed ServiceBuilder disposed (`cleanup_spell`) and ServiceBuilder bound bare, a bind of BrokenX
          returns the spell_id `Bind.spell_id_inspector` computes, and a meld builds BrokenX with its ServiceBuilder.
        - On 0.2.8315 the refused BrokenX stayed bound, so the bind after the fix raised the spell-id collision.

    Returns:
        None.
    """
    book = _book("fixed-cause")
    root = _conjure_with_hidden_provider(book, "fixed-cause-root")
    broken_id = Bind.spell_id_inspector(BrokenX)

    with pytest.raises(SpellbookValidationError):
        book.bind(spell=BrokenX, existence=Existence.many)

    assert book.find_spell_by_spell_id(broken_id) is None

    framed = book.find_spell_by_spell_id(Bind.spell_id_inspector(ServiceBuilder))
    assert framed is not None
    root.cleanup_spell(spell=framed)
    book.bind(spell=ServiceBuilder, existence=Existence.many)

    assert book.bind(spell=BrokenX, existence=Existence.many) == broken_id
    built = root.meld(BrokenX)
    assert isinstance(built, BrokenX)
    assert isinstance(built.service_builder, ServiceBuilder)


def test_refused_window_undoes_its_good_mate_which_then_binds_alone_and_melds() -> None:
    """
    Purpose:
        The window is the transaction: a good spell bound in a refused window is undone with the refused one.

    Contract:
        - `with book.transaction("bind")` binding GoodX then BrokenX raises SpellbookValidationError at its exit.
        - Neither spell stays bound, and the note names both.
        - GoodX then binds alone, returning its spell_id, and a meld builds it.
        - On 0.2.8315 both stayed bound.

    Returns:
        None.
    """
    book = _book("good-mate")
    root = _conjure_with_hidden_provider(book, "good-mate-root")
    good_id = Bind.spell_id_inspector(GoodX)
    broken_id = Bind.spell_id_inspector(BrokenX)

    with pytest.raises(SpellbookValidationError) as refusal:
        with book.transaction("bind"):
            assert book.bind(spell=GoodX, existence=Existence.many) == good_id
            book.bind(spell=BrokenX, existence=Existence.many)

    assert _refused_spell_ids(refusal.value) == [broken_id]
    assert book.find_spell_by_spell_id(good_id) is None
    assert book.find_spell_by_spell_id(broken_id) is None
    note = _undone_note(refusal.value)
    assert _named("GoodX", good_id) in note
    assert _named("BrokenX", broken_id) in note

    assert book.bind(spell=GoodX, existence=Existence.many) == good_id
    assert isinstance(root.meld(GoodX), GoodX)


def test_existing_object_in_a_refused_window_leaves_its_store_slot_undisposed_and_binds_again() -> None:
    """
    Purpose:
        An existing object bound in a refused window leaves the Book and its store slot without being disposed, and
        the same object binds again afterwards.

    Contract:
        - The Holder instance is bound with existence unique and `disposal_method_names=["close"]` in the window that
          BrokenX's refusal undoes; its bind files it in the root store at once.
        - After the refused window nothing is registered under the object's spell_id, the note names it, the root
          store holds no object under that spell_id, and `close` never ran.
        - Binding the same instance again returns the same spell_id, and a meld of Holder returns that very object.
        - The store is read through the root's private `_creations.count_spell_creations`: no public call reads a
          slot whose spell is no longer bound, and after the rebind a slot the unwind left behind and a slot the
          rebind filed hold the same object, so no public signal tells them apart.
        - `closed` staying False pins that the unwind does not dispose the caller's object. Bind keeps disposal
          names only for classes, so this object's spell carries none and no Melder disposal path would close it
          on 0.2.8315 (cleanup_spell, root cleanup and the Aether reset all leave it open); the check guards an
          unwind that would run the object's method itself.
        - On 0.2.8315 the object's spell stayed bound, and its slot with it.

    Returns:
        None.
    """
    book = _book("existing-object")
    root = _conjure_with_hidden_provider(book, "existing-object-root")
    holder = Holder()
    holder_id = Bind.spell_id_inspector(holder)

    with pytest.raises(SpellbookValidationError) as refusal:
        with book.transaction("bind"):
            book.bind(spell=holder, existence=Existence.unique, disposal_method_names=["close"])
            book.bind(spell=BrokenX, existence=Existence.many)

    assert book.find_spell_by_spell_id(holder_id) is None
    assert _named("Holder", holder_id) in _undone_note(refusal.value)
    assert root._creations.count_spell_creations(holder_id) == 0
    assert holder.closed is False

    assert book.bind(spell=holder, existence=Existence.unique, disposal_method_names=["close"]) == holder_id
    assert root.meld(Holder) is holder
    assert holder.closed is False


def test_managed_spell_in_a_refused_window_leaves_no_pool_and_binds_again() -> None:
    """
    Purpose:
        A managed spell bound in a refused window leaves no pool behind and binds again afterwards.

    Contract:
        - After the refused window `ReleaseManagedSpell().describe(Pooled)` answers `()` - no live pool manages the
          class - and nothing is registered under its spell_id; the note names it.
        - Binding Pooled again returns its spell_id; `managed_spell_meld` leases a Pooled object, and one pool is
          described.
        - On 0.2.8315 the spell and the pool its bind composed stayed.

    Returns:
        None.
    """
    book = _book("managed-spell")
    root = _conjure_with_hidden_provider(book, "managed-spell-root")
    pooled_id = Bind.spell_id_inspector(Pooled)

    with pytest.raises(SpellbookValidationError) as refusal:
        with book.transaction("bind"):
            book.bind(spell=Pooled, existence=Existence.managed_spell_quantity)
            book.bind(spell=BrokenX, existence=Existence.many)

    assert ReleaseManagedSpell().describe(Pooled) == ()
    assert book.find_spell_by_spell_id(pooled_id) is None
    assert _named("Pooled", pooled_id) in _undone_note(refusal.value)

    assert book.bind(spell=Pooled, existence=Existence.managed_spell_quantity) == pooled_id
    with root.managed_spell_meld(Pooled) as pooled:
        assert isinstance(pooled, Pooled)
    assert len(ReleaseManagedSpell().describe(Pooled)) == 1


def test_bind_inactive_mate_in_a_refused_window_is_removed_and_can_be_staged_again() -> None:
    """
    Purpose:
        A version staged with bind_inactive in a refused window is removed with the window, and the same version can
        be staged onto the index again.

    Contract:
        - Impl is bound before conjure under the category "impl"; ImplRevision is staged onto Impl's index, at
          Impl's address, inside the window that BrokenX's refusal undoes.
        - Afterwards nothing is registered under ImplRevision's spell_id, Impl is still the index's active version,
          and the note names ImplRevision as a parked version: "'ImplRevision' (spell_id <id>, parked)".
        - `bind_inactive` of ImplRevision onto the index again returns its spell_id.
        - On 0.2.8315 the parked version stayed, so staging it again raised the spell-id collision.

    Returns:
        None.
    """
    book = _book("staged-mate")
    book.bind(spell=Impl, existence=Existence.many, spellframe="impl")
    root = _conjure_with_hidden_provider(book, "staged-mate-root")
    impl = book.find_spell_by_spell_id(Bind.spell_id_inspector(Impl))
    assert impl is not None
    index = impl.spell_index
    revision_id = Bind.spell_id_inspector(ImplRevision)

    with pytest.raises(SpellbookValidationError) as refusal:
        with book.transaction("bind"):
            staged = root.bind_inactive(
                spell=ImplRevision, spell_index=index, existence=Existence.many, spellframe="impl",
            )
            assert staged == revision_id
            book.bind(spell=BrokenX, existence=Existence.many)

    assert book.find_spell_by_spell_id(revision_id) is None
    assert index.selected_spell_id == impl.spell_id
    assert f"'ImplRevision' (spell_id {revision_id}, parked)" in _undone_note(refusal.value)

    assert root.bind_inactive(
        spell=ImplRevision, spell_index=index, existence=Existence.many, spellframe="impl",
    ) == revision_id


def test_book_the_unwind_empties_keeps_the_frames_view_of_its_later_spell_ids() -> None:
    """
    Purpose:
        A Book whose only spells a refused window bound is empty after the unwind, and the frame still sees the
        spell_ids it binds afterwards.

    Contract:
        - The Book is conjured with nothing bound; one window binds ServiceBuilder under "spectrum" and BrokenX and
          is refused. The window binds the framed ServiceBuilder itself, so that the unwind leaves the Book empty.
        - Afterwards neither spell is registered; GoodX then binds in the emptied Book.
        - A second Book of the same frame is refused binding GoodX with the spell-id collision - one object is one
          spell - which proves the frame's live view of the first Book's spell_ids survived the unwind.
        - The second Book is never conjured, so the Aether reset does not clean it; the test cleans it itself.
        - On 0.2.8315 the refused window's spells stayed, so the Book was never emptied.

    Returns:
        None.
    """
    frame_name = "emptied-book"
    book = _book(frame_name)
    book.conjure(dynamic=True, name=f"{frame_name}-root")
    framed_id = Bind.spell_id_inspector(ServiceBuilder)
    broken_id = Bind.spell_id_inspector(BrokenX)
    good_id = Bind.spell_id_inspector(GoodX)

    with pytest.raises(SpellbookValidationError):
        with book.transaction("bind"):
            book.bind(
                spell=ServiceBuilder, existence=Existence.many, spellframe="spectrum", binding_name="ServiceBuilder",
            )
            book.bind(spell=BrokenX, existence=Existence.many)

    assert book.find_spell_by_spell_id(framed_id) is None
    assert book.find_spell_by_spell_id(broken_id) is None

    assert book.bind(spell=GoodX, existence=Existence.many) == good_id
    second = Spellbook(aetheric_frame=frame_name)
    try:
        with pytest.raises(RuntimeError, match=LateBindContract.COLLISION):
            second.bind(spell=GoodX, existence=Existence.many)
    finally:
        second.cleanup()


def test_in_window_abort_keeps_its_spells_bound_and_another_thread_melds_them_after_the_window() -> None:
    """
    Purpose:
        Today's contract for an in-window abort, which the fix keeps: a window whose body raises unwinds nothing.

    Contract:
        - `with book.transaction("bind")` that binds GoodX and then raises propagates that error unchanged.
        - GoodX stays bound.
        - After the window a meld of GoodX on another thread builds it; the thread finishes within the bound.
        - Passes on 0.2.8315 as well: it pins the contract, not the fix.

    Returns:
        None.
    """
    book = _book("in-window-abort")
    root = book.conjure(dynamic=True, name="in-window-abort-root")
    good_id = Bind.spell_id_inspector(GoodX)

    with pytest.raises(WindowAbort, match="the window body failed after binding GoodX"):
        with book.transaction("bind"):
            assert book.bind(spell=GoodX, existence=Existence.many) == good_id
            raise WindowAbort("the window body failed after binding GoodX")

    assert book.find_spell_by_spell_id(good_id) is not None
    after = MeldOnAnotherThread(root, GoodX)
    assert after.run_and_join(), "the meld thread did not finish within the bound"
    assert isinstance(after.built, GoodX), after.describe()


def test_consumer_refused_because_of_a_window_spell_is_regated_by_the_unwind() -> None:
    """
    Purpose:
        A consumer refused inside the window because of a window spell is re-gated when the unwind removes that
        spell, so its next meld answers for the Book as it is again.

    Contract:
        - Waiter2(svc2: Svc2) is bound before conjure and never melded. It is re-gated before the window with
          `Spell.invalidate_spell()` (public, on the Spell `find_spell_by_spell_id` returns), standing in for any
          change that re-gates it: a consumer bound before conjure keeps its conjure-time verdict, and without a
          re-gate its meld inside the window answers from that verdict (UnresolvedInputError) instead of compiling
          against the window's spells.
        - The window binds Svc2 under the spellframe "spectrum2" and BrokenX; inside it a second thread melds
          Waiter2 and is refused with SpellbookValidationError (HIDDEN_PROVIDER: Svc2 is bound only under a frame).
          The window's exit is refused.
        - After the unwind Svc2 is gone, so a meld of Waiter2 raises UnresolvedInputError, not the stale
          SpellbookValidationError; with the override {'svc2': Svc2()} it builds.
        - On 0.2.8315 Svc2 stayed framed, so Waiter2 stayed refused with HIDDEN_PROVIDER.

    Returns:
        None.
    """
    book = _book("regated-consumer")
    book.bind(spell=Waiter2, existence=Existence.many)
    root = _conjure_with_hidden_provider(book, "regated-consumer-root")
    waiter2 = book.find_spell_by_spell_id(Bind.spell_id_inspector(Waiter2))
    assert waiter2 is not None
    waiter2.invalidate_spell()
    inside = MeldOnAnotherThread(root, Waiter2)

    with pytest.raises(SpellbookValidationError):
        with book.transaction("bind"):
            book.bind(spell=Svc2, existence=Existence.many, spellframe="spectrum2", binding_name="Svc2")
            book.bind(spell=BrokenX, existence=Existence.many)
            finished = inside.run_and_join()

    assert finished, "the meld thread did not finish within the bound"
    assert isinstance(inside.error, SpellbookValidationError), inside.describe()
    assert LateBindContract.HIDDEN_PROVIDER in str(inside.error)

    assert _meld_outcome(root, Waiter2) == f"raises {UnresolvedInputError.__name__}"
    built = root.meld(Waiter2, override={"svc2": Svc2()})
    assert isinstance(built, Waiter2)
    assert isinstance(built.svc2, Svc2)


def test_consumer_the_binding_thread_compiled_against_a_window_spell_is_flagged_by_the_unwind() -> None:
    """
    Purpose:
        A consumer the binding thread compiled against a window spell, inside the window, is flagged when the unwind
        removes that spell, so it is not built from a plan over a spell that is gone.

    Contract:
        - Waiter(svc: Svc) is bound before conjure with existence many, and re-gated before the window with
          `Spell.invalidate_spell()` for the reason the HIDDEN_PROVIDER consumer test gives: without it Waiter keeps
          its conjure-time verdict and its meld inside the window raises UnresolvedInputError.
        - The window binds Svc bare and BrokenX; inside it the binding thread melds Waiter, which compiles against
          the window's Svc and builds with it. The window's exit is refused.
        - After the unwind Svc is gone, so a meld of Waiter raises UnresolvedInputError instead of building.
        - On 0.2.8315 Svc stayed bound and Waiter kept building.

    Returns:
        None.
    """
    book = _book("flagged-consumer")
    book.bind(spell=Waiter, existence=Existence.many)
    root = _conjure_with_hidden_provider(book, "flagged-consumer-root")
    waiter = book.find_spell_by_spell_id(Bind.spell_id_inspector(Waiter))
    assert waiter is not None
    waiter.invalidate_spell()

    with pytest.raises(SpellbookValidationError):
        with book.transaction("bind"):
            book.bind(spell=Svc, existence=Existence.unique)
            book.bind(spell=BrokenX, existence=Existence.many)
            inside = _built_or_raised(root, Waiter)

    assert isinstance(inside, Waiter), f"the binding thread's meld inside the window: {inside!r}"
    assert isinstance(inside.svc, Svc)

    assert _meld_outcome(root, Waiter) == f"raises {UnresolvedInputError.__name__}"


def test_commit_refuses_a_staged_spell_the_binding_thread_already_compiled_broken() -> None:
    """
    Purpose:
        A staged spell the binding thread compiled broken inside its window is refused by the commit, not committed.

    Contract:
        - Inside a window that binds BrokenX, the binding thread's meld of BrokenX raises SpellbookValidationError
          (HIDDEN_PROVIDER) - the binding thread's own melds run.
        - The window's exit then raises SpellbookValidationError, and BrokenX is not left bound.
        - On 0.2.8315 the commit skipped a staged spell that already had its Phase-4 result, so the window committed
          and BrokenX stayed bound, broken.

    Returns:
        None.
    """
    book = _book("compiled-broken")
    root = _conjure_with_hidden_provider(book, "compiled-broken-root")
    broken_id = Bind.spell_id_inspector(BrokenX)

    with pytest.raises(SpellbookValidationError):
        with book.transaction("bind"):
            book.bind(spell=BrokenX, existence=Existence.many)
            inside = _built_or_raised(root, BrokenX)
            assert isinstance(inside, SpellbookValidationError), f"the in-window meld of BrokenX: {inside!r}"

    assert book.find_spell_by_spell_id(broken_id) is None
