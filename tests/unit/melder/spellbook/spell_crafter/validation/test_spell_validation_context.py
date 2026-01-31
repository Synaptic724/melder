import pytest

from melder.spellbook.spell_crafter.validation.spell_validation_context import (
    SpellValidationContext,
)
from melder.utilities.general_base.cleanable import Cleanable


class _CleanableStub(Cleanable):
    """
    Purpose:
        Provide a Cleanable artifact stub for cleanup behavior tests.
    Contract:
        Tracks cleanup calls and can raise when configured.
    """

    def __init__(self, *, raise_on_cleanup: bool = False) -> None:
        """
        Purpose:
            Initialize the stub with optional failure behavior.
        Contract:
            Stores the raise_on_cleanup flag and resets the call counter.
        Args:
            raise_on_cleanup: Whether cleanup should raise.
        Returns:
            None.
        """
        super().__init__()
        self.cleanup_calls = 0
        self._raise_on_cleanup = raise_on_cleanup

    def cleanup(self) -> None:
        """
        Purpose:
            Record cleanup calls and optionally raise.
        Contract:
            Increments cleanup_calls on each invocation.
        Raises:
            RuntimeError: When configured to raise.
        """
        self.cleanup_calls += 1
        if self._raise_on_cleanup:
            raise RuntimeError("cleanup boom")
        self._cleaned = True

    async def async_cleanup(self) -> None:
        """
        Purpose:
            Provide the async cleanup hook required by Cleanable.
        Contract:
            Not used in these tests.
        """
        raise NotImplementedError("async cleanup not implemented in test stub")


def test_init_requires_spell() -> None:
    """
    Purpose:
        Ensure a spell is required for initialization.
    Contract:
        Raises ValueError when spell is None.
    Returns:
        None.
    Raises:
        AssertionError: If ValueError is not raised.
    """
    with pytest.raises(ValueError, match="spell"):
        SpellValidationContext(
            spell=None,
            spellbook=None,
            requirements=None,
            symbolic_graph=None,
            resolution_frame=None,
            cancel_event=None,
            issues=[],
        )


def test_init_requires_issues_list() -> None:
    """
    Purpose:
        Ensure an issues list is required for initialization.
    Contract:
        Raises ValueError when issues is None.
    Returns:
        None.
    Raises:
        AssertionError: If ValueError is not raised.
    """
    with pytest.raises(ValueError, match="issues"):
        SpellValidationContext(
            spell=object(),
            spellbook=None,
            requirements=None,
            symbolic_graph=None,
            resolution_frame=None,
            cancel_event=None,
            issues=None,
        )


def test_init_sets_fields() -> None:
    """
    Purpose:
        Verify initialization stores the provided fields.
    Contract:
        All attributes match the provided arguments.
    Returns:
        None.
    Raises:
        AssertionError: If any attribute is not set correctly.
    """
    spell = object()
    spellbook = object()
    requirements = object()
    symbolic_graph = object()
    resolution_frame = object()
    cancel_event = object()
    issues: list[object] = []

    context = SpellValidationContext(
        spell=spell,
        spellbook=spellbook,
        requirements=requirements,
        symbolic_graph=symbolic_graph,
        resolution_frame=resolution_frame,
        cancel_event=cancel_event,
        issues=issues,
    )

    assert context.spell is spell
    assert context.spellbook is spellbook
    assert context.requirements is requirements
    assert context.symbolic_graph is symbolic_graph
    assert context.resolution_frame is resolution_frame
    assert context.cancel_event is cancel_event
    assert context.issues is issues


def test_issues_list_shared_and_not_cleared_on_cleanup() -> None:
    """
    Purpose:
        Ensure the issues list is shared and not cleared during cleanup.
    Contract:
        The original list remains intact after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If the issues list is mutated.
    """
    issues: list[object] = ["keep"]
    context = SpellValidationContext(
        spell=object(),
        spellbook=None,
        requirements=None,
        symbolic_graph=None,
        resolution_frame=None,
        cancel_event=None,
        issues=issues,
    )
    assert context.issues is issues

    context.cleanup()

    assert issues == ["keep"]
    assert context.issues is None


def test_cleanup_marks_cleaned_and_drops_references() -> None:
    """
    Purpose:
        Validate cleanup nulls references and marks the context as cleaned.
    Contract:
        All stored references are set to None after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If references are not cleared or cleaned flag is false.
    """
    context = SpellValidationContext(
        spell=object(),
        spellbook=object(),
        requirements=object(),
        symbolic_graph=object(),
        resolution_frame=object(),
        cancel_event=object(),
        issues=[],
    )

    context.cleanup()

    assert context.cleaned is True
    assert context.spell is None
    assert context.spellbook is None
    assert context.requirements is None
    assert context.symbolic_graph is None
    assert context.resolution_frame is None
    assert context.cancel_event is None
    assert context.issues is None
    with pytest.raises(RuntimeError):
        context.check_cleaned()

def test_cleanup_calls_artifact_cleanup() -> None:
    """
    Purpose:
        Ensure Cleanable artifacts are cleaned when present.
    Contract:
        Each artifact cleanup is called exactly once.
    Returns:
        None.
    Raises:
        AssertionError: If artifact cleanup is not invoked.
    """
    requirements = _CleanableStub()
    symbolic_graph = _CleanableStub()
    resolution_frame = _CleanableStub()
    context = SpellValidationContext(
        spell=object(),
        spellbook=None,
        requirements=requirements,
        symbolic_graph=symbolic_graph,
        resolution_frame=resolution_frame,
        cancel_event=None,
        issues=[],
    )

    context.cleanup()

    assert requirements.cleanup_calls == 1
    assert symbolic_graph.cleanup_calls == 1
    assert resolution_frame.cleanup_calls == 1


def test_cleanup_skips_artifact_cleanup_when_disabled() -> None:
    """
    Purpose:
        Ensure artifact cleanup can be disabled for deferred teardown.
    Contract:
        Cleanable artifacts are not cleaned when cleanup_artifacts is False.
    Returns:
        None.
    Raises:
        AssertionError: If artifact cleanup is invoked when disabled.
    """
    requirements = _CleanableStub()
    symbolic_graph = _CleanableStub()
    resolution_frame = _CleanableStub()
    context = SpellValidationContext(
        spell=object(),
        spellbook=None,
        requirements=requirements,
        symbolic_graph=symbolic_graph,
        resolution_frame=resolution_frame,
        cancel_event=None,
        issues=[],
        cleanup_artifacts=False,
    )

    context.cleanup()

    assert requirements.cleanup_calls == 0
    assert symbolic_graph.cleanup_calls == 0
    assert resolution_frame.cleanup_calls == 0


def test_cleanup_swallows_artifact_cleanup_errors() -> None:
    """
    Purpose:
        Confirm artifact cleanup exceptions are swallowed.
    Contract:
        cleanup completes even if artifact cleanup raises.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup raises or cleaned flag is not set.
    """
    requirements = _CleanableStub(raise_on_cleanup=True)
    context = SpellValidationContext(
        spell=object(),
        spellbook=None,
        requirements=requirements,
        symbolic_graph=None,
        resolution_frame=None,
        cancel_event=None,
        issues=[],
    )

    context.cleanup()

    assert context.cleaned is True


def test_cleanup_is_idempotent() -> None:
    """
    Purpose:
        Ensure cleanup is safe to call multiple times.
    Contract:
        Artifact cleanup runs once and no errors are raised on second call.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup calls are not idempotent.
    """
    requirements = _CleanableStub()
    context = SpellValidationContext(
        spell=object(),
        spellbook=None,
        requirements=requirements,
        symbolic_graph=None,
        resolution_frame=None,
        cancel_event=None,
        issues=[],
    )

    context.cleanup()
    context.cleanup()

    assert requirements.cleanup_calls == 1
