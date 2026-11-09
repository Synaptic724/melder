"""DI-shape string values and compiler-family dispatch contracts."""

import base64
import inspect
import pickle
import typing
from enum import StrEnum
from types import SimpleNamespace

import pytest

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_3 import CompilerPhase3
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import ParameterDIShape
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_parameter_requirements import (
    SpellParameterRequirement,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_requirements import SpellRequirements
from melder.aether.spellbook.spell_compiler.validation.strategies.annotation_shape_guard_strategy import (
    AnnotationShapeGuardStrategy,
)
from melder.aether.spellbook.spell_compiler.validation.strategies.parameter_policy_strategy import (
    ParameterPolicyStrategy,
)
from melder.aether.spellbook.spell_types.spell_types import SpellType


class ForeignShape(StrEnum):
    """Different enum family with intentionally colliding string values."""

    SINGLE_BY_ANNOTATION = "SINGLE_BY_ANNOTATION"
    SPELL_CONTRACT = "SPELL_CONTRACT"


def _context(shape: object, annotation: object) -> SimpleNamespace:
    """Build a minimal real-strategy input carrying one given shape."""
    parameter = SimpleNamespace(
        name="dependency", di_shape=shape, annotation=annotation,
        is_var_positional=False, is_var_keyword=False,
    )
    return SimpleNamespace(
        requirements=SimpleNamespace(parameters=[parameter]),
        spell=SimpleNamespace(resolvable=True, spell_name="Consumer"),
        cancel_event=None,
        issues=[],
    )


def test_di_shape_values_and_historical_ordinals() -> None:
    """Every old ordinal and exact name resolves to its original shape."""
    names = (
        "IGNORE", "PLAIN", "SINGLE_BY_ANNOTATION", "COLLECTION_BY_ANNOTATION",
        "SPELLMAP_DEFAULT", "SPELL_CONTRACT",
    )
    assert issubclass(ParameterDIShape, StrEnum)
    assert tuple(member.name for member in ParameterDIShape) == names
    for ordinal, name in enumerate(names, 1):
        member = ParameterDIShape[name]
        assert member.value == name
        assert ParameterDIShape(name) is member
        assert ParameterDIShape(ordinal) is member
        assert ParameterDIShape(float(ordinal)) is member


@pytest.mark.parametrize(
    ("payload", "expected"),
    (
        ("gASVcgAAAAAAAACMU21lbGRlci5hZXRoZXIuc3BlbGxib29rLnNwZWxsX2NvbXBpbGVyLnNwZWxsX3JlcXVpcmVtZW50c19maW5kZXIucGFyYW1ldGVyX2RpX3NoYXBllIwQUGFyYW1ldGVyRElTaGFwZZSTlEsBhZRSlC4=", ParameterDIShape.IGNORE),
        ("gASVcgAAAAAAAACMU21lbGRlci5hZXRoZXIuc3BlbGxib29rLnNwZWxsX2NvbXBpbGVyLnNwZWxsX3JlcXVpcmVtZW50c19maW5kZXIucGFyYW1ldGVyX2RpX3NoYXBllIwQUGFyYW1ldGVyRElTaGFwZZSTlEsGhZRSlC4=", ParameterDIShape.SPELL_CONTRACT),
    ),
)
def test_old_numeric_pickles_remain_readable(payload: str, expected: ParameterDIShape) -> None:
    """Numeric protocol-4 payloads from before migration preserve identity."""
    assert pickle.loads(base64.b64decode(payload)) is expected


@pytest.mark.parametrize("shape", ("SINGLE_BY_ANNOTATION", ForeignShape.SINGLE_BY_ANNOTATION))
def test_requirements_iterator_does_not_treat_foreign_shape_as_di(shape: object) -> None:
    """Only the proper enum member enters the real requirements iterator."""
    parameter = SpellParameterRequirement(
        name="dependency", position=0, kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
        annotation=object, default_value=None, has_default=False, is_var_positional=False,
        is_var_keyword=False, is_keyword_only=False, is_optional=False, di_shape=shape,
    )
    requirements = SpellRequirements(
        spell_id="sid", spell_type=SpellType.SPELL, existence=Existence.unique,
        spellframe=None, binding_name=None, parameters=[parameter],
    )
    try:
        assert list(requirements.iter_di_parameters()) == []
    finally:
        requirements.cleanup()


@pytest.mark.parametrize("shape", ("SINGLE_BY_ANNOTATION", ForeignShape.SINGLE_BY_ANNOTATION))
def test_phase3_foreign_shape_has_no_dependency_key(shape: object) -> None:
    """An equal string or foreign member does not create a DI dependency key."""
    dependency = SimpleNamespace(di_shape=shape, target_annotation=object)
    assert CompilerPhase3()._dependency_key_for_dep(dependency) is None
    dependency.di_shape = ParameterDIShape.SINGLE_BY_ANNOTATION
    assert CompilerPhase3()._dependency_key_for_dep(dependency) is not None


@pytest.mark.parametrize("shape", ("SINGLE_BY_ANNOTATION", ForeignShape.SINGLE_BY_ANNOTATION))
def test_parameter_policy_does_not_validate_a_foreign_shape(shape: object) -> None:
    """A foreign shape does not create a missing-annotation error."""
    strategy = ParameterPolicyStrategy()
    context = _context(shape, None)
    strategy.validate(context)
    assert context.issues == []
    context = _context(ParameterDIShape.SINGLE_BY_ANNOTATION, None)
    strategy.validate(context)
    assert [issue.code for issue in context.issues] == ["DI_MISSING_ANNOTATION"]
    strategy.cleanup()


@pytest.mark.parametrize("shape", ("SPELL_CONTRACT", ForeignShape.SPELL_CONTRACT))
def test_annotation_guard_does_not_skip_a_foreign_shape(shape: object) -> None:
    """Only the actual contract member suppresses the annotation warning."""
    strategy = AnnotationShapeGuardStrategy()
    context = _context(shape, typing.ForwardRef("Missing"))
    strategy.validate(context)
    assert [issue.code for issue in context.issues] == ["UNRESOLVED_FORWARD_REF"]
    context = _context(ParameterDIShape.SPELL_CONTRACT, typing.ForwardRef("Missing"))
    strategy.validate(context)
    assert context.issues == []
    strategy.cleanup()
