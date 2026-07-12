import json

from melder.crystallizer.crystals.mutation_research_crystal import (
    MutationResearchCrystal,
)


def _composition() -> dict:
    """
    Build one two-lane composition carrying BOTH node families.

    Returns:
        dict: Set name -> composition payload (describe_composition shape).
    """
    return {
        "default": {
            "organization": {
                "set_id": "01SET",
                "name": "default",
                "lanes": [
                    {
                        "lane_id": "L1",
                        "name": "default",
                        "lane_type": "development",
                        "nodes": [
                            {
                                "spell_id": "sha-a",
                                "module_source_sha256": None,
                                "parent_spell_ids": [],
                                "author": "mutation_0",
                                "campaign": "apollo",
                                "reason": None,
                                "created_at": "2026-07-12T00:00:00Z",
                            },
                        ],
                    },
                    {
                        "lane_id": "L2",
                        "name": "subsystem",
                        "lane_type": "production",
                        "nodes": [
                            {
                                "node_type": "group",
                                "group_id": "g-1",
                                "member_spell_ids": ["sha-a"],
                                "parent_group_ids": [],
                                "author": "mutation_0",
                                "campaign": "apollo",
                                "reason": None,
                                "created_at": "2026-07-12T00:00:01Z",
                            },
                        ],
                    },
                ],
                "residence": {"lane_id_by_spell_id": {
                    "sha-a": "L1", "g-1": "L2",
                }},
            },
            "journal": {"entries": []},
        },
    }


def test_twin_derives_explicit_node_rows_per_family() -> None:
    """
    Contract (owner ruling 2026-07-12): the MR twin carries its record as
    PROPER OBJECTS - flat, DB-storable rows per node family, derived from
    the composition at construction (blob and rows cannot disagree), each
    row carrying its set/lane context.
    """
    twin = MutationResearchCrystal(
        activated=True,
        configuration_payload={},
        composition_payload=_composition(),
    )
    try:
        spells = twin.research_nodes
        groups = twin.grouped_research_nodes

        assert [row["spell_id"] for row in spells] == ["sha-a"]
        assert spells[0]["lane_name"] == "default"
        assert spells[0]["lane_type"] == "development"
        assert spells[0]["campaign"] == "apollo"

        assert [row["group_id"] for row in groups] == ["g-1"]
        assert groups[0]["member_spell_ids"] == ["sha-a"]
        assert groups[0]["lane_name"] == "subsystem"
        assert groups[0]["lane_type"] == "production"
        assert groups[0]["set_name"] == "default"
    finally:
        twin.cleanup()


def test_twin_describe_carries_rows_json_clean() -> None:
    """
    Contract: describe() exposes both row families beside the composition
    blob, the whole payload JSON round-trips (the DB-storable form), and
    Phase-A emitters (no composition) carry honest empty row lists.
    """
    twin = MutationResearchCrystal(
        activated=True,
        configuration_payload={"unrestricted_module_mutations": False},
        composition_payload=_composition(),
    )
    try:
        payload = twin.describe()
        assert payload["twin_kind"] == "mutation_research"
        assert len(payload["research_nodes"]) == 1
        assert len(payload["grouped_research_nodes"]) == 1
        assert json.loads(json.dumps(payload)) == payload
    finally:
        twin.cleanup()

    phase_a = MutationResearchCrystal(activated=True)
    try:
        payload = phase_a.describe()
        assert payload["research_nodes"] == []
        assert payload["grouped_research_nodes"] == []
    finally:
        phase_a.cleanup()
