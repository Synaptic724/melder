import pytest
from typing import List, Optional

from melder.spellbook.spell_crafter.validation.spell_validation_context import (
    SpellValidationContext,
)
from melder.spellbook.spell_crafter.validation.spell_validation_issue import (
    SpellValidationIssue,
)
from melder.spellbook.spell_crafter.validation.strategies.self_validation_strategy import (
    SelfDependencyStrategy,
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
        Provide a spell stub with name, index, and dependencies.
    Contract:
        Optionally exposes dependencies to mimic spell graph entries.
    """

    def __init__(
        self,
        *,
        spell_id: str,
        spell_name: str = "spell-name",
        dependencies: Optional[List[str]] = None,
    ) -> None:
        """
        Purpose:
            Initialize the stub with identifiers and dependencies.
        Contract:
            dependencies is always set; None represents "no dependencies".
        Args:
            spell_id: Spell identifier for spell_index.current.
            spell_name: Spell name used in diagnostics.
            dependencies: Optional list of dependency ids.
        Returns:
            None.
        """
        self.spell_index = _SpellIndexStub(spell_id)
        self.spell_name = spell_name
        self.dependencies = list(dependencies) if dependencies is not None else None


class _CancelStub:
    """
    Purpose:
        Provide a cancellation stub that raises when set.
    Contract:
        throw_if_set raises RuntimeError when is_set is True.
    """

    def __init__(self, *, is_set: bool) -> None:
        """
        Purpose:
            Initialize the stub with a fixed cancellation state.
        Contract:
            Stores the provided state for is_set queries.
        Args:
            is_set: Whether cancellation is active.
        Returns:
            None.
        """
        self._is_set = is_set
        self.throw_calls = 0

    @property
    def is_set(self) -> bool:
        """
        Purpose:
            Report whether cancellation is active.
        Contract:
            Returns the configured state.
        Returns:
            bool: True when cancellation is active.
        """
        return self._is_set

    def throw_if_set(self) -> None:
        """
        Purpose:
            Raise when cancellation is active.
        Contract:
            Increments throw_calls on each invocation.
        Raises:
            RuntimeError: When cancellation is active.
        """
        self.throw_calls += 1
        if self._is_set:
            raise RuntimeError("cancelled")


def _make_context(
    *,
    spell: _SpellStub,
    cancel_event: Optional[object] = None,
    issues: Optional[List[SpellValidationIssue]] = None,
) -> SpellValidationContext:
    """
    Purpose:
        Build a SpellValidationContext for strategy tests.
    Contract:
        Returns a context with the provided spell and issues list.
    Args:
        spell: Spell under validation.
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
    strategy = SelfDependencyStrategy()
    assert strategy.name == "self_dependency"
    assert "depend" in strategy.description


def test_validate_no_dependencies_is_noop() -> None:
    """
    Purpose:
        Ensure spells with empty dependencies emit no issues.
    Contract:
        No diagnostics are added when dependencies are empty.
    Returns:
        None.
    Raises:
        AssertionError: If issues are added.
    """
    strategy = SelfDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_id="root", dependencies=[])
    context = _make_context(spell=spell, issues=issues)

    strategy.validate(context)

    assert issues == []


def test_validate_dependencies_default_none_is_ok() -> None:
    """
    Purpose:
        Ensure default None dependencies are treated as no dependencies.
    Contract:
        No diagnostics are added when dependencies is None by default.
    Returns:
        None.
    Raises:
        AssertionError: If issues are added.
    """
    strategy = SelfDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_id="root")
    context = _make_context(spell=spell, issues=issues)

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
    strategy = SelfDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(
        spell_id="root",
        dependencies=None,
    )
    context = _make_context(spell=spell, issues=issues)

    strategy.validate(context)

    assert issues == []


def test_validate_no_self_dependency_is_noop() -> None:
    """
    Purpose:
        Ensure dependencies without the root id emit no issues.
    Contract:
        No diagnostics are added when root id is not in dependencies.
    Returns:
        None.
    Raises:
        AssertionError: If issues are added.
    """
    strategy = SelfDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_id="root", dependencies=["other"])
    context = _make_context(spell=spell, issues=issues)

    strategy.validate(context)

    assert issues == []


def test_validate_detects_self_dependency() -> None:
    """
    Purpose:
        Ensure self-dependencies are flagged as errors.
    Contract:
        A self dependency issue is appended with correct details.
    Returns:
        None.
    Raises:
        AssertionError: If issue is missing or malformed.
    """
    strategy = SelfDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_id="root", spell_name="Root", dependencies=["root"])
    context = _make_context(spell=spell, issues=issues)

    strategy.validate(context)

    assert len(issues) == 1
    issue = issues[0]
    assert issue.severity == "error"
    assert issue.code == "SELF_DEPENDENCY"
    assert issue.details["spell_id"] == "root"
    assert "Root" in issue.message


def test_validate_self_dependency_in_list_with_others() -> None:
    """
    Purpose:
        Ensure self dependency is detected among other dependencies.
    Contract:
        A single self dependency issue is emitted.
    Returns:
        None.
    Raises:
        AssertionError: If the issue is missing.
    """
    strategy = SelfDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(
        spell_id="root",
        spell_name="Root",
        dependencies=["other", "root", "another"],
    )
    context = _make_context(spell=spell, issues=issues)

    strategy.validate(context)

    assert len(issues) == 1
    assert issues[0].details["spell_id"] == "root"


def test_validate_duplicate_self_dependency_emits_single_issue() -> None:
    """
    Purpose:
        Ensure duplicate self dependencies still emit a single issue.
    Contract:
        Only one issue is added regardless of duplicate entries.
    Returns:
        None.
    Raises:
        AssertionError: If multiple issues are emitted.
    """
    strategy = SelfDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(
        spell_id="root",
        spell_name="Root",
        dependencies=["root", "root"],
    )
    context = _make_context(spell=spell, issues=issues)

    strategy.validate(context)

    assert len(issues) == 1


def test_validate_appends_to_existing_issues() -> None:
    """
    Purpose:
        Ensure issues are appended to a shared list.
    Contract:
        Existing entries remain and new issue is appended after them.
    Returns:
        None.
    Raises:
        AssertionError: If issues are not appended correctly.
    """
    strategy = SelfDependencyStrategy()
    existing = SpellValidationIssue("warning", "EXISTING", "existing")
    issues: list[SpellValidationIssue] = [existing]
    spell = _SpellStub(spell_id="root", dependencies=["root"])
    context = _make_context(spell=spell, issues=issues)

    strategy.validate(context)

    assert issues[0] is existing
    assert issues[1].code == "SELF_DEPENDENCY"


def test_validate_issue_details_are_exact() -> None:
    """
    Purpose:
        Ensure issue details contain only the expected keys.
    Contract:
        Details include spell_id and nothing else.
    Returns:
        None.
    Raises:
        AssertionError: If detail keys are incorrect.
    """
    strategy = SelfDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_id="root", dependencies=["root"])
    context = _make_context(spell=spell, issues=issues)

    strategy.validate(context)

    assert set(issues[0].details.keys()) == {"spell_id"}


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
    strategy = SelfDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    cancel_event = _CancelStub(is_set=True)
    spell = _SpellStub(spell_id="root", dependencies=["root"])
    context = _make_context(
        spell=spell,
        cancel_event=cancel_event,
        issues=issues,
    )

    with pytest.raises(RuntimeError, match="cancelled"):
        strategy.validate(context)

    assert issues == []
    assert cancel_event.throw_calls == 1


def test_validate_cancel_event_not_set_allows_processing() -> None:
    """
    Purpose:
        Ensure validation proceeds when cancellation is not set.
    Contract:
        Self dependency issue is emitted and throw_if_set is not invoked.
    Returns:
        None.
    Raises:
        AssertionError: If cancellation blocks processing or throws.
    """
    strategy = SelfDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    cancel_event = _CancelStub(is_set=False)
    spell = _SpellStub(spell_id="root", dependencies=["root"])
    context = _make_context(
        spell=spell,
        cancel_event=cancel_event,
        issues=issues,
    )

    strategy.validate(context)

    assert cancel_event.throw_calls == 0
    assert len(issues) == 1
    assert issues[0].code == "SELF_DEPENDENCY"


def test_validate_dependencies_tuple_is_supported() -> None:
    """
    Purpose:
        Ensure tuple dependencies are handled like lists.
    Contract:
        Self dependency in a tuple still emits an issue.
    Returns:
        None.
    Raises:
        AssertionError: If self dependency is not detected.
    """
    strategy = SelfDependencyStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_id="root", dependencies=[])
    spell.dependencies = ("root",)
    context = _make_context(spell=spell, issues=issues)

    strategy.validate(context)

    assert len(issues) == 1
