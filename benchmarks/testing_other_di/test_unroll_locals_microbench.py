"""
Focused A/B micro-benchmark for the generalized "unrolled locals" executor.

What it measures
----------------
The warm per-meld cost of a `many`-root-over-`unique`-singletons graph at several
depths, comparing the two emitted executor shapes on IDENTICAL graphs in the same
process:

  - dict path  : results published into an `instance_results` dict; deps read via
                 dict lookups (the prior behavior).
  - unroll path : results kept in straight-line `instance_{i}` locals; deps read
                 those locals; no dict (the new behavior).

The A/B is done by monkeypatching `_all_steps_inlinable` to force the dict path
for the baseline run, then restoring it for the unrolled run. Both runs compile a
fresh executor (separate spellbook/conjure per run), so they exercise the two
shapes on the same dependency graph.

Why this shape: a `many` root means the door calls the inner executor on EVERY
meld (no singleton short-circuit), so the warm loop actually runs the
inner executor each iteration -- which is exactly where the unroll lives. The
`unique` deps are built once and reused, so each warm meld constructs the root and
walks the (present) singleton deps.

Run it (from repo root):
  pytest -s -k test_unroll_locals_warm_microbench benchmarks/testing_other_di/test_unroll_locals_microbench.py

Pin to P-cores (recommended on hybrid Intel) by setting the env first:
  DI_PIN_P_CORES=1 pytest -s -k test_unroll_locals_warm_microbench benchmarks/testing_other_di/test_unroll_locals_microbench.py
(or it always attempts a pin via pin_current_process_to_p_cores below)
"""

import gc
import time
from typing import Dict, List, Tuple, Type

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.deep_layers import (
    get_depth_3_classes,
    get_depth_5_classes,
    get_depth_7_classes,
    get_depth_9_classes,
)
from benchmarks.p_core_affinity.p_core_affinity import (
    pin_current_process_to_p_cores,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers import (
    generalized_no_overrides_codegen_creation_compiler as GEN,
)


def _reset_aether() -> None:
    """Rebind a fresh Aether singleton so each case is isolated."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _bind_many_root_over_singletons(
    spellbook: Spellbook,
    classes: Tuple[Type, ...],
    root_cls: Type,
) -> Dict[Type, str]:
    """Bind the root as `many` (transient) and every dependency as `unique`."""
    spell_ids: Dict[Type, str] = {}
    for cls in classes:
        existence = Existence.many if cls is root_cls else Existence.unique
        spell_ids[cls] = spellbook.bind(
            spell=cls,
            existence=existence,
            permissions="create",
        )
    return spell_ids


def _warm_per_meld_us(
    depth: int,
    classes: Tuple[Type, ...],
    root_cls: Type,
    *,
    force_dict: bool,
    iterations: int,
    repeats: int,
    warmup: int,
) -> float:
    """Return the best (least-noisy) warm per-meld time in microseconds."""
    original = GEN._all_steps_inlinable
    if force_dict:
        GEN._all_steps_inlinable = lambda steps: False  # force the dict path
    samples: List[float] = []
    try:
        for _ in range(repeats):
            _reset_aether()
            label = "dict" if force_dict else "unroll"
            spellbook = Spellbook(aetheric_frame=f"unroll-mb-d{depth}-{label}")
            spellbook.get_configuration().set_property(
                "phase_scheduler_workers_per_spellbook", 1
            )
            spell_ids = _bind_many_root_over_singletons(spellbook, classes, root_cls)
            root_id = spell_ids[root_cls]
            conduit = spellbook.conjure(name=f"unroll-mb-d{depth}-{label}")
            try:
                conduit.meld(spell=root_id)  # cold: compiles the executor + builds deps
                for _ in range(warmup):
                    conduit.meld(spell=root_id)
                gc.collect()
                gc.disable()
                try:
                    start = time.perf_counter()
                    for _ in range(iterations):
                        conduit.meld(spell=root_id)
                    elapsed = time.perf_counter() - start
                finally:
                    gc.activate()
                samples.append((elapsed / iterations) * 1_000_000.0)
            finally:
                conduit.cleanup()
        return min(samples)
    finally:
        GEN._all_steps_inlinable = original


@pytest.mark.parametrize(
    "depth_name",
    ["3", "5", "7", "9"],
)
def test_unroll_locals_warm_microbench(depth_name: str) -> None:
    """
    Print warm per-meld dict-vs-unroll for a many-root-over-singletons graph.

    No threshold is asserted (timings are machine-dependent); this prints numbers
    for local comparison. A positive delta means the unroll path is faster.
    """
    pin = pin_current_process_to_p_cores(strict=False)

    cases = {
        "3": (3, get_depth_3_classes()),
        "5": (5, get_depth_5_classes()),
        "7": (7, get_depth_7_classes()),
        "9": (9, get_depth_9_classes()),
    }
    depth, classes = cases[depth_name]
    root_cls = classes[-1]  # DepthNRoot is last in dependency order
    step_count = len(classes)

    iterations = 100_000
    repeats = 4
    warmup = 3_000

    dict_us = _warm_per_meld_us(
        depth, classes, root_cls,
        force_dict=True, iterations=iterations, repeats=repeats, warmup=warmup,
    )
    unroll_us = _warm_per_meld_us(
        depth, classes, root_cls,
        force_dict=False, iterations=iterations, repeats=repeats, warmup=warmup,
    )
    delta_pct = (dict_us - unroll_us) / dict_us * 100.0 if dict_us else 0.0

    print(
        "\n[unroll micro-bench] many-root-over-singletons "
        f"depth={depth} steps={step_count} "
        f"(best of {repeats} x {iterations} warm melds, single-thread)\n"
        f"  dict path   : {dict_us:8.3f} us/meld  ({1e6 / dict_us:,.0f} melds/s)\n"
        f"  unroll path : {unroll_us:8.3f} us/meld  ({1e6 / unroll_us:,.0f} melds/s)\n"
        f"  delta       : {delta_pct:+.1f}%  "
        f"({'unroll faster' if delta_pct > 0 else 'dict faster'})\n"
        f"  p-core pin  : applied={pin.get('applied')} "
        f"reason={pin.get('reason')} cpus={pin.get('selected_affinity')}"
    )

    # Soft sanity only: both paths must produce a usable instance and time.
    assert dict_us > 0.0 and unroll_us > 0.0
