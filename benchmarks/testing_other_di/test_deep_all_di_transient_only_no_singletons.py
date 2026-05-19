from __future__ import annotations

"""
Transient-only deep perf harness: Melder vs 4 DI libraries.

This file intentionally removes singleton/caching behavior from ALL libraries to answer one
question cleanly:

  "How fast can each container build a depth-N transient object graph?"

What this file does NOT measure:
- cached/singleton warm hits ("unique" mode)
- spellspace/per-scope caching
- leaf-only caching scenarios
- cleanup lifecycle costs across cached objects

Run:
  pytest -q benchmarks/testing_other_di/test_deep_all_di_transient_only_no_singletons.py -s
"""

import gc
import inspect
import time
from dataclasses import dataclass
from typing import Any, Callable

import pytest

from tests.mocks.spellbook.deep_layers import (
    Depth7Root,
    Depth9Root,
    get_depth_3_classes,
    get_depth_5_classes,
    get_depth_7_classes,
    get_depth_9_classes,
)

# ======================================================================================
# Shared helpers
# ======================================================================================


def _ms(seconds: float) -> float:
    return seconds * 1000.0


def _us(seconds: float) -> float:
    return seconds * 1_000_000.0


def _median(values: list[float]) -> float:
    """
    Return the median value for a numeric sample list.

    Contract:
        - Returns 0.0 for empty input.
        - Uses midpoint average for even-sized lists.
    """
    if not values:
        return 0.0
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2.0


def _gc_cleanup() -> None:
    gc.collect()


def _depth9_leaf_ids(root: Depth9Root) -> tuple[int, int]:
    layer2 = root.left
    layer3 = layer2.left
    layer4 = layer3.left
    layer5 = layer4.left
    layer6 = layer5.left
    layer7 = layer6.left
    layer8 = layer7.left
    leaf_a = layer8.left
    leaf_b = layer8.right
    return id(leaf_a), id(leaf_b)


def _ctor_param_types(cls: type) -> tuple[tuple[str, type], ...]:
    sig = inspect.signature(cls.__init__)
    params = list(sig.parameters.values())[1:]  # skip self
    out: list[tuple[str, type]] = []
    for p in params:
        if p.annotation is inspect._empty:
            raise AssertionError(f"{cls.__name__}.__init__ param '{p.name}' missing annotation")
        if not isinstance(p.annotation, type):
            raise AssertionError(
                f"{cls.__name__}.__init__ param '{p.name}' has non-type annotation: {p.annotation!r}"
            )
        out.append((p.name, p.annotation))
    return tuple(out)


# ======================================================================================
# Melder harness (transient only)
# ======================================================================================

pytest.importorskip("melder")
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


@pytest.fixture(autouse=True)
def _reset_aether_singleton_for_integration() -> None:
    """
    Keep Melder's global singleton from bleeding across tests.

    This fixture runs for the whole module (including other libs) — that's fine.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@dataclass(frozen=True)
class _MelderState:
    conduit: Conduit
    root_id: str
    conjure_s: float
    bind_s: float


def _melder_build_transient(*, frame: str, classes: tuple[type, ...], root_cls: type) -> _MelderState:
    spellbook = Spellbook(aetheric_frame=frame)
    cfg = spellbook.get_configuration()
    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)

    t0 = time.perf_counter()
    spell_ids: dict[type, str] = {}
    for cls in classes:
        spell_ids[cls] = spellbook.bind(
            spell=cls,
            existence=Existence.many,  # IMPORTANT: transient
            permissions="create",
        )
    bind_s = time.perf_counter() - t0

    root_id = spell_ids[root_cls]

    t0 = time.perf_counter()
    conduit = spellbook.conjure(name=frame)
    conjure_s = time.perf_counter() - t0

    return _MelderState(conduit=conduit, root_id=root_id, conjure_s=conjure_s, bind_s=bind_s)


def _melder_get(state: _MelderState) -> Any:
    return state.conduit.meld(spell=state.root_id)


def _melder_get_alias(state: _MelderState) -> Any:
    """
    Resolve the root spell using local aliases for the callsite fields.

    Contract:
        - Executes the same meld route as `_melder_get`.
        - Only differs by local aliasing of state fields.
    """
    conduit = state.conduit
    root_id = state.root_id
    return conduit.meld(spell=root_id)


def _melder_cleanup(state: _MelderState) -> None:
    state.conduit.cleanup()
    _gc_cleanup()


def _measure_loop_s(*, fn: Callable[[], Any], warmup: int, iterations: int) -> float:
    """
    Measure loop elapsed seconds for a zero-arg callable.

    Contract:
        - Executes warmup calls before timing.
        - Returns total elapsed wall time for timed calls.
    """
    for _ in range(warmup):
        fn()
    t0 = time.perf_counter()
    for _ in range(iterations):
        fn()
    return time.perf_counter() - t0


def _paired_order_avg_and_delta_s(
        *,
        first_fn: Callable[[], Any],
        second_fn: Callable[[], Any],
        warmup: int,
        iterations: int,
        pair_repeats: int,
) -> tuple[float, float, float]:
    """
    Measure two call paths with paired alternating order.

    Contract:
        - Alternates execution order each pair to reduce fixed-order bias.
        - Returns average totals plus median per-iteration delta.
    """
    first_runs_s: list[float] = []
    second_runs_s: list[float] = []
    deltas_us_per_iter: list[float] = []
    for pair_index in range(pair_repeats):
        if pair_index % 2 == 0:
            first_s = _measure_loop_s(fn=first_fn, warmup=warmup, iterations=iterations)
            second_s = _measure_loop_s(fn=second_fn, warmup=warmup, iterations=iterations)
        else:
            second_s = _measure_loop_s(fn=second_fn, warmup=warmup, iterations=iterations)
            first_s = _measure_loop_s(fn=first_fn, warmup=warmup, iterations=iterations)
        first_runs_s.append(first_s)
        second_runs_s.append(second_s)
        deltas_us_per_iter.append(_us(second_s - first_s) / float(iterations))
    return (
        sum(first_runs_s) / float(pair_repeats),
        sum(second_runs_s) / float(pair_repeats),
        _median(deltas_us_per_iter),
    )


def _aa_noise_floor_us_per_iter(
        *,
        fn: Callable[[], Any],
        warmup: int,
        iterations: int,
        pair_repeats: int,
) -> float:
    """
    Measure median A/A absolute noise floor for one call path.

    Contract:
        - Runs the same callable twice per pair.
        - Returns median absolute delta in microseconds per iteration.
    """
    deltas_us_per_iter: list[float] = []
    for _ in range(pair_repeats):
        first_s = _measure_loop_s(fn=fn, warmup=warmup, iterations=iterations)
        second_s = _measure_loop_s(fn=fn, warmup=warmup, iterations=iterations)
        deltas_us_per_iter.append(_us(abs(second_s - first_s)) / float(iterations))
    return _median(deltas_us_per_iter)


# ======================================================================================
# dependency-injector harness (transient only)
# ======================================================================================


@dataclass(frozen=True)
class _DIState:
    providers_by_type: dict[type, Any]


def _build_dependency_injector_transient(classes: tuple[type, ...]) -> _DIState:
    pytest.importorskip("dependency_injector")
    from dependency_injector import providers

    providers_by_type: dict[type, Any] = {}
    for cls in classes:
        param_specs = _ctor_param_types(cls)
        kwargs: dict[str, Any] = {}
        for pname, ptype in param_specs:
            dep = providers_by_type.get(ptype)
            if dep is None:
                raise AssertionError(
                    f"DI wiring error: {cls.__name__} depends on {ptype.__name__} before it was registered"
                )
            kwargs[pname] = dep
        providers_by_type[cls] = providers.Factory(cls, **kwargs)  # no Singleton
    return _DIState(providers_by_type=providers_by_type)


def _di_get(state: _DIState, cls: type) -> Any:
    return state.providers_by_type[cls]()


def _di_cleanup(_state: _DIState) -> None:
    _gc_cleanup()


# ======================================================================================
# Lagom harness (transient only)
# ======================================================================================


@dataclass(frozen=True)
class _LagomState:
    container: Any


def _build_lagom_transient(classes: tuple[type, ...]) -> _LagomState:
    pytest.importorskip("lagom")
    from lagom import Container

    container = Container()

    def _make_leaf_factory(_cls: type) -> Callable[[], Any]:
        def factory() -> Any:
            return _cls()
        return factory

    def _make_factory(_cls: type, _specs: tuple[tuple[str, type], ...]) -> Callable[[Any], Any]:
        def factory(c: Any) -> Any:
            kwargs = {pname: c[ptype] for pname, ptype in _specs}
            return _cls(**kwargs)
        return factory

    for cls in classes:
        param_specs = _ctor_param_types(cls)
        if not param_specs:
            container[cls] = _make_leaf_factory(cls)
        else:
            container[cls] = _make_factory(cls, param_specs)

    return _LagomState(container=container)


def _lagom_get(state: _LagomState, cls: type) -> Any:
    return state.container[cls]


def _lagom_cleanup(_state: _LagomState) -> None:
    _gc_cleanup()


# ======================================================================================
# Injector harness (transient only)
# ======================================================================================


@dataclass(frozen=True)
class _InjectorState:
    injector: Any
    original_inits: dict[type, Any]


def _build_injector_transient(classes: tuple[type, ...]) -> _InjectorState:
    pytest.importorskip("injector")
    from injector import Binder, Injector, Module, inject

    original_inits: dict[type, Any] = {}
    for cls in classes:
        original_inits[cls] = cls.__init__
        cls.__init__ = inject(cls.__init__)  # type: ignore[method-assign]

    class PerfModule(Module):
        def configure(self, binder: Binder) -> None:
            for cls in classes:
                binder.bind(cls, to=cls)  # no singleton scope

    injector = Injector([PerfModule()])
    return _InjectorState(injector=injector, original_inits=original_inits)


def _injector_get(state: _InjectorState, cls: type) -> Any:
    return state.injector.get(cls)


def _injector_cleanup(state: _InjectorState) -> None:
    for cls, orig in state.original_inits.items():
        cls.__init__ = orig  # type: ignore[method-assign]
    _gc_cleanup()


# ======================================================================================
# Dishka harness (transient only)
# ======================================================================================


@dataclass(frozen=True)
class _DishkaState:
    container: Any


def _build_dishka_transient(classes: tuple[type, ...]) -> _DishkaState:
    pytest.importorskip("dishka")
    from dishka import Provider, Scope, make_container

    provider = Provider()
    for cls in classes:
        provider.provide(cls, scope=Scope.APP, cache=False)  # IMPORTANT: no caching

    container = make_container(provider)
    return _DishkaState(container=container)


def _dishka_get(state: _DishkaState, cls: type) -> Any:
    return state.container.get(cls)


def _dishka_cleanup(state: _DishkaState) -> None:
    state.container.close()
    _gc_cleanup()


# ======================================================================================
# Dispatcher
# ======================================================================================


def _libs() -> tuple[str, ...]:
    return ("melder", "dependency-injector", "lagom", "injector", "dishka")


# ======================================================================================
# Tests
# ======================================================================================


@pytest.mark.parametrize("lib", _libs())
def test_perf_transient_scaling_depth3_5_7_9(lib: str) -> None:
    """
    Transient scaling: build/container setup + first root resolve.
    All libs are configured transient-only.
    """
    cases = (
        (3, get_depth_3_classes()),
        (5, get_depth_5_classes()),
        (7, get_depth_7_classes()),
        (9, get_depth_9_classes()),
    )

    for depth, classes in cases:
        root_cls = classes[-1]

        if lib == "melder":
            state = _melder_build_transient(frame=f"transient-scale-{depth}", classes=classes, root_cls=root_cls)
            try:
                t0 = time.perf_counter()
                root = _melder_get(state)
                meld_s = time.perf_counter() - t0
                assert isinstance(root, root_cls)
            finally:
                _melder_cleanup(state)

            print(
                f"[melder] transient scaling depth={depth} (ms): "
                f"bind={_ms(state.bind_s):.3f}, "
                f"conjure={_ms(state.conjure_s):.3f}, "
                f"meld_root_cold={_ms(meld_s):.3f}"
            )
            continue

        if lib == "dependency-injector":
            t0 = time.perf_counter()
            state = _build_dependency_injector_transient(classes)
            conjure_s = time.perf_counter() - t0
            try:
                t0 = time.perf_counter()
                root = _di_get(state, root_cls)
                meld_s = time.perf_counter() - t0
                assert isinstance(root, root_cls)
            finally:
                _di_cleanup(state)

        elif lib == "lagom":
            t0 = time.perf_counter()
            state = _build_lagom_transient(classes)
            conjure_s = time.perf_counter() - t0
            try:
                t0 = time.perf_counter()
                root = _lagom_get(state, root_cls)
                meld_s = time.perf_counter() - t0
                assert isinstance(root, root_cls)
            finally:
                _lagom_cleanup(state)

        elif lib == "injector":
            t0 = time.perf_counter()
            state = _build_injector_transient(classes)
            conjure_s = time.perf_counter() - t0
            try:
                t0 = time.perf_counter()
                root = _injector_get(state, root_cls)
                meld_s = time.perf_counter() - t0
                assert isinstance(root, root_cls)
            finally:
                _injector_cleanup(state)

        elif lib == "dishka":
            t0 = time.perf_counter()
            state = _build_dishka_transient(classes)
            conjure_s = time.perf_counter() - t0
            try:
                t0 = time.perf_counter()
                root = _dishka_get(state, root_cls)
                meld_s = time.perf_counter() - t0
                assert isinstance(root, root_cls)
            finally:
                _dishka_cleanup(state)

        else:
            raise AssertionError(f"Unknown lib: {lib}")

        print(
            f"[{lib}] transient scaling depth={depth} (ms): "
            f"conjure={_ms(conjure_s):.3f}, "
            f"meld_root_cold={_ms(meld_s):.3f}"
        )


@pytest.mark.parametrize("lib", _libs())
def test_perf_depth9_transient_cold_second_and_avg(lib: str) -> None:
    """
    Depth-9 transient:
      - time first resolve (cold)
      - time second resolve (still transient, MUST be a new graph)
      - average over 250
    """
    classes = get_depth_9_classes()
    root_cls = Depth9Root
    iterations = 250

    if lib == "melder":
        state = _melder_build_transient(frame="transient-depth9", classes=classes, root_cls=root_cls)
        try:
            t0 = time.perf_counter()
            root1 = _melder_get(state)
            cold_s = time.perf_counter() - t0
            assert isinstance(root1, Depth9Root)
            a1, b1 = _depth9_leaf_ids(root1)

            t0 = time.perf_counter()
            root2 = _melder_get(state)
            second_s = time.perf_counter() - t0
            assert isinstance(root2, Depth9Root)
            a2, b2 = _depth9_leaf_ids(root2)

            assert root1 is not root2
            assert a1 != a2
            assert b1 != b2

            t0 = time.perf_counter()
            for _ in range(iterations):
                _ = _melder_get(state)
            total_s = time.perf_counter() - t0
        finally:
            _melder_cleanup(state)

        print(
            f"[melder] depth9 transient (ms/us): "
            f"bind={_ms(state.bind_s):.3f}ms, "
            f"conjure={_ms(state.conjure_s):.3f}ms, "
            f"cold={_ms(cold_s):.3f}ms, "
            f"second={_us(second_s):.2f}us, "
            f"avg={_ms(total_s) / iterations:.3f}ms"
        )
        return

    if lib == "dependency-injector":
        state = _build_dependency_injector_transient(classes)
        try:
            t0 = time.perf_counter()
            root1 = _di_get(state, root_cls)
            cold_s = time.perf_counter() - t0
            a1, b1 = _depth9_leaf_ids(root1)

            t0 = time.perf_counter()
            root2 = _di_get(state, root_cls)
            second_s = time.perf_counter() - t0
            a2, b2 = _depth9_leaf_ids(root2)

            assert a1 != a2 and b1 != b2

            t0 = time.perf_counter()
            for _ in range(iterations):
                _ = _di_get(state, root_cls)
            total_s = time.perf_counter() - t0
        finally:
            _di_cleanup(state)

    elif lib == "lagom":
        state = _build_lagom_transient(classes)
        try:
            t0 = time.perf_counter()
            root1 = _lagom_get(state, root_cls)
            cold_s = time.perf_counter() - t0
            a1, b1 = _depth9_leaf_ids(root1)

            t0 = time.perf_counter()
            root2 = _lagom_get(state, root_cls)
            second_s = time.perf_counter() - t0
            a2, b2 = _depth9_leaf_ids(root2)

            assert a1 != a2 and b1 != b2

            t0 = time.perf_counter()
            for _ in range(iterations):
                _ = _lagom_get(state, root_cls)
            total_s = time.perf_counter() - t0
        finally:
            _lagom_cleanup(state)

    elif lib == "injector":
        state = _build_injector_transient(classes)
        try:
            t0 = time.perf_counter()
            root1 = _injector_get(state, root_cls)
            cold_s = time.perf_counter() - t0
            a1, b1 = _depth9_leaf_ids(root1)

            t0 = time.perf_counter()
            root2 = _injector_get(state, root_cls)
            second_s = time.perf_counter() - t0
            a2, b2 = _depth9_leaf_ids(root2)

            assert a1 != a2 and b1 != b2

            t0 = time.perf_counter()
            for _ in range(iterations):
                _ = _injector_get(state, root_cls)
            total_s = time.perf_counter() - t0
        finally:
            _injector_cleanup(state)

    elif lib == "dishka":
        state = _build_dishka_transient(classes)
        try:
            t0 = time.perf_counter()
            root1 = _dishka_get(state, root_cls)
            cold_s = time.perf_counter() - t0
            a1, b1 = _depth9_leaf_ids(root1)

            t0 = time.perf_counter()
            root2 = _dishka_get(state, root_cls)
            second_s = time.perf_counter() - t0
            a2, b2 = _depth9_leaf_ids(root2)

            assert a1 != a2 and b1 != b2

            t0 = time.perf_counter()
            for _ in range(iterations):
                _ = _dishka_get(state, root_cls)
            total_s = time.perf_counter() - t0
        finally:
            _dishka_cleanup(state)

    else:
        raise AssertionError(f"Unknown lib: {lib}")

    print(
        f"[{lib}] depth9 transient (ms/us): "
        f"cold={_ms(cold_s):.3f}ms, "
        f"second={_us(second_s):.2f}us, "
        f"avg={_ms(total_s) / iterations:.3f}ms"
    )


@pytest.mark.parametrize("lib", _libs())
def test_perf_mixed_workload_depth7_depth9_transient(lib: str) -> None:
    iterations = 200

    if lib == "melder":
        spellbook = Spellbook(aetheric_frame="transient-mixed")
        cfg = spellbook.get_configuration()
        cfg.set_property("phase_scheduler_workers_per_spellbook", 1)

        t0 = time.perf_counter()
        spell_ids_9: dict[type, str] = {}
        for cls in get_depth_9_classes():
            spell_ids_9[cls] = spellbook.bind(
                spell=cls, existence=Existence.many, permissions="create")
        spell_ids_7: dict[type, str] = {}
        for cls in get_depth_7_classes():
            spell_ids_7[cls] = spellbook.bind(
                spell=cls, existence=Existence.many, permissions="create")
        bind_s = time.perf_counter() - t0

        root9_id = spell_ids_9[Depth9Root]
        root7_id = spell_ids_7[Depth7Root]

        t0 = time.perf_counter()
        conduit = spellbook.conjure(name="transient-mixed")
        conjure_s = time.perf_counter() - t0

        try:
            t0 = time.perf_counter()
            for i in range(iterations):
                if i % 2 == 0:
                    r = conduit.meld(spell=root9_id)
                    assert isinstance(r, Depth9Root)
                else:
                    r = conduit.meld(spell=root7_id)
                    assert isinstance(r, Depth7Root)
            total_s = time.perf_counter() - t0
        finally:
            conduit.cleanup()
            _gc_cleanup()

        print(
            f"[melder] mixed transient (iters={iterations}) (ms): "
            f"bind={_ms(bind_s):.3f}, "
            f"conjure={_ms(conjure_s):.3f}, "
            f"avg_step={_ms(total_s) / iterations:.3f}"
        )
        return

    depth9_classes = get_depth_9_classes()
    depth7_classes = get_depth_7_classes()
    all_classes = tuple(depth9_classes) + tuple(c for c in depth7_classes if c not in depth9_classes)

    if lib == "dependency-injector":
        state = _build_dependency_injector_transient(all_classes)
        try:
            t0 = time.perf_counter()
            for i in range(iterations):
                if i % 2 == 0:
                    r = _di_get(state, Depth9Root)
                    assert isinstance(r, Depth9Root)
                else:
                    r = _di_get(state, Depth7Root)
                    assert isinstance(r, Depth7Root)
            total_s = time.perf_counter() - t0
        finally:
            _di_cleanup(state)

    elif lib == "lagom":
        state = _build_lagom_transient(all_classes)
        try:
            t0 = time.perf_counter()
            for i in range(iterations):
                if i % 2 == 0:
                    r = _lagom_get(state, Depth9Root)
                    assert isinstance(r, Depth9Root)
                else:
                    r = _lagom_get(state, Depth7Root)
                    assert isinstance(r, Depth7Root)
            total_s = time.perf_counter() - t0
        finally:
            _lagom_cleanup(state)

    elif lib == "injector":
        state = _build_injector_transient(all_classes)
        try:
            t0 = time.perf_counter()
            for i in range(iterations):
                if i % 2 == 0:
                    r = _injector_get(state, Depth9Root)
                    assert isinstance(r, Depth9Root)
                else:
                    r = _injector_get(state, Depth7Root)
                    assert isinstance(r, Depth7Root)
            total_s = time.perf_counter() - t0
        finally:
            _injector_cleanup(state)

    elif lib == "dishka":
        state = _build_dishka_transient(all_classes)
        try:
            t0 = time.perf_counter()
            for i in range(iterations):
                if i % 2 == 0:
                    r = _dishka_get(state, Depth9Root)
                    assert isinstance(r, Depth9Root)
                else:
                    r = _dishka_get(state, Depth7Root)
                    assert isinstance(r, Depth7Root)
            total_s = time.perf_counter() - t0
        finally:
            _dishka_cleanup(state)

    else:
        raise AssertionError(f"Unknown lib: {lib}")

    print(f"[{lib}] mixed transient (iters={iterations}) (ms): avg_step={_ms(total_s) / iterations:.3f}")


def test_perf_melder_depth9_transient_direct_vs_alias_paired() -> None:
    """
    Measure melder transient depth-9 direct vs alias callsite with paired order.

    Contract:
        - Uses paired alternating run order to reduce order bias.
        - Reports median per-iteration delta and A/A noise floor.
        - Uses transient-only Depth9 root resolution path.
    """
    classes = get_depth_9_classes()
    iterations = 300
    warmup = 30
    pair_repeats = 8
    state = _melder_build_transient(
        frame="transient-depth9-direct-vs-alias",
        classes=classes,
        root_cls=Depth9Root,
    )
    try:
        direct_fn = lambda: _melder_get(state)
        alias_fn = lambda: _melder_get_alias(state)
        first_direct = direct_fn()
        first_alias = alias_fn()
        assert isinstance(first_direct, Depth9Root)
        assert isinstance(first_alias, Depth9Root)
        direct_avg_s, alias_avg_s, median_delta_us_per_iter = _paired_order_avg_and_delta_s(
            first_fn=direct_fn,
            second_fn=alias_fn,
            warmup=warmup,
            iterations=iterations,
            pair_repeats=pair_repeats,
        )
        aa_noise_floor_us_per_iter = _aa_noise_floor_us_per_iter(
            fn=direct_fn,
            warmup=warmup,
            iterations=iterations,
            pair_repeats=pair_repeats,
        )
    finally:
        _melder_cleanup(state)

    direct_avg_us = _us(direct_avg_s) / float(iterations)
    alias_avg_us = _us(alias_avg_s) / float(iterations)
    ratio = alias_avg_s / direct_avg_s
    print(
        f"[melder-direct-vs-alias] depth9 transient | "
        f"iterations={iterations}, warmup={warmup}, pair_repeats={pair_repeats} | "
        f"direct_us_per_iter={direct_avg_us:.3f} | "
        f"alias_us_per_iter={alias_avg_us:.3f} | "
        f"alias_over_direct_ratio={ratio:.6f} | "
        f"median_pair_delta_us_per_iter={median_delta_us_per_iter:.3f} | "
        f"aa_noise_floor_us_per_iter={aa_noise_floor_us_per_iter:.3f}"
    )
