import threading

import pytest

from melder.aether.spellbook.spell_crafter.symbolic_graph.spell_symbolic_graph import (
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
    assert not hasattr(g, '_dependencies')
    assert not hasattr(g, '_lock')
    assert g._cleaned is True
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
    assert not hasattr(g, '_dependencies')


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


def test_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Verify cleanup returns early when another thread marks the graph cleaned.

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

    graph = _graph([])
    coordinated_lock = _CoordinatedLock()
    graph._lock = coordinated_lock

    thread_results = []

    def _run_cleanup() -> None:
        graph.cleanup()
        thread_results.append(True)

    first = threading.Thread(target=_run_cleanup)
    second = threading.Thread(target=_run_cleanup)
    first.start()
    coordinated_lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join(timeout=1.0)
    second.join(timeout=1.0)

    assert thread_results == [True, True]
    assert graph.cleaned is True
    assert not hasattr(graph, '_lock')

