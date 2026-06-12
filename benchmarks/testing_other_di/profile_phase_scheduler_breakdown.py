"""
Phase-scheduler breakdown profiler: per-phase walls, plan_group division.

Purpose:
    Answer two questions about PhaseScheduler v2 with numbers:
      1. Where does conjure wall time live per PHASE (barrier wall vs the
         summed busy time of the workers that served it)?
      2. Is the fused plan_group (phases 8-11) work divided evenly across
         workers, or do contiguous equal-count chunks load-imbalance on
         heterogeneous per-spell costs (deep roots vs leaves)?

Method:
    - Reuses the real-world gauntlet class graph (29 binds) so numbers line
      up with `profile_bind_conjure_cycle.py` and the competitive suites.
    - Patches the Spellbook-module `PhaseScheduler` symbol (the sanctioned
      patch seam) with an instrumented subclass that records per-phase wall
      times and unit counts.
    - Patches `SpellbookCreationSystem._run_spell_chunk` with a timing
      wrapper that preserves the original cancel/error semantics while
      recording per-spell durations and the serving worker thread.
    - Optional chunk-granularity experiment: BENCH_BREAKDOWN_CHUNK_MULT
      multiplies the chunk count (chunks = workers * mult) so queue-level
      balancing can be measured against per-unit overhead.

Usage (run under the native free-threaded interpreter):
    .venv_new\\Scripts\\python.exe benchmarks\\testing_other_di\\profile_phase_scheduler_breakdown.py

Env knobs:
    BENCH_BREAKDOWN_WORKERS     comma list of worker counts (default "1,2,5")
    BENCH_BREAKDOWN_REPEATS     timed repeats per worker count (default 5)
    BENCH_BREAKDOWN_CHUNK_MULT  comma list of chunk multipliers (default "1")

Contract:
    - Caching disabled so phases 8-11 always run.
    - Each cycle starts from a fresh Aether singleton.
    - par_eff = busy_sum / (wall * workers); 1.00 is perfect division,
      shown only for multi-unit phases.
"""

import os
import statistics
import sys
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Sequence, Tuple


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

FRAME_NAME = "bench-phase-scheduler-breakdown"
CONDUIT_NAME = "bench-phase-scheduler-breakdown"

WORKER_SWEEP = [
    max(1, int(token))
    for token in os.environ.get("BENCH_BREAKDOWN_WORKERS", "1,2,5").split(",")
]
REPEATS = max(1, int(os.environ.get("BENCH_BREAKDOWN_REPEATS", "5")))
CHUNK_MULT_SWEEP = [
    max(1, int(token))
    for token in os.environ.get("BENCH_BREAKDOWN_CHUNK_MULT", "1").split(",")
]


@dataclass
class PhaseRecord:
    """
    One phase execution observed by the instrumented scheduler.
    """

    name: str
    wall_ns: int
    unit_count: int


@dataclass
class SpellRecord:
    """
    One per-spell step execution observed inside a chunk unit.
    """

    phase: str
    spell_id: str
    duration_ns: int
    thread_name: str


@dataclass
class CycleCapture:
    """
    All instrumentation captured for one bind->conjure cycle.
    """

    phases: List[PhaseRecord] = field(default_factory=list)
    spells: List[SpellRecord] = field(default_factory=list)


_CAPTURE = CycleCapture()

# Original-partitioner holder so repeated installs (one per chunk-mult value)
# always wrap the PRODUCTION partitioner instead of compounding multipliers.
_ORIGINAL_CHUNK_SPELLS: List[Callable[..., Any]] = []


def _reset_capture() -> CycleCapture:
    """
    Swap in a fresh capture object and return it.
    """
    global _CAPTURE
    _CAPTURE = CycleCapture()
    return _CAPTURE


def _install_instrumentation(chunk_mult: int) -> None:
    """
    Install the instrumented scheduler and chunk-timing wrapper.

    Contract:
        - Idempotent per process for the scheduler subclass; the chunk
          multiplier is applied by re-patching `_chunk_spells` each call.
        - Preserves production semantics exactly: chunk cancel checks and
          first-error re-raise behavior are replicated unchanged.
    """
    import melder.aether.spellbook.spellbook as spellbook_module
    from melder.aether.spellbook.spellbook_creation_system import (
        SpellbookCreationSystem,
    )
    from melder.utilities.custom_exceptions.operation_cancelled_error import (
        OperationCancelledError,
    )
    from melder.utilities.synchronization.phase_scheduler import PhaseScheduler

    class BreakdownPhaseScheduler(PhaseScheduler):
        """
        PhaseScheduler that records per-phase wall time and unit counts.
        """

        def _run_single_phase(
                self,
                phase_name: str,
                factory: Callable[[], Sequence[Any]],
        ) -> Sequence[Any]:
            """
            Time one phase (factory + dispatch + barrier) end to end.
            """
            phase_t0 = time.perf_counter_ns()
            units = super()._run_single_phase(phase_name, factory)
            _CAPTURE.phases.append(
                PhaseRecord(
                    name=phase_name,
                    wall_ns=time.perf_counter_ns() - phase_t0,
                    unit_count=len(units),
                )
            )
            return units

    spellbook_module.PhaseScheduler = BreakdownPhaseScheduler

    if not _ORIGINAL_CHUNK_SPELLS:
        # Class-attribute access on a staticmethod already yields the plain
        # function in Python 3; no `__func__` indirection exists here.
        _ORIGINAL_CHUNK_SPELLS.append(SpellbookCreationSystem._chunk_spells)
    original_chunk_spells = _ORIGINAL_CHUNK_SPELLS[0]

    def _multiplied_chunk_spells(spells: List[Any], chunk_count: int) -> List[Tuple[Any, ...]]:
        """
        Apply the chunk-granularity multiplier under measurement.
        """
        return original_chunk_spells(spells, chunk_count * chunk_mult)

    SpellbookCreationSystem._chunk_spells = staticmethod(_multiplied_chunk_spells)

    def _timed_run_spell_chunk(
            spell_runner: Callable[[Any], None],
            chunk: Tuple[Any, ...],
            cancel_event: Any,
            phase_name: str,
    ) -> None:
        """
        Production chunk loop with per-spell timing capture added.
        """
        thread_name = threading.current_thread().name
        for spell in chunk:
            if cancel_event is not None and cancel_event.is_set:
                raise OperationCancelledError(
                    f"Phase '{phase_name}' chunk aborted due to run cancellation."
                )
            spell_t0 = time.perf_counter_ns()
            spell_runner(spell)
            _CAPTURE.spells.append(
                SpellRecord(
                    phase=phase_name,
                    spell_id=spell.spell_id,
                    duration_ns=time.perf_counter_ns() - spell_t0,
                    thread_name=thread_name,
                )
            )

    SpellbookCreationSystem._run_spell_chunk = staticmethod(_timed_run_spell_chunk)


def _reset_runtime() -> None:
    """
    Reset the Aether singleton runtime between cycles.
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

def _spell_names_by_id(spell_ids: Dict[type, str]) -> Dict[str, str]:
    """
    Invert the class->spell-id map into spell-id->class-name for reporting.
    """
    return {spell_id: cls.__name__ for cls, spell_id in spell_ids.items()}


def _run_cycle(workers: int) -> Tuple[CycleCapture, Dict[str, str]]:
    """
    Run one instrumented bind->conjure cycle at the requested worker count.
    """
    from melder.aether.spellbook.spellbook import Spellbook

    _reset_runtime()
    capture = _reset_capture()
    spellbook = Spellbook(aetheric_frame=FRAME_NAME)
    configuration = spellbook.get_configuration()
    configuration.set_property("phase_scheduler_workers_per_spellbook", workers)
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
    names = _spell_names_by_id(spell_ids)
    conduit.permanent_cleanup()
    spellbook.cleanup()
    return capture, names


def _format_ms(value_ns: float) -> str:
    """
    Render nanoseconds as fixed-width milliseconds.
    """
    return f"{value_ns / 1e6:8.3f}ms"


def _report_sweep(workers: int, chunk_mult: int) -> None:
    """
    Run REPEATS cycles and print the per-phase and plan_group division report.
    """
    phase_walls: Dict[str, List[int]] = defaultdict(list)
    phase_units: Dict[str, int] = {}
    last_capture: CycleCapture = CycleCapture()
    last_names: Dict[str, str] = {}

    for _ in range(REPEATS):
        capture, names = _run_cycle(workers)
        last_capture = capture
        last_names = names
        for record in capture.phases:
            phase_walls[record.name].append(record.wall_ns)
            phase_units[record.name] = record.unit_count

    print(f"\n--- workers={workers} chunk_mult={chunk_mult} repeats={REPEATS} ---")
    print(f"{'phase':24s} {'wall_med':>10s} {'units':>5s} {'busy_sum':>10s} {'par_eff':>7s}")
    busy_by_phase: Dict[str, int] = defaultdict(int)
    for record in last_capture.spells:
        busy_by_phase[record.phase] += record.duration_ns
    for name, walls in phase_walls.items():
        wall_med = statistics.median(walls)
        units = phase_units.get(name, 0)
        busy = busy_by_phase.get(name, 0)
        if units > 1 and busy > 0 and wall_med > 0:
            par_eff = f"{busy / (wall_med * workers):7.2f}"
        else:
            par_eff = "      -"
        busy_text = _format_ms(busy) if busy else "         -"
        print(f"{name:24s} {_format_ms(wall_med)} {units:5d} {busy_text} {par_eff}")

    # plan_group division detail (last repeat).
    plan_records = [r for r in last_capture.spells if r.phase == "plan_group"]
    if plan_records:
        per_thread: Dict[str, int] = defaultdict(int)
        for record in plan_records:
            per_thread[record.thread_name] += record.duration_ns
        thread_loads = sorted(per_thread.values(), reverse=True)
        loads_text = ", ".join(f"{load / 1e6:.3f}ms" for load in thread_loads)
        print(f"plan_group worker loads (last repeat): [{loads_text}]")
        if len(thread_loads) > 1 and thread_loads[-1] > 0:
            print(
                "plan_group load skew (max/min): "
                f"{thread_loads[0] / thread_loads[-1]:.2f}x"
            )
        top_spells = sorted(
            plan_records, key=lambda r: r.duration_ns, reverse=True
        )[:5]
        top_text = ", ".join(
            f"{last_names.get(r.spell_id, r.spell_id[:8])} {r.duration_ns / 1e6:.3f}ms"
            for r in top_spells
        )
        print(f"plan_group top spells (last repeat): {top_text}")


def main() -> None:
    """
    Run the breakdown sweeps and print the report.
    """
    gil_probe = getattr(sys, "_is_gil_enabled", None)
    gil_text = "enabled" if (gil_probe is None or gil_probe()) else "disabled"
    print("=" * 78)
    print("PHASE SCHEDULER BREAKDOWN (caching disabled, phases 1-11)")
    print(
        f"classes={len(_support.ALL_CLASSES)}  repeats={REPEATS}  "
        f"workers_sweep={WORKER_SWEEP}  chunk_mult_sweep={CHUNK_MULT_SWEEP}  "
        f"gil={gil_text}"
    )
    print("=" * 78)
    for chunk_mult in CHUNK_MULT_SWEEP:
        _install_instrumentation(chunk_mult)
        for workers in WORKER_SWEEP:
            _report_sweep(workers, chunk_mult)


if __name__ == "__main__":
    main()
