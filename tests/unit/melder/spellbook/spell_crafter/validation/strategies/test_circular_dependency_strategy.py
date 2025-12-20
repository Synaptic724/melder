from __future__ import annotations

from typing import Iterable

import pytest

from melder.spellbook.spell_crafter.validation.spell_validation_context import (
    SpellValidationContext,
)
from melder.spellbook.spell_crafter.validation.spell_validation_issue import (
    SpellValidationIssue,
)
from melder.spellbook.spell_crafter.validation.strategies.circular_dependency_strategy import (
    CircularDependencyStrategy,
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
    strategy = CircularDependencyStrategy()
    assert strategy.name == "circular_dependency"
    assert "cycle" in strategy.description.lower()


def test_validate_without_scanner_emits_no_issue() -> None:
    """
    Purpose:
        Ensure validation exits when no scanner is available.
    Contract:
        No issues are added without a scanner.
    Returns:
        None.
    Raises:
        AssertionError: If issues are added.
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    context = _make_context(
        spell=_SpellStub(spell_id="root"),
        scanner=None,
        issues=issues,
    )

    strategy.validate(context)

    assert issues == []


def test_validate_handles_empty_scanner() -> None:
    """
    Purpose:
        Confirm an empty scanner produces no diagnostics.
    Contract:
        No cycle issues are reported when no spells are present.
    Returns:
        None.
    Raises:
        AssertionError: If issues are added.
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    scanner = _ScannerStub([])
    context = _make_context(
        spell=_SpellStub(spell_id="root"),
        scanner=scanner,
        issues=issues,
    )

    strategy.validate(context)

    assert issues == []


def test_validate_ignores_dangling_dependency() -> None:
    """
    Purpose:
        Ensure dangling dependency nodes are ignored for cycle detection.
    Contract:
        No issues are reported when a dependency is missing from adjacency.
    Returns:
        None.
    Raises:
        AssertionError: If a cycle issue is reported.
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    root = _SpellStub(spell_id="root", dependencies=["missing"])
    scanner = _ScannerStub([root])
    context = _make_context(spell=root, scanner=scanner, issues=issues)

    strategy.validate(context)

    assert issues == []


def test_validate_linear_chain_is_acyclic() -> None:
    """
    Purpose:
        Confirm a linear dependency chain is not flagged as cyclic.
    Contract:
        No issues are reported for a simple acyclic chain.
    Returns:
        None.
    Raises:
        AssertionError: If a cycle issue is reported.
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    spell_a = _SpellStub(spell_id="a", dependencies=["b"])
    spell_b = _SpellStub(spell_id="b", dependencies=["c"])
    spell_c = _SpellStub(spell_id="c", dependencies=[])
    scanner = _ScannerStub([spell_a, spell_b, spell_c])
    context = _make_context(spell=spell_a, scanner=scanner, issues=issues)

    strategy.validate(context)

    assert issues == []


def test_validate_detects_self_cycle() -> None:
    """
    Purpose:
        Ensure self-dependencies are flagged as cycles.
    Contract:
        A single circular dependency issue is emitted.
    Returns:
        None.
    Raises:
        AssertionError: If the issue is missing or malformed.
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    root = _SpellStub(spell_id="a", spell_name="Alpha", dependencies=["a"])
    scanner = _ScannerStub([root])
    context = _make_context(spell=root, scanner=scanner, issues=issues)

    strategy.validate(context)

    assert len(issues) == 1
    issue = issues[0]
    assert issue.code == "CIRCULAR_DEPENDENCY"
    assert issue.severity == "error"
    assert "Alpha" in issue.message
    assert "a" in issue.details["cycle"]


def test_validate_detects_two_node_cycle() -> None:
    """
    Purpose:
        Ensure a two-node cycle is detected.
    Contract:
        A circular dependency issue includes both nodes in details.
    Returns:
        None.
    Raises:
        AssertionError: If the cycle is not reported correctly.
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    spell_a = _SpellStub(spell_id="a", spell_name="Alpha", dependencies=["b"])
    spell_b = _SpellStub(spell_id="b", spell_name="Beta", dependencies=["a"])
    scanner = _ScannerStub([spell_a, spell_b])
    context = _make_context(spell=spell_a, scanner=scanner, issues=issues)

    strategy.validate(context)

    assert len(issues) == 1
    issue = issues[0]
    assert issue.code == "CIRCULAR_DEPENDENCY"
    assert issue.severity == "error"
    assert "Alpha" in issue.message
    assert "a" in issue.details["cycle"]
    assert "b" in issue.details["cycle"]


def test_validate_ignores_unreachable_cycle() -> None:
    """
    Purpose:
        Ensure cycles not reachable from the root spell are ignored.
    Contract:
        No issues are reported when the root cannot reach a cycle.
    Returns:
        None.
    Raises:
        AssertionError: If a cycle issue is reported.
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    root = _SpellStub(spell_id="root", dependencies=[])
    spell_b = _SpellStub(spell_id="b", dependencies=["c"])
    spell_c = _SpellStub(spell_id="c", dependencies=["b"])
    scanner = _ScannerStub([root, spell_b, spell_c])
    context = _make_context(spell=root, scanner=scanner, issues=issues)

    strategy.validate(context)

    assert issues == []


def test_validate_reports_single_issue_for_multiple_cycles() -> None:
    """
    Purpose:
        Confirm only the first detected cycle is reported.
    Contract:
        A single issue is emitted even when multiple cycles exist.
    Returns:
        None.
    Raises:
        AssertionError: If multiple issues are reported.
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    spell_a = _SpellStub(spell_id="a", dependencies=["b", "c"])
    spell_b = _SpellStub(spell_id="b", dependencies=["a"])
    spell_c = _SpellStub(spell_id="c", dependencies=["d"])
    spell_d = _SpellStub(spell_id="d", dependencies=["c"])
    scanner = _ScannerStub([spell_a, spell_b, spell_c, spell_d])
    context = _make_context(spell=spell_a, scanner=scanner, issues=issues)

    strategy.validate(context)

    assert len(issues) == 1


def test_validate_missing_dependencies_attribute_is_ok() -> None:
    """
    Purpose:
        Ensure spells without a dependencies attribute are handled safely.
    Contract:
        No issues are emitted when dependencies are absent.
    Returns:
        None.
    Raises:
        AssertionError: If issues are added.
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    root = _SpellStub(
        spell_id="root",
        include_dependencies=False,
    )
    scanner = _ScannerStub([root])
    context = _make_context(spell=root, scanner=scanner, issues=issues)

    strategy.validate(context)

    assert issues == []


def test_validate_cancel_event_preempts() -> None:
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
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    cancel_event = _CancelSequence([True], exc=RuntimeError("cancelled"))
    context = _make_context(
        spell=_SpellStub(spell_id="root"),
        scanner=_ScannerStub([]),
        cancel_event=cancel_event,
        issues=issues,
    )

    with pytest.raises(RuntimeError, match="cancelled"):
        strategy.validate(context)

    assert issues == []


def test_validate_cancel_event_during_scan() -> None:
    """
    Purpose:
        Ensure cancellation is checked while building the adjacency list.
    Contract:
        validate raises during scanning when cancellation toggles on.
    Returns:
        None.
    Raises:
        RuntimeError: When cancellation is signaled.
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    cancel_event = _CancelSequence([False, False, True], exc=RuntimeError("cancelled"))
    spell_a = _SpellStub(spell_id="a", dependencies=[])
    spell_b = _SpellStub(spell_id="b", dependencies=[])
    scanner = _ScannerStub([spell_a, spell_b])
    context = _make_context(
        spell=spell_a,
        scanner=scanner,
        cancel_event=cancel_event,
        issues=issues,
    )

    with pytest.raises(RuntimeError, match="cancelled"):
        strategy.validate(context)

    assert issues == []


def test_validate_cancel_event_during_traversal() -> None:
    """
    Purpose:
        Ensure cancellation is checked during dependency traversal.
    Contract:
        validate raises when cancellation toggles during DFS.
    Returns:
        None.
    Raises:
        RuntimeError: When cancellation is signaled.
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    cancel_event = _CancelSequence(
        [False, False, False, True],
        exc=RuntimeError("cancelled"),
    )
    spell_a = _SpellStub(spell_id="a", dependencies=["b"])
    spell_b = _SpellStub(spell_id="b", dependencies=[])
    scanner = _ScannerStub([spell_a, spell_b])
    context = _make_context(
        spell=spell_a,
        scanner=scanner,
        cancel_event=cancel_event,
        issues=issues,
    )

    with pytest.raises(RuntimeError, match="cancelled"):
        strategy.validate(context)

    assert issues == []
