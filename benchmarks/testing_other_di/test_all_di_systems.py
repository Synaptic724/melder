from __future__ import annotations

import gc
import inspect
import time
from dataclasses import dataclass
from typing import Any, Callable

import pytest

from tests.mocks.spellbook.deep_layers import (
    Depth9Root,
    get_depth_9_classes,
)

# ======================================================================================
# Shared helpers
# ======================================================================================

def _ms(seconds: float) -> float:
    return seconds * 1000.0


def _us(seconds: float) -> float:
    return seconds * 1_000_000.0


def _gc_cleanup() -> None:
    """Best-effort cleanup to reduce cross-test noise."""
    gc.collect()


def _depth9_leaf_ids(root: Depth9Root) -> tuple[int, int]:
    """Extract leaf object ids from a Depth9Root instance for reuse checks."""
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
    """Extract (param_name, param_type) for cls.__init__ excluding self."""
    sig = inspect.signature(cls.__init__)
    params = list(sig.parameters.values())[1:]  # skip self
    out: list[tuple[str, type]] = []
    for p in params:
        if p.annotation is inspect._empty:
            raise AssertionError(
                f"{cls.__name__}.__init__ param '{p.name}' missing annotation"
            )
        if not isinstance(p.annotation, type):
            raise AssertionError(
                f"{cls.__name__}.__init__ param '{p.name}' has non-type annotation: {p.annotation!r}"
            )
        out.append((p.name, p.annotation))
    return tuple(out)


# ======================================================================================
# Melder harness
# ======================================================================================

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
    """Ensure integration tests start with a clean Aether singleton."""
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
    spellbook: Spellbook
    conduit: Conduit
    root_id: str


def _melder_bind_depth9_all(
        spellbook: Spellbook,
        *,
        existence: Existence,
) -> str:
    """Bind depth-9 classes with the same existence; return root spell id."""
    spell_ids: dict[type, str] = {}
    for cls in get_depth_9_classes():
        spell_ids[cls] = spellbook.bind(
            spell=cls,
            existence=existence,
            permissions="create",
        )
    return spell_ids[Depth9Root]


def _build_melder_depth9(*, existence: Existence, frame: str, conjure_name: str) -> tuple[_MelderState, float]:
    spellbook = Spellbook(aetheric_frame=frame)
    cfg = spellbook.get_configuration()
    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)
    # Benchmark the core runtime without the cache lane so cache I/O and
    # package-build overhead do not contaminate DI hotpath comparisons.
    spellbook.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
        system_caching_enabled=True,
    )

    root_id = _melder_bind_depth9_all(spellbook, existence=existence)

    t0 = time.perf_counter()
    conduit = spellbook.conjure(name=conjure_name)
    conjure_s = time.perf_counter() - t0

    return _MelderState(spellbook=spellbook, conduit=conduit, root_id=root_id), conjure_s


def _melder_get(state: _MelderState) -> Any:
    return state.conduit.meld(spell=state.root_id)


def _melder_cleanup(state: _MelderState) -> None:
    state.conduit.cleanup()
    _gc_cleanup()


# ======================================================================================
# Dependency Injector harness
# ======================================================================================

@dataclass(frozen=True)
class _DIState:
    providers_by_type: dict[type, Any]


def _build_dependency_injector_transient(classes: tuple[type, ...]) -> _DIState:
    """Build providers.Factory chain for ALL classes (no Singletons)."""
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

        providers_by_type[cls] = providers.Factory(cls, **kwargs)

    return _DIState(providers_by_type=providers_by_type)


def _di_get(state: _DIState, cls: type) -> Any:
    return state.providers_by_type[cls]()


def _di_cleanup(_state: _DIState) -> None:
    _gc_cleanup()


# ======================================================================================
# Lagom harness
# ======================================================================================

@dataclass(frozen=True)
class _LagomState:
    container: Any


def _build_lagom_transient(classes: tuple[type, ...]) -> _LagomState:
    """Bind ALL classes as transient factories (no Singleton)."""
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
            continue

        container[cls] = _make_factory(cls, param_specs)

    return _LagomState(container=container)


def _lagom_get(state: _LagomState, cls: type) -> Any:
    return state.container[cls]


def _lagom_cleanup(_state: _LagomState) -> None:
    _gc_cleanup()


# ======================================================================================
# Injector harness (python-injector)
# ======================================================================================

@dataclass(frozen=True)
class _InjectorState:
    injector: Any
    original_inits: dict[type, Any]


def _build_injector_transient(classes: tuple[type, ...]) -> _InjectorState:
    """Bind ALL classes as transient (no singleton scope)."""
    pytest.importorskip("injector")
    from injector import Binder, Injector, Module, inject

    # Patch constructors so Injector will actually inject.
    original_inits: dict[type, Any] = {}
    for cls in classes:
        original_inits[cls] = cls.__init__
        cls.__init__ = inject(cls.__init__)  # type: ignore[method-assign]

    class PerfModule(Module):
        def configure(self, binder: Binder) -> None:
            for cls in classes:
                binder.bind(cls, to=cls)

    injector = Injector([PerfModule()])

    return _InjectorState(injector=injector, original_inits=original_inits)


def _injector_get(state: _InjectorState, cls: type) -> Any:
    return state.injector.get(cls)


def _injector_cleanup(state: _InjectorState) -> None:
    for cls, orig in state.original_inits.items():
        cls.__init__ = orig  # type: ignore[method-assign]
    _gc_cleanup()


# ======================================================================================
# Dishka harness
# ======================================================================================

@dataclass(frozen=True)
class _DishkaState:
    container: Any


def _build_dishka_transient(classes: tuple[type, ...]) -> _DishkaState:
    """Provide ALL classes with cache=False so every get() creates a fresh graph."""
    pytest.importorskip("dishka")
    from dishka import Provider, Scope, make_container

    provider = Provider()
    for cls in classes:
        provider.provide(cls, scope=Scope.APP, cache=False)

    container = make_container(provider)
    return _DishkaState(container=container)


def _dishka_get(state: _DishkaState, cls: type) -> Any:
    return state.container.get(cls)


def _dishka_cleanup(state: _DishkaState) -> None:
    state.container.close()
    _gc_cleanup()


# ======================================================================================
# Test dispatcher
# ======================================================================================

def _libs() -> tuple[str, ...]:
    return ("melder", "dependency-injector", "lagom", "injector", "dishka")


# ======================================================================================
# TRANSIENT cold/warm (this replaces the old "unique" singleton test)
# ======================================================================================

@pytest.mark.parametrize("lib", _libs())
def test_perf_depth9_transient_conjure_and_meld_cold_warm_all(lib: str) -> None:
    """Cold/warm where BOTH calls are transient (root must differ).

    This answers your question directly: no singletons, no caching.
    """

    classes = get_depth_9_classes()
    root_cls = Depth9Root

    if lib == "melder":
        state, conjure_s = _build_melder_depth9(
            existence=Existence.many,
            frame="perf-depth9-transient",
            conjure_name="perf-depth9-transient",
        )
        try:
            t0 = time.perf_counter()
            root1 = _melder_get(state)
            cold_s = time.perf_counter() - t0
            assert isinstance(root1, Depth9Root)

            t0 = time.perf_counter()
            root2 = _melder_get(state)
            warm_s = time.perf_counter() - t0
            assert isinstance(root2, Depth9Root)

            # STRICT: transient means new objects.
            assert root1 is not root2
            a1, b1 = _depth9_leaf_ids(root1)
            a2, b2 = _depth9_leaf_ids(root2)
            assert a1 != a2
            assert b1 != b2

        finally:
            _melder_cleanup(state)

        print(
            f"[melder] Perf depth9 transient cold/warm (ms/us): "
            f"conjure={_ms(conjure_s):.3f}ms, "
            f"meld_root_cold={_ms(cold_s):.3f}ms, "
            f"meld_root_2nd={_us(warm_s):.2f}us"
        )
        return

    if lib == "dependency-injector":
        t0 = time.perf_counter()
        state = _build_dependency_injector_transient(classes)
        conjure_s = time.perf_counter() - t0
        try:
            t0 = time.perf_counter()
            root1 = _di_get(state, root_cls)
            cold_s = time.perf_counter() - t0
            assert isinstance(root1, Depth9Root)

            t0 = time.perf_counter()
            root2 = _di_get(state, root_cls)
            warm_s = time.perf_counter() - t0
            assert isinstance(root2, Depth9Root)

            assert root1 is not root2
            a1, b1 = _depth9_leaf_ids(root1)
            a2, b2 = _depth9_leaf_ids(root2)
            assert a1 != a2
            assert b1 != b2
        finally:
            _di_cleanup(state)

    elif lib == "lagom":
        t0 = time.perf_counter()
        state = _build_lagom_transient(classes)
        conjure_s = time.perf_counter() - t0
        try:
            t0 = time.perf_counter()
            root1 = _lagom_get(state, root_cls)
            cold_s = time.perf_counter() - t0
            assert isinstance(root1, Depth9Root)

            t0 = time.perf_counter()
            root2 = _lagom_get(state, root_cls)
            warm_s = time.perf_counter() - t0
            assert isinstance(root2, Depth9Root)

            assert root1 is not root2
            a1, b1 = _depth9_leaf_ids(root1)
            a2, b2 = _depth9_leaf_ids(root2)
            assert a1 != a2
            assert b1 != b2
        finally:
            _lagom_cleanup(state)

    elif lib == "injector":
        t0 = time.perf_counter()
        state = _build_injector_transient(classes)
        conjure_s = time.perf_counter() - t0
        try:
            t0 = time.perf_counter()
            root1 = _injector_get(state, root_cls)
            cold_s = time.perf_counter() - t0
            assert isinstance(root1, Depth9Root)

            t0 = time.perf_counter()
            root2 = _injector_get(state, root_cls)
            warm_s = time.perf_counter() - t0
            assert isinstance(root2, Depth9Root)

            assert root1 is not root2
            a1, b1 = _depth9_leaf_ids(root1)
            a2, b2 = _depth9_leaf_ids(root2)
            assert a1 != a2
            assert b1 != b2
        finally:
            _injector_cleanup(state)

    elif lib == "dishka":
        t0 = time.perf_counter()
        state = _build_dishka_transient(classes)
        conjure_s = time.perf_counter() - t0
        try:
            t0 = time.perf_counter()
            root1 = _dishka_get(state, root_cls)
            cold_s = time.perf_counter() - t0
            assert isinstance(root1, Depth9Root)

            t0 = time.perf_counter()
            root2 = _dishka_get(state, root_cls)
            warm_s = time.perf_counter() - t0
            assert isinstance(root2, Depth9Root)

            assert root1 is not root2
            a1, b1 = _depth9_leaf_ids(root1)
            a2, b2 = _depth9_leaf_ids(root2)
            assert a1 != a2
            assert b1 != b2
        finally:
            _dishka_cleanup(state)

    else:
        raise AssertionError(f"Unknown lib: {lib}")

    print(
        f"[{lib}] Perf depth9 transient cold/warm (ms/us): "
        f"conjure={_ms(conjure_s):.3f}ms, "
        f"meld_root_cold={_ms(cold_s):.3f}ms, "
        f"meld_root_2nd={_us(warm_s):.2f}us"
    )


# ======================================================================================
# TRANSIENT many avg
# ======================================================================================

@pytest.mark.parametrize("lib", _libs())
def test_perf_depth9_transient_many_avg_all(lib: str) -> None:
    """Average cost of resolving a fully-transient depth-9 graph."""

    classes = get_depth_9_classes()
    root_cls = Depth9Root
    iterations = 250

    if lib == "melder":
        state, conjure_s = _build_melder_depth9(
            existence=Existence.many,
            frame="perf-depth9-many",
            conjure_name="perf-depth9-many",
        )
        try:
            _ = _melder_get(state)  # warm up

            t0 = time.perf_counter()
            first_a = None
            first_b = None
            last_a = None
            last_b = None

            for i in range(iterations):
                root = _melder_get(state)
                assert isinstance(root, Depth9Root)
                a, b = _depth9_leaf_ids(root)
                if i == 0:
                    first_a, first_b = a, b
                last_a, last_b = a, b

            total_s = time.perf_counter() - t0

            assert first_a is not None and last_a is not None
            assert first_b is not None and last_b is not None
            assert first_a != last_a
            assert first_b != last_b

        finally:
            _melder_cleanup(state)

        print(
            f"[melder] Perf depth9 transient many (avg over {iterations}) (ms): "
            f"conjure={_ms(conjure_s):.3f}, "
            f"avg_meld_root={_ms(total_s) / iterations:.3f}"
        )
        return

    if lib == "dependency-injector":
        state = _build_dependency_injector_transient(classes)
        try:
            _ = _di_get(state, root_cls)

            t0 = time.perf_counter()
            first_a = None
            first_b = None
            last_a = None
            last_b = None

            for i in range(iterations):
                root = _di_get(state, root_cls)
                assert isinstance(root, Depth9Root)
                a, b = _depth9_leaf_ids(root)
                if i == 0:
                    first_a, first_b = a, b
                last_a, last_b = a, b

            total_s = time.perf_counter() - t0

            assert first_a is not None and last_a is not None
            assert first_b is not None and last_b is not None
            assert first_a != last_a
            assert first_b != last_b
        finally:
            _di_cleanup(state)

    elif lib == "lagom":
        state = _build_lagom_transient(classes)
        try:
            _ = _lagom_get(state, root_cls)

            t0 = time.perf_counter()
            first_a = None
            first_b = None
            last_a = None
            last_b = None

            for i in range(iterations):
                root = _lagom_get(state, root_cls)
                assert isinstance(root, Depth9Root)
                a, b = _depth9_leaf_ids(root)
                if i == 0:
                    first_a, first_b = a, b
                last_a, last_b = a, b

            total_s = time.perf_counter() - t0

            assert first_a is not None and last_a is not None
            assert first_b is not None and last_b is not None
            assert first_a != last_a
            assert first_b != last_b
        finally:
            _lagom_cleanup(state)

    elif lib == "injector":
        state = _build_injector_transient(classes)
        try:
            _ = _injector_get(state, root_cls)

            t0 = time.perf_counter()
            first_a = None
            first_b = None
            last_a = None
            last_b = None

            for i in range(iterations):
                root = _injector_get(state, root_cls)
                assert isinstance(root, Depth9Root)
                a, b = _depth9_leaf_ids(root)
                if i == 0:
                    first_a, first_b = a, b
                last_a, last_b = a, b

            total_s = time.perf_counter() - t0

            assert first_a is not None and last_a is not None
            assert first_b is not None and last_b is not None
            assert first_a != last_a
            assert first_b != last_b
        finally:
            _injector_cleanup(state)

    elif lib == "dishka":
        state = _build_dishka_transient(classes)
        try:
            _ = _dishka_get(state, root_cls)

            t0 = time.perf_counter()
            first_a = None
            first_b = None
            last_a = None
            last_b = None

            for i in range(iterations):
                root = _dishka_get(state, root_cls)
                assert isinstance(root, Depth9Root)
                a, b = _depth9_leaf_ids(root)
                if i == 0:
                    first_a, first_b = a, b
                last_a, last_b = a, b

            total_s = time.perf_counter() - t0

            assert first_a is not None and last_a is not None
            assert first_b is not None and last_b is not None
            assert first_a != last_a
            assert first_b != last_b
        finally:
            _dishka_cleanup(state)

    else:
        raise AssertionError(f"Unknown lib: {lib}")

    print(
        f"[{lib}] Perf depth9 transient many (avg over {iterations}) (ms): "
        f"avg_meld_root={_ms(total_s) / iterations:.3f}"
    )
