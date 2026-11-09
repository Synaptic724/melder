import inspect

import pytest

from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_parameter_requirements import (
    SpellParameterRequirement,
)
from tests._cleanup_recheck_support import CleanupRecheckHandshake


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


def test_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Verify a second cleanup caller that passed the outer check returns at the inner `_cleaned` recheck.

    The handshake holds the first caller inside the lock until the second has passed the outer check and is about
    to block, then marks the requirement cleaned, as a cleanup racing in from elsewhere would. Both callers must
    return at the inner recheck and finish without raising - without it the teardown would run twice and the
    second run would raise on attributes the first had already deleted - and the requirement must read cleaned.
    The handshake also fails the test if either caller is still running after its bounded join. The callers are
    ordered by the handshake, not by timing: the earlier hand-made lock could lose its signal and failed on CI
    (GitHub #206; TASK-2026-11-08-deterministic_cleanup_recheck_handshake).

    Returns:
        None.
    """
    req = _make_requirement()

    def _mark_cleaned() -> None:
        """Mark the requirement cleaned while the first caller holds the lock and the second waits for it."""
        req._cleaned = True

    handshake = CleanupRecheckHandshake(on_holder_ready=_mark_cleaned)
    req._lock = handshake.lock

    handshake.run(req.cleanup)

    assert req.cleaned is True
