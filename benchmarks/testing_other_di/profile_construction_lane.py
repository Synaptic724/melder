"""
Construction-lane cProfile attribution (meld#1 executor body).

Purpose:
    Decompose the ~2.7-3.1us meld#1 construction lane (76% of per-cycle meld
    cost in the contention harness) into ranked function costs so the
    shared-touch trim candidates can be ordered by evidence:
      (1) step_spells reads / shared Spell refcount traffic
      (2) creations dict + lock traffic for non-many existences
      (3) registration blocks for disposal-tracked instances
      (4) generic `_construct_spell_instance` helper path

Design:
    - Single-threaded by design: cProfile ranks the t1 instruction path; the
      t3/t5 inflation mechanism (refcount/cache-line ping-pong) is NOT
      visible to a function profiler and is measured separately by the
      contention harness micro mode.
    - Every cycle is create_lesser -> meld outer (#1) -> enter spellspace ->
      meld request (#1) -> exit -> cleanup. No repeat melds, so every meld
      profiled is a construction meld; door hits contribute ~0.3us/meld and
      are visible separately as the conduit/spellspace meld frames.
    - Re-execs under PYTHON_GIL=1 (profiler convention shared with
      profile_bind_conjure_cycle.py): relative attribution is the
      deliverable; absolute numbers are profiler-inflated.

Usage:
    .venv_new\\Scripts\\python.exe benchmarks\\testing_other_di\\profile_construction_lane.py

Env knobs:
    BENCH_CONSTRUCTION_CYCLES   profiled cycles (default 20000)
    BENCH_CONSTRUCTION_WARMUP   unprofiled warmup cycles (default 2000)
"""

import cProfile
import io
import os
import pstats
import sys
import time
from pathlib import Path
from typing import Any, Dict


def _ensure_local_paths() -> None:
    """Ensure local source and benchmark helper paths are importable."""
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parents[1]
    src_dir = project_root / "src"
    for path in (src_dir, current_dir):
        path_as_str = str(path)
        if path_as_str not in sys.path:
            sys.path.insert(0, path_as_str)


def _ensure_gil_enabled_interpreter() -> None:
    """Re-exec under PYTHON_GIL=1 (profiler accuracy convention)."""
    is_gil_enabled_probe = getattr(sys, "_is_gil_enabled", None)
    if is_gil_enabled_probe is None or is_gil_enabled_probe():
        return
    environment = dict(os.environ)
    environment["PYTHON_GIL"] = "1"
    os.execve(sys.executable, [sys.executable, *sys.argv], environment)


_ensure_gil_enabled_interpreter()
_ensure_local_paths()

import melder_gauntlet_support as _support  # noqa: E402

FRAME_NAME = "bench-construction-lane"
CONDUIT_NAME = "bench-construction-lane"
CYCLES = max(1, int(os.environ.get("BENCH_CONSTRUCTION_CYCLES", "20000")))
WARMUP = max(0, int(os.environ.get("BENCH_CONSTRUCTION_WARMUP", "2000")))


def _reset_runtime() -> None:
    """Reset the Aether singleton runtime."""
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
    """Map one gauntlet class to its gauntlet existence (same as the suite)."""
    from melder.aether.spellbook.existence.existence import Existence

    if cls in set(_support.SINGLETON_TYPES):
        return Existence.unique
    if cls in set(_support.OUTER_SCOPED_TYPES):
        return Existence.unique_per_conduit
    if cls in set(_support.REQUEST_SCOPED_TYPES):
        return Existence.unique_per_spell_space
    return Existence.many


def _build_root() -> Any:
    """Bind the gauntlet graph and conjure one root conduit (caching off)."""
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
    root = spellbook.conjure(name=CONDUIT_NAME, dynamic=False)
    return root, spell_ids


def _run_cycles(root: Any, outer_id: str, request_id: str, count: int) -> int:
    """
    Run `count` construction-only scope cycles; return total wall ns.

    Every meld is a meld#1 (pool recycle resets storage), so the profiled
    body is the construction lane plus create/cleanup machinery, separable
    by frame name in the report.
    """
    total_t0 = time.perf_counter_ns()
    for _ in range(count):
        lesser = root.create_lesser_conduit()
        try:
            lesser.meld(spell=outer_id)
            space_cm = lesser.enter_spellspace()
            space = space_cm.__enter__()
            try:
                space.meld(spell=request_id)
            finally:
                space_cm.__exit__(None, None, None)
        finally:
            lesser.cleanup()
    return time.perf_counter_ns() - total_t0


def main() -> None:
    """Warm up, profile the cycle loop, and print ranked attribution."""
    gil_probe = getattr(sys, "_is_gil_enabled", None)
    print("=" * 78)
    print("CONSTRUCTION LANE PROFILE (meld#1 executor body, single thread)")
    print(
        f"classes={len(_support.ALL_CLASSES)}  cycles={CYCLES}  "
        f"warmup={WARMUP}  gil_enabled={None if gil_probe is None else gil_probe()}"
    )
    print("=" * 78)

    root, spell_ids = _build_root()
    outer_id = spell_ids[_support.OUTER_SCOPED_TYPES[0]]
    request_id = spell_ids[_support.REQUEST_SCOPED_TYPES[0]]

    if WARMUP:
        _run_cycles(root, outer_id, request_id, WARMUP)

    profiler = cProfile.Profile()
    profiler.activate()
    wall_ns = _run_cycles(root, outer_id, request_id, CYCLES)
    profiler.disable()

    per_cycle_us = wall_ns / CYCLES / 1e3
    report = io.StringIO()
    stats = pstats.Stats(profiler, stream=report)
    stats.strip_dirs()
    report.write(f"per-cycle wall under profiler: {per_cycle_us:.2f}us\n")
    report.write("=" * 78 + "\nTOP 50 BY TOTTIME (self time)\n" + "=" * 78 + "\n")
    stats.sort_stats("tottime").print_stats(50)
    report.write("=" * 78 + "\nLANE ATTRIBUTION\n" + "=" * 78 + "\n")
    stats.sort_stats("cumulative")
    stats.print_stats("melder_gauntlet_support")
    stats.print_stats("_construct_spell_instance|_register_spell_instance|_raise_meld")
    stats.print_stats("acquire|release|RLock|__enter__|__exit__")
    stats.print_stats("conduit_meld|spellspace_meld|meld\\.py")
    stats.print_stats("creation_context|creations")
    stats.print_stats("create_lesser|cleanup|reset_for_pool|ward")

    text = report.getvalue()
    output_path = Path(__file__).resolve().parent / "construction_lane_profile.txt"
    output_path.write_text(text, encoding="utf-8")
    print(text[:9000])
    print(f"\nFull report written to: {output_path}")

    root.cleanup()
    _reset_runtime()


if __name__ == "__main__":
    main()
