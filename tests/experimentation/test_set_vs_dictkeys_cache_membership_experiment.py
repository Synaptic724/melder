import time
from typing import Dict, FrozenSet, Tuple


def _build_spell_id(index: int) -> str:
    """
    Build one deterministic SHA-like spell id string for the experiment.

    Args:
        index:
            Stable numeric index for the generated id.

    Returns:
        str:
            Fixed-width lowercase hex string shaped like a spell_id.
    """
    return f"{index:064x}"


def _build_cache_shapes() -> Tuple[FrozenSet[str], FrozenSet[str], Dict[str, object]]:
    """
    Build the experiment shapes for the cache-coverage check.

    Purpose:
        Mirror the actual cache question with a requested spell-id set and one
        payload dictionary keyed by the same spell ids.

    Returns:
        Tuple[FrozenSet[str], FrozenSet[str], Dict[str, object]]:
            Requested spell ids, cached spell ids, and payload dictionary.
    """
    cached_spell_ids = frozenset(_build_spell_id(index) for index in range(300))
    requested_spell_ids = frozenset(_build_spell_id(index) for index in range(300))
    payloads_by_spell_id = {
        spell_id: object()
        for spell_id in cached_spell_ids
    }
    return requested_spell_ids, cached_spell_ids, payloads_by_spell_id


def test_set_vs_dictkeys_cache_membership_experiment() -> None:
    """
    Measure `set` versus `dict.keys()` for the cache coverage-check shape.

    Contract:
        - Uses the exact same semantic operation for both paths:
          compute the missing requested spell ids.
        - Repeats each operation 1000 times.
        - Prints total and per-iteration timing for quick inspection.
        - Asserts both approaches produce identical semantic results.

    Returns:
        None.
    """
    requested_spell_ids, cached_spell_ids, payloads_by_spell_id = _build_cache_shapes()
    payload_keys = payloads_by_spell_id.keys()
    iterations = 1000

    # Warm both paths so we do not time first-use noise only.
    missing_from_set = requested_spell_ids - cached_spell_ids
    missing_from_keys = requested_spell_ids - payload_keys
    assert missing_from_set == missing_from_keys

    started_at_ns = time.perf_counter_ns()
    for _ in range(iterations):
        missing_from_set = requested_spell_ids - cached_spell_ids
    set_elapsed_ns = time.perf_counter_ns() - started_at_ns

    started_at_ns = time.perf_counter_ns()
    for _ in range(iterations):
        missing_from_keys = requested_spell_ids - payload_keys
    dict_keys_elapsed_ns = time.perf_counter_ns() - started_at_ns

    assert missing_from_set == missing_from_keys

    set_ns_per_iteration = set_elapsed_ns / iterations
    dict_keys_ns_per_iteration = dict_keys_elapsed_ns / iterations

    print("CACHE_MEMBERSHIP_EXPERIMENT")
    print(f"iterations={iterations}")
    print(f"requested_spell_count={len(requested_spell_ids)}")
    print(f"cached_spell_count={len(cached_spell_ids)}")
    print(f"set_total_ns={set_elapsed_ns}")
    print(f"set_ns_per_iteration={set_ns_per_iteration:.2f}")
    print(f"dict_keys_total_ns={dict_keys_elapsed_ns}")
    print(f"dict_keys_ns_per_iteration={dict_keys_ns_per_iteration:.2f}")
    print(
        "dict_keys_over_set_ratio="
        f"{(dict_keys_elapsed_ns / set_elapsed_ns):.6f}"
    )
