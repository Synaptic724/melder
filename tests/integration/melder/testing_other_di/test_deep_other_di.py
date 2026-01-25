from __future__ import annotations

import contextlib
import contextvars
import gc
import inspect
import time
from dataclasses import dataclass
from typing import Any, Callable

import pytest

from tests.mocks.spellbook.deep_layers import (
    Depth3Root,
    Depth7Root,
    Depth9LeafA,
    Depth9LeafB,
    Depth9Root,
    get_depth_3_classes,
    get_depth_5_classes,
    get_depth_7_classes,
    get_depth_9_classes,
)


# ======================================================================================
# Shared helpers (match Melder test semantics as closely as other containers allow)
# ======================================================================================


def _ms(seconds: float) -> float:
    return seconds * 1000.0


def _us(seconds: float) -> float:
    return seconds * 1_000_000.0


def _depth9_leaf_ids(root: Depth9Root) -> tuple[int, int]:
    """
    Purpose:
        Extract leaf object ids from a Depth9Root instance for reuse checks.
    Returns:
        tuple[int, int]: (leaf_a_id, leaf_b_id)
    """
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
    """
    Purpose:
        Extract (param_name, param_type) for cls.__init__ excluding self.
    Notes:
        - Assumes deep_layers classes use concrete type annotations, which they do.
    """
    sig = inspect.signature(cls.__init__)
    params = list(sig.parameters.values())[1:]  # skip self
    out: list[tuple[str, type]] = []
    for p in params:
        if p.annotation is inspect._empty:
            raise AssertionError(f"{cls.__name__}.__init__ param '{p.name}' missing annotation")
        if not isinstance(p.annotation, type):
            # deep_layers uses concrete classes; keep it strict
            raise AssertionError(f"{cls.__name__}.__init__ param '{p.name}' has non-type annotation: {p.annotation!r}")
        out.append((p.name, p.annotation))
    return tuple(out)


def _gc_cleanup() -> None:
    """
    Purpose:
        Best-effort cleanup for containers that don't have explicit disposal.
    Contract:
        - Forces a collection pass to reduce cross-test noise.
    """
    gc.collect()


# ======================================================================================
# Dependency Injector harness
# ======================================================================================


@dataclass(frozen=True)
class _DIState:
    """
    Purpose:
        Hold Dependency Injector provider graph for a given test scenario.
    """
    providers_by_type: dict[type, Any]
    singleton_types: set[type]


def _build_dependency_injector(
        classes: tuple[type, ...],
        *,
        singleton_types: set[type],
) -> _DIState:
    """
    Purpose:
        Build Dependency Injector providers for the given classes.
    Contract:
        - Singleton for types in singleton_types; Factory otherwise.
        - Wires dependencies explicitly by constructor signature.
    """
    dependency_injector = pytest.importorskip("dependency_injector")
    from dependency_injector import providers

    providers_by_type: dict[type, Any] = {}

    for cls in classes:
        param_specs = _ctor_param_types(cls)
        kwargs: dict[str, Any] = {}
        for pname, ptype in param_specs:
            dep = providers_by_type.get(ptype)
            if dep is None:
                raise AssertionError(f"DI wiring error: {cls.__name__} depends on {ptype.__name__} before it was registered")
            kwargs[pname] = dep

        if cls in singleton_types:
            prov = providers.Singleton(cls, **kwargs)
        else:
            prov = providers.Factory(cls, **kwargs)

        providers_by_type[cls] = prov

    return _DIState(providers_by_type=providers_by_type, singleton_types=set(singleton_types))


def _di_get(state: _DIState, cls: type) -> Any:
    prov = state.providers_by_type[cls]
    return prov()


@contextlib.contextmanager
def _di_reset_singletons(state: _DIState, *, types_to_reset: tuple[type, ...]) -> Any:
    """
    Purpose:
        Reset a targeted subset of singleton providers to emulate "spellspace"
        without disturbing unrelated cached providers.
    """
    for t in types_to_reset:
        if t in state.singleton_types:
            state.providers_by_type[t].reset()
    try:
        yield
    finally:
        for t in types_to_reset:
            if t in state.singleton_types:
                state.providers_by_type[t].reset()


def _di_cleanup(state: _DIState) -> None:
    # reset all singletons (best effort)
    for t in state.singleton_types:
        state.providers_by_type[t].reset()
    _gc_cleanup()


# ======================================================================================
# Lagom harness
# ======================================================================================


@dataclass(frozen=True)
class _LagomState:
    """
    Purpose:
        Hold a Lagom base container.
    """
    container: Any

def _build_lagom(
        classes: tuple[type, ...],
        *,
        singleton_types: set[type],
) -> _LagomState:
    """
    Purpose:
        Build Lagom container with explicit definitions (no reflection/autowire).
    Contract:
        - Singleton for types in singleton_types; transient otherwise.
    Notes:
        Lagom only supports resolver arity 0 or 1. Any extra parameters in the
        factory signature (even defaults) count toward arity and will explode.
    """
    pytest.importorskip("lagom")
    from lagom import Container
    from lagom import Singleton

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
            if cls in singleton_types:
                container[cls] = Singleton(cls)
            else:
                container[cls] = _make_leaf_factory(cls)
            continue

        factory = _make_factory(cls, param_specs)
        if cls in singleton_types:
            container[cls] = Singleton(factory)
        else:
            container[cls] = factory

    return _LagomState(container=container)



def _lagom_get(state: _LagomState, cls: type) -> Any:
    return state.container[cls]


def _lagom_cleanup(_state: _LagomState) -> None:
    _gc_cleanup()


# ======================================================================================
# Injector harness (python-injector)
# ======================================================================================


class _SpellspaceScope:  # injector.Scope subclass created below (after import)
    """
    Placeholder type for injector scope binding.
    """
    pass


@dataclass(frozen=True)
class _InjectorState:
    """
    Purpose:
        Hold an Injector instance and spellspace scope type.
    Notes:
        We patch class __init__ with @inject so injector will actually perform
        constructor injection (annotations alone are not enough in modern versions).
    """
    injector: Any
    spellspace_scope_type: type | None
    original_inits: dict[type, Any]


def _build_injector(
        classes: tuple[type, ...],
        *,
        singleton_types: set[type],
        spellspace_types: set[type] | None = None,
) -> _InjectorState:
    """
    Purpose:
        Build Injector container with explicit bindings.
    Contract:
        - Singleton for types in singleton_types.
        - If spellspace_types is provided, those types are cached per spellspace context.
    Notes:
        - Injector(use_annotations=...) was removed in 0.13.0. :contentReference[oaicite:2]{index=2}
        - Injection only happens when callables/constructors are marked injectable
          (e.g. @inject). :contentReference[oaicite:3]{index=3}
        So we patch each class __init__ with @inject for the duration of this container.
    """
    pytest.importorskip("injector")
    from injector import Binder, Injector, Module, Scope, ScopeDecorator, InstanceProvider, singleton, inject

    # Patch constructors so Injector will actually inject.
    original_inits: dict[type, Any] = {}
    for cls in classes:
        original_inits[cls] = cls.__init__
        cls.__init__ = inject(cls.__init__)  # type: ignore[method-assign]

    # Context-var-backed spellspace cache
    cache_var: contextvars.ContextVar[dict[Any, Any] | None] = contextvars.ContextVar(
        "melder_perf_spellspace_cache", default=None
    )

    class SpellspaceScope(Scope):
        """
        Purpose:
            Provide a per-"spellspace" cache for Injector.
        Contract:
            - Outside an entered spellspace, behaves like no caching.
            - Inside a spellspace, caches instances by key in a context-local dict.
        """

        @contextlib.contextmanager
        def enter(self) -> Any:
            token = cache_var.set({})
            try:
                yield
            finally:
                cache_var.reset(token)

        def get(self, key: Any, provider: Any) -> Any:
            cache = cache_var.get()
            if cache is None:
                return provider
            existing = cache.get(key)
            if existing is not None:
                return existing
            instance = provider.get(self.injector)
            wrapped = InstanceProvider(instance)
            cache[key] = wrapped
            return wrapped

    spellspace = ScopeDecorator(SpellspaceScope)

    class PerfModule(Module):
        def configure(self, binder: Binder) -> None:
            for cls in classes:
                if spellspace_types is not None and cls in spellspace_types:
                    binder.bind(cls, to=cls, scope=spellspace)
                elif cls in singleton_types:
                    binder.bind(cls, to=cls, scope=singleton)
                else:
                    binder.bind(cls, to=cls)

    # NOTE: no use_annotations kwarg (removed)
    injector = Injector([PerfModule()])

    scope_type: type | None = SpellspaceScope if spellspace_types is not None else None
    return _InjectorState(injector=injector, spellspace_scope_type=scope_type, original_inits=original_inits)



def _injector_get(state: _InjectorState, cls: type) -> Any:
    return state.injector.get(cls)


@contextlib.contextmanager
def _injector_enter_spellspace(state: _InjectorState) -> Any:
    if state.spellspace_scope_type is None:
        raise AssertionError("Injector spellspace scope not configured for this state")
    scope = state.injector.get(state.spellspace_scope_type)
    with scope.enter():
        yield


def _injector_cleanup(state: _InjectorState) -> None:
    # Restore original constructors
    for cls, orig in state.original_inits.items():
        cls.__init__ = orig  # type: ignore[method-assign]
    _gc_cleanup()



# ======================================================================================
# Dishka harness
# ======================================================================================


@dataclass(frozen=True)
class _DishkaState:
    """
    Purpose:
        Hold a Dishka container.
    """
    container: Any


def _build_dishka(
        classes: tuple[type, ...],
        *,
        scope_name: Any,
        cache_policy: dict[type, bool],
) -> _DishkaState:
    """
    Purpose:
        Build Dishka container programmatically for given classes.
    Contract:
        - Each class is provided via Provider.provide(cls, scope=..., cache=...).
        - Dishka analyzes __init__ typehints automatically.
    """
    pytest.importorskip("dishka")
    from dishka import Provider, make_container

    provider = Provider()
    for cls in classes:
        cache = cache_policy.get(cls, True)
        provider.provide(cls, scope=scope_name, cache=cache)

    container = make_container(provider)
    return _DishkaState(container=container)


def _dishka_get(state: _DishkaState, cls: type) -> Any:
    return state.container.get(cls)


@contextlib.contextmanager
def _dishka_enter_request(state: _DishkaState, *, scope_name: Any | None = None) -> Any:
    # Enter next scope (REQUEST by default) or a specified one if supported
    if scope_name is None:
        with state.container() as nested:
            yield nested
    else:
        with state.container(scope=scope_name) as nested:
            yield nested


def _dishka_cleanup(state: _DishkaState) -> None:
    state.container.close()
    _gc_cleanup()


# ======================================================================================
# Test dispatcher
# ======================================================================================


def _libs() -> tuple[str, ...]:
    return ("dependency-injector", "lagom", "injector", "dishka")


# ======================================================================================
# Deep tests for other containers (Melder excluded)
# ======================================================================================


@pytest.mark.parametrize("lib", _libs())
def test_perf_conjure_scaling_depth3_5_7_9_automatic_other_di(lib: str) -> None:
    """
    Purpose:
        Mirror Melder scaling test (depth 3/5/7/9) for other DI containers.
    Notes:
        - For these libs, "conjure" is interpreted as container build/config time.
    """
    cases = (
        (3, get_depth_3_classes(), Depth3Root),
        (5, get_depth_5_classes(), None),
        (7, get_depth_7_classes(), None),
        (9, get_depth_9_classes(), Depth9Root),
    )

    for depth, classes, root_cls in cases:
        if root_cls is None:
            root_cls = classes[-1]

        if lib == "dependency-injector":
            t0 = time.perf_counter()
            state = _build_dependency_injector(classes, singleton_types=set(classes))
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
            state = _build_lagom(classes, singleton_types=set(classes))
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
            state = _build_injector(classes, singleton_types=set(classes))
            conjure_s = time.perf_counter() - t0
            try:
                t0 = time.perf_counter()
                root = _injector_get(state, root_cls)
                meld_s = time.perf_counter() - t0
                assert isinstance(root, root_cls)
            finally:
                _injector_cleanup(state)

        elif lib == "dishka":
            # Dishka "unique": APP-scope, cache=True
            pytest.importorskip("dishka")
            from dishka import Scope

            cache_policy = {c: True for c in classes}
            t0 = time.perf_counter()
            state = _build_dishka(classes, scope_name=Scope.APP, cache_policy=cache_policy)
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
            f"[{lib}] Perf scaling depth={depth} (ms): "
            f"conjure={_ms(conjure_s):.3f}, "
            f"meld_root_cold={_ms(meld_s):.3f}"
        )


@pytest.mark.parametrize("lib", _libs())
def test_perf_depth9_unique_conjure_and_meld_cold_warm_other_di(lib: str) -> None:
    """
    Purpose:
        Mirror Melder depth-9 unique cold/warm for other DI containers.
    """
    classes = get_depth_9_classes()
    root_cls = Depth9Root

    if lib == "dependency-injector":
        t0 = time.perf_counter()
        state = _build_dependency_injector(classes, singleton_types=set(classes))
        conjure_s = time.perf_counter() - t0
        try:
            t0 = time.perf_counter()
            root1 = _di_get(state, root_cls)
            cold_s = time.perf_counter() - t0
            assert isinstance(root1, Depth9Root)

            t0 = time.perf_counter()
            root2 = _di_get(state, root_cls)
            warm_s = time.perf_counter() - t0
            assert root1 is root2
        finally:
            _di_cleanup(state)

    elif lib == "lagom":
        t0 = time.perf_counter()
        state = _build_lagom(classes, singleton_types=set(classes))
        conjure_s = time.perf_counter() - t0
        try:
            t0 = time.perf_counter()
            root1 = _lagom_get(state, root_cls)
            cold_s = time.perf_counter() - t0
            assert isinstance(root1, Depth9Root)

            t0 = time.perf_counter()
            root2 = _lagom_get(state, root_cls)
            warm_s = time.perf_counter() - t0
            assert root1 is root2
        finally:
            _lagom_cleanup(state)

    elif lib == "injector":
        t0 = time.perf_counter()
        state = _build_injector(classes, singleton_types=set(classes))
        conjure_s = time.perf_counter() - t0
        try:
            t0 = time.perf_counter()
            root1 = _injector_get(state, root_cls)
            cold_s = time.perf_counter() - t0
            assert isinstance(root1, Depth9Root)

            t0 = time.perf_counter()
            root2 = _injector_get(state, root_cls)
            warm_s = time.perf_counter() - t0
            assert root1 is root2
        finally:
            _injector_cleanup(state)

    elif lib == "dishka":
        pytest.importorskip("dishka")
        from dishka import Scope

        cache_policy = {c: True for c in classes}
        t0 = time.perf_counter()
        state = _build_dishka(classes, scope_name=Scope.APP, cache_policy=cache_policy)
        conjure_s = time.perf_counter() - t0
        try:
            t0 = time.perf_counter()
            root1 = _dishka_get(state, root_cls)
            cold_s = time.perf_counter() - t0
            assert isinstance(root1, Depth9Root)

            t0 = time.perf_counter()
            root2 = _dishka_get(state, root_cls)
            warm_s = time.perf_counter() - t0
            assert root1 is root2
        finally:
            _dishka_cleanup(state)

    else:
        raise AssertionError(f"Unknown lib: {lib}")

    print(
        f"[{lib}] Perf depth9 unique (ms/us): "
        f"conjure={_ms(conjure_s):.3f}ms, "
        f"meld_root_cold={_ms(cold_s):.3f}ms, "
        f"meld_root_warm={_us(warm_s):.2f}us"
    )


@pytest.mark.parametrize("lib", _libs())
def test_perf_depth9_many_all_nodes_avg_other_di(lib: str) -> None:
    """
    Purpose:
        Mirror Melder depth-9 many average meld cost.
    """
    classes = get_depth_9_classes()
    root_cls = Depth9Root

    iterations = 250

    if lib == "dependency-injector":
        state = _build_dependency_injector(classes, singleton_types=set())
        try:
            # Warm up
            _ = _di_get(state, root_cls)

            t0 = time.perf_counter()
            leaf_a_id = 0
            leaf_b_id = 0
            for _i in range(iterations):
                root = _di_get(state, root_cls)
                assert isinstance(root, Depth9Root)
                leaf_a_id, leaf_b_id = _depth9_leaf_ids(root)
            total_s = time.perf_counter() - t0
            assert leaf_a_id != 0
            assert leaf_b_id != 0
        finally:
            _di_cleanup(state)

    elif lib == "lagom":
        state = _build_lagom(classes, singleton_types=set())
        try:
            _ = _lagom_get(state, root_cls)

            t0 = time.perf_counter()
            leaf_a_id = 0
            leaf_b_id = 0
            for _i in range(iterations):
                root = _lagom_get(state, root_cls)
                assert isinstance(root, Depth9Root)
                leaf_a_id, leaf_b_id = _depth9_leaf_ids(root)
            total_s = time.perf_counter() - t0
            assert leaf_a_id != 0
            assert leaf_b_id != 0
        finally:
            _lagom_cleanup(state)

    elif lib == "injector":
        state = _build_injector(classes, singleton_types=set())
        try:
            _ = _injector_get(state, root_cls)

            t0 = time.perf_counter()
            leaf_a_id = 0
            leaf_b_id = 0
            for _i in range(iterations):
                root = _injector_get(state, root_cls)
                assert isinstance(root, Depth9Root)
                leaf_a_id, leaf_b_id = _depth9_leaf_ids(root)
            total_s = time.perf_counter() - t0
            assert leaf_a_id != 0
            assert leaf_b_id != 0
        finally:
            _injector_cleanup(state)

    elif lib == "dishka":
        pytest.importorskip("dishka")
        from dishka import Scope

        # Transient: cache=False at APP scope
        cache_policy = {c: False for c in classes}
        state = _build_dishka(classes, scope_name=Scope.APP, cache_policy=cache_policy)
        try:
            _ = _dishka_get(state, root_cls)

            t0 = time.perf_counter()
            leaf_a_id = 0
            leaf_b_id = 0
            for _i in range(iterations):
                root = _dishka_get(state, root_cls)
                assert isinstance(root, Depth9Root)
                leaf_a_id, leaf_b_id = _depth9_leaf_ids(root)
            total_s = time.perf_counter() - t0
            assert leaf_a_id != 0
            assert leaf_b_id != 0
        finally:
            _dishka_cleanup(state)

    else:
        raise AssertionError(f"Unknown lib: {lib}")

    print(
        f"[{lib}] Perf depth9 many (avg over {iterations}) (ms): "
        f"avg_meld_root={_ms(total_s) / iterations:.3f}"
    )


@pytest.mark.parametrize("lib", _libs())
def test_perf_spellspace_depth3_unique_per_spellspace_other_di(lib: str) -> None:
    """
    Purpose:
        Mirror Melder spellspace depth-3 unique-per-spellspace behavior.
    Notes:
        - Implemented as:
            - DI: singleton providers + targeted reset for depth-3 types
            - Lagom: base container + clone per spellspace
            - Injector: custom SpellspaceScope
            - Dishka: REQUEST scope container() context
    """
    classes = get_depth_3_classes()
    root_cls = Depth3Root

    warm_iters = 10_000
    spaces = 200

    if lib == "dependency-injector":
        # singleton for depth3 types, reset only those within spellspace
        state = _build_dependency_injector(classes, singleton_types=set(classes))
        try:
            with _di_reset_singletons(state, types_to_reset=classes):
                t0 = time.perf_counter()
                root1 = _di_get(state, root_cls)
                cold_s = time.perf_counter() - t0
                assert isinstance(root1, Depth3Root)

                t0 = time.perf_counter()
                for _ in range(warm_iters):
                    root2 = _di_get(state, root_cls)
                warm_total_s = time.perf_counter() - t0
                assert root1 is root2

            t0 = time.perf_counter()
            first_id = None
            last_id = None
            for i in range(spaces):
                with _di_reset_singletons(state, types_to_reset=classes):
                    root = _di_get(state, root_cls)
                    if i == 0:
                        first_id = id(root)
                    last_id = id(root)
            total_spaces_s = time.perf_counter() - t0
            assert first_id is not None and last_id is not None
            assert first_id != last_id
        finally:
            _di_cleanup(state)

    elif lib == "lagom":
        # IMPORTANT:
        # - clone() is for overriding deps and can share singleton caches via parent containers.
        # - temporary_singletons([...]) is Lagom's "per invocation / per scope" singleton mechanism.
        base = _build_lagom(classes, singleton_types=set())
        try:
            # One spellspace: cold + warm within the same scope.
            with base.container.temporary_singletons(list(classes)) as space:
                t0 = time.perf_counter()
                root1 = space[root_cls]
                cold_s = time.perf_counter() - t0
                assert isinstance(root1, Depth3Root)

                t0 = time.perf_counter()
                for _ in range(warm_iters):
                    root2 = space[root_cls]
                warm_total_s = time.perf_counter() - t0
                assert root1 is root2

            # Multiple spellspaces: each should get its own instance.
            t0 = time.perf_counter()
            first_root = None
            last_root = None
            for i in range(spaces):
                with base.container.temporary_singletons(list(classes)) as space:
                    root = space[root_cls]
                    if i == 0:
                        first_root = root
                    last_root = root
            total_spaces_s = time.perf_counter() - t0

            assert first_root is not None and last_root is not None
            assert first_root is not last_root
        finally:
            _lagom_cleanup(base)


    elif lib == "injector":
        # bind depth3 types to spellspace scope
        state = _build_injector(classes, singleton_types=set(), spellspace_types=set(classes))
        try:
            with _injector_enter_spellspace(state):
                t0 = time.perf_counter()
                root1 = _injector_get(state, root_cls)
                cold_s = time.perf_counter() - t0
                assert isinstance(root1, Depth3Root)

                t0 = time.perf_counter()
                for _ in range(warm_iters):
                    root2 = _injector_get(state, root_cls)
                warm_total_s = time.perf_counter() - t0
                assert root1 is root2

            t0 = time.perf_counter()
            first_id = None
            last_id = None
            for i in range(spaces):
                with _injector_enter_spellspace(state):
                    root = _injector_get(state, root_cls)
                    if i == 0:
                        first_id = id(root)
                    last_id = id(root)
            total_spaces_s = time.perf_counter() - t0
            assert first_id is not None and last_id is not None
            assert first_id != last_id
        finally:
            _injector_cleanup(state)

    elif lib == "dishka":
        pytest.importorskip("dishka")
        from dishka import Scope

        # request scope caches within spellspace
        cache_policy = {c: True for c in classes}
        state = _build_dishka(classes, scope_name=Scope.REQUEST, cache_policy=cache_policy)
        try:
            with _dishka_enter_request(state) as request_container:
                t0 = time.perf_counter()
                root1 = request_container.get(root_cls)
                cold_s = time.perf_counter() - t0
                assert isinstance(root1, Depth3Root)

                t0 = time.perf_counter()
                for _ in range(warm_iters):
                    root2 = request_container.get(root_cls)
                warm_total_s = time.perf_counter() - t0
                assert root1 is root2

            t0 = time.perf_counter()
            first_id = None
            last_id = None
            for i in range(spaces):
                with _dishka_enter_request(state) as request_container:
                    root = request_container.get(root_cls)
                    if i == 0:
                        first_id = id(root)
                    last_id = id(root)
            total_spaces_s = time.perf_counter() - t0
            assert first_id is not None and last_id is not None
            assert first_id != last_id
        finally:
            _dishka_cleanup(state)

    else:
        raise AssertionError(f"Unknown lib: {lib}")

    print(
        f"[{lib}] Perf spellspace depth3 (ms/us): "
        f"meld_root_cold_in_space={_ms(cold_s):.3f}ms, "
        f"meld_root_warm_avg={_us(warm_total_s) / warm_iters:.2f}us, "
        f"per_spellspace_cold_avg={_ms(total_spaces_s) / spaces:.3f}ms"
    )


@pytest.mark.parametrize("lib", _libs())
def test_perf_depth9_many_with_cached_leaves_and_cleanup_other_di(lib: str) -> None:
    """
    Purpose:
        Mirror Melder "many w/ cached leaves + cleanup" for other DI containers.
    """
    classes = get_depth_9_classes()
    root_cls = Depth9Root
    leaf_types = {Depth9LeafA, Depth9LeafB}

    iterations = 200

    if lib == "dependency-injector":
        state = _build_dependency_injector(classes, singleton_types=set(leaf_types))
        try:
            t0 = time.perf_counter()
            root1 = _di_get(state, root_cls)
            cold_s = time.perf_counter() - t0
            assert isinstance(root1, Depth9Root)
            leaf_a_1, leaf_b_1 = _depth9_leaf_ids(root1)

            root2 = _di_get(state, root_cls)
            assert isinstance(root2, Depth9Root)
            leaf_a_2, leaf_b_2 = _depth9_leaf_ids(root2)
            assert leaf_a_1 == leaf_a_2
            assert leaf_b_1 == leaf_b_2

            t0 = time.perf_counter()
            for _ in range(iterations):
                root = _di_get(state, root_cls)
                assert isinstance(root, Depth9Root)
            total_s = time.perf_counter() - t0

            t0 = time.perf_counter()
            _di_cleanup(state)
            cleanup_s = time.perf_counter() - t0
        finally:
            # already cleaned above
            pass

    elif lib == "lagom":
        state = _build_lagom(classes, singleton_types=set(leaf_types))
        try:
            t0 = time.perf_counter()
            root1 = _lagom_get(state, root_cls)
            cold_s = time.perf_counter() - t0
            assert isinstance(root1, Depth9Root)
            leaf_a_1, leaf_b_1 = _depth9_leaf_ids(root1)

            root2 = _lagom_get(state, root_cls)
            assert isinstance(root2, Depth9Root)
            leaf_a_2, leaf_b_2 = _depth9_leaf_ids(root2)
            assert leaf_a_1 == leaf_a_2
            assert leaf_b_1 == leaf_b_2

            t0 = time.perf_counter()
            for _ in range(iterations):
                root = _lagom_get(state, root_cls)
                assert isinstance(root, Depth9Root)
            total_s = time.perf_counter() - t0

            t0 = time.perf_counter()
            _lagom_cleanup(state)
            cleanup_s = time.perf_counter() - t0
        finally:
            pass

    elif lib == "injector":
        state = _build_injector(classes, singleton_types=set(leaf_types))
        try:
            t0 = time.perf_counter()
            root1 = _injector_get(state, root_cls)
            cold_s = time.perf_counter() - t0
            assert isinstance(root1, Depth9Root)
            leaf_a_1, leaf_b_1 = _depth9_leaf_ids(root1)

            root2 = _injector_get(state, root_cls)
            assert isinstance(root2, Depth9Root)
            leaf_a_2, leaf_b_2 = _depth9_leaf_ids(root2)
            assert leaf_a_1 == leaf_a_2
            assert leaf_b_1 == leaf_b_2

            t0 = time.perf_counter()
            for _ in range(iterations):
                root = _injector_get(state, root_cls)
                assert isinstance(root, Depth9Root)
            total_s = time.perf_counter() - t0

            t0 = time.perf_counter()
            _injector_cleanup(state)
            cleanup_s = time.perf_counter() - t0
        finally:
            pass

    elif lib == "dishka":
        pytest.importorskip("dishka")
        from dishka import Scope

        cache_policy: dict[type, bool] = {}
        for c in classes:
            cache_policy[c] = c in leaf_types  # leaves cached, others transient
        state = _build_dishka(classes, scope_name=Scope.APP, cache_policy=cache_policy)
        try:
            t0 = time.perf_counter()
            root1 = _dishka_get(state, root_cls)
            cold_s = time.perf_counter() - t0
            assert isinstance(root1, Depth9Root)
            leaf_a_1, leaf_b_1 = _depth9_leaf_ids(root1)

            root2 = _dishka_get(state, root_cls)
            assert isinstance(root2, Depth9Root)
            leaf_a_2, leaf_b_2 = _depth9_leaf_ids(root2)
            assert leaf_a_1 == leaf_a_2
            assert leaf_b_1 == leaf_b_2

            t0 = time.perf_counter()
            for _ in range(iterations):
                root = _dishka_get(state, root_cls)
                assert isinstance(root, Depth9Root)
            total_s = time.perf_counter() - t0

            t0 = time.perf_counter()
            _dishka_cleanup(state)
            cleanup_s = time.perf_counter() - t0
        finally:
            pass

    else:
        raise AssertionError(f"Unknown lib: {lib}")

    print(
        f"[{lib}] Perf depth9 many w/ cached leaves (iters={iterations}) (ms): "
        f"meld_root_cold={_ms(cold_s):.3f}, "
        f"avg_meld_root={_ms(total_s) / iterations:.3f}, "
        f"conduit_cleanup={_ms(cleanup_s):.3f}"
    )


@pytest.mark.parametrize("lib", _libs())
def test_perf_mixed_workload_alternating_depth7_depth9_and_spellspace_cleanup_other_di(lib: str) -> None:
    """
    Purpose:
        Mirror Melder mixed workload:
          - Alternate depth9 vs depth7 roots
          - Periodically enter spellspace for depth3 root
          - Measure avg step + spellspace cycle cost + cleanup
    """
    depth9_classes = get_depth_9_classes()
    depth7_classes = get_depth_7_classes()
    depth3_classes = get_depth_3_classes()

    iterations = 200
    spellspace_every = 20

    if lib == "dependency-injector":
        # Main state: depth9 leaf cached, others transient; depth7 transient
        main_classes = tuple(depth9_classes) + tuple(c for c in depth7_classes if c not in depth9_classes)
        leaf_types = {Depth9LeafA, Depth9LeafB}
        main_state = _build_dependency_injector(main_classes, singleton_types=set(leaf_types))
        try:
            # Spellspace: just depth3 singleton with targeted resets (does not touch main leaf cache)
            spell_state = _build_dependency_injector(depth3_classes, singleton_types=set(depth3_classes))

            spellspace_count = 0
            spellspace_total_s = 0.0

            t0 = time.perf_counter()
            for i in range(iterations):
                if i % 2 == 0:
                    root = _di_get(main_state, Depth9Root)
                    assert isinstance(root, Depth9Root)
                else:
                    root = _di_get(main_state, Depth7Root)
                    assert isinstance(root, Depth7Root)

                if (i + 1) % spellspace_every == 0:
                    spellspace_count += 1
                    t_space = time.perf_counter()
                    with _di_reset_singletons(spell_state, types_to_reset=depth3_classes):
                        obj = _di_get(spell_state, Depth3Root)
                        assert isinstance(obj, Depth3Root)
                    spellspace_total_s += time.perf_counter() - t_space

            workload_s = time.perf_counter() - t0

            t0 = time.perf_counter()
            _di_cleanup(spell_state)
            _di_cleanup(main_state)
            cleanup_s = time.perf_counter() - t0
        finally:
            pass

    elif lib == "lagom":
        leaf_types = {Depth9LeafA, Depth9LeafB}
        main_classes = tuple(depth9_classes) + tuple(c for c in depth7_classes if c not in depth9_classes)
        main = _build_lagom(main_classes, singleton_types=set(leaf_types))
        try:
            # Spellspace base: all transient; scoped caching is done via temporary_singletons.
            spell_base = _build_lagom(depth3_classes, singleton_types=set())

            spellspace_count = 0
            spellspace_total_s = 0.0

            t0 = time.perf_counter()
            for i in range(iterations):
                if i % 2 == 0:
                    root = _lagom_get(main, Depth9Root)
                    assert isinstance(root, Depth9Root)
                else:
                    root = _lagom_get(main, Depth7Root)
                    assert isinstance(root, Depth7Root)

                if (i + 1) % spellspace_every == 0:
                    spellspace_count += 1
                    t_space = time.perf_counter()
                    with spell_base.container.temporary_singletons(list(depth3_classes)) as space:
                        obj = space[Depth3Root]
                        assert isinstance(obj, Depth3Root)
                    spellspace_total_s += time.perf_counter() - t_space

            workload_s = time.perf_counter() - t0

            t0 = time.perf_counter()
            _lagom_cleanup(spell_base)
            _lagom_cleanup(main)
            cleanup_s = time.perf_counter() - t0
        finally:
            pass


    elif lib == "injector":
        # Single injector that supports:
        # - depth9 leaves singleton, other depth9 transient
        # - depth7 transient
        # - depth3 cached per spellspace scope
        main_classes = tuple(depth9_classes) + tuple(c for c in depth7_classes if c not in depth9_classes) + tuple(
            c for c in depth3_classes if c not in depth9_classes and c not in depth7_classes
        )
        leaf_types = {Depth9LeafA, Depth9LeafB}
        state = _build_injector(
            main_classes,
            singleton_types=set(leaf_types),
            spellspace_types=set(depth3_classes),
        )
        try:
            spellspace_count = 0
            spellspace_total_s = 0.0

            t0 = time.perf_counter()
            for i in range(iterations):
                if i % 2 == 0:
                    root = _injector_get(state, Depth9Root)
                    assert isinstance(root, Depth9Root)
                else:
                    root = _injector_get(state, Depth7Root)
                    assert isinstance(root, Depth7Root)

                if (i + 1) % spellspace_every == 0:
                    spellspace_count += 1
                    t_space = time.perf_counter()
                    with _injector_enter_spellspace(state):
                        obj = _injector_get(state, Depth3Root)
                        assert isinstance(obj, Depth3Root)
                    spellspace_total_s += time.perf_counter() - t_space

            workload_s = time.perf_counter() - t0

            t0 = time.perf_counter()
            _injector_cleanup(state)
            cleanup_s = time.perf_counter() - t0
        finally:
            pass

    elif lib == "dishka":
        pytest.importorskip("dishka")
        from dishka import Scope

        # One container holding:
        # - depth9 leaves cached at APP, others transient (cache=False)
        # - depth7 transient at APP
        # - depth3 cached per REQUEST spellspace
        all_classes = tuple(depth9_classes) + tuple(c for c in depth7_classes if c not in depth9_classes) + tuple(
            c for c in depth3_classes if c not in depth9_classes and c not in depth7_classes
        )
        leaf_types = {Depth9LeafA, Depth9LeafB}

        provider = pytest.importorskip("dishka").Provider()
        for cls in all_classes:
            if cls in depth3_classes:
                provider.provide(cls, scope=Scope.REQUEST, cache=True)
            else:
                # APP level
                if cls in leaf_types:
                    provider.provide(cls, scope=Scope.APP, cache=True)
                else:
                    provider.provide(cls, scope=Scope.APP, cache=False)

        from dishka import make_container

        container = make_container(provider)
        state = _DishkaState(container=container)

        try:
            spellspace_count = 0
            spellspace_total_s = 0.0

            t0 = time.perf_counter()
            for i in range(iterations):
                if i % 2 == 0:
                    root = state.container.get(Depth9Root)
                    assert isinstance(root, Depth9Root)
                else:
                    root = state.container.get(Depth7Root)
                    assert isinstance(root, Depth7Root)

                if (i + 1) % spellspace_every == 0:
                    spellspace_count += 1
                    t_space = time.perf_counter()
                    with state.container() as request_container:
                        obj = request_container.get(Depth3Root)
                        assert isinstance(obj, Depth3Root)
                    spellspace_total_s += time.perf_counter() - t_space

            workload_s = time.perf_counter() - t0

            t0 = time.perf_counter()
            _dishka_cleanup(state)
            cleanup_s = time.perf_counter() - t0
        finally:
            pass

    else:
        raise AssertionError(f"Unknown lib: {lib}")

    print(
        f"[{lib}] Perf mixed workload (iters={iterations}) (ms): "
        f"avg_step={_ms(workload_s) / iterations:.3f}, "
        f"spellspace_cycles={spellspace_count}, "
        f"avg_spellspace_cycle={_ms(spellspace_total_s) / max(spellspace_count, 1):.3f}, "
        f"conduit_cleanup={_ms(cleanup_s):.3f}"
    )


@pytest.mark.parametrize("lib", _libs())
def test_perf_cycle_conjure_meld_cleanup_depth9_unique_per_container_other_di(lib: str) -> None:
    """
    Purpose:
        Mirror Melder cycle test: build -> resolve -> cleanup (depth9 unique per container).
    Notes:
        - Here "unique_per_conduit" maps to singleton-per-container instance.
    """
    cycles = 10
    classes = get_depth_9_classes()
    root_cls = Depth9Root

    conjure_total = 0.0
    meld_total = 0.0
    cleanup_total = 0.0

    for i in range(cycles):
        if lib == "dependency-injector":
            t0 = time.perf_counter()
            state = _build_dependency_injector(classes, singleton_types=set(classes))
            conjure_s = time.perf_counter() - t0
            conjure_total += conjure_s
            try:
                t0 = time.perf_counter()
                root = _di_get(state, root_cls)
                meld_s = time.perf_counter() - t0
                meld_total += meld_s
                assert isinstance(root, Depth9Root)

                t0 = time.perf_counter()
                _di_cleanup(state)
                cleanup_s = time.perf_counter() - t0
                cleanup_total += cleanup_s
            finally:
                pass

        elif lib == "lagom":
            t0 = time.perf_counter()
            state = _build_lagom(classes, singleton_types=set(classes))
            conjure_s = time.perf_counter() - t0
            conjure_total += conjure_s
            try:
                t0 = time.perf_counter()
                root = _lagom_get(state, root_cls)
                meld_s = time.perf_counter() - t0
                meld_total += meld_s
                assert isinstance(root, Depth9Root)

                t0 = time.perf_counter()
                _lagom_cleanup(state)
                cleanup_s = time.perf_counter() - t0
                cleanup_total += cleanup_s
            finally:
                pass

        elif lib == "injector":
            t0 = time.perf_counter()
            state = _build_injector(classes, singleton_types=set(classes))
            conjure_s = time.perf_counter() - t0
            conjure_total += conjure_s
            try:
                t0 = time.perf_counter()
                root = _injector_get(state, root_cls)
                meld_s = time.perf_counter() - t0
                meld_total += meld_s
                assert isinstance(root, Depth9Root)

                t0 = time.perf_counter()
                _injector_cleanup(state)
                cleanup_s = time.perf_counter() - t0
                cleanup_total += cleanup_s
            finally:
                pass

        elif lib == "dishka":
            pytest.importorskip("dishka")
            from dishka import Scope

            cache_policy = {c: True for c in classes}
            t0 = time.perf_counter()
            state = _build_dishka(classes, scope_name=Scope.APP, cache_policy=cache_policy)
            conjure_s = time.perf_counter() - t0
            conjure_total += conjure_s
            try:
                t0 = time.perf_counter()
                root = _dishka_get(state, root_cls)
                meld_s = time.perf_counter() - t0
                meld_total += meld_s
                assert isinstance(root, Depth9Root)

                t0 = time.perf_counter()
                _dishka_cleanup(state)
                cleanup_s = time.perf_counter() - t0
                cleanup_total += cleanup_s
            finally:
                pass

        else:
            raise AssertionError(f"Unknown lib: {lib}")

    print(
        f"[{lib}] Perf cycle depth9 unique_per_container (cycles={cycles}) (ms): "
        f"avg_conjure={_ms(conjure_total) / cycles:.3f}, "
        f"avg_meld_root={_ms(meld_total) / cycles:.3f}, "
        f"avg_cleanup={_ms(cleanup_total) / cycles:.3f}"
    )


@pytest.mark.parametrize("lib", _libs())
def test_perf_spellspace_depth9_unique_per_spellspace_repeated_cleanup_other_di(lib: str) -> None:
    """
    Purpose:
        Mirror Melder repeated spellspace cycles for depth-9 graph.
    Notes:
        - "unique_per_spellspace" semantics:
            - within a spellspace: cached
            - across spellspaces: new instance
    """
    classes = get_depth_9_classes()
    root_cls = Depth9Root
    spaces = 50

    if lib == "dependency-injector":
        # singleton for all depth9 types, reset only depth9 types per spellspace
        state = _build_dependency_injector(classes, singleton_types=set(classes))
        try:
            t0 = time.perf_counter()
            for _ in range(spaces):
                with _di_reset_singletons(state, types_to_reset=classes):
                    root = _di_get(state, root_cls)
                    assert isinstance(root, Depth9Root)
            total_s = time.perf_counter() - t0
        finally:
            _di_cleanup(state)

    elif lib == "lagom":
        # Per-spellspace caching in Lagom should use temporary_singletons, not clone().
        base = _build_lagom(classes, singleton_types=set())
        try:
            t0 = time.perf_counter()
            for _ in range(spaces):
                with base.container.temporary_singletons(list(classes)) as space:
                    root = space[root_cls]
                    assert isinstance(root, Depth9Root)
            total_s = time.perf_counter() - t0
        finally:
            _lagom_cleanup(base)


    elif lib == "injector":
        # depth9 cached per spellspace scope (not singleton), so each spellspace is isolated
        state = _build_injector(classes, singleton_types=set(), spellspace_types=set(classes))
        try:
            t0 = time.perf_counter()
            for _ in range(spaces):
                with _injector_enter_spellspace(state):
                    root = _injector_get(state, root_cls)
                    assert isinstance(root, Depth9Root)
            total_s = time.perf_counter() - t0
        finally:
            _injector_cleanup(state)

    elif lib == "dishka":
        pytest.importorskip("dishka")
        from dishka import Scope

        # request scope per spellspace
        cache_policy = {c: True for c in classes}
        state = _build_dishka(classes, scope_name=Scope.REQUEST, cache_policy=cache_policy)
        try:
            t0 = time.perf_counter()
            for _ in range(spaces):
                with _dishka_enter_request(state) as request_container:
                    root = request_container.get(root_cls)
                    assert isinstance(root, Depth9Root)
            total_s = time.perf_counter() - t0
        finally:
            _dishka_cleanup(state)

    else:
        raise AssertionError(f"Unknown lib: {lib}")

    print(
        f"[{lib}] Perf spellspace depth9 (spaces={spaces}) (ms): "
        f"avg_cycle={_ms(total_s) / spaces:.3f}"
    )
