"""Meld-only lock-order probe (row 4). Author: melder_0, 2026-09-25.

Question: can two ordinary first-time melds on one root conduit form the store/Spell cycle with no purge?
Thread A melds PReq (unique_per_conduit or lineage) -> its door holds the store lock, then its USvc step
asks for USvc's Spell lock. A is paused exactly at that request. Thread C melds USvc (unique) -> its door
holds USvc's Spell lock, and its disposal-bearing MLeaf step registers into the store. C's store request is
refused (ProbeWouldBlock) instead of waited on, so a real cycle is recorded without hanging the process.
Control: MLeaf without disposal methods. Diagnostic only; no production file changes.
"""
import hashlib
import json
import sys
from pathlib import Path
from threading import Thread

import pytest

import context_compass.artifacts.override_occurrence_discovery_20260924.graph_slice_probe as gsp
from context_compass.artifacts.override_structural_discovery_20260924.native_lock_probe import (
    ObservedLock,
    Trace,
)
from melder.aether.spellbook.existence.existence import Existence


class MLeaf:
    """Transient dependency that optionally declares a disposal method."""

    def __init__(self) -> None:
        """Start open."""
        self.closed = False

    def close(self) -> None:
        """Disposal method used when the probe declares one."""
        self.closed = True


class USvc:
    """Frame-wide singleton holding one MLeaf."""

    def __init__(self, leaf: MLeaf) -> None:
        """Borrow the leaf."""
        self.leaf = leaf


class PReq:
    """Per-conduit (or lineage) consumer of the unique service."""

    def __init__(self, svc: USvc) -> None:
        """Borrow the service."""
        self.svc = svc


class ProbeRoot:
    """Harmless world root."""

    def __init__(self) -> None:
        """No dependencies."""


class DisposalWorld(gsp.World):
    """World variant that can declare a disposal method on MLeaf."""

    def setup_disposal_model(self, name: str, leaf_disposal: bool, parent_existence: Existence) -> None:
        """Mirror World.setup_model with the probe's three bindings."""
        self.graph, self.root_type = name, ProbeRoot
        gsp.Aether._reset_singleton_for_tests()
        gsp.Spellbook._aether = gsp.Aether()
        gsp.Conduit._aether = gsp.Spellbook._aether
        config = gsp.SpellbookConfiguration(f"meldonly-{name}").with_defaults()
        config.with_phase_scheduler_workers(1)
        frame = gsp.configure_frame_posture_for_spellbook_configuration(config, dynamic=False)
        frame.with_system_caching_enabled(False)
        self.book = gsp.Spellbook(aetheric_frame=config._aether_frame, configuration=config)
        self.book.bind(spell=MLeaf, existence=Existence.many, permissions="create",
                       disposal_method_names=["close"] if leaf_disposal else None)
        self.book.bind(spell=USvc, existence=Existence.unique, permissions="create")
        self.book.bind(spell=PReq, existence=parent_existence, permissions="create")
        self.root_id = self.book.bind(spell=ProbeRoot, existence=Existence.many, permissions="create")
        self.conduit = self.book.conjure(name="probe", dynamic=False)


def meld_only_case(leaf_disposal: bool, parent_existence: Existence) -> dict[str, object]:
    """Run one interleaving and report whether thread C would block on the store A holds."""
    world = DisposalWorld()
    trace = Trace()
    try:
        world.setup_disposal_model(f"{parent_existence.name}-{leaf_disposal}", leaf_disposal, parent_existence)
        conduit = world.conduit
        conduit.meld(spell=PReq)  # warm the compiled contexts
        assert conduit.purge(PReq) == 1
        assert conduit.purge(USvc) == 1
        svc = next(s for s in world.book._spell_id_pool.values() if s.spell is USvc)
        store = (conduit._meld._root_creations if parent_existence is Existence.unique_per_conduit_lineage
                 else conduit._meld._conduit_creations)
        store_lock = ObservedLock(store._lock, trace, "store")
        svc_lock = ObservedLock(svc._lock, trace, "svc_spell")
        svc_lock.pause_thread = "meld-A"
        store_lock.refuse_thread = "meld-C"
        results: dict[str, list[object]] = {"A": [], "C": []}
        errors: dict[str, list[str]] = {"A": [], "C": []}

        def run(tag: str, spell_type: type) -> None:
            """Call the public meld door and capture any outcome."""
            try:
                results[tag].append(conduit.meld(spell=spell_type))
            except BaseException as error:  # diagnostic capture only
                errors[tag].append(f"{type(error).__name__}: {error} <- {error.__cause__!r}")

        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(store, "_lock", store_lock)
            patch.setattr(svc, "_lock", svc_lock)
            thread_a = Thread(target=run, args=("A", PReq), name="meld-A", daemon=True)
            thread_a.start()
            try:
                a_paused_at_svc_lock = svc_lock.paused.wait(4)
                a_holds_store = ("meld-A", "store", "acquired") in trace.rows
                thread_c = Thread(target=run, args=("C", USvc), name="meld-C", daemon=True)
                thread_c.start()
                thread_c.join(3)
                c_stuck_elsewhere = thread_c.is_alive()
            finally:
                svc_lock.resume.set()
                thread_a.join(10)
                thread_c.join(10)
        c_would_block_on_store = ("meld-C", "store", "would_block") in trace.rows
        c_held_svc_lock = ("meld-C", "svc_spell", "acquired") in trace.rows
        return {
            "parent_existence": parent_existence.name,
            "leaf_disposal": leaf_disposal,
            "same_store_for_parent_and_unique": svc._owner_creations is store,
            "A_held_store_when_requesting_svc_lock": a_paused_at_svc_lock and a_holds_store,
            "C_held_svc_lock": c_held_svc_lock,
            "C_would_block_on_store_held_by_A": c_would_block_on_store,
            "cycle_formed": bool(a_paused_at_svc_lock and a_holds_store and c_held_svc_lock
                                 and c_would_block_on_store),
            "C_stuck_elsewhere": c_stuck_elsewhere,
            "A_completed": bool(results["A"]) and not thread_a.is_alive(),
            "A_errors": errors["A"],
            "C_errors": errors["C"],
            "trace": trace.rows,
        }
    finally:
        world.cleanup()


def main() -> None:
    """Run disposal and control cases for per-conduit and lineage parents."""
    files = [
        "src/melder/aether/conduit/creations/creations.py",
        "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py",
        "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py",
        "src/melder/aether/spellbook/spell_compiler/system/validation/scope_ordering_strategy.py",
    ]
    cases = [meld_only_case(disposal, existence)
             for existence in (Existence.unique_per_conduit, Existence.unique_per_conduit_lineage)
             for disposal in (True, False)]
    report = {
        "python": sys.version,
        "gil_enabled": getattr(sys, "_is_gil_enabled", lambda: True)(),
        "source_sha256": {f: hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in files},
        "cases": cases,
        "limits": "Scheduling instrumentation; C's contended store request is refused, not waited on.",
    }
    Path("meld_only_lock_results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    for case in cases:
        print({k: v for k, v in case.items() if k != "trace"})


if __name__ == "__main__":
    main()
