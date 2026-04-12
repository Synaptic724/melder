import inspect
import threading

import pytest

from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.spell_parameter_requirements import (
    SpellParameterRequirement,
)
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.spell_requirements import (
    SpellRequirements,
)
from melder.spellbook.spell_types.spell_types import SpellType


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

    Returns:
        None.
    """

    class _CoordinatedLock:
        def __init__(self) -> None:
            self._entered_first = threading.Event()
            self._second_attempted = threading.Event()
            self._lock = threading.RLock()

        def __enter__(self):
            if self._entered_first.is_set():
                self._second_attempted.set()
            self._lock.acquire()
            if not self._entered_first.is_set():
                self._entered_first.set()
                assert self._second_attempted.wait(timeout=1.0)
            return self

        def __exit__(self, exc_type, exc, tb):
            self._lock.release()

    reqs = SpellRequirements(
        spell_id="sid",
        spell_type=SpellType.SPELL,
        existence=Existence.unique,
        spellframe=None,
        binding_name=None,
        parameters=[],
    )
    coordinated_lock = _CoordinatedLock()
    reqs._lock = coordinated_lock

    thread_results = []

    def _run_cleanup() -> None:
        reqs.cleanup()
        thread_results.append(True)

    first = threading.Thread(target=_run_cleanup)
    second = threading.Thread(target=_run_cleanup)
    first.start()
    coordinated_lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join(timeout=1.0)
    second.join(timeout=1.0)

    assert thread_results == [True, True]
    assert reqs.cleaned is True
    assert reqs._lock is None
