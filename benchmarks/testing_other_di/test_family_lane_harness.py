"""
Unified family-lane harness: solo / many_only(transient) / many_only(step-plan) /
generalized -- proves WHICH emitted executor each binding shape compiles to, and
times the warm per-meld cost of each, on the same machine in one run.

Why this exists
---------------
The discovery rules (phase 10) route a spell graph to one of three creation
families by its *visible spell set*:

  - solo        : exactly 1 visible spell (any existence)
  - many_only: >1 visible spell AND everyone is many
  - generalized : everything else (mixed existences, singletons, etc.)

Each family emits a DIFFERENT executor source, and we must benchmark the real
one -- not assume. This harness captures every emitted source via a
`builtins.compile` wrapper (robust: catches the compile regardless of which
module triggers it) and prints each `source_name`, so routing is proven, not
guessed. Expected source_names:

  solo                       -> <solo_no_overrides_codegen_creation: ...>
  many_only, no disposal -> <melder_no_overrides_codegen_creation_transient_executor>
  many_only, WITH disposal -> <melder_no_overrides_codegen_creation_step_executor_disposal_aware>
  generalized (mixed) -> <melder_generalized_no_overrides_step_factory>

The many_only WITH-disposal lane is the one that matters for porting the
generalized create-path optimizations (locals mode, alias trim, caller-guard
hoist): many graphs drop out of the fast transient-unrolled path the moment
ANY step carries disposal methods, and land on the dict-based step-plan
emitter. The deep_layers mocks have no disposal methods, so this file defines a
small disposal-bearing all-many graph locally to reach that lane.

Run (fresh process so nothing is pre-cached), from repo root:
  pytest -s -k test_family_lane_routing_proof benchmarks/testing_other_di/test_family_lane_harness.py
  pytest -s -k test_family_lane_warm_timing benchmarks/testing_other_di/test_family_lane_harness.py

Iteration counts can be overridden:
  DI_LANE_ITERS=200000 DI_DISP_ITERS=20000 pytest -s -k test_family_lane_warm_timing ...
"""

import sys
from pathlib import Path

# benchmarks/ has no conftest and pyproject does not add src/ to the path, so a
# plain-terminal pytest cannot import `melder` (PyCharm adds source roots; a bare
# shell does not). Put repo-root/src + repo-root on sys.path so this runs anywhere.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
for _candidate in (str(_PROJECT_ROOT / "src"), str(_PROJECT_ROOT)):
    if _candidate not in sys.path:
        sys.path.insert(0, _candidate)

import builtins
import gc
import os
import time
from typing import Callable, Dict, List, Tuple, Type

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.deep_layers import (
    get_depth_5_classes,
    Depth5LeafA,
)
from benchmarks.p_core_affinity.p_core_affinity import (
    pin_current_process_to_p_cores,
)


# ---------------------------------------------------------------------------
# Disposal-bearing all-many graph (local): every class exposes `cleanup`, bound
# with disposal_method_names=["cleanup"] so has_disposal_methods is True. This is
# what forces a many_only graph off the transient path onto the step-plan emitter.
# ---------------------------------------------------------------------------
class DispLeafA:
    def __init__(self) -> None:
        self.marker = "DLA"

    def cleanup(self) -> None:
        pass


class DispLeafB:
    def __init__(self) -> None:
        self.marker = "DLB"

    def cleanup(self) -> None:
        pass


class DispMidA:
    def __init__(self, left: DispLeafA, right: DispLeafB) -> None:
        self.left = left
        self.right = right

    def cleanup(self) -> None:
        pass


class DispMidB:
    def __init__(self, left: DispLeafA, right: DispLeafB) -> None:
        self.left = left
        self.right = right

    def cleanup(self) -> None:
        pass


class DispRoot:
    def __init__(self, left: DispMidA, right: DispMidB) -> None:
        self.left = left
        self.right = right

    def cleanup(self) -> None:
        pass


_DISP_CLASSES: Tuple[Type, ...] = (
    DispLeafA,
    DispLeafB,
    DispMidA,
    DispMidB,
    DispRoot,
)


# Mixed-disposal all-many graph: only MixMidA + MixRoot declare disposal, so the
# step-plan emitter registers those two and emits pure constructors (no creations
# routing, no lock) for the rest -- exercises the per-step disposal gate plus the
# creations_N dead-alias trim.
class MixLeafA:
    def __init__(self) -> None:
        self.marker = "MLA"


class MixLeafB:
    def __init__(self) -> None:
        self.marker = "MLB"


class MixMidA:
    def __init__(self, left: MixLeafA, right: MixLeafB) -> None:
        self.left = left
        self.right = right

    def cleanup(self) -> None:
        pass


class MixMidB:
    def __init__(self, left: MixLeafA, right: MixLeafB) -> None:
        self.left = left
        self.right = right


class MixRoot:
    def __init__(self, left: MixMidA, right: MixMidB) -> None:
        self.left = left
        self.right = right

    def cleanup(self) -> None:
        pass


_MIXED_CLASSES: Tuple[Type, ...] = (
    MixLeafA,
    MixLeafB,
    MixMidA,
    MixMidB,
    MixRoot,
)
_MIXED_DISPOSAL_CLASSES = {MixMidA, MixRoot}


def _reset_aether() -> None:
    """Rebind a fresh Aether singleton so each case is fully isolated."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _new_spellbook(tag: str) -> Spellbook:
    """Fresh, single-threaded, caching-DISABLED spellbook for one lane."""
    _reset_aether()
    spellbook = Spellbook(aetheric_frame=f"lane-harness-{tag}")
    spellbook.get_configuration().set_property(
        "phase_scheduler_workers_per_spellbook", 1
    )
    # Disable system caching so each case compiles fresh and nothing leaks across
    # cases. Disposal is set PER BIND (writes the fresh per-spellbook
    # _configured_disposal_method_names), never via the idempotent frame config
    # property, which persists across spellbooks and raises on re-set.
    spellbook.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
        system_caching_enabled=False,
    )
    return spellbook


# ---------------------------------------------------------------------------
# Lane binders: each returns the root spell_id to meld. Shapes are chosen to land
# on a specific discovery family + emitter.
# ---------------------------------------------------------------------------
def _bind_solo(spellbook: Spellbook) -> str:
    """Exactly ONE visible spell (a no-dep leaf, many) -> solo family."""
    return spellbook.bind(
        spell=Depth5LeafA, existence=Existence.many, permissions="create"
    )


def _bind_many_transient(spellbook: Spellbook) -> str:
    """Depth-5, ALL many, no disposal -> many_only -> transient unrolled."""
    classes = get_depth_5_classes()
    root_id = ""
    for cls in classes:
        spell_id = spellbook.bind(
            spell=cls, existence=Existence.many, permissions="create"
        )
        if cls is classes[-1]:
            root_id = spell_id
    return root_id


def _bind_many_stepplan(spellbook: Spellbook) -> str:
    """ALL many WITH disposal -> many_only -> step-plan (dict) emitter."""
    root_id = ""
    for cls in _DISP_CLASSES:
        spell_id = spellbook.bind(
            spell=cls,
            existence=Existence.many,
            permissions="create",
            disposal_method_names=["cleanup"],
        )
        if cls is _DISP_CLASSES[-1]:
            root_id = spell_id
    return root_id


def _bind_many_mixed_disposal(spellbook: Spellbook) -> str:
    """ALL many, MIXED disposal -> step-plans. Every bind passes ["cleanup"], so the
    spellbook's configured disposal set is {"cleanup"} (same as the all-disposal
    lane); per-class disposal is then decided by whether the class actually
    defines cleanup -- only MixMidA + MixRoot do, the rest are non-disposal."""
    root_id = ""
    for cls in _MIXED_CLASSES:
        spell_id = spellbook.bind(
            spell=cls,
            existence=Existence.many,
            permissions="create",
            disposal_method_names=["cleanup"],
        )
        if cls is _MIXED_CLASSES[-1]:
            root_id = spell_id
    return root_id


def _bind_generalized(spellbook: Spellbook) -> str:
    """Depth-5, all many EXCEPT one unique leaf (mixed) -> generalized."""
    classes = get_depth_5_classes()
    first_leaf = classes[0]
    root_id = ""
    for cls in classes:
        existence = Existence.unique if cls is first_leaf else Existence.many
        spell_id = spellbook.bind(
            spell=cls, existence=existence, permissions="create"
        )
        if cls is classes[-1]:
            root_id = spell_id
    return root_id


_LANES: Tuple[Tuple[str, Callable[[Spellbook], str], str], ...] = (
    ("solo", _bind_solo, "<solo_no_overrides_codegen_creation:"),
    ("many_transient", _bind_many_transient, "transient_executor"),
    ("many_stepplan(disposal)", _bind_many_stepplan, "step_executor_disposal"),
    ("many_mixed(disposal)", _bind_many_mixed_disposal, "step_executor_disposal"),
    ("generalized(mixed)", _bind_generalized, "generalized_no_overrides_step_factory"),
)


def _capture_sources(
    tag: str, bind_fn: Callable[[Spellbook], str]
) -> List[Tuple[str, str]]:
    """Build the graph once, capturing every emitted executor source_name."""
    captured: List[Tuple[str, str]] = []
    original_compile = builtins.compile

    def _cap(source, filename, mode, *args, **kwargs):
        if (
            isinstance(filename, str)
            and isinstance(source, str)
            and filename.startswith("<")
            and (
                "executor" in filename
                or "creation" in filename
                or "melder" in filename
                or "solo" in filename
                or "factory" in filename
            )
        ):
            captured.append((filename, source))
        return original_compile(source, filename, mode, *args, **kwargs)

    builtins.compile = _cap
    try:
        spellbook = _new_spellbook(tag)
        root_id = bind_fn(spellbook)
        conduit = spellbook.conjure(name=f"lane-{tag}")
        try:
            conduit.meld(spell=root_id)
        finally:
            conduit.cleanup()
    finally:
        builtins.compile = original_compile
    # de-dup by source text
    seen = set()
    rows: List[Tuple[str, str]] = []
    for name, src in captured:
        if src in seen:
            continue
        seen.add(src)
        rows.append((name, src))
    return rows


def _warm_per_meld_us(
    tag: str,
    bind_fn: Callable[[Spellbook], str],
    *,
    iterations: int,
    repeats: int,
    warmup: int,
) -> float:
    """Best (least-noisy) warm per-meld time in microseconds for one lane."""
    samples: List[float] = []
    for _ in range(repeats):
        spellbook = _new_spellbook(tag)
        root_id = bind_fn(spellbook)
        conduit = spellbook.conjure(name=f"lane-{tag}")
        try:
            conduit.meld(spell=root_id)  # cold: compile + first build
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
                gc.enable()
            samples.append((elapsed / iterations) * 1_000_000.0)
        finally:
            conduit.cleanup()
    return min(samples)


def test_family_lane_routing_proof() -> None:
    """Print the emitted executor source_name(s) each lane compiles to."""
    pin = pin_current_process_to_p_cores(strict=False)
    print(
        f"\n[routing proof] p-core pin applied={pin.get('applied')} "
        f"reason={pin.get('reason')} cpus={pin.get('selected_affinity')}"
    )
    for tag, bind_fn, expected_substr in _LANES:
        rows = _capture_sources(tag, bind_fn)
        print(f"\n========== lane = {tag} ==========")
        print(f"  expected source_name to contain: {expected_substr!r}")
        hit = False
        for name, src in rows:
            marker = "DICT" if "instance_results" in src else "no-dict"
            flag = ""
            if expected_substr in name:
                hit = True
                flag = "  <== MATCH"
            print(f"    [{marker:7s}] lines={src.count(chr(10)) + 1:4d}  {name}{flag}")
        print(f"  routing match: {hit}")
        # Soft: at least SOMETHING was captured for every lane.
        assert rows, f"lane {tag}: no executor source captured at all"


def test_family_lane_warm_timing() -> None:
    """Warm per-meld timing for each lane (no thresholds; prints numbers)."""
    pin = pin_current_process_to_p_cores(strict=False)

    iters = int(os.environ.get("DI_LANE_ITERS", "100000"))
    # disposal-many registers an entry per meld (the list grows), so keep its
    # iteration count lower to stop registry growth from dominating the sample.
    disp_iters = int(os.environ.get("DI_DISP_ITERS", "10000"))
    repeats = 4
    warmup = 3_000

    print(
        f"\n[warm timing] best of {repeats} runs, single-thread, "
        f"caching disabled\n  p-core pin applied={pin.get('applied')} "
        f"reason={pin.get('reason')} cpus={pin.get('selected_affinity')}"
    )
    results: Dict[str, float] = {}
    for tag, bind_fn, _expected in _LANES:
        n = disp_iters if "disposal" in tag else iters
        us = _warm_per_meld_us(
            tag, bind_fn, iterations=n, repeats=repeats, warmup=warmup
        )
        results[tag] = us
        print(
            f"  {tag:26s}: {us:9.4f} us/meld  "
            f"({1e6 / us:>12,.0f} melds/s)  [iters={n:,}]"
        )
    assert all(v > 0.0 for v in results.values())
