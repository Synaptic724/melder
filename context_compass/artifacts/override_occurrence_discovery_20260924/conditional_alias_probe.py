"""Qualify conditional alias activation on bounded real compiler declarations.

This uses externally injected reuse results, not native Melder store operations.
It checks values, identities, constructor counts and unchanged prepared metadata.
Earlier diagnostic files and their receipts are preserved as independent evidence.
"""

import hashlib
import json
import marshal
import sys
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from functools import partial
from pathlib import Path
from types import FrameType
from typing import Optional

import pytest

from context_compass.artifacts.override_occurrence_discovery_20260924.alias_demand_probe import (
    AliasInputConflict,
    PreparedShapeMismatch,
    ReuseSiblingRoot,
    UnequalDepthRoot,
    Wrapper,
)
from context_compass.artifacts.override_occurrence_discovery_20260924.conditional_alias_plan import (
    ConditionalAliasPlan,
)
from context_compass.artifacts.override_occurrence_discovery_20260924.graph_slice_probe import (
    Branch,
    CollectionRoot,
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


class ServiceWithToken:
    """Shared descendant with a dependency edge that may need to become live again."""

    def __init__(self, token: Token) -> None:
        """Borrow one Token to expose whether conditional replacement cuts its edge."""
        self.token = token


class CachedTokenParent:
    """Reusable parent that can carry an externally supplied service."""

    def __init__(self, service: ServiceWithToken) -> None:
        """Borrow the external or newly constructed service."""
        self.service = service


class FreshTokenParent:
    """Independently demanded parent with the same shared service dependency."""

    def __init__(self, service: ServiceWithToken) -> None:
        """Borrow the service reached through the active path."""
        self.service = service


class FallbackRoot:
    """Join paths whose runtime liveness changes the shared service's input source."""

    def __init__(self, cached: CachedTokenParent, fresh: FreshTokenParent) -> None:
        """Expose both paths for constructor, value and identity assertions."""
        self.cached, self.fresh = cached, fresh


@contextmanager
def prepared(
    name: str, root: type, bindings: tuple[tuple[type, Existence], ...], raw: dict[str, object],
) -> Iterator[ConditionalAliasPlan]:
    """Own an isolated World and detached plan; assert native manifest preservation.

    Cleanup always follows plan -> probe -> world. The manifest check covers
    preparation and evaluation, including expected-error cases inside the yield.
    """
    world = World()
    try:
        world.setup_model(name, root, bindings)
        probe = SliceProbe(world)
        plan = ConditionalAliasPlan(probe)
        try:
            plan.build(raw)
            yield plan
            assert marshal.dumps(probe.artifact._spell_codegen_creation.metadata["codegen_creation_manifest"]) == probe.manifest_bytes
        finally:
            plan.cleanup()
            probe.cleanup()
    finally:
        world.cleanup()


def observe(
    call: Callable[[], object], error: Optional[type[Exception]] = None,
) -> tuple[object, list[str]]:
    """Count only fixture constructors and prove expected refusals precede construction."""
    calls: list[str] = []

    def trace(frame: FrameType, event: str, arg: object) -> None:
        """Keep compiler/helper allocations outside the application-constructor count."""
        if (event == "call" and frame.f_code.co_name == "__init__"
                and frame.f_code.co_filename.endswith((
                    "graph_slice_probe.py", "alias_demand_probe.py", "review_alias_demand.py",
                    "conditional_alias_probe.py",
                ))):
            calls.append(type(frame.f_locals["self"]).__qualname__)

    previous = sys.getprofile()
    sys.setprofile(trace)
    try:
        if error is None:
            result = call()
        else:
            with pytest.raises(error):
                call()
            assert not calls
            result = None
    finally:
        sys.setprofile(previous)
    return result, calls


def shared_id(plan: ConditionalAliasPlan, provider: type) -> str:
    """Locate the real selected Spell ID for an explicitly named fixture provider."""
    return next(site.spell_id for site in plan.sites if plan.probe.lookup[site.spell_id].spell is provider)


def signature(plan: ConditionalAliasPlan) -> bytes:
    """Snapshot value-only plan metadata to detect changes across calls and reuse states."""
    sites = tuple((site.spell_id, tuple(sorted(site.aliases.items())), site.demand, site.construct,
                   tuple((name, tuple(children)) for name, children in site.children.items()),
                   tuple((name, tuple((ref.node_id, ref.param_path_id, ref.param_name, rank, guard)
                                      for ref, rank, guard in candidates))
                         for name, candidates in site.inputs.items())) for site in plan.sites)
    return marshal.dumps((plan.guards.rows, sites, plan.socket_shape, plan.rank_shape))


def static_controls() -> list[dict[str, object]]:
    """Retain the earlier static alias, specificity and distinct-many guarantees."""
    rows = []
    supplied = Branch(Token(77))
    cases = (
        ("secondary_alias", {"right>token>value": 91}, 91, False),
        ("cut_primary", {"left": supplied, "right>token>value": 91}, 91, False),
        ("inactive_primary", {"left": supplied, "left>token>value": 21}, 13, False),
        ("matching_aliases", {"left>token>value": 91, "right>token>value": 91}, 91, False),
        ("conflicting_aliases", {"left>token>value": 21, "right>token>value": 91}, 0, True),
        ("inactive_conflict", {"left": supplied, "left>token>value": 21, "right>token>value": 91}, 91, False),
        ("specificity", {"**value": 21, "right>token>value": 91}, 91, False),
    )
    bindings = ((Token, Existence.many), (Branch, Existence.unique_per_conduit))
    for name, raw, expected, conflict in cases:
        with prepared(name, PairRoot, bindings, raw) as plan:
            before = signature(plan)
            result, calls = observe(partial(plan.evaluate, raw), AliasInputConflict if conflict else None)
            if not conflict:
                assert isinstance(result, PairRoot) and result.right.token.value == expected
                assert len(calls) == 3
                if "left" in raw:
                    assert result.left is supplied
                else:
                    assert result.left is result.right
            if name == "secondary_alias":
                for value in (None, False, 0, object()):
                    assert plan.evaluate({"right>token>value": value}).right.token.value is value
            if name == "specificity":
                changed = {"left>token>value": 21, "right>token>value": 91}
                observe(partial(plan.evaluate, changed), PreparedShapeMismatch)
            assert signature(plan) == before
            rows.append({"case": name, "constructors": calls, "expected_conflict": conflict})
    many_cases = (
        ("distinct_many", {}, 5),
        ("distinct_many_values", {"left>token>value": 21, "right>token>value": 91}, 5),
        ("distinct_many_cut", {"left": supplied, "right>token>value": 91}, 3),
    )
    for name, raw, count in many_cases:
        with prepared(name, PairRoot, ((Token, Existence.many), (Branch, Existence.many)), raw) as plan:
            result, calls = observe(partial(plan.evaluate, raw))
            assert len(calls) == count and result.left is not result.right
            assert result.left.token is not result.right.token
            if name == "distinct_many_values":
                assert (result.left.token.value, result.right.token.value) == (21, 91)
            if name == "distinct_many_cut":
                assert result.left is supplied and result.right.token.value == 91
            rows.append({"case": name, "constructors": calls})
    return rows


def reuse_controls() -> list[dict[str, object]]:
    """Resolve both lead counterexamples and retain fresh-state conflict detection."""
    rows = []
    parent = CachedParent(SharedService(77))
    cases = (
        ("reuse_equal_rank", {"cached>service>value": 21, "fresh>service>value": 91}, True),
        ("reuse_priority", {"**value": 91, "cached>service>value": 21}, False),
    )
    bindings = ((SharedService, Existence.unique_per_conduit),
                (CachedParent, Existence.unique_per_conduit), (FreshParent, Existence.many))
    for name, raw, fresh_conflict in cases:
        with prepared(name, ReuseAliasRoot, bindings, raw) as plan:
            before = signature(plan)
            reused = {shared_id(plan, CachedParent): parent}
            result, calls = observe(partial(plan.evaluate, raw, reused))
            assert result.cached is parent and result.cached.service.value == 77
            assert result.fresh.service.value == 91 and result.fresh.service is not parent.service
            assert calls == ["SharedService", "FreshParent", "ReuseAliasRoot"]
            fresh, fresh_calls = observe(partial(plan.evaluate, raw), AliasInputConflict if fresh_conflict else None)
            if not fresh_conflict:
                assert fresh.cached.service is fresh.fresh.service and fresh.fresh.service.value == 21
                assert len(fresh_calls) == 4
            existing_service = SharedService(52)
            reused[shared_id(plan, SharedService)] = existing_service
            reused_result, both_calls = observe(partial(plan.evaluate, raw, reused))
            assert reused_result.fresh.service is existing_service
            assert both_calls == ["FreshParent", "ReuseAliasRoot"]
            assert signature(plan) == before
            rows.append({"case": name, "reuse_constructors": calls, "active_value": 91,
                         "fresh_constructors": fresh_calls, "fresh_conflict": fresh_conflict,
                         "both_reused_constructors": both_calls, "same_plan_unchanged": True})
    return rows


def fallback_controls() -> list[dict[str, object]]:
    """Restore a dependency cut by the only alias that becomes inactive at runtime."""
    rows = []
    old_parent = CachedTokenParent(ServiceWithToken(Token(77)))
    supplied_token = Token(99)
    bindings = ((Token, Existence.many), (ServiceWithToken, Existence.unique_per_conduit),
                (CachedTokenParent, Existence.unique_per_conduit), (FreshTokenParent, Existence.many))
    for value in (supplied_token, None, False):
        raw = {"cached>service>token": value}
        with prepared("conditional-default-edge", FallbackRoot, bindings, raw) as plan:
            before = signature(plan)
            reuse = {shared_id(plan, CachedTokenParent): old_parent}
            result, calls = observe(partial(plan.evaluate, raw, reuse))
            assert result.cached is old_parent and result.fresh.service.token.value == 13
            assert result.fresh.service.token is not supplied_token
            assert calls == ["Token", "ServiceWithToken", "FreshTokenParent", "FallbackRoot"]
            fresh, fresh_calls = observe(partial(plan.evaluate, raw))
            assert fresh.cached.service is fresh.fresh.service and fresh.fresh.service.token is value
            assert "Token" not in fresh_calls and len(fresh_calls) == 4
            assert signature(plan) == before
            rows.append({"case": "fallback_after_reuse", "supplied_kind": type(value).__name__,
                         "reuse_constructors": calls, "fresh_constructors": fresh_calls,
                         "fallback_value": 13, "same_plan_unchanged": True})
    return rows


def remaining_controls() -> list[dict[str, object]]:
    """Retain unequal-depth fan-in, independent demand and falsey collection cuts."""
    rows = []
    bindings = ((Token, Existence.many), (Branch, Existence.unique_per_conduit), (Wrapper, Existence.many))
    raw = {"wrapped>branch>token>value": 91}
    with prepared("unequal-depth", UnequalDepthRoot, bindings, raw) as plan:
        result, calls = observe(partial(plan.evaluate, raw))
        assert result.direct is result.wrapped.branch and result.direct.token.value == 91
        assert len(calls) == 4
        rows.append({"case": "unequal_depth", "constructors": calls})
    with prepared("reuse-sibling", ReuseSiblingRoot, bindings, {}) as plan:
        shared = Branch(Token(77))
        reused, calls = observe(partial(plan.evaluate, {}, {shared_id(plan, Branch): shared}))
        fresh, fresh_calls = observe(partial(plan.evaluate, {}))
        assert reused.branch is shared and reused.token is not shared.token
        assert len(calls) == 2 and len(fresh_calls) == 4 and fresh.branch is not shared
        rows.append({"case": "reuse_sibling", "constructors": calls, "fresh_constructors": fresh_calls})
    for value in ([], None, False):
        raw = {"items": value}
        with prepared("collection-cut", CollectionRoot, ((Leaf, Existence.many),), raw) as plan:
            result, calls = observe(partial(plan.evaluate, raw))
            assert result.items is value and calls == ["CollectionRoot"]
            rows.append({"case": "collection_cut", "supplied_kind": type(value).__name__, "constructors": calls})
    return rows


def main() -> None:
    """Write one receipt after checking constructor semantics and source preservation."""
    directory = Path(__file__).resolve().parent
    preserved = (directory / "alias_demand_probe.py", directory / "alias_results.json",
                 directory / "graph_slice_probe.py", directory / "results.json",
                 directory.parent / "override_structural_discovery_20260924" / "review_alias_demand.py",
                 directory.parent / "override_emission_prototype_20260924" / "prototype.py")
    # The exact emitter artifact path is asserted rather than silently skipped.
    hashes = {str(path.relative_to(directory.parents[2])): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in preserved}
    scripts = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
               for path in (Path(__file__), directory / "conditional_alias_plan.py")}
    before = _source_fingerprints(directory.parents[2])
    rows = static_controls() + reuse_controls() + fallback_controls() + remaining_controls()
    after = _source_fingerprints(directory.parents[2])
    changed = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
    assert not changed
    assert all(hashlib.sha256(path.read_bytes()).hexdigest() == hashes[str(path.relative_to(directory.parents[2]))]
               for path in preserved)
    report = {"timestamp": datetime.now(UTC).isoformat(), "python": sys.version,
              "source_sha256": before, "source_changed": changed, "preserved_sha256": hashes,
              "scripts_sha256": scripts, "cases": rows,
              "limits": "Untimed interpreter; fixed reuse outcomes injected; no native admission, locks, hooks or disposal."}
    (directory / "conditional_alias_results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
