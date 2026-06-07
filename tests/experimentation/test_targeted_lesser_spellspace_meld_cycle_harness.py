"""
Targeted cycle-cost harness for lesser conduit, spellspace, and meld surfaces.

Purpose:
    Provide a narrower additive benchmark than the broad real-world gauntlet by
    separating three steady-state runtime surfaces:
    - pooled lesser conduit acquire/cleanup,
    - pooled spellspace enter/exit,
    - front-door meld on persistent scopes.

This is an experimentation surface, not production runtime code.
"""

import gc
import os
import sys
import time
from typing import Any, Callable, Dict, Optional, Sequence, Tuple

from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
)


def _ensure_src_on_path() -> None:
    """
    Ensure the local `src/` tree is importable for direct experiment execution.
    """
    if "src" not in sys.path:
        sys.path.insert(0, "src")
    if "." not in sys.path:
        sys.path.insert(0, ".")


_ensure_src_on_path()

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class _NoDeps:
    """
    Provide an explicit zero-argument constructor for benchmark leaves.
    """

    __slots__ = ()

    def __init__(self) -> None:
        return None


class CycleSingleton(_NoDeps):
    """
    Shared singleton dependency used by the targeted cycle roots.
    """

    __slots__ = ()


class ConduitScopedRoot:
    """
    Root resolved through `Existence.unique_per_conduit`.
    """

    __slots__ = ("shared",)

    def __init__(self, shared: CycleSingleton) -> None:
        self.shared = shared


class SpellspaceScopedRoot:
    """
    Root resolved through `Existence.unique_per_spell_space`.
    """

    __slots__ = ("shared",)

    def __init__(self, shared: CycleSingleton) -> None:
        self.shared = shared


class SharedRoot:
    """
    Root resolved through `Existence.unique`.
    """

    __slots__ = ("shared",)

    def __init__(self, shared: CycleSingleton) -> None:
        self.shared = shared


class ManyRoot:
    """
    Root resolved through `Existence.many`.
    """

    __slots__ = ("shared",)

    def __init__(self, shared: CycleSingleton) -> None:
        self.shared = shared


def _env_int(name: str, default: int) -> int:
    """
    Read one integer experiment setting from the environment.
    """
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def _iterations() -> int:
    """
    Return the configured steady-state iteration count for this harness.
    """
    value = _env_int("MELDER_TARGETED_CYCLE_ITERS", 3000)
    if value <= 0:
        raise AssertionError("MELDER_TARGETED_CYCLE_ITERS must be > 0")
    return value


def _warmup_iterations() -> int:
    """
    Return the configured warmup iteration count for this harness.
    """
    value = _env_int("MELDER_TARGETED_CYCLE_WARMUP", 300)
    if value < 0:
        raise AssertionError("MELDER_TARGETED_CYCLE_WARMUP must be >= 0")
    return value


def _reset_runtime() -> None:
    """
    Reset Aether and rebind Spellbook and Conduit to the fresh singleton.
    """
    Aether._reset_singleton_for_tests()
    fresh_aether = Aether()
    Spellbook._aether = fresh_aether
    Conduit._aether = fresh_aether


def _build_runtime() -> Tuple[Spellbook, Conduit, Dict[str, str], Dict[str, Any]]:
    """
    Build one automatic Melder runtime for targeted cycle measurement.
    """
    _reset_runtime()
    configuration = SpellbookConfiguration("targeted-cycle-harness")
    apply_automatic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook = Spellbook(
        aetheric_frame="targeted-cycle-harness",
        configuration=configuration,
    )

    spell_ids = {
        "singleton": spellbook.bind(
            spell=CycleSingleton,
            existence=Existence.unique,
            permissions="create",
        ),
        "conduit": spellbook.bind(
            spell=ConduitScopedRoot,
            existence=Existence.unique_per_conduit,
            permissions="create",
        ),
        "spellspace": spellbook.bind(
            spell=SpellspaceScopedRoot,
            existence=Existence.unique_per_spell_space,
            permissions="create",
        ),
        "shared": spellbook.bind(
            spell=SharedRoot,
            existence=Existence.unique,
            permissions="create",
        ),
        "many": spellbook.bind(
            spell=ManyRoot,
            existence=Existence.many,
            permissions="create",
        ),
    }
    conduit = spellbook.conjure(
        name="targeted-cycle-harness",
        automatic=True,
    )

    spells = {}
    for name, spell_id in spell_ids.items():
        spell = spellbook._spell_id_pool.get(spell_id)
        if spell is None:
            raise AssertionError("Targeted cycle harness could not resolve live spell.")
        spells[name] = spell

    return spellbook, conduit, spell_ids, spells


def _cleanup_runtime(spellbook: Spellbook, conduit: Conduit) -> None:
    """
    Permanently tear down one targeted-cycle runtime.
    """
    try:
        conduit.permanent_cleanup()
    except Exception:
        pass
    try:
        spellbook.cleanup()
    except Exception:
        pass
    _reset_runtime()
    gc.collect()


def _prime_lesser_pool(root_conduit: Conduit) -> None:
    """
    Seed the lesser pool so the measured loop hits the steady-state reuse path.
    """
    lesser = root_conduit.create_lesser_conduit()
    lesser.cleanup()


def _prime_spellspace_pool(lesser: Conduit) -> None:
    """
    Seed the spellspace pool so the measured loop hits the steady-state reuse path.
    """
    spellspace_context = lesser.enter_spellspace()
    spellspace_context.__enter__()
    spellspace_context.__exit__(None, None, None)


def _measure_average_ns(
    action: Callable[[], None],
    *,
    reset: Optional[Callable[[], None]],
    iterations: int,
    warmup: int,
) -> float:
    """
    Measure the average time in nanoseconds for one action.
    """
    for _ in range(warmup):
        if reset is not None:
            reset()
        action()
    start_ns = time.perf_counter_ns()
    for _ in range(iterations):
        if reset is not None:
            reset()
        action()
    end_ns = time.perf_counter_ns()
    return (end_ns - start_ns) / float(iterations)


def _measure_lesser_cycle_components(
    root_conduit: Conduit,
    *,
    iterations: int,
    warmup: int,
) -> Dict[str, float]:
    """
    Measure pooled lesser acquire and cleanup cost separately and together.
    """
    _prime_lesser_pool(root_conduit)

    def acquire_only() -> Conduit:
        return root_conduit.create_lesser_conduit()

    def cycle_action() -> None:
        lesser = root_conduit.create_lesser_conduit()
        lesser.cleanup()

    for _ in range(warmup):
        lesser = acquire_only()
        lesser.cleanup()

    acquire_total_ns = 0
    cleanup_total_ns = 0
    cycle_total_ns = 0
    for _ in range(iterations):
        cycle_t0 = time.perf_counter_ns()
        lesser = root_conduit.create_lesser_conduit()
        acquire_t1 = time.perf_counter_ns()
        lesser.cleanup()
        cleanup_t2 = time.perf_counter_ns()
        acquire_total_ns += acquire_t1 - cycle_t0
        cleanup_total_ns += cleanup_t2 - acquire_t1
        cycle_total_ns += cleanup_t2 - cycle_t0

    _ = cycle_action
    return {
        "lesser_acquire_ns": acquire_total_ns / float(iterations),
        "lesser_cleanup_ns": cleanup_total_ns / float(iterations),
        "lesser_cycle_total_ns": cycle_total_ns / float(iterations),
    }


def _measure_spellspace_cycle_components(
    lesser: Conduit,
    *,
    iterations: int,
    warmup: int,
) -> Dict[str, float]:
    """
    Measure pooled spellspace enter and exit cost separately and together.
    """
    _prime_spellspace_pool(lesser)

    for _ in range(warmup):
        spellspace_context = lesser.enter_spellspace()
        spellspace_context.__enter__()
        spellspace_context.__exit__(None, None, None)

    enter_total_ns = 0
    exit_total_ns = 0
    cycle_total_ns = 0
    for _ in range(iterations):
        cycle_t0 = time.perf_counter_ns()
        spellspace_context = lesser.enter_spellspace()
        spellspace_context.__enter__()
        enter_t1 = time.perf_counter_ns()
        spellspace_context.__exit__(None, None, None)
        exit_t2 = time.perf_counter_ns()
        enter_total_ns += enter_t1 - cycle_t0
        exit_total_ns += exit_t2 - enter_t1
        cycle_total_ns += exit_t2 - cycle_t0

    return {
        "spellspace_enter_ns": enter_total_ns / float(iterations),
        "spellspace_exit_ns": exit_total_ns / float(iterations),
        "spellspace_cycle_total_ns": cycle_total_ns / float(iterations),
    }


def _measure_lesser_meld_route(
    lesser: Conduit,
    spell_id: str,
    *,
    cold_reset: Optional[Callable[[], None]],
    iterations: int,
    warmup: int,
) -> Dict[str, float]:
    """
    Measure cold and warm front-door meld on one persistent lesser conduit.
    """
    if cold_reset is None:
        raise AssertionError("Targeted lesser meld route requires a cold reset callable.")

    def cold_action() -> None:
        resolved = lesser.meld(spell=spell_id)
        if resolved is None:
            raise AssertionError("Targeted lesser meld route returned None.")

    cold_ns = _measure_average_ns(
        cold_action,
        reset=cold_reset,
        iterations=iterations,
        warmup=warmup,
    )

    cold_reset()
    cold_action()

    warm_ns = _measure_average_ns(
        cold_action,
        reset=None,
        iterations=iterations,
        warmup=warmup,
    )
    return {
        "cold_ns": cold_ns,
        "warm_ns": warm_ns,
    }


def _measure_spellspace_meld_route(
    space: Any,
    spell_id: str,
    *,
    cold_reset: Optional[Callable[[], None]],
    iterations: int,
    warmup: int,
) -> Dict[str, float]:
    """
    Measure cold and warm front-door meld on one persistent spellspace.
    """
    if cold_reset is None:
        raise AssertionError("Targeted spellspace meld route requires a cold reset callable.")

    def cold_action() -> None:
        resolved = space.meld(spell=spell_id)
        if resolved is None:
            raise AssertionError("Targeted spellspace meld route returned None.")

    cold_ns = _measure_average_ns(
        cold_action,
        reset=cold_reset,
        iterations=iterations,
        warmup=warmup,
    )

    cold_reset()
    cold_action()

    warm_ns = _measure_average_ns(
        cold_action,
        reset=None,
        iterations=iterations,
        warmup=warmup,
    )
    return {
        "cold_ns": cold_ns,
        "warm_ns": warm_ns,
    }


def _measure_many_meld_route(
    lesser: Conduit,
    spell_id: str,
    *,
    cold_reset: Optional[Callable[[], None]],
    iterations: int,
    warmup: int,
) -> float:
    """
    Measure the always-create `many` meld path on one persistent lesser conduit.
    """
    if cold_reset is None:
        raise AssertionError("Targeted many meld route requires a cold reset callable.")

    def action() -> None:
        resolved = lesser.meld(spell=spell_id)
        if resolved is None:
            raise AssertionError("Targeted many meld route returned None.")

    return _measure_average_ns(
        action,
        reset=cold_reset,
        iterations=iterations,
        warmup=warmup,
    )


def _format_results_table(rows: Sequence[Dict[str, str]]) -> str:
    """
    Format one compact terminal table for the targeted harness output.
    """
    headers = (
        "surface",
        "scope",
        "route",
        "cold_ns",
        "warm_ns",
        "enter_or_acquire_ns",
        "exit_or_cleanup_ns",
        "total_ns",
        "note",
    )
    widths: Dict[str, int] = {}
    for header in headers:
        widths[header] = len(header)
    for row in rows:
        for header in headers:
            widths[header] = max(widths[header], len(row[header]))

    def line(values: Dict[str, str]) -> str:
        return "| " + " | ".join(
            values[header].ljust(widths[header]) for header in headers
        ) + " |"

    separator = {}
    for header in headers:
        separator[header] = "-" * widths[header]
    lines = [line(dict((header, header) for header in headers)), line(separator)]
    for row in rows:
        lines.append(line(row))
    return "\n".join(lines)


def _run_targeted_cycle_harness() -> Sequence[Dict[str, str]]:
    """
    Execute the targeted cycle-cost harness and return printable rows.
    """
    iterations = _iterations()
    warmup = _warmup_iterations()
    spellbook, root_conduit, spell_ids, spells = _build_runtime()
    rows: list[Dict[str, str]] = []
    try:
        lesser_cycle = _measure_lesser_cycle_components(
            root_conduit,
            iterations=iterations,
            warmup=warmup,
        )
        rows.append(
            {
                "surface": "lesser_cycle",
                "scope": "pooled",
                "route": "lesser_only",
                "cold_ns": "-",
                "warm_ns": "-",
                "enter_or_acquire_ns": f"{lesser_cycle['lesser_acquire_ns']:.3f}",
                "exit_or_cleanup_ns": f"{lesser_cycle['lesser_cleanup_ns']:.3f}",
                "total_ns": f"{lesser_cycle['lesser_cycle_total_ns']:.3f}",
                "note": "steady_state_pooled_reuse",
            }
        )

        persistent_lesser = root_conduit.create_lesser_conduit()
        try:
            spellspace_cycle = _measure_spellspace_cycle_components(
                persistent_lesser,
                iterations=iterations,
                warmup=warmup,
            )
            rows.append(
                {
                    "surface": "spellspace_cycle",
                    "scope": "pooled",
                    "route": "spellspace_only",
                    "cold_ns": "-",
                    "warm_ns": "-",
                    "enter_or_acquire_ns": f"{spellspace_cycle['spellspace_enter_ns']:.3f}",
                    "exit_or_cleanup_ns": f"{spellspace_cycle['spellspace_exit_ns']:.3f}",
                    "total_ns": f"{spellspace_cycle['spellspace_cycle_total_ns']:.3f}",
                    "note": "steady_state_pooled_reuse",
                }
            )

            conduit_unique_metrics = _measure_lesser_meld_route(
                persistent_lesser,
                spell_ids["conduit"],
                cold_reset=persistent_lesser._creations.clear_all,
                iterations=iterations,
                warmup=warmup,
            )
            rows.append(
                {
                    "surface": "meld",
                    "scope": "persistent_lesser",
                    "route": "unique_per_conduit",
                    "cold_ns": f"{conduit_unique_metrics['cold_ns']:.3f}",
                    "warm_ns": f"{conduit_unique_metrics['warm_ns']:.3f}",
                    "enter_or_acquire_ns": "-",
                    "exit_or_cleanup_ns": "-",
                    "total_ns": "-",
                    "note": "direct_spell_id_frontdoor",
                }
            )

            shared_owner_creations = spells["shared"]._owner_creations
            if shared_owner_creations is None:
                raise AssertionError("Shared route spell has no owner creations.")
            shared_metrics = _measure_lesser_meld_route(
                persistent_lesser,
                spell_ids["shared"],
                cold_reset=shared_owner_creations.clear_all,
                iterations=iterations,
                warmup=warmup,
            )
            rows.append(
                {
                    "surface": "meld",
                    "scope": "persistent_lesser",
                    "route": "shared_unique",
                    "cold_ns": f"{shared_metrics['cold_ns']:.3f}",
                    "warm_ns": f"{shared_metrics['warm_ns']:.3f}",
                    "enter_or_acquire_ns": "-",
                    "exit_or_cleanup_ns": "-",
                    "total_ns": "-",
                    "note": "owner_creations_plus_spell_lock",
                }
            )

            many_ns = _measure_many_meld_route(
                persistent_lesser,
                spell_ids["many"],
                cold_reset=persistent_lesser._creations.clear_all,
                iterations=iterations,
                warmup=warmup,
            )
            rows.append(
                {
                    "surface": "meld",
                    "scope": "persistent_lesser",
                    "route": "many",
                    "cold_ns": f"{many_ns:.3f}",
                    "warm_ns": "-",
                    "enter_or_acquire_ns": "-",
                    "exit_or_cleanup_ns": "-",
                    "total_ns": "-",
                    "note": "always_creates",
                }
            )

            spellspace_context = persistent_lesser.enter_spellspace()
            active_spellspace = spellspace_context.__enter__()
            try:
                spellspace_metrics = _measure_spellspace_meld_route(
                    active_spellspace,
                    spell_ids["spellspace"],
                    cold_reset=active_spellspace._creations.clear_all,
                    iterations=iterations,
                    warmup=warmup,
                )
                rows.append(
                    {
                        "surface": "meld",
                        "scope": "persistent_spellspace",
                        "route": "unique_per_spell_space",
                        "cold_ns": f"{spellspace_metrics['cold_ns']:.3f}",
                        "warm_ns": f"{spellspace_metrics['warm_ns']:.3f}",
                        "enter_or_acquire_ns": "-",
                        "exit_or_cleanup_ns": "-",
                        "total_ns": "-",
                        "note": "space_frontdoor_only",
                    }
                )
            finally:
                spellspace_context.__exit__(None, None, None)
        finally:
            persistent_lesser.cleanup()
    finally:
        _cleanup_runtime(spellbook, root_conduit)

    print("TARGETED_CYCLE_COST_HARNESS")
    print(_format_results_table(rows))
    return rows


def test_targeted_lesser_spellspace_meld_cycle_harness() -> None:
    """
    Run the targeted cycle-cost harness and assert it produced usable output.
    """
    rows = _run_targeted_cycle_harness()
    if len(rows) != 6:
        raise AssertionError("Targeted cycle harness did not produce the expected row count.")
    by_route = {}
    for row in rows:
        by_route[(row["surface"], row["route"])] = row

    if float(by_route[("lesser_cycle", "lesser_only")]["total_ns"]) <= 0.0:
        raise AssertionError("Targeted lesser cycle metric must be positive.")
    if float(by_route[("spellspace_cycle", "spellspace_only")]["total_ns"]) <= 0.0:
        raise AssertionError("Targeted spellspace cycle metric must be positive.")
    if float(by_route[("meld", "unique_per_conduit")]["cold_ns"]) <= 0.0:
        raise AssertionError("Targeted unique_per_conduit cold meld metric must be positive.")
    if float(by_route[("meld", "unique_per_conduit")]["warm_ns"]) <= 0.0:
        raise AssertionError("Targeted unique_per_conduit warm meld metric must be positive.")
    if float(by_route[("meld", "shared_unique")]["cold_ns"]) <= 0.0:
        raise AssertionError("Targeted shared cold meld metric must be positive.")
    if float(by_route[("meld", "shared_unique")]["warm_ns"]) <= 0.0:
        raise AssertionError("Targeted shared warm meld metric must be positive.")
    if float(by_route[("meld", "many")]["cold_ns"]) <= 0.0:
        raise AssertionError("Targeted many meld metric must be positive.")
    if float(by_route[("meld", "unique_per_spell_space")]["cold_ns"]) <= 0.0:
        raise AssertionError("Targeted spellspace cold meld metric must be positive.")
    if float(by_route[("meld", "unique_per_spell_space")]["warm_ns"]) <= 0.0:
        raise AssertionError("Targeted spellspace warm meld metric must be positive.")
