import threading

import pytest

from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_compiler.symbolic_graph.spell_symbolic_dependency import (
    SpellSymbolicDependency,
)


def _dep(**overrides):
    defaults = dict(
        spell_version_id="v1",
        param_name="p",
        position=2,
        di_shape=ParameterDIShape.SINGLE_BY_ANNOTATION,
        is_optional=False,
        target_annotation=str,
        is_collection=False,
        spellmap_default=None,
    )
    defaults.update(overrides)
    return SpellSymbolicDependency(**defaults)


@pytest.mark.parametrize("bad_id", [None, "", 0])
def test_init_rejects_invalid_spell_version_id(bad_id):
    with pytest.raises(ValueError):
        _dep(spell_version_id=bad_id)


# Whitespace-only names are allowed by the implementation; only falsy names are rejected.
@pytest.mark.parametrize("bad_name", [None, ""])
def test_init_rejects_invalid_param_name(bad_name):
    with pytest.raises(ValueError):
        _dep(param_name=bad_name)


def test_fields_are_exposed_via_properties():
    dep = _dep(
        spell_version_id="spell-123",
        param_name="dep_param",
        position=1,
        di_shape=ParameterDIShape.SPELLMAP_DEFAULT,
        is_optional=True,
        target_annotation="Frame",
        is_collection=True,
        spellmap_default="default-map",
    )

    assert dep.spell_id == "spell-123"
    assert dep.param_name == "dep_param"
    assert dep.position == 1
    assert dep.di_shape is ParameterDIShape.SPELLMAP_DEFAULT
    assert dep.is_optional is True
    assert dep.target_annotation == "Frame"
    assert dep.is_collection is True
    assert dep.spellmap_default == "default-map"


def test_is_collection_flag_tracks_di_shape_independently():
    dep = _dep(di_shape=ParameterDIShape.COLLECTION_BY_ANNOTATION, is_collection=False)
    assert dep.di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION
    # The code does not derive is_collection; it honors the constructor flag.
    assert dep.is_collection is False


def test_cleanup_nulls_fields_and_blocks_access():
    dep = _dep()
    dep.cleanup()

    assert dep._cleaned is True
    assert not hasattr(dep, '_lock')
    with pytest.raises(RuntimeError):
        _ = dep.spell_id
    with pytest.raises(RuntimeError):
        _ = dep.param_name
    with pytest.raises(RuntimeError):
        _ = dep.di_shape
    with pytest.raises(RuntimeError):
        _ = dep.spellmap_default


def test_cleanup_is_idempotent():
    dep = _dep()
    dep.cleanup()
    dep.cleanup()  # second call should be a no-op
    assert dep._cleaned is True  # noqa: SLF001


@pytest.mark.parametrize(
    "target_annotation,is_collection",
    [
        (None, False),
        ("Frame", False),
        (int, True),
    ],
)
def test_target_annotation_and_collection_flags_survive_roundtrip(target_annotation, is_collection):
    dep = _dep(target_annotation=target_annotation, is_collection=is_collection)
    assert dep.target_annotation == target_annotation
    assert dep.is_collection is is_collection


def test_position_allows_negative_values_without_validation():
    dep = _dep(position=-5)
    assert dep.position == -5


def test_accepts_arbitrary_truthy_spell_id_and_preserves_reference():
    sentinel = object()
    dep = _dep(spell_version_id=sentinel)
    assert dep.spell_id is sentinel


def test_whitespace_param_name_is_preserved():
    dep = _dep(param_name="   spaced   ")
    assert dep.param_name == "   spaced   "


def test_defaults_set_expected_flags_and_none_values():
    dep = _dep()
    assert dep.is_optional is False
    assert dep.spellmap_default is None
    assert dep.target_annotation is str


@pytest.mark.parametrize("prop", ["spell_id", "param_name", "position", "di_shape", "is_optional", "target_annotation", "is_collection", "spellmap_default"])
def test_access_after_cleanup_raises(prop):
    dep = _dep()
    dep.cleanup()
    with pytest.raises(RuntimeError):
        getattr(dep, prop)


def test_cleanup_resets_fields_to_safe_defaults():
    dep = _dep(
        is_optional=True,
        target_annotation="X",
        is_collection=True,
        spellmap_default="map",
    )
    dep.cleanup()
    assert not hasattr(dep, '_spell_id')
    assert not hasattr(dep, '_param_name')
    assert dep._position == -1
    assert not hasattr(dep, '_di_shape')
    assert dep._is_optional is False
    assert not hasattr(dep, '_target_annotation')
    assert dep._is_collection is False
    assert not hasattr(dep, '_spellmap_default')


def test_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Verify cleanup returns early when another thread marks the dependency cleaned.

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

    dep = _dep()
    coordinated_lock = _CoordinatedLock()
    dep._lock = coordinated_lock

    thread_results = []

    def _run_cleanup() -> None:
        dep.cleanup()
        thread_results.append(True)

    first = threading.Thread(target=_run_cleanup)
    second = threading.Thread(target=_run_cleanup)
    first.start()
    coordinated_lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join(timeout=1.0)
    second.join(timeout=1.0)

    assert thread_results == [True, True]
    assert dep.cleaned is True
    assert not hasattr(dep, '_lock')
