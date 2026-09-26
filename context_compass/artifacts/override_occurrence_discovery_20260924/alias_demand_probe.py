"""Prove construction-site identity with logical aliases on bounded real graphs.

This interpreter is an untimed design experiment. Policy under test: validate
selectors first, ignore valid inactive targets, and reject conflicting active
equal-rank inputs on one physical socket. It simulates reuse but does not model
native admission, store locking, disposal or hook delivery. No production edits.
"""

import hashlib
import json
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from functools import partial
from pathlib import Path
from types import FrameType
from typing import TYPE_CHECKING, Optional

import pytest

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

if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.artifacts.spell_override_targeting_codegen_creation import (
        SpellOverrideTargetSocketRef,
    )


class AliasInputConflict(ValueError):
    """Experimental refusal of different equal-rank values for one physical socket."""


class PreparedShapeMismatch(ValueError):
    """An input needs a different prepared selector/rank binding layout."""


class Wrapper:
    """Provide an alias to Branch at a different graph depth."""

    def __init__(self, branch: Branch) -> None:
        """Borrow the shared Branch under one additional constructor context."""
        self.branch = branch


class UnequalDepthRoot:
    """Demand the same Branch directly and through a Wrapper."""

    def __init__(self, direct: Branch, wrapped: Wrapper) -> None:
        """Retain both constructor paths to observe alias convergence."""
        self.direct, self.wrapped = direct, wrapped


class ReuseSiblingRoot:
    """Keep an independent Token demand beside a reusable shared Branch."""

    def __init__(self, branch: Branch, token: Token) -> None:
        """Borrow the two independently demanded values."""
        self.branch, self.token = branch, token


class Site:
    """Own one physical constructor's metadata and value-free input socket references."""

    def __init__(self, index: int, spell_id: str) -> None:
        """Initialize empty alias, operand and dependency collections."""
        self.index, self.spell_id = index, spell_id
        self.aliases: set[tuple[str, int]] = set()
        self.inputs: dict[str, tuple[SpellOverrideTargetSocketRef, ...]] = {}
        self.children: dict[str, list[int]] = {}

    def cleanup(self) -> None:
        """Drop metadata references without cleaning application objects."""
        self.aliases.clear()
        self.inputs.clear()
        self.children.clear()


class AliasPlan:
    """Own a shape-specific constructor graph while borrowing native declarations."""

    def __init__(self, probe: SliceProbe) -> None:
        """Retain native graph access and initialize detached constructor-site state."""
        self.probe = probe
        self.sites: list[Site] = []
        self.by_identity: dict[tuple, Site] = {}
        self.by_spell: dict[str, list[Site]] = {}
        self.inactive: list[str] = []
        self.socket_shape: tuple[tuple[object, ...], ...] = ()
        self.rank_shape: tuple[tuple[object, ...], ...] = ()

    def cleanup(self) -> None:
        """Release owned site state; the caller owns the borrowed SliceProbe."""
        for site in self.sites:
            site.cleanup()
        self.sites.clear()
        self.by_identity.clear()
        self.by_spell.clear()
        self.inactive.clear()
        del self.probe

    def site(self, spell_id: str, parent: int, param: str, member: int) -> Site:
        """Converge shared providers; many identity follows its physical parent site."""
        identity = (
            ("shared", spell_id)
            if spell_id in self.probe.model.instance_shape.shared_spell_ids
            else ("many", parent, param, member, spell_id)
        )
        found = self.by_identity.get(identity)
        if found is None:
            found = Site(len(self.sites), spell_id)
            self.by_identity[identity] = found
            self.by_spell.setdefault(spell_id, []).append(found)
            self.sites.append(found)
        return found

    def selection(self, raw: dict[str, object]) -> tuple[
        dict[SpellOverrideTargetSocketRef, object], tuple[tuple[object, ...], ...],
        dict[SpellOverrideTargetSocketRef, int], tuple[tuple[object, ...], ...],
    ]:
        """Resolve logical targets and retain the specificity needed for alias merging."""
        probe = self.probe
        selected, shape = probe.targeting._apply_with_socket_shape_prechecked(spell_override=raw)
        levels = {}
        for key in raw:
            targets, level, _ = probe.targeting._resolve_targets_for_raw_key(key)
            for ref in targets:
                levels[ref] = max(levels.get(ref, 0), int(level))
        ranked = tuple(sorted(
            (ref.node_id, ref.param_path_id, ref.param_name, ref.socket_kind_value, levels[ref])
            for ref in selected
        ))
        return selected, shape, levels, ranked

    def build(self, raw: dict[str, object]) -> None:
        """Propagate active aliases consumer-first, then cut supplied physical sockets."""
        probe = self.probe
        selected, self.socket_shape, levels, self.rank_shape = self.selection(raw)
        by_owner = {}
        for ref in selected:
            owner = (ref.node_id, probe.registry.parent_id(ref.param_path_id))
            by_owner.setdefault(owner, []).append((ref, levels[ref]))
        root = self.site(probe.world.root_id, -1, "<root>", 0)
        root.aliases.add((probe.world.root_id, probe.registry.root_path_id))
        active_refs = set()
        processed = set()
        for spell_id in reversed(probe.model.order_shape.execution_order):
            for site in self.by_spell.get(spell_id, ()):
                winners = {}
                for alias in sorted(site.aliases):
                    for ref, level in by_owner.get(alias, ()):
                        active_refs.add(ref)
                        previous = winners.get(ref.param_name)
                        if previous is None or level > previous[0]:
                            winners[ref.param_name] = (level, [ref])
                        elif level == previous[0]:
                            previous[1].append(ref)
                site.inputs.update((name, tuple(refs)) for name, (_level, refs) in winners.items())
                template = probe.logical_graph[min(site.aliases)]
                for param, providers in template.items():
                    if param in site.inputs:
                        continue
                    children = []
                    for member, provider in enumerate(providers):
                        assert provider[0] not in processed, "Provider processed before all consumer aliases"
                        child = self.site(provider[0], site.index, param, member)
                        for alias in site.aliases:
                            alias_providers = probe.logical_graph[alias][param]
                            assert len(alias_providers) == len(providers)
                            assert alias_providers[member][0] == provider[0]
                            child.aliases.add(alias_providers[member])
                        children.append(child.index)
                    site.children[param] = children
            processed.add(spell_id)
        assert all(site.spell_id in processed for site in self.sites)
        self.inactive = sorted(probe.registry.format_path(ref.param_path_id) for ref in selected if ref not in active_refs)

    def bind_values(self, raw: dict[str, object]) -> dict[int, dict[str, object]]:
        """Bind fresh values and check active physical-slot conflicts before construction."""
        selected, shape, _levels, ranked = self.selection(raw)
        if shape != self.socket_shape or ranked != self.rank_shape:
            raise PreparedShapeMismatch("Rebuild for the changed selector/socket specificity layout.")
        values = {}
        for site in self.sites:
            bound = {}
            for name, refs in site.inputs.items():
                first = selected[refs[0]]
                if any(selected[ref] != first for ref in refs[1:]):
                    raise AliasInputConflict(f"Active aliases supply conflicting values for parameter {name!r}.")
                bound[name] = first
            values[site.index] = bound
        return values

    def evaluate(self, raw: dict[str, object], reused: Optional[dict[str, object]] = None) -> object:
        """Interpret constructor demand; an injected shared reuse value terminates descent."""
        reused_values = {} if reused is None else reused
        bound_values = self.bind_values(raw)
        results: dict[int, object] = {}

        def resolve(index: int) -> object:
            """Resolve one physical site once and construct children only after reuse misses."""
            if index in results:
                return results[index]
            site = self.sites[index]
            if site.spell_id in self.probe.model.instance_shape.shared_spell_ids and site.spell_id in reused_values:
                results[index] = reused_values[site.spell_id]
                return results[index]
            spell = self.probe.lookup[site.spell_id]
            assert spell.is_class_spell and not spell.has_disposal_methods
            topology = self.probe.root._spell_system_states.get_local_topology_by_id(site.spell_id)
            collections = {socket.param_name for socket in topology.sockets if socket.is_collection}
            kwargs = {}
            for name, children in site.children.items():
                values = [resolve(child) for child in children]
                if name in collections:
                    kwargs[name] = values
                elif values:
                    assert len(values) == 1
                    kwargs[name] = values[0]
            kwargs.update(bound_values[index])
            results[index] = spell.spell(**kwargs)
            return results[index]

        return resolve(0)


def observe(call: Callable[[], object]) -> tuple[object, list[str]]:
    """Count fixture constructors during evaluation, excluding plan construction."""
    calls = []

    def trace(frame: FrameType, event: str, arg: object) -> None:
        """Record only these two files' fixture constructors during the observed call."""
        if event == "call" and frame.f_code.co_name == "__init__" and frame.f_code.co_filename.endswith((
            "graph_slice_probe.py", "alias_demand_probe.py",
        )):
            calls.append(type(frame.f_locals["self"]).__qualname__)

    previous = sys.getprofile()
    sys.setprofile(trace)
    try:
        result = call()
    finally:
        sys.setprofile(previous)
    return result, calls


def main() -> None:
    """Prove active alias selection, conflict policy, unequal depth and conditional reuse."""
    directory = Path(__file__).resolve().parent
    before = _source_fingerprints(directory.parents[2])
    own_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    fixture_hash = hashlib.sha256((directory / "graph_slice_probe.py").read_bytes()).hexdigest()
    rows = []
    cases = (
        ("secondary_alias", {"right>token>value": 91}, 91, False),
        ("cut_primary", {"left": Branch(Token(77)), "right>token>value": 91}, 91, False),
        ("inactive_primary_input", {"left": Branch(Token(77)), "left>token>value": 91}, 13, False),
        ("matching_alias_inputs", {"left>token>value": 91, "right>token>value": 91}, 91, False),
        ("conflicting_alias_inputs", {"left>token>value": 21, "right>token>value": 91}, 0, True),
        ("inactive_conflict", {"left": Branch(Token(77)), "left>token>value": 21, "right>token>value": 91}, 91, False),
    )
    for name, raw, expected, conflict in cases:
        world = World()
        try:
            world.setup_model(name, PairRoot, ((Token, Existence.many), (Branch, Existence.unique_per_conduit)))
            probe = SliceProbe(world)
            plan = AliasPlan(probe)
            try:
                try:
                    plan.build(raw)
                    plan.bind_values(raw)
                except AliasInputConflict:
                    assert conflict
                    rows.append({"case": name, "conflict_before_construction": True})
                    continue
                assert not conflict and len(plan.sites) == 3
                result, calls = observe(partial(plan.evaluate, raw))
                assert len(calls) == 3 and result.right.token.value == expected
                if "left" in raw:
                    assert result.left is raw["left"]
                else:
                    assert result.left is result.right
                rows.append({"case": name, "sites": len(plan.sites), "constructors": calls,
                             "right_value": result.right.token.value, "inactive": plan.inactive.copy()})
                if name == "secondary_alias":
                    site_count = len(plan.sites)
                    for value in (None, False, 0, object()):
                        changed = plan.evaluate({"right>token>value": value})
                        assert changed.right.token.value is value
                    assert len(plan.sites) == site_count
                    rows[-1]["changing_values_same_plan"] = 4
            finally:
                plan.cleanup()
                probe.cleanup()
        finally:
            world.cleanup()
    for root in (UnequalDepthRoot, ReuseSiblingRoot):
        world = World()
        try:
            world.setup_model(root.__name__, root, ((Token, Existence.many), (Branch, Existence.unique_per_conduit), (Wrapper, Existence.many)))
            probe = SliceProbe(world)
            plan = AliasPlan(probe)
            try:
                raw = {"wrapped>branch>token>value": 91} if root is UnequalDepthRoot else {}
                plan.build(raw)
                result, calls = observe(partial(plan.evaluate, raw))
                assert len(calls) == 4 and len(plan.sites) == 4
                if root is UnequalDepthRoot:
                    assert result.direct is result.wrapped.branch and result.direct.token.value == 91
                    rows.append({"case": "unequal_depth", "constructors": calls, "value": 91, "sites": 4})
                else:
                    shared = Branch(Token(77))
                    shared_id = next(site.spell_id for site in plan.sites if probe.lookup[site.spell_id].spell is Branch)
                    reused, reused_calls = observe(partial(plan.evaluate, raw, {shared_id: shared}))
                    assert len(reused_calls) == 2 and reused.branch is shared
                    assert reused.token is not shared.token
                    fresh, fresh_calls = observe(partial(plan.evaluate, raw))
                    assert len(fresh_calls) == 4 and fresh.branch is not shared
                    rows.append({"case": "reuse_then_fresh_same_plan", "sites": 4, "reuse_constructors": reused_calls, "fresh_constructors": fresh_calls})
            finally:
                plan.cleanup()
                probe.cleanup()
        finally:
            world.cleanup()
    world = World()
    try:
        world.setup_model("specificity", PairRoot, ((Token, Existence.many), (Branch, Existence.unique_per_conduit)))
        probe = SliceProbe(world)
        plan, equal_rank_plan = AliasPlan(probe), AliasPlan(probe)
        try:
            ranked = {"**value": 21, "right>token>value": 91}
            equal_rank = {"left>token>value": 21, "right>token>value": 91}
            plan.build(ranked)
            result = plan.evaluate(ranked)
            assert result.left is result.right and result.right.token.value == 91
            _, same_sockets, _, different_ranks = plan.selection(equal_rank)
            assert same_sockets == plan.socket_shape and different_ranks != plan.rank_shape
            with pytest.raises(PreparedShapeMismatch):
                plan.bind_values(equal_rank)
            equal_rank_plan.build(equal_rank)
            with pytest.raises(AliasInputConflict):
                equal_rank_plan.bind_values(equal_rank)
            rows.append({"case": "same_socket_set_different_specificity", "winning_value": 91,
                         "rebind_required": True, "equal_rank_conflict": True})
        finally:
            plan.cleanup()
            equal_rank_plan.cleanup()
            probe.cleanup()
    finally:
        world.cleanup()
    after = _source_fingerprints(directory.parents[2])
    changed = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
    report = {"timestamp": datetime.now(UTC).isoformat(), "python": sys.version, "source_sha256": before,
              "source_changed": changed, "diagnostic_sha256": own_hash,
              "fixture_sha256": fixture_hash, "cases": rows,
              "policy": "Ignore valid inactive targets; reject active equal-rank physical-socket conflicts.",
              "limits": "Untimed interpreter; reuse injected, no native admission, locks, hooks or disposal."}
    (directory / "alias_results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    assert not changed and hashlib.sha256(Path(__file__).read_bytes()).hexdigest() == own_hash
    assert hashlib.sha256((directory / "graph_slice_probe.py").read_bytes()).hexdigest() == fixture_hash


if __name__ == "__main__":
    main()
