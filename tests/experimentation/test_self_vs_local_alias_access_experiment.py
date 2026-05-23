import time
from typing import Callable, ClassVar, Dict, List, Tuple


_REUSE_COUNTS: Tuple[int, ...] = (1, 2, 3, 4, 5)
_INNER_LOOPS: int = 1000
_OUTER_RUNS: int = 1000
_REPEATS: int = 9


def _build_generated_methods() -> Dict[str, Callable[..., int]]:
    """
    Build direct-self and local-alias methods for reuse counts 1 through 5.

    Contract:
        - Direct methods read `self._value` exactly `N` times per loop body.
        - Alias methods bind `value = self._value` once per loop body and then
          reuse `value` exactly `N` times.
        - Every generated method executes exactly `_INNER_LOOPS` loop
          iterations and writes the final total back to `_sink`.

    Returns:
        Dict[str, Callable[..., int]]:
            Generated benchmark methods keyed by method name.
    """
    namespace: Dict[str, Callable[..., int]] = {}
    parts: List[str] = []

    for reuse_count in _REUSE_COUNTS:
        direct_lines: List[str] = [
            f"def run_direct_{reuse_count}(self) -> int:",
            f'    """Use self._value directly {reuse_count} times per loop."""',
            "    total = 0",
            f"    for _ in range({_INNER_LOOPS}):",
        ]
        for _ in range(reuse_count):
            direct_lines.append("        total += self._value")
        direct_lines.extend(
            [
                "    self._sink = total",
                "    return total",
            ]
        )

        alias_lines: List[str] = [
            f"def run_alias_{reuse_count}(self) -> int:",
            f'    """Bind value = self._value, then reuse it {reuse_count} times per loop."""',
            "    total = 0",
            f"    for _ in range({_INNER_LOOPS}):",
            "        value = self._value",
        ]
        for _ in range(reuse_count):
            alias_lines.append("        total += value")
        alias_lines.extend(
            [
                "    self._sink = total",
                "    return total",
            ]
        )

        parts.append("\n".join(direct_lines))
        parts.append("\n".join(alias_lines))

    exec("\n\n".join(parts), {}, namespace)
    return namespace


class _AttributeReuseProbe:
    """
    Probe object for direct-self versus local-alias reuse microbenchmarks.

    Purpose:
        Hold one stable attribute and expose generated methods that differ only
        in whether they re-read through `self` or reuse a local alias.

    Contract:
        - `_value` stays constant for the benchmark lifetime.
        - `_sink` captures the final total so the work is observed.
        - Generated methods are attached to the class after definition.
    """

    __slots__ = [
        "_sink",
        "_value",
    ]

    def __init__(self) -> None:
        """
        Initialize the probe state.

        Returns:
            None.
        """
        self._value: int = 1
        self._sink: int = 0


for _method_name, _method in _build_generated_methods().items():
    setattr(_AttributeReuseProbe, _method_name, _method)


def _measure_variant(
        label: str,
        method: Callable[[], int],
        expected_total: int,
) -> Dict[str, float]:
    """
    Measure one generated reuse variant over repeated timed passes.

    Args:
        label:
            Human-readable benchmark label.
        method:
            Bound method to execute.
        expected_total:
            Expected accumulated result used as a correctness guard.

    Returns:
        Dict[str, float]:
            Timing summary with min/median wall-clock values.
    """
    samples_ns: List[int] = []
    first_result = method()
    if first_result != expected_total:
        raise RuntimeError(
            "Unexpected result for {0}: {1} != {2}".format(
                label,
                first_result,
                expected_total,
            )
        )
    for _ in range(_REPEATS):
        start_ns = time.perf_counter_ns()
        for _ in range(_OUTER_RUNS):
            result = method()
        elapsed_ns = time.perf_counter_ns() - start_ns
        if result != expected_total:
            raise RuntimeError(
                "Unexpected repeated result for {0}: {1} != {2}".format(
                    label,
                    result,
                    expected_total,
                )
            )
        samples_ns.append(elapsed_ns)

    sorted_samples = sorted(samples_ns)
    min_ns = float(sorted_samples[0])
    median_ns = float(sorted_samples[len(sorted_samples) // 2])
    return {
        "label": label,
        "min_ns": min_ns,
        "median_ns": median_ns,
        "ns_per_call_min": min_ns / float(_OUTER_RUNS),
    }


def test_self_vs_local_alias_access_experiment() -> None:
    """
    Measure direct-self versus local-alias access at reuse counts 1 through 5.

    Contract:
        - For each reuse count `N`, direct-self reads `self._value` `N` times.
        - For each reuse count `N`, alias mode binds `value = self._value`
          once and reuses `value` `N` times.
        - Each generated method runs `_INNER_LOOPS` loop iterations.
        - Each timed sample calls the method `_OUTER_RUNS` times.
        - This is an experiment, so it prints results and does not assert on
          timing ratios.
    """
    probe = _AttributeReuseProbe()
    results: List[Dict[str, float]] = []

    for reuse_count in _REUSE_COUNTS:
        expected_total = _INNER_LOOPS * reuse_count
        direct_method = getattr(probe, f"run_direct_{reuse_count}")
        alias_method = getattr(probe, f"run_alias_{reuse_count}")
        results.append(
            _measure_variant(
                f"direct x{reuse_count}",
                direct_method,
                expected_total,
            )
        )
        results.append(
            _measure_variant(
                f"alias x{reuse_count}",
                alias_method,
                expected_total,
            )
        )

    print("self vs local alias attribute access experiment")
    print(
        "outer runs={0}, inner loops={1}, repeats={2}".format(
            _OUTER_RUNS,
            _INNER_LOOPS,
            _REPEATS,
        )
    )
    print()
    print(
        "{0:<16} {1:>12} {2:>14} {3:>16}".format(
            "variant",
            "min(ms)",
            "median(ms)",
            "ns/call(min)",
        )
    )
    print("-" * 64)
    for result in results:
        print(
            "{0:<16} {1:>12.3f} {2:>14.3f} {3:>16.2f}".format(
                result["label"],
                result["min_ns"] / 1_000_000.0,
                result["median_ns"] / 1_000_000.0,
                result["ns_per_call_min"],
            )
        )
    print()

    for reuse_count in _REUSE_COUNTS:
        direct_result = next(
            result for result in results if result["label"] == f"direct x{reuse_count}"
        )
        alias_result = next(
            result for result in results if result["label"] == f"alias x{reuse_count}"
        )
        ratio = alias_result["min_ns"] / direct_result["min_ns"]
        print(
            "alias x{0} vs direct x{0}: min-time ratio={1:.4f}".format(
                reuse_count,
                ratio,
            )
        )
