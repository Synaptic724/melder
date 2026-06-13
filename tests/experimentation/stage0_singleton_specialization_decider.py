"""
Stage 0 decider: does a singleton-guarded *speculated* meld body beat the
generic construction lane at threads 1/3/5 on the free-threaded (3.14t)
interpreter?

WHY THIS EXISTS
    The adaptive PGO DI optimizer (design:
    codex/context_compass/artifacts/2026-06-13_adaptive_pgo_di_optimizer_design.md;
    = "trim #2" on
    tickets/tasks/2026-06-13_executor_construction_lane_trim_task.md) speculates
    that when a meld's dependency prefix is `Existence.unique` singletons,
    re-walking those deps on every meld#1 (load the shared `Spell`, read
    `Spell._owner_creations`, lock-free `store._creations.get(spell_id)`) is
    wasted work once the singletons are live for the process lifetime. A
    speculated body instead CLOSES OVER the resolved singleton instances and
    guards them with a single `Spell._door_epoch` int-compare per dep, deopting
    to the generic body on a guard miss.

    Stage 0 is the GO/NO-GO gate. If closing-over + epoch-guard does NOT beat the
    generic per-dep acquisition by a margin that GROWS (or at least holds) at
    threads 3/5 -- where the +52/+94% shared-read inflation lives -- the optimizer
    is not worth building and the ticket stays parked. Spend a day here, not two
    weeks downstream.

WHAT IT MEASURES (3 arms, all over REAL melder runtime objects)
    generic_replica
        Faithful replica of the CURRENT (post-trim-#1) emitted no-overrides body
        for the singleton prefix. Per dep: load the shared `Spell`, read
        `spell._owner_creations`, inline `store._creations.get(spell_id)` (the
        emitter inlines this exact dict get; `get_creation` is a bare
        `self._creations.get`). `use_spell_lock` is NOT computed on a warm hit
        (trim #1 moved it under the miss branch) so it is not modelled here.
        Then construct the root directly.
    speculated
        Per dep: one `spell._door_epoch == captured_epoch` int-compare; on hit use
        the closed-over instance; on miss deopt to the generic acquisition. Then
        construct the root the SAME way. The ONLY difference from generic_replica
        is dep acquisition, so the delta isolates exactly the lever.
    real_meld_anchor (scale context, not a per-op peer)
        `lesser.meld(spell=root_id)` meld#1 inside a recycled pooled scope -- the
        true generic construction lane including the door + registration -- so the
        per-op numbers above can be read against the real meld#1 wall.

HOW TO READ THE RESULT
    Primary signal = speculated_ns / generic_ns at each thread count.
        < 1.0 and FALLING t1 -> t3 -> t5  => strong GO (the nogil contention win
            we predicted; build Stage 1).
        < 1.0 but flat                     => weak GO (shape-only win; weigh it
            against warmup amortization).
        >= 1.0 at t3 or t5                 => NO-GO; the guard cost ate the win.
            Park the ticket; the day was cheap.

ENV KNOBS
    STAGE0_THREADS        comma list (default "1,3,5")
    STAGE0_ITERS          tight-loop iters per arm per thread (default 200000)
    STAGE0_SINGLETONS     unique singleton deps in the root (default "5,12")
    STAGE0_ANCHOR         "1" to run the recycled-scope real-meld#1 anchor (default "1")
    STAGE0_ANCHOR_SECONDS seconds per anchor sweep (default 3.0)

RUN (on the 3.14t target)
    PYTHON_GIL=0 python tests/experimentation/stage0_singleton_specialization_decider.py
    PYTHON_GIL=1 python tests/experimentation/stage0_singleton_specialization_decider.py   # control

CAVEAT
    The author could NOT smoke-test this: the dev sandbox is CPython 3.10 and
    melder targets 3.14t. The melder setup idioms are copied verbatim from
    benchmarks/testing_other_di/profile_scope_cycle_contention.py. The spots most
    likely to need your eye are flagged with `# VERIFY:` comments, and a hard
    self-check (`_assert_di_wired`) fails LOUD if the dynamic graph's DI did not
    inject as expected, so you never read garbage numbers.
"""

import os
import statistics
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


# --------------------------------------------------------------------------- #
# Path + env
# --------------------------------------------------------------------------- #
def _ensure_src_on_path() -> None:
    """
    Put the melder `src/` directory on `sys.path` so `import melder` resolves.

    Contract:
        - This file lives at `<root>/tests/experimentation/`, so the project
          root is `parents[2]` and the import root is `<root>/src`.
    """
    project_root = Path(__file__).resolve().parents[2]
    src_dir = project_root / "src"
    src_as_str = str(src_dir)
    if src_as_str not in sys.path:
        sys.path.insert(0, src_as_str)


_ensure_src_on_path()

FRAME_NAME = "stage0-singleton-decider"
CONDUIT_NAME = "stage0-singleton-decider"

THREAD_SWEEP: List[int] = [
    max(1, int(token))
    for token in os.environ.get("STAGE0_THREADS", "1,3,5").split(",")
]
TIGHT_ITERS: int = max(1000, int(os.environ.get("STAGE0_ITERS", "200000")))
SINGLETON_WIDTHS: List[int] = [
    max(1, int(token))
    for token in os.environ.get("STAGE0_SINGLETONS", "5,12").split(",")
]
RUN_ANCHOR: bool = os.environ.get("STAGE0_ANCHOR", "1") == "1"
ANCHOR_SECONDS: float = max(0.5, float(os.environ.get("STAGE0_ANCHOR_SECONDS", "3.0")))


# --------------------------------------------------------------------------- #
# Synthetic graph (codegen'd into module globals so DI annotations resolve)
# --------------------------------------------------------------------------- #
class CapturedDep:
    """
    One captured singleton dependency for the speculated/generic arms.

    Holds live runtime object references (Spell, store, instance), so this is a
    normal class, not a value-only dataclass.

    Attributes:
        spell: The dependency's live `Spell` record (shared across threads).
        store: The dependency's `_owner_creations` scope store (shared).
        spell_id: The dependency's sha256 spell id.
        instance: The resolved singleton instance (closed over by the
            speculated arm).
        epoch: The `Spell._door_epoch` value captured at warmup (the guard).
    """

    __slots__ = ("spell", "store", "spell_id", "instance", "epoch")

    def __init__(
            self,
            *,
            spell: Any,
            store: Any,
            spell_id: str,
            instance: Any,
            epoch: int,
    ) -> None:
        self.spell = spell
        self.store = store
        self.spell_id = spell_id
        self.instance = instance
        self.epoch = epoch


class CapturedGraph:
    """
    Everything the arms need after one warmup meld of the root.

    Attributes:
        spellbook: Owning spellbook (for cleanup).
        conduit: Root conduit (for the anchor + capture).
        root_cls: The root class (constructed directly by both arms).
        transient_cls: The `many` transient class (constructed fresh per call).
        root_id: The root spell id (for the real-meld anchor).
        deps: Captured singleton deps in DI order.
    """

    __slots__ = (
        "spellbook", "conduit", "root_cls", "transient_cls", "root_id", "deps",
    )

    def __init__(
            self,
            *,
            spellbook: Any,
            conduit: Any,
            root_cls: type,
            transient_cls: type,
            root_id: str,
            deps: List[CapturedDep],
    ) -> None:
        self.spellbook = spellbook
        self.conduit = conduit
        self.root_cls = root_cls
        self.transient_cls = transient_cls
        self.root_id = root_id
        self.deps = deps


def _install_graph(n_singletons: int) -> Tuple[List[type], type, type]:
    """
    Codegen `n_singletons` trivial singleton classes + one transient + one root
    into MODULE globals, so the root's DI annotations resolve via
    `__init__.__globals__`.

    Returns:
        (singleton_classes, transient_class, root_class).

    Notes:
        - `exec` is the codegen path here (permitted for agent codegen work); the
          generated classes are plain and annotation-resolvable.
        - Distinct class per singleton so each is its own SINGLE_BY_ANNOTATION
          target (one unique spell each).
    """
    module_globals = globals()
    lines: List[str] = []
    for index in range(n_singletons):
        lines.append(
            f"class _Stage0S{index}:\n"
            f"    def __init__(self) -> None:\n"
            f"        pass\n"
        )
    lines.append(
        "class _Stage0Transient:\n"
        "    def __init__(self) -> None:\n"
        "        pass\n"
    )
    params = ", ".join(f"s{i}: _Stage0S{i}" for i in range(n_singletons))
    params = f"{params}, t: _Stage0Transient"
    assigns = "\n        ".join(
        [f"self.s{i} = s{i}" for i in range(n_singletons)] + ["self.t = t"]
    )
    lines.append(
        f"class _Stage0Root:\n"
        f"    def __init__(self, {params}) -> None:\n"
        f"        {assigns}\n"
    )
    # VERIFY: exec into module globals so get_type_hints on _Stage0Root.__init__
    # resolves _Stage0S* via the function's own __globals__. If melder resolves
    # annotations differently on 3.14t, _assert_di_wired below will fail loud.
    exec("\n".join(lines), module_globals)  # noqa: S102  (intentional codegen)
    singletons = [module_globals[f"_Stage0S{i}"] for i in range(n_singletons)]
    return singletons, module_globals["_Stage0Transient"], module_globals["_Stage0Root"]


# --------------------------------------------------------------------------- #
# Melder runtime setup (idioms copied from profile_scope_cycle_contention.py)
# --------------------------------------------------------------------------- #
def _reset_runtime() -> None:
    """
    Reset the Aether/Nexus singleton runtime between graph builds.
    """
    from melder.aether.aether import Aether
    from melder.aether.conduit.conduit import Conduit
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.nexus.nexus import Nexus

    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _build_root_conduit(
        singletons: List[type],
        transient_cls: type,
        root_cls: type,
) -> Tuple[Any, Any, List[str], str]:
    """
    Bind the synthetic graph and conjure one non-dynamic root conduit
    (caching disabled, single phase-scheduler worker), matching the contention
    harness setup.

    Returns:
        (spellbook, conduit, singleton_ids_in_DI_order, root_id).
    """
    from melder.aether.spellbook.existence.existence import Existence
    from melder.aether.spellbook.spellbook import Spellbook

    _reset_runtime()
    spellbook = Spellbook(aetheric_frame=FRAME_NAME)
    configuration = spellbook.get_configuration()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
        system_caching_enabled=False,
    )
    singleton_ids: List[str] = [
        spellbook.bind(spell=cls, existence=Existence.unique, permissions="create")
        for cls in singletons
    ]
    spellbook.bind(spell=transient_cls, existence=Existence.many, permissions="create")
    root_id = spellbook.bind(
        spell=root_cls,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    conduit = spellbook.conjure(name=CONDUIT_NAME, dynamic=False)
    return spellbook, conduit, singleton_ids, root_id


def _warm_and_capture(
        *,
        spellbook: Any,
        conduit: Any,
        singleton_ids: List[str],
        root_id: str,
        root_cls: type,
        transient_cls: type,
) -> CapturedGraph:
    """
    Warm the graph (one root meld) and capture the per-dep state both arms need.

    Raises:
        RuntimeError: if a singleton's `_owner_creations` store or live instance
            could not be captured (the speculated/generic arms would be invalid).
    """
    # Warm: build the root once so every unique singleton is live in its owner
    # store and the root's executor is hydrated (cold->hot slot swap).
    conduit.meld(spell=root_id)

    deps: List[CapturedDep] = []
    for spell_id in singleton_ids:
        # VERIFY: _spell_id_pool is the Spellbook's id->Spell map (same map the
        # live door reads); private but stable.
        spell = spellbook._spell_id_pool.get(spell_id)
        if spell is None:
            raise RuntimeError(f"Stage0: no Spell for singleton id {spell_id!r}.")
        store = spell._owner_creations  # VERIFY: set at ownership-stamp time.
        if store is None:
            raise RuntimeError(
                f"Stage0: singleton {spell_id!r} has no _owner_creations store; "
                f"capture invalid (is it really Existence.unique?)."
            )
        instance = conduit.meld(spell=spell_id)
        if instance is None:
            raise RuntimeError(f"Stage0: singleton {spell_id!r} melded to None.")
        deps.append(
            CapturedDep(
                spell=spell,
                store=store,
                spell_id=spell_id,
                instance=instance,
                epoch=spell._door_epoch,
            )
        )
    return CapturedGraph(
        spellbook=spellbook,
        conduit=conduit,
        root_cls=root_cls,
        transient_cls=transient_cls,
        root_id=root_id,
        deps=deps,
    )


# --------------------------------------------------------------------------- #
# The two primary arms (closures over captured state)
# --------------------------------------------------------------------------- #
def _make_generic_arm(captured: CapturedGraph) -> Callable[[], Any]:
    """
    Build the generic-replica arm: faithful per-dep singleton re-walk + root
    construct (post-trim-#1 warm-hit shape).
    """
    deps = captured.deps
    root_cls = captured.root_cls
    transient_cls = captured.transient_cls

    def _generic() -> Any:
        instances: List[Any] = []
        append = instances.append
        for dep in deps:
            spell = dep.spell                       # shared Spell load
            store = spell._owner_creations          # shared attr read
            append(store._creations.get(dep.spell_id))  # lock-free dict get
        return root_cls(*instances, transient_cls())

    return _generic


def _make_speculated_arm(captured: CapturedGraph) -> Callable[[], Any]:
    """
    Build the speculated arm: per-dep epoch int-compare over closed-over
    instances; deopt to the generic acquisition on a guard miss; then the SAME
    root construct.
    """
    deps = captured.deps
    root_cls = captured.root_cls
    transient_cls = captured.transient_cls

    def _speculated() -> Any:
        instances: List[Any] = []
        append = instances.append
        for dep in deps:
            if dep.spell._door_epoch != dep.epoch:   # guard: one int-compare
                # Deopt: fall back to the live generic acquisition for this dep.
                store = dep.spell._owner_creations
                append(store._creations.get(dep.spell_id))
            else:
                append(dep.instance)                 # closed-over, no store read
        return root_cls(*instances, transient_cls())

    return _speculated


def _assert_di_wired(captured: CapturedGraph) -> None:
    """
    Hard self-check: prove the dynamic graph's DI actually injected the
    singletons + transient, and that both arms construct an equivalent root.

    Raises:
        RuntimeError: if DI did not wire as expected (so the timing below is
            never trusted on a broken graph).
    """
    melded_root = captured.conduit.meld(spell=captured.root_id)
    n = len(captured.deps)
    for index in range(n):
        attr = f"s{index}"
        if not hasattr(melded_root, attr):
            raise RuntimeError(
                f"Stage0: root is missing DI attr {attr!r}; dynamic-graph DI "
                f"wiring failed (check annotation resolution on 3.14t)."
            )
    if not hasattr(melded_root, "t"):
        raise RuntimeError("Stage0: root is missing transient DI attr 't'.")

    generic_root = _make_generic_arm(captured)()
    spec_root = _make_speculated_arm(captured)()
    for index in range(n):
        attr = f"s{index}"
        if getattr(generic_root, attr) is not getattr(spec_root, attr):
            raise RuntimeError(
                f"Stage0: arms disagree on dep {attr!r}; speculated capture is "
                f"not identity-equal to the generic store read."
            )
    # Deopt detection: bump a dep's epoch and confirm speculated sees the miss.
    probe = captured.deps[0]
    saved = probe.epoch
    probe.epoch = saved - 1  # force mismatch vs live spell._door_epoch
    _make_speculated_arm(captured)()  # must run through the deopt branch, no error
    probe.epoch = saved


# --------------------------------------------------------------------------- #
# Threaded timing
# --------------------------------------------------------------------------- #
def _time_arm(
        *,
        arm: Callable[[], Any],
        thread_count: int,
        iters: int,
) -> float:
    """
    Time one arm in barrier-synced tight loops across `thread_count` threads.

    Returns:
        Mean per-operation nanoseconds across threads (post-warmup, all threads
        started together so cross-thread shared-read contention is in the number).
    """
    results: List[float] = [0.0] * thread_count
    barrier = threading.Barrier(thread_count)

    def _worker(slot: int) -> None:
        perf = time.perf_counter_ns
        for _ in range(1000):  # warmup
            arm()
        barrier.wait(timeout=30)
        start = perf()
        for _ in range(iters):
            arm()
        results[slot] = (perf() - start) / iters

    threads = [
        threading.Thread(target=_worker, args=(index,), name=f"stage0-{index}")
        for index in range(thread_count)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return statistics.fmean(results)


def _run_width(width: int) -> None:
    """
    Build one graph width, self-check, and print the generic-vs-speculated
    per-op table + ratios + a GO/NO-GO read across the thread sweep.
    """
    singletons, transient_cls, root_cls = _install_graph(width)
    spellbook, conduit, singleton_ids, root_id = _build_root_conduit(
        singletons, transient_cls, root_cls
    )
    try:
        captured = _warm_and_capture(
            spellbook=spellbook,
            conduit=conduit,
            singleton_ids=singleton_ids,
            root_id=root_id,
            root_cls=root_cls,
            transient_cls=transient_cls,
        )
        _assert_di_wired(captured)
        generic_arm = _make_generic_arm(captured)
        speculated_arm = _make_speculated_arm(captured)

        print(f"\n{'=' * 74}")
        print(
            f"WIDTH={width} singleton deps  "
            f"(generic touches/dep=3: Spell, _owner_creations, dict.get; "
            f"speculated touches/dep=1: _door_epoch)"
        )
        print(f"{'threads':>8} {'generic_ns':>12} {'spec_ns':>12} "
              f"{'spec/gen':>9} {'saved_ns':>10}")
        ratios: Dict[int, float] = {}
        for thread_count in THREAD_SWEEP:
            generic_ns = _time_arm(
                arm=generic_arm, thread_count=thread_count, iters=TIGHT_ITERS
            )
            spec_ns = _time_arm(
                arm=speculated_arm, thread_count=thread_count, iters=TIGHT_ITERS
            )
            ratio = spec_ns / generic_ns if generic_ns else float("nan")
            ratios[thread_count] = ratio
            print(
                f"{thread_count:>8} {generic_ns:>12.1f} {spec_ns:>12.1f} "
                f"{ratio:>9.3f} {generic_ns - spec_ns:>10.1f}"
            )
        _print_verdict(width, ratios)
    finally:
        conduit.permanent_cleanup()
        spellbook.cleanup()


def _print_verdict(width: int, ratios: Dict[int, float]) -> None:
    """
    Print a blunt GO/NO-GO read from the spec/gen ratios.
    """
    if not ratios:
        print("verdict: no data")
        return
    hi = max(ratios)
    lo = min(ratios)
    ratio_hi = ratios[hi]
    ratio_lo = ratios[lo]
    contention_trend = "falls" if ratio_hi < ratio_lo else "flat/rises"
    if ratio_hi < 0.90 and ratio_hi <= ratio_lo:
        verdict = "STRONG GO -- speculation wins and the win grows with threads"
    elif ratio_hi < 0.95:
        verdict = "WEAK GO -- shape win; weigh vs profiler-warmup amortization"
    elif ratio_hi < 1.0:
        verdict = "MARGINAL -- small win; probably not worth the subsystem"
    else:
        verdict = "NO-GO -- guard cost >= the re-walk it replaces; park the ticket"
    print(
        f"verdict(width={width}): {verdict}  "
        f"[ratio@t{lo}={ratio_lo:.3f}, ratio@t{hi}={ratio_hi:.3f}, "
        f"contention-trend={contention_trend}]"
    )


# --------------------------------------------------------------------------- #
# Real-meld#1 scale anchor (recycled pooled scope, like the contention harness)
# --------------------------------------------------------------------------- #
def _run_anchor(width: int) -> None:
    """
    Recycled-scope real meld#1 sweep for absolute scale: how big is the per-op
    delta above against the true generic meld#1 wall?
    """
    singletons, transient_cls, root_cls = _install_graph(width)
    spellbook, conduit, _singleton_ids, root_id = _build_root_conduit(
        singletons, transient_cls, root_cls
    )
    try:
        conduit.meld(spell=root_id)  # warm singletons + hydrate executor
        print(f"\n--- real meld#1 anchor (width={width}, recycled scope) ---")
        for thread_count in THREAD_SWEEP:
            per_op = _anchor_sweep(conduit, root_id, thread_count)
            print(f"{'threads':>8}={thread_count}  meld#1_avg={per_op:>10.1f}ns")
    finally:
        conduit.permanent_cleanup()
        spellbook.cleanup()


def _anchor_sweep(conduit: Any, root_id: str, thread_count: int) -> float:
    """
    Run `ANCHOR_SECONDS` of recycled-scope meld#1 cycles and return mean per-op
    nanoseconds. Each cycle: create_lesser_conduit -> meld#1(root) -> cleanup.
    """
    per_thread: List[List[float]] = [[] for _ in range(thread_count)]
    stop_at = time.perf_counter() + ANCHOR_SECONDS

    def _worker(slot: int) -> None:
        perf = time.perf_counter_ns
        samples = per_thread[slot]
        while time.perf_counter() < stop_at:
            lesser = conduit.create_lesser_conduit()
            try:
                start = perf()
                lesser.meld(spell=root_id)
                samples.append(float(perf() - start))
            finally:
                lesser.cleanup()

    threads = [
        threading.Thread(target=_worker, args=(index,), name=f"stage0-anchor-{index}")
        for index in range(thread_count)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    flat = [value for samples in per_thread for value in samples]
    return statistics.fmean(flat) if flat else float("nan")


def main() -> None:
    """
    Run the Stage 0 decider across the configured singleton widths + thread
    sweep, then the optional real-meld#1 scale anchor.
    """
    gil_probe = getattr(sys, "_is_gil_enabled", None)
    gil_text = "enabled" if (gil_probe is None or gil_probe()) else "disabled"
    print("=" * 74)
    print("STAGE 0 DECIDER -- singleton-guarded speculation vs generic re-walk")
    print(
        f"threads={THREAD_SWEEP}  iters={TIGHT_ITERS}  widths={SINGLETON_WIDTHS}  "
        f"gil={gil_text}"
    )
    print("Primary signal: spec/gen ratio < 1 and FALLING into t3/t5 => GO.")
    print("=" * 74)
    for width in SINGLETON_WIDTHS:
        _run_width(width)
    if RUN_ANCHOR:
        for width in SINGLETON_WIDTHS:
            _run_anchor(width)


if __name__ == "__main__":
    main()
