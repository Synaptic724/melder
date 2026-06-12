"""
Bind -> conjure -> resolution cycle benchmark + cProfile attribution.

Purpose:
    Price every stage of melder setup separately so the ~206ms wall can be
    attacked with numbers instead of vibes:
      - bind lane:        N binds on a fresh Spellbook (reflection + hashing)
      - conjure lane:     phases 1-11 (cold / caching disabled) vs phases 1-7
                          (cache full-hit)
      - resolution lane:  first meld of every spell (plain resolution cold,
                          lazy manifest hydration warm)
      - full cycle:       bind + conjure + first-meld sweep per posture

Postures:
    disabled   caching off            -> conjure runs phases 1-11, zero cache IO
    cold       caching on, cache wiped-> phases 1-11 + staging + bundle emit
    warm       caching on, pre-seeded -> full-hit, phases 1-7 + lazy hydration

Usage:
    Wall timings (run under the native free-threaded posture):
        .venv_new\\Scripts\\python.exe benchmarks\\testing_other_di\\profile_bind_conjure_cycle.py

    cProfile attribution (re-execs under PYTHON_GIL=1; relative attribution
    is the deliverable, absolute numbers are inflated by the profiler):
        .venv_new\\Scripts\\python.exe benchmarks\\testing_other_di\\profile_bind_conjure_cycle.py --profile

Env knobs:
    BENCH_CYCLE_REPEATS      timed repeats per posture (default 9)
    BENCH_CYCLE_WORKERS      phase_scheduler_workers_per_spellbook (default 1)
    BENCH_CYCLE_KEEP_CACHE   "1" keeps the bench cache dir after the run

Contract:
    - Uses the exact real-world gauntlet class graph (29 binds) so numbers
      line up with the competitive suite's melder setup figure.
    - Each cycle starts from a fresh Aether singleton; frame + conduit names
      are constant so warm cycles classify as cache full-hits.
    - The bench cache lives under `src/melder/__melder_cache__/` (the runtime
      requires package-root-relative fragments) in its own subfolder and is
      removed at exit unless BENCH_CYCLE_KEEP_CACHE=1.
    - Writes the cProfile report to `bind_conjure_cycle_profile.txt` next to
      this script.
"""

import cProfile
import gc
import io
import os
import pstats
import shutil
import statistics
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


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


def _ensure_gil_enabled_interpreter() -> None:
    """
    Re-exec under PYTHON_GIL=1 when profiling on a free-threaded build.

    Contract:
        - Only called for `--profile` runs; wall-timing runs keep the native
          interpreter posture so numbers reflect production reality.
    """
    is_gil_enabled_probe = getattr(sys, "_is_gil_enabled", None)
    if is_gil_enabled_probe is None or is_gil_enabled_probe():
        return
    environment = dict(os.environ)
    environment["PYTHON_GIL"] = "1"
    os.execve(sys.executable, [sys.executable, *sys.argv], environment)


if "--profile" in sys.argv:
    _ensure_gil_enabled_interpreter()
_ensure_local_paths()

import melder_gauntlet_support as _support  # noqa: E402

FRAME_NAME = "bench-bind-conjure-cycle"
CONDUIT_NAME = "bench-bind-conjure-cycle"
CACHE_FRAGMENT = Path("__melder_cache__") / "bench_bind_conjure_cycle"

REPEATS = max(1, int(os.environ.get("BENCH_CYCLE_REPEATS", "9")))
WORKERS = max(1, int(os.environ.get("BENCH_CYCLE_WORKERS", "1")))
KEEP_CACHE = os.environ.get("BENCH_CYCLE_KEEP_CACHE", "0") == "1"


# ======================================================================================
# Cycle primitives
# ======================================================================================

@dataclass
class CycleTimings:
    """
    Wall-clock attribution for one bind -> conjure -> first-meld cycle.
    """

    bind_ns: int = 0
    conjure_ns: int = 0
    first_meld_ns: int = 0
    cleanup_ns: int = 0
    per_bind_ns: List[int] = field(default_factory=list)
    cache_bundle_exists: bool = False
    cache_full_hit_possible: bool = False

    @property
    def setup_ns(self) -> int:
        """bind + conjure (the competitive suites' 'setup' figure)."""
        return self.bind_ns + self.conjure_ns

    @property
    def full_cycle_ns(self) -> int:
        """bind + conjure + first-meld sweep."""
        return self.bind_ns + self.conjure_ns + self.first_meld_ns


def _package_root() -> Path:
    """
    Return the melder package root that cache fragments resolve against.
    """
    from melder.aether.aetheric_frame.aetheric_frame_configuration import (
        AethericFrameConfiguration,
    )
    import inspect

    return Path(inspect.getfile(AethericFrameConfiguration)).resolve().parents[2]


def _bench_cache_dir() -> Path:
    """
    Return the absolute bench cache directory.
    """
    return _package_root() / CACHE_FRAGMENT


def _wipe_bench_cache() -> None:
    """
    Remove the bench cache directory (cold-run guarantee).
    """
    cache_dir = _bench_cache_dir()
    if cache_dir.exists():
        shutil.rmtree(cache_dir, ignore_errors=True)


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


def _make_spellbook(*, caching_enabled: bool) -> Any:
    """
    Build one gauntlet-shaped Spellbook with bench cache wiring.
    """
    from melder.aether.spellbook.spellbook import Spellbook

    spellbook = Spellbook(aetheric_frame=FRAME_NAME)
    configuration = spellbook.get_configuration()
    configuration.set_property("phase_scheduler_workers_per_spellbook", WORKERS)
    spellbook.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
        system_caching_enabled=caching_enabled,
    )
    frame_configuration = spellbook._aetheric_frame_configuration
    if frame_configuration is None:
        raise AssertionError("Frame configuration missing after configure_aether_frame.")
    frame_configuration.with_system_cache_root_path(CACHE_FRAGMENT)
    return spellbook


def run_cycle(
        *,
        caching_enabled: bool,
        meld_sweep: bool = True,
        bind_profiler: Optional[cProfile.Profile] = None,
        conjure_profiler: Optional[cProfile.Profile] = None,
        meld_profiler: Optional[cProfile.Profile] = None,
) -> CycleTimings:
    """
    Run one full bind -> conjure -> first-meld cycle and time each stage.

    Contract:
        - Resets the runtime singleton before starting (reset cost excluded).
        - Optional per-stage profilers wrap exactly one stage each so the
          attribution report cannot smear bind cost into conjure cost.
        - Cleanup runs after timing and its cost is reported separately.
    """
    timings = CycleTimings()
    _reset_runtime()
    spellbook = _make_spellbook(caching_enabled=caching_enabled)

    # ---- bind lane ----
    spell_ids: Dict[type, str] = {}
    if bind_profiler is not None:
        bind_profiler.enable()
    bind_t0 = time.perf_counter_ns()
    for cls in _support.ALL_CLASSES:
        single_t0 = time.perf_counter_ns()
        spell_ids[cls] = spellbook.bind(
            spell=cls,
            existence=_existence_for(cls),
            permissions="create",
        )
        timings.per_bind_ns.append(time.perf_counter_ns() - single_t0)
    timings.bind_ns = time.perf_counter_ns() - bind_t0
    if bind_profiler is not None:
        bind_profiler.disable()

    # Probe whether a warm classification is even possible before conjure
    # consumes the state (cached ids must cover live ids).
    if caching_enabled:
        try:
            caching_system = spellbook._get_or_create_caching_system(
                conduit_name=CONDUIT_NAME,
            )
            cached = set(caching_system.cached_spell_ids)
            live = set(spell_ids.values())
            timings.cache_full_hit_possible = bool(live) and live.issubset(cached)
        except Exception:
            timings.cache_full_hit_possible = False

    # ---- conjure lane ----
    if conjure_profiler is not None:
        conjure_profiler.enable()
    conjure_t0 = time.perf_counter_ns()
    conduit = spellbook.conjure(name=CONDUIT_NAME, dynamic=False)
    timings.conjure_ns = time.perf_counter_ns() - conjure_t0
    if conjure_profiler is not None:
        conjure_profiler.disable()

    # ---- resolution lane (first meld of every spell) ----
    try:
        if meld_sweep:
            if meld_profiler is not None:
                meld_profiler.enable()
            meld_t0 = time.perf_counter_ns()
            for cls, spell_id in spell_ids.items():
                resolved = conduit.meld(spell=spell_id)
                if not isinstance(resolved, cls):
                    raise AssertionError(
                        f"meld returned wrong type for {cls.__name__}"
                    )
            timings.first_meld_ns = time.perf_counter_ns() - meld_t0
            if meld_profiler is not None:
                meld_profiler.disable()

        if caching_enabled:
            try:
                bundle_path = spellbook._get_or_create_caching_system(
                    conduit_name=CONDUIT_NAME,
                ).bundle_path
                timings.cache_bundle_exists = Path(bundle_path).exists()
            except Exception:
                timings.cache_bundle_exists = False
    finally:
        cleanup_t0 = time.perf_counter_ns()
        try:
            conduit.cleanup()
        finally:
            _reset_runtime()
        timings.cleanup_ns = time.perf_counter_ns() - cleanup_t0
        gc.collect()

    return timings


# ======================================================================================
# Posture runners
# ======================================================================================

@dataclass
class PostureResult:
    """
    Aggregated repeat timings for one cache posture.
    """

    label: str
    cycles: List[CycleTimings]

    def _stage_ms(self, getter: Callable[[CycleTimings], int]) -> List[float]:
        return [getter(cycle) / 1e6 for cycle in self.cycles]

    def stats_line(self, stage: str, getter: Callable[[CycleTimings], int]) -> str:
        values = self._stage_ms(getter)
        return (
            f"    {stage:<12} min {min(values):8.3f}  "
            f"median {statistics.median(values):8.3f}  "
            f"mean {statistics.fmean(values):8.3f}  "
            f"max {max(values):8.3f} ms"
        )


def run_posture(
        label: str,
        *,
        caching_enabled: bool,
        cold: bool,
        repeats: int,
) -> PostureResult:
    """
    Run timed repeats of one posture.

    Contract:
        - `cold=True` wipes the bench cache before EVERY repeat.
        - warm postures wipe once, then run one untimed seed cycle so every
          timed repeat starts from a guaranteed full-hit cache.
    """
    if cold:
        cycles: List[CycleTimings] = []
        for _ in range(repeats):
            if caching_enabled:
                _wipe_bench_cache()
            cycles.append(run_cycle(caching_enabled=caching_enabled))
        return PostureResult(label=label, cycles=cycles)

    _wipe_bench_cache()
    seed = run_cycle(caching_enabled=caching_enabled)
    if not seed.cache_bundle_exists:
        raise AssertionError(
            "Warm posture seed cycle did not emit a cache bundle; "
            "warm repeats would silently measure cold builds."
        )
    cycles = []
    for _ in range(repeats):
        cycle = run_cycle(caching_enabled=caching_enabled)
        cycles.append(cycle)
    for cycle in cycles:
        if not cycle.cache_full_hit_possible:
            raise AssertionError(
                "Warm repeat was not classifiable as a cache full-hit; "
                "spell fingerprints drifted between cycles."
            )
    return PostureResult(label=label, cycles=cycles)


def print_posture(result: PostureResult) -> None:
    """
    Print the per-stage stat block for one posture.
    """
    print(f"  [{result.label}]  ({len(result.cycles)} repeats)")
    print(result.stats_line("bind", lambda c: c.bind_ns))
    print(result.stats_line("conjure", lambda c: c.conjure_ns))
    print(result.stats_line("setup", lambda c: c.setup_ns))
    print(result.stats_line("first-meld", lambda c: c.first_meld_ns))
    print(result.stats_line("full-cycle", lambda c: c.full_cycle_ns))
    print(result.stats_line("cleanup", lambda c: c.cleanup_ns))
    slowest_binds = sorted(
        (
            (ns / 1e6, _support.ALL_CLASSES[i].__name__)
            for cycle in result.cycles[-1:]
            for i, ns in enumerate(cycle.per_bind_ns)
        ),
        reverse=True,
    )[:3]
    rendered = ", ".join(f"{name} {ms:.3f}ms" for ms, name in slowest_binds)
    print(f"    slowest binds (last repeat): {rendered}")
    print()


def run_timing_suite(repeats: int) -> Dict[str, PostureResult]:
    """
    Run all three postures and print the comparison table.
    """
    gil_probe = getattr(sys, "_is_gil_enabled", None)
    gil_state = "n/a (gil build)" if gil_probe is None else str(gil_probe())
    print("=" * 78)
    print("BIND -> CONJURE -> RESOLUTION CYCLE BENCHMARK")
    print(
        f"classes={len(_support.ALL_CLASSES)}  repeats={repeats}  "
        f"workers={WORKERS}  gil_enabled={gil_state}"
    )
    print("=" * 78)

    results: Dict[str, PostureResult] = {}
    results["disabled"] = run_posture(
        "caching DISABLED (phases 1-11, no cache IO)",
        caching_enabled=False,
        cold=True,
        repeats=repeats,
    )
    print_posture(results["disabled"])

    results["cold"] = run_posture(
        "caching COLD (phases 1-11 + stage + emit)",
        caching_enabled=True,
        cold=True,
        repeats=repeats,
    )
    print_posture(results["cold"])

    results["warm"] = run_posture(
        "caching WARM full-hit (phases 1-7 + hydrate)",
        caching_enabled=True,
        cold=False,
        repeats=repeats,
    )
    print_posture(results["warm"])

    disabled_setup = statistics.median(
        c.setup_ns for c in results["disabled"].cycles
    ) / 1e6
    cold_setup = statistics.median(c.setup_ns for c in results["cold"].cycles) / 1e6
    warm_setup = statistics.median(c.setup_ns for c in results["warm"].cycles) / 1e6
    warm_cycle = statistics.median(
        c.full_cycle_ns for c in results["warm"].cycles
    ) / 1e6
    print("-" * 78)
    print("HEADLINE (median setup = bind + conjure)")
    print(f"  disabled : {disabled_setup:8.3f} ms")
    print(
        f"  cold     : {cold_setup:8.3f} ms   "
        f"(cache overhead vs disabled: {cold_setup - disabled_setup:+.3f} ms)"
    )
    print(
        f"  warm     : {warm_setup:8.3f} ms   "
        f"(saves {disabled_setup - warm_setup:+.3f} ms vs disabled)"
    )
    print(f"  warm full cycle (incl. first-meld hydration): {warm_cycle:8.3f} ms")
    print("-" * 78)
    return results


# ======================================================================================
# cProfile attribution
# ======================================================================================

def _dump_stage_profile(
        label: str,
        profiler: cProfile.Profile,
        report_stream: io.StringIO,
) -> None:
    """
    Append top-40 tottime/cumulative plus lane-targeted rows for one stage.
    """
    stats = pstats.Stats(profiler, stream=report_stream)
    stats.strip_dirs()
    report_stream.write("=" * 78 + "\n")
    report_stream.write(f"[{label}] TOP 40 BY TOTTIME (self time)\n")
    report_stream.write("=" * 78 + "\n")
    stats.sort_stats("tottime").print_stats(40)
    report_stream.write("=" * 78 + "\n")
    report_stream.write(f"[{label}] TOP 40 BY CUMULATIVE (call tree)\n")
    report_stream.write("=" * 78 + "\n")
    stats.sort_stats("cumulative").print_stats(40)
    report_stream.write("=" * 78 + "\n")
    report_stream.write(f"[{label}] LANE ATTRIBUTION\n")
    report_stream.write("=" * 78 + "\n")
    stats.print_stats("compiler_phase_")
    stats.print_stats("spell_requirements_finder|spell_examiner|bind\\.py|spell_id_inspector")
    stats.print_stats("hash_codegen_signature|sha256|fingerprint")
    stats.print_stats("caching_system|manifest|marshal")
    stats.print_stats("phase_scheduler|unit_of_work")


def run_profile_suite() -> None:
    """
    Profile each stage separately for cold and warm postures.

    Contract:
        - One profiler per stage per posture; profilers never overlap, so a
          row in the bind section is genuinely bind-lane cost.
        - Absolute times are profiler-inflated; use them for ranking only.
    """
    report_stream = io.StringIO()

    # Cold posture: wipe, profile bind / conjure(1-11 + emit) / meld sweep.
    _wipe_bench_cache()
    bind_prof, conjure_prof, meld_prof = (
        cProfile.Profile(), cProfile.Profile(), cProfile.Profile(),
    )
    cold = run_cycle(
        caching_enabled=True,
        bind_profiler=bind_prof,
        conjure_profiler=conjure_prof,
        meld_profiler=meld_prof,
    )
    _dump_stage_profile("COLD bind (29 binds)", bind_prof, report_stream)
    _dump_stage_profile("COLD conjure (phases 1-11 + emit)", conjure_prof, report_stream)
    _dump_stage_profile("COLD first-meld sweep", meld_prof, report_stream)

    # Warm posture: cache now seeded by the cold cycle above.
    bind_prof, conjure_prof, meld_prof = (
        cProfile.Profile(), cProfile.Profile(), cProfile.Profile(),
    )
    warm = run_cycle(
        caching_enabled=True,
        bind_profiler=bind_prof,
        conjure_profiler=conjure_prof,
        meld_profiler=meld_prof,
    )
    if not warm.cache_full_hit_possible:
        raise AssertionError("Warm profile cycle was not a cache full-hit.")
    _dump_stage_profile("WARM bind (29 binds)", bind_prof, report_stream)
    _dump_stage_profile("WARM conjure (full-hit, phases 1-7)", conjure_prof, report_stream)
    _dump_stage_profile("WARM first-meld sweep (lazy hydration)", meld_prof, report_stream)

    report_stream.write("=" * 78 + "\n")
    report_stream.write("STAGE WALL TIMES UNDER PROFILER (inflated; ranking only)\n")
    report_stream.write("=" * 78 + "\n")
    for label, cycle in (("cold", cold), ("warm", warm)):
        report_stream.write(
            f"  {label}: bind {cycle.bind_ns / 1e6:.3f} ms | "
            f"conjure {cycle.conjure_ns / 1e6:.3f} ms | "
            f"first-meld {cycle.first_meld_ns / 1e6:.3f} ms\n"
        )

    report_text = report_stream.getvalue()
    output_path = Path(__file__).resolve().parent / "bind_conjure_cycle_profile.txt"
    output_path.write_text(report_text, encoding="utf-8")
    print(report_text[:12000])
    print(f"\nFull report written to: {output_path}")


# ======================================================================================
# Entry point
# ======================================================================================

def main() -> None:
    """
    Run the wall-timing suite, and the cProfile suite when --profile is set.
    """
    try:
        if "--profile" in sys.argv:
            run_profile_suite()
        else:
            run_timing_suite(REPEATS)
            print("Run with --profile for per-stage cProfile attribution.")
    finally:
        if not KEEP_CACHE:
            _wipe_bench_cache()


if __name__ == "__main__":
    main()
