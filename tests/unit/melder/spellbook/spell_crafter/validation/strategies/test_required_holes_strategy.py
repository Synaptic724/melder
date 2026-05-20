from typing import Iterable, List, Optional

import pytest

from melder.aether.spellbook.spell_compiler.validation.spell_validation_context import (
    SpellValidationContext,
)
from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import (
    SpellValidationIssue,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.required_holes_strategy import (
    RequiredHolesStrategy,
)


class _ParamStub:
    """
    Purpose:
        Provide a parameter stub for required hole reporting.
    Contract:
        Exposes name, position, and annotation attributes.
    """

    def __init__(self, name: str, position: int, annotation: object) -> None:
        """
        Purpose:
            Initialize the parameter stub fields.
        Contract:
            Stores the provided values without validation.
        Args:
            name: Parameter name string.
            position: Parameter position index.
            annotation: Parameter annotation object.
        Returns:
            None.
        """
        self.name = name
        self.position = position
        self.annotation = annotation


class _RequirementsStub:
    """
    Purpose:
        Provide a requirements stub with required hole iteration.
    Contract:
        Returns configured required holes from iter_required_holes.
    """

    def __init__(self, required_holes: list[_ParamStub]) -> None:
        """
        Purpose:
            Initialize the stub with required hole parameters.
        Contract:
            Stores the provided required holes list.
        Args:
            required_holes: Parameters considered required holes.
        Returns:
            None.
        """
        self._required_holes = list(required_holes)
        self.has_required_holes_calls = 0
        self.iter_required_holes_calls = 0

    def has_required_holes(self) -> bool:
        """
        Purpose:
            Report whether any required holes exist.
        Contract:
            Returns True when the required hole list is non-empty.
        Returns:
            bool: True if required holes exist.
        """
        self.has_required_holes_calls += 1
        return bool(self._required_holes)

    def iter_required_holes(self) -> Iterable[_ParamStub]:
        """
        Purpose:
            Yield required hole parameters.
        Contract:
            Iterates over the configured required holes list.
        Returns:
            Iterable[_ParamStub]: Required hole parameters.
        """
        self.iter_required_holes_calls += 1
        return iter(self._required_holes)


class _SpellStub:
    """
    Purpose:
        Provide a spell stub with a name for diagnostics.
    Contract:
        Exposes spell_name for issue messages.
    """

    def __init__(self, spell_name: str = "spell-name") -> None:
        """
        Purpose:
            Initialize the spell stub with a name.
        Contract:
            Stores spell_name without validation.
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
    requirements: Optional[_RequirementsStub],
    cancel_event: Optional[object] = None,
    issues: Optional[List[SpellValidationIssue]] = None,
) -> SpellValidationContext:
    """
    Purpose:
        Build a SpellValidationContext for strategy tests.
    Contract:
        Returns a context with the provided spell, requirements, and issues list.
    Args:
        spell: Spell under validation.
        requirements: Requirements stub or None.
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
        requirements=requirements,
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
    strategy = RequiredHolesStrategy()
    assert strategy.name == "required_holes"
    assert "defaults" in strategy.description


def test_validate_without_requirements_is_noop() -> None:
    """
    Purpose:
        Ensure validation exits when requirements are missing.
    Contract:
        No issues are added without requirements.
    Returns:
        None.
    Raises:
        AssertionError: If issues are added.
    """
    strategy = RequiredHolesStrategy()
    issues: list[SpellValidationIssue] = []
    context = _make_context(
        spell=_SpellStub(),
        requirements=None,
        issues=issues,
    )

    strategy.validate(context)

    assert issues == []


def test_validate_no_required_holes_is_noop() -> None:
    """
    Purpose:
        Ensure no issues are emitted when there are no required holes.
    Contract:
        has_required_holes is consulted and iter_required_holes is not called.
    Returns:
        None.
    Raises:
        AssertionError: If issues are added or iter_required_holes is called.
    """
    strategy = RequiredHolesStrategy()
    issues: list[SpellValidationIssue] = []
    requirements = _RequirementsStub(required_holes=[])
    context = _make_context(
        spell=_SpellStub(),
        requirements=requirements,
        issues=issues,
    )

    strategy.validate(context)

    assert issues == []
    assert requirements.has_required_holes_calls == 1
    assert requirements.iter_required_holes_calls == 0


def test_validate_emits_issue_for_each_required_hole() -> None:
    """
    Purpose:
        Ensure each required hole produces a warning issue.
    Contract:
        One issue per required hole with parameter metadata is added.
    Returns:
        None.
    Raises:
        AssertionError: If issues are missing or malformed.
    """
    strategy = RequiredHolesStrategy()
    issues: list[SpellValidationIssue] = []
    params = [
        _ParamStub("a", 0, "int"),
        _ParamStub("b", 1, None),
    ]
    requirements = _RequirementsStub(required_holes=params)
    spell = _SpellStub(spell_name="Root")
    context = _make_context(
        spell=spell,
        requirements=requirements,
        issues=issues,
    )

    strategy.validate(context)

    assert len(issues) == 2
    assert {issue.details["parameter_name"] for issue in issues} == {"a", "b"}
    assert {issue.details["position"] for issue in issues} == {0, 1}
    assert any(issue.details["annotation"] == "int" for issue in issues)
    assert any(issue.details["annotation"] is None for issue in issues)
    assert all(issue.severity == "warning" for issue in issues)
    assert all(issue.code == "REQUIRED_HOLE" for issue in issues)
    assert all("Root" in issue.message for issue in issues)
    assert requirements.iter_required_holes_calls == 1


def test_validate_appends_to_existing_issue_list() -> None:
    """
    Purpose:
        Ensure issues are appended to the provided shared list.
    Contract:
        Existing entries remain and new issues are appended after them.
    Returns:
        None.
    Raises:
        AssertionError: If issues are not appended correctly.
    """
    strategy = RequiredHolesStrategy()
    existing = SpellValidationIssue("warning", "EXISTING", "existing")
    issues: list[SpellValidationIssue] = [existing]
    requirements = _RequirementsStub(
        required_holes=[_ParamStub("a", 0, int), _ParamStub("b", 1, str)]
    )
    context = _make_context(
        spell=_SpellStub(spell_name="Root"),
        requirements=requirements,
        issues=issues,
    )

    strategy.validate(context)

    assert issues[0] is existing
    assert len(issues) == 3
    assert issues[1].details["parameter_name"] == "a"
    assert issues[2].details["parameter_name"] == "b"


def test_validate_issue_details_keys_and_annotation_identity() -> None:
    """
    Purpose:
        Verify issue details include only expected keys and values.
    Contract:
        Details contain parameter_name, position, annotation with identity preserved.
    Returns:
        None.
    Raises:
        AssertionError: If detail keys or annotation identity are incorrect.
    """
    strategy = RequiredHolesStrategy()
    issues: list[SpellValidationIssue] = []
    annotation = object()
    requirements = _RequirementsStub(required_holes=[_ParamStub("a", 5, annotation)])
    context = _make_context(
        spell=_SpellStub(spell_name="Root"),
        requirements=requirements,
        issues=issues,
    )

    strategy.validate(context)

    details = issues[0].details
    assert set(details.keys()) == {"parameter_name", "position", "annotation"}
    assert details["annotation"] is annotation
    assert details["position"] == 5


def test_validate_issue_order_matches_required_holes_order() -> None:
    """
    Purpose:
        Ensure issue ordering mirrors required hole iteration order.
    Contract:
        Issues are appended in the same order as iter_required_holes yields.
    Returns:
        None.
    Raises:
        AssertionError: If issue ordering does not match required hole order.
    """
    strategy = RequiredHolesStrategy()
    issues: list[SpellValidationIssue] = []
    params = [_ParamStub("first", 0, int), _ParamStub("second", 1, str)]
    requirements = _RequirementsStub(required_holes=params)
    context = _make_context(
        spell=_SpellStub(spell_name="Root"),
        requirements=requirements,
        issues=issues,
    )

    strategy.validate(context)

    assert [issue.details["parameter_name"] for issue in issues] == [
        "first",
        "second",
    ]


def test_validate_cancel_event_not_set_allows_processing() -> None:
    """
    Purpose:
        Ensure validation proceeds when cancellation is not set.
    Contract:
        Issues are emitted and throw_if_set is not invoked.
    Returns:
        None.
    Raises:
        AssertionError: If cancellation blocks processing or throws.
    """
    strategy = RequiredHolesStrategy()
    issues: list[SpellValidationIssue] = []
    cancel_event = _CancelStub(is_set=False)
    requirements = _RequirementsStub(required_holes=[_ParamStub("a", 0, int)])
    context = _make_context(
        spell=_SpellStub(spell_name="Root"),
        requirements=requirements,
        cancel_event=cancel_event,
        issues=issues,
    )

    strategy.validate(context)

    assert cancel_event.throw_calls == 0
    assert len(issues) == 1


def test_validate_emits_issue_for_generator_required_holes() -> None:
    """
    Purpose:
        Ensure generator-backed required holes are supported.
    Contract:
        Issues are emitted for required holes yielded by iter_required_holes.
    Returns:
        None.
    Raises:
        AssertionError: If issues are missing.
    """
    strategy = RequiredHolesStrategy()
    issues: list[SpellValidationIssue] = []
    requirements = _RequirementsStub(required_holes=[_ParamStub("a", 0, int)])
    spell = _SpellStub(spell_name="Root")
    context = _make_context(
        spell=spell,
        requirements=requirements,
        issues=issues,
    )

    strategy.validate(context)

    assert len(issues) == 1
    assert issues[0].details["parameter_name"] == "a"


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
    strategy = RequiredHolesStrategy()
    issues: list[SpellValidationIssue] = []
    cancel_event = _CancelStub(is_set=True)
    requirements = _RequirementsStub(required_holes=[_ParamStub("a", 0, int)])
    context = _make_context(
        spell=_SpellStub(),
        requirements=requirements,
        cancel_event=cancel_event,
        issues=issues,
    )

    with pytest.raises(RuntimeError, match="cancelled"):
        strategy.validate(context)

    assert issues == []
    assert cancel_event.throw_calls == 1
