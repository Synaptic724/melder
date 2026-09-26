"""Review conditional alias selection using a natively reachable reused parent.

Native Meld/purge establishes the store state. The conditional planner still
receives fixed reuse outcomes and invokes constructors in its own interpreter;
this is not production execution or native concurrency qualification.
"""

import hashlib
import json
import marshal
import sys
from datetime import UTC, datetime
from functools import partial
from pathlib import Path

from context_compass.artifacts.override_occurrence_discovery_20260924.alias_demand_probe import (
    AliasInputConflict,
)
from context_compass.artifacts.override_occurrence_discovery_20260924.conditional_alias_plan import (
    ConditionalAliasPlan,
)
from context_compass.artifacts.override_occurrence_discovery_20260924.graph_slice_probe import (
    SliceProbe,
    World,
)
from context_compass.artifacts.override_structural_discovery_20260924.review_alias_demand import (
    CachedParent,
    FreshParent,
    ReuseAliasRoot,
    SharedService,
    observe,
)
from melder.aether.spellbook.existence.existence import Existence
from tests.experimentation.test_melder_creation_overrides_performance import (
    _source_fingerprints,
)


def review() -> list[dict[str, object]]:
    """Verify active input selection across simulated reuse changes in one plan.

    Contract:
        A native live parent holds an external child while the registered child
        store is empty. Equal-rank inputs conflict only when both constructor
        paths are active. Higher-rank inactive input loses to the active rule.
        Guard instructions and the canonical native manifest remain unchanged.

    Returns:
        Rows describing the two input layouts and their alternating results.
    """
    world = World()
    rows: list[dict[str, object]] = []
    try:
        world.setup_model("lead-conditional-review", ReuseAliasRoot, (
            (SharedService, Existence.unique_per_conduit),
            (CachedParent, Existence.unique_per_conduit),
            (FreshParent, Existence.many),
        ))
        external = SharedService(77)
        cached = world.conduit.meld(spell=CachedParent, override={"service": external})
        assert isinstance(cached, CachedParent) and cached.service is external
        assert world.conduit.purge(SharedService) == 1
        assert world.conduit.has_live_creation(spell=CachedParent)
        assert not world.conduit.has_live_creation(spell=SharedService)
        probe = SliceProbe(world)
        try:
            layouts = (
                ("equal_rank", {"cached>service>value": 21, "fresh>service>value": 91}),
                ("different_rank", {"**value": 91, "cached>service>value": 21}),
            )
            for name, raw in layouts:
                plan = ConditionalAliasPlan(probe)
                try:
                    plan.build(raw)
                    guards_before = tuple(plan.guards.rows)
                    cached_id = next(site.spell_id for site in plan.sites
                                     if probe.lookup[site.spell_id].spell is CachedParent)
                    result, calls = observe(partial(plan.evaluate, raw, {cached_id: cached}))
                    assert isinstance(result, ReuseAliasRoot)
                    assert result.cached is cached and cached.service is external
                    assert result.fresh.service.value == 91
                    assert calls == ["SharedService", "FreshParent", "ReuseAliasRoot"]
                    if name == "equal_rank":
                        try:
                            plan.evaluate(raw)
                        except AliasInputConflict:
                            fresh_outcome: object = "conflict"
                        else:
                            raise AssertionError("Two active equal-rank inputs must conflict in this model.")
                    else:
                        fresh, fresh_calls = observe(partial(plan.evaluate, raw))
                        assert isinstance(fresh, ReuseAliasRoot)
                        assert fresh.cached is not cached
                        assert fresh.cached.service is fresh.fresh.service
                        assert fresh.fresh.service.value == 21 and len(fresh_calls) == 4
                        fresh_outcome = 21
                    again = plan.evaluate(raw, {cached_id: cached})
                    assert isinstance(again, ReuseAliasRoot) and again.fresh.service.value == 91
                    assert tuple(plan.guards.rows) == guards_before
                    assert marshal.dumps(probe.artifact._spell_codegen_creation.metadata[
                        "codegen_creation_manifest"
                    ]) == probe.manifest_bytes
                    rows.append({"case": name, "fresh_service_with_parent_reused": 91,
                                 "fresh_outcome": fresh_outcome, "reused_again_fresh_service": 91,
                                 "constructors": calls,
                                 "guards_unchanged": True, "canonical_manifest_unchanged": True})
                finally:
                    plan.cleanup()
        finally:
            probe.cleanup()
    finally:
        world.cleanup()
    return rows


def main() -> None:
    """Write a source-stable independent receipt without overwriting earlier evidence."""
    directory = Path(__file__).resolve().parent
    peer = directory.parent / "override_occurrence_discovery_20260924"
    paths = (Path(__file__), directory / "review_alias_demand.py", peer / "conditional_alias_plan.py",
             peer / "alias_demand_probe.py", peer / "graph_slice_probe.py")
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    before = _source_fingerprints(directory.parents[2])
    rows = review()
    after = _source_fingerprints(directory.parents[2])
    changed = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
    assert not changed
    assert all(hashlib.sha256(path.read_bytes()).hexdigest() == hashes[path.name] for path in paths)
    report = {"timestamp": datetime.now(UTC).isoformat(), "python": sys.version,
              "scripts_sha256": hashes, "source_sha256": before, "source_changed": changed,
              "cases": rows, "limits": "Untimed; fixed reuse outcomes; no native store-lock integration."}
    (directory / "conditional_alias_review_results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
