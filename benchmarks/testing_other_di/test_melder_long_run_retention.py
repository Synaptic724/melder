"""
Long-run retention and attribution diagnostics for the shared gauntlet's Melder lane.

Purpose:
    The owner's shared gauntlet showed Melder holding throughput from 5k to 50k
    iterations and dropping ~12.5% at 100k, which raised the question of a
    memory leak. These tests pin down the answer in a form that can be rerun on
    any machine:

    - The two retention tests prove that Melder's lesser-conduit + SpellSpace
      scope cycle returns the process to the same object and allocator state,
      both when every iteration starts three NEW threads (the gauntlet's shape)
      and when the same cycles run on three persistent threads. A leak of one
      object per cycle, per iteration, or per thread fails them by orders of
      magnitude.
    - The attribution test (opt-in, it is slow) runs one lane three times:
      discarding samples, storing them as the harness now does (values in
      `array("q")`), and storing them as the harness used to (the worker
      threads' int objects in lists). It prints per-window throughput, CPU per
      cycle and GC activity for each, to answer "is a long-run drop the
      library, or the measuring harness?" on the owner's own hardware. In the
      2026-09-26 sandbox runs (CPython 3.14.0rc2 free-threaded) only the former
      storage slowed down - Melder and dishka alike, with zero automatic
      collections - which is why the harness was changed.

Method:
    The workload is the exact one the shared gauntlet runs: the runtime is built
    by `test_real_world_gauntlet._build_ops("melder")` (the shared gauntlet's own
    Melder lane, kept identical to the Melder-only gauntlet by
    `test_gauntlet_melder_lane_parity.py`), and one iteration is
    `test_real_world_gauntlet._run_gauntlet_once(...)`: 65 scope cycles spread
    over three lanes (10 request, 25 worker A, 30 worker B).

    Retention is measured in two windows after a warm-up, each preceded by
    `gc.collect()`: the count of GC-tracked objects (`gc.get_objects()`) and the
    interpreter's allocated block count (`sys.getallocatedblocks()`). Only the
    growth BETWEEN the two post-warm-up snapshots is asserted, so first-use
    caches (pools filling, lazy doors, slot guards) never count as a leak.

Usage (from the repository root):
    python -X gil=0 -m pytest benchmarks/testing_other_di/test_melder_long_run_retention.py -q -s

    Attribution run, PowerShell:
        $env:MELDER_LONG_RUN_ATTRIBUTION = "1"
        $env:MELDER_LONG_RUN_ATTRIBUTION_ITERS = "50000"      # per mode; three modes run
        $env:MELDER_LONG_RUN_ATTRIBUTION_LIB = "melder"       # or dishka / dependency-injector
        python -X gil=0 -m pytest benchmarks/testing_other_di/test_melder_long_run_retention.py -q -s -k attribution

    Attribution run, POSIX shell:
        MELDER_LONG_RUN_ATTRIBUTION=1 MELDER_LONG_RUN_ATTRIBUTION_ITERS=50000 \\
            python -X gil=0 -m pytest benchmarks/testing_other_di/test_melder_long_run_retention.py \\
            -q -s -k attribution

Validation:
    Intended for free-threaded CPython 3.14 (`-X gil=0`); it also runs with the
    GIL. Assertions are on object and block counts, never on wall-clock time.

This is a benchmark diagnostic surface, not production runtime code.
"""

import gc
import os
import random
import sys
import threading
import time
from pathlib import Path
from array import array
from typing import Any, Callable, Dict, List, MutableSequence, Optional, Tuple

import pytest


def _ensure_local_paths() -> None:
    """
    Ensure the repository root, `src/` and this benchmark directory are importable.

    Contract:
        Mirrors the path setup of `real_world_gauntlet_gil_runner.py` (repository
        root, so `benchmarks.testing_other_di...` resolves) and of
        `test_melder_gauntlet.py` (`src/` and this directory), adding each path
        once. Supports pytest and direct `python` execution.
    """
    current_dir = Path(__file__).resolve().parent
    repo_root = current_dir.parents[1]
    for path in (repo_root, repo_root / "src", current_dir):
        path_as_str = str(path)
        if path_as_str not in sys.path:
            sys.path.insert(0, path_as_str)


_ensure_local_paths()

import test_real_world_gauntlet as _gauntlet


class _RetentionBudget:
    """
    Iteration counts and growth ceilings for the retention tests.

    Purpose:
        Keep every tunable in one place (this profile keeps constants on classes,
        not at module scope) and document why each ceiling is safe.

    Contract:
        - `WARMUP_ITERATIONS` fills the lesser-conduit and SpellSpace pools and
          every lazily built door before any snapshot is taken.
        - `WINDOW_ITERATIONS` is the length of each measured window. One window
          is 65 x WINDOW_ITERATIONS scope cycles and 3 x WINDOW_ITERATIONS fresh
          threads in the churn test.
        - The ceilings bound growth between the two post-warm-up snapshots. The
          sandbox measurement that set them (CPython 3.14.0rc2 free-threaded,
          2,000-iteration windows) saw -316..0 objects and -1..+12 blocks per
          window. A leak of one object per iteration alone would add
          WINDOW_ITERATIONS objects and fail; one per cycle would add 65x that.
    """

    WARMUP_ITERATIONS: int = 300
    WINDOW_ITERATIONS: int = 1_000
    MAX_OBJECT_GROWTH: int = 150
    MAX_BLOCK_GROWTH: int = 400


class _Snapshot:
    """
    One post-`gc.collect()` reading of process-level object and block counts.

    Purpose:
        Carry the two retention measures the tests compare, taken the same way
        every time.

    Contract:
        - `take()` runs a full `gc.collect()` first so only reachable objects
          are counted.
        - `objects` counts GC-tracked objects; `blocks` is
          `sys.getallocatedblocks()`, which also covers untracked allocations
          such as ints, strings and list storage.
    """

    __slots__ = ("objects", "blocks")

    def __init__(self, objects: int, blocks: int) -> None:
        """
        Store one reading.

        Args:
            objects: Number of GC-tracked objects after a full collection.
            blocks: `sys.getallocatedblocks()` after the same collection.
        """
        self.objects: int = objects
        self.blocks: int = blocks

    @classmethod
    def take(cls) -> _Snapshot:
        """
        Collect garbage, then read the object and block counts.

        Returns:
            _Snapshot: The current reading.
        """
        gc.collect()
        return cls(objects=len(gc.get_objects()), blocks=sys.getallocatedblocks())


class _PersistentLaneRunner:
    """
    Run the gauntlet's three Melder lanes on three long-lived threads.

    Purpose:
        Provide the no-churn control for the retention tests: the same 65 scope
        cycles per iteration as `_run_gauntlet_once`, but every iteration reuses
        the same three threads, so per-thread state is created once.

    Contract:
        - `run_iteration(ix)` runs one bootstrap fan-out on the calling thread,
          then releases the three workers, which each run their lane's cycle
          count with the harness's seed formula, and returns when all three are
          done.
        - A worker failure is re-raised on the calling thread from the next
          `run_iteration` or from `close()`.
        - `close()` stops and joins the workers; it is idempotent.

    Threading:
        Two `threading.Barrier(4)` objects gate each iteration (start, end). The
        iteration index is written before the start barrier and read after it.

    Lifecycle / Cleanup:
        The runner owns its three threads and barriers. Call `close()` in a
        `finally`. The Melder runtime itself is owned by the caller.
    """

    def __init__(self, ops: Any) -> None:
        """
        Start three persistent lane workers against one Melder runtime.

        Args:
            ops: The `_RuntimeOps` returned by `_gauntlet._build_ops("melder")`.
                Borrowed; the caller cleans it.
        """
        self._ops: Any = ops
        self._start: threading.Barrier = threading.Barrier(4)
        self._end: threading.Barrier = threading.Barrier(4)
        self._iteration_ix: int = 0
        self._stopping: bool = False
        self._closed: bool = False
        self._errors: List[BaseException] = []
        lanes: Tuple[Tuple[Callable[[int], Any], int, int], ...] = (
            (ops.request_scope_cycle, _gauntlet._REQUEST_SCOPE_RUNS_DEFAULT, 17),
            (ops.worker_a_scope_cycle, _gauntlet._WORKER_A_JOBS_DEFAULT, 29),
            (ops.worker_b_scope_cycle, _gauntlet._WORKER_B_JOBS_DEFAULT, 41),
        )
        self._threads: List[threading.Thread] = [
            threading.Thread(target=self._worker, args=lane, daemon=True) for lane in lanes
        ]
        for thread in self._threads:
            thread.start()

    def _worker(self, call: Callable[[int], Any], reps: int, seed_offset: int) -> None:
        """
        Run one lane's cycles once per released iteration until stopped.

        Args:
            call: The lane's scope-cycle callable (takes a variant index).
            reps: Cycles per iteration for this lane.
            seed_offset: The lane's seed offset in the harness seed formula.
        """
        while True:
            self._start.wait()
            if self._stopping:
                return
            try:
                rng = random.Random(
                    _gauntlet._LIB_SEEDS["melder"] + self._iteration_ix * 101 + seed_offset
                )
                for _ in range(reps):
                    call(rng.randrange(_gauntlet._VARIANT_COUNT))
            except BaseException as exc:
                self._errors.append(exc)
            self._end.wait()

    def run_iteration(self, iteration_ix: int) -> None:
        """
        Run one gauntlet iteration on the persistent workers.

        Args:
            iteration_ix: Iteration index used in the lane seed formula.

        Raises:
            BaseException: The first error raised by any worker.
        """
        self._ops.bootstrap_fanout()
        self._iteration_ix = iteration_ix
        self._start.wait()
        self._end.wait()
        if self._errors:
            raise self._errors[0]

    def close(self) -> None:
        """
        Stop and join the three workers. Idempotent.

        Raises:
            BaseException: The first worker error, if one was recorded.
        """
        if self._closed:
            return
        self._closed = True
        self._stopping = True
        self._start.wait()
        for thread in self._threads:
            thread.join()
        if self._errors:
            raise self._errors[0]


def _build_melder_ops() -> Any:
    """
    Build the Melder runtime exactly as the shared gauntlet does, singletons spawned.

    Returns:
        Any: The `_RuntimeOps` for the Melder lane. The caller must call
        `.cleanup()`.
    """
    ops = _gauntlet._build_ops("melder")
    ops.spawn_singletons()
    return ops


def _gauntlet_config(iterations: int) -> Any:
    """
    Return the shared gauntlet's default three-thread configuration.

    Args:
        iterations: Iteration count to record in the config.

    Returns:
        Any: A `_GauntletConfig` with the harness's default lane sizes.
    """
    return _gauntlet._GauntletConfig(
        iterations=iterations,
        threads=3,
        request_scope_runs=_gauntlet._REQUEST_SCOPE_RUNS_DEFAULT,
        worker_a_jobs=_gauntlet._WORKER_A_JOBS_DEFAULT,
        worker_b_jobs=_gauntlet._WORKER_B_JOBS_DEFAULT,
    )


def _measure_window_growth(run_iteration: Callable[[int], None]) -> Tuple[_Snapshot, _Snapshot, _Snapshot]:
    """
    Warm up, then take snapshots before and after two equal measured windows.

    Args:
        run_iteration: Runs one gauntlet iteration for a given index.

    Returns:
        Tuple[_Snapshot, _Snapshot, _Snapshot]: Readings after warm-up, after
        window one and after window two.
    """
    budget = _RetentionBudget
    ix = 0
    for _ in range(budget.WARMUP_ITERATIONS):
        run_iteration(ix)
        ix += 1
    after_warmup = _Snapshot.take()
    for _ in range(budget.WINDOW_ITERATIONS):
        run_iteration(ix)
        ix += 1
    after_first = _Snapshot.take()
    for _ in range(budget.WINDOW_ITERATIONS):
        run_iteration(ix)
        ix += 1
    after_second = _Snapshot.take()
    return after_warmup, after_first, after_second


def _assert_no_window_growth(label: str, readings: Tuple[_Snapshot, _Snapshot, _Snapshot]) -> None:
    """
    Print the three readings and assert the second window added nothing material.

    Args:
        label: Scenario name for the printed report.
        readings: Snapshots after warm-up, window one and window two.

    Raises:
        AssertionError: Object or block growth across window two exceeded the
            `_RetentionBudget` ceilings.
    """
    after_warmup, after_first, after_second = readings
    object_growth = after_second.objects - after_first.objects
    block_growth = after_second.blocks - after_first.blocks
    cycles = 65 * _RetentionBudget.WINDOW_ITERATIONS
    print(
        f"[{label}] objects {after_warmup.objects} -> {after_first.objects} -> {after_second.objects} "
        f"| blocks {after_warmup.blocks} -> {after_first.blocks} -> {after_second.blocks} "
        f"| window-2 growth: objects {object_growth:+d}, blocks {block_growth:+d} over {cycles} cycles"
    )
    assert object_growth <= _RetentionBudget.MAX_OBJECT_GROWTH, (
        f"{label}: {object_growth} GC-tracked objects survived {cycles} Melder scope cycles "
        f"(ceiling {_RetentionBudget.MAX_OBJECT_GROWTH}). Something on the lesser-conduit/"
        "SpellSpace cycle retains state; diff gc.get_objects() by type between windows to find it."
    )
    assert block_growth <= _RetentionBudget.MAX_BLOCK_GROWTH, (
        f"{label}: allocated blocks grew by {block_growth} over {cycles} Melder scope cycles "
        f"(ceiling {_RetentionBudget.MAX_BLOCK_GROWTH}). Untracked memory (strings, ints, list or "
        "dict storage) is accumulating; compare tracemalloc snapshots between windows."
    )


def test_melder_scope_cycles_retain_nothing_under_fresh_thread_churn() -> None:
    """
    Melder's scope cycle leaves no residue when every iteration starts three new threads.

    Contract:
        Runs the shared gauntlet's own `_run_gauntlet_once` (three fresh threads
        per iteration, 65 lesser-conduit + SpellSpace cycles) and asserts that
        the second measured window adds no GC-tracked objects or allocated
        blocks beyond `_RetentionBudget`. Covers per-thread state
        (`SpellSpaceThreadState`'s `threading.local`), pool return, ward
        detach and store reset together.
    """
    ops = _build_melder_ops()
    cfg = _gauntlet_config(_RetentionBudget.WARMUP_ITERATIONS + 2 * _RetentionBudget.WINDOW_ITERATIONS)
    try:
        readings = _measure_window_growth(lambda ix: _gauntlet._run_gauntlet_once(ops, cfg, ix))
    finally:
        ops.cleanup()
    _assert_no_window_growth("fresh-thread churn", readings)


def test_melder_scope_cycles_retain_nothing_on_persistent_threads() -> None:
    """
    Melder's scope cycle leaves no residue on three long-lived threads.

    Contract:
        Same workload and ceilings as the churn test, but the three lanes run on
        persistent threads, so any growth here is per cycle, not per thread.
    """
    ops = _build_melder_ops()
    runner = _PersistentLaneRunner(ops)
    try:
        readings = _measure_window_growth(runner.run_iteration)
    finally:
        try:
            runner.close()
        finally:
            ops.cleanup()
    _assert_no_window_growth("persistent threads", readings)


class _AttributionSettings:
    """
    Environment switches for the opt-in long-run attribution benchmark.

    Purpose:
        Keep the attribution run out of ordinary test sessions (it runs for
        minutes) and let the owner size it on his machine.

    Contract:
        - `enabled()` is True only when `MELDER_LONG_RUN_ATTRIBUTION` is truthy.
        - `iterations()` reads `MELDER_LONG_RUN_ATTRIBUTION_ITERS` (default 20,000).
        - `windows()` reads `MELDER_LONG_RUN_ATTRIBUTION_WINDOWS` (default 10).
        - `lib()` reads `MELDER_LONG_RUN_ATTRIBUTION_LIB` (default "melder"); any
          name `_gauntlet._build_ops` accepts is valid, so the same control can
          be run for dependency-injector or dishka.
    """

    ENABLE_ENV: str = "MELDER_LONG_RUN_ATTRIBUTION"
    ITERS_ENV: str = "MELDER_LONG_RUN_ATTRIBUTION_ITERS"
    WINDOWS_ENV: str = "MELDER_LONG_RUN_ATTRIBUTION_WINDOWS"
    LIB_ENV: str = "MELDER_LONG_RUN_ATTRIBUTION_LIB"
    DEFAULT_ITERATIONS: int = 20_000
    DEFAULT_WINDOWS: int = 10

    @classmethod
    def enabled(cls) -> bool:
        """
        Returns:
            bool: True when the attribution benchmark was requested.
        """
        return os.getenv(cls.ENABLE_ENV, "").strip().lower() in {"1", "true", "yes", "on"}

    @classmethod
    def iterations(cls) -> int:
        """
        Returns:
            int: Iterations per mode (discard, harness and worker_objects each run this many).
        """
        return _gauntlet._env_int(cls.ITERS_ENV, cls.DEFAULT_ITERATIONS)

    @classmethod
    def windows(cls) -> int:
        """
        Returns:
            int: Number of equal reporting windows per mode.
        """
        return _gauntlet._env_int(cls.WINDOWS_ENV, cls.DEFAULT_WINDOWS)

    @classmethod
    def lib(cls) -> str:
        """
        Returns:
            str: Library lane to run through the shared harness.
        """
        return os.getenv(cls.LIB_ENV, "melder").strip() or "melder"


class _GcPauseWindow:
    """
    gc.callbacks recorder that reports collections and pauses per window.

    Purpose:
        Attribute per-window slowdowns to automatic collections: how many ran
        and how long the stop-the-world pauses were.

    Contract:
        - `install()` / `uninstall()` add and remove one gc.callbacks hook.
        - `take()` returns (collections, pause_total_ns, pause_max_ns) since the
          previous `take()` and resets the counters.

    Threading:
        Under the free-threaded build the callback runs on the thread that
        triggered the collection; start stamps are kept per thread and totals
        are merged under `_lock`.
    """

    def __init__(self) -> None:
        """Initialize empty counters and the merge lock."""
        self._lock: threading.Lock = threading.Lock()
        self._start_by_thread: Dict[int, int] = {}
        self._collections: int = 0
        self._pause_total_ns: int = 0
        self._pause_max_ns: int = 0

    def _callback(self, phase: str, info: Dict[str, Any]) -> None:
        """
        Time one collection.

        Args:
            phase: "start" or "stop", as supplied by the collector.
            info: Collector-supplied mapping (unused).
        """
        thread_id = threading.get_ident()
        if phase == "start":
            self._start_by_thread[thread_id] = time.perf_counter_ns()
            return
        start_ns: Optional[int] = self._start_by_thread.pop(thread_id, None)
        if start_ns is None:
            return
        pause_ns = time.perf_counter_ns() - start_ns
        with self._lock:
            self._collections += 1
            self._pause_total_ns += pause_ns
            self._pause_max_ns = max(self._pause_max_ns, pause_ns)

    def install(self) -> None:
        """Append the recording hook to gc.callbacks."""
        gc.callbacks.append(self._callback)

    def uninstall(self) -> None:
        """Remove the recording hook; a no-op when already absent."""
        if self._callback in gc.callbacks:
            gc.callbacks.remove(self._callback)

    def take(self) -> Tuple[int, int, int]:
        """
        Return and reset this window's counters.

        Returns:
            Tuple[int, int, int]: (collections, pause_total_ns, pause_max_ns).
        """
        with self._lock:
            result = (self._collections, self._pause_total_ns, self._pause_max_ns)
            self._collections = 0
            self._pause_total_ns = 0
            self._pause_max_ns = 0
        return result


class _RetentionMode:
    """
    Names of the three sample-handling modes the attribution benchmark compares.

    Purpose:
        Show on any machine that the gauntlet harness is fair after the
        2026-09-26 storage fix, and reproduce the defect it removed.

    Contract:
        - `DISCARD`: each iteration's samples are dropped; nothing accumulates.
          The no-harness baseline.
        - `HARNESS`: exactly what `_run_gauntlet_benchmark` does now - values are
          copied from each iteration's lists into run-long `array("q")` storage,
          so no int object created on a worker thread outlives its iteration.
        - `WORKER_OBJECTS`: what the harness did before the fix - the int objects
          the worker threads created are kept in run-long lists for the whole
          leg, outliving the threads that allocated them. On free-threaded
          CPython 3.14 this mode slows down window after window.
    """

    DISCARD: str = "discard"
    HARNESS: str = "harness"
    WORKER_OBJECTS: str = "worker_objects"
    ALL: Tuple[str, str, str] = ("discard", "harness", "worker_objects")


def _new_lane_keepers(mode: str) -> Dict[str, List[MutableSequence[int]]]:
    """
    Return empty run-long per-lane storage for one attribution mode.

    Args:
        mode: One of `_RetentionMode.ALL`.

    Returns:
        Dict[str, List[MutableSequence[int]]]: Per lane, six sequences in harness
        metric order: `array("q")` for `HARNESS` (the fixed harness storage),
        plain lists otherwise (which keep the worker-created int objects).
    """
    lanes = ("request", "worker_a", "worker_b")
    if mode == _RetentionMode.HARNESS:
        return {name: [array("q") for _ in range(6)] for name in lanes}
    return {name: [[] for _ in range(6)] for name in lanes}


def _keep_iteration_samples(
        result: Any,
        mode: str,
        kept_iteration: List[List[int]],
        kept_lanes: Dict[str, List[MutableSequence[int]]],
) -> None:
    """
    Store one iteration's samples according to the retention mode.

    Contract:
        Iteration-level times are measured on the main thread and are kept as
        the harness keeps them. Lane samples are extended into `kept_lanes`,
        whose storage type (see `_new_lane_keepers`) decides whether values or
        worker-created objects are retained.

    Args:
        result: The `_IterationResult` returned by `_gauntlet._run_gauntlet_once`.
        mode: One of `_RetentionMode.ALL`.
        kept_iteration: Run-long lists for total, bootstrap and threaded times.
        kept_lanes: Run-long storage per lane, six metrics each, in harness order.
    """
    if mode == _RetentionMode.DISCARD:
        return
    kept_iteration[0].append(result.total_ns)
    kept_iteration[1].append(result.bootstrap_ns)
    kept_iteration[2].append(result.threaded_ns)
    for name, values in result.lane_metrics.items():
        sources = (
            values.outer_create_ns,
            values.outer_cleanup_ns,
            values.outer_total_ns,
            values.request_create_ns,
            values.request_cleanup_ns,
            values.request_total_ns,
        )
        for kept, source in zip(kept_lanes[name], sources):
            kept.extend(source)


def _run_attribution_mode(lib: str, mode: str, iterations: int, windows: int) -> List[str]:
    """
    Run one library lane through the shared harness and report per-window cost.

    Contract:
        - Uses `_gauntlet._run_gauntlet_once` for every iteration (three fresh
          worker threads, 65 scope cycles), exactly as `_run_gauntlet_benchmark`
          does, with a fresh runtime from `_gauntlet._build_ops(lib)`.
        - Samples are handled per `_RetentionMode` (see `_new_lane_keepers` and
          `_keep_iteration_samples`).
        - Each window reports wall scope cycles/s, the median threaded-phase
          time, process CPU microseconds per cycle, GC collections and pauses,
          and the number of retained entries at the window's end.

    Args:
        lib: Library lane name accepted by `_gauntlet._build_ops`.
        mode: One of `_RetentionMode.ALL`.
        iterations: Iterations to run.
        windows: Number of reporting windows.

    Returns:
        List[str]: One formatted line per window.
    """
    cfg = _gauntlet_config(iterations)
    window_size = max(1, iterations // windows)
    cycles = window_size * (cfg.request_scope_runs + cfg.worker_a_jobs + cfg.worker_b_jobs)
    ops = _gauntlet._build_ops(lib)
    probe = _GcPauseWindow()
    kept_iteration: List[List[int]] = [[], [], []]
    kept_lanes = _new_lane_keepers(mode)
    lines: List[str] = []
    try:
        ops.spawn_singletons()
        probe.install()
        wall_t0 = time.perf_counter()
        cpu_t0 = time.process_time()
        threaded: List[int] = []
        for ix in range(iterations):
            result = _gauntlet._run_gauntlet_once(ops, cfg, ix)
            threaded.append(result.threaded_ns)
            _keep_iteration_samples(result, mode, kept_iteration, kept_lanes)
            if (ix + 1) % window_size != 0:
                continue
            wall_s = time.perf_counter() - wall_t0
            cpu_s = time.process_time() - cpu_t0
            collections, pause_total_ns, pause_max_ns = probe.take()
            retained = sum(len(values) for values in kept_iteration) + sum(
                len(values) for lane in kept_lanes.values() for values in lane
            )
            threaded.sort()
            lines.append(
                f"[{lib} {mode:<7}] iters<={ix + 1:7d} | "
                f"cycles/s={cycles / wall_s:9,.0f} | thr_med={threaded[len(threaded) // 2] / 1e6:6.3f}ms | "
                f"cpu={cpu_s / cycles * 1e6:6.1f}us/cycle | gc={collections:4d} "
                f"pause_tot={pause_total_ns / 1e6:8.1f}ms max={pause_max_ns / 1e6:7.2f}ms | "
                f"retained={retained:,}"
            )
            print(lines[-1], flush=True)
            threaded = []
            wall_t0 = time.perf_counter()
            cpu_t0 = time.process_time()
    finally:
        probe.uninstall()
        kept_iteration.clear()
        kept_lanes.clear()
        ops.cleanup()
    return lines


@pytest.mark.skipif(
    not _AttributionSettings.enabled(),
    reason="Opt-in long-run benchmark: set MELDER_LONG_RUN_ATTRIBUTION=1 (minutes per run).",
)
def test_long_run_attribution_harness_retention_modes() -> None:
    """
    Show whether a long-run slowdown follows the harness's sample retention.

    Contract:
        Runs the chosen lane three times in one process - discard, harness
        (the fixed run-long `array("q")` storage) and worker_objects (the former
        list storage) - each with a fresh runtime, and prints a per-window table
        for each.

        How to read it: DISCARD and HARNESS should both stay flat across windows;
        if they do, the harness no longer penalizes long runs on this machine.
        WORKER_OBJECTS shows the defect the fix removed. If DISCARD itself slows
        down, the library (or the machine) is responsible. `gc=` shows whether
        automatic collections ran at all.

        The only assertion is that every window was reported; the printed table
        is the deliverable. Timing is machine-specific and is never asserted.
    """
    lib = _AttributionSettings.lib()
    iterations = _AttributionSettings.iterations()
    windows = _AttributionSettings.windows()
    print(
        f"[attribution] lib={lib} iterations={iterations} windows={windows} "
        f"python={sys.version.split()[0]} gil_enabled={sys._is_gil_enabled()}"
    )
    reported: Dict[str, List[str]] = {}
    for mode in _RetentionMode.ALL:
        reported[mode] = _run_attribution_mode(lib, mode, iterations, windows)
        gc.collect()
    assert all(len(lines) == windows for lines in reported.values())
