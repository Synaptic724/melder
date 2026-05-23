from __future__ import annotations

import cProfile
import io
import os
import pstats
from dataclasses import replace
from pathlib import Path

import pytest

import benchmarks.testing_other_di.test_real_world_gauntlet as gauntlet


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def _results_dir() -> Path:
    path = Path(__file__).resolve().parent / "results"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _print_profile(label: str, profiler: cProfile.Profile, *, sort: str, top: int) -> None:
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream).strip_dirs().sort_stats(sort)
    stats.print_stats(top)
    print(f"[CPROFILE] {label} sort={sort} top={top}")
    print(stream.getvalue())


@pytest.mark.timeout(3600)
@pytest.mark.parametrize("lib", ("dependency-injector", "dishka", "melder"))
def test_cprofile_real_world_gauntlet(lib: str) -> None:
    """
    Profile the real-world gauntlet with cProfile and dump the raw stats.

    Notes:
        - Uses the same gauntlet runtime helpers as the timing benchmark.
        - Defaults to fewer iterations than the timing suite because cProfile
          adds substantial overhead.
        - Override with:
            DI_GAUNTLET_PROFILE_ITERS
            DI_GAUNTLET_PROFILE_TOP
    """
    base_cfg = gauntlet._GauntletConfig.from_env()
    cfg = replace(base_cfg, iterations=_env_int("DI_GAUNTLET_PROFILE_ITERS", 25))
    top = _env_int("DI_GAUNTLET_PROFILE_TOP", 40)

    profiler = cProfile.Profile()
    result = profiler.runcall(gauntlet._run_gauntlet_benchmark, lib, cfg)

    gauntlet._print_benchmark_result(result)

    out_path = _results_dir() / f"real_world_gauntlet_{lib.replace('-', '_')}.prof"
    profiler.dump_stats(str(out_path))
    print(f"[CPROFILE] wrote {out_path}")

    _print_profile(f"{lib} real-world gauntlet", profiler, sort="cumtime", top=top)
    _print_profile(f"{lib} real-world gauntlet", profiler, sort="tottime", top=top)
