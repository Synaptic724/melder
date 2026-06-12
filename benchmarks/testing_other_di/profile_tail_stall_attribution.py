"""
Tail-stall attribution profiler: classify melder's 17-70ms gauntlet tails.

Purpose:
    Prior lanes exonerated the scope-cycle locks and the fast meld door for
    melder's tail stalls (whole-cycle cv 240-340% vs dishka ~70% in the same
    runs). This harness classifies the remaining suspects:
      - GC pauses: gc.callbacks record every collection window (phase,
        generation, wall time); each worker-observed stall is checked for
        overlap with a GC window.
      - Everything else: stalls with no GC overlap point at allocator /
        scheduler / lock behavior and keep their surface attribution.
    A GC-disabled control mode provides the causal check: if tails collapse
    with gc off, GC is convicted; if they persist, GC is exonerated.

Usage:
    .venv_new\\Scripts\\python.exe benchmarks\\testing_other_di\\profile_tail_stall_attribution.py
    $env:BENCH_TAIL_GC_DISABLE="1"; ... (control mode)

Env knobs:
    BENCH_TAIL_THREADS     comma list (default "3")
    BENCH_TAIL_SECONDS     seconds per sweep (default 10.0)
    BENCH_TAIL_STALL_MS    stall threshold in ms (default 1.0)
    BENCH_TAIL_GC_DISABLE  "1" disables gc during the measured window
"""

import gc
import os
import statistics
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Tuple


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

import profile_scope_cycle_contention as _cycle  # noqa: E402
import melder_gauntlet_support as _support  # noqa: E402

THREAD_SWEEP = [
    max(1, int(token))
    for token in os.environ.get("BENCH_TAIL_THREADS", "3").split(",")
]
DURATION_S = max(1.0, float(os.environ.get("BENCH_TAIL_SECONDS", "10.0")))
STALL_NS = int(
    max(0.1, float(os.environ.get("BENCH_TAIL_STALL_MS", "1.0"))) * 1e6
)
GC_DISABLE = os.environ.get("BENCH_TAIL_GC_DISABLE", "0") == "1"


@dataclass
class GcLog:
    """
    GC collection windows recorded via gc.callbacks.

    Contract:
        - Entries are (phase, generation, perf_counter_ns) appended from the
          GC callback; start/stop pairs are folded into windows post-run.
        - The callback list is process-wide; install/remove is owned here.
    """

    events: List[Tuple[str, int, int]] = field(default_factory=list)

    def callback(self, phase: str, info: Dict[str, Any]) -> None:
        """
        Record one GC phase event with its generation and timestamp.
        """
        self.events.append(
            (phase, info.get("generation", -1), time.perf_counter_ns())
        )

    def windows(self) -> List[Tuple[int, int, int]]:
        """
        Fold start/stop events into (start_ns, stop_ns, generation) windows.
        """
        folded: List[Tuple[int, int, int]] = []
        open_start: Dict[int, int] = {}
        for phase, generation, stamp in self.events:
            if phase == "start":
                open_start[generation] = stamp
            else:
                started = open_start.pop(generation, None)
                if started is not None:
                    folded.append((started, stamp, generation))
        return folded


@dataclass
class StallLog:
    """
    Per-thread stall records: (surface, start_ns, duration_ns).
    """

    cycles: int = 0
    records: List[Tuple[str, int, int]] = field(default_factory=list)


def _worker(
        *,
        root: Any,
        spell_ids: Dict[type, str],
        log: StallLog,
        stop_at: float,
) -> None:
    """
    Run gauntlet-lite scope cycles, logging stall windows per surface.

    Contract:
        - One cycle = create lesser -> 2 outer melds -> request spellspace
          with 2 melds -> cleanup (same shape as the contention harness).
        - Any segment >= threshold is logged with its absolute start time so
          overlap with GC windows can be computed post-run.
    """
    outer_id = spell_ids[_support.OUTER_SCOPED_TYPES[0]]
    request_id = spell_ids[_support.REQUEST_SCOPED_TYPES[0]]
    while time.perf_counter() < stop_at:
        seg_start = time.perf_counter_ns()
        lesser = root.create_lesser_conduit()
        seg_dur = time.perf_counter_ns() - seg_start
        if seg_dur >= STALL_NS:
            log.records.append(("create", seg_start, seg_dur))

        seg_start = time.perf_counter_ns()
        lesser.meld(spell=outer_id)
        lesser.meld(spell=outer_id)
        with lesser.enter_spellspace() as space:
            space.meld(spell=request_id)
            space.meld(spell=request_id)
        seg_dur = time.perf_counter_ns() - seg_start
        if seg_dur >= STALL_NS:
            log.records.append(("melds", seg_start, seg_dur))

        seg_start = time.perf_counter_ns()
        lesser.cleanup()
        seg_dur = time.perf_counter_ns() - seg_start
        if seg_dur >= STALL_NS:
            log.records.append(("cleanup", seg_start, seg_dur))
        log.cycles += 1


def _overlaps(
        stall: Tuple[str, int, int],
        gc_windows: List[Tuple[int, int, int]],
) -> bool:
    """
    Return True when the stall window intersects any GC window.
    """
    _surface, start, duration = stall
    end = start + duration
    for window_start, window_stop, _generation in gc_windows:
        if window_start < end and window_stop > start:
            return True
    return False


def _run_sweep(thread_count: int) -> None:
    """
    Run one attribution sweep and print the classification report.
    """
    spellbook, root, spell_ids = _cycle._build_root()
    gc_log = GcLog()
    try:
        logs = [StallLog() for _ in range(thread_count)]
        gc.collect()
        if GC_DISABLE:
            gc.disable()
        else:
            gc.callbacks.append(gc_log.callback)
        stop_at = time.perf_counter() + DURATION_S
        threads = [
            threading.Thread(
                target=_worker,
                kwargs={
                    "root": root,
                    "spell_ids": spell_ids,
                    "log": logs[index],
                    "stop_at": stop_at,
                },
                name=f"tail-{index}",
            )
            for index in range(thread_count)
        ]
        bench_t0 = time.perf_counter()
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        elapsed = time.perf_counter() - bench_t0
    finally:
        if GC_DISABLE:
            gc.enable()
        elif gc_log.callback in gc.callbacks:
            gc.callbacks.remove(gc_log.callback)
        root.permanent_cleanup()
        spellbook.cleanup()

    gc_windows = gc_log.windows()
    gc_durations = [stop - start for start, stop, _gen in gc_windows]
    all_stalls = [record for log in logs for record in log.records]
    all_stalls.sort(key=lambda record: record[2], reverse=True)
    total_cycles = sum(log.cycles for log in logs)
    overlapped = [
        stall for stall in all_stalls if _overlaps(stall, gc_windows)
    ]
    by_surface: Dict[str, int] = {}
    for surface, _start, _dur in all_stalls:
        by_surface[surface] = by_surface.get(surface, 0) + 1

    print(
        f"\n--- threads={thread_count} duration={elapsed:.2f}s "
        f"gc={'DISABLED' if GC_DISABLE else 'on'} "
        f"stall>={STALL_NS / 1e6:.1f}ms ---"
    )
    print(f"cycles={total_cycles}  cycles/s={total_cycles / elapsed:,.0f}")
    if gc_durations:
        print(
            f"gc collections={len(gc_durations)}  "
            f"total={sum(gc_durations) / 1e6:.1f}ms  "
            f"avg={statistics.fmean(gc_durations) / 1e6:.3f}ms  "
            f"max={max(gc_durations) / 1e6:.3f}ms"
        )
    else:
        print("gc collections=0")
    print(
        f"stalls={len(all_stalls)}  by-surface={by_surface}  "
        f"gc-overlapped={len(overlapped)} "
        f"({(len(overlapped) / len(all_stalls) * 100) if all_stalls else 0:.0f}%)"
    )
    if all_stalls:
        worst = ", ".join(
            f"{surface} {dur / 1e6:.2f}ms{'*' if _overlaps(stall, gc_windows) else ''}"
            for stall in all_stalls[:8]
            for surface, _s, dur in (stall,)
        )
        print(f"worst (* = gc-overlapped): {worst}")


def main() -> None:
    """
    Run the attribution sweeps and print the report.
    """
    gil_probe = getattr(sys, "_is_gil_enabled", None)
    gil_text = "enabled" if (gil_probe is None or gil_probe()) else "disabled"
    print("=" * 78)
    print("TAIL STALL ATTRIBUTION (GC windows vs surface stalls)")
    print(
        f"threads_sweep={THREAD_SWEEP}  duration={DURATION_S}s  "
        f"gc_disable={GC_DISABLE}  gil={gil_text}"
    )
    print("=" * 78)
    for thread_count in THREAD_SWEEP:
        _run_sweep(thread_count)


if __name__ == "__main__":
    main()
