"""
Contract tests for the target-local pass flag: a dependency compiled only inside its consumer's plan owes its own
resolution, so its first direct meld resolves it.

`SpellbookCreationSystem.flag_dependencies_without_own_plan` runs at the tail of a successful
`run_resolution_phases_for_target_spell`. It flags `resolution_required` on each spell in the pass's scope that the
Book owns, that is resolvable and not an existing creation, and that has neither a phase-11 plan nor a published
CreationContext, writing under that spell's lock. These tests pin who is flagged, who is left alone, where the
write happens, and that only the success path flags.
"""

import types
from threading import RLock
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import pytest

from melder.aether.spellbook.spellbook_creation_system import SpellbookCreationSystem
from melder.utilities.custom_exceptions.phase_execution_error import PhaseExecutionError
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError


class _RecordingLock:
    """
    A spell lock that records its spell's `resolution_required` when entered and when left.

    Lets a test show the flag is written while the lock is held: False on entry, True on exit.
    """

    def __init__(self) -> None:
        """Start unbound, with an inner re-entrant lock and empty records."""
        self.inner: RLock = RLock()
        self.spell: Optional["_SpellStub"] = None
        self.flag_on_enter: List[bool] = []
        self.flag_on_exit: List[bool] = []

    def __enter__(self) -> "_RecordingLock":
        """Acquire the inner lock and record the spell's flag."""
        self.inner.acquire()
        assert self.spell is not None
        self.flag_on_enter.append(self.spell.resolution_required)
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        """Record the spell's flag and release the inner lock."""
        assert self.spell is not None
        self.flag_on_exit.append(self.spell.resolution_required)
        self.inner.release()


class _SpellStub:
    """The Spell surface the flag reads and writes."""

    def __init__(
            self,
            spell_id: str,
            spellbook: object,
            *,
            has_plan: bool = False,
            has_context: bool = False,
            resolvable: bool = True,
            is_existing_creation: bool = False,
            resolution_required: bool = False,
    ) -> None:
        """
        Build a spell stub.

        Args:
            spell_id: The spell id.
            spellbook: The owning Book (identity is what the flag compares).
            has_plan: Whether the compiler artifact holds a phase-11 plan.
            has_context: Whether a CreationContext is published (switch state 2).
            resolvable: The registration's resolvable capability.
            is_existing_creation: Whether the spell wraps an existing object.
            resolution_required: The flag's starting value.
        """
        self.spell_id: str = spell_id
        self._spellbook: object = spellbook
        self.resolvable: bool = resolvable
        self.is_existing_creation: bool = is_existing_creation
        self._compiler_artifact = types.SimpleNamespace(
            _spell_codegen_creation=object() if has_plan else None,
        )
        self._creation_context_switch = types.SimpleNamespace(state=2 if has_context else 0)
        self.resolution_required: bool = resolution_required
        self.resolution_complete: bool = not resolution_required
        self._door_epoch: int = 0
        self._lock: _RecordingLock = _RecordingLock()
        self._lock.spell = self


class _SpellbookStub:
    """The Spellbook surface the flag and the target pass read."""

    def __init__(self) -> None:
        """Start with an empty visible pool and a resolution state with no diagnostics."""
        self._spell_id_pool: Dict[str, Any] = {}
        self._spell_system_states = types.SimpleNamespace(
            get_conduit_resolution_state=lambda conduit_id: types.SimpleNamespace(list_diagnostics=lambda: []),
        )

    def check_cleaned(self) -> None:
        """Mirror Spellbook.check_cleaned for the target pass; the stub is never cleaned."""

    def add(self, spell: _SpellStub) -> _SpellStub:
        """Put one spell in the visible pool and return it."""
        self._spell_id_pool[spell.spell_id] = spell
        return spell


def _flag(spellbook: _SpellbookStub, target_spell_id: str, scoped_spell_ids: Set[str]) -> Tuple[str, ...]:
    """Run the flag over one scope and return the flagged ids."""
    return SpellbookCreationSystem.flag_dependencies_without_own_plan(
        spellbook=spellbook,
        target_spell_id=target_spell_id,
        scoped_spell_ids=scoped_spell_ids,
    )


def test_flags_owned_dependency_without_plan_or_context() -> None:
    """An owned, resolvable, plan-less dependency with no context is flagged and its door epoch bumped."""
    book = _SpellbookStub()
    dependency = book.add(_SpellStub("dep", book))

    assert _flag(book, "consumer", {"consumer", "dep"}) == ("dep",)
    assert dependency.resolution_required is True
    assert dependency.resolution_complete is False
    assert dependency._door_epoch == 1


@pytest.mark.parametrize(
    ("case", "kwargs"),
    [
        ("own plan", {"has_plan": True}),
        ("published context", {"has_context": True}),
        ("existing creation", {"is_existing_creation": True}),
        ("non-resolvable definition", {"resolvable": False}),
    ],
)
def test_leaves_dependency_that_needs_no_pass_of_its_own(case: str, kwargs: Dict[str, bool]) -> None:
    """A dependency with a plan or a context, an existing creation, or a non-resolvable definition stays as it was."""
    book = _SpellbookStub()
    dependency = book.add(_SpellStub("dep", book, **kwargs))

    assert _flag(book, "consumer", {"consumer", "dep"}) == (), case
    assert dependency.resolution_required is False
    assert dependency.resolution_complete is True
    assert dependency._door_epoch == 0


def test_leaves_dependency_owned_by_another_book() -> None:
    """A borrowed dependency belongs to its own Book's passes and is never flagged by this one."""
    book = _SpellbookStub()
    borrowed = book.add(_SpellStub("dep", object()))

    assert _flag(book, "consumer", {"consumer", "dep"}) == ()
    assert borrowed.resolution_required is False
    assert borrowed._door_epoch == 0


def test_leaves_the_target_and_ids_missing_from_the_pool() -> None:
    """The pass's own target is never flagged, and a scoped id the pool no longer holds is skipped."""
    book = _SpellbookStub()
    target = book.add(_SpellStub("consumer", book))

    assert _flag(book, "consumer", {"consumer", "gone"}) == ()
    assert target.resolution_required is False
    assert target._door_epoch == 0


def test_already_flagged_dependency_is_not_flagged_again() -> None:
    """Flagging is idempotent: a dependency that already owes its pass keeps its epoch and is not reported."""
    book = _SpellbookStub()
    dependency = book.add(_SpellStub("dep", book, resolution_required=True))

    assert _flag(book, "consumer", {"consumer", "dep"}) == ()
    assert dependency.resolution_required is True
    assert dependency._door_epoch == 0


def test_flags_every_plan_less_dependency_in_sorted_order() -> None:
    """Transitive dependencies in the scope are flagged too, and the ids come back sorted."""
    book = _SpellbookStub()
    for spell_id in ("dep-c", "dep-a", "dep-b"):
        book.add(_SpellStub(spell_id, book))
    book.add(_SpellStub("dep-planned", book, has_plan=True))

    assert _flag(book, "consumer", {"consumer", "dep-c", "dep-a", "dep-planned", "dep-b"}) == (
        "dep-a", "dep-b", "dep-c",
    )


def test_flag_is_written_under_the_dependency_lock() -> None:
    """The check and the write happen while the dependency's own spell lock is held."""
    book = _SpellbookStub()
    dependency = book.add(_SpellStub("dep", book))

    _flag(book, "consumer", {"consumer", "dep"})

    assert dependency._lock.flag_on_enter == [False]
    assert dependency._lock.flag_on_exit == [True]


def _stub_target_pass_phases(
        monkeypatch: pytest.MonkeyPatch,
        plan_phases: Callable[..., Dict[str, Any]],
        has_errors: bool = False,
) -> None:
    """Replace the target pass's phase runners so only its orchestration and tail run."""
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_run_target_foundational_resolution_phases",
        staticmethod(lambda **kwargs: {"root_blueprints_local": ["rb"]}),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_conduit_resolution_has_errors",
        staticmethod(lambda **kwargs: has_errors),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_collect_target_resolution_scope",
        staticmethod(lambda **kwargs: ({"consumer", "dep"}, ("consumer",))),
    )
    monkeypatch.setattr(SpellbookCreationSystem, "_run_target_plan_resolution_phases", staticmethod(plan_phases))
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "record_local_resolution_visibility_failure",
        staticmethod(lambda **kwargs: None),
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "cleanup_phase_artifacts_after_resolution",
        staticmethod(lambda *, spellbook, spell_ids=None: None),
    )


def _run_target_pass(book: _SpellbookStub) -> Dict[str, Any]:
    """Run the target-local pass for the consumer over the stubbed phases."""
    return SpellbookCreationSystem.run_resolution_phases_for_target_spell(
        spellbook=book,
        conduit_id="cid",
        target_spell=types.SimpleNamespace(spell_id="consumer"),
    )


def test_target_pass_flags_plan_less_dependencies_when_it_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    """A successful target pass leaves its plan-less owned dependency owing its own resolution."""
    book = _SpellbookStub()
    dependency = book.add(_SpellStub("dep", book))
    _stub_target_pass_phases(monkeypatch, lambda **kwargs: {"occurrence_plan_local": ["op"]})

    assert _run_target_pass(book) == {"root_blueprints_local": ["rb"], "occurrence_plan_local": ["op"]}
    assert dependency.resolution_required is True
    assert dependency.resolution_complete is False


def test_target_pass_flags_nothing_after_a_visibility_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """A visibility failure records invalid verdicts and returns; it flags no dependency."""
    book = _SpellbookStub()
    dependency = book.add(_SpellStub("dep", book))

    def _missing_dependency(**kwargs: Any) -> Dict[str, Any]:
        """Fail the plan phases on a dependency the Book cannot see."""
        raise PhaseExecutionError("phase failed", errors=[KeyError("missing-dep")])

    _stub_target_pass_phases(monkeypatch, _missing_dependency)

    assert _run_target_pass(book) == {"root_blueprints_local": ["rb"]}
    assert dependency.resolution_required is False
    assert dependency._door_epoch == 0


def test_target_pass_flags_nothing_when_its_foundational_phases_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    """Foundational errors raise the validation error before any plan phase; no dependency is flagged."""
    book = _SpellbookStub()
    dependency = book.add(_SpellStub("dep", book))
    _stub_target_pass_phases(monkeypatch, lambda **kwargs: {"occurrence_plan_local": ["op"]}, has_errors=True)

    with pytest.raises(SpellbookValidationError):
        _run_target_pass(book)
    assert dependency.resolution_required is False
    assert dependency._door_epoch == 0
