"""Untimed structural diagnostics over real Melder occurrence and injection plans.

The row-slice simulation calls constructors directly and does not implement
Meld admission, scope reuse, hooks or disposal. Shared-alias counterexamples are
reported rather than silently normalized. Canonical plans and the earlier
emitter prototype are untouched; uncollapsed expansion owns a cloned registry.
"""

import hashlib
import json
import marshal
import sys
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from types import FrameType
from typing import Optional

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.artifacts.spell_override_targeting_codegen_creation import (
    SpellOverrideTargetingCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_graph_analyzer_strategy import (
    SpellOccurrenceGraphAnalyzerStrategy,
)
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import (
    configure_frame_posture_for_spellbook_configuration,
)
from tests.experimentation.test_melder_creation_overrides_performance import (
    MelderExperiment,
    _source_fingerprints,
)

InstanceKey = tuple[str, Optional[int]]
Graph = dict[InstanceKey, dict[str, tuple[InstanceKey, ...]]]


class Leaf:
    """Resource-free provider; profiler records each distinct occurrence."""

    def __init__(self) -> None:
        """Create one provider without external state or disposal behavior."""


class FiveRoot:
    """Five dependency sockets requesting the same provider type."""

    def __init__(self, a: Leaf, b: Leaf, c: Leaf, d: Leaf, e: Leaf) -> None:
        """Borrow supplied/injected references so individual socket cuts are visible."""
        self.a, self.b, self.c, self.d, self.e = a, b, c, d, e


class Token:
    """Transient descendant with one plain constructor input."""

    def __init__(self, value: int = 13) -> None:
        """Retain a scalar to expose whether nested targeting reaches this instance."""
        self.value = value


class Branch:
    """Provider that can be shared while its child is declared many."""

    def __init__(self, token: Token) -> None:
        """Borrow the injected child; one Branch has one physical token field."""
        self.token = token


class PairRoot:
    """Two aliases that may lead to the same shared provider."""

    def __init__(self, left: Branch, right: Branch) -> None:
        """Retain both paths so alias identity and nested values can be inspected."""
        self.left, self.right = left, right


class ChildRoot:
    """Distinguish replacing a dependency from modifying its constructor input."""

    def __init__(self, child: Token) -> None:
        """Borrow a constructed or supplied Token reference."""
        self.child = child


class CollectionRoot:
    """Expose replacement of an entire one-member collection socket."""

    def __init__(self, items: list[Leaf]) -> None:
        """Retain the exact list supplied by DI or the caller."""
        self.items = items


class World(MelderExperiment):
    """Reuse the established isolated-world cleanup while binding new fixtures."""

    def setup_model(self, name: str, root: type, bindings: tuple[tuple[type, Existence], ...]) -> None:
        """Build one automatic, uncached graph without warming its creations."""
        self.graph, self.root_type = name, root
        Aether._reset_singleton_for_tests()
        Spellbook._aether = Aether()
        Conduit._aether = Spellbook._aether
        config = SpellbookConfiguration(f"occurrence-{name}").with_defaults()
        config.with_phase_scheduler_workers(1)
        frame = configure_frame_posture_for_spellbook_configuration(config, dynamic=False)
        frame.with_system_caching_enabled(False)
        self.book = Spellbook(aetheric_frame=config._aether_frame, configuration=config)
        for provider, existence in bindings:
            self.book.bind(spell=provider, existence=existence, permissions="create")
        self.root_id = self.book.bind(spell=root, existence=Existence.many, permissions="create")
        self.conduit = self.book.conjure(name="probe", dynamic=False)


class SliceProbe:
    """Own detached diagnostic graphs and borrow a live model for one scene."""

    def __init__(self, world: MelderExperiment) -> None:
        """Clone path state before expanding logical occurrences for comparison."""
        self.world = world
        self.root = world.book._spell_id_pool[world.root_id]
        self.artifact = self.root._compiler_artifact
        self.model = self.artifact._spell_codegen_model
        self.lookup = world.book._spell_id_pool
        self.manifest_bytes = marshal.dumps(
            self.artifact._spell_codegen_creation.metadata["codegen_creation_manifest"]
        )
        blueprint = self.artifact._root_blueprint_phase5
        self.registry = blueprint.path_registry.clone()
        targeting = self.model.override_targeting_shape
        self.targeting = SpellOverrideTargetingCodegenCreation.from_analysis(
            root_spell_id=world.root_id,
            targets_by_spec=targeting.targets_by_spec,
            specificity_by_spec=targeting.specificity_by_spec,
        )
        self.logical_graph = SpellOccurrenceGraphAnalyzerStrategy()._build_occurrence_graph(
            dag=blueprint.dag, root_spell_id=world.root_id, collapse_shared_occurrences=False,
            spell_lookup=self.lookup, spell_system_states=self.root._spell_system_states,
            path_registry=self.registry, spellbook=world.book, root_blueprint=blueprint,
        )
        self.instance_graph: Graph = {
            key: {name: tuple(source.dependency_keys or ()) for name, source in spec.param_sources.items()}
            for key, spec in self.model.injection_shape.instance_specs_by_instance_key.items()
        }

    def cleanup(self) -> None:
        """Release owned scratch graphs and clone; do not clean borrowed model state."""
        self.targeting.cleanup()
        self.registry.cleanup()
        self.logical_graph.clear()
        self.instance_graph.clear()
        del self.targeting
        del self.registry
        del self.logical_graph
        del self.instance_graph
        del self.manifest_bytes
        del self.world
        del self.root
        del self.artifact
        del self.model
        del self.lookup

    def physical_key(self, occurrence: InstanceKey) -> InstanceKey:
        """Mirror current phase-9 shared grouping without inventing alias translation."""
        return (occurrence[0], None) if occurrence[0] in self.model.instance_shape.shared_spell_ids else occurrence

    def label(self, key: InstanceKey) -> str:
        """Describe a key with provider name and its logical or shared path label."""
        path = "<shared>" if key[1] is None else self.registry.format_path(key[1]) or "<root>"
        return f"{self.lookup[key[0]].spell_name}@{path}"

    @staticmethod
    def closure(
        graph: Mapping[InstanceKey, Mapping[str, Sequence[InstanceKey]]],
        root: InstanceKey, supplied: dict[InstanceKey, dict[str, object]],
    ) -> set[InstanceKey]:
        """Visit root-required nodes, cutting all edges of each supplied parameter.

        Presence controls cuts, including None/False/empty containers. The
        operation is per shape, O(nodes + edges), not proposed per meld work.
        """
        seen: set[InstanceKey] = set()
        pending = [root]
        while pending:
            key = pending.pop()
            if key in seen:
                continue
            seen.add(key)
            for name, children in graph[key].items():
                if name not in supplied.get(key, {}):
                    pending.extend(children)
        return seen

    @staticmethod
    def observe(call: Callable[[], object]) -> tuple[object, list[str]]:
        """Record fixture constructors during an untimed call; restore profiling."""
        sequence: list[str] = []

        def trace(frame: FrameType, event: str, arg: object) -> None:
            """Capture only fixture constructors, excluding compiler/helper allocations."""
            code = frame.f_code
            if event == "call" and code.co_name == "__init__" and code.co_filename.endswith((
                "graph_slice_probe.py", "test_overrides_all.py", "deep_layers.py",
            )):
                sequence.append(type(frame.f_locals["self"]).__qualname__)

        previous = sys.getprofile()
        sys.setprofile(trace)
        try:
            value = call()
        finally:
            sys.setprofile(previous)
        return value, sequence

    def simulate(self, retained: set[InstanceKey], supplied: dict[InstanceKey, dict[str, object]]) -> object:
        """Execute a row-only slice directly, without native scope/hook/disposal semantics."""
        results: dict[InstanceKey, object] = {}
        specs = self.model.injection_shape.instance_specs_by_instance_key
        for step in self.artifact._spell_codegen_plan.overrides_plan.steps:
            key = step.instance_key
            if key not in retained:
                continue
            spec = specs[key]
            assert spec.contract_payload is None and not spec.uses_positional_override
            assert step.spell.is_class_spell and not step.spell.has_disposal_methods
            kwargs = {}
            for name, source in spec.param_sources.items():
                if name in supplied.get(key, {}):
                    continue
                dependencies = source.dependency_keys
                if source.is_collection:
                    kwargs[name] = [results[child] for child in dependencies or ()]
                elif dependencies:
                    assert len(dependencies) == 1
                    kwargs[name] = results[dependencies[0]]
            kwargs.update(supplied.get(key, {}))
            results[key] = step.spell.spell(**kwargs)
        return results[self.model.instance_shape.root_instance_key]

    def run(self, name: str, raw: dict[str, object], expected_retained: int) -> dict[str, object]:
        """Compare native behavior, row slicing and logical-path closure in one scene."""
        override_map, shape = self.targeting._apply_with_socket_shape_prechecked(spell_override=raw)
        physical: dict[InstanceKey, dict[str, object]] = {}
        logical: dict[InstanceKey, dict[str, object]] = {}
        target_owners = []
        for ref, value in override_map.items():
            parent = self.registry.parent_id(ref.param_path_id)
            assert parent is not None
            owner = (ref.node_id, parent)
            logical.setdefault(owner, {})[ref.param_name] = value
            physical.setdefault(self.physical_key(owner), {})[ref.param_name] = value
            target_owners.append((ref, owner))
        root_key = self.model.instance_shape.root_instance_key
        retained = self.closure(self.instance_graph, root_key, physical)
        decoded = marshal.loads(self.manifest_bytes)
        manifest_graph = {
            tuple(step["instance_key"]): {
                param: tuple(tuple(child) for child in children)
                for param, children in step["dependency_resolution_order"]
            }
            for step in decoded["overrides"]["plan_rows"]
        }
        manifest_retained = self.closure(
            manifest_graph, tuple(decoded["no_overrides"]["root_instance_key"]), physical,
        )
        assert manifest_retained == retained
        logical_retained = self.closure(self.logical_graph, (self.world.root_id, self.registry.root_path_id), logical)
        naive_grouped = {self.physical_key(key) for key in logical_retained}
        assert len(retained) == expected_retained, (name, len(retained), expected_retained)
        native, native_calls = self.observe(lambda: self.world.conduit.meld(spell_id=self.world.root_id, override=raw))
        simulated, simulated_calls = self.observe(lambda: self.simulate(retained, physical))
        assert len(simulated_calls) == len(retained)
        row = {
            "scene": name, "raw_keys": list(raw), "shape": shape,
            "base_instance_count": len(self.instance_graph), "row_slice_count": len(retained),
            "manifest_roundtrip_closure_matches": True,
            "base_occurrence_count": len(self.model.graph_shape.occurrence_graph),
            "uncollapsed_occurrence_count": len(self.logical_graph),
            "logical_reachable_count": len(logical_retained), "naive_grouped_count": len(naive_grouped),
            "row_slice_instances": sorted(self.label(key) for key in retained),
            "naive_extra_instances": sorted(self.label(key) for key in naive_grouped - retained),
            "target_owners_absent_from_base_rows": [self.registry.format_path(ref.param_path_id) for ref, owner in target_owners if self.physical_key(owner) not in self.instance_graph],
            "targets_below_removed_logical_paths": [self.registry.format_path(ref.param_path_id) for ref, owner in target_owners if owner not in logical_retained],
            "native_constructors": native_calls, "row_simulation_constructors": simulated_calls,
        }
        if isinstance(native, FiveRoot):
            assert native.a is raw["a"] and native.b is raw["b"] and native.c is raw["c"]
            assert simulated.a is raw.get("a", simulated.a)
            assert simulated.b is raw.get("b", simulated.b)
            assert simulated.c is raw.get("c", simulated.c)
            row["remaining_d_e_share"] = simulated.d is simulated.e
            assert (native.d is native.e) == (simulated.d is simulated.e)
        if isinstance(native, CollectionRoot):
            assert simulated.items is raw["items"] and native.items is raw["items"]
        if isinstance(native, ChildRoot):
            row["native_value"] = native.child.value
            row["row_simulation_value"] = simulated.child.value
        if isinstance(native, PairRoot):
            row["native_left_right_share"] = native.left is native.right
            row["native_right_value"] = native.right.token.value
            row["row_simulation_right_value"] = simulated.right.token.value
        if name.startswith("deep"):
            assert simulated.left is raw["left"]
            if "right" in raw:
                assert simulated.right is raw["right"]
        assert marshal.dumps(
            self.artifact._spell_codegen_creation.metadata["codegen_creation_manifest"]
        ) == self.manifest_bytes
        row["canonical_manifest_unchanged"] = True
        return row


def main() -> None:
    """Run bounded real-plan counterexamples and retain source-hashed JSON evidence."""
    directory = Path(__file__).resolve().parent
    repo = directory.parents[2]
    before = _source_fingerprints(repo)
    own_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    rows = []
    scenes = (
        ("five_many_three_supplied", FiveRoot, ((Leaf, Existence.many),), {"a": None, "b": False, "c": object()}, 3),
        ("five_shared_three_supplied", FiveRoot, ((Leaf, Existence.unique_per_conduit),), {"a": None, "b": False, "c": object()}, 2),
        ("collection_replaced_empty", CollectionRoot, ((Leaf, Existence.many),), {"items": []}, 1),
        ("child_parameter", ChildRoot, ((Token, Existence.many),), {"child>value": 91}, 2),
        ("child_replaced", ChildRoot, ((Token, Existence.many),), {"child": Token(77)}, 1),
        ("shared_descendant_base", PairRoot, ((Token, Existence.many), (Branch, Existence.unique_per_conduit)), {}, 3),
        ("shared_secondary_descendant_input", PairRoot, ((Token, Existence.many), (Branch, Existence.unique_per_conduit)), {"right>token>value": 91}, 3),
        ("shared_primary_cut_secondary_input", PairRoot, ((Token, Existence.many), (Branch, Existence.unique_per_conduit)), {"left": Branch(Token(77)), "right>token>value": 91}, 3),
        ("shared_primary_cut_shadowed_input", PairRoot, ((Token, Existence.many), (Branch, Existence.unique_per_conduit)), {"left": Branch(Token(77)), "left>token>value": 91}, 3),
    )
    for name, root, bindings, raw, expected in scenes:
        world = World()
        try:
            world.setup_model(name, root, bindings)
            probe = SliceProbe(world)
            try:
                rows.append(probe.run(name, raw, expected))
            finally:
                probe.cleanup()
        finally:
            world.cleanup()
    for whole in (False, True):
        world = MelderExperiment()
        try:
            world.setup("deep", "automatic")
            native = world.conduit.meld(spell_id=world.root_id)
            raw = {"left": native.left, "right": native.right} if whole else {"left": native.left}
            probe = SliceProbe(world)
            try:
                rows.append(probe.run("deep_all" if whole else "deep_left", raw, 1 if whole else 256))
            finally:
                probe.cleanup()
        finally:
            world.cleanup()
    after = _source_fingerprints(repo)
    changed = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
    payload = {"timestamp": datetime.now(UTC).isoformat(), "python": sys.version, "source_sha256": before,
               "diagnostic_sha256": own_hash, "source_changed": changed, "scenes": rows,
               "timing": "Not measured. Row simulation is not native Meld execution."}
    (directory / "results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    assert not changed
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest() == own_hash


if __name__ == "__main__":
    main()
