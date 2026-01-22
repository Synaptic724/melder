from typing import Dict

from melder.aether.structure_profiles.structure_profile_builder import (
    StructureProfileBuilder,
    StructureProfileTooling,
)
from melder.aether.structure_profiles.structure_profile_models import (
    FrameStructureProfile,
    SpellStructureRecord,
)
from melder.aether.dev_ops.spell_system_states.spell_system_state import SpellSystemState
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
