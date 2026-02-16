import argparse
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple


def _resolve_repo_root() -> Path:
    """
    Resolve repository root from this script location.

    Contract:
        - Assumes script path is `<repo>/benchmarks/testing_other_di/run_snapshot_timings.py`.
        - Returns `<repo>` path.
    """
    return Path(__file__).resolve().parents[2]


def _ensure_import_paths(repo_root: Path) -> None:
    """
    Ensure repository import paths are present in `sys.path`.

    Contract:
        - Inserts `<repo>` so namespace imports like `benchmarks.testing_other_di.*` work.
        - Inserts `<repo>/src` at path index 0 when present and absent from `sys.path`.
        - Does nothing for paths already present.
    """
    repo_str = str(repo_root)
    if repo_str not in sys.path:
        sys.path.insert(0, repo_str)

    src_path = repo_root / "src"
    if not src_path.exists():
        return
    src_str = str(src_path)
    if src_str in sys.path:
        return
    sys.path.insert(0, src_str)


def _parse_csv(value: str) -> Tuple[str, ...]:
    """
    Parse a comma-separated string into a normalized tuple.

    Contract:
        - Trims whitespace around each item.
        - Drops empty segments.
        - Returns tuple preserving source order.
    """
    return tuple(part.strip() for part in value.split(",") if part.strip())


def _positive_int(value: str) -> int:
    """
    Parse a strictly-positive integer CLI value.

    Contract:
        - Raises `argparse.ArgumentTypeError` when value is non-integer or <= 0.
    """
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Expected integer, got {value!r}.") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError(f"Expected integer > 0, got {parsed}.")
    return parsed


def _nonnegative_int(value: str) -> int:
    """
    Parse a non-negative integer CLI value.

    Contract:
        - Raises `argparse.ArgumentTypeError` when value is non-integer or < 0.
    """
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Expected integer, got {value!r}.") from exc
    if parsed < 0:
        raise argparse.ArgumentTypeError(f"Expected integer >= 0, got {parsed}.")
    return parsed


def _nonnegative_float(value: str) -> float:
    """
    Parse a non-negative float CLI value.

    Contract:
        - Raises `argparse.ArgumentTypeError` when value is non-numeric or < 0.
    """
    try:
        parsed = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Expected float, got {value!r}.") from exc
    if parsed < 0.0:
        raise argparse.ArgumentTypeError(f"Expected float >= 0, got {parsed}.")
    return parsed


def _build_parser() -> argparse.ArgumentParser:
    """
    Build CLI parser for averaged snapshot benchmark execution.

    Contract:
        - Defaults to 1000 measured iterations and 100 warmup iterations.
        - Supports explicit 10000+ iteration runs via `--iterations`.
        - Uses the same fast/overrides graph lanes as cProfile suites by default.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Run non-cProfile benchmark snapshots for Melder fast/overrides lanes "
            "and emit averaged timing artifacts."
        )
    )
    parser.add_argument(
        "--snapshot-label",
        default="snapshot",
        help="Label prefix used in output artifact names.",
    )
    parser.add_argument(
        "--iterations",
        type=_positive_int,
        default=1000,
        help="Measured iteration count per lane (default: 1000; 10000 is supported).",
    )
    parser.add_argument(
        "--warmup-iters",
        type=_nonnegative_int,
        default=100,
        help="Warmup iteration count per lane before measurement (default: 100).",
    )
    parser.add_argument(
        "--fast-graphs",
        default="solo,shallow,wide,diamond",
        help="CSV list of fast graph names (default: solo,shallow,wide,diamond).",
    )
    parser.add_argument(
        "--override-graphs",
        default="solo,shallow,wide,diamond",
        help="CSV list of override graph names (default: solo,shallow,wide,diamond).",
    )
    parser.add_argument(
        "--output-dir",
        default="benchmarks/testing_other_di/profiles/overrides_graphs_melder",
        help="Directory where JSON and summary artifacts are written.",
    )
    parser.add_argument(
        "--baseline-json",
        default=None,
        help="Optional path to prior snapshot JSON for delta comparison.",
    )
    parser.add_argument(
        "--max-regression-pct",
        type=_nonnegative_float,
        default=None,
        help=(
            "Optional regression threshold for baseline comparison; "
            "if any comparable metric exceeds this percent, exit code is 2."
        ),
    )
    return parser


def _capture_samples_ns(
    fn: Callable[[], Any],
    *,
    iterations: int,
    warmup_iters: int,
) -> Tuple[int, ...]:
    """
    Capture per-call nanosecond samples for one benchmark callable.

    Contract:
        - Executes `fn` exactly `warmup_iters` times before measurement.
        - Executes `fn` exactly `iterations` times under timing capture.
        - Returns immutable nanosecond sample tuple with length `iterations`.
    """
    for _ in range(warmup_iters):
        fn()

    samples: List[int] = []
    for _ in range(iterations):
        start_ns = time.perf_counter_ns()
        fn()
        end_ns = time.perf_counter_ns()
        samples.append(end_ns - start_ns)
    return tuple(samples)


def _build_stats(samples_ns: Sequence[int]) -> Dict[str, Any]:
    """
    Build descriptive statistics for one sample sequence.

    Contract:
        - Requires non-empty sample sequence.
        - Returns count, mean/median/stddev, and min/max in nanoseconds.
        - Uses population standard deviation for deterministic low-sample behavior.
    """
    if not samples_ns:
        raise ValueError("samples_ns must not be empty.")

    values = [int(sample) for sample in samples_ns]
    mean_ns = float(statistics.fmean(values))
    median_ns = float(statistics.median(values))
    stddev_ns = float(statistics.pstdev(values))

    return {
        "count": len(values),
        "mean_ns": mean_ns,
        "median_ns": median_ns,
        "stddev_ns": stddev_ns,
        "min_ns": int(min(values)),
        "max_ns": int(max(values)),
    }


def _ns_to_ms(value_ns: float) -> float:
    """
    Convert nanoseconds to milliseconds.

    Contract:
        - Returns float milliseconds preserving sub-millisecond precision.
    """
    return float(value_ns) / 1_000_000.0


def _extract_mean_ns(stats: Dict[str, Any]) -> float:
    """
    Extract mean nanoseconds from a stats dictionary.

    Contract:
        - Requires `mean_ns` key with numeric value.
        - Raises `ValueError` when contract is violated.
    """
    value = stats.get("mean_ns")
    if not isinstance(value, (int, float)):
        raise ValueError("stats.mean_ns must be numeric.")
    return float(value)


def _build_fast_snapshot(
    *,
    fast_module: Any,
    graph_names: Sequence[str],
    iterations: int,
    warmup_iters: int,
) -> Dict[str, Dict[str, Any]]:
    """
    Capture averaged fast-lane snapshots for selected graphs.

    Contract:
        - Uses canonical melder runtime builder `_build_melder_runtime_ops`.
        - Captures root A, root B, spellspace, and combined-cycle lanes per graph.
        - Always calls `ops.cleanup()` for each graph.
    """
    results: Dict[str, Dict[str, Any]] = {}

    for graph_name in graph_names:
        graph_spec, ops = fast_module._build_melder_runtime_ops(graph_name)
        try:
            def _root_a_call() -> None:
                root_a = ops.get_root_a()
                if not isinstance(root_a, graph_spec.root_a):
                    raise AssertionError(f"{graph_name}: root_a type mismatch.")

            def _root_b_call() -> None:
                root_b = ops.get_root_b()
                if not isinstance(root_b, graph_spec.root_b):
                    raise AssertionError(f"{graph_name}: root_b type mismatch.")

            def _spellspace_call() -> None:
                ops.spellspace_cycle()

            def _cycle_call() -> None:
                root_a = ops.get_root_a()
                root_b = ops.get_root_b()
                if not isinstance(root_a, graph_spec.root_a):
                    raise AssertionError(f"{graph_name}: cycle root_a type mismatch.")
                if not isinstance(root_b, graph_spec.root_b):
                    raise AssertionError(f"{graph_name}: cycle root_b type mismatch.")
                ops.spellspace_cycle()

            lane_results = {
                "root_a": _build_stats(
                    _capture_samples_ns(_root_a_call, iterations=iterations, warmup_iters=warmup_iters)
                ),
                "root_b": _build_stats(
                    _capture_samples_ns(_root_b_call, iterations=iterations, warmup_iters=warmup_iters)
                ),
                "spellspace": _build_stats(
                    _capture_samples_ns(_spellspace_call, iterations=iterations, warmup_iters=warmup_iters)
                ),
                "cycle": _build_stats(
                    _capture_samples_ns(_cycle_call, iterations=iterations, warmup_iters=warmup_iters)
                ),
            }
            results[graph_name] = lane_results
        finally:
            ops.cleanup()

    return results


def _build_override_snapshot(
    *,
    override_module: Any,
    graph_names: Sequence[str],
    iterations: int,
    warmup_iters: int,
) -> Dict[str, Dict[str, Any]]:
    """
    Capture averaged overrides-lane snapshots for selected graphs.

    Contract:
        - Uses canonical melder override builder `_build_melder_override_ops`.
        - Validates override application on every measured call.
        - Always calls `ops.cleanup()` for each graph.
    """
    results: Dict[str, Dict[str, Any]] = {}

    for graph_name in graph_names:
        graph_spec, ops = override_module._build_melder_override_ops(graph_name)
        try:
            def _root_call() -> None:
                root = ops.get_root()
                override_module._assert_override_applied(graph_spec, ops, root)

            results[graph_name] = {
                "root": _build_stats(
                    _capture_samples_ns(_root_call, iterations=iterations, warmup_iters=warmup_iters)
                )
            }
        finally:
            ops.cleanup()

    return results


def _mean_of_means(stats_by_graph: Dict[str, Dict[str, Any]], lane_key: str) -> float:
    """
    Compute aggregate mean across graphs for one lane key.

    Contract:
        - Requires at least one graph result.
        - Uses arithmetic mean of per-graph `mean_ns`.
    """
    if not stats_by_graph:
        raise ValueError("stats_by_graph must not be empty.")

    means: List[float] = []
    for graph_payload in stats_by_graph.values():
        lane_payload = graph_payload.get(lane_key)
        if not isinstance(lane_payload, dict):
            raise ValueError(f"Missing lane '{lane_key}'.")
        means.append(_extract_mean_ns(lane_payload))
    return float(statistics.fmean(means))


def _build_metric_map(snapshot_payload: Dict[str, Any]) -> Dict[str, float]:
    """
    Flatten snapshot payload to comparable metric map.

    Contract:
        - Emits graph-level metrics for fast-cycle and overrides-root means.
        - Emits lane aggregate metrics from `lane_summary`.
    """
    metric_map: Dict[str, float] = {}

    fast_payload = snapshot_payload.get("fast")
    if isinstance(fast_payload, dict):
        for graph_name, graph_lanes in fast_payload.items():
            if not isinstance(graph_lanes, dict):
                continue
            cycle_payload = graph_lanes.get("cycle")
            if isinstance(cycle_payload, dict):
                metric_map[f"fast/{graph_name}/cycle_mean_ns"] = _extract_mean_ns(cycle_payload)

    overrides_payload = snapshot_payload.get("overrides")
    if isinstance(overrides_payload, dict):
        for graph_name, graph_lanes in overrides_payload.items():
            if not isinstance(graph_lanes, dict):
                continue
            root_payload = graph_lanes.get("root")
            if isinstance(root_payload, dict):
                metric_map[f"overrides/{graph_name}/root_mean_ns"] = _extract_mean_ns(root_payload)

    lane_summary = snapshot_payload.get("lane_summary")
    if isinstance(lane_summary, dict):
        for key in ("fast_cycle_mean_ns", "overrides_root_mean_ns", "combined_mean_ns"):
            value = lane_summary.get(key)
            if isinstance(value, (int, float)):
                metric_map[f"lane/{key}"] = float(value)

    return metric_map


def _load_json(path: Path) -> Dict[str, Any]:
    """
    Load JSON payload from disk.

    Contract:
        - Requires existing file path.
        - Requires top-level JSON object.
    """
    if not path.exists():
        raise FileNotFoundError(f"Baseline JSON not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Baseline JSON must be an object.")
    return payload


def _compare_with_baseline(
    *,
    current_payload: Dict[str, Any],
    baseline_payload: Dict[str, Any],
    max_regression_pct: Optional[float],
) -> Dict[str, Any]:
    """
    Compare current snapshot metrics against baseline snapshot metrics.

    Contract:
        - Compares overlapping metric keys only.
        - Returns per-metric deltas in ns and percent.
        - Flags regressions above `max_regression_pct` when threshold is provided.
    """
    current_metrics = _build_metric_map(current_payload)
    baseline_metrics = _build_metric_map(baseline_payload)

    comparable_keys = sorted(set(current_metrics.keys()) & set(baseline_metrics.keys()))

    comparisons: List[Dict[str, Any]] = []
    failures: List[Dict[str, Any]] = []

    for key in comparable_keys:
        baseline_value = baseline_metrics[key]
        current_value = current_metrics[key]
        if baseline_value <= 0.0:
            continue

        delta_ns = current_value - baseline_value
        delta_pct = (delta_ns / baseline_value) * 100.0
        row = {
            "metric": key,
            "baseline_mean_ns": baseline_value,
            "current_mean_ns": current_value,
            "delta_ns": delta_ns,
            "delta_pct": delta_pct,
        }
        comparisons.append(row)

        if max_regression_pct is not None and delta_pct > max_regression_pct:
            failures.append(row)

    return {
        "compared_metric_count": len(comparisons),
        "max_regression_pct": max_regression_pct,
        "comparisons": comparisons,
        "failures": failures,
        "passed": len(failures) == 0,
    }


def _render_summary_lines(
    *,
    payload: Dict[str, Any],
    baseline_path: Optional[Path],
) -> List[str]:
    """
    Render human-readable summary lines for snapshot artifact.

    Contract:
        - Prints per-graph lane means in milliseconds.
        - Includes lane aggregate means and optional baseline deltas.
    """
    lines: List[str] = []

    config = payload.get("config", {})
    lines.append(f"snapshot_label: {payload.get('snapshot_label')}")
    lines.append(f"timestamp_utc: {payload.get('timestamp_utc')}")
    lines.append(f"iterations: {config.get('iterations')}")
    lines.append(f"warmup_iters: {config.get('warmup_iters')}")
    lines.append("")

    fast_payload = payload.get("fast", {})
    if isinstance(fast_payload, dict):
        lines.append("[fast lane]")
        for graph_name in sorted(fast_payload.keys()):
            graph_lanes = fast_payload[graph_name]
            if not isinstance(graph_lanes, dict):
                continue
            for lane_key in ("root_a", "root_b", "spellspace", "cycle"):
                lane_stats = graph_lanes.get(lane_key)
                if not isinstance(lane_stats, dict):
                    continue
                mean_ms = _ns_to_ms(_extract_mean_ns(lane_stats))
                median_ms = _ns_to_ms(float(lane_stats.get("median_ns", 0.0)))
                stddev_ms = _ns_to_ms(float(lane_stats.get("stddev_ns", 0.0)))
                lines.append(
                    f"- {graph_name}/{lane_key}: mean={mean_ms:.6f}ms median={median_ms:.6f}ms stddev={stddev_ms:.6f}ms"
                )
        lines.append("")

    overrides_payload = payload.get("overrides", {})
    if isinstance(overrides_payload, dict):
        lines.append("[overrides lane]")
        for graph_name in sorted(overrides_payload.keys()):
            graph_lanes = overrides_payload[graph_name]
            if not isinstance(graph_lanes, dict):
                continue
            lane_stats = graph_lanes.get("root")
            if not isinstance(lane_stats, dict):
                continue
            mean_ms = _ns_to_ms(_extract_mean_ns(lane_stats))
            median_ms = _ns_to_ms(float(lane_stats.get("median_ns", 0.0)))
            stddev_ms = _ns_to_ms(float(lane_stats.get("stddev_ns", 0.0)))
            lines.append(
                f"- {graph_name}/root: mean={mean_ms:.6f}ms median={median_ms:.6f}ms stddev={stddev_ms:.6f}ms"
            )
        lines.append("")

    lane_summary = payload.get("lane_summary", {})
    if isinstance(lane_summary, dict):
        lines.append("[lane summary]")
        for key in ("fast_cycle_mean_ns", "overrides_root_mean_ns", "combined_mean_ns"):
            value = lane_summary.get(key)
            if isinstance(value, (int, float)):
                lines.append(f"- {key}: {_ns_to_ms(float(value)):.6f}ms")
        lines.append("")

    baseline = payload.get("baseline_comparison")
    if isinstance(baseline, dict):
        lines.append("[baseline comparison]")
        lines.append(f"- baseline_json: {baseline_path}")
        lines.append(f"- compared_metric_count: {baseline.get('compared_metric_count')}")
        lines.append(f"- passed: {baseline.get('passed')}")
        failures = baseline.get("failures", [])
        if isinstance(failures, list) and failures:
            lines.append("- failures:")
            for failure in failures:
                metric = failure.get("metric")
                delta_pct = failure.get("delta_pct")
                lines.append(f"  - {metric}: delta_pct={float(delta_pct):.4f}%")
        lines.append("")

        comparisons = baseline.get("comparisons", [])
        if isinstance(comparisons, list) and comparisons:
            lines.append("[baseline deltas]")
            for row in comparisons:
                metric = row.get("metric")
                baseline_ns = float(row.get("baseline_mean_ns", 0.0))
                current_ns = float(row.get("current_mean_ns", 0.0))
                delta_pct = float(row.get("delta_pct", 0.0))
                lines.append(
                    "- {0}: baseline={1:.6f}ms current={2:.6f}ms delta_pct={3:+.4f}%".format(
                        metric,
                        _ns_to_ms(baseline_ns),
                        _ns_to_ms(current_ns),
                        delta_pct,
                    )
                )
            lines.append("")

    return lines


def _write_artifacts(
    *,
    output_dir: Path,
    snapshot_label: str,
    payload: Dict[str, Any],
    summary_lines: Sequence[str],
) -> Tuple[Path, Path]:
    """
    Write JSON and text summary artifacts for a snapshot payload.

    Contract:
        - Creates output directory when missing.
        - Uses UTC timestamp suffix to keep artifact names unique.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp_tag = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")

    json_path = output_dir / f"{snapshot_label}_snapshot_{timestamp_tag}.json"
    txt_path = output_dir / f"{snapshot_label}_snapshot_summary_{timestamp_tag}.txt"

    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    txt_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    return json_path, txt_path


def run_snapshot(arguments: argparse.Namespace) -> Tuple[Dict[str, Any], Path, Path]:
    """
    Execute one averaged non-cProfile snapshot and persist artifacts.

    Contract:
        - Reuses canonical melder fast/overrides builders from cProfile suites.
        - Computes per-graph lane stats and lane aggregate means.
        - Optionally computes baseline deltas from prior snapshot JSON.
    """
    repo_root = _resolve_repo_root()
    _ensure_import_paths(repo_root)

    from benchmarks.testing_other_di import test_melder_fast_graphs_cprofile as fast_cprofile
    from benchmarks.testing_other_di import test_melder_overrides_graphs_cprofile as overrides_cprofile

    fast_graphs = _parse_csv(arguments.fast_graphs)
    override_graphs = _parse_csv(arguments.override_graphs)

    fast_available = set(fast_cprofile._FAST_GRAPH_NAMES)
    for graph_name in fast_graphs:
        if graph_name not in fast_available:
            raise AssertionError(f"Unknown fast graph '{graph_name}'. Supported: {sorted(fast_available)}")

    override_available = {graph.name for graph in overrides_cprofile.overrides_all._override_graphs()}
    for graph_name in override_graphs:
        if graph_name not in override_available:
            raise AssertionError(
                f"Unknown override graph '{graph_name}'. Supported: {sorted(override_available)}"
            )

    fast_snapshot = _build_fast_snapshot(
        fast_module=fast_cprofile,
        graph_names=fast_graphs,
        iterations=arguments.iterations,
        warmup_iters=arguments.warmup_iters,
    )
    overrides_snapshot = _build_override_snapshot(
        override_module=overrides_cprofile,
        graph_names=override_graphs,
        iterations=arguments.iterations,
        warmup_iters=arguments.warmup_iters,
    )

    fast_lane_mean_ns = _mean_of_means(fast_snapshot, "cycle")
    overrides_lane_mean_ns = _mean_of_means(overrides_snapshot, "root")
    combined_mean_ns = float(statistics.fmean([fast_lane_mean_ns, overrides_lane_mean_ns]))

    payload: Dict[str, Any] = {
        "snapshot_label": arguments.snapshot_label,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "config": {
            "iterations": arguments.iterations,
            "warmup_iters": arguments.warmup_iters,
            "fast_graphs": list(fast_graphs),
            "override_graphs": list(override_graphs),
        },
        "fast": fast_snapshot,
        "overrides": overrides_snapshot,
        "lane_summary": {
            "fast_cycle_mean_ns": fast_lane_mean_ns,
            "overrides_root_mean_ns": overrides_lane_mean_ns,
            "combined_mean_ns": combined_mean_ns,
        },
    }

    baseline_path: Optional[Path] = None
    if arguments.baseline_json is not None:
        baseline_path = Path(arguments.baseline_json)
        baseline_payload = _load_json(baseline_path)
        payload["baseline_comparison"] = _compare_with_baseline(
            current_payload=payload,
            baseline_payload=baseline_payload,
            max_regression_pct=arguments.max_regression_pct,
        )

    summary_lines = _render_summary_lines(payload=payload, baseline_path=baseline_path)
    output_dir = Path(arguments.output_dir)
    json_path, summary_path = _write_artifacts(
        output_dir=output_dir,
        snapshot_label=arguments.snapshot_label,
        payload=payload,
        summary_lines=summary_lines,
    )

    return payload, json_path, summary_path


def main(argv: Optional[Sequence[str]] = None) -> int:
    """
    Program entrypoint for averaged snapshot benchmark runner.

    Contract:
        - Returns 0 when snapshot completes and optional baseline gate passes.
        - Returns 2 when `--max-regression-pct` gate fails.
        - Returns non-zero on unhandled errors.
    """
    parser = _build_parser()
    arguments = parser.parse_args(argv)

    try:
        payload, json_path, summary_path = run_snapshot(arguments)
    except Exception as exc:
        print(f"[snapshot] ERROR: {exc}")
        return 1

    print(f"[snapshot] json={json_path}")
    print(f"[snapshot] summary={summary_path}")

    baseline = payload.get("baseline_comparison")
    if isinstance(baseline, dict):
        passed = bool(baseline.get("passed", True))
        compared_count = baseline.get("compared_metric_count", 0)
        print(
            "[snapshot] baseline compared_metrics={0} passed={1}".format(
                compared_count,
                passed,
            )
        )
        if not passed:
            return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
