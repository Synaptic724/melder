import cProfile
import io
import os
import pstats
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any, Callable, Tuple


def _ensure_repo_root_on_path() -> None:
    """
    Purpose:
        Ensure the repository root is importable when this runner is executed
        directly as a script.
    Contract:
        - Prepends the repo root to `sys.path` once when missing.
        - Uses the known location of this file under
          `benchmarks/testing_other_di/`.
    Returns:
        None.
    """
    repo_root = Path(__file__).resolve().parents[2]
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)


_ensure_repo_root_on_path()

import benchmarks.testing_other_di.test_melder_gauntlet as melder_gauntlet


def _env_int(name: str, default: int) -> int:
    """
    Purpose:
        Parse an integer environment override for the standalone Melder cProfile
        runner.
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


def _results_dir() -> Path:
    """
    Purpose:
        Resolve the artifact directory for standalone Melder-only cProfile
        outputs.
    Contract:
        - Creates the shared benchmark results directory when missing.
        - Returns a stable path that lives beside the existing gauntlet results.
    Returns:
        Results directory path.
    """
    path = Path(__file__).resolve().parent / "results"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _print_profile(
    label: str,
    profiler: cProfile.Profile,
    *,
    sort: str,
    top: int,
) -> None:
    """
    Purpose:
        Print a trimmed pstats view for one Melder-only profile block.
    Contract:
        - Uses `strip_dirs()` so file paths stay readable in terminal output.
        - Prints only the requested top rows for the chosen sort mode.
    Args:
        label: Human-readable block label.
        profiler: Completed cProfile profile object.
        sort: pstats sort key.
        top: Number of rows to print.
    Returns:
        None.
    """
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream).strip_dirs().sort_stats(sort)
    stats.print_stats(top)
    print(f"[CPROFILE] {label} sort={sort} top={top}")
    print(stream.getvalue())


def _dump_profile(label: str, profiler: cProfile.Profile) -> Path:
    """
    Purpose:
        Persist one Melder-only cProfile block to a deterministic `.prof` file.
    Contract:
        - Writes into the shared benchmark results directory.
        - Uses a stable name so repeated runs overwrite the same artifact
          instead of leaving ambiguous partial files.
    Args:
        label: Artifact label without extension.
        profiler: Completed cProfile profile object.
    Returns:
        Path to the dumped `.prof` artifact.
    """
    out_path = _results_dir() / f"{label}.prof"
    profiler.dump_stats(str(out_path))
    print(f"[CPROFILE] wrote {out_path}")
    return out_path


def _profile_call(
    label: str,
    fn: Callable[[], Any],
    *,
    top: int,
) -> Tuple[Any, Path]:
    """
    Purpose:
        Execute one callable under cProfile, dump the raw stats, and print the
        top cumulative and total-time rows.
    Contract:
        - Returns the callable result so profiled setup can hand the prepared
          runtime bundle into later phases.
        - Emits both `cumtime` and `tottime` views for the same profile block.
    Args:
        label: Artifact label without extension.
        fn: Zero-argument callable to profile.
        top: Number of rows to print in each pstats view.
    Returns:
        Tuple of `(call_result, dumped_profile_path)`.
    """
    profiler = cProfile.Profile()
    result = profiler.runcall(fn)
    out_path = _dump_profile(label, profiler)
    _print_profile(label, profiler, sort="cumtime", top=top)
    _print_profile(label, profiler, sort="tottime", top=top)
    return result, out_path


def main() -> int:
    """
    Purpose:
        Run the standalone Melder-only cProfile harness.
    Contract:
        - Profiles the full standalone Melder-only gauntlet through the
          current standalone benchmark surface.
        - Does not modify the interpreter's GIL posture.
    Returns:
        Process exit code.
    """
    base_cfg = melder_gauntlet._melder_config_from_env()
    cfg = replace(
        base_cfg,
        iterations=_env_int("MELDER_GAUNTLET_PROFILE_ITERS", 25),
    )
    top = _env_int("MELDER_GAUNTLET_PROFILE_TOP", 25)

    def run_full_benchmark() -> Any:
        """
        Purpose:
            Run the full standalone Melder-only benchmark once under cProfile.
        Contract:
            - Uses the current standalone Melder-only benchmark file and its
              local support module.
            - Builds only Melder runtime ops.
        Returns:
            Completed Melder benchmark result payload.
        """
        ops = melder_gauntlet._build_runtime_melder()
        return melder_gauntlet._support.run_gauntlet_benchmark(ops, cfg)

    result, _ = _profile_call(
        "melder_gauntlet_full",
        run_full_benchmark,
        top=top,
    )
    melder_gauntlet._support.print_benchmark_result(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
