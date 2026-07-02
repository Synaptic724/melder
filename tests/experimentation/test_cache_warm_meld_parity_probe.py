"""
Warm-meld parity probe: cold-built runtime vs warm-cache-loaded runtime.

Purpose:
    Reproduce (or clear) the user-measured "system is slower after the cache
    is made" gauntlet observation with an in-repo minimal pair, and prove
    WHICH cache load seam actually serves current saves.

Background (epic EPIC-2026-07-02-unify-cache-rehydration):
    The epic's original root-cause hypothesis blamed the LEGACY spell-level
    cache (save-time emission + code-object replay). The S1 pipeline read
    showed manifest-first save has been live since 2026-06-12 for all three
    families (generalized/solo/many_only): manifest packages load lazily
    through the SAME hydrator as live builds, so post-first-meld hot doors
    are identical by construction. This probe therefore checks, in one run:
      1. SHAPE AUDIT: every staged payload is a manifest package (if any
         legacy-shaped payload appears, the epic's original surgery target
         is live again and this probe names it).
      2. SEAM PROOF: after a warm-cache conjure, cached spells carry a
         published context while `_spell_codegen_creation` stays None
         (phases 8-11 skipped) - proving the manifest seam served them.
      3. PARITY MEASURE: identical warm workloads (flat warm melds + the
         gauntlet-shaped lesser-conduit cycle lane) timed on the cold-built
         runtime vs the warm-cache runtime. Ratio ~1.00 clears the load
         path; a systematic gap reproduces the regression in-repo.

Usage (3.14t target; sandbox 3.10 cannot import melder):
    pytest tests/experimentation/test_cache_warm_meld_parity_probe.py -q -s
    python tests/experimentation/test_cache_warm_meld_parity_probe.py

Env knobs:
    MELDER_CACHE_PROBE_ITERS        warm-loop iterations (default 20000)
    MELDER_CACHE_PROBE_WARMUP       warm-loop warmup (default 2000)
    MELDER_CACHE_PROBE_CYCLE_ITERS  lesser-cycle iterations (default 2000)

This is an experimentation surface, not production runtime code.
"""

import inspect
import marshal
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple


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
    apply_dynamic_defaults_for_spellbook_configuration,
)

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame_configuration import (
    AethericFrameConfiguration,
)
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.creation_context.creation_context_builder import (
    CreationContextBuilder,
)
from melder.aether.conduit.meld.meld import Meld
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.manifest_creation_cache import (
    is_manifest_package,
)
from melder.utilities.caching_system.caching_system import CachingSystem


class ProbeUniqueA:
    """
    `unique` dependency spell (frame-global identity anchor).
    """

    def __init__(self) -> None:
        """
        Initialize an identity marker.
        """
        self.marker = object()


class ProbeUniqueB:
    """
    `unique` dependency spell (second width member).
    """

    def __init__(self) -> None:
        """
        Initialize an identity marker.
        """
        self.marker = object()


class ProbeUniqueC:
    """
    `unique` dependency spell (third width member).
    """

    def __init__(self) -> None:
        """
        Initialize an identity marker.
        """
        self.marker = object()


class ProbeUniqueD:
    """
    `unique` dependency spell (fourth width member).
    """

    def __init__(self) -> None:
        """
        Initialize an identity marker.
        """
        self.marker = object()


class ProbeManyRoot:
    """
    `many` root over four unique deps (flat warm lane workload).
    """

    def __init__(
            self,
            a: ProbeUniqueA,
            b: ProbeUniqueB,
            c: ProbeUniqueC,
            d: ProbeUniqueD,
    ) -> None:
        """
        Store injected references.
        """
        self.a = a
        self.b = b
        self.c = c
        self.d = d


class ProbeCycleRoot:
    """
    `unique_per_conduit` root over two unique deps (gauntlet cycle lane).
    """

    def __init__(self, a: ProbeUniqueA, b: ProbeUniqueB) -> None:
        """
        Store injected references.
        """
        self.a = a
        self.b = b


class ProbeSpaceRoot:
    """
    `unique_per_spell_space` root over two unique deps (request-scope lane).
    """

    def __init__(self, a: ProbeUniqueA, b: ProbeUniqueB) -> None:
        """
        Store injected references.
        """
        self.a = a
        self.b = b


_BINDINGS: Tuple[Tuple[str, type, Existence], ...] = (
    ("ua", ProbeUniqueA, Existence.unique),
    ("ub", ProbeUniqueB, Existence.unique),
    ("uc", ProbeUniqueC, Existence.unique),
    ("ud", ProbeUniqueD, Existence.unique),
    ("many_root", ProbeManyRoot, Existence.many),
    ("cycle_root", ProbeCycleRoot, Existence.unique_per_conduit),
    ("space_root", ProbeSpaceRoot, Existence.unique_per_spell_space),
)


_SEAM_TARGETS: Tuple[Tuple[str, type, str], ...] = (
    ("builder_build", CreationContextBuilder, "build"),
    ("cache_disk_emit", CachingSystem, "emit"),
    ("cache_stage_upsert", CachingSystem, "upsert_spell_payload"),
    ("spellbook_stage_attempt", Spellbook, "_emit_spell_cache"),
    ("spellbook_file_emit", Spellbook, "_emit_cache_file_if_required"),
    ("runtime_reresolution", Meld, "_ensure_runtime_resolution_ready"),
)


def _install_seam_counters() -> Tuple[Dict[str, int], Callable[[], None]]:
    """
    Wrap the cache/rebuild seams with call counters for one measured phase.

    Purpose:
        The gauntlet showed equal active-cycle throughput but a systematic
        wall gap with caching on - the cost lives OUTSIDE the door calls.
        These counters name the seam that fires during the warm phase:
        context rebuilds, cache staging attempts, bundle disk writes, and
        runtime re-resolution entries.

    Contract:
        - Test-scope instrumentation only; the restore callable reinstalls
          every original attribute and MUST run in a finally block.
        - `CreationContextBuilder.build` is a staticmethod and is restored
          as one.

    Returns:
        Tuple[Dict[str, int], Callable[[], None]]:
            Live counter map (mutated in place by the wrappers) plus the
            restore callable.
    """
    counters: Dict[str, int] = {name: 0 for name, _, _ in _SEAM_TARGETS}
    originals: Dict[str, Any] = {}

    def _make_wrapper(name: str, target: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            counters[name] += 1
            return target(*args, **kwargs)

        return wrapper

    for name, owner, attribute in _SEAM_TARGETS:
        original = owner.__dict__[attribute]
        originals[name] = original
        if isinstance(original, staticmethod):
            wrapped: Any = staticmethod(
                _make_wrapper(name, original.__func__)
            )
        else:
            wrapped = _make_wrapper(name, original)
        setattr(owner, attribute, wrapped)

    def restore() -> None:
        for name, owner, attribute in _SEAM_TARGETS:
            setattr(owner, attribute, originals[name])

    return counters, restore


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


def _package_root() -> Path:
    """
    Return the melder package root the runtime anchors cache fragments under.

    Contract:
        Mirrors the component caching suite: must resolve to `src/melder`,
        the same root `AethericFrameConfiguration` resolves relative cache
        fragments against.
    """
    return Path(
        inspect.getfile(AethericFrameConfiguration)
    ).resolve().parents[2]


def _cache_root_fragment(*, prepare: bool) -> Path:
    """
    Resolve (and optionally reset) the probe-owned cache root.

    Args:
        prepare:
            True clears any previous probe cache so the pair starts cold;
            False reuses the existing bundle (the warm-cache leg).

    Returns:
        Path:
            Cache-root fragment relative to the melder package root.
    """
    cache_root_path = (
        _package_root() / "tests/experimentation/_cache_parity_probe_root"
    )
    if prepare:
        if cache_root_path.exists():
            shutil.rmtree(cache_root_path)
        cache_root_path.mkdir(parents=True, exist_ok=True)
    return cache_root_path.relative_to(_package_root())


def _build_runtime(
        *,
        dynamic: bool,
        frame_name: str,
        prepare_cache_root: bool,
) -> Tuple[Spellbook, Conduit, Dict[str, str]]:
    """
    Build one caching-enabled runtime for the probe pair.

    Contract:
        - Frame-level cache configuration is activated BEFORE the Spellbook
          exists, mirroring the component caching suite ordering.
        - Both pair legs use the SAME frame name and cache root so the warm
          leg's conjure resolves the cold leg's bundle by deterministic
          spell fingerprints.

    Args:
        dynamic:
            Conjure posture for the pair leg.
        frame_name:
            Aether frame name shared by both pair legs.
        prepare_cache_root:
            True on the cold leg (clears previous bundles), False on the
            warm leg (consumes the cold leg's bundle).

    Returns:
        Tuple[Spellbook, Conduit, Dict[str, str]]:
            Runtime handles plus name -> spell_id map.
    """
    _reset_runtime()
    fragment = _cache_root_fragment(prepare=prepare_cache_root)
    frame = Aether()._ensure_frame(frame_name)
    frame_configuration = frame.frame_configuration
    if frame_configuration is None:
        raise AssertionError("Frame configuration missing for probe frame.")
    frame_configuration.with_system_caching_enabled(True)
    frame_configuration.with_system_cache_root_path(fragment)

    configuration = SpellbookConfiguration(frame_name)
    if dynamic:
        apply_dynamic_defaults_for_spellbook_configuration(configuration)
    else:
        apply_automatic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
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
    conduit = spellbook.conjure(name=frame_name, dynamic=dynamic)
    return spellbook, conduit, spell_ids


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


def _audit_staged_payload_shapes(spellbook: Spellbook) -> Tuple[int, int]:
    """
    Count manifest-shaped vs legacy-shaped payloads staged by this Spellbook.

    Returns:
        Tuple[int, int]:
            (manifest_count, legacy_count) over every staged spell payload.
    """
    caching_system = spellbook._get_or_create_caching_system()
    manifest_count = 0
    legacy_count = 0
    for _, payload in caching_system.spell_payloads.items():
        if is_manifest_package(payload):
            manifest_count += 1
        else:
            legacy_count += 1
    return manifest_count, legacy_count


def _audit_bundle_shapes_on_disk(spellbook: Spellbook) -> Tuple[int, int]:
    """
    Count manifest vs legacy payload shapes in the persisted bundle file.

    Contract:
        Reads the marshal bundle directly so the warm leg audits exactly
        what its conjure consumed, independent of in-memory staging.

    Returns:
        Tuple[int, int]:
            (manifest_count, legacy_count) over the persisted payload map.
    """
    caching_system = spellbook._get_or_create_caching_system()
    bundle_path = caching_system.bundle_path
    if not bundle_path.exists():
        return 0, 0
    decoded = marshal.loads(bundle_path.read_bytes())
    payloads = decoded.get("spell_payloads", {})
    manifest_count = 0
    legacy_count = 0
    for payload_bytes in payloads.values():
        # Version-3 bundles store nested-marshal bytes per spell (the
        # GC-untracked resident-cache contract); decode one payload at a
        # time for the shape check.
        payload = marshal.loads(payload_bytes)
        if is_manifest_package(payload):
            manifest_count += 1
        else:
            legacy_count += 1
    return manifest_count, legacy_count


def _count_cache_served_spells(
        spellbook: Spellbook,
        spell_ids: Dict[str, str],
) -> Tuple[int, int]:
    """
    Count spells served by the cache seam vs live-compiled after conjure.

    Contract:
        A cache-served spell carries `resolution_complete` with NO phase-11
        `_spell_codegen_creation` on its artifact (phases 8-11 skipped); a
        live-compiled spell carries the phase-11 container. Read BEFORE any
        meld so first-meld hydration cannot blur the two groups.

    Returns:
        Tuple[int, int]:
            (cache_served_count, live_compiled_count).
    """
    cache_served = 0
    live_compiled = 0
    for spell_id in spell_ids.values():
        spell = spellbook._spell_id_pool.get(spell_id)
        if spell is None:
            raise AssertionError("Probe could not resolve live spell.")
        artifact = spell._compiler_artifact
        codegen_creation = (
            None if artifact is None else artifact._spell_codegen_creation
        )
        if spell.resolution_complete and codegen_creation is None:
            cache_served += 1
        else:
            live_compiled += 1
    return cache_served, live_compiled


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


def _measure_workloads(
        conduit: Conduit,
        spell_ids: Dict[str, str],
) -> Dict[str, float]:
    """
    Run the probe workload suite on one runtime and return lane ns/op.

    Lanes:
        - warm_many4: warm `many` root melds (flat warm instance-door lane).
        - warm_unique: warm `unique` leaf melds (short-circuit route lane).
        - cycle_meld1: fresh lesser conduit + `unique_per_conduit` root
          meld#1 + cleanup per iteration (gauntlet-shaped scope-cycle lane).
        - space_cycle: enter spellspace -> `unique_per_spell_space` root
          meld#1 -> exit, on one persistent lesser conduit (the gauntlet
          request-scope shape).
        - space_hot_many: warm `many` root melds INSIDE one open spellspace
          (the gauntlet hot-object shape - this is where the cache-on wall
          gap lives if scope-hosted melds diverge from root-conduit melds).
    """
    iterations = _env_int("MELDER_CACHE_PROBE_ITERS", 20000)
    warmup = _env_int("MELDER_CACHE_PROBE_WARMUP", 2000)
    cycle_iterations = _env_int("MELDER_CACHE_PROBE_CYCLE_ITERS", 2000)
    many_root_id = spell_ids["many_root"]
    unique_id = spell_ids["ua"]
    cycle_root_id = spell_ids["cycle_root"]
    space_root_id = spell_ids["space_root"]

    def warm_many() -> None:
        if conduit.meld(spell=many_root_id) is None:
            raise AssertionError("many root meld returned None.")

    def warm_unique() -> None:
        if conduit.meld(spell=unique_id) is None:
            raise AssertionError("unique leaf meld returned None.")

    def cycle() -> None:
        lesser = conduit.create_lesser_conduit()
        try:
            if lesser.meld(spell=cycle_root_id) is None:
                raise AssertionError("cycle root meld returned None.")
        finally:
            lesser.cleanup()

    lanes: Dict[str, float] = {
        "warm_many4": _measure_average_ns(
            warm_many, iterations=iterations, warmup=warmup
        ),
        "warm_unique": _measure_average_ns(
            warm_unique, iterations=iterations, warmup=warmup
        ),
        "cycle_meld1": _measure_average_ns(
            cycle,
            iterations=cycle_iterations,
            warmup=max(cycle_iterations // 10, 50),
        ),
    }

    space_host = conduit.create_lesser_conduit()
    try:
        def space_cycle() -> None:
            context_manager = space_host.enter_spellspace()
            space = context_manager.__enter__()
            try:
                if space.meld(spell=space_root_id) is None:
                    raise AssertionError("space root meld returned None.")
            finally:
                context_manager.__exit__(None, None, None)

        lanes["space_cycle"] = _measure_average_ns(
            space_cycle,
            iterations=cycle_iterations,
            warmup=max(cycle_iterations // 10, 50),
        )

        hot_manager = space_host.enter_spellspace()
        hot_space = hot_manager.__enter__()
        try:
            def space_hot_many() -> None:
                if hot_space.meld(spell=many_root_id) is None:
                    raise AssertionError("space many meld returned None.")

            lanes["space_hot_many"] = _measure_average_ns(
                space_hot_many, iterations=iterations, warmup=warmup
            )
        finally:
            hot_manager.__exit__(None, None, None)
    finally:
        space_host.cleanup()

    return lanes


def _assert_identity_semantics(
        conduit: Conduit,
        spell_ids: Dict[str, str],
) -> None:
    """
    Assert reuse semantics hold on this runtime (correctness net).

    Contract:
        - `unique` identity is stable across melds.
        - `many` root is fresh per meld and threads the SAME unique deps.
    """
    first_unique = conduit.meld(spell=spell_ids["ua"])
    second_unique = conduit.meld(spell=spell_ids["ua"])
    assert first_unique is second_unique, "unique identity drifted."
    first_root = conduit.meld(spell=spell_ids["many_root"])
    second_root = conduit.meld(spell=spell_ids["many_root"])
    assert second_root is not first_root, "many root was not fresh per meld."
    assert first_root.a is second_root.a, "unique dep identity drifted."


def _run_pair(*, dynamic: bool) -> None:
    """
    Run one cold-save vs warm-cache pair and print the parity report.

    Contract:
        - The cold leg MUST stage manifest-shaped payloads only; a legacy
          payload is a hard failure naming the epic's original surgery
          target as live.
        - The warm leg MUST have at least one cache-served spell, otherwise
          the pair proved nothing and fails loudly.
        - Lane timings are printed for the user-run report; no perf asserts
          (variance-prone), the numbers are the deliverable.
    """
    posture = "dynamic" if dynamic else "automatic"
    frame_name = f"cache-parity-{posture}"

    cold_spellbook, cold_conduit, cold_ids = _build_runtime(
        dynamic=dynamic,
        frame_name=frame_name,
        prepare_cache_root=True,
    )
    try:
        _assert_identity_semantics(cold_conduit, cold_ids)
        cold_counters, cold_restore = _install_seam_counters()
        try:
            cold_lanes = _measure_workloads(cold_conduit, cold_ids)
        finally:
            cold_restore()
        manifest_count, legacy_count = _audit_staged_payload_shapes(
            cold_spellbook
        )
        disk_manifest, disk_legacy = _audit_bundle_shapes_on_disk(
            cold_spellbook
        )
    finally:
        _cleanup_runtime(cold_spellbook, cold_conduit)

    assert legacy_count == 0, (
        f"[{posture}] {legacy_count} LEGACY-shaped payload(s) staged: the "
        "legacy spell-level cache save path is live again - the epic's "
        "original unification surgery applies after all."
    )
    assert manifest_count > 0, f"[{posture}] no payloads staged at all."

    warm_spellbook, warm_conduit, warm_ids = _build_runtime(
        dynamic=dynamic,
        frame_name=frame_name,
        prepare_cache_root=False,
    )
    try:
        cache_served, live_compiled = _count_cache_served_spells(
            warm_spellbook, warm_ids
        )
        _assert_identity_semantics(warm_conduit, warm_ids)
        warm_counters, warm_restore = _install_seam_counters()
        try:
            warm_lanes = _measure_workloads(warm_conduit, warm_ids)
        finally:
            warm_restore()
    finally:
        _cleanup_runtime(warm_spellbook, warm_conduit)

    assert cache_served > 0, (
        f"[{posture}] warm leg loaded ZERO spells from cache: the pair "
        "proved nothing (bundle miss or fingerprint drift)."
    )

    print(f"\n[cache-parity:{posture}] staged payloads: "
          f"manifest={manifest_count} legacy={legacy_count} "
          f"(disk: manifest={disk_manifest} legacy={disk_legacy})")
    print(f"[cache-parity:{posture}] warm-leg spells: "
          f"cache_served={cache_served} live_compiled={live_compiled}")
    for lane in (
            "warm_many4",
            "warm_unique",
            "cycle_meld1",
            "space_cycle",
            "space_hot_many",
    ):
        cold_ns = cold_lanes[lane]
        warm_ns = warm_lanes[lane]
        ratio = warm_ns / cold_ns if cold_ns else float("nan")
        print(f"[cache-parity:{posture}] {lane}: "
              f"cold={cold_ns:.0f}ns warm_cache={warm_ns:.0f}ns "
              f"ratio={ratio:.3f}")
    for name, _, _ in _SEAM_TARGETS:
        print(f"[cache-parity:{posture}] seam {name}: "
              f"cold={cold_counters[name]} warm_cache={warm_counters[name]}")


def test_cache_warm_meld_parity_automatic() -> None:
    """
    Cold-save vs warm-cache parity pair in automatic conjure posture.
    """
    _run_pair(dynamic=False)


def test_cache_warm_meld_parity_dynamic() -> None:
    """
    Cold-save vs warm-cache parity pair in dynamic conjure posture.
    """
    _run_pair(dynamic=True)


def main() -> None:
    """
    Direct-exec entry: run both posture pairs.
    """
    _run_pair(dynamic=False)
    _run_pair(dynamic=True)


if __name__ == "__main__":
    main()
