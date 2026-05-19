import inspect

import pytest

from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.spellbook.spell_crafter.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_crafter.spell_requirements_finder.spell_parameter_requirements import (
    SpellParameterRequirement,
)


def _make_requirement(
    *,
    name: str = "dep",
    kind: inspect._ParameterKind = inspect.Parameter.POSITIONAL_OR_KEYWORD,
    di_shape: ParameterDIShape = ParameterDIShape.SINGLE_BY_ANNOTATION,
    has_default: bool = False,
    default_value=None,
    is_var_positional: bool = False,
    is_var_keyword: bool = False,
    is_keyword_only: bool = False,
    is_optional: bool = True,
    collection_element_annotation=None,
    spellmap_default=None,
) -> SpellParameterRequirement:
    return SpellParameterRequirement(
        name=name,
        position=1,
        kind=kind,
        annotation=int,
        default_value=default_value,
        has_default=has_default,
        is_var_positional=is_var_positional,
        is_var_keyword=is_var_keyword,
        is_keyword_only=is_keyword_only,
        is_optional=is_optional,
        di_shape=di_shape,
        collection_element_annotation=collection_element_annotation,
        spellmap_default=spellmap_default,
    )


def test_component_spell_parameter_requirement_preserves_spellmap_default() -> None:
    """
    Purpose:
        Validate SpellParameterRequirement records SpellMap defaults.
    Contract:
        - spellmap_default matches the provided SpellMap instance.
        - default_value and di_shape reflect constructor inputs.
    Returns:
        None.
    """
    spellmap = SpellMap("Concrete")
    requirement = _make_requirement(
        di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
        has_default=True,
        default_value=spellmap,
        spellmap_default=spellmap,
    )

    assert requirement.spellmap_default is spellmap
    assert requirement.default_value is spellmap
    assert requirement.di_shape is ParameterDIShape.SPELLMAP_DEFAULT
    assert requirement.has_default is True


def test_component_spell_parameter_requirement_tracks_collection_annotation() -> None:
    """
    Purpose:
        Validate collection element annotations are preserved.
    Contract:
        - collection_element_annotation is stored when shape is collection-based.
    Returns:
        None.
    """
    requirement = _make_requirement(
        di_shape=ParameterDIShape.COLLECTION_BY_ANNOTATION,
        collection_element_annotation=str,
    )

    assert requirement.di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION
    assert requirement.collection_element_annotation is str


def test_component_spell_parameter_requirement_exposes_flags() -> None:
    """
    Purpose:
        Validate parameter flags reflect constructor inputs.
    Contract:
        - varargs/keyword-only flags match the supplied values.
    Returns:
        None.
    """
    requirement = _make_requirement(
        kind=inspect.Parameter.KEYWORD_ONLY,
        is_var_positional=False,
        is_var_keyword=False,
        is_keyword_only=True,
    )

    assert requirement.kind is inspect.Parameter.KEYWORD_ONLY
    assert requirement.is_var_positional is False
    assert requirement.is_var_keyword is False
    assert requirement.is_keyword_only is True


def test_component_spell_parameter_requirement_cleanup_blocks_access() -> None:
    """
    Purpose:
        Validate cleanup prevents further property access.
    Contract:
        - Property access raises RuntimeError after cleanup.
    Returns:
        None.
    """
    requirement = _make_requirement()
    requirement.cleanup()

    assert requirement.cleaned is True
    with pytest.raises(RuntimeError):
        _ = requirement.name


def test_component_spell_parameter_requirement_rejects_empty_name() -> None:
    """
    Purpose:
        Validate empty parameter names are rejected.
    Contract:
        - ValueError is raised when name is empty.
    Returns:
        None.
    """
    with pytest.raises(ValueError):
        _make_requirement(name="")
