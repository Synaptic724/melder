from __future__ import annotations

import pytest

from melder.spellbook.spell_crafter.validation.strategies.spell_validation_strategy import (
    SpellValidationStrategy,
)


class _ContextStub:
    """
    Purpose:
        Provide a minimal context object for validate tests.
    Contract:
        Acts as a stable identity to verify passing through validate.
    """

    def __init__(self, tag: str) -> None:
        """
        Purpose:
            Initialize the stub with a tag for identification.
        Contract:
            Stores the tag without validation.
        Args:
            tag: Identifier for this context instance.
        Returns:
            None.
        """
        self.tag = tag


class _RecordingStrategy(SpellValidationStrategy):
    """
    Purpose:
        Concrete strategy that records validate calls and contexts.
    Contract:
        validate increments calls and records each context.
    """

    def __init__(self, *, name: str = "recording", description: str = "") -> None:
        """
        Purpose:
            Initialize the strategy with name metadata.
        Contract:
            Sets counters and stores base class properties.
        Args:
            name: Strategy name string.
            description: Strategy description string.
        Returns:
            None.
        """
        super().__init__(name=name, description=description)
        self.calls = 0
        self.contexts: list[object] = []

    def validate(self, context: object) -> None:
        """
        Purpose:
            Record each validation call.
        Contract:
            Calls check_cleaned, then records the context.
        Args:
            context: Context object provided by the caller.
        Returns:
            None.
        Raises:
            RuntimeError: If the strategy has been cleaned.
        """
        self.check_cleaned()
        self.calls += 1
        self.contexts.append(context)


def test_init_sets_name_and_description() -> None:
    """
    Purpose:
        Verify strategy metadata is initialized.
    Contract:
        Name and description match constructor inputs.
    Returns:
        None.
    Raises:
        AssertionError: If metadata is incorrect.
    """
    strategy = SpellValidationStrategy(name="alpha", description="desc")
    assert strategy.name == "alpha"
    assert strategy.description == "desc"


def test_init_default_description_is_empty() -> None:
    """
    Purpose:
        Ensure description defaults to an empty string.
    Contract:
        Description is empty when not provided.
    Returns:
        None.
    Raises:
        AssertionError: If description is not empty.
    """
    strategy = SpellValidationStrategy(name="alpha")
    assert strategy.description == ""


def test_init_requires_nonempty_name() -> None:
    """
    Purpose:
        Ensure empty names are rejected.
    Contract:
        ValueError is raised when name is empty.
    Returns:
        None.
    Raises:
        AssertionError: If ValueError is not raised.
    """
    with pytest.raises(ValueError, match="name"):
        SpellValidationStrategy(name="")


def test_cleaned_flags_default_false() -> None:
    """
    Purpose:
        Ensure new strategies start in a non-cleaned state.
    Contract:
        cleaned and is_cleaned are False after initialization.
    Returns:
        None.
    Raises:
        AssertionError: If cleaned flags are True initially.
    """
    strategy = SpellValidationStrategy(name="alpha")
    assert strategy.cleaned is False
    assert strategy.is_cleaned is False


def test_cleanup_marks_cleaned() -> None:
    """
    Purpose:
        Ensure cleanup marks the strategy as cleaned.
    Contract:
        cleaned becomes True after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If cleaned is not True after cleanup.
    """
    strategy = SpellValidationStrategy(name="alpha")
    strategy.cleanup()
    assert strategy.cleaned is True


def test_cleanup_is_idempotent() -> None:
    """
    Purpose:
        Ensure cleanup can be called multiple times safely.
    Contract:
        Subsequent cleanup calls do not raise and keep cleaned True.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup is not idempotent.
    """
    strategy = SpellValidationStrategy(name="alpha")
    strategy.cleanup()
    strategy.cleanup()
    assert strategy.cleaned is True


def test_check_cleaned_raises_after_cleanup() -> None:
    """
    Purpose:
        Ensure check_cleaned raises after cleanup.
    Contract:
        RuntimeError is raised when calling check_cleaned on cleaned strategy.
    Returns:
        None.
    Raises:
        AssertionError: If RuntimeError is not raised.
    """
    strategy = SpellValidationStrategy(name="alpha")
    strategy.cleanup()
    with pytest.raises(RuntimeError, match="cleaned"):
        strategy.check_cleaned()


def test_properties_accessible_after_cleanup() -> None:
    """
    Purpose:
        Ensure name and description remain accessible after cleanup.
    Contract:
        name and description return the original values post-cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If properties change or raise.
    """
    strategy = SpellValidationStrategy(name="alpha", description="desc")
    strategy.cleanup()
    assert strategy.name == "alpha"
    assert strategy.description == "desc"


def test_validate_on_base_raises_not_implemented() -> None:
    """
    Purpose:
        Ensure the base validate method is not usable directly.
    Contract:
        NotImplementedError is raised when validate is called on base class.
    Returns:
        None.
    Raises:
        AssertionError: If NotImplementedError is not raised.
    """
    strategy = SpellValidationStrategy(name="alpha")
    with pytest.raises(NotImplementedError, match="SpellValidationStrategy.validate"):
        strategy.validate(_ContextStub("ctx"))


def test_subclass_validate_records_context() -> None:
    """
    Purpose:
        Verify subclass validate records calls and contexts.
    Contract:
        Calls count increments and contexts are stored in order.
    Returns:
        None.
    Raises:
        AssertionError: If call tracking is incorrect.
    """
    strategy = _RecordingStrategy()
    context = _ContextStub("ctx")
    strategy.validate(context)
    assert strategy.calls == 1
    assert strategy.contexts == [context]


def test_subclass_validate_multiple_calls() -> None:
    """
    Purpose:
        Ensure multiple validate calls are tracked.
    Contract:
        Calls count increments for each validate invocation.
    Returns:
        None.
    Raises:
        AssertionError: If call tracking is incorrect.
    """
    strategy = _RecordingStrategy()
    strategy.validate(_ContextStub("one"))
    strategy.validate(_ContextStub("two"))
    assert strategy.calls == 2
    assert [ctx.tag for ctx in strategy.contexts] == ["one", "two"]


def test_subclass_validate_raises_after_cleanup() -> None:
    """
    Purpose:
        Ensure subclasses honoring check_cleaned raise after cleanup.
    Contract:
        RuntimeError is raised when validate is called on a cleaned strategy.
    Returns:
        None.
    Raises:
        AssertionError: If RuntimeError is not raised.
    """
    strategy = _RecordingStrategy()
    strategy.cleanup()
    with pytest.raises(RuntimeError, match="cleaned"):
        strategy.validate(_ContextStub("ctx"))
