"""
Purpose:
    Standalone cProfile harness for the deep transient DI benchmark.

Contract:
    - Mirrors benchmarks/testing_other_di/test_deep_all_di_transient_only_no_singletons.py
      workloads without pytest.
    - Uses in-file configuration (ProfileConfig) with no CLI args.
    - Profiles only the resolve loop by default (setup is outside the profile).
"""

import cProfile
import functools
import gc
import importlib
import inspect
import io
import logging
import pstats
import time
from typing import Any, Callable, Dict, Sequence, Tuple, Type

from tests.mocks.spellbook.deep_layers import (
    Depth7Root,
    Depth9Root,
    get_depth_7_classes,
    get_depth_9_classes,
)

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.helpers.init_helpers import InitHelpers
from melder.utilities.logger.safe_logger import SafeLogger


class ProfileConfig:
    """
    In-file configuration for the profiling harness.

    Purpose:
        Centralize knobs for iterations, libraries, and pstats output.

    Contract:
        - Edit class attributes directly to change profiling behavior.
        - No CLI parsing is performed.
    """
    __slots__ = ()

    ITERATIONS: int = 200
    PROFILE_MODE: str = "depth9_avg"  # Options: "depth9_avg", "mixed"
    PROFILE_LIBS: Tuple[str, ...] = (
        "melder",
        "dependency-injector",
        "lagom",
        "injector",
        "dishka",
    )
    WARMUP: int = 1
    SORT_BY: str = "cumtime"
    TOP_N: int = 40


def _build_logger() -> SafeLogger:
    """
    Build a SafeLogger backed by stdlib logging.

    Contract:
        - Configures a basic stdout logger for profile summaries.
        - Returns a SafeLogger wrapper for consistent logging calls.

    Returns:
        SafeLogger: Logger for profile output.
    """
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    base_logger = logging.getLogger("benchmarks.profile")
    return InitHelpers.resolve_safe_logger(base_logger)


def _log_lines(logger: SafeLogger, header: str, lines: Sequence[str]) -> None:
    """
    Emit a header and a block of lines through SafeLogger.

    Args:
        logger: SafeLogger used for output.
        header: Header line to emit before the block.
        lines: Lines to emit in order.
    """
    logger.info(header, "_log_lines")
    for line in lines:
        logger.info(line, "_log_lines")


def _gc_cleanup() -> None:
    """
    Force a garbage-collection pass.

    Contract:
        - Calls gc.collect() once.
    """
    gc.collect()


def _depth9_leaf_ids(root: Depth9Root) -> Tuple[int, int]:
    """
    Extract leaf instance ids from a Depth9Root for validation.

    Args:
        root: Depth9Root instance.

    Returns:
        Tuple[int, int]: (id(left_leaf), id(right_leaf)).
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


def _ctor_param_types(cls: Type[Any]) -> Tuple[Tuple[str, Type[Any]], ...]:
    """
    Extract typed constructor parameters for a class.

    Args:
        cls: Class to inspect.

    Returns:
        Tuple[Tuple[str, Type[Any]], ...]: Sequence of (param_name, param_type).

    Raises:
        AssertionError: If any constructor parameter lacks a type annotation.
    """
    sig = inspect.signature(cls.__init__)
    params = list(sig.parameters.values())[1:]
    out: list[Tuple[str, Type[Any]]] = []
    for param in params:
        if param.annotation is inspect._empty:
            raise AssertionError(
                "{0}.__init__ param '{1}' missing annotation".format(
                    cls.__name__,
                    param.name,
                )
            )
        if not isinstance(param.annotation, type):
            raise AssertionError(
                "{0}.__init__ param '{1}' has non-type annotation: {2!r}".format(
                    cls.__name__,
                    param.name,
                    param.annotation,
                )
            )
        out.append((param.name, param.annotation))
    return tuple(out)


def _reset_aether_singleton() -> None:
    """
    Reset the Melder Aether singleton to avoid cross-run contamination.

    Contract:
        - Resets Aether, Spellbook, and Conduit singleton references.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _melder_build_transient(
        *,
        frame: str,
        classes: Tuple[Type[Any], ...],
        root_cls: Type[Any],
) -> Dict[str, Any]:
    """
    Build a transient-only Melder spellbook and conduit.

    Args:
        frame: Aetheric frame name for isolation.
        classes: Classes to bind as transient spells.
        root_cls: Root class used for resolution.

    Returns:
        Dict[str, Any]: State bundle for melder profiling.
    """
    spellbook = Spellbook(aetheric_frame=frame)
    cfg = spellbook.get_configuration()
    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)

    t0 = time.perf_counter()
    spell_ids: Dict[Type[Any], str] = {}
    for cls in classes:
        spell_ids[cls] = spellbook.bind(
            spell=cls,
            existence=Existence.many,
            permissions="create",
        )
    bind_s = time.perf_counter() - t0

    root_id = spell_ids[root_cls]

    t0 = time.perf_counter()
    conduit = spellbook.conjure(name=frame)
    conjure_s = time.perf_counter() - t0

    return {
        "conduit": conduit,
        "root_id": root_id,
        "spell_ids": spell_ids,
        "bind_s": bind_s,
        "conjure_s": conjure_s,
    }


def _melder_get_root(state: Dict[str, Any]) -> Any:
    """
    Resolve the root spell from a Melder profiling state.

    Args:
        state: Melder profiling state dict.

    Returns:
        Any: Resolved root instance.
    """
    return state["conduit"].meld(spell=state["root_id"])


def _melder_get_by_id(state: Dict[str, Any], spell_id: str) -> Any:
    """
    Resolve a spell by id using a Melder profiling state.

    Args:
        state: Melder profiling state dict.
        spell_id: Spell id to resolve.

    Returns:
        Any: Resolved instance.
    """
    return state["conduit"].meld(spell=spell_id)


def _melder_cleanup(state: Dict[str, Any]) -> None:
    """
    Cleanup Melder profiling state and reset global singleton.

    Args:
        state: Melder profiling state dict.
    """
    state["conduit"].cleanup()
    _gc_cleanup()
    _reset_aether_singleton()


def _build_dependency_injector_transient(
        classes: Tuple[Type[Any], ...],
) -> Dict[str, Any]:
    """
    Build a dependency-injector container with transient providers.

    Args:
        classes: Classes to register in order.

    Returns:
        Dict[str, Any]: Profiling state dict.
    """
    providers_module = importlib.import_module("dependency_injector.providers")
    providers = providers_module

    providers_by_type: Dict[Type[Any], Any] = {}
    for cls in classes:
        param_specs = _ctor_param_types(cls)
        kwargs: Dict[str, Any] = {}
        for pname, ptype in param_specs:
            dep = providers_by_type.get(ptype)
            if dep is None:
                raise AssertionError(
                    "DI wiring error: {0} depends on {1} before it was registered".format(
                        cls.__name__,
                        ptype.__name__,
                    )
                )
            kwargs[pname] = dep
        providers_by_type[cls] = providers.Factory(cls, **kwargs)
    return {"providers_by_type": providers_by_type}


def _di_get_root(state: Dict[str, Any], root_cls: Type[Any]) -> Any:
    """
    Resolve the root instance using dependency-injector state.

    Args:
        state: dependency-injector state dict.
        root_cls: Root class to resolve.

    Returns:
        Any: Resolved root instance.
    """
    return state["providers_by_type"][root_cls]()


def _di_cleanup(_state: Dict[str, Any]) -> None:
    """
    Cleanup dependency-injector profiling state.

    Args:
        _state: dependency-injector state dict.
    """
    _gc_cleanup()


def _build_lagom_transient(classes: Tuple[Type[Any], ...]) -> Dict[str, Any]:
    """
    Build a Lagom container with transient factories.

    Args:
        classes: Classes to register in order.

    Returns:
        Dict[str, Any]: Profiling state dict.
    """
    module = importlib.import_module("lagom")
    container = module.Container()

    def _make_leaf_factory(target_cls: Type[Any]) -> Callable[[], Any]:
        """
        Build a zero-arg factory for a leaf node.

        Args:
            target_cls: Leaf class.

        Returns:
            Callable[[], Any]: Factory function.
        """
        def factory() -> Any:
            """
            Instantiate a leaf class with no arguments.

            Returns:
                Any: New instance.
            """
            return target_cls()
        return factory

    def _make_factory(
            target_cls: Type[Any],
            param_specs: Tuple[Tuple[str, Type[Any]], ...],
    ) -> Callable[[Any], Any]:
        """
        Build a Lagom factory for a class with dependencies.

        Args:
            target_cls: Class to construct.
            param_specs: Constructor parameter specs.

        Returns:
            Callable[[Any], Any]: Lagom factory.
        """
        def factory(container_obj: Any) -> Any:
            """
            Instantiate a class using Lagom container lookups.

            Args:
                container_obj: Lagom container.

            Returns:
                Any: New instance.
            """
            kwargs = {pname: container_obj[ptype] for pname, ptype in param_specs}
            return target_cls(**kwargs)
        return factory

    for cls in classes:
        param_specs = _ctor_param_types(cls)
        if not param_specs:
            container[cls] = _make_leaf_factory(cls)
        else:
            container[cls] = _make_factory(cls, param_specs)

    return {"container": container}


def _lagom_get_root(state: Dict[str, Any], root_cls: Type[Any]) -> Any:
    """
    Resolve the root instance using a Lagom container.

    Args:
        state: Lagom profiling state dict.
        root_cls: Root class to resolve.

    Returns:
        Any: Resolved root instance.
    """
    return state["container"][root_cls]


def _lagom_cleanup(_state: Dict[str, Any]) -> None:
    """
    Cleanup Lagom profiling state.

    Args:
        _state: Lagom profiling state dict.
    """
    _gc_cleanup()


def _build_injector_transient(classes: Tuple[Type[Any], ...]) -> Dict[str, Any]:
    """
    Build an Injector container with transient bindings.

    Args:
        classes: Classes to register in order.

    Returns:
        Dict[str, Any]: Profiling state dict.
    """
    module = importlib.import_module("injector")
    Binder = module.Binder
    Injector = module.Injector
    Module = module.Module
    inject = module.inject

    original_inits: Dict[Type[Any], Any] = {}
    for cls in classes:
        original_inits[cls] = cls.__init__
        cls.__init__ = inject(cls.__init__)

    class PerfModule(Module):
        """
        Injector module used for profiling.

        Purpose:
            Register transient bindings for the target classes.

        Contract:
            - Binds each class directly to itself (no singleton scope).
        """
        def configure(self, binder: Binder) -> None:
            """
            Bind all classes as transient providers.

            Args:
                binder: Injector binder.
            """
            for cls in classes:
                binder.bind(cls, to=cls)

    injector = Injector([PerfModule()])
    return {"injector": injector, "original_inits": original_inits}


def _injector_get_root(state: Dict[str, Any], root_cls: Type[Any]) -> Any:
    """
    Resolve the root instance using Injector.

    Args:
        state: Injector profiling state dict.
        root_cls: Root class to resolve.

    Returns:
        Any: Resolved root instance.
    """
    return state["injector"].get(root_cls)


def _injector_cleanup(state: Dict[str, Any]) -> None:
    """
    Cleanup Injector profiling state and restore patched constructors.

    Args:
        state: Injector profiling state dict.
    """
    for cls, orig in state["original_inits"].items():
        cls.__init__ = orig
    _gc_cleanup()


def _build_dishka_transient(classes: Tuple[Type[Any], ...]) -> Dict[str, Any]:
    """
    Build a Dishka container with caching disabled.

    Args:
        classes: Classes to register in order.

    Returns:
        Dict[str, Any]: Profiling state dict.
    """
    module = importlib.import_module("dishka")
    Provider = module.Provider
    Scope = module.Scope
    make_container = module.make_container

    provider = Provider()
    for cls in classes:
        provider.provide(cls, scope=Scope.APP, cache=False)

    container = make_container(provider)
    return {"container": container}


def _dishka_get_root(state: Dict[str, Any], root_cls: Type[Any]) -> Any:
    """
    Resolve the root instance using Dishka.

    Args:
        state: Dishka profiling state dict.
        root_cls: Root class to resolve.

    Returns:
        Any: Resolved root instance.
    """
    return state["container"].get(root_cls)


def _dishka_cleanup(state: Dict[str, Any]) -> None:
    """
    Cleanup Dishka profiling state.

    Args:
        state: Dishka profiling state dict.
    """
    state["container"].close()
    _gc_cleanup()


def _module_available(module_name: str) -> bool:
    """
    Check whether a module can be imported.

    Args:
        module_name: Module import name.

    Returns:
        bool: True if import succeeds; False otherwise.
    """
    try:
        importlib.import_module(module_name)
        return True
    except Exception:
        return False


def _run_loop(get_fn: Callable[[], Any], iterations: int) -> None:
    """
    Run a simple resolve loop for profiling.

    Args:
        get_fn: Zero-arg callable that returns the root instance.
        iterations: Number of iterations to execute.
    """
    for _ in range(iterations):
        get_fn()


def _run_mixed_loop(
        get_fn_a: Callable[[], Any],
        get_fn_b: Callable[[], Any],
        iterations: int,
) -> None:
    """
    Run a mixed workload alternating between two roots.

    Args:
        get_fn_a: Callable for even iterations.
        get_fn_b: Callable for odd iterations.
        iterations: Total iterations to execute.
    """
    for i in range(iterations):
        if i % 2 == 0:
            get_fn_a()
        else:
            get_fn_b()


def _profile_loop(
        *,
        label: str,
        run_fn: Callable[[], None],
        logger: SafeLogger,
) -> None:
    """
    Profile a callable and emit cProfile summaries.

    Args:
        label: Label for the profile output.
        run_fn: Callable to profile.
        logger: SafeLogger for output.
    """
    profiler = cProfile.Profile()
    start = time.perf_counter()
    profiler.activate()
    run_fn()
    profiler.disable()
    elapsed_s = time.perf_counter() - start

    logger.info(
        "[{0}] profiled in {1:.3f}ms".format(label, elapsed_s * 1000.0),
        "_profile_loop",
    )

    output = io.StringIO()
    stats = pstats.Stats(profiler, stream=output)
    stats.strip_dirs()
    stats.sort_stats(ProfileConfig.SORT_BY)
    stats.print_stats(ProfileConfig.TOP_N)
    text = output.getvalue().strip()
    if not text:
        logger.info("[{0}] no stats collected".format(label), "_profile_loop")
        return

    _log_lines(
        logger,
        "[{0}] top {1} sorted by {2}".format(
            label,
            ProfileConfig.TOP_N,
            ProfileConfig.SORT_BY,
        ),
        text.splitlines(),
    )


def _profile_melder(logger: SafeLogger) -> None:
    """
    Profile Melder for the configured workload.

    Args:
        logger: SafeLogger for output.
    """
    _reset_aether_singleton()
    classes_9 = get_depth_9_classes()
    classes_7 = get_depth_7_classes()

    if ProfileConfig.PROFILE_MODE == "mixed":
        all_classes = tuple(classes_9) + tuple(c for c in classes_7 if c not in classes_9)
        state = _melder_build_transient(
            frame="profile-mixed",
            classes=all_classes,
            root_cls=Depth9Root,
        )
        try:
            root9 = _melder_get_root(state)
            if not isinstance(root9, Depth9Root):
                raise AssertionError("Melder root9 mismatch")
            root7_id = state["spell_ids"][Depth7Root]
            root7 = _melder_get_by_id(state, root7_id)
            if not isinstance(root7, Depth7Root):
                raise AssertionError("Melder root7 mismatch")

            get_root9 = functools.partial(_melder_get_root, state)
            get_root7 = functools.partial(_melder_get_by_id, state, root7_id)
            run_fn = functools.partial(
                _run_mixed_loop,
                get_root9,
                get_root7,
                ProfileConfig.ITERATIONS,
            )

            _profile_loop(label="melder-mixed", run_fn=run_fn, logger=logger)
        finally:
            _melder_cleanup(state)
        return

    state = _melder_build_transient(
        frame="profile-depth9",
        classes=classes_9,
        root_cls=Depth9Root,
    )
    try:
        root = _melder_get_root(state)
        if not isinstance(root, Depth9Root):
            raise AssertionError("Melder root mismatch")
        _depth9_leaf_ids(root)

        run_fn = functools.partial(
            _run_loop,
            functools.partial(_melder_get_root, state),
            ProfileConfig.ITERATIONS,
        )
        _profile_loop(label="melder-depth9", run_fn=run_fn, logger=logger)
    finally:
        _melder_cleanup(state)


def _profile_dependency_injector(logger: SafeLogger) -> None:
    """
    Profile dependency-injector for the configured workload.

    Args:
        logger: SafeLogger for output.
    """
    if not _module_available("dependency_injector"):
        logger.info(
            "[dependency-injector] skipped (module missing)",
            "_profile_dependency_injector",
        )
        return
    if not _module_available("dependency_injector.providers"):
        logger.info(
            "[dependency-injector] skipped (providers submodule missing)",
            "_profile_dependency_injector",
        )
        return

    classes_9 = get_depth_9_classes()
    classes_7 = get_depth_7_classes()

    if ProfileConfig.PROFILE_MODE == "mixed":
        all_classes = tuple(classes_9) + tuple(c for c in classes_7 if c not in classes_9)
        state = _build_dependency_injector_transient(all_classes)
        try:
            root9 = _di_get_root(state, Depth9Root)
            root7 = _di_get_root(state, Depth7Root)
            if not isinstance(root9, Depth9Root) or not isinstance(root7, Depth7Root):
                raise AssertionError("dependency-injector root mismatch")

            run_fn = functools.partial(
                _run_mixed_loop,
                functools.partial(_di_get_root, state, Depth9Root),
                functools.partial(_di_get_root, state, Depth7Root),
                ProfileConfig.ITERATIONS,
            )
            _profile_loop(label="dependency-injector-mixed", run_fn=run_fn, logger=logger)
        finally:
            _di_cleanup(state)
        return

    state = _build_dependency_injector_transient(classes_9)
    try:
        root = _di_get_root(state, Depth9Root)
        if not isinstance(root, Depth9Root):
            raise AssertionError("dependency-injector root mismatch")
        _depth9_leaf_ids(root)

        run_fn = functools.partial(
            _run_loop,
            functools.partial(_di_get_root, state, Depth9Root),
            ProfileConfig.ITERATIONS,
        )
        _profile_loop(label="dependency-injector-depth9", run_fn=run_fn, logger=logger)
    finally:
        _di_cleanup(state)


def _profile_lagom(logger: SafeLogger) -> None:
    """
    Profile Lagom for the configured workload.

    Args:
        logger: SafeLogger for output.
    """
    if not _module_available("lagom"):
        logger.info("[lagom] skipped (module missing)", "_profile_lagom")
        return

    classes_9 = get_depth_9_classes()
    classes_7 = get_depth_7_classes()

    if ProfileConfig.PROFILE_MODE == "mixed":
        all_classes = tuple(classes_9) + tuple(c for c in classes_7 if c not in classes_9)
        state = _build_lagom_transient(all_classes)
        try:
            root9 = _lagom_get_root(state, Depth9Root)
            root7 = _lagom_get_root(state, Depth7Root)
            if not isinstance(root9, Depth9Root) or not isinstance(root7, Depth7Root):
                raise AssertionError("lagom root mismatch")

            run_fn = functools.partial(
                _run_mixed_loop,
                functools.partial(_lagom_get_root, state, Depth9Root),
                functools.partial(_lagom_get_root, state, Depth7Root),
                ProfileConfig.ITERATIONS,
            )
            _profile_loop(label="lagom-mixed", run_fn=run_fn, logger=logger)
        finally:
            _lagom_cleanup(state)
        return

    state = _build_lagom_transient(classes_9)
    try:
        root = _lagom_get_root(state, Depth9Root)
        if not isinstance(root, Depth9Root):
            raise AssertionError("lagom root mismatch")
        _depth9_leaf_ids(root)

        run_fn = functools.partial(
            _run_loop,
            functools.partial(_lagom_get_root, state, Depth9Root),
            ProfileConfig.ITERATIONS,
        )
        _profile_loop(label="lagom-depth9", run_fn=run_fn, logger=logger)
    finally:
        _lagom_cleanup(state)


def _profile_injector(logger: SafeLogger) -> None:
    """
    Profile Injector for the configured workload.

    Args:
        logger: SafeLogger for output.
    """
    if not _module_available("injector"):
        logger.info("[injector] skipped (module missing)", "_profile_injector")
        return

    classes_9 = get_depth_9_classes()
    classes_7 = get_depth_7_classes()

    if ProfileConfig.PROFILE_MODE == "mixed":
        all_classes = tuple(classes_9) + tuple(c for c in classes_7 if c not in classes_9)
        state = _build_injector_transient(all_classes)
        try:
            root9 = _injector_get_root(state, Depth9Root)
            root7 = _injector_get_root(state, Depth7Root)
            if not isinstance(root9, Depth9Root) or not isinstance(root7, Depth7Root):
                raise AssertionError("injector root mismatch")

            run_fn = functools.partial(
                _run_mixed_loop,
                functools.partial(_injector_get_root, state, Depth9Root),
                functools.partial(_injector_get_root, state, Depth7Root),
                ProfileConfig.ITERATIONS,
            )
            _profile_loop(label="injector-mixed", run_fn=run_fn, logger=logger)
        finally:
            _injector_cleanup(state)
        return

    state = _build_injector_transient(classes_9)
    try:
        root = _injector_get_root(state, Depth9Root)
        if not isinstance(root, Depth9Root):
            raise AssertionError("injector root mismatch")
        _depth9_leaf_ids(root)

        run_fn = functools.partial(
            _run_loop,
            functools.partial(_injector_get_root, state, Depth9Root),
            ProfileConfig.ITERATIONS,
        )
        _profile_loop(label="injector-depth9", run_fn=run_fn, logger=logger)
    finally:
        _injector_cleanup(state)


def _profile_dishka(logger: SafeLogger) -> None:
    """
    Profile Dishka for the configured workload.

    Args:
        logger: SafeLogger for output.
    """
    if not _module_available("dishka"):
        logger.info("[dishka] skipped (module missing)", "_profile_dishka")
        return

    classes_9 = get_depth_9_classes()
    classes_7 = get_depth_7_classes()

    if ProfileConfig.PROFILE_MODE == "mixed":
        all_classes = tuple(classes_9) + tuple(c for c in classes_7 if c not in classes_9)
        state = _build_dishka_transient(all_classes)
        try:
            root9 = _dishka_get_root(state, Depth9Root)
            root7 = _dishka_get_root(state, Depth7Root)
            if not isinstance(root9, Depth9Root) or not isinstance(root7, Depth7Root):
                raise AssertionError("dishka root mismatch")

            run_fn = functools.partial(
                _run_mixed_loop,
                functools.partial(_dishka_get_root, state, Depth9Root),
                functools.partial(_dishka_get_root, state, Depth7Root),
                ProfileConfig.ITERATIONS,
            )
            _profile_loop(label="dishka-mixed", run_fn=run_fn, logger=logger)
        finally:
            _dishka_cleanup(state)
        return

    state = _build_dishka_transient(classes_9)
    try:
        root = _dishka_get_root(state, Depth9Root)
        if not isinstance(root, Depth9Root):
            raise AssertionError("dishka root mismatch")
        _depth9_leaf_ids(root)

        run_fn = functools.partial(
            _run_loop,
            functools.partial(_dishka_get_root, state, Depth9Root),
            ProfileConfig.ITERATIONS,
        )
        _profile_loop(label="dishka-depth9", run_fn=run_fn, logger=logger)
    finally:
        _dishka_cleanup(state)


def main() -> None:
    """
    Entry point for the profiling harness.

    Purpose:
        Run the configured profiling passes and emit summaries.

    Contract:
        - Honors ProfileConfig settings.
        - Profiles libraries in the listed order.
    """
    logger = _build_logger()
    logger.info(
        "Profile mode={0}, iterations={1}".format(
            ProfileConfig.PROFILE_MODE,
            ProfileConfig.ITERATIONS,
        ),
        "main",
    )

    for lib in ProfileConfig.PROFILE_LIBS:
        if lib == "melder":
            _profile_melder(logger)
        elif lib == "dependency-injector":
            _profile_dependency_injector(logger)
        elif lib == "lagom":
            _profile_lagom(logger)
        elif lib == "injector":
            _profile_injector(logger)
        elif lib == "dishka":
            _profile_dishka(logger)
        else:
            logger.info("Unknown lib '{0}'".format(lib), "main")


if __name__ == "__main__":
    main()
