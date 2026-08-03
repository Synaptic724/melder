import gc
import statistics
import time
from dataclasses import dataclass
from typing import Callable, List


FIELD_COUNT: int = 20
RUNS: int = 1_000
REPEATS: int = 20


@dataclass(frozen=True)
class _BenchmarkResult:
    """
    Hold one guard-vs-direct clear measurement result.

    Contract:
        - `durations_ns` stores one full-repeat elapsed duration per scenario.
        - `ns_per_run` reports mean nanoseconds per 1000-run scenario.
        - `ns_per_clear_site` reports mean nanoseconds per individual clear site.
    """

    label: str
    durations_ns: tuple[int, ...]

    @property
    def mean_ns(self) -> float:
        """Return mean elapsed nanoseconds across repeats."""
        return statistics.mean(self.durations_ns)

    @property
    def min_ns(self) -> int:
        """Return the fastest repeat duration."""
        return min(self.durations_ns)

    @property
    def max_ns(self) -> int:
        """Return the slowest repeat duration."""
        return max(self.durations_ns)

    @property
    def ns_per_run(self) -> float:
        """Return mean nanoseconds spent per 1000-run scenario."""
        return self.mean_ns / float(RUNS)

    @property
    def ns_per_clear_site(self) -> float:
        """Return mean nanoseconds spent per individual clear site."""
        return self.mean_ns / float(RUNS * FIELD_COUNT)


def _build_empty_lists() -> List[list[object]]:
    """
    Build the 20 empty built-in list containers for one benchmark repeat.
    """

    return [[] for _ in range(FIELD_COUNT)]


def _run_guarded_clear(containers: List[list[object]]) -> None:
    """
    Execute 20 guarded clear checks over empty built-in lists for 1000 runs.
    """

    for _ in range(RUNS):
        for container in containers:
            if container:
                container.clear()


def _run_direct_clear(containers: List[list[object]]) -> None:
    """
    Execute 20 unconditional clear calls over empty built-in lists for 1000 runs.
    """

    for _ in range(RUNS):
        for container in containers:
            container.clear()


def _measure(label: str, runner: Callable[[List[list[object]]], None]) -> _BenchmarkResult:
    """
    Measure one empty-list cleanup scenario across multiple repeats.

    Contract:
        - Construction happens outside the timed section.
        - Cyclic GC is disabled during the timed section to reduce noise.
        - Each repeat starts from 20 fresh empty lists.
    """

    durations: list[int] = []
    gc_was_enabled = gc.isenabled()
    try:
        for _ in range(REPEATS):
            containers = _build_empty_lists()
            gc.collect()
            gc.deactivate()
            start_ns = time.perf_counter_ns()
            runner(containers)
            elapsed_ns = time.perf_counter_ns() - start_ns
            durations.append(elapsed_ns)
            if gc_was_enabled:
                gc.activate()
    finally:
        if gc_was_enabled and not gc.isenabled():
            gc.activate()

    return _BenchmarkResult(label=label, durations_ns=tuple(durations))


def _print_summary(
        guarded_result: _BenchmarkResult,
        direct_result: _BenchmarkResult,
) -> None:
    """
    Print one compact benchmark table for the empty-list clear scenarios.
    """

    print("empty built-in list cleanup benchmark")
    print(f"field_count={FIELD_COUNT} runs={RUNS} repeats={REPEATS}")
    print(
        f"{'scenario':<18} {'mean(ms)':>12} {'ns/run':>12} "
        f"{'ns/site':>12} {'min(ms)':>12} {'max(ms)':>12}"
    )
    print("-" * 84)
    for result in (guarded_result, direct_result):
        print(
            f"{result.label:<18} "
            f"{result.mean_ns / 1_000_000.0:>12.3f} "
            f"{result.ns_per_run:>12.1f} "
            f"{result.ns_per_clear_site:>12.3f} "
            f"{result.min_ns / 1_000_000.0:>12.3f} "
            f"{result.max_ns / 1_000_000.0:>12.3f}"
        )
    ratio = direct_result.mean_ns / guarded_result.mean_ns
    print(f"direct_over_guard_ratio={ratio:.3f}x")


def test_empty_clear_guard_experiment() -> None:
    """
    Measure `if container: clear()` versus unconditional `clear()` on empty lists.

    Purpose:
        Give one repo-local measurement for the exact cleanup question raised in
        this lane: whether we should branch before clearing always-live built-in
        containers that are already empty.

    Contract:
        - Uses 20 empty built-in lists.
        - Runs each scenario 1000 times per repeat.
        - Prints the timing table for manual inspection.
        - Asserts only the semantic postcondition that every list remains empty.
    """

    guarded_result = _measure("guard_then_clear", _run_guarded_clear)
    direct_result = _measure("clear_directly", _run_direct_clear)
    _print_summary(guarded_result, direct_result)

    guarded_lists = _build_empty_lists()
    direct_lists = _build_empty_lists()
    _run_guarded_clear(guarded_lists)
    _run_direct_clear(direct_lists)

    assert all(len(container) == 0 for container in guarded_lists)
    assert all(len(container) == 0 for container in direct_lists)
