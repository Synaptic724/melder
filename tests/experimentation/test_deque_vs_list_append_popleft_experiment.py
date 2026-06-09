from collections import deque
import gc
import time
from typing import Callable, Dict, List


_CYCLES: int = 1_000_000
_WARM_QUEUE_SIZE: int = 1024
_REPEATS: int = 3


def _run_list_cycle() -> int:
    """
    Execute one fixed-size queue cycle using `list.append` and `pop(0)`.

    Contract:
        - Starts with `_WARM_QUEUE_SIZE` items already present so `pop(0)`
          measures a non-trivial left-pop shift.
        - Runs exactly `_CYCLES` append+pop-left pairs.
        - Preserves queue size across the full experiment.

    Returns:
        int:
            Final queue length after all operations.
    """
    queue = list(range(_WARM_QUEUE_SIZE))
    for index in range(_CYCLES):
        queue.append(index)
        queue.pop(0)
    return len(queue)


def _run_deque_cycle() -> int:
    """
    Execute one fixed-size queue cycle using `deque.append` and `popleft`.

    Contract:
        - Starts with `_WARM_QUEUE_SIZE` items already present so the queue
          shape matches the list experiment.
        - Runs exactly `_CYCLES` append+pop-left pairs.
        - Preserves queue size across the full experiment.

    Returns:
        int:
            Final queue length after all operations.
    """
    queue = deque(range(_WARM_QUEUE_SIZE))
    for index in range(_CYCLES):
        queue.append(index)
        queue.popleft()
    return len(queue)


def _measure(label: str, action: Callable[[], int]) -> Dict[str, float]:
    """
    Measure one experiment variant over repeated wall-clock runs.

    Args:
        label:
            Human-readable experiment label.
        action:
            Zero-argument callable that executes the benchmarked operation mix.

    Returns:
        Dict[str, float]:
            Timing summary for the variant.
    """
    samples_ns: List[int] = []
    for _ in range(_REPEATS):
        gc.collect()
        start_ns = time.perf_counter_ns()
        final_length = action()
        elapsed_ns = time.perf_counter_ns() - start_ns
        if final_length != _WARM_QUEUE_SIZE:
            raise AssertionError(
                f"{label} changed queue length: {final_length} != {_WARM_QUEUE_SIZE}"
            )
        samples_ns.append(elapsed_ns)

    sorted_samples = sorted(samples_ns)
    min_ns = float(sorted_samples[0])
    median_ns = float(sorted_samples[len(sorted_samples) // 2])
    return {
        "label": label,
        "min_ns": min_ns,
        "median_ns": median_ns,
        "ns_per_cycle_min": min_ns / float(_CYCLES),
    }


def test_deque_vs_list_append_popleft_experiment() -> None:
    """
    Compare `list.append + pop(0)` against `deque.append + popleft`.

    Purpose:
        Answer the direct queue-shape question with one million append and
        pop-left pairs on the same steady-state queue depth.

    Contract:
        - Uses exactly `_CYCLES == 1_000_000` append+pop-left pairs.
        - Uses the same initial queue depth for both containers.
        - Prints timing summaries and ratio only; this is an experiment, not a
          behavioral assertion about which container must always win.
    """
    list_result = _measure("list append+pop(0)", _run_list_cycle)
    deque_result = _measure("deque append+popleft", _run_deque_cycle)

    print("DEQUE_VS_LIST_APPEND_PLEFT_EXPERIMENT")
    print(f"cycles={_CYCLES}")
    print(f"warm_queue_size={_WARM_QUEUE_SIZE}")
    print(f"repeats={_REPEATS}")
    print(
        "{0:<24} {1:>12} {2:>14} {3:>18}".format(
            "variant",
            "min(ms)",
            "median(ms)",
            "ns/cycle(min)",
        )
    )
    print("-" * 74)
    for result in (list_result, deque_result):
        print(
            "{0:<24} {1:>12.3f} {2:>14.3f} {3:>18.2f}".format(
                result["label"],
                result["min_ns"] / 1_000_000.0,
                result["median_ns"] / 1_000_000.0,
                result["ns_per_cycle_min"],
            )
        )
    print(
        "list_over_deque_ratio="
        f"{(list_result['min_ns'] / deque_result['min_ns']):.6f}"
    )
