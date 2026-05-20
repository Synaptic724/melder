import pytest
from typing import Optional, List

from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import (
    SpellValidationContext,
)
from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import (
    SpellValidationIssue,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.resolution_frame_presence_strategy import (
    ResolutionFramePresenceStrategy,
)


class _SpellStub:
    """
    Purpose:
        Provide a spell stub with name and dependency graph attribute.
    Contract:
        Exposes spell_name and optional dependency_graph.
    """

    def __init__(
        self,
        *,
        spell_name: str = "spell-name",
        dependency_graph: Optional[object] = None,
    ) -> None:
        """
        Purpose:
            Initialize the spell stub.
        Contract:
            dependency_graph is always set; None represents "no graph".
        Args:
            spell_name: Spell name used in diagnostics.
            dependency_graph: Dependency graph object or None.
        Returns:
            None.
        """
        self.spell_name = spell_name
        self.dependency_graph = dependency_graph


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
    resolution_frame: Optional[object],
    cancel_event: Optional[object] = None,
    issues: Optional[List[SpellValidationIssue]] = None,
) -> SpellValidationContext:
    """
    Purpose:
        Build a SpellValidationContext for strategy tests.
    Contract:
        Returns a context with the provided spell, resolution frame, and issues list.
    Args:
        spell: Spell under validation.
        resolution_frame: Resolution frame or None.
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
        resolution_frame=resolution_frame,
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
    strategy = ResolutionFramePresenceStrategy()
    assert strategy.name == "resolution_frame_presence"
    assert "resolution frame" in strategy.description.lower()


def test_validate_missing_resolution_frame_emits_error() -> None:
    """
    Purpose:
        Ensure missing resolution frame emits an error issue.
    Contract:
        A missing resolution frame issue is appended and warning is not emitted.
    Returns:
        None.
    Raises:
        AssertionError: If issue severity or code is incorrect.
    """
    strategy = ResolutionFramePresenceStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_name="Root", dependency_graph="graph")
    context = _make_context(
        spell=spell,
        resolution_frame=None,
        issues=issues,
    )

    strategy.validate(context)

    assert len(issues) == 1
    issue = issues[0]
    assert issue.severity == "error"
    assert issue.code == "MISSING_RESOLUTION_FRAME"
    assert "Root" in issue.message
    assert issue.details == {}


def test_validate_missing_resolution_frame_returns_early() -> None:
    """
    Purpose:
        Ensure missing resolution frame prevents dependency graph warning.
    Contract:
        Only the missing frame error is emitted even if graph is missing.
    Returns:
        None.
    Raises:
        AssertionError: If multiple issues are emitted.
    """
    strategy = ResolutionFramePresenceStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_name="Root", dependency_graph=None)
    context = _make_context(
        spell=spell,
        resolution_frame=None,
        issues=issues,
    )

    strategy.validate(context)

    assert len(issues) == 1
    assert issues[0].code == "MISSING_RESOLUTION_FRAME"


def test_validate_missing_dependency_graph_emits_warning() -> None:
    """
    Purpose:
        Ensure missing dependency graph emits a warning when frame exists.
    Contract:
        A missing dependency graph warning is appended when frame is present.
    Returns:
        None.
    Raises:
        AssertionError: If warning is not emitted.
    """
    strategy = ResolutionFramePresenceStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_name="Root", dependency_graph=None)
    context = _make_context(
        spell=spell,
        resolution_frame=object(),
        issues=issues,
    )

    strategy.validate(context)

    assert len(issues) == 1
    issue = issues[0]
    assert issue.severity == "warning"
    assert issue.code == "MISSING_DEPENDENCY_GRAPH"
    assert issue.details == {}


def test_validate_dependency_graph_present_emits_no_issue() -> None:
    """
    Purpose:
        Ensure no warning is emitted when graph is present.
    Contract:
        No issues are added when resolution frame and graph are present.
    Returns:
        None.
    Raises:
        AssertionError: If any issues are added.
    """
    strategy = ResolutionFramePresenceStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_name="Root", dependency_graph=object())
    context = _make_context(
        spell=spell,
        resolution_frame=object(),
        issues=issues,
    )

    strategy.validate(context)

    assert issues == []


def test_validate_falsey_dependency_graph_is_treated_as_present() -> None:
    """
    Purpose:
        Ensure falsey non-None dependency_graph does not trigger a warning.
    Contract:
        No issues are added when dependency_graph is an empty container.
    Returns:
        None.
    Raises:
        AssertionError: If any issues are added.
    """
    strategy = ResolutionFramePresenceStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_name="Root", dependency_graph=[])
    context = _make_context(
        spell=spell,
        resolution_frame=object(),
        issues=issues,
    )

    strategy.validate(context)

    assert issues == []


def test_validate_dependency_graph_none_emits_warning() -> None:
    """
    Purpose:
        Ensure dependency_graph None triggers a warning.
    Contract:
        The missing dependency graph warning is appended when graph is None.
    Returns:
        None.
    Raises:
        AssertionError: If warning is not emitted.
    """
    strategy = ResolutionFramePresenceStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_name="Root", dependency_graph=None)
    context = _make_context(
        spell=spell,
        resolution_frame=object(),
        issues=issues,
    )

    strategy.validate(context)

    assert len(issues) == 1
    assert issues[0].code == "MISSING_DEPENDENCY_GRAPH"


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
    strategy = ResolutionFramePresenceStrategy()
    existing = SpellValidationIssue("warning", "EXISTING", "existing")
    issues: list[SpellValidationIssue] = [existing]
    spell = _SpellStub(spell_name="Root", dependency_graph=None)
    context = _make_context(
        spell=spell,
        resolution_frame=object(),
        issues=issues,
    )

    strategy.validate(context)

    assert issues[0] is existing
    assert issues[1].code == "MISSING_DEPENDENCY_GRAPH"


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
    strategy = ResolutionFramePresenceStrategy()
    issues: list[SpellValidationIssue] = []
    cancel_event = _CancelStub(is_set=True)
    spell = _SpellStub(spell_name="Root")
    context = _make_context(
        spell=spell,
        resolution_frame=None,
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
        Missing resolution frame error is emitted and throw_if_set is not invoked.
    Returns:
        None.
    Raises:
        AssertionError: If cancellation blocks processing or throws.
    """
    strategy = ResolutionFramePresenceStrategy()
    issues: list[SpellValidationIssue] = []
    cancel_event = _CancelStub(is_set=False)
    spell = _SpellStub(spell_name="Root")
    context = _make_context(
        spell=spell,
        resolution_frame=None,
        cancel_event=cancel_event,
        issues=issues,
    )

    strategy.validate(context)

    assert cancel_event.throw_calls == 0
    assert len(issues) == 1
    assert issues[0].code == "MISSING_RESOLUTION_FRAME"
