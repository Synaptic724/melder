import pytest
from typing import List, Optional

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
        Provide a spell stub with the one attribute the strategy reads.
    Contract:
        Exposes spell_name only; the strategy must not read any other spell
        attribute (the retired graph read would fail on this stub).
    """

    def __init__(
        self,
        *,
        spell_name: str = "spell-name",
    ) -> None:
        """
        Purpose:
            Initialize the spell stub.
        Contract:
            Stores the diagnostics name only.
        Args:
            spell_name: Spell name used in diagnostics.
        Returns:
            None.
        """
        self.spell_name = spell_name


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
        A missing resolution frame issue is appended and nothing else.
    Returns:
        None.
    Raises:
        AssertionError: If issue severity or code is incorrect.
    """
    strategy = ResolutionFramePresenceStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_name="Root")
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
        Ensure a missing resolution frame emits exactly one issue.
    Contract:
        Only the missing frame error is emitted; nothing else is inspected.
    Returns:
        None.
    Raises:
        AssertionError: If multiple issues are emitted.
    """
    strategy = ResolutionFramePresenceStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_name="Root")
    context = _make_context(
        spell=spell,
        resolution_frame=None,
        issues=issues,
    )

    strategy.validate(context)

    assert len(issues) == 1
    assert issues[0].code == "MISSING_RESOLUTION_FRAME"


def test_validate_resolution_frame_present_emits_no_issue() -> None:
    """
    Purpose:
        Ensure a present resolution frame yields no issue at all.
    Contract:
        No issues are added when the resolution frame exists; the strategy reads
        nothing else from the spell (the stub carries only a name).
    Returns:
        None.
    Raises:
        AssertionError: If any issues are added.
    """
    strategy = ResolutionFramePresenceStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_name="Root")
    context = _make_context(
        spell=spell,
        resolution_frame=object(),
        issues=issues,
    )

    strategy.validate(context)

    assert issues == []


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
    spell = _SpellStub(spell_name="Root")
    context = _make_context(
        spell=spell,
        resolution_frame=None,
        issues=issues,
    )

    strategy.validate(context)

    assert issues[0] is existing
    assert issues[1].code == "MISSING_RESOLUTION_FRAME"


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
