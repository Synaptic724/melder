"""
Pytest wrapper for the bind -> conjure -> resolution cycle benchmark.

Purpose:
    Keep the cycle harness honest in CI-ish runs:
      - every stage actually executes and reports non-zero wall time,
      - a cold conjure with caching enabled emits the bundle file,
      - warm repeats genuinely classify as cache full-hits (fingerprint
        stability across same-process cycles),
      - the timing table prints so a manual run doubles as a benchmark.

Contract:
    - Small repeat counts: this is a structural smoke + a printable
      benchmark, not a statistics farm (use the profile script for that).
    - No latency assertions between postures: wall-clock comparisons are
      machine/load dependent and would flake. Posture deltas are printed,
      never asserted.
"""

import sys
from pathlib import Path

import pytest


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

import profile_bind_conjure_cycle as _cycle  # noqa: E402


@pytest.fixture(autouse=True)
def _bench_cache_isolation():
    """
    Guarantee a wiped bench cache before and after every test.
    """
    _cycle._wipe_bench_cache()
    yield
    _cycle._wipe_bench_cache()


@pytest.mark.timeout(600)
def test_cycle_disabled_runs_all_stages() -> None:
    """
    Caching-disabled cycle executes bind/conjure/meld with real wall time.
    """
    timings = _cycle.run_cycle(caching_enabled=False)

    assert len(timings.per_bind_ns) == len(_cycle._support.ALL_CLASSES)
    assert timings.bind_ns > 0
    assert timings.conjure_ns > 0
    assert timings.first_meld_ns > 0
    assert timings.setup_ns == timings.bind_ns + timings.conjure_ns
    assert timings.full_cycle_ns == timings.setup_ns + timings.first_meld_ns
    # Caching disabled must not leave a bundle behind.
    assert timings.cache_bundle_exists is False
    assert not _cycle._bench_cache_dir().exists()


@pytest.mark.timeout(600)
def test_cycle_cold_emits_bundle_then_warm_full_hits() -> None:
    """
    Cold cycle stages + emits the bundle; the next cycle is a full-hit.
    """
    cold = _cycle.run_cycle(caching_enabled=True)
    assert cold.cache_bundle_exists is True
    # First-ever cycle cannot be a full hit (cache was empty at bind time).
    assert cold.cache_full_hit_possible is False

    warm = _cycle.run_cycle(caching_enabled=True)
    # Same classes, same frame/conduit names, fresh Aether: the fingerprints
    # must land on the cached ids, otherwise the warm lane silently rots.
    assert warm.cache_full_hit_possible is True
    assert warm.cache_bundle_exists is True
    assert warm.first_meld_ns > 0


@pytest.mark.timeout(1200)
def test_cycle_benchmark_prints_timing_table() -> None:
    """
    Run the full three-posture suite with small repeats and print the table.
    """
    results = _cycle.run_timing_suite(repeats=3)

    assert set(results) == {"disabled", "cold", "warm"}
    for posture, result in results.items():
        assert len(result.cycles) == 3, posture
        for cycle in result.cycles:
            assert cycle.setup_ns > 0, posture
    # Warm repeats must all have been classifiable as full hits (run_posture
    # raises otherwise, but assert again so the contract is visible here).
    for cycle in results["warm"].cycles:
        assert cycle.cache_full_hit_possible is True


if __name__ == "__main__":
    test_cycle_disabled_runs_all_stages()
    test_cycle_cold_emits_bundle_then_warm_full_hits()
    test_cycle_benchmark_prints_timing_table()
    print("OK_BIND_CONJURE_CYCLE_BENCHMARK")
