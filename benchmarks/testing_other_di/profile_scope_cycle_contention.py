"""
Scope-cycle contention profiler: price the threads>=3 lesser-conduit gap.

Purpose:
    Measure, under real thread contention, where pooled lesser-conduit scope
    cycles spend their time:
      - wait time on the ROOT conduit RLock (held for the whole
        `create_lesser_conduit` body, including ward linking)
      - total create wall vs total cleanup wall per cycle
      - >1ms stall events with surface attribution
    so the threads=3 hot-loop deficit (melder 22.0k vs DI 36.7k hot
    scopes/s, 11-22ms max stalls) can be attacked in evidence order.

Method:
    - Reuses the real-world gauntlet class graph (29 binds, same existences).
    - Probes root-lock wait with a sample-then-release acquire before each
      create call (the lock is not held across the call: since the
      lock-narrowing fix the create body only takes the parent lock for a
      short link window, and holding across would re-serialize it).
    - Times `Conduit.cleanup` (the pooled-release path) per call.
    - Sweeps thread counts; each thread runs scope cycles for a fixed
      duration. Optional melds mode adds outer-scoped melds + one request
      spellspace with request melds per cycle (gauntlet-lite shape).

Usage:
    .venv_new\\Scripts\\python.exe benchmarks\\testing_other_di\\profile_scope_cycle_contention.py

Env knobs:
    BENCH_CONTENTION_THREADS   comma list (default "1,3,5")
    BENCH_CONTENTION_SECONDS   seconds per sweep (default 5.0)
    BENCH_CONTENTION_MELDS     "1" adds gauntlet-lite melds per cycle (default 1)
    BENCH_CONTENTION_STALL_MS  stall threshold in ms (default 1.0)
    BENCH_CONTENTION_MICRO     "1" runs repeat-meld micro loops instead of
                               cycle sweeps: pure fast-door per-op ns for
                               outer and request melds at each thread count
    BENCH_CONTENTION_MICRO_ITERS  micro loop iterations (default 200000)
"""

import os
import statistics
import sys
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


def _ensure_local_paths() -> None:
    """
    Ensure local source and benchmark helper paths are importable.
    """
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parents[1]
    src_dir = project_root / "src"
    for path in (src_dir, current_dir):
        path_as_str = str(path)
        if path_as_str not in sys.path:
            sys.path.insert(0, path_as_str)


_ensure_local_paths()

import melder_gauntlet_support as _support  # noqa: E402

FRAME_NAME = "bench-scope-cycle-contention"
CONDUIT_NAME = "bench-scope-cycle-contention"

THREAD_SWEEP = [
    max(1, int(token))
    for token in os.environ.get("BENCH_CONTENTION_THREADS", "1,3,5").split(",")
]
DURATION_S = max(0.5, float(os.environ.get("BENCH_CONTENTION_SECONDS", "5.0")))
WITH_MELDS = os.environ.get("BENCH_CONTENTION_MELDS", "1") == "1"
STALL_NS = int(
    max(0.05, float(os.environ.get("BENCH_CONTENTION_STALL_MS", "1.0"))) * 1e6
)
MICRO_MODE = os.environ.get("BENCH_CONTENTION_MICRO", "0") == "1"
MICRO_ITERS = max(
    1000, int(os.environ.get("BENCH_CONTENTION_MICRO_ITERS", "200000"))
)


@dataclass
class ThreadStats:
    """
    Per-thread timing accumulators for one sweep.
    """

    cycles: int = 0
    create_ns: List[int] = field(default_factory=list)
    lock_wait_ns: List[int] = field(default_factory=list)
    cleanup_ns: List[int] = field(default_factory=list)
    meld_ns: List[int] = field(default_factory=list)
    outer_meld1_ns: List[int] = field(default_factory=list)
    outer_meld2_ns: List[int] = field(default_factory=list)
    space_enter_ns: List[int] = field(default_factory=list)
    request_meld1_ns: List[int] = field(default_factory=list)
    request_meld2_ns: List[int] = field(default_factory=list)
    space_exit_ns: List[int] = field(default_factory=list)
    stalls: List[str] = field(default_factory=list)


def _reset_runtime() -> None:
    """
    Reset the Aether singleton runtime between sweeps.
    """
    from melder.aether.aether import Aether
    from melder.aether.conduit.conduit import Conduit
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.nexus.nexus import Nexus

    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _existence_for(cls: type) -> Any:
    """
    Map one gauntlet class to its gauntlet existence (same as the suite).
    """
    from melder.aether.spellbook.existence.existence import Existence

    if cls in set(_support.SINGLETON_TYPES):
        return Existence.unique
    if cls in set(_support.OUTER_SCOPED_TYPES):
        return Existence.unique_per_conduit
    if cls in set(_support.REQUEST_SCOPED_TYPES):
        return Existence.unique_per_spell_space
    return Existence.many


def _build_root() -> Any:
    """
    Bind the gauntlet graph and conjure one root conduit (caching disabled).
    """
    from melder.aether.spellbook.spellbook import Spellbook

    _reset_runtime()
    spellbook = Spellbook(aetheric_frame=FRAME_NAME)
    configuration = spellbook.get_configuration()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
        system_caching_enabled=False,
    )
    spell_ids: Dict[type, str] = {}
    for cls in _support.ALL_CLASSES:
        spell_ids[cls] = spellbook.bind(
            spell=cls,
            existence=_existence_for(cls),
            permissions="create",
        )
    conduit = spellbook.conjure(name=CONDUIT_NAME, dynamic=False)
    return spellbook, conduit, spell_ids


def _worker(
        *,
        root: Any,
        spell_ids: Dict[type, str],
        stats: ThreadStats,
        stop_at: float,
) -> None:
    """
    Run pooled lesser-conduit scope cycles until the deadline.

    Contract:
        - One cycle = root-lock wait probe + create_lesser_conduit +
          (optional gauntlet-lite melds + one request spellspace) + cleanup.
        - Per-call durations and >threshold stalls are recorded per surface.
    """
    outer_cls = _support.OUTER_SCOPED_TYPES[0]
    request_cls = _support.REQUEST_SCOPED_TYPES[0]
    outer_id = spell_ids[outer_cls]
    request_id = spell_ids[request_cls]
    root_lock = root._lock
    while time.perf_counter() < stop_at:
        # Root-lock wait probe: sample-then-release. The lock is NOT held
        # across create_lesser_conduit -- since the lock-narrowing fix the
        # create body only takes the parent lock for its short link window,
        # and holding the probe lock across the call would re-serialize the
        # narrowed path and falsify the measurement.
        wait_t0 = time.perf_counter_ns()
        root_lock.acquire()
        lock_wait = time.perf_counter_ns() - wait_t0
        root_lock.release()
        create_t0 = time.perf_counter_ns()
        lesser = root.create_lesser_conduit()
        create_ns = time.perf_counter_ns() - create_t0
        meld_ns = 0
        outer1_ns = 0
        outer2_ns = 0
        enter_ns = 0
        request1_ns = 0
        request2_ns = 0
        exit_ns = 0
        if WITH_MELDS:
            # Sub-attributed meld segments. meld#1 of each family is the
            # CONSTRUCTION lane (storage was reset by the pool cycle, so the
            # executor builds the instance even on a fast-door hit); meld#2
            # is the pure repeat-door lane (cached instance read). Timing
            # them separately attributes per-cycle cost to the right lane.
            seg_t0 = time.perf_counter_ns()
            lesser.meld(spell=outer_id)
            outer1_ns = time.perf_counter_ns() - seg_t0
            seg_t0 = time.perf_counter_ns()
            lesser.meld(spell=outer_id)
            outer2_ns = time.perf_counter_ns() - seg_t0
            space_cm = lesser.enter_spellspace()
            seg_t0 = time.perf_counter_ns()
            space = space_cm.__enter__()
            enter_ns = time.perf_counter_ns() - seg_t0
            try:
                seg_t0 = time.perf_counter_ns()
                space.meld(spell=request_id)
                request1_ns = time.perf_counter_ns() - seg_t0
                seg_t0 = time.perf_counter_ns()
                space.meld(spell=request_id)
                request2_ns = time.perf_counter_ns() - seg_t0
            finally:
                seg_t0 = time.perf_counter_ns()
                space_cm.__exit__(None, None, None)
                exit_ns = time.perf_counter_ns() - seg_t0
            meld_ns = (
                outer1_ns + outer2_ns + enter_ns
                + request1_ns + request2_ns + exit_ns
            )
        cleanup_t0 = time.perf_counter_ns()
        lesser.cleanup()
        cleanup_ns = time.perf_counter_ns() - cleanup_t0

        stats.cycles += 1
        stats.lock_wait_ns.append(lock_wait)
        stats.create_ns.append(create_ns)
        stats.cleanup_ns.append(cleanup_ns)
        if WITH_MELDS:
            stats.meld_ns.append(meld_ns)
            stats.outer_meld1_ns.append(outer1_ns)
            stats.outer_meld2_ns.append(outer2_ns)
            stats.space_enter_ns.append(enter_ns)
            stats.request_meld1_ns.append(request1_ns)
            stats.request_meld2_ns.append(request2_ns)
            stats.space_exit_ns.append(exit_ns)
        for surface, value in (
                ("root_lock_wait", lock_wait),
                ("create", create_ns),
                ("outer_meld1", outer1_ns),
                ("outer_meld2", outer2_ns),
                ("space_enter", enter_ns),
                ("request_meld1", request1_ns),
                ("request_meld2", request2_ns),
                ("space_exit", exit_ns),
                ("cleanup", cleanup_ns),
        ):
            if value >= STALL_NS:
                stats.stalls.append(f"{surface} {value / 1e6:.3f}ms")


def _series_line(name: str, samples: List[int]) -> str:
    """
    Render avg/median/p95/max for one timing series in microseconds.
    """
    if not samples:
        return f"{name:16s} (no samples)"
    ordered = sorted(samples)
    p95 = ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))]
    return (
        f"{name:16s} avg={statistics.fmean(samples) / 1e3:9.2f}us "
        f"med={statistics.median(samples) / 1e3:9.2f}us "
        f"p95={p95 / 1e3:9.2f}us "
        f"max={max(samples) / 1e6:8.3f}ms"
    )


def _run_sweep(thread_count: int) -> None:
    """
    Run one contention sweep and print the per-surface report.
    """
    spellbook, root, spell_ids = _build_root()
    try:
        all_stats = [ThreadStats() for _ in range(thread_count)]
        stop_at = time.perf_counter() + DURATION_S
        threads = [
            threading.Thread(
                target=_worker,
                kwargs={
                    "root": root,
                    "spell_ids": spell_ids,
                    "stats": all_stats[index],
                    "stop_at": stop_at,
                },
                name=f"contention-{index}",
            )
            for index in range(thread_count)
        ]
        bench_t0 = time.perf_counter()
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        elapsed = time.perf_counter() - bench_t0

        total_cycles = sum(stats.cycles for stats in all_stats)
        merged: Dict[str, List[int]] = defaultdict(list)
        stall_counts: Dict[str, int] = defaultdict(int)
        worst_stalls: List[str] = []
        for stats in all_stats:
            merged["root_lock_wait"].extend(stats.lock_wait_ns)
            merged["create"].extend(stats.create_ns)
            merged["cleanup"].extend(stats.cleanup_ns)
            merged["melds"].extend(stats.meld_ns)
            merged["outer_meld1"].extend(stats.outer_meld1_ns)
            merged["outer_meld2"].extend(stats.outer_meld2_ns)
            merged["space_enter"].extend(stats.space_enter_ns)
            merged["request_meld1"].extend(stats.request_meld1_ns)
            merged["request_meld2"].extend(stats.request_meld2_ns)
            merged["space_exit"].extend(stats.space_exit_ns)
            for stall in stats.stalls:
                stall_counts[stall.split(" ")[0]] += 1
            worst_stalls.extend(stats.stalls)
        worst_stalls.sort(
            key=lambda entry: float(entry.split(" ")[1][:-2]),
            reverse=True,
        )
        total_wait_ms = sum(merged["root_lock_wait"]) / 1e6

        print(
            f"\n--- threads={thread_count} duration={elapsed:.2f}s "
            f"melds={'on' if WITH_MELDS else 'off'} ---"
        )
        print(
            f"cycles={total_cycles}  cycles/s={total_cycles / elapsed:,.0f}  "
            f"per-thread={[stats.cycles for stats in all_stats]}"
        )
        print(_series_line("root_lock_wait", merged["root_lock_wait"]))
        print(_series_line("create", merged["create"]))
        if WITH_MELDS:
            print(_series_line("melds", merged["melds"]))
            print(_series_line("  outer_meld1", merged["outer_meld1"]))
            print(_series_line("  outer_meld2", merged["outer_meld2"]))
            print(_series_line("  space_enter", merged["space_enter"]))
            print(_series_line("  request_meld1", merged["request_meld1"]))
            print(_series_line("  request_meld2", merged["request_meld2"]))
            print(_series_line("  space_exit", merged["space_exit"]))
        print(_series_line("cleanup", merged["cleanup"]))
        print(
            f"root-lock wait total: {total_wait_ms:,.1f}ms "
            f"({total_wait_ms / (elapsed * 1e3 * thread_count) * 100:.1f}% of "
            f"thread-time)"
        )
        stall_text = ", ".join(
            f"{surface}:{count}" for surface, count in sorted(stall_counts.items())
        )
        print(f"stalls >= {STALL_NS / 1e6:.1f}ms: {stall_text or 'none'}")
        if worst_stalls:
            print(f"worst stalls: {', '.join(worst_stalls[:6])}")
    finally:
        root.permanent_cleanup()
        spellbook.cleanup()


def _micro_worker(
        *,
        root: Any,
        outer_id: str,
        request_id: str,
        barrier: "threading.Barrier",
        results: Dict[str, float],
) -> None:
    """
    Run tight repeat-meld loops on one private lesser conduit.

    Contract:
        - All iterations after warmup are pure fast-door hits (cached
          instance reads); the loop measures the door itself, isolated
          from scope-cycle machinery.
        - Threads start together via the barrier so cross-thread door
          inflation (shared spell/spellbook/context guard reads) shows
          in the per-op time.
    """
    lesser = root.create_lesser_conduit()
    try:
        for _ in range(1000):
            lesser.meld(spell=outer_id)
        barrier.wait(timeout=10)
        loop_t0 = time.perf_counter_ns()
        for _ in range(MICRO_ITERS):
            lesser.meld(spell=outer_id)
        results["outer_door_ns"] = (
            (time.perf_counter_ns() - loop_t0) / MICRO_ITERS
        )
        space_cm = lesser.enter_spellspace()
        space = space_cm.__enter__()
        try:
            for _ in range(1000):
                space.meld(spell=request_id)
            barrier.wait(timeout=10)
            loop_t0 = time.perf_counter_ns()
            for _ in range(MICRO_ITERS):
                space.meld(spell=request_id)
            results["request_door_ns"] = (
                (time.perf_counter_ns() - loop_t0) / MICRO_ITERS
            )
        finally:
            space_cm.__exit__(None, None, None)
    finally:
        lesser.cleanup()


def _run_micro(thread_count: int) -> None:
    """
    Run one repeat-meld micro sweep and print per-op door costs.
    """
    spellbook, root, spell_ids = _build_root()
    try:
        outer_id = spell_ids[_support.OUTER_SCOPED_TYPES[0]]
        request_id = spell_ids[_support.REQUEST_SCOPED_TYPES[0]]
        barrier = threading.Barrier(thread_count)
        all_results: List[Dict[str, float]] = [
            {} for _ in range(thread_count)
        ]
        threads = [
            threading.Thread(
                target=_micro_worker,
                kwargs={
                    "root": root,
                    "outer_id": outer_id,
                    "request_id": request_id,
                    "barrier": barrier,
                    "results": all_results[index],
                },
                name=f"micro-{index}",
            )
            for index in range(thread_count)
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        print(f"\n--- micro threads={thread_count} iters={MICRO_ITERS} ---")
        for key in ("outer_door_ns", "request_door_ns"):
            values = [result[key] for result in all_results if key in result]
            if values:
                per_thread = ", ".join(f"{value:7.1f}" for value in values)
                print(
                    f"{key:16s} avg={statistics.fmean(values):7.1f}ns "
                    f"per-thread=[{per_thread}]"
                )
    finally:
        root.permanent_cleanup()
        spellbook.cleanup()


def main() -> None:
    """
    Run the contention sweeps (or micro mode) and print the report.
    """
    gil_probe = getattr(sys, "_is_gil_enabled", None)
    gil_text = "enabled" if (gil_probe is None or gil_probe()) else "disabled"
    print("=" * 78)
    print("SCOPE CYCLE CONTENTION BREAKDOWN (pooled lesser conduits)")
    print(
        f"classes={len(_support.ALL_CLASSES)}  threads_sweep={THREAD_SWEEP}  "
        f"duration={DURATION_S}s  melds={'on' if WITH_MELDS else 'off'}  "
        f"gil={gil_text}"
    )
    print("=" * 78)
    if MICRO_MODE:
        for thread_count in THREAD_SWEEP:
            _run_micro(thread_count)
        return
    for thread_count in THREAD_SWEEP:
        _run_sweep(thread_count)


if __name__ == "__main__":
    main()
