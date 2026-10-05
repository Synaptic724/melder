"""Apply the owner's bounded gauntlet workload and child-process changes."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


def replace_once(text: str, old: str, new: str) -> str:
    """Refuse drift or ambiguity before replacing a reviewed source passage."""
    if text.count(old) != 1:
        raise ValueError(f"Expected one match: {old[:110]!r}")
    return text.replace(old, new, 1)


def main() -> None:
    """Preserve exact preimages and apply only benchmark, runner and related test changes."""
    repo = Path("C:/Users/Mark/PycharmProjects/melder_private")
    artifact = repo / "context_compass/artifacts/2026-10-03_real_world_gauntlet_ci"
    relative = "benchmarks/testing_other_di/test_real_world_gauntlet.py"
    target = repo / relative
    raw = target.read_bytes()
    if hashlib.sha256(raw).hexdigest().upper() != "08CFC9C02384E9A204BF5E992D5C82E371CD75AFB08E316C02051E7A70392CC7":
        raise ValueError("Shared gauntlet moved since review")
    source = raw.decode("utf-8").replace("\r\n", "\n")
    source = replace_once(source, "from typing import Any\n", "from typing import Any, Optional\n")
    source = replace_once(source,
        "# Keep this `True` so the shared gauntlet always runs through a standalone\n"
        "# `-X gil=0` subprocess when launched from pytest. Set to `False` only if you\n"
        "# explicitly want the wrapper to use the current interpreter mode instead.\n"
        "REAL_WORLD_GAUNTLET_FORCE_NOGIL = True\n",
        "# Every measured library runs in a fresh child with -X gil=0 and PYTHON_GIL=0.\n"
        "# The measurement entry point also refuses a process whose GIL is enabled.\n")
    source = replace_once(source,
        "        if cfg.threads <= 0 or cfg.threads > 3:\n"
        "            raise AssertionError(\"DI_GAUNTLET_THREADS must be between 1 and 3\")\n",
        "        if cfg.threads <= 0:\n"
        "            raise AssertionError(\"DI_GAUNTLET_THREADS must be > 0\")\n")
    layout = '''def _lane_layout(cfg: _GauntletConfig) -> tuple[tuple[str, str, int, int], ...]:
    """Describe every thread's name, workload family, cycle count and random seed offset.

    Repeat request, worker A and worker B workloads across positive N threads.
    The first three names remain request, worker_a and worker_b. Later threads
    are worker_c, worker_d and onward through worker_z, worker_aa, etc. Each
    name receives its own counters and samples; no two threads mutate one lane.
    A repeated workload uses that family's configured cycle count and class graph.

    Args:
        cfg: Run configuration with a positive thread count.

    Returns:
        Tuples in launch/report order. Existing 1-3-thread seeds are preserved.

    Raises:
        AssertionError: The requested thread count is not positive.
    """
    if cfg.threads <= 0:
        raise AssertionError("DI_GAUNTLET_THREADS must be > 0")
    patterns = (("request", cfg.request_scope_runs),
                ("worker_a", cfg.worker_a_jobs), ("worker_b", cfg.worker_b_jobs))
    lanes: list[tuple[str, str, int, int]] = []
    for index in range(cfg.threads):
        name = "request"
        if index:
            ordinal = index
            label = ""
            while ordinal:
                ordinal, letter = divmod(ordinal - 1, 26)
                label = chr(ord("a") + letter) + label
            name = f"worker_{label}"
        workload, cycles = patterns[index % len(patterns)]
        lanes.append((name, workload, cycles, 17 + 12 * index))
    return tuple(lanes)


def _require_gil_disabled() -> None:
    """Refuse measurement unless this process is actually running without the GIL.

    The subprocess wrapper selects -X gil=0 and PYTHON_GIL=0 before startup.
    Direct runner/profile invocations must select a free-threaded interpreter
    themselves; changing an environment variable after startup is insufficient.

    Raises:
        RuntimeError: The interpreter reports an enabled or unknown GIL state.
    """
    if _gil_status() != "disabled":
        raise RuntimeError(
            "The real-world gauntlet requires the GIL disabled in the measured process. "
            "Run free-threaded Python with -X gil=0 or PYTHON_GIL=0 before process startup."
        )


'''
    source = replace_once(source, "def _lane_objects_per_cycle(name: str) -> int:\n",
                          layout + "def _lane_objects_per_cycle(name: str) -> int:\n")
    source = replace_once(source,
        '    """\n    Time one full gauntlet iteration from fresh container build through cleanup.\n    """\n',
        '''    """Time one synchronized burst against the already-built library container.

    Bootstrap work runs on the parent, then N fresh threads wait at a readiness
    barrier and start together. Each repeats its assigned workload in independent
    scopes and writes only its own named metrics. The parent joins every thread
    before inspecting counters or propagating a worker error. No work queue or
    producer/consumer handoff exists. Total time includes thread startup and
    joining; threaded time begins after readiness. Container setup and terminal
    cleanup are measured separately by _run_gauntlet_benchmark.
    """
''')
    start = source.index('    lane_counts = {', source.index('def _run_gauntlet_once('))
    end = source.index('    ready_barrier = ', start)
    source = source[:start] + '''    layout = _lane_layout(cfg)
    lane_counts = {name: 0 for name, _, _, _ in layout}
    lane_metrics = {name: _new_lane_metric_samples() for name, _, _, _ in layout}
    lane_variant_counts = {name: [0] * _VARIANT_COUNT for name, _, _, _ in layout}
    errors: list[BaseException] = []
    stop_event = threading.Event()
    scope_cycles = {
        "request": ops.request_scope_cycle,
        "worker_a": ops.worker_a_scope_cycle,
        "worker_b": ops.worker_b_scope_cycle,
    }
    active_lanes = [(name, scope_cycles[workload], reps, offset)
                    for name, workload, reps, offset in layout]

''' + source[end:]
    source = replace_once(source, '            call: Callable[[int], None],\n',
                          '            call: Callable[[int], _ScopeCycleMetrics],\n')
    source = replace_once(source,
        '    if lane_counts["request"] != cfg.request_scope_runs:\n'
        '        raise AssertionError("Request lane did not complete expected scope cycles")\n'
        '    if cfg.threads >= 2 and lane_counts["worker_a"] != cfg.worker_a_jobs:\n'
        '        raise AssertionError("Worker A lane did not complete expected scope cycles")\n'
        '    if cfg.threads >= 3 and lane_counts["worker_b"] != cfg.worker_b_jobs:\n'
        '        raise AssertionError("Worker B lane did not complete expected scope cycles")\n',
        '    for name, _, reps, _ in layout:\n'
        '        if lane_counts[name] != reps:\n'
        '            raise AssertionError(f"{name} did not complete expected scope cycles")\n')
    source = replace_once(source,
        '        wall_total_ns: int,\n) -> _LaneSummary:\n',
        '        wall_total_ns: int,\n        workload: Optional[str] = None,\n) -> _LaneSummary:\n'
        '    """Summarize one named thread using its repeated workload family for object counts.\n\n'
        '    workload defaults to name for the original three lanes. Repeated lanes\n'
        '    supply their original family; their samples and output names stay separate.\n'
        '    """\n')
    source = replace_once(source,
        '    objects_min = len(metric_samples.outer_total_ns) * _lane_objects_per_cycle(name)\n',
        '    objects_min = len(metric_samples.outer_total_ns) * _lane_objects_per_cycle(\n'
        '        name if workload is None else workload)\n')
    source = replace_once(source,
        'def _run_gauntlet_benchmark(lib: str, cfg: _GauntletConfig) -> _BenchmarkResult:\n',
        '''def _run_gauntlet_benchmark(lib: str, cfg: _GauntletConfig) -> _BenchmarkResult:
    """Measure one library with GIL-off checks before setup, after imports and after the run.

    Build one container, reuse it across synchronized N-thread iterations, and
    retire it in finally. Each repeated workload has independent lane storage;
    throughput and object minima include every configured thread. Existing GC
    instrumentation and its restoration remain local to this library's run.
    """
    _require_gil_disabled()
    layout = _lane_layout(cfg)
    lane_workloads = {name: workload for name, workload, _, _ in layout}
''')
    source = replace_once(source,
        '    min_request_objects = cfg.request_scope_runs * _REQUEST_OBJECTS_PER_ROOT\n'
        '    min_worker_a_objects = cfg.worker_a_jobs * _WORKER_A_OBJECTS_PER_ROOT if cfg.threads >= 2 else 0\n'
        '    min_worker_b_objects = cfg.worker_b_jobs * _WORKER_B_OBJECTS_PER_ROOT if cfg.threads >= 3 else 0\n'
        '    bootstrap_objects = len(_BOOTSTRAP_TYPES) * _BOOTSTRAP_FANOUT_PER_SINGLETON\n'
        '    hot_objects_per_iter_min = bootstrap_objects + min_request_objects + min_worker_a_objects + min_worker_b_objects\n',
        '    min_request_objects = sum(reps * _REQUEST_OBJECTS_PER_ROOT\n'
        '                              for _, workload, reps, _ in layout if workload == "request")\n'
        '    bootstrap_objects = len(_BOOTSTRAP_TYPES) * _BOOTSTRAP_FANOUT_PER_SINGLETON\n'
        '    hot_objects_per_iter_min = bootstrap_objects + sum(\n'
        '        reps * _lane_objects_per_cycle(workload) for _, workload, reps, _ in layout)\n')
    source = replace_once(source, '    try:\n        ops.spawn_singletons()\n',
                          '    try:\n        _require_gil_disabled()\n        ops.spawn_singletons()\n')
    source = replace_once(source,
        '        lane_metric_samples = {\n'
        '            "request": _new_lane_metric_storage(),\n'
        '            "worker_a": _new_lane_metric_storage(),\n'
        '            "worker_b": _new_lane_metric_storage(),\n'
        '        }\n'
        '        lane_variant_counts = {\n'
        '            "request": [0] * _VARIANT_COUNT,\n'
        '            "worker_a": [0] * _VARIANT_COUNT,\n'
        '            "worker_b": [0] * _VARIANT_COUNT,\n'
        '        }\n',
        '        lane_metric_samples = {name: _new_lane_metric_storage() for name, _, _, _ in layout}\n'
        '        lane_variant_counts = {name: [0] * _VARIANT_COUNT for name, _, _, _ in layout}\n')
    source = replace_once(source,
        '                wall_total_ns=threaded_summary.total_ns,\n',
        '                wall_total_ns=threaded_summary.total_ns,\n'
        '                workload=lane_workloads[lane_name],\n')
    source = replace_once(source, '        result_payload = {\n',
                          '        _require_gil_disabled()\n        result_payload = {\n')
    source = replace_once(source,
        '    for lane_name in ("request", "worker_a", "worker_b"):\n'
        '        lane = result.lane_summaries.get(lane_name)\n'
        '        if lane is None:\n'
        '            continue\n',
        '    for lane in result.lane_summaries.values():\n')
    source = replace_once(source,
        '        "hot_scopes_per_s": result.hot_scope_cycles_per_s,\n',
        '        "hot_scopes_per_s": result.hot_scope_cycles_per_s,\n'
        '        "total_hot_scopes": result.total_hot_scopes,\n'
        '        "hot_objects_per_iter_min": result.hot_objects_per_iter_min,\n'
        '        "lane_cycles": {name: lane.cycles for name, lane in result.lane_summaries.items()},\n'
        '        "lane_variants": {name: list(lane.variant_counts) for name, lane in result.lane_summaries.items()},\n')
    source = replace_once(source,
        '          interpreter, adding `-X gil=0` when `REAL_WORLD_GAUNTLET_FORCE_NOGIL` is\n'
        '          true, from the repository root and with a copy of this environment.\n',
        '          interpreter with `-X gil=0`, from the repository root. A copied\n'
        '          child environment forces PYTHON_GIL=0 even when the parent has 1;\n'
        '          the parent environment itself is unchanged.\n')
    source = replace_once(source,
        '    command = [sys.executable]\n'
        '    if REAL_WORLD_GAUNTLET_FORCE_NOGIL:\n'
        '        command.extend(["-X", "gil=0"])\n',
        '    command = [sys.executable, "-X", "gil=0"]\n'
        '    child_env = os.environ.copy()\n'
        '    child_env["PYTHON_GIL"] = "0"\n')
    source = replace_once(source, '        env=os.environ.copy(),\n', '        env=child_env,\n')
    source = replace_once(source,
        '        - Forces `-X gil=0` when `REAL_WORLD_GAUNTLET_FORCE_NOGIL` is true.\n',
        '        - Forces `-X gil=0` and PYTHON_GIL=0 in every measured child process.\n'
        '        - DI_GAUNTLET_THREADS accepts positive N; request/A/B workloads repeat\n'
        '          under distinct request, worker_a, worker_b, worker_c, ... lane names.\n')
    source = replace_once(source,
        '# The measurement entry point also refuses a process whose GIL is enabled.\n',
        '# The measurement entry point also refuses a process whose GIL is enabled.\n\n'
        '# Benchmark configuration: edit this list to change the default thread-count relay.\n'
        'REAL_WORLD_GAUNTLET_THREAD_COUNTS: list[int] = [3, 5, 7, 9]\n')
    thread_counts = '''def _gauntlet_thread_counts() -> tuple[int, ...]:
    """Select the ordered thread-count relay without changing parent process state.

    Edit REAL_WORLD_GAUNTLET_THREAD_COUNTS for the normal run. An optional
    comma-separated environment variable of the same name overrides that list;
    otherwise DI_GAUNTLET_THREADS selects one count for existing single-run tools.
    Counts must be distinct positive integers. Each library/count/round receives
    a fresh process, and summaries never combine different thread counts.
    """
    series = os.getenv("REAL_WORLD_GAUNTLET_THREAD_COUNTS", "").strip()
    single = os.getenv("DI_GAUNTLET_THREADS", "").strip()
    counts = ([int(value.strip()) for value in series.split(",")] if series
              else [int(single)] if single else list(REAL_WORLD_GAUNTLET_THREAD_COUNTS))
    if not counts or any(type(value) is not int or value <= 0 for value in counts):
        raise ValueError("Gauntlet thread counts must be a nonempty list of positive integers")
    if len(counts) != len(set(counts)):
        raise ValueError("Gauntlet thread counts must be distinct; use rounds for repetition")
    return tuple(counts)


'''
    source = replace_once(source, 'def _lane_layout(cfg: _GauntletConfig)',
                          thread_counts + 'def _lane_layout(cfg: _GauntletConfig)')
    source = replace_once(source,
        '        result_path: Path,\n) -> subprocess.CompletedProcess[str]:\n',
        '        result_path: Path,\n        *, threads: Optional[int] = None,\n) -> subprocess.CompletedProcess[str]:\n')
    source = replace_once(source, '    child_env["PYTHON_GIL"] = "0"\n',
        '    child_env["PYTHON_GIL"] = "0"\n'
        '    if threads is not None:\n'
        '        child_env["DI_GAUNTLET_THREADS"] = str(threads)\n')
    source = replace_once(source,
        '        result_path: Where the child writes its JSON payload.\n',
        '        result_path: Where the child writes its JSON payload.\n'
        '        threads: This child\'s count; None preserves the inherited single-run setting.\n')
    source = replace_once(source,
        '        writer.writerow([*_per_turn_csv_header(), "Round"])\n',
        '        writer.writerow([*_per_turn_csv_header(), "Round", "Threads"])\n')
    source = replace_once(source,
        '                writer.writerow([*_per_turn_csv_row(payload["lib"], row), payload["round"]])\n',
        '                writer.writerow([*_per_turn_csv_row(payload["lib"], row), payload["round"], payload["threads"]])\n')
    source = source.replace('which adds a Round column.', 'which adds Round and Threads columns.')
    source = source.replace('which adds a Round column', 'which adds Round and Threads columns')
    source = replace_once(source,
        '          more than one round repeats every library.\n',
        '          more than one round repeats every library. A Threads column separates\n'
        '          rows from each configured thread count.\n')
    median_start = source.index('    lines: list[str] = []\n', source.index('def _isolated_median_lines('))
    median_end = source.index('\n\ndef _run_isolated_library(', median_start)
    source = source[:median_start] + '''    lines: list[str] = []
    thread_counts = dict.fromkeys(payload["threads"] for payload in payloads)
    for threads in thread_counts:
        for lib in _gauntlet_libraries():
            runs = [payload for payload in payloads
                    if payload["lib"] == lib and payload["threads"] == threads]
            if not runs:
                continue
            totals = [run["total_ms"] for run in runs]
            noun = "round" if len(runs) == 1 else "rounds"
            lines.append(
                f"[{lib}] isolated median over {len(runs)} {noun} | threads={threads} | "
                f"total={statistics.median(totals):.2f}ms (min={min(totals):.2f}, max={max(totals):.2f}) | "
                f"avg={statistics.median([run['avg_ms'] for run in runs]):.3f}ms | "
                f"p99={statistics.median([run['p99_ms'] for run in runs]):.3f}ms | "
                f"threaded avg={statistics.median([run['threaded_avg_ms'] for run in runs]):.3f}ms | "
                f"hot_scopes/s={statistics.median([run['hot_scopes_per_s'] for run in runs]):,.0f} | "
                f"setup={statistics.median([run['setup_ms'] for run in runs]):.3f}ms"
            )
    return lines
''' + source[median_end:]
    source = replace_once(source,
        '        - One line per library that has payloads, in `_gauntlet_libraries()` order;\n'
        '          a library with none is skipped.\n',
        '        - One line per library/thread-count pair, in first-seen count order and\n'
        '          `_gauntlet_libraries()` order; a pair with no payloads is skipped.\n')
    wrapper_start = source.index('    rounds = _gauntlet_rounds()\n', source.index('def test_real_world_gauntlet()'))
    source = source[:wrapper_start] + '''    rounds = _gauntlet_rounds()
    thread_counts = _gauntlet_thread_counts()
    payloads: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="real_world_gauntlet_") as scratch:
        for threads in thread_counts:
            for round_ix in range(rounds):
                round_number = round_ix + 1
                for lib in _isolated_order(round_ix):
                    result_path = Path(scratch) / f"threads{threads}_round{round_number}_{lib}.json"
                    print(f"[gauntlet] threads={threads}, round {round_number}/{rounds}: {lib} in its own process")
                    completed = _run_isolated_library(lib, round_number, result_path, threads=threads)
                    if completed.stdout:
                        print(completed.stdout, end="" if completed.stdout.endswith("\\n") else "\\n")
                    if completed.stderr:
                        print(completed.stderr, end="" if completed.stderr.endswith("\\n") else "\\n")
                    if completed.returncode != 0:
                        raise AssertionError(
                            f"Shared real-world gauntlet runner failed for {lib}, threads={threads}, "
                            f"round {round_number}, exit code {completed.returncode}."
                        )
                    payload = json.loads(result_path.read_text(encoding="utf-8"))
                    if (payload["lib"], payload["threads"], payload["round"], payload["gil_status"]) != (
                            lib, threads, round_number, "disabled"):
                        raise AssertionError("Gauntlet child returned mismatched library/thread/round/GIL identity")
                    payloads.append(payload)
    if rounds > 1 or len(thread_counts) > 1:
        for line in _isolated_median_lines(payloads):
            print(line)
    _write_isolated_per_turn_csv(payloads)
'''
    source = replace_once(source,
        '        - DI_GAUNTLET_THREADS accepts positive N; request/A/B workloads repeat\n',
        '        - The editable REAL_WORLD_GAUNTLET_THREAD_COUNTS list defaults to 3,5,7,9.\n'
        '          Each count runs every library/round in a separate fresh process.\n'
        '        - DI_GAUNTLET_THREADS accepts positive N; request/A/B workloads repeat\n')
    isolation_rel = "benchmarks/testing_other_di/test_real_world_gauntlet_isolation.py"
    isolation = (repo / isolation_rel).read_text(encoding="utf-8")
    isolation = replace_once(isolation,
        '    assert (command[1:3] == ["-X", "gil=0"]) == _shared.REAL_WORLD_GAUNTLET_FORCE_NOGIL\n',
        '    assert command[1:3] == ["-X", "gil=0"]\n'
        '    assert seen["kwargs"]["env"]["PYTHON_GIL"] == "0"\n')
    isolation = replace_once(isolation,
        '        Uses this interpreter, adds `-X gil=0` exactly when the module forces it,\n',
        '        Uses this interpreter, always adds `-X gil=0` and child PYTHON_GIL=0,\n')
    isolation = replace_once(isolation,
        '    assert rows[0] == [*_shared._per_turn_csv_header(), "Round"]\n',
        '    assert rows[0] == [*_shared._per_turn_csv_header(), "Round", "Threads"]\n')
    isolation = replace_once(isolation,
        '    assert rows[1] == ["dishka", "0", "1.0000", "0.0100", "0.9000", "no", "5", "1"]\n',
        '    assert rows[1] == ["dishka", "0", "1.0000", "0.0100", "0.9000", "no", "5", "1", "3"]\n')
    isolation = replace_once(isolation,
        '    assert rows[2] == ["melder", "0", "2.0000", "0.0200", "1.8000", "yes", "7", "2"]\n',
        '    assert rows[2] == ["melder", "0", "2.0000", "0.0200", "1.8000", "yes", "7", "2", "3"]\n')
    isolation = replace_once(isolation,
        '    assert rows[3][0] == "melder" and rows[3][-1] == "2"\n',
        '    assert rows[3][0] == "melder" and rows[3][-2:] == ["2", "3"]\n')
    runner_rel = "benchmarks/testing_other_di/real_world_gauntlet_gil_runner.py"
    runner = (repo / runner_rel).read_text(encoding="utf-8")
    runner = replace_once(runner, 'Environment:\n',
        'Runtime:\n'
        '    Use free-threaded Python with -X gil=0 or PYTHON_GIL=0 before startup.\n'
        '    The shared measurement entry point refuses an enabled GIL. Its pytest\n'
        '    wrapper sets both for each isolated child process automatically.\n\n'
        'Environment:\n')
    runner = replace_once(runner,
        '    GAUNTLET_* instruments in either mode.\n',
        '    GAUNTLET_* instruments in either mode. DI_GAUNTLET_THREADS accepts positive N;\n'
        '    workload families repeat request/A/B while lane names continue C, D, E, etc.\n')
    edits = {relative: source, isolation_rel: isolation, runner_rel: runner}
    pins = {}
    for path, text in edits.items():
        original = (repo / path).read_bytes()
        backup = artifact / "baseline" / path
        backup.parent.mkdir(parents=True, exist_ok=True)
        if backup.exists():
            raise RuntimeError(f"Existing baseline: {backup}")
        backup.write_bytes(original)
        pins[path] = hashlib.sha256(original).hexdigest()
    for path, text in edits.items():
        if hashlib.sha256((repo / path).read_bytes()).hexdigest() != pins[path]:
            raise RuntimeError(f"Concurrent edit: {path}")
        (repo / path).write_text(text, encoding="utf-8", newline="\n")
    (artifact / "benchmark_edit.py").write_bytes(Path(__file__).read_bytes())
    (artifact / "benchmark_pre_pins.json").write_text(json.dumps(pins, indent=2), encoding="utf-8")
    task = repo / "context_compass/tickets/tasks/2026-10-03_real_world_gauntlet_ci_task.md"
    with task.open("a", encoding="utf-8") as handle:
        handle.write("\n## Workload decision and implementation\n"
                     "Owner selected repetition of the full request/A/B workload cycle, with C, D, E, F, G\n"
                     "and onward as distinct additional thread lanes. No producer/consumer queue is added.\n"
                     "Every lane owns its metrics and counter slots; the existing readiness/start/join pattern\n"
                     "is preserved. The launcher now forces child PYTHON_GIL=0 and -X gil=0; the measured\n"
                     "entry point checks GIL state before setup, after imports and after measurement.\n"
                     "The owner additionally requests an editable [3,5,7,9] thread-count list in the\n"
                     "benchmark configuration section. The wrapper executes each library/count/round in\n"
                     "its own child and separates summaries and per-turn CSV by thread count.\n"
                     "Next: add focused N-thread/GIL contracts, then wire the workflow and validate.\n")
    print("Applied benchmark, runner documentation and existing launch-contract adjustment.")


if __name__ == "__main__":
    main()
