from __future__ import annotations

import pytest

from melder.spellbook.spell_crafter.validation.spell_validation_issue import (
    SpellValidationIssue,
)
from melder.spellbook.spell_crafter.validation.spell_validation_result import (
    SpellValidationResult,
)
from melder.utilities.general_base.cleanable import Cleanable


class _IssueStub(Cleanable):
    """
    Purpose:
        Provide a Cleanable issue stub for cleanup behavior tests.
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


class _RaisingList(list):
    """
    Purpose:
        List subclass that raises when clear is called.
    Contract:
        clear always raises RuntimeError.
    """

    def clear(self) -> None:
        """
        Purpose:
            Raise to simulate cleanup failure.
        Contract:
            Always raises RuntimeError.
        Raises:
            RuntimeError: Unconditional error for testing.
        """
        raise RuntimeError("clear failed")


def test_init_requires_spell_id() -> None:
    """
    Purpose:
        Ensure spell_id is required for initialization.
    Contract:
        Raises ValueError when spell_id is empty.
    Returns:
        None.
    Raises:
        AssertionError: If ValueError is not raised.
    """
    with pytest.raises(ValueError, match="spell_id"):
        SpellValidationResult(spell_id="", spell_name="name")


def test_init_requires_spell_name() -> None:
    """
    Purpose:
        Ensure spell_name is required for initialization.
    Contract:
        Raises ValueError when spell_name is empty.
    Returns:
        None.
    Raises:
        AssertionError: If ValueError is not raised.
    """
    with pytest.raises(ValueError, match="spell_name"):
        SpellValidationResult(spell_id="id", spell_name="")


def test_init_defaults_issues_to_empty_list() -> None:
    """
    Purpose:
        Verify issues defaults to an empty list when not provided.
    Contract:
        issues is an empty list and has_errors/has_warnings are False.
    Returns:
        None.
    Raises:
        AssertionError: If defaults are incorrect.
    """
    result = SpellValidationResult(spell_id="id", spell_name="name")
    assert result.issues == []
    assert result.has_errors is False
    assert result.has_warnings is False


def test_init_uses_provided_issues_list() -> None:
    """
    Purpose:
        Ensure a provided issues list is used as-is.
    Contract:
        issues list is the same object and contents are preserved.
    Returns:
        None.
    Raises:
        AssertionError: If issues list is copied or altered.
    """
    issues = [SpellValidationIssue("warning", "W", "warn")]
    result = SpellValidationResult(spell_id="id", spell_name="name", issues=issues)
    assert result.issues is issues
    assert result.issues == issues


def test_has_errors_true_when_any_error_present() -> None:
    """
    Purpose:
        Validate has_errors reflects presence of error issues.
    Contract:
        has_errors is True when any issue severity is "error".
    Returns:
        None.
    Raises:
        AssertionError: If has_errors is incorrect.
    """
    issues = [
        SpellValidationIssue("warning", "W", "warn"),
        SpellValidationIssue("error", "E", "err"),
    ]
    result = SpellValidationResult(spell_id="id", spell_name="name", issues=issues)
    assert result.has_errors is True


def test_has_warnings_true_when_any_warning_present() -> None:
    """
    Purpose:
        Validate has_warnings reflects presence of warning issues.
    Contract:
        has_warnings is True when any issue severity is "warning".
    Returns:
        None.
    Raises:
        AssertionError: If has_warnings is incorrect.
    """
    issues = [
        SpellValidationIssue("warning", "W", "warn"),
        SpellValidationIssue("error", "E", "err"),
    ]
    result = SpellValidationResult(spell_id="id", spell_name="name", issues=issues)
    assert result.has_warnings is True


def test_has_warnings_false_when_no_warnings() -> None:
    """
    Purpose:
        Ensure has_warnings is False when no warning issues exist.
    Contract:
        has_warnings is False for error-only issue sets.
    Returns:
        None.
    Raises:
        AssertionError: If has_warnings is incorrect.
    """
    issues = [SpellValidationIssue("error", "E", "err")]
    result = SpellValidationResult(spell_id="id", spell_name="name", issues=issues)
    assert result.has_warnings is False


def test_cleanup_clears_issues_and_marks_cleaned() -> None:
    """
    Purpose:
        Ensure cleanup clears issues and marks the result as cleaned.
    Contract:
        issues list is empty and cleaned is True after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup does not clear or mark cleaned.
    """
    issues = [SpellValidationIssue("error", "E", "err")]
    result = SpellValidationResult(spell_id="id", spell_name="name", issues=issues)
    result.cleanup()
    assert result.issues == []
    assert result.cleaned is True


def test_cleanup_calls_issue_cleanup() -> None:
    """
    Purpose:
        Verify cleanup invokes cleanup on Cleanable issues.
    Contract:
        Each Cleanable issue cleanup is called once.
    Returns:
        None.
    Raises:
        AssertionError: If issue cleanup is not invoked.
    """
    issue = _IssueStub()
    result = SpellValidationResult(spell_id="id", spell_name="name", issues=[issue])
    result.cleanup()
    assert issue.cleanup_calls == 1


def test_cleanup_swallows_issue_cleanup_errors() -> None:
    """
    Purpose:
        Ensure cleanup suppresses exceptions from issue cleanup.
    Contract:
        cleanup completes and marks cleaned even if issue cleanup raises.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup raises or cleaned flag is false.
    """
    issue = _IssueStub(raise_on_cleanup=True)
    result = SpellValidationResult(spell_id="id", spell_name="name", issues=[issue])
    result.cleanup()
    assert result.cleaned is True


def test_cleanup_swallows_issue_list_clear_errors() -> None:
    """
    Purpose:
        Confirm cleanup suppresses errors raised when clearing issues list.
    Contract:
        cleanup completes and marks cleaned even if clear raises.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup raises or cleaned flag is false.
    """
    issues = _RaisingList([SpellValidationIssue("error", "E", "err")])
    result = SpellValidationResult(spell_id="id", spell_name="name", issues=issues)
    result.cleanup()
    assert result.cleaned is True


def test_check_cleaned_raises_after_cleanup() -> None:
    """
    Purpose:
        Validate check_cleaned raises once cleanup has run.
    Contract:
        check_cleaned raises RuntimeError after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If check_cleaned does not raise.
    """
    result = SpellValidationResult(spell_id="id", spell_name="name")
    result.cleanup()
    with pytest.raises(RuntimeError):
        result.check_cleaned()
