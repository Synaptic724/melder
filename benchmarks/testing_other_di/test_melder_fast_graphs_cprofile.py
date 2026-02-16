import cProfile
import json
import io
import os
import pstats
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import pytest

from benchmarks.testing_other_di import test_shallow_all as shallow_all
from benchmarks.p_core_affinity.p_core_affinity import (
    get_or_apply_p_core_affinity_from_env,
)


_FAST_GRAPH_NAMES: Tuple[str, ...] = ("solo", "shallow", "wide", "diamond")


def _resolve_affinity_status() -> Dict[str, Any]:
    """
    Purpose:
        Resolve optional P-core affinity status for the current process.
    Contract:
        - Delegates to shared affinity utility cache.
        - Returns status payload for artifact traceability on every run.
    Returns:
        Structured affinity status dictionary.
    """
    return get_or_apply_p_core_affinity_from_env()


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


def _env_float_nonneg(name: str, default: float) -> float:
    """
    Purpose:
        Parse a non-negative float from the environment.
    Contract:
        - Uses `default` when the variable is missing.
        - Raises AssertionError for non-float or negative values.
    Args:
        name: Environment variable name.
        default: Fallback float value.
    Returns:
        Parsed non-negative float.
    Raises:
        AssertionError: If value cannot be parsed as non-negative float.
    """
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError as exc:
        raise AssertionError(f"{name} must be a float; got {raw!r}.") from exc
    if value < 0:
        raise AssertionError(f"{name} must be >= 0; got {value}.")
    return value


def _resolve_cprofile_duration_seconds() -> float:
    """
    Purpose:
        Resolve optional duration-budget mode for benchmark lanes.
    Contract:
        - `DI_CPROFILE_DURATION_S` takes precedence for this suite.
        - Falls back to shared `DI_BENCHMARK_DURATION_S`.
        - `0.0` disables duration mode (default behavior).
    Returns:
        Duration budget in seconds.
    """
    shared = _env_float_nonneg("DI_BENCHMARK_DURATION_S", 0.0)
    return _env_float_nonneg("DI_CPROFILE_DURATION_S", shared)


def _run_for_duration_budget(
    *,
    run_once: Callable[[], None],
    duration_s: float,
    check_interval: int = 8,
) -> Tuple[int, float]:
    """
    Purpose:
        Execute one benchmark sample repeatedly for at least a target duration.
    Contract:
        - Executes at least one sample.
        - Uses periodic clock checks to keep overhead low.
    Args:
        run_once: One benchmark sample operation.
        duration_s: Target runtime budget in seconds.
        check_interval: Clock-check interval in iterations.
    Returns:
        Tuple `(sample_count, elapsed_seconds)`.
    Raises:
        AssertionError: If duration is non-positive or check interval is invalid.
    """
    if duration_s <= 0:
        raise AssertionError("duration_s must be > 0 for duration mode")
    if check_interval <= 0:
        raise AssertionError("check_interval must be > 0")

    start = time.perf_counter()
    deadline = start + duration_s
    sample_count = 0

    while True:
        run_once()
        sample_count += 1
        if sample_count == 1:
            if time.perf_counter() >= deadline:
                break
            continue
        if sample_count % check_interval == 0 and time.perf_counter() >= deadline:
            break

    elapsed = time.perf_counter() - start
    return sample_count, elapsed


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


def _extract_codegen_call_chains(
    profile: cProfile.Profile,
    *,
    top_edges: int,
) -> List[Dict[str, Any]]:
    """
    Purpose:
        Extract caller/callee edges for codegen-relevant functions from cProfile stats.
    Contract:
        - Targets function names that include creation-context or phase12 markers.
        - Returns a list of function records with top caller/callee edges.
    Args:
        profile: Completed cProfile instance.
        top_edges: Maximum caller/callee edges per function.
    Returns:
        Structured call-chain rows.
    """
    stats = pstats.Stats(profile).strip_dirs()
    stats.calc_callees()
    target_markers = (
        "creation_context",
        "phase12_no_overrides_executor.py",
        "phase12_overrides_executor.py",
        "melder_phase12_no_overrides",
        "melder_phase12_overrides",
    )
    target_funcs = [f for f in stats.stats if any(marker in f[0] for marker in target_markers)]

    rows: List[Dict[str, Any]] = []
    for func in sorted(target_funcs):
        file_path, line_no, func_name = func
        callers = stats.stats[func][4]
        caller_rows = []
        for caller, values in sorted(callers.items(), key=lambda kv: kv[1][3], reverse=True)[:top_edges]:
            c_file, c_line, c_name = caller
            caller_rows.append(
                {
                    "function": f"{c_file}:{c_line}({c_name})",
                    "cumtime_s": round(float(values[3]), 9),
                    "tottime_s": round(float(values[2]), 9),
                    "total_calls": values[1],
                    "primitive_calls": values[0],
                }
            )

        callees = stats.all_callees.get(func, {})
        callee_rows = []
        for callee, values in sorted(callees.items(), key=lambda kv: kv[1][3], reverse=True)[:top_edges]:
            d_file, d_line, d_name = callee
            callee_rows.append(
                {
                    "function": f"{d_file}:{d_line}({d_name})",
                    "cumtime_s": round(float(values[3]), 9),
                    "tottime_s": round(float(values[2]), 9),
                    "total_calls": values[1],
                    "primitive_calls": values[0],
                }
            )

        rows.append(
            {
                "function": f"{file_path}:{line_no}({func_name})",
                "callers": caller_rows,
                "callees": callee_rows,
            }
        )
    return rows


def _write_call_chain_artifact(
    label: str,
    *,
    profile_path: Path,
    call_chain_rows: List[Dict[str, Any]],
) -> Path:
    """
    Purpose:
        Persist codegen call-chain rows to a JSON artifact.
    Contract:
        - Writes `<label>.call_chain.json` into `DI_CPROFILE_CALLCHAIN_DIR` when set,
          else to the profile artifact directory.
    Args:
        label: Profile artifact label.
        profile_path: Existing `.prof` artifact path.
        call_chain_rows: Structured call-chain records.
    Returns:
        Path to written call-chain artifact.
    """
    configured = os.getenv("DI_CPROFILE_CALLCHAIN_DIR")
    out_dir = Path(configured) if configured is not None else profile_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{label}.call_chain.json"
    payload = {
        "label": label,
        "profile_path": str(profile_path),
        "call_chain_rows": call_chain_rows,
    }
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return out_path


def _write_disabled_call_chain_artifact(label: str, artifact_dir: Path) -> Path:
    """
    Purpose:
        Persist an explicit call-chain artifact when cProfile is disabled.
    Contract:
        - Writes `<label>.call_chain.json` with `profile_enabled=false`.
    Args:
        label: Benchmark lane label.
        artifact_dir: Base artifact directory.
    Returns:
        Path of written call-chain artifact.
    """
    artifact_dir.mkdir(parents=True, exist_ok=True)
    out_path = artifact_dir / f"{label}.call_chain.json"
    payload = {
        "label": label,
        "profile_enabled": False,
        "call_chain_rows": [],
    }
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return out_path


def _build_quick_summary_lines(
    *,
    label: str,
    elapsed_seconds: float,
    hotspots: List[Dict[str, Any]],
    call_chain_rows: List[Dict[str, Any]],
    sample_metadata: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """
    Purpose:
        Build concise, human-readable profiling summary lines.
    Contract:
        - Emits compact hotspot rows and call-chain highlights.
        - Uses cumulative-time ordering from provided hotspot rows.
    Args:
        label: Benchmark label.
        elapsed_seconds: End-to-end elapsed time.
        hotspots: Structured hotspot rows.
        call_chain_rows: Structured call-chain rows.
    Returns:
        Summary lines suitable for console output and text artifacts.
    """
    lines: List[str] = []
    elapsed_ms = elapsed_seconds * 1000.0
    lines.append(f"[{label}] profiled in {elapsed_ms:.3f}ms")
    if sample_metadata is not None:
        sample_count = sample_metadata.get("sample_count")
        sample_avg_ms = sample_metadata.get("sample_avg_ms")
        sample_mode = sample_metadata.get("sample_mode")
        if sample_count is not None and sample_avg_ms is not None:
            lines.append(
                f"[{label}] samples={sample_count} sample_avg_ms={float(sample_avg_ms):.6f} mode={sample_mode}"
            )
        elif sample_count is not None:
            lines.append(f"[{label}] samples={sample_count} mode={sample_mode}")

    if not hotspots:
        lines.append(f"[{label}] no hotspots collected")
    else:
        top_hotspots = hotspots[:8]
        lines.append(f"[{label}] top {len(top_hotspots)} hotspots by cumtime")
        for idx, row in enumerate(top_hotspots, start=1):
            lines.append(
                "  {0:02d}. {1} calls={2} cum={3:.6f}s".format(
                    idx,
                    row["function"],
                    row["total_calls"],
                    float(row["cumtime_s"]),
                )
            )

    chain_focus = [
        row
        for row in call_chain_rows
        if (
            "_creation_context_execute_" in row["function"]
            or "_phase12_executor" in row["function"]
            or "phase12_" in row["function"]
        )
    ]
    if not chain_focus:
        lines.append(f"[{label}] no codegen chain rows collected")
    else:
        lines.append(f"[{label}] call-chain highlights")
        for row in chain_focus[:6]:
            caller = row["callers"][0]["function"] if row["callers"] else "<none>"
            callee = row["callees"][0]["function"] if row["callees"] else "<none>"
            lines.append(f"  func: {row['function']}")
            lines.append(f"    caller: {caller}")
            lines.append(f"    callee: {callee}")

    return lines


def _write_summary_artifact(
    *,
    label: str,
    profile_path: Path,
    lines: List[str],
) -> Path:
    """
    Purpose:
        Persist a concise text summary artifact for quick review.
    Contract:
        - Writes `<label>.summary.txt` into `DI_CPROFILE_SUMMARY_DIR` when set,
          else to the profile artifact directory.
    Args:
        label: Benchmark label.
        profile_path: Existing profile artifact path.
        lines: Preformatted summary lines.
    Returns:
        Path of the written summary artifact.
    """
    configured = os.getenv("DI_CPROFILE_SUMMARY_DIR")
    out_dir = Path(configured) if configured is not None else profile_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{label}.summary.txt"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


def _append_benchmark_record(
    label: str,
    elapsed_seconds: float,
    *,
    profile_enabled: bool,
    profile_path: Path,
    log_path: Path,
    hotspot_path: Path,
    call_chain_path: Path,
    summary_path: Path,
    sample_metadata: Optional[Dict[str, Any]] = None,
    affinity_metadata: Optional[Dict[str, Any]] = None,
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
        call_chain_path: Persisted structured call-chain artifact path.
        summary_path: Persisted human-readable summary artifact path.
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
        "call_chain_path": str(call_chain_path),
        "summary_path": str(summary_path),
        "sample_mode": None if sample_metadata is None else sample_metadata.get("sample_mode"),
        "sample_count": None if sample_metadata is None else sample_metadata.get("sample_count"),
        "sample_avg_ms": None if sample_metadata is None else sample_metadata.get("sample_avg_ms"),
        "sample_target_duration_s": (
            None if sample_metadata is None else sample_metadata.get("sample_target_duration_s")
        ),
        "sample_actual_duration_s": (
            None if sample_metadata is None else sample_metadata.get("sample_actual_duration_s")
        ),
        "affinity_requested": (
            None if affinity_metadata is None else affinity_metadata.get("requested")
        ),
        "affinity_applied": (
            None if affinity_metadata is None else affinity_metadata.get("applied")
        ),
        "affinity_reason": (
            None if affinity_metadata is None else affinity_metadata.get("reason")
        ),
        "affinity_selected": (
            None if affinity_metadata is None else affinity_metadata.get("selected_affinity")
        ),
    }
    with artifact_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return artifact_file


def _profile_execution(
    label: str,
    fn: Callable[[], None],
    *,
    sample_metadata: Optional[Dict[str, Any]] = None,
) -> None:
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
    affinity_metadata = _resolve_affinity_status()

    start = time.perf_counter()
    if profile_enabled:
        profiler.enable()
    try:
        fn()
    finally:
        elapsed = time.perf_counter() - start
        normalized_sample_metadata = None if sample_metadata is None else dict(sample_metadata)
        if normalized_sample_metadata is not None:
            sample_count = normalized_sample_metadata.get("sample_count")
            if (
                sample_count is not None
                and float(sample_count) > 0
                and normalized_sample_metadata.get("sample_avg_ms") is None
            ):
                normalized_sample_metadata["sample_avg_ms"] = (
                    elapsed * 1000.0
                ) / float(sample_count)
            if (
                normalized_sample_metadata.get("sample_mode") == "duration"
                and normalized_sample_metadata.get("sample_actual_duration_s") is None
            ):
                normalized_sample_metadata["sample_actual_duration_s"] = elapsed
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
            hotspot_rows = _extract_top_hotspots(profiler, sort=sort, top=top)
            call_chain_rows = _extract_codegen_call_chains(
                profiler,
                top_edges=_env_int_nonneg("DI_CPROFILE_CALLCHAIN_TOP", 6),
            )
            hotspot_path = _write_hotspot_artifact(
                label,
                profile_path=profile_path,
                hotspots=hotspot_rows,
            )
            call_chain_path = _write_call_chain_artifact(
                label,
                profile_path=profile_path,
                call_chain_rows=call_chain_rows,
            )
            summary_lines = _build_quick_summary_lines(
                label=label,
                elapsed_seconds=elapsed,
                hotspots=hotspot_rows,
                call_chain_rows=call_chain_rows,
                sample_metadata=normalized_sample_metadata,
            )
            for line in summary_lines:
                print(line)
            summary_path = _write_summary_artifact(
                label=label,
                profile_path=profile_path,
                lines=summary_lines,
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
            call_chain_path = _write_disabled_call_chain_artifact(label, artifact_dir)
            summary_lines = [
                f"[{label}] profiled in {elapsed * 1000.0:.3f}ms",
                f"[{label}] profiling disabled (DI_CPROFILE=0)",
            ]
            if normalized_sample_metadata is not None:
                sample_count = normalized_sample_metadata.get("sample_count")
                sample_avg_ms = normalized_sample_metadata.get("sample_avg_ms")
                sample_mode = normalized_sample_metadata.get("sample_mode")
                if sample_count is not None and sample_avg_ms is not None:
                    summary_lines.append(
                        f"[{label}] samples={sample_count} sample_avg_ms={float(sample_avg_ms):.6f} mode={sample_mode}"
                    )
            for line in summary_lines:
                print(line)
            summary_path = _write_summary_artifact(
                label=label,
                profile_path=profile_path,
                lines=summary_lines,
            )
            print(f"[melder][benchmark] {label} profile_disabled elapsed_ms={elapsed * 1000.0:.3f}")

        benchmark_file = _append_benchmark_record(
            label,
            elapsed,
            profile_enabled=profile_enabled,
            profile_path=profile_path,
            log_path=log_path,
            hotspot_path=hotspot_path,
            call_chain_path=call_chain_path,
            summary_path=summary_path,
            sample_metadata=normalized_sample_metadata,
            affinity_metadata=affinity_metadata,
        )
        sample_suffix = ""
        if normalized_sample_metadata is not None:
            sample_count = normalized_sample_metadata.get("sample_count")
            sample_avg_ms = normalized_sample_metadata.get("sample_avg_ms")
            sample_mode = normalized_sample_metadata.get("sample_mode")
            if sample_count is not None and sample_avg_ms is not None:
                sample_suffix = (
                    f" sample_count={sample_count} sample_avg_ms={float(sample_avg_ms):.6f} mode={sample_mode}"
                )
        print(
            f"[melder][benchmark] {label} benchmark={benchmark_file} "
            f"elapsed_ms={elapsed * 1000.0:.3f}{sample_suffix}"
        )


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
    duration_s = _resolve_cprofile_duration_seconds()
    sample_metadata: Dict[str, Any] = {
        "sample_mode": "duration" if duration_s > 0 else "single",
        "sample_target_duration_s": duration_s if duration_s > 0 else None,
    }
    try:
        def _run_once() -> None:
            root_a = ops.get_root_a()
            root_b = ops.get_root_b()
            assert isinstance(root_a, graph_spec.root_a)
            assert isinstance(root_b, graph_spec.root_b)
            ops.spellspace_cycle()

        def _run() -> None:
            if duration_s > 0:
                sample_count, sample_elapsed = _run_for_duration_budget(
                    run_once=_run_once,
                    duration_s=duration_s,
                )
                sample_metadata["sample_count"] = sample_count
                sample_metadata["sample_actual_duration_s"] = sample_elapsed
                return
            _run_once()
            sample_metadata["sample_count"] = 1

        _profile_execution(
            f"melder_fast_smoke_{graph}",
            _run,
            sample_metadata=sample_metadata,
        )
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
    duration_s = _resolve_cprofile_duration_seconds()
    profile_iters = _env_int_nonneg("DI_CPROFILE_ITERS", _env_int_nonneg("DI_SINGLE_AVG_ITERS", 1000))
    if duration_s <= 0 and profile_iters <= 0:
        raise AssertionError("DI_CPROFILE_ITERS must be > 0 when duration mode is disabled")

    graph_spec, ops = _build_melder_runtime_ops(graph)
    sample_metadata: Dict[str, Any] = {
        "sample_mode": "duration" if duration_s > 0 else "iterations",
        "sample_target_duration_s": duration_s if duration_s > 0 else None,
    }
    try:
        def _run_iteration() -> None:
            root_a = ops.get_root_a()
            root_b = ops.get_root_b()
            assert isinstance(root_a, graph_spec.root_a)
            assert isinstance(root_b, graph_spec.root_b)
            ops.spellspace_cycle()

        def _run() -> None:
            for _ in range(warmup_iters):
                ops.get_root_a()
                ops.get_root_b()
                ops.spellspace_cycle()
            if duration_s > 0:
                sample_count, sample_elapsed = _run_for_duration_budget(
                    run_once=_run_iteration,
                    duration_s=duration_s,
                )
                sample_metadata["sample_count"] = sample_count
                sample_metadata["sample_actual_duration_s"] = sample_elapsed
                return

            for _ in range(profile_iters):
                _run_iteration()
            sample_metadata["sample_count"] = profile_iters

        _profile_execution(
            f"melder_fast_timings_{graph}",
            _run,
            sample_metadata=sample_metadata,
        )
    finally:
        ops.cleanup()
