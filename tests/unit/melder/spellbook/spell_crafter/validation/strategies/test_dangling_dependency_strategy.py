from __future__ import annotations

from typing import Iterable

import pytest

from melder.spellbook.spell_crafter.validation.spell_validation_context import (
    SpellValidationContext,
)
from melder.spellbook.spell_crafter.validation.spell_validation_issue import (
    SpellValidationIssue,
)
from melder.spellbook.spell_crafter.validation.strategies.dangling_dependency_strategy import (
    DanglingDependenciesStrategy,
)


class _SpellIndexStub:
    """
    Purpose:
        Provide a minimal spell index with a current id.
    Contract:
        Exposes the current id without validation.
    """

    def __init__(self, current: str) -> None:
        """
        Purpose:
            Initialize the stub with a current id.
        Contract:
            Stores the provided id as current.
        Args:
            current: Spell identifier string.
        Returns:
            None.
        """
        self.current = current


class _SpellStub:
    """
    Purpose:
        Provide a spell stub with index, name, and dependencies.
    Contract:
        Optionally exposes dependencies to mimic spell graph entries.
    """

    def __init__(
        self,
        *,
        spell_id: str,
        spell_name: str = "spell-name",
        dependencies: list[str] | None = None,
        include_dependencies: bool = True,
    ) -> None:
        """
        Purpose:
            Initialize the stub with identifiers and dependencies.
        Contract:
            When include_dependencies is False, dependencies is not set.
        Args:
            spell_id: Spell identifier for spell_index.current.
            spell_name: Spell name used in diagnostics.
            dependencies: Optional list of dependency ids.
            include_dependencies: Whether to set the dependencies attribute.
        Returns:
            None.
        """
        self.spell_index = _SpellIndexStub(spell_id)
        self.spell_name = spell_name
        if include_dependencies:
            self.dependencies = list(dependencies) if dependencies is not None else []


class _ScannerStub:
    """
    Purpose:
        Provide a scanner stub yielding spell/index pairs.
    Contract:
        Iteration order matches the provided spell list.
    """

    def __init__(self, spells: list[_SpellStub]) -> None:
        """
        Purpose:
            Store the spells to be yielded during iteration.
        Contract:
            Copies the provided list for stable iteration.
        Args:
            spells: Spells to yield in iter_all_spells.
        Returns:
            None.
        """
        self._spells = list(spells)

    def iter_all_spells(self) -> Iterable[tuple[_SpellIndexStub, _SpellStub]]:
        """
        Purpose:
            Yield all spells with their index objects.
        Contract:
            Each yielded pair matches spell.spell_index and the spell.
        Returns:
            Iterable[tuple[_SpellIndexStub, _SpellStub]]: Index and spell pairs.
        """
        for spell in self._spells:
            yield spell.spell_index, spell


class _CancelSequence:
    """
    Purpose:
        Provide a cancellation stub with a fixed is_set sequence.
    Contract:
        Each is_set call advances through the provided sequence.
    """

    def __init__(self, sequence: list[bool], exc: Exception | None = None) -> None:
        """
        Purpose:
            Initialize the cancellation sequence and exception.
        Contract:
            Stores the sequence and raises the provided exception when set.
        Args:
            sequence: Ordered cancellation states to return.
            exc: Exception to raise when cancellation is active.
        Returns:
            None.
        """
        self._sequence = list(sequence) if sequence else [False]
        self._index = 0
        self._last = False
        self._exc = exc or RuntimeError("cancelled")

    @property
    def is_set(self) -> bool:
        """
        Purpose:
            Return the next cancellation state in the sequence.
        Contract:
            Once exhausted, the last state is reused.
        Returns:
            bool: Current cancellation state.
        """
        if self._index < len(self._sequence):
            self._last = self._sequence[self._index]
            self._index += 1
        return self._last

    def throw_if_set(self) -> None:
        """
        Purpose:
            Raise the configured exception when cancellation is active.
        Contract:
            Uses the most recent is_set value when available.
        Raises:
            Exception: When cancellation is active.
        """
        if self._index == 0:
            _ = self.is_set
        if self._last:
            raise self._exc


def _make_context(
    *,
    spell: _SpellStub,
    scanner: _ScannerStub | None,
    cancel_event: object | None = None,
    issues: list[SpellValidationIssue] | None = None,
) -> SpellValidationContext:
    """
    Purpose:
        Build a SpellValidationContext for strategy tests.
    Contract:
        Returns a context with the provided spell, scanner, and issues list.
    Args:
        spell: Spell under validation.
        scanner: Spellbook scanner stub or None.
        cancel_event: Cancellation stub or None.
        issues: Optional issues list to populate.
    Returns:
        SpellValidationContext: The configured validation context.
    """
    if issues is None:
        issues = []
    return SpellValidationContext(
        spell=spell,
        spellbook=None,
        requirements=None,
        symbolic_graph=None,
        resolution_frame=None,
        scanner=scanner,
        cancel_event=cancel_event,
        issues=issues,
    )


def test_init_sets_name_and_description() -> None:
    """
    Purpose:
        Verify strategy metadata is initialized.
    Contract:
        Name matches the expected identifier and description is non-empty.
    Returns:
        None.
    Raises:
        AssertionError: If metadata is missing or incorrect.
    """
    strategy = DanglingDependenciesStrategy()
    assert strategy.name == "dangling_dependencies"
    assert "dependency" in strategy.description.lower()


def test_validate_no_dependencies_is_noop() -> None:
    """
    Purpose:
        Ensure spells with no dependencies emit no issues.
    Contract:
        No diagnostics are added when dependencies are empty.
    Returns:
        None.
    Raises:
        AssertionError: If issues are added.
    """
    strategy = DanglingDependenciesStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_id="root", dependencies=[])
    context = _make_context(spell=spell, scanner=None, issues=issues)

    strategy.validate(context)

    assert issues == []


def test_validate_missing_dependencies_attribute_is_ok() -> None:
    """
    Purpose:
        Ensure missing dependencies attribute is treated as no dependencies.
    Contract:
        No diagnostics are added when dependencies are absent.
    Returns:
        None.
    Raises:
        AssertionError: If issues are added.
    """
    strategy = DanglingDependenciesStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(
        spell_id="root",
        include_dependencies=False,
    )
    context = _make_context(spell=spell, scanner=None, issues=issues)

    strategy.validate(context)

    assert issues == []


def test_validate_dependencies_none_is_noop() -> None:
    """
    Purpose:
        Ensure a None dependencies value is treated as empty.
    Contract:
        No diagnostics are added when dependencies is None.
    Returns:
        None.
    Raises:
        AssertionError: If issues are added.
    """
    strategy = DanglingDependenciesStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(
        spell_id="root",
        dependencies=None,
        include_dependencies=True,
    )
    context = _make_context(spell=spell, scanner=None, issues=issues)

    strategy.validate(context)

    assert issues == []


def test_validate_dependencies_tuple_is_supported() -> None:
    """
    Purpose:
        Ensure tuple dependencies are handled like lists.
    Contract:
        Missing ids from a tuple are still reported.
    Returns:
        None.
    Raises:
        AssertionError: If missing dependencies are not reported.
    """
    strategy = DanglingDependenciesStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_id="root", dependencies=[])
    spell.dependencies = ("missing",)
    scanner = _ScannerStub([spell])
    context = _make_context(spell=spell, scanner=scanner, issues=issues)

    strategy.validate(context)

    assert len(issues) == 1
    assert issues[0].details["missing_spell_id"] == "missing"


def test_validate_warns_when_dependencies_and_no_scanner() -> None:
    """
    Purpose:
        Ensure missing scanner yields a warning when dependencies exist.
    Contract:
        A warning issue is added when dependencies cannot be verified.
    Returns:
        None.
    Raises:
        AssertionError: If the warning is missing or incorrect.
    """
    strategy = DanglingDependenciesStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_id="root", spell_name="Root", dependencies=["a"])
    context = _make_context(spell=spell, scanner=None, issues=issues)

    strategy.validate(context)

    assert len(issues) == 1
    issue = issues[0]
    assert issue.severity == "warning"
    assert issue.code == "NO_SPELLBOOK_FOR_DEPENDENCY_CHECK"
    assert "Root" in issue.message
    assert issue.details == {}


def test_validate_warns_once_even_with_multiple_dependencies() -> None:
    """
    Purpose:
        Ensure no-scanner warning is emitted only once.
    Contract:
        A single warning is produced regardless of dependency count.
    Returns:
        None.
    Raises:
        AssertionError: If multiple warnings are emitted.
    """
    strategy = DanglingDependenciesStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_id="root", dependencies=["a", "b"])
    context = _make_context(spell=spell, scanner=None, issues=issues)

    strategy.validate(context)

    assert len(issues) == 1


def test_validate_all_dependencies_present_no_issues() -> None:
    """
    Purpose:
        Confirm no issues are emitted when all dependencies exist.
    Contract:
        Validation produces no diagnostics when dependencies are resolved.
    Returns:
        None.
    Raises:
        AssertionError: If issues are added.
    """
    strategy = DanglingDependenciesStrategy()
    issues: list[SpellValidationIssue] = []
    root = _SpellStub(spell_id="root", dependencies=["a", "b"])
    spell_a = _SpellStub(spell_id="a", dependencies=[])
    spell_b = _SpellStub(spell_id="b", dependencies=[])
    scanner = _ScannerStub([root, spell_a, spell_b])
    context = _make_context(spell=root, scanner=scanner, issues=issues)

    strategy.validate(context)

    assert issues == []


def test_validate_missing_dependency_emits_issue() -> None:
    """
    Purpose:
        Ensure missing dependencies are reported as errors.
    Contract:
        A dangling dependency issue is emitted with the missing id.
    Returns:
        None.
    Raises:
        AssertionError: If the issue is missing or malformed.
    """
    strategy = DanglingDependenciesStrategy()
    issues: list[SpellValidationIssue] = []
    root = _SpellStub(spell_id="root", spell_name="Root", dependencies=["missing"])
    scanner = _ScannerStub([root])
    context = _make_context(spell=root, scanner=scanner, issues=issues)

    strategy.validate(context)

    assert len(issues) == 1
    issue = issues[0]
    assert issue.severity == "error"
    assert issue.code == "DANGLING_DEPENDENCY"
    assert issue.details["missing_spell_id"] == "missing"
    assert "Root" in issue.message


def test_validate_multiple_missing_dependencies_emit_multiple_issues() -> None:
    """
    Purpose:
        Ensure each missing dependency produces its own issue.
    Contract:
        Each missing id is reported with a distinct issue.
    Returns:
        None.
    Raises:
        AssertionError: If the issue count or details are incorrect.
    """
    strategy = DanglingDependenciesStrategy()
    issues: list[SpellValidationIssue] = []
    root = _SpellStub(spell_id="root", dependencies=["x", "y"])
    scanner = _ScannerStub([root])
    context = _make_context(spell=root, scanner=scanner, issues=issues)

    strategy.validate(context)

    assert len(issues) == 2
    missing_ids = {issue.details["missing_spell_id"] for issue in issues}
    assert missing_ids == {"x", "y"}


def test_validate_mixed_dependencies_reports_only_missing() -> None:
    """
    Purpose:
        Verify only missing dependency ids are flagged.
    Contract:
        Issues are produced only for ids not in the scanner.
    Returns:
        None.
    Raises:
        AssertionError: If extra issues are emitted.
    """
    strategy = DanglingDependenciesStrategy()
    issues: list[SpellValidationIssue] = []
    root = _SpellStub(spell_id="root", dependencies=["a", "missing"])
    spell_a = _SpellStub(spell_id="a", dependencies=[])
    scanner = _ScannerStub([root, spell_a])
    context = _make_context(spell=root, scanner=scanner, issues=issues)

    strategy.validate(context)

    assert len(issues) == 1
    assert issues[0].details["missing_spell_id"] == "missing"


def test_validate_duplicate_scanner_ids_do_not_create_issues() -> None:
    """
    Purpose:
        Confirm duplicate ids in the scanner do not create false errors.
    Contract:
        Dependencies are considered resolved if any spell matches the id.
    Returns:
        None.
    Raises:
        AssertionError: If an issue is emitted incorrectly.
    """
    strategy = DanglingDependenciesStrategy()
    issues: list[SpellValidationIssue] = []
    root = _SpellStub(spell_id="root", dependencies=["a"])
    spell_a1 = _SpellStub(spell_id="a", dependencies=[])
    spell_a2 = _SpellStub(spell_id="a", dependencies=[])
    scanner = _ScannerStub([root, spell_a1, spell_a2])
    context = _make_context(spell=root, scanner=scanner, issues=issues)

    strategy.validate(context)

    assert issues == []


def test_validate_cancellation_preempts() -> None:
    """
    Purpose:
        Ensure cancellation is honored before any work begins.
    Contract:
        validate raises and does not emit issues when cancelled.
    Returns:
        None.
    Raises:
        RuntimeError: When cancellation is signaled.
    """
    strategy = DanglingDependenciesStrategy()
    issues: list[SpellValidationIssue] = []
    cancel_event = _CancelSequence([True], exc=RuntimeError("cancelled"))
    spell = _SpellStub(spell_id="root", dependencies=["a"])
    context = _make_context(
        spell=spell,
        scanner=_ScannerStub([spell]),
        cancel_event=cancel_event,
        issues=issues,
    )

    with pytest.raises(RuntimeError, match="cancelled"):
        strategy.validate(context)

    assert issues == []


def test_validate_cancellation_during_dependency_loop() -> None:
    """
    Purpose:
        Ensure cancellation is checked during dependency iteration.
    Contract:
        Validation raises before processing the cancelled dependency.
    Returns:
        None.
    Raises:
        RuntimeError: When cancellation is signaled.
    """
    strategy = DanglingDependenciesStrategy()
    issues: list[SpellValidationIssue] = []
    cancel_event = _CancelSequence([False, False, True], exc=RuntimeError("cancelled"))
    root = _SpellStub(spell_id="root", dependencies=["missing", "missing2"])
    scanner = _ScannerStub([root])
    context = _make_context(
        spell=root,
        scanner=scanner,
        cancel_event=cancel_event,
        issues=issues,
    )

    with pytest.raises(RuntimeError, match="cancelled"):
        strategy.validate(context)

    assert len(issues) == 1
