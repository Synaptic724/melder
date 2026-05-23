import os
from dataclasses import replace
from typing import Any, List

import pytest

import benchmarks.testing_other_di.test_real_world_gauntlet as gauntlet


def _env_int(name: str, default: int) -> int:
    """
    Purpose:
        Parse an integer environment override for the isolated Melder gauntlet.
    Contract:
        - Returns `default` when the variable is unset or blank.
        - Raises `ValueError` through `int(...)` if the value is not numeric.
    Args:
        name: Environment variable name to read.
        default: Fallback value when the variable is absent.
    Returns:
        Parsed integer value.
    """
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def _melder_cfg_from_env() -> gauntlet._GauntletConfig:
    """
    Purpose:
        Resolve the Melder-only gauntlet configuration from the environment.
    Contract:
        - Starts from the canonical gauntlet configuration parser so the
          benchmark keeps the same validation behavior by default.
        - Allows Melder-specific overrides without affecting the shared
          multi-library benchmark file.
    Returns:
        Melder-only gauntlet configuration.
    """
    base_cfg = gauntlet._GauntletConfig.from_env()
    return replace(
        base_cfg,
        iterations=_env_int("MELDER_GAUNTLET_ITERS", base_cfg.iterations),
        threads=_env_int("MELDER_GAUNTLET_THREADS", base_cfg.threads),
        request_scope_runs=_env_int(
            "MELDER_GAUNTLET_REQUEST_SCOPES",
            base_cfg.request_scope_runs,
        ),
        worker_a_jobs=_env_int(
            "MELDER_GAUNTLET_WORKER_A_JOBS",
            base_cfg.worker_a_jobs,
        ),
        worker_b_jobs=_env_int(
            "MELDER_GAUNTLET_WORKER_B_JOBS",
            base_cfg.worker_b_jobs,
        ),
    )


def _melder_cprofile_cfg_from_env() -> gauntlet._GauntletConfig:
    """
    Purpose:
        Resolve a cProfile-safe Melder gauntlet configuration.
    Contract:
        - Starts from the canonical gauntlet parser to keep field semantics
          aligned with the shared benchmark.
        - Intentionally defaults to a much smaller workload than the timing
          benchmark because profiling the full Melder build + hot path at the
          shared defaults is not tractable.
        - Allows the request-scope count to drop below the shared benchmark's
          500-object floor because this harness is for hotspot inspection, not
          headline timing comparison.
    Returns:
        Smaller Melder-only configuration for cProfile runs.
    """
    base_cfg = gauntlet._GauntletConfig.from_env()
    return replace(
        base_cfg,
        iterations=_env_int("MELDER_GAUNTLET_PROFILE_ITERS", 1),
        threads=_env_int("MELDER_GAUNTLET_PROFILE_THREADS", 1),
        request_scope_runs=_env_int("MELDER_GAUNTLET_PROFILE_REQUEST_SCOPES", 1),
        worker_a_jobs=_env_int(
            "MELDER_GAUNTLET_PROFILE_WORKER_A_JOBS",
            1,
        ),
        worker_b_jobs=_env_int(
            "MELDER_GAUNTLET_PROFILE_WORKER_B_JOBS",
            1,
        ),
    )


def _build_melder_ops() -> gauntlet._RuntimeOps:
    """
    Purpose:
        Construct the Melder-only runtime operations bundle.
    Contract:
        - Delegates to the canonical shared Melder runtime builder.
        - Returns the same `_RuntimeOps` surface used by the multi-library
          gauntlet so timing and cProfile harnesses stay behaviorally aligned.
    Returns:
        Melder runtime operations bundle.
    """
    return gauntlet._build_runtime_melder()


def _run_melder_gauntlet_benchmark(
    cfg: gauntlet._GauntletConfig,
) -> gauntlet._BenchmarkResult:
    """
    Purpose:
        Execute the shared gauntlet benchmark against Melder only.
    Contract:
        - Uses the canonical shared gauntlet runner.
        - Keeps output formatting and metric semantics identical to the shared
          benchmark, but fixes the library under test to `melder`.
    Args:
        cfg: Timing configuration for the run.
    Returns:
        Completed benchmark result for Melder.
    """
    return gauntlet._run_gauntlet_benchmark("melder", cfg)


def _run_melder_profiled_iterations(
    ops: gauntlet._RuntimeOps,
    cfg: gauntlet._GauntletConfig,
) -> List[gauntlet._IterationResult]:
    """
    Purpose:
        Execute only the hot Melder gauntlet iterations after runtime setup.
    Contract:
        - Assumes the caller already built runtime ops and primed singleton
          state through `spawn_singletons()`.
        - Reuses the shared `_run_gauntlet_once(...)` helper so the hot path
          matches the canonical benchmark behavior exactly.
    Args:
        ops: Prepared Melder runtime operations bundle.
        cfg: Profile-safe Melder gauntlet configuration.
    Returns:
        Ordered iteration results for the profiled hot path.
    """
    out: List[gauntlet._IterationResult] = []
    for iteration_ix in range(cfg.iterations):
        out.append(gauntlet._run_gauntlet_once(ops, cfg, iteration_ix))
    return out


def _print_melder_iteration_summary(
    cfg: gauntlet._GauntletConfig,
    iterations: List[gauntlet._IterationResult],
) -> None:
    """
    Purpose:
        Print a compact hot-iteration summary for the isolated Melder profile.
    Contract:
        - Summarizes total, bootstrap, and threaded iteration timing with the
          canonical shared summary formatter.
        - Prints enough context to compare cProfile runs without rebuilding the
          full shared benchmark result object.
    Args:
        cfg: Melder gauntlet configuration used for the profiled run.
        iterations: Ordered iteration results returned by the hot path runner.
    Returns:
        None.
    """
    total_summary = gauntlet._summarize([item.total_ns for item in iterations])
    bootstrap_summary = gauntlet._summarize([item.bootstrap_ns for item in iterations])
    threaded_summary = gauntlet._summarize([item.threaded_ns for item in iterations])
    print(
        "[melder-only] hot gauntlet config: "
        f"iterations={cfg.iterations}, "
        f"threads={cfg.threads}, "
        f"request_scopes={cfg.request_scope_runs}, "
        f"worker_a_scopes={cfg.worker_a_jobs if cfg.threads >= 2 else 0}, "
        f"worker_b_scopes={cfg.worker_b_jobs if cfg.threads >= 3 else 0}"
    )
    print(
        "[melder-only] hot iteration total | "
        f"{gauntlet._format_summary_ms(total_summary)}"
    )
    print(
        "[melder-only] hot iteration bootstrap | "
        f"{gauntlet._format_summary_ms(bootstrap_summary)}"
    )
    print(
        "[melder-only] hot iteration threaded phase | "
        f"{gauntlet._format_summary_ms(threaded_summary)}"
    )


@pytest.mark.timeout(3600)
def test_melder_gauntlet() -> None:
    """
    Purpose:
        Run the real-world gauntlet against Melder only.
    Contract:
        - Keeps the canonical gauntlet workload and metric reporting intact.
        - Removes the shared parametrization so Melder can be timed and debugged
          in isolation from the other DI systems.
    Returns:
        None.
    """
    cfg = _melder_cfg_from_env()
    result = _run_melder_gauntlet_benchmark(cfg)
    gauntlet._print_benchmark_result(result)
