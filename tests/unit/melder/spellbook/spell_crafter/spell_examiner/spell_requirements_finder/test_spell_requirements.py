import inspect

import pytest

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_parameter_requirements import (
    SpellParameterRequirement,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_requirements import (
    SpellRequirements,
)
from melder.aether.spellbook.spell_types.spell_types import SpellType
from tests._cleanup_recheck_support import CleanupRecheckHandshake


def _param(name: str, shape: ParameterDIShape, has_default: bool = False):
    return SpellParameterRequirement(
        name=name,
        position=0,
        kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
        annotation=object,
        default_value=None,
        has_default=has_default,
        is_var_positional=False,
        is_var_keyword=False,
        is_keyword_only=False,
        is_optional=False,
        di_shape=shape,
        collection_element_annotation=None,
        spellmap_default=None,
    )


def test_properties_and_parameters_read_only_view():
    params = [_param("a", ParameterDIShape.PLAIN)]
    reqs = SpellRequirements(
        spell_id="sid",
        spell_type=SpellType.SPELL,
        existence=Existence.unique,
        spellframe="frame",
        binding_name="bind",
        parameters=params,
    )

    assert reqs.spell_id == "sid"
    assert reqs.spell_type is SpellType.SPELL
    assert reqs.existence is Existence.unique
    assert reqs.spellframe == "frame"
    assert reqs.binding_name == "bind"

    params_view = reqs.parameters
    assert isinstance(params_view, tuple)
    assert params_view[0] is params[0]


def test_iterators_filter_shapes_correctly():
    di_params = [
        _param("one", ParameterDIShape.SINGLE_BY_ANNOTATION),
        _param("many", ParameterDIShape.COLLECTION_BY_ANNOTATION),
        _param("map", ParameterDIShape.SPELLMAP_DEFAULT),
    ]
    plain_param = _param("plain", ParameterDIShape.PLAIN, has_default=True)
    ignore_param = _param("ignored", ParameterDIShape.IGNORE)

    reqs = SpellRequirements(
        spell_id="sid",
        spell_type=SpellType.SPELL,
        existence=Existence.unique,
        spellframe=None,
        binding_name=None,
        parameters=[*di_params, plain_param, ignore_param],
    )

    assert set(p.name for p in reqs.iter_di_parameters()) == {"one", "many", "map"}
    assert [p.name for p in reqs.iter_plain_parameters()] == ["plain"]
    assert list(reqs.iter_required_holes()) == []  # plain has default
    assert reqs.has_required_holes() is False


def test_required_holes_detected_when_plain_without_default():
    hole = _param("missing", ParameterDIShape.PLAIN, has_default=False)
    optional_plain = _param("opt", ParameterDIShape.PLAIN, has_default=True)
    reqs = SpellRequirements(
        spell_id="sid",
        spell_type=SpellType.SPELL,
        existence=Existence.unique,
        spellframe=None,
        binding_name=None,
        parameters=[hole, optional_plain],
    )

    holes = list(reqs.iter_required_holes())
    assert holes == [hole]
    assert reqs.has_required_holes() is True


def test_cleanup_cascades_and_is_idempotent():
    class CleanableStub:
        def __init__(self):
            self.cleaned = 0

        @property
        def di_shape(self):
            return ParameterDIShape.PLAIN

        @property
        def has_default(self):
            return False

        def cleanup(self):
            self.cleaned += 1

    exploding = CleanableStub()

    class Exploder(CleanableStub):
        def cleanup(self):
            super().cleanup()
            raise RuntimeError("boom")

    reqs = SpellRequirements(
        spell_id="sid",
        spell_type=SpellType.SPELL,
        existence=Existence.unique,
        spellframe=None,
        binding_name=None,
        parameters=[exploding, Exploder()],
    )

    reqs.cleanup()
    assert reqs.cleaned is True
    assert exploding.cleaned >= 1
    with pytest.raises(RuntimeError):
        _ = reqs.parameters

    reqs.cleanup()  # idempotent
    with pytest.raises(RuntimeError):
        _ = reqs.spell_id


def test_spell_id_must_be_non_empty():
    with pytest.raises(ValueError):
        SpellRequirements(
            spell_id="",
            spell_type=SpellType.SPELL,
            existence=Existence.unique,
            spellframe=None,
            binding_name=None,
            parameters=[],
        )


def test_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Verify cleanup returns early when another thread marks the object cleaned.

    The handshake holds the first caller inside the lock until the second has passed the outer `_cleaned` check
    and is about to block; the first caller then runs the real cleanup and marks the requirements cleaned. The
    second caller must return at the inner recheck - without it the teardown would run twice and a caller would
    raise on an attribute the other had already deleted - so both callers finish without raising and the
    requirements read cleaned with their `_lock` dropped. The callers are ordered by the handshake, not by timing:
    the earlier hand-made lock could lose its signal and failed on CI (GitHub #206;
    TASK-2026-11-08-deterministic_cleanup_recheck_handshake).

    Returns:
        None.
    """
    reqs = SpellRequirements(
        spell_id="sid",
        spell_type=SpellType.SPELL,
        existence=Existence.unique,
        spellframe=None,
        binding_name=None,
        parameters=[],
    )
    handshake = CleanupRecheckHandshake()
    reqs._lock = handshake.lock

    handshake.run(reqs.cleanup)

    assert reqs.cleaned is True
    assert not hasattr(reqs, '_lock')
