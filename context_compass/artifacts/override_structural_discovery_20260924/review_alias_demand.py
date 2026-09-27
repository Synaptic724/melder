"""Independently challenge the alias-demand design without changing Melder.

The imported planner is an untimed interpreter, not the production runtime.
Repeated-many cases assert the desired construction identity. Reuse cases
characterize a remaining design boundary: static alias selection can still
include inputs below a constructor that is skipped after a live reuse hit.
"""

import hashlib
import json
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from functools import partial
from pathlib import Path
from types import FrameType

from context_compass.artifacts.override_occurrence_discovery_20260924.alias_demand_probe import (
    AliasInputConflict,
    AliasPlan,
)
from context_compass.artifacts.override_occurrence_discovery_20260924.graph_slice_probe import (
    Branch,
    PairRoot,
    SliceProbe,
    Token,
    World,
)
from melder.aether.spellbook.existence.existence import Existence
from tests.experimentation.test_melder_creation_overrides_performance import (
    _source_fingerprints,
)


class SharedService:
    """Expose the input chosen for a shared descendant constructor.

    Contract:
        Holds a diagnostic scalar with no external resources or disposal.
    """

    def __init__(self, value: int = 13) -> None:
        """Retain the selected scalar so cross-alias input leakage is observable."""
        self.value = value


class CachedParent:
    """Represent a reusable parent previously given an external service.

    Contract:
        Borrows the supplied service. Its reuse does not prove that a service
        was ever registered in the current runtime's shared creation store.
    """

    def __init__(self, service: SharedService) -> None:
        """Borrow one service; no resource ownership is modeled in this probe."""
        self.service = service


class FreshParent:
    """Request the same service type through an independently live constructor."""

    def __init__(self, service: SharedService) -> None:
        """Expose the service chosen for this independently demanded parent."""
        self.service = service


class ReuseAliasRoot:
    """Join a reusable parent with a separate parent that still needs construction."""

    def __init__(self, cached: CachedParent, fresh: FreshParent) -> None:
        """Borrow both parents and preserve their references for identity checks."""
        self.cached = cached
        self.fresh = fresh


def observe(call: Callable[[], object]) -> tuple[object, list[str]]:
    """Record fixture constructors and restore the caller's profiler.

    Contract:
        Profiling is used only outside timing. It counts this review's fixture
        constructors and the imported Token/Branch/PairRoot fixture constructors.
        Exceptions propagate after the prior profiler has been restored.
    """
    calls: list[str] = []

    def trace(frame: FrameType, event: str, arg: object) -> None:
        """Record only the fixture call sites relevant to this design review."""
        if (event == "call" and frame.f_code.co_name == "__init__"
                and frame.f_code.co_filename.endswith(("review_alias_demand.py", "graph_slice_probe.py"))):
            calls.append(type(frame.f_locals["self"]).__qualname__)

    previous = sys.getprofile()
    sys.setprofile(trace)
    try:
        result = call()
    finally:
        sys.setprofile(previous)
    return result, calls


def review_many_sites() -> list[dict[str, object]]:
    """Prove that physical construction grouping preserves distinct many parents.

    Returns:
        Diagnostic rows for full construction, separate nested inputs and a
        whole-parent substitution. Every row checks instance identity and count.

    Lifecycle:
        Each scenario owns and tears down its isolated World and detached plan.
    """
    rows: list[dict[str, object]] = []
    supplied = Branch(Token(77))
    cases = (
        ("distinct_many_parents", {}, 5),
        ("distinct_many_inputs", {"left>token>value": 21, "right>token>value": 91}, 5),
        ("cut_one_many_parent", {"left": supplied, "right>token>value": 91}, 3),
    )
    for name, raw, expected in cases:
        world = World()
        try:
            world.setup_model(name, PairRoot, ((Token, Existence.many), (Branch, Existence.many)))
            probe = SliceProbe(world)
            plan = AliasPlan(probe)
            try:
                plan.build(raw)
                result, calls = observe(partial(plan.evaluate, raw))
                assert isinstance(result, PairRoot)
                assert len(plan.sites) == expected and len(calls) == expected
                assert result.left is not result.right
                assert result.left.token is not result.right.token
                if name == "distinct_many_inputs":
                    assert (result.left.token.value, result.right.token.value) == (21, 91)
                if name == "cut_one_many_parent":
                    assert result.left is supplied and result.right.token.value == 91
                rows.append({"case": name, "constructors": calls, "sites": len(plan.sites)})
            finally:
                plan.cleanup()
                probe.cleanup()
        finally:
            world.cleanup()
    return rows


def review_reused_aliases() -> list[dict[str, object]]:
    """Characterize alias inputs below a parent skipped by a simulated reuse hit.

    Contract:
        Native Meld plus child purge establishes the reuse state: the parent
        remains live while its declared shared child has no stored creation.
        These assertions capture prototype limitations, not approved production
        semantics. The current native runtime is not patched or simulated here.
    """
    world = World()
    rows: list[dict[str, object]] = []
    try:
        world.setup_model("review-reused-alias", ReuseAliasRoot, (
            (SharedService, Existence.unique_per_conduit),
            (CachedParent, Existence.unique_per_conduit),
            (FreshParent, Existence.many),
        ))
        probe = SliceProbe(world)
        try:
            external_service = SharedService(77)
            reused_parent = world.conduit.meld(spell=CachedParent, override={"service": external_service})
            assert isinstance(reused_parent, CachedParent)
            assert reused_parent.service is external_service
            assert world.conduit.has_live_creation(spell=CachedParent)
            removed = world.conduit.purge(SharedService)
            assert removed == 1
            assert not world.conduit.has_live_creation(spell=SharedService)
            assert world.conduit.has_live_creation(spell=CachedParent)
            assert world.conduit.meld_existing_spell(spell=CachedParent) is reused_parent
            rows.append({"case": "native_parent_live_after_child_purge", "removed_children": removed,
                         "parent_live": True, "child_live": False, "external_child_retained": True})
            cases = (
                ("equal_rank_below_reused_parent", {
                    "cached>service>value": 21, "fresh>service>value": 91,
                }),
                ("higher_rank_below_reused_parent", {
                    "**value": 91, "cached>service>value": 21,
                }),
            )
            for name, raw in cases:
                plan = AliasPlan(probe)
                try:
                    plan.build(raw)
                    cached_id = next(site.spell_id for site in plan.sites
                                     if probe.lookup[site.spell_id].spell is CachedParent)
                    reuse = {cached_id: reused_parent}
                    try:
                        result, calls = observe(partial(plan.evaluate, raw, reuse))
                    except AliasInputConflict as error:
                        assert name == "equal_rank_below_reused_parent"
                        rows.append({"case": name, "outcome": "prototype_conflict", "message": str(error)})
                    else:
                        assert name == "higher_rank_below_reused_parent"
                        assert isinstance(result, ReuseAliasRoot)
                        assert result.cached is reused_parent
                        assert result.cached.service.value == 77
                        assert result.fresh.service.value == 21
                        assert "CachedParent" not in calls
                        rows.append({"case": name, "outcome": "prototype_inactive_alias_wins",
                                     "fresh_value": result.fresh.service.value, "constructors": calls})
                finally:
                    plan.cleanup()
        finally:
            probe.cleanup()
    finally:
        world.cleanup()
    return rows


def main() -> None:
    """Persist independent review evidence with exact source and prototype provenance.

    Contract:
        Writes only this review's JSON receipt. Asserts runtime source and both
        borrowed prototype files stayed unchanged during the review. No timings,
        live-store locks, admission behavior, hooks or disposal are qualified.
    """
    directory = Path(__file__).resolve().parent
    repo = directory.parents[2]
    prototype_directory = directory.parent / "override_occurrence_discovery_20260924"
    review_paths = (Path(__file__), prototype_directory / "alias_demand_probe.py",
                    prototype_directory / "graph_slice_probe.py")
    scripts = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in review_paths}
    before = _source_fingerprints(repo)
    rows = review_many_sites() + review_reused_aliases()
    after = _source_fingerprints(repo)
    changed = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
    assert not changed
    assert all(hashlib.sha256(path.read_bytes()).hexdigest() == scripts[path.name] for path in review_paths)
    report = {"timestamp": datetime.now(UTC).isoformat(), "python": sys.version,
              "scripts_sha256": scripts, "source_sha256": before, "source_changed": changed,
              "cases": rows, "limits": "Untimed interpreter review; reuse supplied as a test condition.",
              "open_contract": "Should runtime-reused ancestors deactivate descendant alias inputs?"}
    (directory / "alias_review_results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
