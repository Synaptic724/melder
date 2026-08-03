"""
Purpose:
    Direct (non-scheduler) build-phase benchmark for Melder vs other DI libs.

Contract:
    - Runs Melder phases directly on spells (no PhaseScheduler).
    - Benchmarks build/registration only for other DI libs.
    - Uses in-file configuration (ProfileConfig) with no CLI args.
"""

from __future__ import annotations

import cProfile
import gc
import importlib
import io
import logging
import pstats
import time
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Optional, Sequence, Tuple

from tests.mocks.spellbook.deep_layers import get_depth_9_classes

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.helpers.init_helpers import InitHelpers
from melder.utilities.logger.safe_logger import SafeLogger


class ProfileConfig:
    """
    In-file configuration for the profiling harness.
    """

    __slots__ = ()

    ITERATIONS: int = 1
    PROFILE_LIBS: Tuple[str, ...] = (
        "melder",
        "dependency-injector",
        "lagom",
        "injector",
        "dishka",
    )
    SORT_BY: str = "cumtime"
    TOP_N: int = 40
    FRAME_NAME: str = "bench-build-direct"
    CONJURE_NAME: str = "bench-build-direct"
    VERBOSE_PROGRESS: bool = True

    # Direct phases to run (build-only).
    MELDER_PHASES: Tuple[str, ...] = (
        "requirements",
        "symbolic_graph",
        "local_frame",
        "validation",
        "root_blueprints",
        "occurrence_plan",
        "injection_plan",
        "patch_maps",
        "system_validation",
        "change_control",
        "execution_plan",
    )

    # Bench-only safety toggles (enable if your local build hangs).
    MELDER_SKIP_DUPLICATE_NAME_VALIDATION: bool = True
    MELDER_SKIP_CONTRACT_SIGNATURE_SCAN: bool = True
    MELDER_PATCH_ID_BUILDER: bool = True


def _build_logger() -> SafeLogger:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    base_logger = logging.getLogger("benchmarks.profile")
    return InitHelpers.resolve_safe_logger(base_logger)


def _log_lines(logger: SafeLogger, header: str, lines: Sequence[str]) -> None:
    logger.info(header, "_log_lines")
    for line in lines:
        logger.info(line, "_log_lines")


def _gc_cleanup() -> None:
    gc.collect()


def _maybe_import(module_name: str) -> Optional[Any]:
    try:
        return importlib.import_module(module_name)
    except Exception:
        return None


def _reset_aether_singleton() -> None:
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _patch_melder_skip_duplicate_spell_name_validation(skip_validation: bool) -> Callable[[], None]:
    if not skip_validation:
        return lambda: None
    from melder.aether.spellbook.spell_compiler.validation.strategies.duplicate_spell_name_strategy import (
        DuplicateSpellNameStrategy,
    )

    original = DuplicateSpellNameStrategy.validate

    def _noop(self: DuplicateSpellNameStrategy, *args: Any, **kwargs: Any) -> None:
        return None

    DuplicateSpellNameStrategy.validate = _noop

    def _restore() -> None:
        DuplicateSpellNameStrategy.validate = original

    return _restore


def _patch_melder_skip_contract_signature_scan(skip_scan: bool) -> Callable[[], None]:
    if not skip_scan:
        return lambda: None
    from melder.aether.spellbook.spell_compiler.blueprints.occurrence_plan import OccurrencePlanBuilder

    original = OccurrencePlanBuilder._iter_spell_contract_defaults

    def _noop(self: OccurrencePlanBuilder, spell: Any) -> tuple:
        return ()

    OccurrencePlanBuilder._iter_spell_contract_defaults = _noop

    def _restore() -> None:
        OccurrencePlanBuilder._iter_spell_contract_defaults = original

    return _restore


def _patch_melder_id_builder(use_fast_ids: bool) -> Callable[[], None]:
    if not use_fast_ids:
        return lambda: None
    from melder.utilities.helpers import id_builder as id_builder_module

    original = id_builder_module.IDBuilder.create_id
    counter = {"n": 0}

    def _fast_id() -> str:
        counter["n"] += 1
        return f"bench-id-{counter['n']}"

    id_builder_module.IDBuilder.create_id = staticmethod(_fast_id)

    def _restore() -> None:
        id_builder_module.IDBuilder.create_id = original

    return _restore


@dataclass(frozen=True)
class _MelderState:
    spellbook: Spellbook
    spells: tuple[Any, ...]


def _build_melder_bind_only(classes: Iterable[type]) -> _MelderState:
    _reset_aether_singleton()
    spellbook = Spellbook(aetheric_frame=ProfileConfig.FRAME_NAME)
    cfg = spellbook.get_configuration()
    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)
    for cls in classes:
        spellbook.bind(
            spell=cls,
            existence=Existence.many,
            permissions="create",
        )
    spells = tuple(spellbook._spells.values())
    return _MelderState(spellbook=spellbook, spells=spells)


def _run_melder_phases_direct(state: _MelderState, *, conduit_id: str) -> None:
    phases = ProfileConfig.MELDER_PHASES
    for phase in phases:
        if phase == "requirements":
            for spell in state.spells:
                spell.run_phase_requirements(cancel_event=None)
        elif phase == "symbolic_graph":
            for spell in state.spells:
                spell.run_phase_symbolic_graph(cancel_event=None)
        elif phase == "local_frame":
            for spell in state.spells:
                spell.run_phase_local_frame(cancel_event=None)
        elif phase == "validation":
            for spell in state.spells:
                spell.run_phase_validation(cancel_event=None)
        elif phase == "root_blueprints":
            for spell in state.spells:
                spell.run_phase_root_blueprints(conduit_id=conduit_id, cancel_event=None)
        elif phase == "occurrence_plan":
            for spell in state.spells:
                spell.run_phase_occurrence_plan(conduit_id=conduit_id, cancel_event=None)
        elif phase == "injection_plan":
            for spell in state.spells:
                spell.run_phase_injection_plan(conduit_id=conduit_id, cancel_event=None)
        elif phase == "patch_maps":
            for spell in state.spells:
                spell.run_phase_patch_maps(conduit_id=conduit_id, cancel_event=None)
        elif phase == "execution_plan":
            for spell in state.spells:
                spell.run_phase_execution_plan(conduit_id=conduit_id, cancel_event=None)
        elif phase == "system_validation":
            for spell in state.spells:
                spell.run_phase_system_validation(conduit_id=conduit_id, cancel_event=None)
        elif phase == "change_control":
            for spell in state.spells:
                spell.run_phase_change_control(conduit_id=conduit_id, cancel_event=None)
        else:
            raise ValueError(f"Unknown phase: {phase}")


def _cleanup_melder(state: _MelderState) -> None:
    for spell in state.spells:
        try:
            spell.cleanup()
        except Exception:
            pass
    _gc_cleanup()


@dataclass(frozen=True)
class _DIState:
    providers_by_type: dict[type, Any]


def _build_dependency_injector_transient(classes: tuple[type, ...]) -> _DIState:
    dependency_injector = _maybe_import("dependency_injector")
    if dependency_injector is None:
        raise RuntimeError("dependency_injector not installed")
    from dependency_injector import providers

    providers_by_type: dict[type, Any] = {}
    for cls in classes:
        params = cls.__init__.__annotations__
        kwargs: dict[str, Any] = {}
        for name, ptype in params.items():
            if name == "return":
                continue
            dep = providers_by_type.get(ptype)
            if dep is None:
                raise AssertionError(
                    f"DI wiring error: {cls.__name__} depends on {ptype.__name__} before it was registered"
                )
            kwargs[name] = dep
        providers_by_type[cls] = providers.Factory(cls, **kwargs)
    return _DIState(providers_by_type=providers_by_type)


def _cleanup_di(_state: _DIState) -> None:
    _gc_cleanup()


@dataclass(frozen=True)
class _LagomState:
    container: Any


def _build_lagom_transient(classes: tuple[type, ...]) -> _LagomState:
    lagom = _maybe_import("lagom")
    if lagom is None:
        raise RuntimeError("lagom not installed")
    from lagom import Container

    container = Container()

    for cls in classes:
        def _make_factory(_cls: type) -> Callable[[Any], Any]:
            def factory(c: Any) -> Any:
                kwargs = {name: c[ptype] for name, ptype in _cls.__init__.__annotations__.items() if name != "return"}
                return _cls(**kwargs)
            return factory
        container[cls] = _make_factory(cls)

    return _LagomState(container=container)


def _cleanup_lagom(_state: _LagomState) -> None:
    _gc_cleanup()


@dataclass(frozen=True)
class _InjectorState:
    injector: Any
    original_inits: dict[type, Any]


def _build_injector_transient(classes: tuple[type, ...]) -> _InjectorState:
    injector_mod = _maybe_import("injector")
    if injector_mod is None:
        raise RuntimeError("injector not installed")
    from injector import Binder, Injector, Module, inject

    original_inits: dict[type, Any] = {}
    for cls in classes:
        original_inits[cls] = cls.__init__
        cls.__init__ = inject(cls.__init__)  # type: ignore[method-assign]

    class _BenchModule(Module):
        def configure(self, binder: Binder) -> None:
            for cls in classes:
                binder.bind(cls, to=cls)

    injector = Injector([_BenchModule()])
    return _InjectorState(injector=injector, original_inits=original_inits)


def _cleanup_injector(state: _InjectorState) -> None:
    for cls, orig in state.original_inits.items():
        cls.__init__ = orig  # type: ignore[method-assign]
    _gc_cleanup()


@dataclass(frozen=True)
class _DishkaState:
    container: Any


def _build_dishka_transient(classes: tuple[type, ...]) -> _DishkaState:
    dishka = _maybe_import("dishka")
    if dishka is None:
        raise RuntimeError("dishka not installed")
    from dishka import Provider, Scope, make_container

    provider = Provider()
    for cls in classes:
        provider.provide(cls, scope=Scope.APP, cache=False)

    container = make_container(provider)
    return _DishkaState(container=container)


def _cleanup_dishka(state: _DishkaState) -> None:
    state.container.close()
    _gc_cleanup()


def _profile_loop(lib: str, classes: tuple[type, ...], iterations: int) -> float:
    t0 = time.perf_counter()
    for idx in range(iterations):
        if ProfileConfig.VERBOSE_PROGRESS:
            logging.info(f"[{lib}] build iteration {idx + 1}/{iterations}")
        if lib == "melder":
            restore_dup = _patch_melder_skip_duplicate_spell_name_validation(
                ProfileConfig.MELDER_SKIP_DUPLICATE_NAME_VALIDATION,
            )
            restore_contracts = _patch_melder_skip_contract_signature_scan(
                ProfileConfig.MELDER_SKIP_CONTRACT_SIGNATURE_SCAN,
            )
            restore_ids = _patch_melder_id_builder(ProfileConfig.MELDER_PATCH_ID_BUILDER)
            try:
                state = _build_melder_bind_only(classes)
                _run_melder_phases_direct(state, conduit_id="bench-direct")
                _cleanup_melder(state)
            finally:
                restore_ids()
                restore_contracts()
                restore_dup()
        elif lib == "dependency-injector":
            state = _build_dependency_injector_transient(classes)
            _cleanup_di(state)
        elif lib == "lagom":
            state = _build_lagom_transient(classes)
            _cleanup_lagom(state)
        elif lib == "injector":
            state = _build_injector_transient(classes)
            _cleanup_injector(state)
        elif lib == "dishka":
            state = _build_dishka_transient(classes)
            _cleanup_dishka(state)
        else:
            raise ValueError(f"Unknown lib: {lib}")
    return time.perf_counter() - t0


def _profile_lib(logger: SafeLogger, lib: str, classes: tuple[type, ...]) -> None:
    profile = cProfile.Profile()
    profile.activate()
    elapsed = _profile_loop(lib, classes, ProfileConfig.ITERATIONS)
    profile.deactivate()

    stream = io.StringIO()
    stats = pstats.Stats(profile, stream=stream).sort_stats(ProfileConfig.SORT_BY)
    stats.print_stats(ProfileConfig.TOP_N)

    per_iter_ms = (elapsed / ProfileConfig.ITERATIONS) * 1000.0
    _log_lines(
        logger,
        header=f"[{lib}] build-only direct phases (iterations={ProfileConfig.ITERATIONS}, avg={per_iter_ms:.3f}ms)",
        lines=stream.getvalue().splitlines(),
    )


def main() -> None:
    logger = _build_logger()
    classes = get_depth_9_classes()
    for lib in ProfileConfig.PROFILE_LIBS:
        try:
            _profile_lib(logger, lib, classes)
        except RuntimeError as exc:
            logger.info(f"[{lib}] skipped: {exc}", "main")


if __name__ == "__main__":
    main()
