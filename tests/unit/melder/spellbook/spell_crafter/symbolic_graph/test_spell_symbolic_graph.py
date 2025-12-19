import pytest

from melder.spellbook.spell_crafter.symbolic_graph.spell_symbolic_graph import (
    SpellSymbolicGraph,
)


class _Dep:
    def __init__(self):
        self.cleaned = 0

    def cleanup(self):
        self.cleaned += 1


class _BoomDep(_Dep):
    def cleanup(self):
        super().cleanup()
        raise RuntimeError("boom")


def _graph(deps=None, spell_id="sid"):
    return SpellSymbolicGraph(spell_version_id=spell_id, dependencies=deps)


@pytest.mark.parametrize("bad_id", [None, "", 0])
def test_init_rejects_invalid_spell_version_id(bad_id):
    with pytest.raises(ValueError):
        SpellSymbolicGraph(spell_version_id=bad_id)


def test_dependencies_default_empty_and_copied():
    g = SpellSymbolicGraph(spell_version_id="s1")
    deps = g.dependencies
    assert deps == []
    deps.append("x")
    # Internal list is untouched
    assert g.dependencies == []


def test_dependencies_copy_does_not_expose_internal_list():
    d1, d2 = _Dep(), _Dep()
    g = _graph([d1, d2])
    deps_a = g.dependencies
    deps_b = g.dependencies
    assert deps_a == deps_b == [d1, d2]
    assert deps_a is not deps_b
    deps_a.pop()
    assert g.dependencies == [d1, d2]


def test_fields_are_exposed_via_properties():
    deps = [_Dep()]
    g = _graph(deps, spell_id="version-123")
    assert g.spell_id == "version-123"
    assert g.dependencies == deps


def test_dependency_order_preserved():
    deps = [_Dep(), _Dep(), _Dep()]
    g = _graph(deps)
    assert g.dependencies == deps


def test_cleanup_cascades_and_clears_state():
    d1, d2 = _Dep(), _Dep()
    g = _graph([d1, d2])
    g.cleanup()

    assert d1.cleaned == 1
    assert d2.cleaned == 1
    assert g._dependencies == []  # noqa: SLF001
    assert g._lock is None  # noqa: SLF001
    assert g._cleaned is True  # noqa: SLF001
    with pytest.raises(RuntimeError):
        _ = g.dependencies
    with pytest.raises(RuntimeError):
        _ = g.spell_id


def test_cleanup_swallows_dependency_errors():
    noisy = _BoomDep()
    quiet = _Dep()
    g = _graph([noisy, quiet])
    g.cleanup()
    assert noisy.cleaned == 1
    assert quiet.cleaned == 1
    assert g._dependencies == []  # noqa: SLF001


def test_cleanup_is_idempotent_and_does_not_recall_dependencies():
    dep = _Dep()
    g = _graph([dep])
    g.cleanup()
    dep.cleaned = 0  # reset counter to detect repeated calls
    g.cleanup()
    assert dep.cleaned == 0


def test_dependencies_property_returns_fresh_copy_each_call():
    g = _graph([_Dep()])
    first = g.dependencies
    second = g.dependencies
    assert first is not second


def test_cleanup_on_empty_dependencies_still_marks_cleaned():
    g = _graph([])
    g.cleanup()
    assert g._cleaned is True  # noqa: SLF001

