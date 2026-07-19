"""
Probe: collection-DI wiring failure (epic 2026-07-05_collection_di_list_wiring_broken).

Run on 3.14t from the repo root:

    python codex/context_compass/artifacts/2026-07-05_collection_di_probe.py

Purpose:
    One run that settles every open unknown in the epic at once:
      P1  Phase-1 classification of `plugins: List[IPlugin]` and
          `engines: List[Engine]` (di_shape, element annotation, identity).
      P3  Phase-3 resolution results per dependency (hypothesis A vs B) and
          whether the candidate index or the scan path ran.
      TOP The exact SpellSocketDescriptor rows phase 3 recorded.
      P6  What EmptyCollectionStrategy actually sees per scoped spell id
          (topology present? is_collection? is_optional? target ids?).

Contract:
    - READ-ONLY probe: every monkeypatched wrapper delegates to the real
      implementation unchanged; no melder source file is modified.
    - print() is intentional here; this is a throwaway diagnostic artifact,
      not library/runtime code.
    - Scenarios mirror the failing c1 tests byte-for-byte where it matters
      (typing.List element forms, bind order, single-worker scheduler).
"""
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

# Path bootstrap: the repo installs nothing into the venv; tests import melder
# through the runner's path setup, so this standalone probe must add src/
# itself. parents[3] = repo root (artifacts -> context_compass -> codex -> root).
_SRC = str(Path(__file__).resolve().parents[3] / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_3 import (
    CompilerPhase3,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_requirements_finder import (
    SpellRequirementsFinder,
)
from melder.aether.spellbook.spell_compiler.system.validation.empty_collection_strategy import (
    EmptyCollectionStrategy,
)


# --------------------------------------------------------------------------- #
# Doubles (mirroring test_spellbook_integration_resolution_break_matrix.py)
# --------------------------------------------------------------------------- #
class IPlugin(Protocol):
    """Collection frame."""


class PluginA:
    """First IPlugin implementation."""

    def __init__(self) -> None:
        self.tag = "a"


class PluginB:
    """Second IPlugin implementation."""

    def __init__(self) -> None:
        self.tag = "b"


class PluginC:
    """Third IPlugin implementation."""

    def __init__(self) -> None:
        self.tag = "c"


class NeedsPlugins:
    """C1 consumer (collection over a Protocol element)."""

    def __init__(self, plugins: List[IPlugin]) -> None:
        self.plugins = plugins


class Engine:
    """Concrete engine provider."""

    def __init__(self) -> None:
        self.kind = "engine"


class NeedsEngineList:
    """C1 consumer over a concrete element type."""

    def __init__(self, engines: List[Engine]) -> None:
        self.engines = engines


print(f"[ids] id(IPlugin)={id(IPlugin):#x}  id(Engine)={id(Engine):#x}")


# --------------------------------------------------------------------------- #
# Probes (delegating wrappers; installed once at import)
# --------------------------------------------------------------------------- #
_real_classify = SpellRequirementsFinder._classify_parameter
_real_collection = CompilerPhase3._resolve_collection_by_annotation
_real_single = CompilerPhase3._resolve_single_by_annotation
_real_topology = CompilerPhase3._build_local_topology
_real_p6_run = EmptyCollectionStrategy.run


def _probe_classify(self, *, param_name, annotation, has_annotation,
                    default_value, has_default):
    result = _real_classify(
        self,
        param_name=param_name,
        annotation=annotation,
        has_annotation=has_annotation,
        default_value=default_value,
        has_default=has_default,
    )
    di_shape, is_optional, element, spellmap = result
    print(
        f"[P1 classify] param={param_name!r} ann={annotation!r} "
        f"(type={type(annotation).__name__}, id={id(annotation):#x}) "
        f"-> shape={di_shape.name} optional={is_optional} "
        f"element={element!r} (id={id(element):#x})"
    )
    return result


def _probe_collection(self, spellbook, dep, candidate_index=None):
    result = _real_collection(self, spellbook, dep, candidate_index)
    names = [s.spell_name for s in result.values()]
    print(
        f"[P3 collection] param={dep.param_name!r} "
        f"target_ann={dep.target_annotation!r} "
        f"(id={id(dep.target_annotation):#x}) "
        f"index_used={candidate_index is not None} "
        f"-> len={len(result)} names={names}"
    )
    if not result:
        pool_view = [
            (
                s.spell_name,
                repr(s.spellframe),
                hex(id(s.spellframe)) if s.spellframe is not None else None,
            )
            for s in spellbook._spell_id_pool.values()
        ]
        print(f"[P3 collection]   EMPTY. pool frames={pool_view}")
    return result


def _probe_single(self, spell, spellbook, dep, candidate_index=None):
    try:
        result = _real_single(self, spell, spellbook, dep, candidate_index)
    except RuntimeError as exc:
        print(
            f"[P3 single] param={dep.param_name!r} "
            f"target_ann={dep.target_annotation!r} RAISED: {exc}"
        )
        raise
    print(
        f"[P3 single] param={dep.param_name!r} "
        f"target_ann={dep.target_annotation!r} -> len={len(result)}"
    )
    return result


def _probe_topology(self, spell, graph, socket_targets):
    topology = _real_topology(self, spell, graph, socket_targets)
    rows = [
        (
            s.param_name,
            s.socket_kind.name,
            f"coll={s.is_collection}",
            f"opt={s.is_optional}",
            f"targets={len(s.target_spell_ids)}",
        )
        for s in topology.iter_sockets()
    ]
    print(f"[P3 topology] spell={spell.spell_name!r} sockets={rows}")
    return topology


def _probe_p6_run(self, *, index, blueprints, phase4_results, broken_spell_ids,
                  spell_system_states, spell_lookup, diagnostics, cancel_event):
    print(f"[P6 empty-collection] scoped_ids={list(index.nodes.keys())}")
    for spell_id in index.nodes.keys():
        topology = spell_system_states.get_local_topology_by_id(spell_id)
        if topology is None:
            print(f"[P6 empty-collection]   {spell_id[:12]}... topology=None")
            continue
        rows = [
            (
                s.param_name,
                f"coll={s.is_collection}",
                f"opt={s.is_optional}",
                f"targets={len(s.target_spell_ids)}",
            )
            for s in topology.iter_sockets()
        ]
        print(f"[P6 empty-collection]   {spell_id[:12]}... sockets={rows}")
    before = len(diagnostics)
    _real_p6_run(
        self,
        index=index,
        blueprints=blueprints,
        phase4_results=phase4_results,
        broken_spell_ids=broken_spell_ids,
        spell_system_states=spell_system_states,
        spell_lookup=spell_lookup,
        diagnostics=diagnostics,
        cancel_event=cancel_event,
    )
    emitted = diagnostics[before:]
    print(
        f"[P6 empty-collection] emitted={len(emitted)} "
        f"codes={[d.code for d in emitted]}"
    )


SpellRequirementsFinder._classify_parameter = _probe_classify
CompilerPhase3._resolve_collection_by_annotation = _probe_collection
CompilerPhase3._resolve_single_by_annotation = _probe_single
CompilerPhase3._build_local_topology = _probe_topology
EmptyCollectionStrategy.run = _probe_p6_run


# --------------------------------------------------------------------------- #
# Scenarios
# --------------------------------------------------------------------------- #
def _fresh_spellbook() -> Spellbook:
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    spellbook = Spellbook()
    spellbook.get_configuration().set_property(
        "phase_scheduler_workers_per_spellbook", 1
    )
    return spellbook


def scenario_zero_providers() -> None:
    print("\n===== SCENARIO 1: c1_zero (NeedsPlugins, 0 providers) =====")
    spellbook = _fresh_spellbook()
    conduit = None
    try:
        spellbook.bind(
            spell=NeedsPlugins, existence=Existence.unique, permissions="create"
        )
        try:
            conduit = spellbook.conjure(name="root")
            print("[outcome] conjure SUCCEEDED (test expects a raise)")
        except Exception as exc:
            print(f"[outcome] conjure RAISED {type(exc).__name__}: {exc}")
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def scenario_three_providers() -> None:
    print("\n===== SCENARIO 2: c1_three (PluginA/B/C + NeedsPlugins) =====")
    spellbook = _fresh_spellbook()
    conduit = None
    try:
        spellbook.bind(
            spell=PluginA, existence=Existence.unique, permissions="create",
            spellframe=IPlugin,
        )
        spellbook.bind(
            spell=PluginB, existence=Existence.unique, permissions="create",
            spellframe=IPlugin, binding_name="b",
        )
        spellbook.bind(
            spell=PluginC, existence=Existence.unique, permissions="create",
            spellframe=IPlugin, binding_name="c",
        )
        spellbook.bind(
            spell=NeedsPlugins, existence=Existence.unique, permissions="create"
        )
        conduit = spellbook.conjure(name="root")
        try:
            instance = conduit.meld(spell=NeedsPlugins)
            print(
                f"[outcome] meld SUCCEEDED plugins type="
                f"{type(instance.plugins).__name__} "
                f"len={len(instance.plugins) if isinstance(instance.plugins, list) else 'n/a'}"
            )
        except Exception as exc:
            print(f"[outcome] meld RAISED {type(exc).__name__}: {exc}")
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


def scenario_concrete_element() -> None:
    print("\n===== SCENARIO 3: c1_concrete (Engine + NeedsEngineList) =====")
    spellbook = _fresh_spellbook()
    conduit = None
    try:
        spellbook.bind(
            spell=Engine, existence=Existence.unique, permissions="create",
            spellframe=Engine,
        )
        spellbook.bind(
            spell=NeedsEngineList, existence=Existence.unique,
            permissions="create",
        )
        conduit = spellbook.conjure(name="root")
        try:
            instance = conduit.meld(spell=NeedsEngineList)
            print(
                f"[outcome] meld SUCCEEDED engines type="
                f"{type(instance.engines).__name__} value={instance.engines!r}"
            )
        except Exception as exc:
            print(f"[outcome] meld RAISED {type(exc).__name__}: {exc}")
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()


if __name__ == "__main__":
    scenario_zero_providers()
    scenario_three_providers()
    scenario_concrete_element()
    print("\n[probe] done")
