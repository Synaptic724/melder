import cProfile
import json
import io
import os
import pstats
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import pytest

from benchmarks.testing_other_di import test_overrides_all as overrides_all


_DEFAULT_FAST_OVERRIDE_GRAPHS: Tuple[str, ...] = ("solo", "shallow", "wide", "diamond")


def _env_str(name: str, default: str) -> str:
    """
    Purpose:
        Read a string environment variable with fallback.
    Contract:
        - Returns `default` when missing or empty.
    Args:
        name: Environment variable name.
        default: Fallback value.
    Returns:
        Parsed string value.
    """
    raw = os.getenv(name)
    return default if raw is None or raw == "" else raw


def _parse_csv(value: str) -> Tuple[str, ...]:
    """
    Purpose:
        Parse a comma-separated list into a normalized tuple.
    Contract:
        - Trims whitespace and drops empty segments.
    Args:
        value: Raw CSV string.
    Returns:
        Tuple of non-empty trimmed items.
    """
    return tuple(part.strip() for part in value.split(",") if part.strip())


def _env_bool(name: str, default: bool) -> bool:
    """
    Purpose:
        Parse a boolean environment toggle.
    Contract:
        - Accepts truthy values: 1,true,yes,on (case-insensitive).
        - Accepts falsy values: 0,false,no,off (case-insensitive).
        - Falls back to `default` for missing or unrecognized values.
    Args:
        name: Environment variable name.
        default: Fallback boolean.
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
        Parse a non-negative integer environment variable.
    Contract:
        - Uses `default` when missing.
        - Raises AssertionError when value is not an integer or is negative.
    Args:
        name: Environment variable name.
        default: Fallback integer.
    Returns:
        Parsed non-negative integer.
    Raises:
        AssertionError: If parsing fails or value is negative.
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
        Parse a non-negative float environment variable.
    Contract:
        - Uses `default` when missing.
        - Raises AssertionError when value is not a float or is negative.
    Args:
        name: Environment variable name.
        default: Fallback float.
    Returns:
        Parsed non-negative float.
    Raises:
        AssertionError: If parsing fails or value is negative.
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


def _resolve_override_duration_seconds() -> float:
    """
    Purpose:
        Resolve optional duration-budget mode for override benchmark lanes.
    Contract:
        - `DI_OVERRIDE_CPROFILE_DURATION_S` takes precedence for this suite.
        - Falls back to shared `DI_BENCHMARK_DURATION_S`.
        - `0.0` disables duration mode (default behavior).
    Returns:
        Duration budget in seconds.
    """
    shared = _env_float_nonneg("DI_BENCHMARK_DURATION_S", 0.0)
    return _env_float_nonneg("DI_OVERRIDE_CPROFILE_DURATION_S", shared)


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


def _selected_override_graphs() -> Tuple[str, ...]:
    """
    Purpose:
        Resolve selected override graph names for this suite.
    Contract:
        - Reads from `DI_OVERRIDE_GRAPHS` with fast-graph default.
        - Validates requested names against `test_overrides_all` graph registry.
    Returns:
        Tuple of selected graph names.
    Raises:
        AssertionError: If an unknown graph is requested.
    """
    default = ",".join(_DEFAULT_FAST_OVERRIDE_GRAPHS)
    selected = _parse_csv(_env_str("DI_OVERRIDE_GRAPHS", default))
    available = {graph.name for graph in overrides_all._override_graphs()}
    for name in selected:
        if name not in available:
            raise AssertionError(f"Unknown override graph '{name}'. Supported: {sorted(available)}")
    return selected


def _override_graph_specs_by_name() -> Dict[str, Any]:
    """
    Purpose:
        Build a graph-spec map for selected overrides graph names.
    Contract:
        - Returns specs for exactly `_selected_override_graphs()`.
    Returns:
        Mapping from graph name to graph specification object.
    """
    selected = _selected_override_graphs()
    all_specs = {graph.name: graph for graph in overrides_all._override_graphs()}
    return {name: all_specs[name] for name in selected}


def _build_melder_override_ops(graph_name: str) -> Tuple[Any, Any]:
    """
    Purpose:
        Build melder override runtime ops for a selected graph.
    Contract:
        - Uses `test_overrides_all._build_override_ops("melder", spec)` to keep runtime
          wiring behavior identical to baseline override benchmark.
    Args:
        graph_name: Selected graph name.
    Returns:
        Tuple of `(graph_spec, override_ops)`.
    Raises:
        AssertionError: If graph name is unknown.
    """
    specs = _override_graph_specs_by_name()
    spec = specs.get(graph_name)
    if spec is None:
        raise AssertionError(f"Unknown override graph '{graph_name}'.")
    ops = overrides_all._build_override_ops("melder", spec)
    return spec, ops


def _dump_profile(label: str, profile: cProfile.Profile) -> Path:
    """
    Purpose:
        Persist cProfile stats artifact and optionally print pstats summary.
    Contract:
        - Writes `<label>.prof` into `DI_OVERRIDE_CPROFILE_DIR` or default path.
        - Prints pstats only when `DI_OVERRIDE_CPROFILE_PRINT=1`.
    Args:
        label: Artifact label.
        profile: Completed cProfile object.
    Returns:
        Path to profile artifact.
    """
    out_dir = Path(
        _env_str(
            "DI_OVERRIDE_CPROFILE_DIR",
            "benchmarks/testing_other_di/profiles/overrides_graphs_melder",
        )
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{label}.prof"
    profile.dump_stats(str(out_path))

    if _env_bool("DI_OVERRIDE_CPROFILE_PRINT", False):
        sort = _env_str("DI_OVERRIDE_CPROFILE_SORT", "cumtime")
        top = _env_int_nonneg("DI_OVERRIDE_CPROFILE_TOP", 30)
        stream = io.StringIO()
        stats = pstats.Stats(profile, stream=stream).strip_dirs().sort_stats(sort)
        stats.print_stats(top)
        print(f"[melder][override-cprofile] {label} profile={out_path} sort={sort} top={top}")
        print(stream.getvalue())
    else:
        print(f"[melder][override-cprofile] {label} profile={out_path}")

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
        Persist text pstats summary artifact.
    Contract:
        - Writes `<label>.pstats.txt` into `DI_OVERRIDE_CPROFILE_LOG_DIR` or profile dir.
    Args:
        label: Artifact label.
        profile: Completed cProfile object.
        profile_path: Existing `.prof` path.
        sort: pstats sort key.
        top: Maximum rows to print.
    Returns:
        Path to text summary artifact.
    """
    stream = io.StringIO()
    stats = pstats.Stats(profile, stream=stream).strip_dirs().sort_stats(sort)
    stats.print_stats(top)

    configured = os.getenv("DI_OVERRIDE_CPROFILE_LOG_DIR")
    out_dir = Path(configured) if configured is not None else profile_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{label}.pstats.txt"
    header = (
        f"label={label}\n"
        f"profile={profile_path}\n"
        f"sort={sort}\n"
        f"top={top}\n\n"
    )
    out_path.write_text(header + stream.getvalue(), encoding="utf-8")
    return out_path


def _extract_top_hotspots(profile: cProfile.Profile, *, sort: str, top: int) -> List[Dict[str, Any]]:
    """
    Purpose:
        Convert cProfile stats into top hotspot rows.
    Contract:
        - Uses `sort` and `top` to rank rows.
    Args:
        profile: Completed cProfile object.
        sort: pstats sort key.
        top: Maximum rows.
    Returns:
        List of hotspot dictionaries.
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


def _write_hotspot_artifact(label: str, *, profile_path: Path, hotspots: List[Dict[str, Any]]) -> Path:
    """
    Purpose:
        Persist structured hotspot rows as JSON.
    Contract:
        - Writes `<label>.hotspots.json` into `DI_OVERRIDE_CPROFILE_HOTSPOT_DIR` or profile dir.
    Args:
        label: Artifact label.
        profile_path: Existing `.prof` path.
        hotspots: Structured hotspot rows.
    Returns:
        Path to hotspot artifact.
    """
    configured = os.getenv("DI_OVERRIDE_CPROFILE_HOTSPOT_DIR")
    out_dir = Path(configured) if configured is not None else profile_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{label}.hotspots.json"
    payload = {"label": label, "profile_path": str(profile_path), "hotspots": hotspots}
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return out_path


def _extract_override_codegen_call_chains(profile: cProfile.Profile, *, top_edges: int) -> List[Dict[str, Any]]:
    """
    Purpose:
        Extract caller/callee chains for override-related codegen functions.
    Contract:
        - Includes both override and no-override codegen markers so mixed graph modes are visible.
    Args:
        profile: Completed cProfile object.
        top_edges: Maximum caller/callee edges per function.
    Returns:
        List of call-chain rows.
    """
    stats = pstats.Stats(profile).strip_dirs()
    stats.calc_callees()
    markers = (
        "creation_context_overrides_only_template",
        "creation_context_no_overrides_only_template",
        "phase12_overrides_executor.py",
        "phase12_no_overrides_executor.py",
        "melder_phase12_overrides",
        "melder_phase12_no_overrides",
    )
    target_funcs = [func for func in stats.stats if any(marker in func[0] for marker in markers)]

    rows: List[Dict[str, Any]] = []
    for func in sorted(target_funcs):
        file_path, line_no, func_name = func
        caller_rows = []
        for caller, values in sorted(stats.stats[func][4].items(), key=lambda kv: kv[1][3], reverse=True)[:top_edges]:
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

        callee_rows = []
        for callee, values in sorted(stats.all_callees.get(func, {}).items(), key=lambda kv: kv[1][3], reverse=True)[
            :top_edges
        ]:
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
        Persist call-chain rows as JSON.
    Contract:
        - Writes `<label>.call_chain.json` into `DI_OVERRIDE_CPROFILE_CALLCHAIN_DIR` or profile dir.
    Args:
        label: Artifact label.
        profile_path: Existing `.prof` path.
        call_chain_rows: Structured caller/callee rows.
    Returns:
        Path to call-chain artifact.
    """
    configured = os.getenv("DI_OVERRIDE_CPROFILE_CALLCHAIN_DIR")
    out_dir = Path(configured) if configured is not None else profile_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{label}.call_chain.json"
    payload = {"label": label, "profile_path": str(profile_path), "call_chain_rows": call_chain_rows}
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
        Build concise human-readable profiling summary lines.
    Contract:
        - Emits compact hotspot rows and call-chain highlights.
    Args:
        label: Lane label.
        elapsed_seconds: End-to-end elapsed time.
        hotspots: Hotspot rows.
        call_chain_rows: Caller/callee rows.
    Returns:
        Summary lines.
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
        top_rows = hotspots[:8]
        lines.append(f"[{label}] top {len(top_rows)} hotspots by cumtime")
        for idx, row in enumerate(top_rows, start=1):
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
        Persist concise text summary for quick reading.
    Contract:
        - Writes `<label>.summary.txt` into `DI_OVERRIDE_CPROFILE_SUMMARY_DIR`
          when set, else into the profile artifact directory.
    Args:
        label: Lane label.
        profile_path: Existing profile artifact path.
        lines: Summary lines.
    Returns:
        Path to summary artifact.
    """
    configured = os.getenv("DI_OVERRIDE_CPROFILE_SUMMARY_DIR")
    out_dir = Path(configured) if configured is not None else profile_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{label}.summary.txt"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


def _append_benchmark_record(
    label: str,
    elapsed_seconds: float,
    *,
    profile_path: Path,
    log_path: Path,
    hotspot_path: Path,
    call_chain_path: Path,
    summary_path: Path,
    sample_metadata: Optional[Dict[str, Any]] = None,
) -> Path:
    """
    Purpose:
        Append a benchmark timing row to a JSONL artifact.
    Contract:
        - Appends one row per test lane execution.
        - Uses `DI_OVERRIDE_BENCHMARK_FILE` when set, else `<profile_dir>/benchmark_results.jsonl`.
    Args:
        label: Lane label.
        elapsed_seconds: End-to-end lane duration.
        profile_path: Profile artifact path.
        log_path: Text log artifact path.
        hotspot_path: Hotspot artifact path.
        call_chain_path: Call-chain artifact path.
        summary_path: Human-readable summary artifact path.
    Returns:
        Path to JSONL benchmark file.
    """
    default_file = profile_path.parent / "benchmark_results.jsonl"
    configured = os.getenv("DI_OVERRIDE_BENCHMARK_FILE")
    out_path = Path(configured) if configured is not None else default_file
    out_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "label": label,
        "elapsed_ms": round(elapsed_seconds * 1000.0, 6),
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
    }
    with out_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")
    return out_path


def _profile_execution(
    label: str,
    fn: Callable[[], None],
    *,
    sample_metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Purpose:
        Execute a benchmark lane with cProfile and write durable artifacts.
    Contract:
        - When `DI_OVERRIDE_CPROFILE=1` (default), emits `.prof`, `.pstats.txt`,
          `.hotspots.json`, `.call_chain.json`, and JSONL benchmark row.
    Args:
        label: Lane label.
        fn: Benchmark callable.
    Returns:
        None.
    """
    profile_enabled = _env_bool("DI_OVERRIDE_CPROFILE", True)
    sort = _env_str("DI_OVERRIDE_CPROFILE_SORT", "cumtime")
    top = _env_int_nonneg("DI_OVERRIDE_CPROFILE_TOP", 30)
    callchain_top = _env_int_nonneg("DI_OVERRIDE_CPROFILE_CALLCHAIN_TOP", 6)

    profiler = cProfile.Profile()
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
            profile_path = _dump_profile(label, profiler)
            log_path = _write_profile_log(label, profiler, profile_path, sort=sort, top=top)
            hotspot_rows = _extract_top_hotspots(profiler, sort=sort, top=top)
            call_chain_rows = _extract_override_codegen_call_chains(profiler, top_edges=callchain_top)
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
            out_dir = Path(
                _env_str(
                    "DI_OVERRIDE_CPROFILE_DIR",
                    "benchmarks/testing_other_di/profiles/overrides_graphs_melder",
                )
            )
            out_dir.mkdir(parents=True, exist_ok=True)
            profile_path = out_dir / f"{label}.prof"
            log_path = out_dir / f"{label}.pstats.txt"
            log_path.write_text(
                f"label={label}\nprofile_enabled=False\nelapsed_ms={elapsed * 1000.0:.6f}\n",
                encoding="utf-8",
            )
            hotspot_path = out_dir / f"{label}.hotspots.json"
            hotspot_path.write_text(
                json.dumps({"label": label, "profile_enabled": False, "hotspots": []}, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            call_chain_path = out_dir / f"{label}.call_chain.json"
            call_chain_path.write_text(
                json.dumps({"label": label, "profile_enabled": False, "call_chain_rows": []}, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            summary_lines = [
                f"[{label}] profiled in {elapsed * 1000.0:.3f}ms",
                f"[{label}] profiling disabled (DI_OVERRIDE_CPROFILE=0)",
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

        benchmark_path = _append_benchmark_record(
            label,
            elapsed,
            profile_path=profile_path,
            log_path=log_path,
            hotspot_path=hotspot_path,
            call_chain_path=call_chain_path,
            summary_path=summary_path,
            sample_metadata=normalized_sample_metadata,
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
            f"[melder][override-benchmark] {label} benchmark={benchmark_path} "
            f"elapsed_ms={elapsed * 1000.0:.3f}{sample_suffix}"
        )


def _assert_override_applied(graph_spec: Any, ops: Any, root: Any) -> None:
    """
    Purpose:
        Validate that override values are applied to a resolved root.
    Contract:
        - Every value returned by `graph_spec.override_accessor(root)` must be the
          same object instance as `ops.override_instance`.
    Args:
        graph_spec: Override graph specification.
        ops: Runtime override ops object.
        root: Resolved root object.
    Returns:
        None.
    Raises:
        AssertionError: If override did not apply.
    """
    observed = graph_spec.override_accessor(root)
    for value in observed:
        if value is not ops.override_instance:
            raise AssertionError(f"melder:{graph_spec.name} override did not apply ({value!r} is not override instance)")


@pytest.mark.parametrize("graph", _selected_override_graphs())
def test_melder_overrides_graph_smoke_cprofile(graph: str) -> None:
    """
    Purpose:
        Capture smoke-lane cProfile artifacts for melder override graph routes.
    Contract:
        - Executes one `get_root()` lane call and validates override application.
        - Always cleans up runtime ops.
    Args:
        graph: Selected override graph name.
    Returns:
        None.
    """
    graph_spec, ops = _build_melder_override_ops(graph)
    duration_s = _resolve_override_duration_seconds()
    sample_metadata: Dict[str, Any] = {
        "sample_mode": "duration" if duration_s > 0 else "single",
        "sample_target_duration_s": duration_s if duration_s > 0 else None,
    }
    try:
        def _run_once() -> None:
            root = ops.get_root()
            _assert_override_applied(graph_spec, ops, root)

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
            f"melder_overrides_smoke_{graph}",
            _run,
            sample_metadata=sample_metadata,
        )
    finally:
        ops.cleanup()


@pytest.mark.parametrize("graph", _selected_override_graphs())
def test_melder_overrides_graph_timings_cprofile(graph: str) -> None:
    """
    Purpose:
        Capture timing-lane cProfile artifacts for melder override graph routes.
    Contract:
        - Executes warmup iterations then measured iterations.
        - Validates override application on each measured iteration.
        - Always cleans up runtime ops.
    Args:
        graph: Selected override graph name.
    Returns:
        None.
    Raises:
        AssertionError: If configured profile iterations are invalid.
    """
    if not _env_bool("DI_OVERRIDE_RUN_SINGLE", True):
        pytest.skip("DI_OVERRIDE_RUN_SINGLE not enabled")

    warmup_iters = _env_int_nonneg("DI_OVERRIDE_PROFILE_WARMUP_ITERS", _env_int_nonneg("DI_OVERRIDE_WARMUP_ITERS", 50))
    duration_s = _resolve_override_duration_seconds()
    profile_iters = _env_int_nonneg("DI_OVERRIDE_PROFILE_ITERS", 1000)
    if duration_s <= 0 and profile_iters <= 0:
        raise AssertionError("DI_OVERRIDE_PROFILE_ITERS must be > 0 when duration mode is disabled")

    graph_spec, ops = _build_melder_override_ops(graph)
    sample_metadata: Dict[str, Any] = {
        "sample_mode": "duration" if duration_s > 0 else "iterations",
        "sample_target_duration_s": duration_s if duration_s > 0 else None,
    }
    try:
        def _run_iteration() -> None:
            root = ops.get_root()
            _assert_override_applied(graph_spec, ops, root)

        def _run() -> None:
            for _ in range(warmup_iters):
                _run_iteration()
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
            f"melder_overrides_timings_{graph}",
            _run,
            sample_metadata=sample_metadata,
        )
    finally:
        ops.cleanup()
