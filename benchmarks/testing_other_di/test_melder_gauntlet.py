import gc
import sys
from pathlib import Path
from typing import Any, Callable

import pytest


def _ensure_local_paths() -> None:
    """
    Ensure local source and benchmark helper paths are importable.

    Contract:
      - Adds the repository `src/` directory and the current benchmark
        directory to `sys.path` once each.
      - Supports both pytest execution and direct `python` execution.
    """
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parents[1]
    src_dir = project_root / "src"
    for path in (src_dir, current_dir):
        path_as_str = str(path)
        if path_as_str not in sys.path:
            sys.path.insert(0, path_as_str)


_ensure_local_paths()

import melder_gauntlet_support as _support


def _melder_config_from_env() -> _support.GauntletConfig:
    """
    Build the Melder-only gauntlet config from Melder-only env names.

    Contract:
      - Uses only `MELDER_GAUNTLET_*` inputs.
      - Preserves the same workload shape and validation bounds as the
        real-world gauntlet model.
    """
    cfg = _support.GauntletConfig(
        iterations=_support.env_int("MELDER_GAUNTLET_ITERS", 1000),
        threads=_support.env_int("MELDER_GAUNTLET_THREADS", 3),
        request_scope_runs=_support.env_int(
            "MELDER_GAUNTLET_REQUEST_SCOPES",
            _support.REQUEST_SCOPE_RUNS_DEFAULT,
        ),
        worker_a_jobs=_support.env_int(
            "MELDER_GAUNTLET_WORKER_A_JOBS",
            _support.WORKER_A_JOBS_DEFAULT,
        ),
        worker_b_jobs=_support.env_int(
            "MELDER_GAUNTLET_WORKER_B_JOBS",
            _support.WORKER_B_JOBS_DEFAULT,
        ),
    )
    if cfg.iterations <= 0:
        raise AssertionError("MELDER_GAUNTLET_ITERS must be > 0")
    if cfg.threads <= 0 or cfg.threads > 3:
        raise AssertionError("MELDER_GAUNTLET_THREADS must be between 1 and 3")
    if cfg.request_scope_runs <= 0:
        raise AssertionError("MELDER_GAUNTLET_REQUEST_SCOPES must be > 0")
    if cfg.worker_a_jobs <= 0:
        raise AssertionError("MELDER_GAUNTLET_WORKER_A_JOBS must be > 0")
    if cfg.worker_b_jobs <= 0:
        raise AssertionError("MELDER_GAUNTLET_WORKER_B_JOBS must be > 0")
    if cfg.request_scope_runs * _support.REQUEST_OBJECTS_PER_ROOT < 500:
        raise AssertionError("Request spellspace must create at least 500 objects total")
    return cfg


def _build_runtime_melder() -> _support.RuntimeOps:
    """
    Build the Melder runtime benchmark surface for the gauntlet workload.

    Contract:
      - Uses the local Melder runtime only.
      - Uses the same workload graph, variants, and throughput math as the
        dedicated Melder support module.
      - Resets the Aether singleton before and after the benchmark run.
    """
    from melder.aether.aether import Aether
    from melder.aether.conduit.conduit import Conduit
    from melder.aether.spellbook.existence.existence import Existence
    from melder.aether.spellbook.spellbook import Spellbook

    singleton_types = set(_support.SINGLETON_TYPES)
    outer_scoped_types = set(_support.OUTER_SCOPED_TYPES)
    request_scoped_types = set(_support.REQUEST_SCOPED_TYPES)

    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether

    spellbook = Spellbook(aetheric_frame="real-world-gauntlet")
    configuration = spellbook.get_configuration()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)

    spell_ids: dict[type, str] = {}
    for cls in _support.ALL_CLASSES:
        if cls in singleton_types:
            existence = Existence.unique
        elif cls in outer_scoped_types:
            existence = Existence.unique_per_conduit
        elif cls in request_scoped_types:
            existence = Existence.unique_per_spell_space
        else:
            existence = Existence.many
        spell_ids[cls] = spellbook.bind(
            spell=cls,
            existence=existence,
            permissions="create",
        )

    conduit = spellbook.conjure(name="real-world-gauntlet", automatic=True)

    def _get(cls: type) -> Any:
        resolved = conduit.meld(spell=spell_ids[cls])
        if not isinstance(resolved, cls):
            raise AssertionError("Melder: resolve returned wrong type")
        return resolved

    def spawn_singletons() -> None:
        for cls in _support.SINGLETON_TYPES:
            left = _get(cls)
            right = _get(cls)
            if left is not right:
                raise AssertionError("Melder: singleton is not cached")

    def bootstrap_fanout() -> None:
        for cls in _support.BOOTSTRAP_TYPES:
            for _ in range(_support.BOOTSTRAP_FANOUT_PER_SINGLETON):
                _get(cls)

    def _run_in_lesser_and_spellspace(
        *,
        outer_cls: type,
        request_marker_cls: type,
        variant_call: Callable[[Any], None],
        variant_error_prefix: str,
    ) -> _support.ScopeCycleMetrics:
        outer_total_t0 = _support.time.perf_counter_ns()
        outer_create_t0 = _support.time.perf_counter_ns()
        lesser = conduit.create_lesser_conduit()
        outer_create_ns = _support.time.perf_counter_ns() - outer_create_t0
        try:
            outer1 = lesser.meld(spell=spell_ids[outer_cls])
            outer2 = lesser.meld(spell=spell_ids[outer_cls])
            if not isinstance(outer1, outer_cls):
                raise AssertionError(
                    f"Melder: {variant_error_prefix} outer resolve returned wrong type"
                )
            if outer1 is not outer2:
                raise AssertionError(
                    f"Melder: {variant_error_prefix} outer scope object not cached"
                )

            request_total_t0 = _support.time.perf_counter_ns()
            request_create_t0 = _support.time.perf_counter_ns()
            request_cm = lesser.enter_spellspace()
            space = request_cm.__enter__()
            request_create_ns = _support.time.perf_counter_ns() - request_create_t0
            try:
                marker1 = space.meld(spell=spell_ids[request_marker_cls])
                marker2 = space.meld(spell=spell_ids[request_marker_cls])
                if not isinstance(marker1, request_marker_cls):
                    raise AssertionError(
                        f"Melder: {variant_error_prefix} request marker wrong type"
                    )
                if marker1 is not marker2:
                    raise AssertionError(
                        f"Melder: {variant_error_prefix} request scope marker not cached"
                    )
                inherited = space.meld(spell=spell_ids[outer_cls])
                if inherited is not outer1:
                    raise AssertionError(
                        f"Melder: {variant_error_prefix} outer scope did not propagate into request"
                    )
                variant_call(space)
            finally:
                request_cleanup_t0 = _support.time.perf_counter_ns()
                request_cm.__exit__(None, None, None)
                request_cleanup_ns = _support.time.perf_counter_ns() - request_cleanup_t0
            request_total_ns = _support.time.perf_counter_ns() - request_total_t0
        finally:
            outer_cleanup_t0 = _support.time.perf_counter_ns()
            lesser.cleanup()
            outer_cleanup_ns = _support.time.perf_counter_ns() - outer_cleanup_t0

        return _support.ScopeCycleMetrics(
            outer_create_ns=outer_create_ns,
            outer_cleanup_ns=outer_cleanup_ns,
            outer_total_ns=_support.time.perf_counter_ns() - outer_total_t0,
            request_create_ns=request_create_ns,
            request_cleanup_ns=request_cleanup_ns,
            request_total_ns=request_total_ns,
        )

    def request_scope_cycle(variant: int) -> _support.ScopeCycleMetrics:
        def variant_call(space: Any) -> None:
            if variant == 0:
                root = space.meld(spell=spell_ids[_support.RequestRoot])
                if not isinstance(root, _support.RequestRoot):
                    raise AssertionError("Melder: request root resolve returned wrong type")
            elif variant == 1:
                group = space.meld(spell=spell_ids[_support.RequestGroup])
                root = space.meld(spell=spell_ids[_support.RequestRoot])
                if not isinstance(group, _support.RequestGroup) or not isinstance(
                    root, _support.RequestRoot
                ):
                    raise AssertionError("Melder: request scope variant returned wrong type")
            else:
                root1 = space.meld(spell=spell_ids[_support.RequestRoot])
                root2 = space.meld(spell=spell_ids[_support.RequestRoot])
                if not isinstance(root1, _support.RequestRoot) or not isinstance(
                    root2, _support.RequestRoot
                ):
                    raise AssertionError("Melder: request scope variant returned wrong type")

        return _run_in_lesser_and_spellspace(
            outer_cls=_support.RequestSession,
            request_marker_cls=_support.RequestScopeMarker,
            variant_call=variant_call,
            variant_error_prefix="request lane",
        )

    def worker_a_scope_cycle(variant: int) -> _support.ScopeCycleMetrics:
        def variant_call(space: Any) -> None:
            if variant == 0:
                root = space.meld(spell=spell_ids[_support.WorkerAJobRoot])
                if not isinstance(root, _support.WorkerAJobRoot):
                    raise AssertionError("Melder: worker A resolve returned wrong type")
            elif variant == 1:
                group = space.meld(spell=spell_ids[_support.WorkerAGroup])
                root = space.meld(spell=spell_ids[_support.WorkerAJobRoot])
                if not isinstance(group, _support.WorkerAGroup) or not isinstance(
                    root, _support.WorkerAJobRoot
                ):
                    raise AssertionError("Melder: worker A scope variant returned wrong type")
            else:
                root1 = space.meld(spell=spell_ids[_support.WorkerAJobRoot])
                root2 = space.meld(spell=spell_ids[_support.WorkerAJobRoot])
                if not isinstance(root1, _support.WorkerAJobRoot) or not isinstance(
                    root2, _support.WorkerAJobRoot
                ):
                    raise AssertionError("Melder: worker A scope variant returned wrong type")

        return _run_in_lesser_and_spellspace(
            outer_cls=_support.WorkerASession,
            request_marker_cls=_support.WorkerAScopeMarker,
            variant_call=variant_call,
            variant_error_prefix="worker A lane",
        )

    def worker_b_scope_cycle(variant: int) -> _support.ScopeCycleMetrics:
        def variant_call(space: Any) -> None:
            if variant == 0:
                root = space.meld(spell=spell_ids[_support.WorkerBJobRoot])
                if not isinstance(root, _support.WorkerBJobRoot):
                    raise AssertionError("Melder: worker B resolve returned wrong type")
            elif variant == 1:
                group = space.meld(spell=spell_ids[_support.WorkerBGroup])
                root = space.meld(spell=spell_ids[_support.WorkerBJobRoot])
                if not isinstance(group, _support.WorkerBGroup) or not isinstance(
                    root, _support.WorkerBJobRoot
                ):
                    raise AssertionError("Melder: worker B scope variant returned wrong type")
            else:
                root1 = space.meld(spell=spell_ids[_support.WorkerBJobRoot])
                root2 = space.meld(spell=spell_ids[_support.WorkerBJobRoot])
                if not isinstance(root1, _support.WorkerBJobRoot) or not isinstance(
                    root2, _support.WorkerBJobRoot
                ):
                    raise AssertionError("Melder: worker B scope variant returned wrong type")

        return _run_in_lesser_and_spellspace(
            outer_cls=_support.WorkerBSession,
            request_marker_cls=_support.WorkerBScopeMarker,
            variant_call=variant_call,
            variant_error_prefix="worker B lane",
        )

    def cleanup() -> None:
        try:
            conduit.cleanup()
        finally:
            Aether._reset_singleton_for_tests()
            refreshed_aether = Aether()
            Spellbook._aether = refreshed_aether
            Conduit._aether = refreshed_aether
        gc.collect()

    return _support.RuntimeOps(
        name="melder",
        spawn_singletons=spawn_singletons,
        bootstrap_fanout=bootstrap_fanout,
        request_scope_cycle=request_scope_cycle,
        worker_a_scope_cycle=worker_a_scope_cycle,
        worker_b_scope_cycle=worker_b_scope_cycle,
        cleanup=cleanup,
    )


@pytest.mark.timeout(3600)
def test_melder_gauntlet() -> None:
    """
    Run the standalone Melder-only variant of the real-world gauntlet.
    """
    cfg = _melder_config_from_env()
    ops = _build_runtime_melder()
    result = _support.run_gauntlet_benchmark(ops, cfg)
    _support.print_benchmark_result(result)


if __name__ == "__main__":
    test_melder_gauntlet()
