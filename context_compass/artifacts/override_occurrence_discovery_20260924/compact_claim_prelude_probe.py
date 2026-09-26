"""Test demanded-site callback ordering and the constructor-free prelude contract."""

import ast
import hashlib
import json
import sys
from contextlib import ExitStack
from datetime import UTC, datetime
from functools import partial
from pathlib import Path

import pytest

from context_compass.artifacts.override_occurrence_discovery_20260924.alias_demand_probe import (
    UnequalDepthRoot,
    Wrapper,
)
from context_compass.artifacts.override_occurrence_discovery_20260924.compact_alias_plan import (
    CompactGraph,
    CompactPlan,
)
from context_compass.artifacts.override_occurrence_discovery_20260924.compact_claim_prelude import (
    CompactClaimPrelude,
)
from context_compass.artifacts.override_occurrence_discovery_20260924.conditional_alias_probe import (
    observe,
)
from context_compass.artifacts.override_occurrence_discovery_20260924.graph_slice_probe import (
    Branch,
    PairRoot,
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


class Contended(RuntimeError):
    """Test-only callback signal whose identity must survive prelude propagation."""


class UntouchableValue:
    """A found value that refuses implicit truth or equality evaluation."""

    def __bool__(self) -> bool:
        """Refuse any accidental truthiness probe of the selected object."""
        raise AssertionError("The selected object must not be tested for truth.")

    def __eq__(self, other: object) -> bool:
        """Refuse any accidental value comparison while gathering claims."""
        raise AssertionError("The selected object must not be compared.")


def checked_source(source: str) -> None:
    """Allow only selector calls, with no comparisons or graph-walking loops."""
    nodes = tuple(ast.walk(ast.parse(source)))
    assert not any(isinstance(node, (ast.Compare, ast.For, ast.While, ast.ListComp, ast.GeneratorExp)) for node in nodes)
    assert all(isinstance(node.func, ast.Name) and node.func.id == "select"
               for node in nodes if isinstance(node, ast.Call))


def run_case(
    name: str, root: type, bindings: tuple[tuple[type, Existence], ...], keys: tuple[str, ...],
    outcomes: dict[type, tuple[bool, object]], expected_calls: tuple[str, ...],
) -> dict[str, object]:
    """Exercise fresh and hydrated preludes against an independent callback log.

    The callback returns caller-owned outcome objects. Every output reference
    must be preserved by identity. Fixture construction is profiled separately
    from setup and must remain zero during selection.
    """
    with ExitStack() as cleanup:
        world = World()
        cleanup.callback(world.cleanup)
        world.setup_model(name, root, bindings)
        graph = CompactGraph.from_world(world)
        cleanup.callback(graph.cleanup)
        plan = CompactPlan(graph, keys)
        cleanup.callback(plan.cleanup)
        payload = plan.dump()
        hydrated = CompactPlan.load(payload)
        cleanup.callback(hydrated.graph.cleanup)
        cleanup.callback(hydrated.cleanup)
        outputs = []
        calls = []
        expected_hits: dict[str, object] = {}

        def select(index: int) -> tuple[bool, object]:
            """Record each requested constructor site without constructing anything."""
            spell_id = graph.rows[index][0]
            provider = world.book._spell_id_pool[spell_id].spell
            calls.append(provider.__name__)
            found, value = outcomes.get(provider, (False, None))
            if found:
                expected_hits[spell_id] = value
            return found, value

        for active_plan in (plan, hydrated):
            prelude = CompactClaimPrelude(active_plan)
            cleanup.callback(prelude.cleanup)
            checked_source(prelude.source)
            calls.clear()
            expected_hits.clear()
            reused, constructors = observe(partial(prelude.prepare, select))
            assert not constructors and tuple(calls) == expected_calls, (name, calls)
            assert reused.keys() == expected_hits.keys()
            assert all(reused[key] is value for key, value in expected_hits.items())
            calls.clear()
            again = prelude.prepare(select)
            assert again is not reused and tuple(calls) == expected_calls
            assert plan.dump() == payload
            outputs.append({"calls": expected_calls, "found_count": len(reused), "constructors": 0})
        return {"case": name, "fresh_and_hydrated": outputs}


def callback_cases() -> list[dict[str, object]]:
    """Cover cuts, reused ancestors, many-only graphs and shared incoming fan-in."""
    rows = []
    shared = ((Token, Existence.unique), (Branch, Existence.unique_per_conduit))
    rows.append(run_case("cold_shared", PairRoot, shared, (), {}, ("Branch", "Token")))
    rows.append(run_case("reused_parent_skips_child", PairRoot, shared, (),
                         {Branch: (True, Branch(Token(77)))}, ("Branch",)))
    rows.append(run_case("whole_parent_cuts", PairRoot, shared, ("left", "right"), {}, ()))
    rows.append(run_case("whole_child_cut", PairRoot, shared, ("**token",), {}, ("Branch",)))
    rows.append(run_case("many_only", PairRoot, ((Token, Existence.many), (Branch, Existence.many)), (), {}, ()))
    for value in (None, False, 0, UntouchableValue()):
        rows.append(run_case("found_" + type(value).__name__, PairRoot, shared, (),
                             {Branch: (True, value)}, ("Branch",)))
    rows.append(run_case("unequal_depth", UnequalDepthRoot,
                         shared + ((Wrapper, Existence.unique_per_conduit),),
                         ("wrapped>branch>token>value",),
                         {Wrapper: (True, Wrapper(Branch(Token(77))))}, ("Wrapper", "Branch", "Token")))
    bindings = ((SharedService, Existence.unique_per_conduit),
                (CachedParent, Existence.unique_per_conduit), (FreshParent, Existence.unique_per_conduit))
    # The two parent claims must be known before their converging child's decision.
    rows.append(run_case("shared_fan_in", ReuseAliasRoot, bindings,
                         ("cached>service>value", "fresh>service>value"),
                         {CachedParent: (True, CachedParent(SharedService(77)))},
                         ("FreshParent", "CachedParent", "SharedService")))
    return rows


def contention_case() -> dict[str, object]:
    """Propagate the original exception and retain no partially selected result."""
    with ExitStack() as cleanup:
        world = World()
        cleanup.callback(world.cleanup)
        world.setup_model("prelude-contention", PairRoot,
                          ((Token, Existence.unique), (Branch, Existence.unique_per_conduit)))
        graph = CompactGraph.from_world(world)
        cleanup.callback(graph.cleanup)
        plan = CompactPlan(graph, ())
        cleanup.callback(plan.cleanup)
        prelude = CompactClaimPrelude(plan)
        cleanup.callback(prelude.cleanup)
        signal = Contended("the caller owns release and retry")
        calls = []

        def contended(index: int) -> tuple[bool, object]:
            """Miss at the parent, then simulate a contested child claim."""
            calls.append(world.book._spell_id_pool[graph.rows[index][0]].spell.__name__)
            if len(calls) == 2:
                raise signal
            return False, None

        with pytest.raises(Contended) as caught:
            prelude.prepare(contended)
        assert caught.value is signal and calls == ["Branch", "Token"]
        marker = UntouchableValue()
        retry_calls = []

        def retry(index: int) -> tuple[bool, object]:
            """Provide a parent hit on a wholly new attempt, omitting the child."""
            retry_calls.append(index)
            return True, marker

        result = prelude.prepare(retry)
        assert len(retry_calls) == len(result) == 1
        assert next(iter(result.values())) is marker
        return {"case": "contention_propagates", "same_exception": True,
                "initial_calls": calls, "new_attempt_calls": 1, "stale_values_retained": False}


def main() -> None:
    """Write a compact receipt and prove all preceding compiler artifacts stayed fixed."""
    directory = Path(__file__).resolve().parent
    names = ("compact_claim_prelude.py", "compact_claim_prelude_probe.py", "compact_alias_plan.py",
             "compact_alias_emitter.py", "compact_alias_probe.py", "compact_alias_results.json")
    hashes = {name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in names}
    before = _source_fingerprints(directory.parents[2])
    cases = callback_cases() + [contention_case()]
    after = _source_fingerprints(directory.parents[2])
    changed = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
    assert not changed
    assert all(hashlib.sha256((directory / name).read_bytes()).hexdigest() == digest for name, digest in hashes.items())
    report = {"timestamp": datetime.now(UTC).isoformat(), "python": sys.version,
              "source_sha256": before, "source_changed": changed, "artifacts_sha256": hashes,
              "cases": cases, "limits": "Compiler callback contract only; native locks/claims belong to the lead's adapter."}
    (directory / "compact_claim_prelude_results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
