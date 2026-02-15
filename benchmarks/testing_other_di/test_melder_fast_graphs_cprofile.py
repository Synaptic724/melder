import cProfile
import json
import io
import os
import pstats
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import pytest

from benchmarks.testing_other_di import test_shallow_all as shallow_all


_FAST_GRAPH_NAMES: Tuple[str, ...] = ("solo", "shallow", "wide", "diamond")


def _env_bool(name: str, default: bool) -> bool:
    """
    Purpose:
        Parse a boolean environment toggle for benchmark execution.
    Contract:
        - Accepts truthy values: 1,true,yes,on (case-insensitive).
        - Accepts falsy values: 0,false,no,off (case-insensitive).
        - Falls back to `default` when unset or unrecognized.
    Args:
        name: Environment variable name.
        default: Fallback value when parsing is not possible.
    Returns:
        Parsed boolean value.
    """
    raw = os.getenv(name)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default


def _env_int_nonneg(name: str, default: int) -> int:
    """
    Purpose:
        Parse a non-negative integer from the environment.
    Contract:
        - Uses `default` if the variable is missing.
        - Raises AssertionError for non-integer or negative values.
    Args:
        name: Environment variable name.
        default: Fallback integer value.
    Returns:
        Parsed non-negative integer.
    Raises:
        AssertionError: If value cannot be parsed as non-negative integer.
    """
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise AssertionError(f"{name} must be an integer; got {raw!r}.") from exc
    if value < 0:
        raise AssertionError(f"{name} must be >= 0; got {value}.")
    return value


def _fast_graph_specs_by_name() -> Dict[str, Any]:
    """
    Purpose:
        Resolve fast graph specifications from the canonical shallow benchmark graph registry.
    Contract:
        - Returns only fast graph specs in `_FAST_GRAPH_NAMES`.
        - Raises if any required fast graph is missing from `_all_graphs()`.
    Returns:
        Mapping from graph name to graph specification object.
    Raises:
        AssertionError: If a required fast graph is unavailable.
    """
    all_specs = shallow_all._all_graphs()
    by_name: Dict[str, Any] = {}
    for spec in all_specs:
        if spec.name in _FAST_GRAPH_NAMES:
            by_name[spec.name] = spec

    missing = [name for name in _FAST_GRAPH_NAMES if name not in by_name]
    if missing:
        raise AssertionError(f"Missing expected fast graph specs: {missing}")
    return by_name


def _dump_profile(label: str, profile: cProfile.Profile) -> Path:
    """
    Purpose:
        Persist cProfile stats to a deterministic artifact path and optionally print top rows.
    Contract:
        - Writes `<label>.prof` into `DI_CPROFILE_DIR` or default profile directory.
        - Prints pstats summary only when `DI_CPROFILE_PRINT=1`.
    Args:
        label: Profile artifact label.
        profile: Completed cProfile instance.
    Returns:
        Output path for the dumped profile artifact.
    """
    out_dir = Path(
        os.getenv(
            "DI_CPROFILE_DIR",
            "benchmarks/testing_other_di/profiles/fast_graphs_melder",
        )
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{label}.prof"
    profile.dump_stats(str(out_path))

    if _env_bool("DI_CPROFILE_PRINT", False):
        sort = os.getenv("DI_CPROFILE_SORT", "cumtime")
        top = _env_int_nonneg("DI_CPROFILE_TOP", 30)
        stream = io.StringIO()
        stats = pstats.Stats(profile, stream=stream).strip_dirs().sort_stats(sort)
        stats.print_stats(top)
        print(f"[melder][cprofile] {label} profile={out_path} sort={sort} top={top}")
        print(stream.getvalue())
    else:
        print(f"[melder][cprofile] {label} profile={out_path}")

    return out_path


def _write_profile_log(
    label: str,
    profile: cProfile.Profile,
    profile_path: Path,
    *,
    sort: str,
    top: int,
) -> Path:
    """
    Purpose:
        Persist a textual pstats summary artifact for a captured cProfile run.
    Contract:
        - Writes `<label>.pstats.txt` into `DI_CPROFILE_LOG_DIR` when set, else
          to the profile artifact directory.
        - Uses provided `sort`/`top` controls.
    Args:
        label: Profile artifact label.
        profile: Completed cProfile instance.
        profile_path: Existing `.prof` artifact path.
    Returns:
        Path of the written text summary artifact.
    """
    stream = io.StringIO()
    stats = pstats.Stats(profile, stream=stream).strip_dirs().sort_stats(sort)
    stats.print_stats(top)

    default_log_dir = profile_path.parent
    configured = os.getenv("DI_CPROFILE_LOG_DIR")
    log_dir = Path(configured) if configured is not None else default_log_dir
    log_dir.mkdir(parents=True, exist_ok=True)

    log_path = log_dir / f"{label}.pstats.txt"
    header = (
        f"label={label}\n"
        f"profile={profile_path}\n"
        f"sort={sort}\n"
        f"top={top}\n\n"
    )
    log_path.write_text(header + stream.getvalue(), encoding="utf-8")
    return log_path


def _extract_top_hotspots(
    profile: cProfile.Profile,
    *,
    sort: str,
    top: int,
) -> List[Dict[str, Any]]:
    """
    Purpose:
        Convert cProfile stats into a structured hotspot list.
    Contract:
        - Returns sorted hotspots using the requested `sort` mode.
        - Each hotspot entry includes function id, call counts, and total/cumulative time.
    Args:
        profile: Completed cProfile instance.
        sort: pstats sort key.
        top: Maximum number of rows to emit.
    Returns:
        List of hotspot dictionaries ordered by requested sort.
    """
    stats = pstats.Stats(profile).strip_dirs().sort_stats(sort)
    rows: List[Dict[str, Any]] = []
    for func in stats.fcn_list[:top]:
        primitive_calls, total_calls, tottime, cumtime, _ = stats.stats[func]
        file_path, line_no, func_name = func
        rows.append(
            {
                "function": f"{file_path}:{line_no}({func_name})",
                "primitive_calls": primitive_calls,
                "total_calls": total_calls,
                "tottime_s": round(float(tottime), 9),
                "cumtime_s": round(float(cumtime), 9),
            }
        )
    return rows


def _write_hotspot_artifact(
    label: str,
    *,
    profile_path: Path,
    hotspots: List[Dict[str, Any]],
) -> Path:
    """
    Purpose:
        Persist structured hotspot rows as a JSON artifact.
    Contract:
        - Writes `<label>.hotspots.json` into `DI_CPROFILE_HOTSPOT_DIR` when set,
          else to the profile artifact directory.
        - Includes label and profile path metadata.
    Args:
        label: Profile artifact label.
        profile_path: Existing `.prof` artifact path.
        hotspots: Structured hotspot rows.
    Returns:
        Path of written hotspot JSON artifact.
    """
    configured = os.getenv("DI_CPROFILE_HOTSPOT_DIR")
    hotspot_dir = Path(configured) if configured is not None else profile_path.parent
    hotspot_dir.mkdir(parents=True, exist_ok=True)

    hotspot_path = hotspot_dir / f"{label}.hotspots.json"
    payload = {
        "label": label,
        "profile_path": str(profile_path),
        "hotspots": hotspots,
    }
    hotspot_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return hotspot_path


def _write_disabled_hotspot_artifact(label: str, artifact_dir: Path) -> Path:
    """
    Purpose:
        Persist an explicit hotspot artifact when cProfile is disabled.
    Contract:
        - Writes `<label>.hotspots.json` with `profile_enabled=false` and no rows.
    Args:
        label: Benchmark lane label.
        artifact_dir: Base artifact directory.
    Returns:
        Path of written hotspot JSON artifact.
    """
    artifact_dir.mkdir(parents=True, exist_ok=True)
    hotspot_path = artifact_dir / f"{label}.hotspots.json"
    payload = {
        "label": label,
        "profile_enabled": False,
        "hotspots": [],
    }
    hotspot_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return hotspot_path


def _append_benchmark_record(
    label: str,
    elapsed_seconds: float,
    *,
    profile_enabled: bool,
    profile_path: Path,
    log_path: Path,
    hotspot_path: Path,
) -> Path:
    """
    Purpose:
        Append a benchmark timing record to a JSONL artifact file.
    Contract:
        - Appends one JSON object per run.
        - Writes to `DI_BENCHMARK_FILE` when set, else to
          `<profile_dir>/benchmark_results.jsonl`.
    Args:
        label: Benchmark label.
        elapsed_seconds: End-to-end lane runtime.
        profile_enabled: Whether cProfile was active for this execution.
        profile_path: Persisted `.prof` path.
        log_path: Persisted `.pstats.txt` path.
        hotspot_path: Persisted structured hotspot artifact path.
    Returns:
        Path of the updated JSONL benchmark artifact.
    """
    default_file = profile_path.parent / "benchmark_results.jsonl"
    configured = os.getenv("DI_BENCHMARK_FILE")
    artifact_file = Path(configured) if configured is not None else default_file
    artifact_file.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "label": label,
        "elapsed_ms": round(elapsed_seconds * 1000.0, 6),
        "profile_enabled": profile_enabled,
        "profile_path": str(profile_path),
        "log_path": str(log_path),
        "hotspot_path": str(hotspot_path),
    }
    with artifact_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return artifact_file


def _profile_execution(label: str, fn: Callable[[], None]) -> None:
    """
    Purpose:
        Execute a benchmark callable with optional cProfile capture.
    Contract:
        - When `DI_CPROFILE` is disabled, executes callable without profiling.
        - When enabled, captures and persists a `.prof` artifact.
    Args:
        label: Profile artifact label.
        fn: Callable benchmark lane.
    Returns:
        None.
    """
    profiler = cProfile.Profile()
    profile_enabled = _env_bool("DI_CPROFILE", True)
    sort = os.getenv("DI_CPROFILE_SORT", "cumtime")
    top = _env_int_nonneg("DI_CPROFILE_TOP", 30)

    start = time.perf_counter()
    if profile_enabled:
        profiler.enable()
    try:
        fn()
    finally:
        elapsed = time.perf_counter() - start
        if profile_enabled:
            profiler.disable()

        if profile_enabled:
            profile_path = _dump_profile(label, profiler)
            log_path = _write_profile_log(
                label,
                profiler,
                profile_path,
                sort=sort,
                top=top,
            )
            hotspot_path = _write_hotspot_artifact(
                label,
                profile_path=profile_path,
                hotspots=_extract_top_hotspots(profiler, sort=sort, top=top),
            )
        else:
            artifact_dir = Path(
                os.getenv(
                    "DI_CPROFILE_DIR",
                    "benchmarks/testing_other_di/profiles/fast_graphs_melder",
                )
            )
            artifact_dir.mkdir(parents=True, exist_ok=True)
            profile_path = artifact_dir / f"{label}.prof"
            log_path = artifact_dir / f"{label}.pstats.txt"
            log_path.write_text(
                f"label={label}\nprofile_enabled=False\nelapsed_ms={elapsed * 1000.0:.6f}\n",
                encoding="utf-8",
            )
            hotspot_path = _write_disabled_hotspot_artifact(label, artifact_dir)
            print(f"[melder][benchmark] {label} profile_disabled elapsed_ms={elapsed * 1000.0:.3f}")

        benchmark_file = _append_benchmark_record(
            label,
            elapsed,
            profile_enabled=profile_enabled,
            profile_path=profile_path,
            log_path=log_path,
            hotspot_path=hotspot_path,
        )
        print(f"[melder][benchmark] {label} benchmark={benchmark_file} elapsed_ms={elapsed * 1000.0:.3f}")


def _build_melder_runtime_ops(graph_name: str) -> Tuple[Any, Any]:
    """
    Purpose:
        Build melder runtime operations for a selected fast graph.
    Contract:
        - Graphs are resolved from the canonical `test_shallow_all` graph registry.
        - Runtime ops are always melder-only (`_build_ops("melder", ...)`).
    Args:
        graph_name: Fast graph name.
    Returns:
        Tuple of `(graph_spec, runtime_ops)`.
    Raises:
        AssertionError: If the graph name is unknown.
    """
    specs = _fast_graph_specs_by_name()
    graph_spec = specs.get(graph_name)
    if graph_spec is None:
        raise AssertionError(f"Unknown graph '{graph_name}'. Supported: {_FAST_GRAPH_NAMES}")
    runtime_ops = shallow_all._build_ops("melder", graph_spec)
    return graph_spec, runtime_ops


@pytest.mark.parametrize("graph", _FAST_GRAPH_NAMES)
def test_melder_fast_graphs_single_resolve_smoke_cprofile(graph: str) -> None:
    """
    Purpose:
        Capture cProfile smoke-path artifacts for melder on fast graphs only.
    Contract:
        - Executes the same smoke route shape as `test_shallow_all` single resolve lane:
          root A resolve, root B resolve, spellspace cycle.
        - Asserts resolved types match graph contract.
        - Always cleans up runtime ops.
    Args:
        graph: Graph name in fast graph tuple.
    Returns:
        None.
    """
    graph_spec, ops = _build_melder_runtime_ops(graph)
    try:
        def _run() -> None:
            root_a = ops.get_root_a()
            root_b = ops.get_root_b()
            assert isinstance(root_a, graph_spec.root_a)
            assert isinstance(root_b, graph_spec.root_b)
            ops.spellspace_cycle()

        _profile_execution(f"melder_fast_smoke_{graph}", _run)
    finally:
        ops.cleanup()


@pytest.mark.parametrize("graph", _FAST_GRAPH_NAMES)
def test_melder_fast_graphs_single_resolve_timings_cprofile(graph: str) -> None:
    """
    Purpose:
        Capture cProfile timing-lane artifacts for melder on fast graphs only.
    Contract:
        - Mirrors timing lane shape from `test_shallow_all` by running warmup then repeated
          root A/root B/spellspace cycles.
        - Obeys `DI_RUN_SINGLE`; skips when disabled.
        - Always cleans up runtime ops.
    Args:
        graph: Graph name in fast graph tuple.
    Returns:
        None.
    Raises:
        AssertionError: If configured profile iteration count is not positive.
    """
    if not _env_bool("DI_RUN_SINGLE", True):
        pytest.skip("DI_RUN_SINGLE not enabled")

    warmup_iters = _env_int_nonneg("DI_SINGLE_AVG_WARMUP_ITERS", 100)
    profile_iters = _env_int_nonneg("DI_CPROFILE_ITERS", _env_int_nonneg("DI_SINGLE_AVG_ITERS", 1000))
    if profile_iters <= 0:
        raise AssertionError("DI_CPROFILE_ITERS must be > 0")

    graph_spec, ops = _build_melder_runtime_ops(graph)
    try:
        def _run() -> None:
            for _ in range(warmup_iters):
                ops.get_root_a()
                ops.get_root_b()
                ops.spellspace_cycle()
            for _ in range(profile_iters):
                root_a = ops.get_root_a()
                root_b = ops.get_root_b()
                assert isinstance(root_a, graph_spec.root_a)
                assert isinstance(root_b, graph_spec.root_b)
                ops.spellspace_cycle()

        _profile_execution(f"melder_fast_timings_{graph}", _run)
    finally:
        ops.cleanup()
