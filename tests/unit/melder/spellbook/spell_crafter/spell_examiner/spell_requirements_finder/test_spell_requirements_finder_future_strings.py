"""String-expression annotation tests for SpellRequirementsFinder."""
import inspect
from typing import get_args

import pytest

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell import Spell
from melder.spellbook.spell_crafter.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.spellbook.spell_crafter.spell_requirements_finder.spell_parameter_requirements import (
    SpellParameterRequirement,
)
from melder.spellbook.spell_crafter.spell_requirements_finder.spell_requirements import (
    SpellRequirements,
)
from melder.spellbook.spell_crafter.spell_requirements_finder.spell_requirements_finder import (
    SpellRequirementsFinder,
)
from melder.spellbook.spell_types.spell_types import SpellType


class _StubSpellbook:
    """
    Purpose:
        Provide a minimal Spellbook stub for Spell construction.
    Contract:
        - Exposes _spell_system_states for Spell initialization.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize the Spellbook stub.
        Contract:
            Sets a placeholder _spell_system_states object.
        Returns:
            None.
        """
        self._spell_system_states = object()


def _make_spell(
    call_target: object,
    *,
    spell_type: SpellType = SpellType.SPELL,
    spellframe: object | None = None,
    binding_name: str | None = None,
    version: str = "v1",
) -> Spell:
    """
    Purpose:
        Build a Spell instance for requirements testing.
    Contract:
        - Returns a Spell with a deterministic SpellIndex.current value.
    Args:
        call_target: Callable or class used as the spell target.
        spell_type: SpellType for the target.
        spellframe: Optional frame for the spell.
        binding_name: Optional binding name for the spell.
        version: Version id to store in the SpellIndex.
    Returns:
        Spell: A Spell configured for requirements inspection.
    """
    return Spell(
        call_target,
        SpellIndex(version),
        spellframe,
        binding_name,
        getattr(call_target, "__name__", "name"),
        Existence.unique,
        spell_type,
        "id",
        Permissions.read,
        "frame",
        spellbook=_StubSpellbook(),
    )


def _reqs_for(
    func: object,
    *,
    spell_type: SpellType = SpellType.METHOD,
) -> SpellRequirements:
    """
    Purpose:
        Build SpellRequirements for a callable.
    Contract:
        - Returns requirements built by SpellRequirementsFinder.
    Args:
        func: Callable or class used as the spell target.
        spell_type: SpellType for the target.
    Returns:
        SpellRequirements: Requirements for the supplied callable.
    """
    spell = _make_spell(func, spell_type=spell_type)
    return SpellRequirementsFinder(spell).build_requirements()


def _by_name(reqs: SpellRequirements) -> dict[str, SpellParameterRequirement]:
    """
    Purpose:
        Index parameter requirements by name.
    Contract:
        - Returns a mapping from parameter name to requirement.
    Args:
        reqs: SpellRequirements instance to index.
    Returns:
        dict[str, SpellParameterRequirement]: Name-indexed requirements.
    """
    return {p.name: p for p in reqs.parameters}


class Dep:
    """
    Purpose:
        Provide a dependency type for string-expression parsing tests.
    Contract:
        Acts as a DI candidate class.
    """


def _requirement_for_expression(
    monkeypatch: pytest.MonkeyPatch,
    expression: str,
) -> SpellParameterRequirement:
    """
    Purpose:
        Build a SpellParameterRequirement from a string annotation expression.
    Contract:
        - Forces inspect.get_annotations to return the provided expression.
        - Returns the requirement for parameter "x".
    Args:
        monkeypatch: Pytest monkeypatch fixture.
        expression: String annotation expression to parse.
    Returns:
        SpellParameterRequirement: Requirement for the annotated parameter.
    """
    def f(x: object) -> object:
        """
        Purpose:
            Provide a callable for requirements extraction.
        Contract:
            Returns the input for completeness.
        Args:
            x: Input value.
        Returns:
            object: The provided input.
        """
        return x

    def fake_get_annotations(*args: object, **kwargs: object) -> dict[str, str]:
        """
        Purpose:
            Provide a deterministic annotation mapping for parsing.
        Contract:
            Returns the string expression for parameter "x".
        Args:
            *args: Unused positional arguments.
            **kwargs: Unused keyword arguments.
        Returns:
            dict[str, str]: Fake annotations mapping.
        """
        return {"x": expression}

    monkeypatch.setattr(inspect, "get_annotations", fake_get_annotations)
    reqs = _reqs_for(f, spell_type=SpellType.METHOD)
    return _by_name(reqs)["x"]


def test_string_expression_list_forward_ref_resolves_collection(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose:
        Validate list[Dep] string expressions resolve collection DI.
    Contract:
        - list[Dep] is classified as collection DI with Dep elements.
    Returns:
        None.
    Raises:
        AssertionError: If collection DI is misclassified.
    """
    requirement = _requirement_for_expression(monkeypatch, "list[Dep]")
    assert requirement.di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION
    assert requirement.collection_element_annotation is Dep


def test_string_expression_list_string_inner_resolves_collection(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose:
        Validate list['Dep'] string expressions resolve collection DI.
    Contract:
        - list['Dep'] is classified as collection DI with Dep elements.
    Returns:
        None.
    Raises:
        AssertionError: If collection DI is misclassified.
    """
    requirement = _requirement_for_expression(monkeypatch, "list['Dep']")
    assert requirement.di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION
    assert requirement.collection_element_annotation is Dep


def test_string_expression_typing_list_string_inner_resolves_collection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate typing.List['Dep'] string expressions resolve collection DI.
    Contract:
        - typing.List['Dep'] is classified as collection DI with Dep elements.
    Returns:
        None.
    Raises:
        AssertionError: If collection DI is misclassified.
    """
    requirement = _requirement_for_expression(monkeypatch, "typing.List['Dep']")
    assert requirement.di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION
    assert requirement.collection_element_annotation is Dep


def test_string_expression_optional_string_inner_marks_optional(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate Optional['Dep'] string expressions mark dependencies optional.
    Contract:
        - Optional['Dep'] becomes optional single DI with Dep in the union.
    Returns:
        None.
    Raises:
        AssertionError: If optional DI is misclassified.
    """
    requirement = _requirement_for_expression(monkeypatch, "Optional['Dep']")
    assert requirement.di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION
    assert requirement.is_optional is True
    assert Dep in get_args(requirement.annotation)
    assert type(None) in get_args(requirement.annotation)


def test_string_expression_typing_optional_string_inner_marks_optional(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate typing.Optional['Dep'] string expressions mark dependencies optional.
    Contract:
        - typing.Optional['Dep'] becomes optional single DI with Dep in the union.
    Returns:
        None.
    Raises:
        AssertionError: If optional DI is misclassified.
    """
    requirement = _requirement_for_expression(monkeypatch, "typing.Optional['Dep']")
    assert requirement.di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION
    assert requirement.is_optional is True
    assert Dep in get_args(requirement.annotation)
    assert type(None) in get_args(requirement.annotation)


def test_string_expression_union_string_inner_marks_optional(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate Union['Dep', None] string expressions mark dependencies optional.
    Contract:
        - Union['Dep', None] becomes optional single DI with Dep in the union.
    Returns:
        None.
    Raises:
        AssertionError: If optional DI is misclassified.
    """
    requirement = _requirement_for_expression(monkeypatch, "Union['Dep', None]")
    assert requirement.di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION
    assert requirement.is_optional is True
    assert Dep in get_args(requirement.annotation)
    assert type(None) in get_args(requirement.annotation)


def test_string_expression_typing_union_string_inner_marks_optional(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate typing.Union['Dep', None] string expressions mark dependencies optional.
    Contract:
        - typing.Union['Dep', None] becomes optional single DI with Dep in the union.
    Returns:
        None.
    Raises:
        AssertionError: If optional DI is misclassified.
    """
    requirement = _requirement_for_expression(monkeypatch, "typing.Union['Dep', None]")
    assert requirement.di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION
    assert requirement.is_optional is True
    assert Dep in get_args(requirement.annotation)
    assert type(None) in get_args(requirement.annotation)


def test_string_expression_pep604_string_inner_marks_optional(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate 'Dep' | None string expressions mark dependencies optional.
    Contract:
        - 'Dep' | None becomes optional single DI with Dep in the union.
    Returns:
        None.
    Raises:
        AssertionError: If optional DI is misclassified.
    """
    requirement = _requirement_for_expression(monkeypatch, "'Dep' | None")
    assert requirement.di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION
    assert requirement.is_optional is True
    assert Dep in get_args(requirement.annotation)
    assert type(None) in get_args(requirement.annotation)


def test_string_expression_typing_list_builtin_is_plain(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Purpose:
        Validate typing.List[int] string expressions do not trigger DI.
    Contract:
        - typing.List[int] is classified as plain.
    Returns:
        None.
    Raises:
        AssertionError: If builtin collection DI is misclassified.
    """
    requirement = _requirement_for_expression(monkeypatch, "typing.List[int]")
    assert requirement.di_shape is ParameterDIShape.PLAIN


def test_string_expression_unknown_dotted_name_remains_string(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate unknown dotted names remain string annotations.
    Contract:
        - Unresolved dotted names are preserved as strings for later matching.
    Returns:
        None.
    Raises:
        AssertionError: If dotted names are resolved unexpectedly.
    """
    requirement = _requirement_for_expression(monkeypatch, "pkg.Dep")
    assert requirement.di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION
    assert requirement.annotation == "pkg.Dep"
