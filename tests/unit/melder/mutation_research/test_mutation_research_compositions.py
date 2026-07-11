from unittest.mock import MagicMock

import pytest

from melder.mutation_research.mutation_research import MutationResearch


@pytest.fixture(autouse=True)
def reset_mutation_research_singleton() -> None:
    """
    Reset the MutationResearch singleton around each composition test.

    Returns:
        None.
    """
    MutationResearch._reset_singleton_for_tests()
    yield
    MutationResearch._reset_singleton_for_tests()


def _mock_aether() -> MagicMock:
    """
    Build one MagicMock Aether whose crystallizer poses as live custody.

    Returns:
        MagicMock: Aether double.
    """
    aether = MagicMock()
    aether._crystallizer.cleaned = False
    aether._crystallizer.activated = True
    return aether


def _activated_root(aether: MagicMock) -> MutationResearch:
    """
    Build one configured + activated root over the mocked host.

    Args:
        aether:
            Mocked Aether host.

    Returns:
        MutationResearch: Live root (no hydration - custody is a mock).
    """
    root = MutationResearch(aether=aether)
    configuration = root.create_configuration().with_defaults().activate()
    root.configure(configuration)
    root.activate(hydrate_from_record=False)
    return root


def _subsystem_root() -> MutationResearch:
    """
    Build one root carrying a small recorded subsystem:
    lane obj-a holds sha-a1 -> sha-a2 (two versions of one object),
    sha-b is declared in the default lane, and lane "subsystem" holds
    composition g1 = {sha-a1, sha-b}.

    Returns:
        MutationResearch: Prepared root.
    """
    root = _activated_root(_mock_aether())
    research_set = root.research_set()
    research_set.create_lane("obj-a")
    research_set.register_spell("sha-a1", lane="obj-a")
    research_set.register_spell("sha-a2", lane="obj-a")
    research_set.register_spell("sha-b")
    research_set.create_lane("subsystem", lane_type="production")
    research_set.register_group(
        ["sha-a1", "sha-b"], lane="subsystem", author="mutation_0",
    )
    return root


def test_group_view_reports_roster_and_drift() -> None:
    """
    Verify the roster read: per-member lane joins, and the drift flag -
    sha-a1 is pinned while its lane tip moved to sha-a2 (behind=True);
    sha-b sits at its lane tip (behind=False).
    """
    root = _subsystem_root()
    group_id = root.research_set().get_lane("subsystem").tip_spell_id

    view = root.group_view(group_id)

    assert view["member_count"] == 2
    assert view["members"]["sha-a1"]["lane_name"] == "obj-a"
    assert view["members"]["sha-a1"]["behind"] is True
    assert view["members"]["sha-a1"]["lane_tip"] == "sha-a2"
    assert view["members"]["sha-b"]["behind"] is False
    assert view["behind_count"] == 1

    with pytest.raises(RuntimeError, match="not resident"):
        root.group_view("g-ghost")
    with pytest.raises(RuntimeError, match="spell version"):
        root.group_view("sha-b")


def test_group_diff_research_pairs_version_moves() -> None:
    """
    Verify the grouped diff end to end through the root-owned engine:
    recomposing to the member's new version pairs as a lane-evidenced
    version_moved row and the compositions report ancestry_related.
    """
    root = _subsystem_root()
    research_set = root.research_set()
    first = research_set.get_lane("subsystem").tip_spell_id
    second = research_set.recompose_group(
        first, add=["sha-a2"], remove=["sha-a1"],
    )

    verdict = root.group_diff_research(first, second.group_id)

    result = verdict["result"]
    assert result["version_moved"] == [{
        "lane_id": research_set.residence_of("sha-a1"),
        "lane_name": "obj-a",
        "from_spell_id": "sha-a1",
        "to_spell_id": "sha-a2",
    }]
    assert result["added_members"] == []
    assert result["removed_members"] == []
    assert result["unchanged_members"] == ["sha-b"]
    assert result["ancestry_related"] is True


def test_group_impact_view_unions_and_measures_closure() -> None:
    """
    Verify the composition radius: member radii union, the direction
    split (internal = affected members, outbound = escapes), closure =
    internal fraction, and the adjacency lift naming OTHER current
    compositions that share affected spells.
    """
    aether = _mock_aether()
    root = _activated_root(aether)
    research_set = root.research_set()
    for sha in ("sha-a", "sha-b", "sha-x"):
        research_set.register_spell(sha)
    research_set.create_lane("subsystem")
    group = research_set.register_group(
        ["sha-a", "sha-b"], lane="subsystem",
    )
    research_set.create_lane("neighbor")
    neighbor = research_set.register_group(["sha-x"], lane="neighbor")

    def _radius(module_name=None, spell_id=None):
        return {
            "sha-a": {
                "affected_spells": ["sha-a", "sha-x"],
                "affected_modules": ["pkg.a", "pkg.shared"],
            },
            "sha-b": {
                "affected_spells": ["sha-b"],
                "affected_modules": ["pkg.b"],
            },
        }[spell_id]

    aether._crystallizer.analyze_impact.side_effect = _radius

    impact = root.group_impact_view(group.group_id)

    assert impact["affected_spells"] == ["sha-a", "sha-b", "sha-x"]
    assert impact["internal_spells"] == ["sha-a", "sha-b"]
    assert impact["outbound_spells"] == ["sha-x"]
    assert impact["closure"] == pytest.approx(2 / 3)
    assert impact["affected_modules"] == [
        "pkg.a", "pkg.b", "pkg.shared",
    ]
    assert impact["affected_compositions"] == [{
        "group_id": neighbor.group_id,
        "lane_name": "neighbor",
        "shared_members": ["sha-x"],
    }]
    assert impact["research"]["sha-x"]["declared"] is True
    assert impact["per_member"]["sha-b"]["affected_spells"] == ["sha-b"]


def test_bootloader_hydration_carries_compositions() -> None:
    """
    Verify the S3 promise at the root seam the restore engine drives:
    a recorded composition payload containing GroupedResearchNodes
    hydrates through load_recorded_composition (the wholesale-replace
    lane the bootloader calls) with members, ancestry, and type intact -
    and the grouped reads work immediately over the hydrated registry.
    """
    donor_root = _subsystem_root()
    research_set = donor_root.research_set()
    first_id = research_set.get_lane("subsystem").tip_spell_id
    second = research_set.recompose_group(first_id, add=["sha-a2"])
    second_id = second.group_id
    recorded = donor_root.describe_research_composition()
    MutationResearch._reset_singleton_for_tests()

    fresh_root = _activated_root(_mock_aether())
    fresh_root.load_recorded_composition(recorded)

    view = fresh_root.group_view(second_id)
    assert view["member_count"] == 3
    assert view["parent_group_ids"] == [first_id]
    verdict = fresh_root.group_diff_research(first_id, second_id)
    assert verdict["result"]["added_members"] == ["sha-a2"]
    row = fresh_root.residency_view(second_id)
    assert row["node_type"] == "group"
    assert row["runtime"] == "informational"


def test_residency_view_answers_node_type_honestly() -> None:
    """
    Verify kind-awareness: a composition identity answers runtime
    "informational" with node_type "group" and NO custody/frame probes
    (in_custody None), while spell identities keep the existing lanes and
    gain node_type "spell".
    """
    root = _subsystem_root()
    group_id = root.research_set().get_lane("subsystem").tip_spell_id

    group_row = root.residency_view(group_id)
    assert group_row["node_type"] == "group"
    assert group_row["runtime"] == "informational"
    assert group_row["in_custody"] is None
    assert group_row["lane_name"] == "subsystem"
    assert group_row["lane_type"] == "production"

    spell_row = root.residency_view("sha-b")
    assert spell_row["node_type"] == "spell"
    assert spell_row["declared"] is True
