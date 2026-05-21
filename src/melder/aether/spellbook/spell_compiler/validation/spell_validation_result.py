from typing import Optional, List, ClassVar

from mypy_extensions import mypyc_attr

# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import (
    SpellValidationIssue,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
@mypyc_attr(native_class=True)
class SpellValidationResult(Cleanable):
    """
    Aggregate validation result for a single spell.

    Attributes
    ----------
    spell_id:
        Versioned identity of the spell (typically ``SpellIndex.current``).
    spell_name:
        Human-readable spell name (usually the underlying callable's __name__).
    issues:
        All issues (errors + warnings) are discovered by the validation strategies.
    errors:
        Read-only filtered view of "issues" containing only error-severity
        entries.
    warnings:
        Read-only filtered view of "issues" containing only warning-severity
        entries.

    Contract:
    - Represents the final aggregate output of one validation run for one
      spell/version.
    - Preserves both error and warning issues in one ordered list.
    - Exposes filtered `errors` and `warnings` views derived from the canonical
      issue list so downstream code can consume split severities without
      duplicating the stored state.
    - Convenience properties expose whether any error/warning class is present
      without forcing callers to rescan the issue list manually.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "spell_id",
        "spell_name",
        "issues",
    ]
    __deletable__ = [
        "spell_id",
        "spell_name",
        "issues",
    ]

    def __init__(
            self,
            spell_id: str,
            spell_name: str,
            issues: Optional[List['SpellValidationIssue']] = None,
    ) -> None:
        """
        Initialize one aggregate spell validation result.

        Args:
            spell_id: Validated spell/version id.
            spell_name: Human-readable validated spell name.
            issues: Optional prebuilt list of validation issues.
        Contract:
            - `spell_id` and `spell_name` are required.
            - Stores the supplied issue list as the owned result list when
              provided; otherwise starts empty.
        Raises:
            ValueError: If `spell_id` or `spell_name` is empty.
        """
        super().__init__()
        if not spell_id:
            raise ValueError("spell_id cannot be empty.")
        if not spell_name:
            raise ValueError("spell_name cannot be empty.")

        self.spell_id: str = spell_id
        self.spell_name: str = spell_name
        self.issues: List['SpellValidationIssue'] = issues or []

    @property
    def errors(self) -> List['SpellValidationIssue']:
        """
        Return a filtered list of error-severity validation issues.

        Contract:
            - Derives the view from the canonical `issues` list each time.
            - Returns a detached list so callers cannot mutate the owned result
              storage through the split-severity view.
        """
        return [
            issue
            for issue in self.issues
            if issue.severity == "error"
        ]

    @property
    def warnings(self) -> List['SpellValidationIssue']:
        """
        Return a filtered list of warning-severity validation issues.

        Contract:
            - Derives the view from the canonical `issues` list each time.
            - Returns a detached list so callers cannot mutate the owned result
              storage through the split-severity view.
        """
        return [
            issue
            for issue in self.issues
            if issue.severity == "warning"
        ]

    @property
    def has_errors(self) -> bool:
        """
        Return True if any issue is an error.

        Contract:
            Scans the current issue list and returns a boolean summary only; it
            does not mutate or filter the issues.
        """
        return bool(self.errors)

    @property
    def has_warnings(self) -> bool:
        """
        Return True if any issue is a warning.

        Contract:
            Scans the current issue list and returns a boolean summary only; it
            does not mutate or filter the issues.
        """
        return bool(self.warnings)

    def cleanup(self) -> None:
        """
        Deterministically tear down this result and its issues.

        This:
        - Calls "cleanup()" on each issue that supports it.
        - Clears the issues list.
        """
        if self._cleaned:
            return

        for issue in self.issues:
            if isinstance(issue, Cleanable):
                try:
                    issue.cleanup()
                except Exception:
                    # Diagnostics cleanup must never break callers.
                    pass

        try:
            self.issues.clear()
        except Exception:
            pass

        self._cleaned = True
