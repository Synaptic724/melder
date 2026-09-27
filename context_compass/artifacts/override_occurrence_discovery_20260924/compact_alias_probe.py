"""Compare compact selection/codegen/hydration with the expanded alias oracle.

Real Melder fixtures qualify a bounded adapter. Synthetic shared-chain graphs
measure representation scaling without asking native compilation to enumerate
exponentially many paths. No native Meld speedup or lock safety is claimed.
"""

import ast
import hashlib
import json
import marshal
import sys
from contextlib import ExitStack
from datetime import UTC, datetime
from functools import partial
from pathlib import Path
from time import perf_counter_ns

import pytest

from context_compass.artifacts.override_occurrence_discovery_20260924.alias_demand_probe import (
    AliasInputConflict,
    UnequalDepthRoot,
    Wrapper,
)
from context_compass.artifacts.override_occurrence_discovery_20260924.compact_alias_emitter import (
    CompactEmitter,
)
from context_compass.artifacts.override_occurrence_discovery_20260924.compact_alias_plan import (
    CompactGraph,
    CompactPlan,
)
from context_compass.artifacts.override_occurrence_discovery_20260924.conditional_alias_plan import (
    ConditionalAliasPlan,
)
from context_compass.artifacts.override_occurrence_discovery_20260924.conditional_alias_probe import (
    CachedTokenParent,
    FallbackRoot,
    FreshTokenParent,
    ServiceWithToken,
    observe,
)
from context_compass.artifacts.override_occurrence_discovery_20260924.graph_slice_probe import (
    Branch,
    CollectionRoot,
    FiveRoot,
    Leaf,
    PairRoot,
    SliceProbe,
    Token,
    World,
)
from context_compass.artifacts.override_structural_discovery_20260924.review_alias_demand import (
    CachedParent,
    FreshParent,
    ReuseAliasRoot,
    SharedService,
)
from melder.aether.spellbook.existence.existence import Existence
from tests.experimentation.test_melder_creation_overrides_performance import (
    _source_fingerprints,
)


class CountedFactory:
    """Count synthetic constructor calls independently of selector or graph metadata."""

    def __init__(self) -> None:
        """Start a fresh counter for one synthetic evaluation."""
        self.calls = 0

    def __call__(self, **kwargs: object) -> dict[str, object]:
        """Return only explicit constructor inputs, incrementing the owned counter."""
        self.calls += 1
        return kwargs


def projection(result: object) -> tuple:
    """Describe fixture outputs through values and meaningful alias identities."""
    if isinstance(result, PairRoot):
        return (result.left.token.value, result.right.token.value,
                result.left is result.right, result.left.token is result.right.token)
    if isinstance(result, UnequalDepthRoot):
        return result.direct is result.wrapped.branch, result.direct.token.value
    if isinstance(result, ReuseAliasRoot):
        return result.cached.service.value, result.fresh.service.value, result.cached.service is result.fresh.service
    if isinstance(result, FallbackRoot):
        value = result.fresh.service.token
        return (value.value if isinstance(value, Token) else value,
                result.cached.service is result.fresh.service)
    assert isinstance(result, CollectionRoot)
    return (result.items,)


def run_case(
    name: str, root: type, bindings: tuple[tuple[type, Existence], ...],
    raw: dict[str, object], reuse_specs: tuple[dict[type, object], ...],
) -> list[dict[str, object]]:
    """Compare four independent execution forms against the prior alias oracle.

    The native physical adapter is built before the expanded oracle exists.
    All versions retain one prepared shape across supplied reuse outcomes.
    Constructor counts and observable values/identities must agree; ordering is
    recorded separately because native ordering is not qualified by this proof.
    """
    rows = []
    with ExitStack() as cleanup:
        world = World()
        cleanup.callback(world.cleanup)
        world.setup_model(name, root, bindings)
        graph = CompactGraph.from_world(world)
        cleanup.callback(graph.cleanup)
        catalog = {spell_id: world.book._spell_id_pool[spell_id].spell for spell_id, _shared, _sockets in graph.rows}
        plan = CompactPlan(graph, tuple(raw))
        cleanup.callback(plan.cleanup)
        payload = plan.dump()
        hydrated = CompactPlan.load(payload)
        cleanup.callback(hydrated.graph.cleanup)
        cleanup.callback(hydrated.cleanup)
        emitted = CompactEmitter(plan, catalog)
        cleanup.callback(emitted.cleanup)
        restored_emitter = CompactEmitter(hydrated, catalog)
        cleanup.callback(restored_emitter.cleanup)
        probe = SliceProbe(world)
        cleanup.callback(probe.cleanup)
        oracle = ConditionalAliasPlan(probe)
        cleanup.callback(oracle.cleanup)
        oracle.build(raw)
        for reuse_spec in reuse_specs:
            reuse = {next(spell_id for spell_id, constructor in catalog.items() if constructor is provider): value
                     for provider, value in reuse_spec.items()}
            try:
                expected, expected_calls = observe(partial(oracle.evaluate, raw, reuse))
            except AliasInputConflict:
                expected = None
            calls_by_lane = {}
            for lane, call in (
                ("compact", partial(plan.evaluate, raw, catalog, reuse)),
                ("generated", partial(emitted.evaluate, raw, reuse)),
                ("hydrated", partial(hydrated.evaluate, raw, catalog, reuse)),
                ("hydrated_generated", partial(restored_emitter.evaluate, raw, reuse)),
            ):
                result, calls = observe(call, AliasInputConflict if expected is None else None)
                calls_by_lane[lane] = calls
                if expected is not None:
                    assert projection(result) == projection(expected), (name, lane)
                    assert len(calls) == len(expected_calls), (name, lane, calls, expected_calls)
                    if "left" in raw:
                        assert result.left is raw["left"]
                    if CachedParent in reuse_spec or CachedTokenParent in reuse_spec:
                        assert result.cached in reuse_spec.values()
            assert plan.dump() == payload
            assert marshal.loads(hydrated.dump()) == marshal.loads(payload)
            rows.append({"case": name, "reused": [provider.__name__ for provider in reuse_spec],
                         "outcome": "conflict" if expected is None else projection(expected),
                         "constructors": calls_by_lane, "physical_sites": len(graph.rows),
                         "selector_states": plan.state_count, "payload_bytes": len(payload)})
        assert marshal.dumps(probe.artifact._spell_codegen_creation.metadata["codegen_creation_manifest"]) == probe.manifest_bytes
    return rows


def real_cases() -> list[dict[str, object]]:
    """Exercise static aliases, repeated many, conditional selection and default restoration."""
    rows = []
    shared = ((Token, Existence.many), (Branch, Existence.unique_per_conduit))
    supplied = Branch(Token(77))
    for name, raw in (
        ("ordinary_shared", {}),
        ("secondary_alias", {"right>token>value": 91}),
        ("cut_primary", {"left": supplied, "right>token>value": 91}),
        ("inactive_primary", {"left": supplied, "left>token>value": 21}),
        ("active_conflict", {"left>token>value": 21, "right>token>value": 91}),
        ("ranked_aliases", {"**value": 21, "right>token>value": 91}),
        ("falsey_value", {"right>token>value": False}),
    ):
        rows += run_case(name, PairRoot, shared, raw, ({}, {Branch: supplied}, {}))
    rows += run_case("distinct_many", PairRoot, ((Token, Existence.many), (Branch, Existence.many)),
                     {"left>token>value": 21, "right>token>value": 91}, ({},))
    rows += run_case("ordinary_many", PairRoot, ((Token, Existence.many), (Branch, Existence.many)), {}, ({},))
    rows += run_case("unequal_depth", UnequalDepthRoot, shared + ((Wrapper, Existence.many),),
                     {"wrapped>branch>token>value": 91}, ({},))
    rows += run_case("collection_empty", CollectionRoot, ((Leaf, Existence.many),), {"items": []}, ({},))
    reuse_bindings = ((SharedService, Existence.unique_per_conduit),
                      (CachedParent, Existence.unique_per_conduit), (FreshParent, Existence.many))
    cached = CachedParent(SharedService(77))
    for name, raw in (
        ("reuse_equal_rank", {"cached>service>value": 21, "fresh>service>value": 91}),
        ("reuse_priority", {"**value": 91, "cached>service>value": 21}),
    ):
        rows += run_case(name, ReuseAliasRoot, reuse_bindings, raw,
                         ({CachedParent: cached}, {}, {CachedParent: cached},
                          {CachedParent: cached, SharedService: SharedService(52)}))
    fallback_bindings = ((Token, Existence.many), (ServiceWithToken, Existence.unique_per_conduit),
                         (CachedTokenParent, Existence.unique_per_conduit), (FreshTokenParent, Existence.many))
    cached_token = CachedTokenParent(ServiceWithToken(Token(77)))
    for value in (Token(99), None, False):
        rows += run_case("fallback_" + type(value).__name__, FallbackRoot, fallback_bindings,
                         {"cached>service>token": value}, ({CachedTokenParent: cached_token}, {}, {CachedTokenParent: cached_token}))
    return rows


def selector_controls() -> dict[str, object]:
    """Preserve declared-path uniqueness and invalid-target rejection despite cuts."""
    with ExitStack() as cleanup:
        world = World()
        cleanup.callback(world.cleanup)
        world.setup_model("compact-selector-errors", PairRoot,
                          ((Token, Existence.many), (Branch, Existence.unique_per_conduit)))
        graph = CompactGraph.from_world(world)
        cleanup.callback(graph.cleanup)
        assert graph.declared_matches(CompactPlan._rule("*value")) == 2
        for keys in (("*value",), ("left", "left>missing"), ("**missing",)):
            with pytest.raises(ValueError):
                CompactPlan(graph, keys)
        unique = CompactPlan(graph, ("*right",))
        cleanup.callback(unique.cleanup)
        wrong_version = list(marshal.loads(unique.dump()))
        wrong_version[0] = -1
        with pytest.raises(ValueError):
            CompactPlan.load(marshal.dumps(tuple(wrong_version)))
    return {"physical_token_sites": 1, "declared_value_paths": 2, "invalid_shapes_rejected": 3,
            "unique_root_parameter_accepted": True, "incompatible_schema_rejected": True}


def scaling_cases() -> list[dict[str, object]]:
    """Measure compact metadata for a chain with two aliases per shared level.

    These synthetic graphs have 2**depth logical leaf paths but depth+1 actual
    constructors. Native graph-building performance is not measured. Report
    one diagnostic preparation/emission duration without speedup inference.
    """
    rows = []
    for depth in (4, 8, 12, 20, 32, 64):
        sites = tuple((f"chain_{index}", index != 0,
                       (("left", False, (index + 1,)), ("right", False, (index + 1,)))
                       if index < depth else (("value", False, ()),)) for index in range(depth + 1))
        with ExitStack() as cleanup:
            start = perf_counter_ns()
            graph = CompactGraph(0, sites)
            cleanup.callback(graph.cleanup)
            path = ">".join(("right",) * depth + ("value",))
            raw = {"**value": 21, path: 91}
            plan = CompactPlan(graph, tuple(raw))
            cleanup.callback(plan.cleanup)
            prepared_ns = perf_counter_ns() - start
            assert graph.path_counts[-1] == 2 ** depth
            assert graph.declared_matches(CompactPlan._rule("*value")) == 2 ** depth
            factory = CountedFactory()
            constructors = {row[0]: factory for row in sites}
            emitter = CompactEmitter(plan, constructors)
            cleanup.callback(emitter.cleanup)
            result = emitter.evaluate(raw)
            assert factory.calls == depth + 1
            for _level in range(depth):
                assert result["left"] is result["right"]
                result = result["right"]
            assert result["value"] == 91
            assert plan.state_count == depth + 1
            rows.append({"depth": depth, "physical_sites": len(sites), "logical_leaf_paths": 2 ** depth,
                         "selector_states": plan.state_count, "guard_instructions": len(plan.guards.rows),
                         "payload_bytes": len(plan.dump()), "generated_source_bytes": len(emitter.source.encode()),
                         "constructors": factory.calls, "diagnostic_preparation_ns": prepared_ns})
    return rows


def static_pruning_controls(directory: Path) -> list[dict[str, object]]:
    """Prove supplied branches disappear from emitted source as well as execution.

    The five-dependency and deep workloads are the original requested structural
    examples. Constructor profiling is independent of plan metadata. Counting
    emitted constructor sites checks that a pruned graph is not merely scanned
    through hundreds of constant-false branches on every call.
    """
    rows = []
    for scene in ("five", "deep_none", "deep_left", "deep_all"):
        with ExitStack() as cleanup:
            world = World()
            cleanup.callback(world.cleanup)
            if scene == "five":
                world.setup_model("compact-five", FiveRoot, ((Leaf, Existence.many),))
                raw = {"a": None, "b": False, "c": 21}
                expected = 3
            else:
                world.setup("deep", "automatic")
                ordinary = world.conduit.meld(spell_id=world.root_id)
                raw = {"left": ordinary.left}
                expected = 256
                if scene == "deep_none":
                    raw = {}
                    expected = 511
                if scene == "deep_all":
                    raw["right"] = ordinary.right
                    expected = 1
            graph = CompactGraph.from_world(world)
            cleanup.callback(graph.cleanup)
            catalog = {spell_id: world.book._spell_id_pool[spell_id].spell for spell_id, _shared, _sockets in graph.rows}
            plan = CompactPlan(graph, tuple(raw))
            cleanup.callback(plan.cleanup)
            emitter = CompactEmitter(plan, catalog)
            cleanup.callback(emitter.cleanup)
            result, calls = SliceProbe.observe(partial(emitter.evaluate, raw))
            assert len(calls) == expected
            if scene == "five":
                assert result.a is None and result.b is False and result.c == 21
                assert result.d is not result.e
            else:
                if "left" in raw:
                    assert result.left is raw["left"]
                if scene == "deep_all":
                    assert result.right is raw["right"]
            constructor_sites = sum(
                isinstance(node, ast.Call) and isinstance(node.func, ast.Subscript)
                and isinstance(node.func.value, ast.Name) and node.func.value.id == "_constructors"
                for node in ast.walk(ast.parse(emitter.source))
            )
            assert constructor_sites == expected
            (directory / f"compact_{scene}_generated.py").write_text(emitter.source, encoding="utf-8")
            rows.append({"case": scene, "base_sites": len(graph.rows), "emitted_sites": constructor_sites,
                         "executed_constructors": len(calls), "generated_source_bytes": len(emitter.source.encode()),
                         "guard_instructions_emitted": len(emitter._live_guards(plan))})
    return rows


def main() -> None:
    """Write source-hashed real-graph equivalence and synthetic scaling evidence."""
    directory = Path(__file__).resolve().parent
    source_before = _source_fingerprints(directory.parents[2])
    files = ("compact_alias_plan.py", "compact_alias_emitter.py", "compact_alias_probe.py",
             "conditional_alias_plan.py", "conditional_alias_probe.py", "conditional_alias_results.json",
             "alias_demand_probe.py", "alias_results.json", "graph_slice_probe.py", "results.json")
    hashes = {name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in files}
    cases = real_cases()
    controls = selector_controls()
    scaling = scaling_cases()
    pruning = static_pruning_controls(directory)
    source_after = _source_fingerprints(directory.parents[2])
    changed = sorted(path for path in source_before.keys() | source_after.keys()
                     if source_before.get(path) != source_after.get(path))
    assert not changed
    assert all(hashlib.sha256((directory / name).read_bytes()).hexdigest() == digest for name, digest in hashes.items())
    report = {"timestamp": datetime.now(UTC).isoformat(), "python": sys.version,
              "source_sha256": source_before, "source_changed": changed, "artifacts_sha256": hashes,
              "cases": cases, "selector_controls": controls, "scaling": scaling, "static_pruning": pruning,
              "limits": "Bounded adapter; fixed reuse; no native admission/locks/disposal, no production throughput claim."}
    (directory / "compact_alias_results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
