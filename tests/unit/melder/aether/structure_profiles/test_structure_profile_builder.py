from typing import Dict

from melder.aether.structure_profiles.structure_profile_builder import (
    StructureProfileBuilder,
    StructureProfileTooling,
)
from melder.aether.structure_profiles.structure_profile_models import (
    FrameStructureProfile,
    SpellStructureRecord,
    StructureHint,
)
from melder.aether.dev_ops.spell_system_states.spell_system_state import SpellSystemState
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell import Spell
from melder.spellbook.spell_types.spell_types import SpellType
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.spellbook.spell_crafter.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind


class _StubSpellbook:
    _spell_system_states = object()


def _make_spell(spell_id: str, spell_index: SpellIndex) -> Spell:
    return Spell(
        spell=object(),
        spell_index=spell_index,
        spellframe=None,
        binding_name=None,
        spell_name="name",
        existence=Existence.unique,
        spell_type=SpellType.SPELL,
        spell_id=spell_id,
        permissions=Permissions.read,
        aetheric_frame="frame",
        spellbook=_StubSpellbook(),
    )


def test_build_spell_record_includes_dependencies_and_sockets() -> None:
    builder = StructureProfileBuilder()
    spell_index = SpellIndex("v1")
    spell = _make_spell("v1", spell_index)
    spell_state = SpellSystemState(spell_index.id, spell_index.current)
    spell_state.attach_dependencies(["dep-a"])
    spell_state.add_dependent("dep-b")

    socket = SpellSocketDescriptor(
        spell_id="v1",
        param_name="dep",
        position=0,
        socket_kind=SocketKind.NORMAL,
        is_collection=False,
        is_optional=False,
        target_spell_ids=("dep-a",),
        dependency_key=("frame", "binding"),
        contract_key=None,
        contract_late_binding=None,
    )
    topology = SpellLocalTopology("v1", [socket])

    record = builder.build_spell_record(
        spell=spell,
        spell_state=spell_state,
        topology=topology,
    )

    assert record.spell_id == "v1"
    assert "dep-a" in record.dependencies["direct_dependencies"]
    assert "dep-b" in record.dependencies["direct_dependents"]
    assert record.sockets[0]["socket_kind"] == "NORMAL"


def test_tooling_dependency_path_and_related_spells() -> None:
    record_a = SpellStructureRecord(
        spell_id="a",
        lineage_id="la",
        owner_conduit_id=None,
        binding_key=None,
        existence=None,
        spell_type=None,
        permissions=None,
        dependencies={"direct_dependencies": ["lb"], "direct_dependents": []},
        sockets=[],
        spellmap_defaults=[],
        derived_hints=[],
    )
    record_b = SpellStructureRecord(
        spell_id="b",
        lineage_id="lb",
        owner_conduit_id=None,
        binding_key=None,
        existence=None,
        spell_type=None,
        permissions=None,
        dependencies={"direct_dependencies": [], "direct_dependents": ["la"]},
        sockets=[],
        spellmap_defaults=[],
        derived_hints=[],
    )
    record_c = SpellStructureRecord(
        spell_id="c",
        lineage_id="lc",
        owner_conduit_id=None,
        binding_key=None,
        existence=None,
        spell_type=None,
        permissions=None,
        dependencies={"direct_dependencies": ["lb"], "direct_dependents": []},
        sockets=[],
        spellmap_defaults=[],
        derived_hints=[],
    )
    frame_profile = FrameStructureProfile(
        frame_id="frame",
        frame_name="frame",
        conduit_profiles={},
        spell_records={"a": record_a, "b": record_b, "c": record_c},
        clusters=[],
        derived_hints=[],
    )

    tooling = StructureProfileTooling(frame_profile)
    path = tooling.explain_dependency_path("a", "b")
    assert path == ["a", "b"]

    description = tooling.describe_spell_structure("la")
    assert description is not None
    assert description["spell_id"] == "a"

    related = tooling.find_related_spells("a", k=5)
    related_ids = [spell_id for spell_id, _score in related]
    assert "c" in related_ids


def test_tooling_describe_spell_structure_returns_copies() -> None:
    record = SpellStructureRecord(
        spell_id="a",
        lineage_id="la",
        owner_conduit_id=None,
        binding_key=None,
        existence=None,
        spell_type=None,
        permissions=None,
        dependencies={"direct_dependencies": ["x"], "direct_dependents": []},
        sockets=[{"spell_id": "a", "param_name": "dep", "target_spell_ids": ["x"]}],
        spellmap_defaults=[],
        derived_hints=[],
    )
    frame_profile = FrameStructureProfile(
        frame_id="frame",
        frame_name="frame",
        conduit_profiles={},
        spell_records={"a": record},
        clusters=[],
        derived_hints=[],
    )

    tooling = StructureProfileTooling(frame_profile)
    snapshot = tooling.describe_spell_structure("a")

    assert snapshot is not None
    snapshot["dependencies"]["direct_dependencies"].append("y")
    snapshot["sockets"][0]["target_spell_ids"].append("y")
    snapshot["sockets"].append({"spell_id": "a", "param_name": "extra"})

    assert "y" not in record.dependencies["direct_dependencies"]
    assert "y" not in record.sockets[0]["target_spell_ids"]
    assert len(record.sockets) == 1


def test_tooling_returns_detached_subsystems_and_hint_provenance() -> None:
    hint = StructureHint(
        kind="demo",
        description="derived",
        confidence=0.4,
        provenance={"source": "unit"},
        scope="spell",
    )
    record = SpellStructureRecord(
        spell_id="a",
        lineage_id="la",
        owner_conduit_id=None,
        binding_key=None,
        existence=None,
        spell_type=None,
        permissions=None,
        dependencies={"direct_dependencies": [], "direct_dependents": []},
        sockets=[],
        spellmap_defaults=[],
        derived_hints=[hint],
    )
    clusters = [
        {
            "name": "alpha",
            "members": ["c1"],
            "shared_spells": {"c1": {"s1"}},
        }
    ]
    frame_profile = FrameStructureProfile(
        frame_id="frame",
        frame_name="frame",
        conduit_profiles={},
        spell_records={"a": record},
        clusters=clusters,
        derived_hints=[],
    )

    tooling = StructureProfileTooling(frame_profile)
    snapshot = tooling.describe_spell_structure("a")
    subsystem_snapshot = tooling.list_subsystems()

    assert snapshot is not None
    assert snapshot["derived_hints"][0]["provenance"] == {"source": "unit"}

    snapshot["derived_hints"][0]["provenance"]["source"] = "mutated"
    subsystem_snapshot[0]["members"].append("c2")
    subsystem_snapshot[0]["shared_spells"]["c1"].add("s2")

    assert hint.provenance == {"source": "unit"}
    assert clusters[0]["members"] == ["c1"]
    assert clusters[0]["shared_spells"]["c1"] == {"s1"}


def test_tooling_missing_lookup_and_default_related_limit_behaviors() -> None:
    record_a = SpellStructureRecord(
        spell_id="a",
        lineage_id="la",
        owner_conduit_id=None,
        binding_key=None,
        existence=None,
        spell_type=None,
        permissions=None,
        dependencies={
            "direct_dependencies": ["lb"],
            "direct_dependents": ["missing-lineage"],
        },
        sockets=[],
        spellmap_defaults=[],
        derived_hints=[],
    )
    record_b = SpellStructureRecord(
        spell_id="b",
        lineage_id="lb",
        owner_conduit_id=None,
        binding_key=None,
        existence=None,
        spell_type=None,
        permissions=None,
        dependencies={"direct_dependencies": [], "direct_dependents": ["la"]},
        sockets=[],
        spellmap_defaults=[],
        derived_hints=[],
    )
    record_c = SpellStructureRecord(
        spell_id="c",
        lineage_id="lc",
        owner_conduit_id=None,
        binding_key=None,
        existence=None,
        spell_type=None,
        permissions=None,
        dependencies={"direct_dependencies": ["lb"], "direct_dependents": []},
        sockets=[],
        spellmap_defaults=[],
        derived_hints=[],
    )
    frame_profile = FrameStructureProfile(
        frame_id="frame",
        frame_name="frame",
        conduit_profiles={},
        spell_records={"a": record_a, "b": record_b, "c": record_c},
        clusters=[],
        derived_hints=[],
    )

    tooling = StructureProfileTooling(frame_profile)

    assert tooling.describe_spell_structure("missing") is None
    assert tooling.find_related_spells("missing") == []
    assert tooling.recommend_next_inspection("missing") == []
    assert tooling.find_related_spells("a") == [("c", 1)]
    assert set(tooling.recommend_next_inspection("a")) == {"b", "missing-lineage"}


def test_tooling_dependency_path_missing_and_disconnected_cases_return_none() -> None:
    record_a = SpellStructureRecord(
        spell_id="a",
        lineage_id="la",
        owner_conduit_id=None,
        binding_key=None,
        existence=None,
        spell_type=None,
        permissions=None,
        dependencies={"direct_dependencies": ["lb"], "direct_dependents": []},
        sockets=[],
        spellmap_defaults=[],
        derived_hints=[],
    )
    record_b = SpellStructureRecord(
        spell_id="b",
        lineage_id="lb",
        owner_conduit_id=None,
        binding_key=None,
        existence=None,
        spell_type=None,
        permissions=None,
        dependencies={"direct_dependencies": [], "direct_dependents": ["la"]},
        sockets=[],
        spellmap_defaults=[],
        derived_hints=[],
    )
    record_c = SpellStructureRecord(
        spell_id="c",
        lineage_id="lc",
        owner_conduit_id=None,
        binding_key=None,
        existence=None,
        spell_type=None,
        permissions=None,
        dependencies={"direct_dependencies": [], "direct_dependents": []},
        sockets=[],
        spellmap_defaults=[],
        derived_hints=[],
    )
    frame_profile = FrameStructureProfile(
        frame_id="frame",
        frame_name="frame",
        conduit_profiles={},
        spell_records={"a": record_a, "b": record_b, "c": record_c},
        clusters=[],
        derived_hints=[],
    )

    tooling = StructureProfileTooling(frame_profile)

    assert tooling.explain_dependency_path("missing", "b") is None
    assert tooling.explain_dependency_path("a", "missing") is None
    assert tooling.explain_dependency_path("a", "c") is None


def test_tooling_internal_indexes_skip_missing_and_duplicate_lineage_ids() -> None:
    record_a = SpellStructureRecord(
        spell_id="a",
        lineage_id="la",
        owner_conduit_id=None,
        binding_key=None,
        existence=None,
        spell_type=None,
        permissions=None,
        dependencies={"direct_dependencies": ["lb"], "direct_dependents": []},
        sockets=[],
        spellmap_defaults=[],
        derived_hints=[],
    )
    record_dup = SpellStructureRecord(
        spell_id="dup",
        lineage_id="la",
        owner_conduit_id=None,
        binding_key=None,
        existence=None,
        spell_type=None,
        permissions=None,
        dependencies={"direct_dependencies": [], "direct_dependents": []},
        sockets=[],
        spellmap_defaults=[],
        derived_hints=[],
    )
    record_none = SpellStructureRecord(
        spell_id="none",
        lineage_id=None,
        owner_conduit_id=None,
        binding_key=None,
        existence=None,
        spell_type=None,
        permissions=None,
        dependencies={"direct_dependencies": [], "direct_dependents": []},
        sockets=[],
        spellmap_defaults=[],
        derived_hints=[],
    )
    frame_profile = FrameStructureProfile(
        frame_id="frame",
        frame_name="frame",
        conduit_profiles={},
        spell_records={"a": record_a, "dup": record_dup, "none": record_none},
        clusters=[],
        derived_hints=[],
    )

    tooling = StructureProfileTooling(frame_profile)

    assert tooling._lineage_index() == {"la": record_a}

    graph_profile = FrameStructureProfile(
        frame_id="frame",
        frame_name="frame",
        conduit_profiles={},
        spell_records={"a": record_a, "none": record_none},
        clusters=[],
        derived_hints=[],
    )

    assert StructureProfileTooling(graph_profile)._build_dependency_graph() == {
        "la": ["lb"]
    }


def test_tooling_cleanup_is_idempotent_and_shortest_path_handles_revisits() -> None:
    record_a = SpellStructureRecord(
        spell_id="a",
        lineage_id="la",
        owner_conduit_id=None,
        binding_key=None,
        existence=None,
        spell_type=None,
        permissions=None,
        dependencies={"direct_dependencies": ["lb", "lc"], "direct_dependents": []},
        sockets=[],
        spellmap_defaults=[],
        derived_hints=[],
    )
    record_b = SpellStructureRecord(
        spell_id="b",
        lineage_id="lb",
        owner_conduit_id=None,
        binding_key=None,
        existence=None,
        spell_type=None,
        permissions=None,
        dependencies={"direct_dependencies": ["la"], "direct_dependents": []},
        sockets=[],
        spellmap_defaults=[],
        derived_hints=[],
    )
    record_c = SpellStructureRecord(
        spell_id="c",
        lineage_id="lc",
        owner_conduit_id=None,
        binding_key=None,
        existence=None,
        spell_type=None,
        permissions=None,
        dependencies={"direct_dependencies": [], "direct_dependents": []},
        sockets=[],
        spellmap_defaults=[],
        derived_hints=[],
    )
    frame_profile = FrameStructureProfile(
        frame_id="frame",
        frame_name="frame",
        conduit_profiles={},
        spell_records={"a": record_a, "b": record_b, "c": record_c},
        clusters=[],
        derived_hints=[],
    )
    tooling = StructureProfileTooling(frame_profile)

    assert tooling._shortest_path(
        {"la": ["lb", "lc"], "lb": ["la"], "lc": []},
        "la",
        "lc",
    ) == ["la", "lc"]

    tooling.cleanup()
    tooling.cleanup()

    assert tooling.cleaned is True


def test_builder_helper_branches_handle_none_and_heuristic_hints() -> None:
    builder = StructureProfileBuilder()
    spell_index = SpellIndex("v1")
    spell = _make_spell("v1", spell_index)
    invalid_state = SpellSystemState(spell_index.id, spell_index.current)
    invalid_state._validity = SpellValidity.invalid

    contract_socket = SpellSocketDescriptor(
        spell_id="v1",
        param_name="dep",
        position=0,
        socket_kind=SocketKind.SPELL_CONTRACT,
        is_collection=False,
        is_optional=False,
        target_spell_ids=("dep-a",),
        dependency_key=("frame", "binding"),
        contract_key=("frame", "binding"),
        contract_late_binding=False,
    )
    topology = SpellLocalTopology("v1", [contract_socket])

    assert builder._index_spell_system_states(None) == {}
    assert builder._extract_dependencies(None) == {
        "direct_dependencies": [],
        "direct_dependents": [],
    }
    assert builder._extract_sockets(None) == []

    hints = builder._derive_spell_hints(invalid_state, topology)

    assert [hint.kind for hint in hints] == [
        "contract_sockets_present",
        "lineage_not_valid",
    ]

    record = builder.build_spell_record(
        spell=spell,
        spell_state=invalid_state,
        topology=topology,
    )

    assert len(record.derived_hints) == 2


def test_builder_frame_cluster_scan_and_cleanup_are_error_tolerant() -> None:
    class _StubLock:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> bool:
            return False

    class _GoodCluster:
        auto_link_dependencies = True

        def check_cleaned(self) -> None:
            return None

        def get_members(self):
            return ("c1",)

        def get_shared_spells(self):
            return {"c1": {"s1"}}

    class _BadCheckCluster:
        def check_cleaned(self) -> None:
            raise RuntimeError("boom")

    class _BadSummaryCluster:
        auto_link_dependencies = False

        def check_cleaned(self) -> None:
            return None

        def get_members(self):
            raise RuntimeError("boom")

        def get_shared_spells(self):
            return {}

    class _StubConduit:
        def check_cleaned(self) -> None:
            return None

        def snapshot_state(self):
            return {
                "conduit_id": "conduit-1",
                "conduit_name": "root",
                "conduit_state": "normal",
                "dynamic_environment": False,
                "aetheric_frame": "ops",
                "spellbook_snapshot": {"local_spells": {}},
            }

    class _StubFrame:
        def __init__(self) -> None:
            self._id = "frame-1"
            self.name = "ops"
            self._lock = _StubLock()
            self._conduits = {"conduit-1": _StubConduit()}
            self._conduit_clusters = {
                "good": _GoodCluster(),
                "bad-check": _BadCheckCluster(),
                "bad-summary": _BadSummaryCluster(),
            }
            self.spell_system_states = None

        def check_cleaned(self) -> None:
            return None

    builder = StructureProfileBuilder(max_related=6)
    profile = builder.build_frame_profile(_StubFrame())

    assert profile.frame_name == "ops"
    assert profile.max_related == 6
    assert list(profile.conduit_profiles.keys()) == ["conduit-1"]
    assert profile.clusters == [
        {
            "name": "good",
            "auto_link_dependencies": True,
            "members": ["c1"],
            "shared_spells": {"c1": {"s1"}},
        }
    ]

    builder.cleanup()
    builder.cleanup()

    assert builder.cleaned is True
