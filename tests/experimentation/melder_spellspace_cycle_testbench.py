"""
Measure raw Melder conduit and spellspace cycle timings without cross-library
benchmark noise.

Purpose:
    Provide a focused Melder-only experiment that times:
    - normal conduit build / first meld / cached meld / cleanup
    - lesser conduit build / first meld / cached meld / cleanup
    - spellspace build / first meld / cached meld / cleanup

This is an experimentation bench, not production runtime code.
"""

from __future__ import annotations

import gc
import sys
import time
from dataclasses import dataclass
from typing import Any, Callable


from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
    apply_dynamic_defaults_for_spellbook_configuration,
)
def _ensure_src_on_path() -> None:
    """
    Ensure the local `src/` tree is importable for the bench.
    """
    if "src" not in sys.path:
        sys.path.insert(0, "src")
    if "." not in sys.path:
        sys.path.insert(0, ".")


_ensure_src_on_path()

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.deep_layers import Depth3Root, get_depth_3_classes


class _NoDeps:
    """
    Provide an explicit zero-arg constructor for benchmark leaves.
    """

    __slots__ = ()

    def __init__(self) -> None:
        return None


class SoloSpaceRoot(_NoDeps):
    __slots__ = ()


class ShallowSpaceLeaf(_NoDeps):
    __slots__ = ()


class ShallowSpaceRoot:
    __slots__ = ("leaf",)

    def __init__(self, leaf: ShallowSpaceLeaf) -> None:
        self.leaf = leaf


@dataclass(frozen=True)
class SpellspaceBenchShape:
    """
    Describe one Melder-only spellspace benchmark shape.
    """

    name: str
    root_type: type
    classes: tuple[type, ...]


@dataclass(frozen=True)
class RuntimeBenchShape:
    """
    Describe one Melder runtime benchmark shape.
    """

    name: str
    root_type: type
    classes: tuple[type, ...]


def _solo_shape() -> RuntimeBenchShape:
    return RuntimeBenchShape(
        name="solo",
        root_type=SoloSpaceRoot,
        classes=(SoloSpaceRoot,),
    )


def _shallow_shape() -> RuntimeBenchShape:
    return RuntimeBenchShape(
        name="shallow",
        root_type=ShallowSpaceRoot,
        classes=(ShallowSpaceLeaf, ShallowSpaceRoot),
    )


def _deep_shape() -> RuntimeBenchShape:
    return RuntimeBenchShape(
        name="deep",
        root_type=Depth3Root,
        classes=get_depth_3_classes(),
    )


def _average_spellspace_cycle_metrics_ns(
        *,
        enter_scope: Callable[[], Any],
        meld_in_scope: Callable[[Any], Any],
        exit_scope: Callable[[Any], None],
        iters: int,
) -> tuple[float, float, float, float, float]:
    """
    Measure build, first meld, cached meld, exit, and total cycle cost.
    """
    if iters <= 0:
        raise AssertionError("iters must be > 0")

    build_total = 0
    first_total = 0
    cached_total = 0
    exit_total = 0
    whole_total = 0

    for _ in range(iters):
        t0 = time.perf_counter_ns()
        handle = enter_scope()
        t1 = time.perf_counter_ns()
        try:
            meld_in_scope(handle)
            t2 = time.perf_counter_ns()
            meld_in_scope(handle)
            t3 = time.perf_counter_ns()
        finally:
            exit_scope(handle)
        t4 = time.perf_counter_ns()

        build_total += t1 - t0
        first_total += t2 - t1
        cached_total += t3 - t2
        exit_total += t4 - t3
        whole_total += t4 - t0

    return (
        build_total / float(iters),
        first_total / float(iters),
        cached_total / float(iters),
        exit_total / float(iters),
        whole_total / float(iters),
    )


def _build_spellbook_and_ids(
        shape: RuntimeBenchShape,
        *,
        existence: Existence,
        frame_name: str,
        automatic: bool,
) -> tuple[Spellbook, str]:
    """
    Build one spellbook and bind the benchmark classes under the requested existence.
    """
    cfg = SpellbookConfiguration(frame_name)
    if automatic:
        apply_automatic_defaults_for_spellbook_configuration(cfg)
    else:
        apply_dynamic_defaults_for_spellbook_configuration(cfg)
    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook = Spellbook(
        aetheric_frame=frame_name,
        configuration=cfg,
    )

    spell_ids: dict[type, str] = {}
    for cls in shape.classes:
        spell_ids[cls] = spellbook.bind(
            spell=cls,
            existence=existence,
            permissions="create",
        )
    return spellbook, spell_ids[shape.root_type]


def _average_conduit_cycle_metrics_ns(
        *,
        build_conduit: Callable[[], Any],
        meld_once: Callable[[Any], Any],
        cleanup_conduit: Callable[[Any], None],
        iters: int,
) -> tuple[float, float, float, float]:
    """
    Measure conduit build, first meld, cached meld, and cleanup over N iterations.
    """
    if iters <= 0:
        raise AssertionError("iters must be > 0")

    build_total = 0
    first_total = 0
    cached_total = 0
    cleanup_total = 0

    for _ in range(iters):
        t0 = time.perf_counter_ns()
        conduit = build_conduit()
        t1 = time.perf_counter_ns()
        try:
            meld_once(conduit)
            t2 = time.perf_counter_ns()
            meld_once(conduit)
            t3 = time.perf_counter_ns()
        finally:
            cleanup_conduit(conduit)
        t4 = time.perf_counter_ns()

        build_total += t1 - t0
        first_total += t2 - t1
        cached_total += t3 - t2
        cleanup_total += t4 - t3

    return (
        build_total / float(iters),
        first_total / float(iters),
        cached_total / float(iters),
        cleanup_total / float(iters),
    )


def _build_melder_spellspace_runtime(
        shape: RuntimeBenchShape,
        *,
        automatic: bool,
) -> tuple[Callable[[], Any], Callable[[Any], Any], Callable[[Any], None], Callable[[], None]]:
    """
    Build one Melder runtime for a focused spellspace bench shape.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether

    spellbook, root_id = _build_spellbook_and_ids(
        shape,
        existence=Existence.unique_per_spell_space,
        frame_name="spellspace-cycle-experiment",
        automatic=automatic,
    )
    conduit = spellbook.conjure(
        name="spellspace-cycle-experiment",
        automatic=automatic,
    )

    def enter_scope() -> Any:
        ctx = conduit.enter_spellspace()
        space = ctx.__enter__()
        return ctx, space

    def meld_in_scope(handle: Any) -> Any:
        _, space = handle
        root = space.meld(spell=root_id)
        if not isinstance(root, shape.root_type):
            raise AssertionError("Melder spellspace bench returned wrong root type.")
        return root

    def exit_scope(handle: Any) -> None:
        ctx, _ = handle
        ctx.__exit__(None, None, None)

    def cleanup() -> None:
        try:
            conduit.cleanup()
        finally:
            Aether._reset_singleton_for_tests()
            aether2 = Aether()
            Spellbook._aether = aether2
            Conduit._aether = aether2
        gc.collect()

    return enter_scope, meld_in_scope, exit_scope, cleanup


def _measure_normal_and_lesser_conduit_cycle(
        shape: RuntimeBenchShape,
        *,
        iters: int,
        automatic: bool,
) -> tuple[tuple[float, float, float, float], tuple[float, float, float, float]]:
    """
    Measure one normal-conduit and one lesser-conduit cycle for the given shape.
    """
    if iters <= 0:
        raise AssertionError("iters must be > 0")

    def normal_cycle_metrics() -> tuple[float, float, float, float]:
        def build_conduit() -> Any:
            Aether._reset_singleton_for_tests()
            aether = Aether()
            Spellbook._aether = aether
            Conduit._aether = aether
            spellbook, root_id = _build_spellbook_and_ids(
                shape,
                existence=Existence.unique_per_conduit,
                frame_name="conduit-cycle-experiment",
                automatic=automatic,
            )
            conduit = spellbook.conjure(
                name="conduit-cycle-experiment",
                automatic=automatic,
            )
            return spellbook, conduit, root_id

        def meld_once(handle: Any) -> Any:
            _, conduit, root_id = handle
            root = conduit.meld(spell=root_id)
            if not isinstance(root, shape.root_type):
                raise AssertionError("Melder conduit bench returned wrong root type.")
            return root

        def cleanup_conduit(handle: Any) -> None:
            spellbook, conduit, _ = handle
            try:
                conduit.cleanup()
            finally:
                try:
                    spellbook.cleanup()
                except Exception:
                    pass
                Aether._reset_singleton_for_tests()
                aether2 = Aether()
                Spellbook._aether = aether2
                Conduit._aether = aether2
                gc.collect()

        return _average_conduit_cycle_metrics_ns(
            build_conduit=build_conduit,
            meld_once=meld_once,
            cleanup_conduit=cleanup_conduit,
            iters=iters,
        )

    def lesser_cycle_metrics() -> tuple[float, float, float, float]:
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether
        spellbook, root_id = _build_spellbook_and_ids(
            shape,
            existence=Existence.unique_per_conduit,
            frame_name="lesser-conduit-cycle-experiment",
            automatic=automatic,
        )
        root_conduit = spellbook.conjure(
            name="lesser-conduit-cycle-experiment",
            automatic=automatic,
        )
        try:
            def build_lesser() -> Any:
                return root_conduit.create_lesser_conduit()

            def meld_once(lesser: Any) -> Any:
                root = lesser.meld(spell=root_id)
                if not isinstance(root, shape.root_type):
                    raise AssertionError("Melder lesser-conduit bench returned wrong root type.")
                return root

            def cleanup_lesser(lesser: Any) -> None:
                lesser.cleanup()

            return _average_conduit_cycle_metrics_ns(
                build_conduit=build_lesser,
                meld_once=meld_once,
                cleanup_conduit=cleanup_lesser,
                iters=iters,
            )
        finally:
            try:
                root_conduit.cleanup()
            finally:
                try:
                    spellbook.cleanup()
                except Exception:
                    pass
                Aether._reset_singleton_for_tests()
                aether2 = Aether()
                Spellbook._aether = aether2
                Conduit._aether = aether2
                gc.collect()

    return normal_cycle_metrics(), lesser_cycle_metrics()


def _run_shape(
        shape: RuntimeBenchShape,
        *,
        iters: int,
        automatic: bool,
) -> None:
    """
    Run one Melder spellspace-cycle timing shape and print the result.
    """
    enter_scope, meld_in_scope, exit_scope, cleanup = _build_melder_spellspace_runtime(
        shape,
        automatic=automatic,
    )
    mode_label = "automatic" if automatic else "dynamic"
    try:
        build_ns, first_ns, cached_ns, exit_ns, total_ns = (
            _average_spellspace_cycle_metrics_ns(
                enter_scope=enter_scope,
                meld_in_scope=meld_in_scope,
                exit_scope=exit_scope,
                iters=iters,
            )
        )
        print(
            "[melder-spellspace-experiment] {0} mode({1}) iters({2}) | build={3:.2f}us | "
            "first_meld={4:.2f}us | cached_meld={5:.2f}us | exit={6:.2f}us | total={7:.2f}us".format(
                shape.name,
                mode_label,
                iters,
                build_ns / 1_000.0,
                first_ns / 1_000.0,
                cached_ns / 1_000.0,
                exit_ns / 1_000.0,
                total_ns / 1_000.0,
            )
        )
    finally:
        cleanup()

    normal_metrics, lesser_metrics = _measure_normal_and_lesser_conduit_cycle(
        shape,
        iters=iters,
        automatic=automatic,
    )
    normal_build_ns, normal_first_ns, normal_cached_ns, normal_cleanup_ns = normal_metrics
    lesser_build_ns, lesser_first_ns, lesser_cached_ns, lesser_cleanup_ns = lesser_metrics
    print(
        "[melder-conduit-experiment] {0} mode({1}) iters({2}) | normal_build={3:.2f}us | "
        "normal_first_meld={4:.2f}us | normal_cached_meld={5:.2f}us | "
        "lesser_build={6:.2f}us | lesser_first_meld={7:.2f}us | "
        "lesser_cached_meld={8:.2f}us | lesser_cleanup={9:.2f}us | "
        "normal_cleanup={10:.2f}us".format(
            shape.name,
            mode_label,
            iters,
            normal_build_ns / 1_000.0,
            normal_first_ns / 1_000.0,
            normal_cached_ns / 1_000.0,
            lesser_build_ns / 1_000.0,
            lesser_first_ns / 1_000.0,
            lesser_cached_ns / 1_000.0,
            lesser_cleanup_ns / 1_000.0,
            normal_cleanup_ns / 1_000.0,
        )
    )


def _run_bench() -> None:
    """
    Execute the focused Melder spellspace-cycle experiment.
    """
    iters = 500
    for automatic in (True, False):
        for shape in (_solo_shape(), _shallow_shape(), _deep_shape()):
            _run_shape(shape, iters=iters, automatic=automatic)
    print("OK_MELDER_SPELLSPACE_CYCLE_EXPERIMENT")


if __name__ == "__main__":
    _run_bench()
