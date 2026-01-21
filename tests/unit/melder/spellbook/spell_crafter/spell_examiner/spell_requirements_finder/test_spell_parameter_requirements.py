import inspect

import pytest

from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.spell_parameter_requirements import (
    SpellParameterRequirement,
)


def _make_requirement(
    *,
    name: str = "dep",
    di_shape: ParameterDIShape = ParameterDIShape.SINGLE_BY_ANNOTATION,
    has_default: bool = False,
    default_value=None,
    collection_element_annotation=None,
    spellmap_default=None,
) -> SpellParameterRequirement:
    return SpellParameterRequirement(
        name=name,
        position=1,
        kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
        annotation=int,
        default_value=default_value,
        has_default=has_default,
        is_var_positional=False,
        is_var_keyword=False,
        is_keyword_only=False,
        is_optional=True,
        di_shape=di_shape,
        collection_element_annotation=collection_element_annotation,
        spellmap_default=spellmap_default,
    )


def test_properties_reflect_constructor_values_and_spellmap_default():
    sm = SpellMap("Concrete")
    req = _make_requirement(
        di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
        has_default=True,
        default_value=sm,
        spellmap_default=sm,
    )

    assert req.name == "dep"
    assert req.position == 1
    assert req.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert req.annotation is int
    assert req.default_value is sm
    assert req.has_default is True
    assert req.is_var_positional is False
    assert req.is_var_keyword is False
    assert req.is_keyword_only is False
    assert req.is_optional is True
    assert req.di_shape is ParameterDIShape.SPELLMAP_DEFAULT
    assert req.collection_element_annotation is None
    assert req.spellmap_default is sm


def test_collection_element_annotation_preserved_for_collection_shape():
    req = _make_requirement(
        di_shape=ParameterDIShape.COLLECTION_BY_ANNOTATION,
        collection_element_annotation=str,
    )
    assert req.collection_element_annotation is str
    assert req.di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION


def test_empty_name_rejected():
    with pytest.raises(ValueError):
        _make_requirement(name="")


def test_cleanup_nulls_and_blocks_property_access():
    req = _make_requirement()
    req.cleanup()
    assert req.cleaned is True

    with pytest.raises(RuntimeError):
        _ = req.name
    with pytest.raises(RuntimeError):
        _ = req.di_shape

    # Idempotent
    req.cleanup()
