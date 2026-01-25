from __future__ import annotations

import cProfile
import gc
import io
import pstats
import statistics
import time
import tracemalloc
from contextlib import contextmanager
from typing import Callable, Iterable

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from melder.utilities.synchronization.phase_scheduler import PhaseScheduler
from tests.mocks.spellbook.deep_layers import Depth9Root, get_depth_9_classes


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
    """
    Purpose:
        Ensure integration tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


# Tune profiling intensity here for local runs.
PROFILE_RUN_HEAVY = True
PROFILE_RUN_CPROFILE = True
PROFILE_RUN_TRACEMALLOC = True
PROFILE_RUN_GC_DELTA = True
PROFILE_RECORD_PHASE_TIMINGS = True
PROFILE_TOP = 30
PROFILE_TRACE_TOP = 20
PROFILE_TRACE_FRAMES = 1
PROFILE_CYCLES = 1
PROFILE_WORKERS: int | None = 1


def _ms(seconds: float) -> float:
    return seconds * 1000.0


def _us(seconds: float) -> float:
    return seconds * 1_000_000.0


def _profile_enabled(flag: bool) -> bool:
    return PROFILE_RUN_HEAVY or flag


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if pct <= 0:
        return ordered[0]
    if pct >= 100:
        return ordered[-1]
    idx = int(round((pct / 100.0) * (len(ordered) - 1)))
    return ordered[idx]


def _summarize_samples(label: str, samples_s: Iterable[float]) -> None:
    samples = list(samples_s)
    if not samples:
        print(f"{label}: no samples")
        return
    avg_s = statistics.mean(samples)
    p50 = _percentile(samples, 50)
    p95 = _percentile(samples, 95)
    p99 = _percentile(samples, 99)
    print(
        f"{label} (ms): avg={_ms(avg_s):.3f}, "
        f"p50={_ms(p50):.3f}, p95={_ms(p95):.3f}, p99={_ms(p99):.3f}"
    )


def _bind_classes(
    spellbook: Spellbook,
    classes: tuple[type, ...],
    *,
    existence: Existence,
) -> dict[type, str]:
    spell_ids: dict[type, str] = {}
    for cls in classes:
        spell_ids[cls] = spellbook.bind(
            spell=cls,
            existence=existence,
            permissions="create",
        )
    return spell_ids


def _configure_scheduler(spellbook: Spellbook) -> None:
    if PROFILE_WORKERS is None:
        return
    cfg = spellbook.get_configuration()
    cfg.set_property("phase_scheduler_workers_per_spellbook", PROFILE_WORKERS)


def _build_depth9_spellbook(frame_name: str) -> tuple[Spellbook, str]:
    spellbook = Spellbook(aetheric_frame=frame_name)
    _configure_scheduler(spellbook)
    spell_ids = _bind_classes(
        spellbook,
        get_depth_9_classes(),
        existence=Existence.unique,
    )
    return spellbook, spell_ids[Depth9Root]


@contextmanager
def _phase_timing_recorder() -> Iterable[list[tuple[str, float]]]:
    timings: list[tuple[str, float]] = []
    original = PhaseScheduler._run_single_phase

    def _wrapped(self, phase_name, factory):  # type: ignore[no-untyped-def]
        start = time.perf_counter()
        try:
            return original(self, phase_name, factory)
        finally:
            timings.append((phase_name, time.perf_counter() - start))

    PhaseScheduler._run_single_phase = _wrapped  # type: ignore[assignment]
    try:
        yield timings
    finally:
        PhaseScheduler._run_single_phase = original  # type: ignore[assignment]


def _print_profile(label: str, profiler: cProfile.Profile, *, sort: str, top: int) -> None:
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream).strip_dirs().sort_stats(sort)
    stats.print_stats(top)
    print(f"[PROFILE] {label} (sort={sort}, top={top})")
    print(stream.getvalue())


def _profile_call(
    label: str,
    fn: Callable[[], None],
    *,
    sort: str = "cumtime",
    top: int = 40,
) -> None:
    profiler = cProfile.Profile()
    profiler.runcall(fn)
    _print_profile(label, profiler, sort=sort, top=top)


def _trace_alloc(label: str, fn: Callable[[], None], *, top: int = 20) -> None:
    tracemalloc.start(PROFILE_TRACE_FRAMES)
    before = tracemalloc.take_snapshot()
    fn()
    after = tracemalloc.take_snapshot()
    tracemalloc.stop()

    stats = after.compare_to(before, "lineno")
    print(f"[TRACEMALLOC] {label} (top={top})")
    for stat in stats[:top]:
        location = stat.traceback.format()[-1].strip()
        size_kb = stat.size_diff / 1024.0
        print(f"{size_kb:8.1f} KiB {stat.count_diff:7d} {location}")


def _gc_delta(label: str, fn: Callable[[], None]) -> None:
    gc.collect()
    before_counts = gc.get_count()
    before_stats = gc.get_stats() if hasattr(gc, "get_stats") else None
    fn()
    gc.collect()
    after_counts = gc.get_count()
    after_stats = gc.get_stats() if hasattr(gc, "get_stats") else None

    print(f"[GC] {label} counts before={before_counts} after={after_counts}")
    if before_stats is None or after_stats is None:
        return
    for idx, (before, after) in enumerate(zip(before_stats, after_stats)):
        collections = after["collections"] - before["collections"]
        collected = after["collected"] - before["collected"]
        print(f"[GC] gen{idx} collections={collections} collected={collected}")


def test_profile_conjure_depth9_hotpaths() -> None:
    """
    Purpose:
        Profile conjure for depth-9 graph and capture phase timings.
    Notes:
        - Run with: pytest -s -k test_profile_conjure_depth9_hotpaths
        - Edit PROFILE_* constants in this file to tune intensity.
    """
    top = PROFILE_TOP

    spellbook, _ = _build_depth9_spellbook("profile-conjure-depth9")
    if PROFILE_RECORD_PHASE_TIMINGS:
        with _phase_timing_recorder() as timings:
            t0 = time.perf_counter()
            conduit = spellbook.conjure(name="profile-conjure-depth9", automatic=True)
            conjure_s = time.perf_counter() - t0

        print(f"Conjure total (ms): {_ms(conjure_s):.3f}")
        for phase_name, elapsed in timings:
            print(f"Phase {phase_name} (ms): {_ms(elapsed):.3f}")
    else:
        t0 = time.perf_counter()
        conduit = spellbook.conjure(name="profile-conjure-depth9", automatic=True)
        conjure_s = time.perf_counter() - t0
        print(f"Conjure total (ms): {_ms(conjure_s):.3f}")

    conduit.cleanup()

    def _conjure_only_profile() -> None:
        sb, _ = _build_depth9_spellbook("profile-conjure-depth9-cprofile")
        t0_inner = time.perf_counter()
        conduit_inner = sb.conjure(name="profile-conjure-depth9-cprofile", automatic=True)
        elapsed = time.perf_counter() - t0_inner
        print(f"Conjure (cprofile target) (ms): {_ms(elapsed):.3f}")
        conduit_inner.cleanup()

    if not (
        PROFILE_RUN_HEAVY
        or PROFILE_RUN_CPROFILE
        or PROFILE_RUN_TRACEMALLOC
        or PROFILE_RUN_GC_DELTA
    ):
        return

    if _profile_enabled(PROFILE_RUN_CPROFILE):
        _profile_call("conjure depth9", _conjure_only_profile, sort="cumtime", top=top)
    if _profile_enabled(PROFILE_RUN_TRACEMALLOC):
        _trace_alloc("conjure depth9", _conjure_only_profile, top=PROFILE_TRACE_TOP)
    if _profile_enabled(PROFILE_RUN_GC_DELTA):
        _gc_delta("conjure depth9", _conjure_only_profile)


def test_profile_meld_depth9_hotpaths() -> None:
    """
    Purpose:
        Profile cold and warm meld for depth-9 graph and capture hotpaths.
    Notes:
        - Run with: pytest -s -k test_profile_meld_depth9_hotpaths
        - Edit PROFILE_* constants in this file to tune intensity.
    """
    top = PROFILE_TOP

    spellbook, root_id = _build_depth9_spellbook("profile-meld-depth9")
    conduit = spellbook.conjure(name="profile-meld-depth9", automatic=True)
    try:
        t0 = time.perf_counter()
        root1 = conduit.meld(spell=root_id)
        cold_s = time.perf_counter() - t0
        assert isinstance(root1, Depth9Root)

        t0 = time.perf_counter()
        root2 = conduit.meld(spell=root_id)
        warm_s = time.perf_counter() - t0
        assert root1 is root2

        print(
            "Meld depth9 (ms): "
            f"cold={_ms(cold_s):.3f}, warm={_us(warm_s):.2f}us"
        )

        if not (
            PROFILE_RUN_HEAVY
            or PROFILE_RUN_CPROFILE
            or PROFILE_RUN_TRACEMALLOC
            or PROFILE_RUN_GC_DELTA
        ):
            return

        def _meld_cold_profile() -> None:
            sb, root = _build_depth9_spellbook("profile-meld-depth9-cold")
            cd = sb.conjure(name="profile-meld-depth9-cold", automatic=True)
            try:
                _ = cd.meld(spell=root)
            finally:
                cd.cleanup()

        def _meld_warm_profile() -> None:
            sb, root = _build_depth9_spellbook("profile-meld-depth9-warm")
            cd = sb.conjure(name="profile-meld-depth9-warm", automatic=True)
            try:
                _ = cd.meld(spell=root)
                _ = cd.meld(spell=root)
            finally:
                cd.cleanup()

        if _profile_enabled(PROFILE_RUN_CPROFILE):
            _profile_call("meld depth9 cold", _meld_cold_profile, sort="cumtime", top=top)
            _profile_call("meld depth9 warm", _meld_warm_profile, sort="cumtime", top=top)
        if _profile_enabled(PROFILE_RUN_TRACEMALLOC):
            _trace_alloc("meld depth9 cold", _meld_cold_profile, top=PROFILE_TRACE_TOP)
        if _profile_enabled(PROFILE_RUN_GC_DELTA):
            _gc_delta("meld depth9 cold", _meld_cold_profile)
    finally:
        conduit.cleanup()


def test_profile_cycle_conjure_meld_cleanup_depth9() -> None:
    """
    Purpose:
        Cycle test: conjure -> meld -> cleanup repeated to capture avg/p95.
    Notes:
        - Run with: pytest -s -k test_profile_cycle_conjure_meld_cleanup_depth9
        - Edit PROFILE_* constants in this file to tune intensity.
    """
    cycles = PROFILE_CYCLES
    if cycles <= 0:
        return

    conjure_times: list[float] = []
    meld_times: list[float] = []
    cleanup_times: list[float] = []

    for i in range(cycles):
        spellbook, root_id = _build_depth9_spellbook(f"profile-cycle-depth9-{i}")
        t0 = time.perf_counter()
        conduit = spellbook.conjure(name=f"profile-cycle-depth9-{i}", automatic=True)
        conjure_times.append(time.perf_counter() - t0)
        try:
            t0 = time.perf_counter()
            _ = conduit.meld(spell=root_id)
            meld_times.append(time.perf_counter() - t0)
        finally:
            t0 = time.perf_counter()
            conduit.cleanup()
            cleanup_times.append(time.perf_counter() - t0)

    _summarize_samples("cycle conjure", conjure_times)
    _summarize_samples("cycle meld", meld_times)
    _summarize_samples("cycle cleanup", cleanup_times)
