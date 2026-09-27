from typing import Dict, Optional

import pytest

from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import (
    SpellValidationContext,
)
from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import (
    SpellValidationIssue,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.circular_dependency_strategy import (
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
        self.selected_spell_id = current


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
        dependencies: Optional[list[str]] = None,
    ) -> None:
        """
        Purpose:
            Initialize the stub with identifiers and dependencies.
        Contract:
            dependencies is always set; None represents "no dependencies".
        Args:
            spell_id: Spell identifier for spell_index.selected_spell_id.
            spell_name: Spell name used in diagnostics.
            dependencies: Optional list of dependency ids.
        Returns:
            None.
        """
        self.spell_index = _SpellIndexStub(spell_id)
        self.spell_name = spell_name
        self.dependencies = list(dependencies) if dependencies is not None else None


class _SpellbookStub:
    """
    Purpose:
        Provide a spellbook stub exposing a spell_id pool.
    Contract:
        Stores spells by spell_id for validation strategies.
    """

    def __init__(self, spells: list[_SpellStub]) -> None:
        """
        Purpose:
            Store the spells in a spell_id pool.
        Contract:
            Builds a mapping from spell_id to spell.
        Args:
            spells: Spells to expose via spell_id pool.
        Returns:
            None.
        """
        self._spell_id_pool: Dict[str, _SpellStub] = {
            spell.spell_index.selected_spell_id: spell for spell in spells
        }


class _CancelSequence:
    """
    Purpose:
        Provide a cancellation stub with a fixed is_set sequence.
    Contract:
        Each is_set call advances through the provided sequence.
    """

    def __init__(self, sequence: list[bool], exc: Optional[Exception] = None) -> None:
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
    spellbook: Optional[_SpellbookStub],
    cancel_event: Optional[object] = None,
    issues: Optional[list[SpellValidationIssue]] = None,
) -> SpellValidationContext:
    """
    Purpose:
        Build a SpellValidationContext for strategy tests.
    Contract:
        Returns a context with the provided spell, spellbook, and issues list.
    Args:
        spell: Spell under validation.
        spellbook: Spellbook stub or None.
        cancel_event: Cancellation stub or None.
        issues: Optional issues list to populate.
    Returns:
        SpellValidationContext: The configured validation context.
    """
    if issues is None:
        issues = []
    return SpellValidationContext(
        spell=spell,
        spellbook=spellbook,
        requirements=None,
        symbolic_graph=None,
        resolution_frame=None,
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


def test_validate_without_spellbook_emits_no_issue() -> None:
    """
    Purpose:
        Ensure validation exits when no spellbook is available.
    Contract:
        No issues are added without a spellbook.
    Returns:
        None.
    Raises:
        AssertionError: If issues are added.
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    context = _make_context(
        spell=_SpellStub(spell_id="root"),
        spellbook=None,
        issues=issues,
    )

    strategy.validate(context)

    assert issues == []


def test_validate_handles_empty_spellbook() -> None:
    """
    Purpose:
        Confirm an empty spellbook produces no diagnostics.
    Contract:
        No cycle issues are reported when no spells are present.
    Returns:
        None.
    Raises:
        AssertionError: If issues are added.
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    spellbook = _SpellbookStub([])
    context = _make_context(
        spell=_SpellStub(spell_id="root"),
        spellbook=spellbook,
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
    spellbook = _SpellbookStub([root])
    context = _make_context(spell=root, spellbook=spellbook, issues=issues)

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
    spellbook = _SpellbookStub([spell_a, spell_b, spell_c])
    context = _make_context(spell=spell_a, spellbook=spellbook, issues=issues)

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
    spellbook = _SpellbookStub([root])
    context = _make_context(spell=root, spellbook=spellbook, issues=issues)

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
    spellbook = _SpellbookStub([spell_a, spell_b])
    context = _make_context(spell=spell_a, spellbook=spellbook, issues=issues)

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
    spellbook = _SpellbookStub([root, spell_b, spell_c])
    context = _make_context(spell=root, spellbook=spellbook, issues=issues)

    strategy.validate(context)

    assert issues == []


def test_validate_shared_dependency_is_not_reported_as_cycle() -> None:
    """
    Purpose:
        Verify revisiting an already explored shared dependency does not emit a cycle.
    Contract:
        A diamond-shaped graph leaves issues empty.
    Returns:
        None.
    Raises:
        AssertionError: If a cycle issue is emitted for a shared dependency.
    """
    strategy = CircularDependencyStrategy()
    root = _SpellStub(spell_id="root", dependencies=["left", "right"])
    left = _SpellStub(spell_id="left", dependencies=["shared"])
    right = _SpellStub(spell_id="right", dependencies=["shared"])
    shared = _SpellStub(spell_id="shared", dependencies=[])
    spellbook = _SpellbookStub([root, left, right, shared])
    issues: list[SpellValidationIssue] = []
    context = _make_context(spell=root, spellbook=spellbook, issues=issues)

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
    spellbook = _SpellbookStub([spell_a, spell_b, spell_c, spell_d])
    context = _make_context(spell=spell_a, spellbook=spellbook, issues=issues)

    strategy.validate(context)

    assert len(issues) == 1


def test_validate_dependencies_default_none_is_ok() -> None:
    """
    Purpose:
        Ensure default None dependencies are handled safely.
    Contract:
        No issues are emitted when dependencies is None by default.
    Returns:
        None.
    Raises:
        AssertionError: If issues are added.
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    root = _SpellStub(spell_id="root")
    spellbook = _SpellbookStub([root])
    context = _make_context(spell=root, spellbook=spellbook, issues=issues)

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
        spellbook=_SpellbookStub([]),
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
    spellbook = _SpellbookStub([spell_a, spell_b])
    context = _make_context(
        spell=spell_a,
        spellbook=spellbook,
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
    spellbook = _SpellbookStub([spell_a, spell_b])
    context = _make_context(
        spell=spell_a,
        spellbook=spellbook,
        cancel_event=cancel_event,
        issues=issues,
    )

    with pytest.raises(RuntimeError, match="cancelled"):
        strategy.validate(context)

    assert issues == []


def test_validate_names_each_cycle_member_and_closes_the_loop_once() -> None:
    """
    Purpose:
        The message names the cycle by spell name and closes it once ("A -> B -> A").
    Contract:
        No doubled start node; a fix sentence follows; details keep ids.
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    spell_a = _SpellStub(spell_id="a", spell_name="Alpha", dependencies=["b"])
    spell_b = _SpellStub(spell_id="b", spell_name="Beta", dependencies=["a"])
    spellbook = _SpellbookStub([spell_a, spell_b])
    context = _make_context(spell=spell_a, spellbook=spellbook, issues=issues)

    strategy.validate(context)

    message = issues[0].message
    assert "'Alpha' -> 'Beta' -> 'Alpha'." in message
    assert "-> 'Alpha' -> 'Alpha'" not in message
    assert "give that parameter a default" in message


def test_validate_words_a_consumer_of_a_cycle_member_as_a_consumer() -> None:
    """
    Purpose:
        A spell that only needs a cycle member is not reported as part of the cycle (2026-09-26).
    Contract:
        The message names the member it needs, the cycle, the fix, and that the spell is not
        part of that cycle; code, severity and details are unchanged.
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    spell_a = _SpellStub(spell_id="a", spell_name="Alpha", dependencies=["b"])
    spell_b = _SpellStub(spell_id="b", spell_name="Beta", dependencies=["a"])
    spell_c = _SpellStub(spell_id="c", spell_name="Gamma", dependencies=["a"])
    spellbook = _SpellbookStub([spell_a, spell_b, spell_c])
    context = _make_context(spell=spell_c, spellbook=spellbook, issues=issues)

    strategy.validate(context)

    assert len(issues) == 1
    issue = issues[0]
    assert issue.code == "CIRCULAR_DEPENDENCY"
    assert issue.severity == "error"
    assert issue.details == {"cycle": ["a", "b", "a"]}
    assert issue.message == (
        "Spell 'Gamma' cannot be built: it needs 'Alpha', which is part of a dependency cycle: "
        "'Alpha' -> 'Beta' -> 'Alpha'. Break that cycle (remove one of those constructor "
        "dependencies or give that parameter a default); 'Gamma' itself is not part of that cycle."
    )


def test_validate_names_the_intermediate_that_leads_a_consumer_to_a_cycle() -> None:
    """
    Purpose:
        A spell that reaches a cycle through a non-member names that intermediate.
    Contract:
        "which depends on a dependency cycle" follows the intermediate; the cycle is unchanged.
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    spell_a = _SpellStub(spell_id="a", spell_name="Alpha", dependencies=["b"])
    spell_b = _SpellStub(spell_id="b", spell_name="Beta", dependencies=["a"])
    spell_c = _SpellStub(spell_id="c", spell_name="Gamma", dependencies=["a"])
    spell_d = _SpellStub(spell_id="d", spell_name="Delta", dependencies=["c"])
    spellbook = _SpellbookStub([spell_a, spell_b, spell_c, spell_d])
    context = _make_context(spell=spell_d, spellbook=spellbook, issues=issues)

    strategy.validate(context)

    message = issues[0].message
    assert message.startswith(
        "Spell 'Delta' cannot be built: it needs 'Gamma', which depends on a dependency cycle: "
        "'Alpha' -> 'Beta' -> 'Alpha'. Break that cycle"
    )
    assert message.endswith("'Delta' itself is not part of that cycle.")
    assert issues[0].details == {"cycle": ["a", "b", "a"]}


def test_validate_words_a_consumer_of_a_self_loop() -> None:
    """
    Purpose:
        A spell that needs a spell depending on itself is told so, and the fix names that spell.
    Contract:
        "which depends on itself" with the two-entry loop; the fix is "Fix 'Node' (...)".
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    node = _SpellStub(spell_id="n", spell_name="Node", dependencies=["n"])
    tree = _SpellStub(spell_id="t", spell_name="Tree", dependencies=["n"])
    spellbook = _SpellbookStub([node, tree])
    context = _make_context(spell=tree, spellbook=spellbook, issues=issues)

    strategy.validate(context)

    assert issues[0].message == (
        "Spell 'Tree' cannot be built: it needs 'Node', which depends on itself ('Node' -> 'Node'). "
        "Fix 'Node' (remove that constructor dependency or give that parameter a default); "
        "'Tree' itself is not part of that cycle."
    )
    assert issues[0].details == {"cycle": ["n", "n"]}


def test_validate_names_the_intermediate_before_a_self_loop() -> None:
    """
    Purpose:
        A spell that reaches a self-loop through a non-member names the intermediate and fixes the loop spell.
    Contract:
        "which depends on a dependency cycle: 'Node' -> 'Node'" and "Fix 'Node' (...)".
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    node = _SpellStub(spell_id="n", spell_name="Node", dependencies=["n"])
    tree = _SpellStub(spell_id="t", spell_name="Tree", dependencies=["n"])
    forest = _SpellStub(spell_id="f", spell_name="Forest", dependencies=["t"])
    spellbook = _SpellbookStub([node, tree, forest])
    context = _make_context(spell=forest, spellbook=spellbook, issues=issues)

    strategy.validate(context)

    message = issues[0].message
    assert message.startswith(
        "Spell 'Forest' cannot be built: it needs 'Tree', which depends on a dependency cycle: "
        "'Node' -> 'Node'. Fix 'Node' (remove that constructor dependency"
    )
    assert message.endswith("'Forest' itself is not part of that cycle.")


def test_validate_keeps_the_member_wording_for_a_self_loop_member() -> None:
    """
    Purpose:
        The spell that depends on itself keeps the member wording.
    Contract:
        "Spell 'Node' is part of a dependency cycle: 'Node' -> 'Node'." with the member fix sentence.
    """
    strategy = CircularDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    node = _SpellStub(spell_id="n", spell_name="Node", dependencies=["n"])
    spellbook = _SpellbookStub([node])
    context = _make_context(spell=node, spellbook=spellbook, issues=issues)

    strategy.validate(context)

    assert issues[0].message.startswith("Spell 'Node' is part of a dependency cycle: 'Node' -> 'Node'.")
    assert "cannot be built" not in issues[0].message
