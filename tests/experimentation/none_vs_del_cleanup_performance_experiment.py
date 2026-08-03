import gc
import statistics
import time
from dataclasses import dataclass
from typing import Callable, Type


FIELD_COUNT: int = 100
RUNS: int = 10_000
REPEATS: int = 5
FIELD_NAMES: tuple[str, ...] = tuple(
    f"field_{index}" for index in range(FIELD_COUNT)
)


@dataclass(frozen=True)
class _CleanupMeasurement:
    """
    Hold one cleanup benchmark summary.

    Contract:
        - `durations_ns` stores one elapsed cleanup duration per repeat.
        - `ns_per_cleanup` is derived from the mean repeat duration.
        - `relative_to_none` is filled only after both strategies are measured.
    """

    label: str
    runs: int
    durations_ns: tuple[int, ...]
    relative_to_none: float | None = None

    @property
    def mean_ns(self) -> float:
        """Return the mean elapsed time across repeats."""
        return statistics.mean(self.durations_ns)

    @property
    def min_ns(self) -> int:
        """Return the fastest repeat."""
        return min(self.durations_ns)

    @property
    def max_ns(self) -> int:
        """Return the slowest repeat."""
        return max(self.durations_ns)

    @property
    def ns_per_cleanup(self) -> float:
        """Return the mean nanoseconds spent per cleanup call."""
        return self.mean_ns / float(self.runs)


class _NoneCleanupProbe:
    """
    Slotted probe that nulls 100 list fields during cleanup.

    This is an experimentation bench, not production runtime code.
    """

    __slots__ = ("_cleaned",) + FIELD_NAMES

    def __init__(self) -> None:
        self._cleaned = False
        for field_name in FIELD_NAMES:
            setattr(self, field_name, [])

    def cleanup(self) -> None:
        if self._cleaned:
            return
        for field_name in FIELD_NAMES:
            setattr(self, field_name, None)
        self._cleaned = True


class _DelCleanupProbe:
    """
    Slotted probe that deletes 100 list fields during cleanup.

    This is an experimentation bench, not production runtime code.
    """

    __slots__ = ("_cleaned",) + FIELD_NAMES

    def __init__(self) -> None:
        self._cleaned = False
        for field_name in FIELD_NAMES:
            setattr(self, field_name, [])

    def cleanup(self) -> None:
        if self._cleaned:
            return
        for field_name in FIELD_NAMES:
            delattr(self, field_name)
        self._cleaned = True


def _build_batch(probe_type: Type[_NoneCleanupProbe] | Type[_DelCleanupProbe]) -> list[object]:
    """
    Build one batch of fresh probe objects for one timed repeat.
    """

    return [probe_type() for _ in range(RUNS)]


def _measure_cleanup(
    label: str,
    probe_type: Type[_NoneCleanupProbe] | Type[_DelCleanupProbe],
) -> _CleanupMeasurement:
    """
    Time cleanup across one full batch for several repeats.

    Contract:
        - Measures cleanup only; object construction happens before the timer.
        - Disables cyclic GC during the timed section to reduce noise.
        - Forces one collection before each repeat to normalize leftover state.
    """

    durations: list[int] = []
    gc_was_enabled = gc.isenabled()

    try:
        for _ in range(REPEATS):
            batch = _build_batch(probe_type)
            gc.collect()
            gc.disable()
            start_ns = time.perf_counter_ns()
            for probe in batch:
                probe.cleanup()
            elapsed_ns = time.perf_counter_ns() - start_ns
            durations.append(elapsed_ns)
            if gc_was_enabled:
                gc.activate()
    finally:
        if gc_was_enabled and not gc.isenabled():
            gc.activate()

    return _CleanupMeasurement(
        label=label,
        runs=RUNS,
        durations_ns=tuple(durations),
    )


def _print_summary(
    none_result: _CleanupMeasurement,
    del_result: _CleanupMeasurement,
) -> None:
    """
    Print one compact comparison table.
    """

    rows = (
        _CleanupMeasurement(
            label=none_result.label,
            runs=none_result.runs,
            durations_ns=none_result.durations_ns,
            relative_to_none=1.0,
        ),
        _CleanupMeasurement(
            label=del_result.label,
            runs=del_result.runs,
            durations_ns=del_result.durations_ns,
            relative_to_none=del_result.mean_ns / none_result.mean_ns,
        ),
    )

    print("cleanup benchmark: 100 slotted list fields, cleanup only")
    print(f"runs={RUNS} repeats={REPEATS}")
    print(
        f"{'strategy':<16} {'mean(ms)':>12} {'ns/cleanup':>14} "
        f"{'min(ms)':>12} {'max(ms)':>12} {'vs_none':>10}"
    )
    print("-" * 82)
    for row in rows:
        print(
            f"{row.label:<16} "
            f"{row.mean_ns / 1_000_000.0:>12.3f} "
            f"{row.ns_per_cleanup:>14.1f} "
            f"{row.min_ns / 1_000_000.0:>12.3f} "
            f"{row.max_ns / 1_000_000.0:>12.3f} "
            f"{row.relative_to_none:>10.3f}x"
        )


def main() -> None:
    """
    Run the cleanup comparison benchmark.
    """

    none_result = _measure_cleanup("set_none", _NoneCleanupProbe)
    del_result = _measure_cleanup("delete_attr", _DelCleanupProbe)
    _print_summary(none_result, del_result)


if __name__ == "__main__":
    main()
