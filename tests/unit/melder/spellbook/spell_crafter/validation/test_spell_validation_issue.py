from __future__ import annotations

import pytest

from melder.spellbook.spell_crafter.validation.spell_validation_issue import (
    SpellValidationIssue,
)


class _RaisingDict(dict):
    """
    Purpose:
        Dict subclass that raises when clear is called.
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


@pytest.mark.parametrize("severity", ["error", "warning"])
def test_init_accepts_valid_severity(severity: str) -> None:
    """
    Purpose:
        Verify valid severity values are accepted.
    Contract:
        Construction succeeds for "error" and "warning".
    Args:
        severity: Severity string under test.
    Returns:
        None.
    Raises:
        AssertionError: If initialization fails or fields mismatch.
    """
    issue = SpellValidationIssue(
        severity=severity,
        code="CODE",
        message="Message",
    )
    assert issue.severity == severity
    assert issue.code == "CODE"
    assert issue.message == "Message"
    assert issue.source is None


def test_init_rejects_invalid_severity() -> None:
    """
    Purpose:
        Ensure invalid severity values are rejected.
    Contract:
        Raises ValueError for unsupported severity strings.
    Returns:
        None.
    Raises:
        AssertionError: If ValueError is not raised.
    """
    with pytest.raises(ValueError, match="severity"):
        SpellValidationIssue(
            severity="info",
            code="CODE",
            message="Message",
        )


def test_init_rejects_empty_code() -> None:
    """
    Purpose:
        Validate that code must be non-empty.
    Contract:
        Raises ValueError when code is empty.
    Returns:
        None.
    Raises:
        AssertionError: If ValueError is not raised.
    """
    with pytest.raises(ValueError, match="code"):
        SpellValidationIssue(
            severity="error",
            code="",
            message="Message",
        )


def test_init_rejects_empty_message() -> None:
    """
    Purpose:
        Validate that message must be non-empty.
    Contract:
        Raises ValueError when message is empty.
    Returns:
        None.
    Raises:
        AssertionError: If ValueError is not raised.
    """
    with pytest.raises(ValueError, match="message"):
        SpellValidationIssue(
            severity="error",
            code="CODE",
            message="",
        )


def test_details_default_to_empty_dict() -> None:
    """
    Purpose:
        Ensure details defaults to an empty dict when not provided.
    Contract:
        details is an empty dict and mutable.
    Returns:
        None.
    Raises:
        AssertionError: If details is not an empty dict.
    """
    issue = SpellValidationIssue(
        severity="warning",
        code="CODE",
        message="Message",
    )
    assert issue.details == {}
    issue.details["k"] = "v"
    assert issue.details == {"k": "v"}


def test_details_preserve_provided_mapping() -> None:
    """
    Purpose:
        Verify provided details content is preserved.
    Contract:
        details contains the provided key/value pairs.
    Returns:
        None.
    Raises:
        AssertionError: If details content is not preserved.
    """
    details = {"a": 1, "b": 2}
    issue = SpellValidationIssue(
        severity="error",
        code="CODE",
        message="Message",
        details=details,
    )
    assert issue.details == details


def test_init_accepts_source() -> None:
    """
    Purpose:
        Verify source attribution is stored on initialization.
    Contract:
        source is preserved on the created issue.
    Returns:
        None.
    Raises:
        AssertionError: If source is not retained.
    """
    issue = SpellValidationIssue(
        severity="warning",
        code="CODE",
        message="Message",
        source="StrategyName",
    )
    assert issue.source == "StrategyName"


def test_cleanup_clears_details_and_marks_cleaned() -> None:
    """
    Purpose:
        Ensure cleanup clears details and marks the issue as cleaned.
    Contract:
        details is empty and cleaned is True after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup does not clear or mark cleaned.
    """
    issue = SpellValidationIssue(
        severity="error",
        code="CODE",
        message="Message",
        details={"x": "y"},
    )
    issue.cleanup()
    assert issue.details == {}
    assert issue.cleaned is True


def test_cleanup_is_idempotent() -> None:
    """
    Purpose:
        Confirm cleanup is safe to call multiple times.
    Contract:
        Multiple cleanup calls do not raise.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup raises on repeated calls.
    """
    issue = SpellValidationIssue(
        severity="warning",
        code="CODE",
        message="Message",
        details={"x": "y"},
    )
    issue.cleanup()
    issue.cleanup()
    assert issue.cleaned is True


def test_cleanup_swallows_details_clear_errors() -> None:
    """
    Purpose:
        Ensure cleanup suppresses exceptions from details.clear.
    Contract:
        cleanup completes and marks cleaned even if clear raises.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup raises or cleaned flag is false.
    """
    issue = SpellValidationIssue(
        severity="error",
        code="CODE",
        message="Message",
        details=_RaisingDict({"x": "y"}),
    )
    issue.cleanup()
    assert issue.cleaned is True


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
    issue = SpellValidationIssue(
        severity="warning",
        code="CODE",
        message="Message",
    )
    issue.cleanup()
    with pytest.raises(RuntimeError):
        issue.check_cleaned()
