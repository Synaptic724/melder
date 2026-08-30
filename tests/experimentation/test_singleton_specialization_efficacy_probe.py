"""
Efficacy and correctness probe for generalized singleton warm-tail specialization.

Purpose:
    Measure the end-to-end effect of the config-gated specialization stage
    (patch lane `generalized_singleton_specialization_2026_07_01`) by running
    identical workloads against flag-OFF and flag-ON runtimes.

Lane map (where the inner executor actually runs decides where capture pays):
    - leaf: CONTROL. The `unique` route door short-circuits warm root hits
      from live storage BEFORE calling the inner executor, so this lane must
      read ~1.00 by construction (and the specializer now declines root-only
      capture on short-circuiting routes).
    - many_over_{2,4,8}u: the `many` route always enters the inner body;
      captured unique deps replace per-step store walks. Width scaling is the
      thesis check: the ratio should IMPROVE as captured-dep count grows.
    - cycle_meld1: gauntlet-shaped lane. A fresh lesser conduit per cycle
      forces root meld#1 construction, which walks the unique deps in the
      inner body - capture pays exactly there.
    - threadsN_many8: nogil contention lane. N threads hammer warm melds of
      the width-8 graph on private lesser conduits; shared-line relief from
      captured deps should GROW the win versus t1.
    - deopt_many2: guard-miss control; must stay ~1.00 vs flag OFF.

Usage (3.14t target; sandbox 3.10 cannot import melder):
    pytest tests/experimentation/test_singleton_specialization_efficacy_probe.py -q -s
    python tests/experimentation/test_singleton_specialization_efficacy_probe.py

Env knobs:
    MELDER_SPEC_PROBE_ITERS        warm-loop iterations (default 20000)
    MELDER_SPEC_PROBE_WARMUP       warm-loop warmup (default 2000)
    MELDER_SPEC_PROBE_CYCLE_ITERS  lesser-cycle iterations (default 3000)
    MELDER_SPEC_PROBE_THREADS      contention lane thread count (default 3)

This is an experimentation surface, not production runtime code.
"""

import os
import sys
import threading
import time
from typing import Any, Callable, Dict, Tuple


def _ensure_src_on_path() -> None:
    """
    Ensure the local `src/` tree is importable for direct experiment execution.
    """
    if "src" not in sys.path:
        sys.path.insert(0, "src")
    if "." not in sys.path:
        sys.path.insert(0, ".")


_ensure_src_on_path()

from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
)

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook

SPEC_FLAG = "generalized_singleton_specialization_enabled"


class UniqueLeaf:
    """
    `unique` control spell with zero dependencies (door short-circuit lane).
    """

    def __init__(self) -> None:
        """
        Initialize an identity marker.
        """
        self.marker = object()


class U1:
    """
    `unique` dependency spell (width member).
    """

    def __init__(self) -> None:
        """
        Initialize an identity marker.
        """
        self.marker = object()


class U2:
    """
    `unique` dependency spell (width member).
    """

    def __init__(self) -> None:
        """
        Initialize an identity marker.
        """
        self.marker = object()


class U3:
    """
    `unique` dependency spell (width member).
    """

    def __init__(self) -> None:
        """
        Initialize an identity marker.
        """
        self.marker = object()


class U4:
    """
    `unique` dependency spell (width member).
    """

    def __init__(self) -> None:
        """
        Initialize an identity marker.
        """
        self.marker = object()


class U5:
    """
    `unique` dependency spell (width member).
    """

    def __init__(self) -> None:
        """
        Initialize an identity marker.
        """
        self.marker = object()


class U6:
    """
    `unique` dependency spell (width member).
    """

    def __init__(self) -> None:
        """
        Initialize an identity marker.
        """
        self.marker = object()


class U7:
    """
    `unique` dependency spell (width member).
    """

    def __init__(self) -> None:
        """
        Initialize an identity marker.
        """
        self.marker = object()


class U8:
    """
    `unique` dependency spell (width member).
    """

    def __init__(self) -> None:
        """
        Initialize an identity marker.
        """
        self.marker = object()


class Many2Root:
    """
    `many` root over two unique deps (mixed-body baseline width).
    """

    def __init__(self, u1: U1, u2: U2) -> None:
        """
        Store injected references.
        """
        self.u1 = u1
        self.u2 = u2


class Many4Root:
    """
    `many` root over four unique deps (width-4 thesis check).
    """

    def __init__(self, u1: U1, u2: U2, u3: U3, u4: U4) -> None:
        """
        Store injected references.
        """
        self.u1 = u1
        self.u2 = u2
        self.u3 = u3
        self.u4 = u4


class Many8Root:
    """
    `many` root over eight unique deps (width-8 thesis check).
    """

    def __init__(
            self,
            u1: U1,
            u2: U2,
            u3: U3,
            u4: U4,
            u5: U5,
            u6: U6,
            u7: U7,
            u8: U8,
    ) -> None:
        """
        Store injected references.
        """
        self.u1 = u1
        self.u2 = u2
        self.u3 = u3
        self.u4 = u4
        self.u5 = u5
        self.u6 = u6
        self.u7 = u7
        self.u8 = u8


class ConduitCycleRoot:
    """
    `unique_per_conduit` root over four unique deps (gauntlet-shaped meld#1).
    """

    def __init__(self, u1: U1, u2: U2, u3: U3, u4: U4) -> None:
        """
        Store injected references.
        """
        self.u1 = u1
        self.u2 = u2
        self.u3 = u3
        self.u4 = u4


class SpaceCycleRoot:
    """
    `unique_per_spell_space` root over four unique deps (request-shaped meld#1).
    """

    def __init__(self, u1: U1, u2: U2, u3: U3, u4: U4) -> None:
        """
        Store injected references.
        """
        self.u1 = u1
        self.u2 = u2
        self.u3 = u3
        self.u4 = u4


def _env_int(name: str, default: int) -> int:
    """
    Read one integer env knob with a default.
    """
    raw = os.environ.get(name)
    if raw is None:
        return default
    return int(raw)


def _reset_runtime() -> None:
    """
    Reset Aether and rebind Spellbook and Conduit to the fresh singleton.
    """
    Aether._reset_singleton_for_tests()
    fresh_aether = Aether()
    Spellbook._aether = fresh_aether
    Conduit._aether = fresh_aether


_BINDINGS: Tuple[Tuple[str, type, Existence], ...] = (
    ("leaf", UniqueLeaf, Existence.unique),
    ("u1", U1, Existence.unique),
    ("u2", U2, Existence.unique),
    ("u3", U3, Existence.unique),
    ("u4", U4, Existence.unique),
    ("u5", U5, Existence.unique),
    ("u6", U6, Existence.unique),
    ("u7", U7, Existence.unique),
    ("u8", U8, Existence.unique),
    ("many2", Many2Root, Existence.many),
    ("many4", Many4Root, Existence.many),
    ("many8", Many8Root, Existence.many),
    ("cycle_root", ConduitCycleRoot, Existence.unique_per_conduit),
    ("space_root", SpaceCycleRoot, Existence.unique_per_spell_space),
)


def _build_runtime(
        *,
        specialization_enabled: bool,
        frame_suffix: str,
) -> Tuple[Spellbook, Conduit, Dict[str, str], Dict[str, Any]]:
    """
    Build one automatic runtime with the specialization flag set pre-conjure.
    """
    _reset_runtime()
    frame_name = f"spec-probe-{frame_suffix}"
    configuration = SpellbookConfiguration(frame_name)
    apply_automatic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.set_property(SPEC_FLAG, specialization_enabled)
    spellbook = Spellbook(
        aetheric_frame=frame_name,
        configuration=configuration,
    )
    spell_ids: Dict[str, str] = {}
    for name, spell_type, existence in _BINDINGS:
        spell_ids[name] = spellbook.bind(
            spell=spell_type,
            existence=existence,
            permissions="create",
        )
    conduit = spellbook.conjure(name=frame_name, dynamic=False)
    spells = {}
    for name, spell_id in spell_ids.items():
        spell = spellbook._spell_id_pool.get(spell_id)
        if spell is None:
            raise AssertionError("Probe could not resolve live spell.")
        spells[name] = spell
    return spellbook, conduit, spell_ids, spells


def _cleanup_runtime(spellbook: Spellbook, conduit: Conduit) -> None:
    """
    Tear down one probe runtime and reset the singleton for isolation.
    """
    try:
        conduit.cleanup()
    finally:
        try:
            spellbook.cleanup()
        finally:
            _reset_runtime()


def _measure_average_ns(
        action: Callable[[], None],
        *,
        iterations: int,
        warmup: int,
) -> float:
    """
    Return the average ns/op for one warm action.
    """
    for _ in range(warmup):
        action()
    start = time.perf_counter_ns()
    for _ in range(iterations):
        action()
    return (time.perf_counter_ns() - start) / iterations


def _measure_cycle_meld1_ns(
        conduit: Conduit,
        cycle_root_id: str,
        *,
        iterations: int,
        warmup: int,
) -> float:
    """
    Return average ns per (create lesser -> root meld#1 -> cleanup) cycle.
    """
    def cycle() -> None:
        lesser = conduit.create_lesser_conduit()
        try:
            resolved = lesser.meld(spell_id=cycle_root_id)
            if resolved is None:
                raise AssertionError("cycle root meld returned None.")
        finally:
            lesser.cleanup()

    return _measure_average_ns(cycle, iterations=iterations, warmup=warmup)


def _measure_spellspace_cycle_meld1_ns(
        conduit: Conduit,
        space_root_id: str,
        *,
        iterations: int,
        warmup: int,
) -> float:
    """
    Return average ns per (enter spellspace -> root meld#1 -> exit) cycle.

    Contract:
        - One persistent lesser conduit hosts every cycle so the measurement
          isolates the request-shaped spellspace lane (the gauntlet request
          lane): each cycle re-enters a fresh spellspace scope, forcing the
          `unique_per_spell_space` root through meld#1 construction, whose
          inner body walks the captured unique deps.
    """
    lesser = conduit.create_lesser_conduit()
    try:
        def cycle() -> None:
            context_manager = lesser.enter_spellspace()
            space = context_manager.__enter__()
            try:
                resolved = space.meld(spell_id=space_root_id)
                if resolved is None:
                    raise AssertionError("space root meld returned None.")
            finally:
                context_manager.__exit__(None, None, None)

        return _measure_average_ns(cycle, iterations=iterations, warmup=warmup)
    finally:
        lesser.cleanup()


def _measure_threaded_warm_ns(
        conduit: Conduit,
        spell_id: str,
        *,
        threads: int,
        iterations: int,
        warmup: int,
) -> float:
    """
    Return wall ns/op for N threads hammering one warm meld on private lessers.
    """
    barrier = threading.Barrier(threads + 1)
    done = threading.Barrier(threads + 1)

    def worker() -> None:
        lesser = conduit.create_lesser_conduit()
        try:
            for _ in range(warmup):
                lesser.meld(spell_id=spell_id)
            barrier.wait()
            for _ in range(iterations):
                lesser.meld(spell_id=spell_id)
            done.wait()
        finally:
            lesser.cleanup()

    workers = [threading.Thread(target=worker) for _ in range(threads)]
    for thread in workers:
        thread.start()
    barrier.wait()
    start = time.perf_counter_ns()
    done.wait()
    elapsed = time.perf_counter_ns() - start
    for thread in workers:
        thread.join()
    return elapsed / (threads * iterations)


def _assert_differential_semantics(
        conduit: Conduit,
        spell_ids: Dict[str, str],
) -> None:
    """
    Assert the identity contract every flag posture must satisfy.
    """
    u1_a = conduit.meld(spell_id=spell_ids["u1"])
    u1_b = conduit.meld(spell_id=spell_ids["u1"])
    if u1_a is not u1_b:
        raise AssertionError("unique dep identity is not stable across melds.")
    many_a = conduit.meld(spell_id=spell_ids["many2"])
    many_b = conduit.meld(spell_id=spell_ids["many2"])
    if many_a is many_b:
        raise AssertionError("many root returned a cached instance.")
    if many_a.u1 is not u1_a:
        raise AssertionError("many root did not receive the shared unique dep.")
    lesser_one = conduit.create_lesser_conduit()
    try:
        cycle_a = lesser_one.meld(spell_id=spell_ids["cycle_root"])
        cycle_b = lesser_one.meld(spell_id=spell_ids["cycle_root"])
        if cycle_a is not cycle_b:
            raise AssertionError("unique_per_conduit root not cached in scope.")
        if cycle_a.u1 is not u1_a:
            raise AssertionError("cycle root did not receive the shared dep.")
    finally:
        lesser_one.cleanup()
    lesser_two = conduit.create_lesser_conduit()
    try:
        cycle_c = lesser_two.meld(spell_id=spell_ids["cycle_root"])
        if cycle_c is cycle_a:
            raise AssertionError("unique_per_conduit root leaked across scopes.")
    finally:
        lesser_two.cleanup()


def test_singleton_specialization_efficacy_probe() -> None:
    """
    Run differential, install, deopt, width, cycle, and threaded probes.
    """
    iterations = _env_int("MELDER_SPEC_PROBE_ITERS", 20000)
    warmup = _env_int("MELDER_SPEC_PROBE_WARMUP", 2000)
    cycle_iterations = _env_int("MELDER_SPEC_PROBE_CYCLE_ITERS", 3000)
    thread_count = _env_int("MELDER_SPEC_PROBE_THREADS", 3)
    lanes = ("leaf", "many2", "many4", "many8")
    results: Dict[str, Dict[str, float]] = {}

    for flag in (False, True):
        key = "on" if flag else "off"
        spellbook, conduit, spell_ids, spells = _build_runtime(
            specialization_enabled=flag,
            frame_suffix=key,
        )
        try:
            _assert_differential_semantics(conduit, spell_ids)

            # Install/settle: after warm melds the executor slot must be
            # stable in BOTH postures (specialized swap settles once). The
            # context is built lazily at FIRST meld, so meld before reading it.
            conduit.meld(spell_id=spell_ids["many8"])
            conduit.meld(spell_id=spell_ids["many8"])
            many8_context = spells["many8"]._creation_context
            if many8_context is None:
                raise AssertionError("many8 context missing after melds.")
            settled = many8_context._no_overrides_executor
            conduit.meld(spell_id=spell_ids["many8"])
            if many8_context._no_overrides_executor is not settled:
                raise AssertionError("executor slot did not settle post-install.")

            lane_ns: Dict[str, float] = {}
            for lane in lanes:
                lane_ns[lane] = _measure_average_ns(
                    lambda lane_id=spell_ids[lane]: conduit.meld(spell_id=lane_id),
                    iterations=iterations,
                    warmup=warmup,
                )
            lane_ns["cycle_meld1"] = _measure_cycle_meld1_ns(
                conduit,
                spell_ids["cycle_root"],
                iterations=cycle_iterations,
                warmup=max(cycle_iterations // 10, 100),
            )
            lane_ns["spellspace_cycle_meld1"] = _measure_spellspace_cycle_meld1_ns(
                conduit,
                spell_ids["space_root"],
                iterations=cycle_iterations,
                warmup=max(cycle_iterations // 10, 100),
            )
            lane_ns[f"threads{thread_count}_many8"] = _measure_threaded_warm_ns(
                conduit,
                spell_ids["many8"],
                threads=thread_count,
                iterations=iterations,
                warmup=warmup,
            )

            if flag:
                # Deopt control: bump one captured dep's epoch; identity
                # semantics must hold and the lane must not error.
                live_u1 = conduit.meld(spell_id=spell_ids["u1"])
                spells["u1"]._door_epoch += 1
                deopt_many = conduit.meld(spell_id=spell_ids["many2"])
                if deopt_many.u1 is not live_u1:
                    raise AssertionError("deopt broke dependency identity.")
                lane_ns["deopt_many2"] = _measure_average_ns(
                    lambda: conduit.meld(spell_id=spell_ids["many2"]),
                    iterations=iterations,
                    warmup=warmup,
                )
            results[key] = lane_ns
        finally:
            _cleanup_runtime(spellbook, conduit)

    print("SINGLETON_SPECIALIZATION_EFFICACY_PROBE_V2")
    print(
        f"iterations={iterations} warmup={warmup} "
        f"cycle_iterations={cycle_iterations} threads={thread_count}"
    )
    header = f"{'lane':<24}{'flag_off_ns':>14}{'flag_on_ns':>14}{'on/off':>10}"
    print(header)
    ordered = [
        "leaf",
        "many2",
        "many4",
        "many8",
        "cycle_meld1",
        "spellspace_cycle_meld1",
        f"threads{thread_count}_many8",
    ]
    for lane in ordered:
        off_ns = results["off"][lane]
        on_ns = results["on"][lane]
        print(f"{lane:<24}{off_ns:>14.1f}{on_ns:>14.1f}{on_ns / off_ns:>10.4f}")
    deopt_ns = results["on"]["deopt_many2"]
    off_many2 = results["off"]["many2"]
    print(
        f"{'deopt_many2':<24}{'-':>14}{deopt_ns:>14.1f}"
        f"{deopt_ns / off_many2:>10.4f}"
    )


if __name__ == "__main__":
    test_singleton_specialization_efficacy_probe()
