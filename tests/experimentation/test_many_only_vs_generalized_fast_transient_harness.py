"""
Experiment comparing forced generalized fast-transient versus many-only.

Purpose:
    Measure whether the dedicated `many_only` phase-10/11 family is actually
    faster than the restored generalized fast-transient path when both are run
    on the same graph topology family.

Method:
    - Reuse the `shallow_all` graph definitions for `shallow`, `wide`,
      `diamond`, and `deep`.
    - Bind only `root_a_classes + root_b_classes` as `Existence.many` so the
      compared graph topology stays the same without importing the stock
      spellspace-binding posture into the family comparison.
    - Conjure normally so phases 1-9 stay real.
    - Force phase 10/11 family selection locally for:
        - generalized fast-transient
        - many-only
    - Measure both:
        - direct `CreationContext.execute_no_hooks(...)`
        - front-door `conduit.meld(...)`

This is an experimentation surface, not production runtime code.
"""

import gc
import sys
import time
from typing import Any, Callable, Dict, Iterable, Optional, Sequence, Tuple

import pytest

from tests.component.melder.spellbook.spell_compiler_runtime_test_support import (
    get_spell_by_version_id,
    make_spellbook,
    reset_aether_runtime,
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

import benchmarks.testing_other_di.test_shallow_all as shallow_all_benchmark
from melder import Aether, Conduit, Existence
from melder.aether.conduit.meld.creation_context.creation_context_builder import (
    CreationContextBuilder,
)
from melder.aether.spellbook import spellbook as spellbook_module
from melder.aether.spellbook import (
    spellbook_creation_system as spellbook_creation_system_module,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation import (
    SpellCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.spell_codegen_strategy_builder import (
    SpellCodegenStrategyBuilder,
)
if not hasattr(spellbook_creation_system_module, "Spellbook"):
    spellbook_creation_system_module.Spellbook = spellbook_module.Spellbook

def _replace_spell_codegen_creation(
        artifact: Any,
        creation: SpellCodegenCreation,
) -> None:
    """
    Publish one forced `SpellCodegenCreation` onto the artifact.
    """
    previous_creation = artifact._spell_codegen_creation
    artifact._spell_codegen_creation = creation
    if previous_creation is not None and previous_creation is not creation:
        try:
            previous_creation.cleanup()
        except Exception:
            pass


def _build_forced_creation(
        *,
        artifact: Any,
        plan: Any,
        creation_strategy_ids: Tuple[str, ...],
        discovery_reason: str,
        selected_codegen_style_id: str,
) -> SpellCodegenCreation:
    """
    Build one forced phase-11 creation artifact using the real creation strategies.
    """
    spell_codegen_model = artifact._spell_codegen_model
    if spell_codegen_model is None or plan is None:
        raise RuntimeError(
            "Forced creation build requires spell_codegen_model and plan."
        )

    creation = SpellCodegenCreation(
        selected_strategy_ids=creation_strategy_ids,
        discovery_reason=discovery_reason,
        no_overrides_executor=None,
        overrides_executor=None,
        metadata={
            "selected_codegen_style_id": selected_codegen_style_id,
            "selected_plan_family_id": plan.plan_family_id,
            "candidate_codegen_style_ids": plan.candidate_codegen_style_ids,
        },
    )
    builder = SpellCodegenStrategyBuilder()
    try:
        strategies = builder.get_strategies(creation_strategy_ids)
        for strategy in strategies:
            strategy.apply(
                spell_codegen_model,
                plan,
                creation,
            )
    finally:
        builder.cleanup()
    _replace_spell_codegen_creation(artifact, creation)
    return creation


def _build_live_generalized_creation_context(
        *,
        spell: Any,
) -> Any:
    """
    Build one `CreationContext` from the live post-conjure generalized artifact.
    """
    spell._cleanup_creation_context()
    return CreationContextBuilder.build(spell)


def _build_forced_many_only_creation_context_from_live_plan(
        *,
        spell: Any,
) -> Any:
    """
    Build one forced many-only `CreationContext` from the live post-conjure plan.

    Contract:
        - Reuses the live phase-10 plan already produced by normal conjure.
        - Replaces only the phase-11 creation-family output.
        - Leaves planner shape intact so the comparison isolates the phase-11
          family/runtime difference.
    """
    artifact = spell._compiler_artifact
    live_plan = artifact._spell_codegen_plan
    if live_plan is None:
        raise RuntimeError("Forced many-only creation requires a live codegen plan.")
    _build_forced_creation(
        artifact=artifact,
        plan=live_plan,
        creation_strategy_ids=("many_only_codegen_creation",),
        discovery_reason="forced_many_only_creation_family_on_live_plan",
        selected_codegen_style_id="generalized_many_only",
    )
    spell._cleanup_creation_context()
    return CreationContextBuilder.build(spell)


def _measure_ns(
        *,
        action: Callable[[], Any],
        iterations: int,
        warmup: int,
) -> float:
    """
    Measure one prepared action in nanoseconds per iteration.
    """
    for _ in range(warmup):
        action()
    start_ns = time.perf_counter_ns()
    for _ in range(iterations):
        action()
    end_ns = time.perf_counter_ns()
    return (end_ns - start_ns) / iterations


def _build_graph_class_sequence(graph: Any) -> Tuple[type, ...]:
    """
    Build the compared graph-class sequence for one `shallow_all` graph.

    Contract:
        - Preserves the benchmark graph topology classes from `root_a_classes`
          and `root_b_classes`.
        - Excludes `spellspace_classes` so the compared visible spell set is
          all-`many`.
        - Preserves first-seen order while de-duplicating shared classes.
    """
    seen: set[type] = set()
    ordered: list[type] = []
    for cls in graph.root_a_classes + graph.root_b_classes:
        if cls in seen:
            continue
        seen.add(cls)
        ordered.append(cls)
    return tuple(ordered)


def _build_many_only_graph_environment(
        *,
        graph: Any,
) -> Tuple[Any, Any, str, str]:
    """
    Build one fresh all-`many` runtime environment for a graph topology.
    """
    reset_aether_runtime()
    spellbook = make_spellbook()
    cfg = spellbook.get_configuration()
    cfg.set_property("phase_scheduler_workers_per_spellbook", 1)
    shallow_all_benchmark._apply_melder_compilation_mode(cfg)

    spell_ids: Dict[type, str] = {}
    for cls in _build_graph_class_sequence(graph):
        spell_ids[cls] = spellbook.bind(
            spell=cls,
            existence=Existence.many,
            permissions="create",
        )

    conduit = spellbook.conjure(name="many-vs-generalized")
    root_a_id = spell_ids[graph.root_a]
    root_b_id = spell_ids[graph.root_b]
    return spellbook, conduit, root_a_id, root_b_id


def _cleanup_environment(
        *,
        spellbook: Any,
        conduit: Any,
) -> None:
    """
    Clean one fresh runtime environment.
    """
    if conduit is not None:
        try:
            conduit.permanent_cleanup()
        except Exception:
            pass
    try:
        spellbook.cleanup()
    except Exception:
        pass
    reset_aether_runtime()
    gc.collect()


def _build_creation_context_pair(
        *,
        spellbook: Any,
        conduit: Any,
        root_ids: Tuple[str, str],
        build_context: Callable[..., Any],
) -> Tuple[Any, Any, Callable[[], Any], Callable[[], Any]]:
    """
    Build creation contexts and alternating actions for both roots.
    """
    root_a_spell = get_spell_by_version_id(spellbook, root_ids[0])
    root_b_spell = get_spell_by_version_id(spellbook, root_ids[1])
    assert root_a_spell is not None
    assert root_b_spell is not None

    ctx_a = build_context(spell=root_a_spell)
    ctx_b = build_context(spell=root_b_spell)

    direct_actions = (
        lambda: ctx_a.execute_no_hooks(conduit._creations),
        lambda: ctx_b.execute_no_hooks(conduit._creations),
    )
    meld_actions = (
        lambda: conduit.meld(spell=root_ids[0]),
        lambda: conduit.meld(spell=root_ids[1]),
    )
    return (
        ctx_a,
        ctx_b,
        _make_alternating_action(direct_actions),
        _make_alternating_action(meld_actions),
    )


def _make_alternating_action(
        actions: Tuple[Callable[[], Any], Callable[[], Any]],
) -> Callable[[], Any]:
    """
    Build one alternating `root_a` / `root_b` action.
    """
    cursor = {"index": -1}

    def run() -> Any:
        cursor["index"] = (cursor["index"] + 1) % len(actions)
        return actions[cursor["index"]]()

    return run


def _benchmark_graph_pair(
        *,
        graph: Any,
        iterations: int,
        warmup: int,
) -> Dict[str, Any]:
    """
    Benchmark generalized fast-transient versus many-only for one graph.
    """
    spellbook = None
    conduit = None
    try:
        spellbook, conduit, root_a_id, root_b_id = _build_many_only_graph_environment(
            graph=graph,
        )

        _, _, generalized_direct, generalized_meld = _build_creation_context_pair(
            spellbook=spellbook,
            conduit=conduit,
            root_ids=(root_a_id, root_b_id),
            build_context=_build_live_generalized_creation_context,
        )
        generalized_direct_ns = _measure_ns(
            action=generalized_direct,
            iterations=iterations,
            warmup=warmup,
        )
        generalized_meld_ns = _measure_ns(
            action=generalized_meld,
            iterations=iterations,
            warmup=warmup,
        )

        _, _, many_only_direct, many_only_meld = _build_creation_context_pair(
            spellbook=spellbook,
            conduit=conduit,
            root_ids=(root_a_id, root_b_id),
            build_context=_build_forced_many_only_creation_context_from_live_plan,
        )
        many_only_direct_ns = _measure_ns(
            action=many_only_direct,
            iterations=iterations,
            warmup=warmup,
        )
        many_only_meld_ns = _measure_ns(
            action=many_only_meld,
            iterations=iterations,
            warmup=warmup,
        )

        return {
            "graph": graph.name,
            "generalized_direct_ns": generalized_direct_ns,
            "many_only_direct_ns": many_only_direct_ns,
            "direct_ratio": many_only_direct_ns / generalized_direct_ns,
            "generalized_meld_ns": generalized_meld_ns,
            "many_only_meld_ns": many_only_meld_ns,
            "meld_ratio": many_only_meld_ns / generalized_meld_ns,
        }
    finally:
        if spellbook is not None and conduit is not None:
            _cleanup_environment(spellbook=spellbook, conduit=conduit)


def _format_results_table(rows: Sequence[Dict[str, Any]]) -> str:
    """
    Format one compact many-only versus generalized results table.
    """
    headers = (
        "graph",
        "generalized_direct_ns",
        "many_only_direct_ns",
        "direct_ratio",
        "generalized_meld_ns",
        "many_only_meld_ns",
        "meld_ratio",
    )
    string_rows = [
        {
            "graph": row["graph"],
            "generalized_direct_ns": f"{row['generalized_direct_ns']:.3f}",
            "many_only_direct_ns": f"{row['many_only_direct_ns']:.3f}",
            "direct_ratio": f"{row['direct_ratio']:.6f}",
            "generalized_meld_ns": f"{row['generalized_meld_ns']:.3f}",
            "many_only_meld_ns": f"{row['many_only_meld_ns']:.3f}",
            "meld_ratio": f"{row['meld_ratio']:.6f}",
        }
        for row in rows
    ]
    widths = {header: len(header) for header in headers}
    for row in string_rows:
        for header in headers:
            widths[header] = max(widths[header], len(row[header]))

    def _line(values: Dict[str, str]) -> str:
        return "| " + " | ".join(
            values[header].ljust(widths[header]) for header in headers
        ) + " |"

    lines = [
        _line({header: header for header in headers}),
        _line({header: "-" * widths[header] for header in headers}),
    ]
    for row in string_rows:
        lines.append(_line(row))
    return "\n".join(lines)


def _selected_graphs() -> Tuple[Any, ...]:
    """
    Return the graph set compared by this harness.
    """
    selected = []
    for graph in shallow_all_benchmark._selected_graphs():
        if graph.name not in {"shallow", "wide", "diamond", "deep"}:
            continue
        selected.append(graph)
    return tuple(selected)


@pytest.mark.timeout(300)
def test_many_only_vs_generalized_fast_transient_harness() -> None:
    """
    Compare forced many-only against forced generalized fast-transient.

    Contract:
        - Reuses the `shallow_all` graph topology family.
        - Forces phase-10/11 family selection locally.
        - Prints a compact table for direct-creation and front-door meld timing.
        - Does not assert a winner; this is an experimentation/reporting
          surface, not a policy test.
    """
    iterations = 10000
    warmup = 2000
    rows = [
        _benchmark_graph_pair(
            graph=graph,
            iterations=iterations,
            warmup=warmup,
        )
        for graph in _selected_graphs()
    ]
    print("\n[many-vs-generalized-fast-transient]")
    print(_format_results_table(rows))
    assert rows
