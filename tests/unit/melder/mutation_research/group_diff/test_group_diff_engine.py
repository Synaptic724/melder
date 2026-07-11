import pytest

from melder.mutation_research.group_diff.group_diff_engine import (
    GroupDiffEngine,
)
from melder.mutation_research.group_diff.group_diff_strategy import (
    GroupDiffStrategy,
)


def _material(
        group_id: str,
        members: list,
        *,
        parents: list = None,
        lanes: dict = None,
) -> dict:
    """
    Build one composition material payload.

    Args:
        group_id:
            Composition identity stamp.
        members:
            Member identities.
        parents:
            Optional composition ancestry.
        lanes:
            Optional spell_id -> lane_id join (lane names mirror ids).

    Returns:
        dict: Resolver-shaped material.
    """
    return {
        "group_id": group_id,
        "member_spell_ids": list(members),
        "parent_group_ids": list(parents) if parents else [],
        "members": {
            spell_id: {
                "lane_id": lane_id,
                "lane_name": f"name-{lane_id}",
                "lane_state": "open",
                "lane_type": "experiment",
                "lane_tip": spell_id,
            }
            for spell_id, lane_id in (lanes or {}).items()
        },
    }


def _resolver_for(materials: dict):
    """
    Build one fake material resolver over a fixed mapping.

    Args:
        materials:
            group_id -> material payload mapping.

    Returns:
        callable: Resolver raising KeyError on unknown identities.
    """
    def resolve(group_id):
        return materials[group_id]
    return resolve


def test_engine_registers_members_default_and_dispatches() -> None:
    """
    Verify the grouped mirror: the members strategy registers by default,
    verdicts stamp both identities and the strategy, and unknown strategy
    names refuse teach-grade.
    """
    materials = {
        "g-left": _material("g-left", ["sha-a"]),
        "g-right": _material("g-right", ["sha-a", "sha-b"]),
    }
    engine = GroupDiffEngine(_resolver_for(materials))

    assert engine.list_strategy_names() == ["members"]
    verdict = engine.diff("g-left", "g-right")
    assert verdict["left_group_id"] == "g-left"
    assert verdict["strategy"] == "members"
    assert verdict["result"]["added_members"] == ["sha-b"]

    with pytest.raises(KeyError, match="Known strategies.*members"):
        engine.diff("g-left", "g-right", strategy="rosters")
    with pytest.raises(KeyError):
        engine.diff("g-left", "g-ghost")
    with pytest.raises(TypeError, match="GroupDiffStrategy"):
        engine.register_strategy(object())
    engine.cleanup()
    engine.cleanup()
    with pytest.raises(RuntimeError):
        engine.diff("g-left", "g-right")


def test_members_strategy_pairs_lane_evidenced_moves() -> None:
    """
    Verify the semantic win: a removed identity and an added identity
    sharing a LANE pair as version_moved (never guessed - identities
    without a lane join report as plain added/removed), unchanged members
    list by name, and ancestry_related fires when one composition parents
    the other.
    """
    materials = {
        "g-1": _material(
            "g-1",
            ["sha-a1", "sha-b", "sha-gone"],
            lanes={"sha-a1": "lane-a", "sha-b": "lane-b"},
        ),
        "g-2": _material(
            "g-2",
            ["sha-a2", "sha-b", "sha-new"],
            parents=["g-1"],
            lanes={"sha-a2": "lane-a", "sha-b": "lane-b"},
        ),
    }
    engine = GroupDiffEngine(_resolver_for(materials))

    result = engine.diff("g-1", "g-2")["result"]

    assert result["identical"] is False
    assert result["version_moved"] == [{
        "lane_id": "lane-a",
        "lane_name": "name-lane-a",
        "from_spell_id": "sha-a1",
        "to_spell_id": "sha-a2",
    }]
    # No lane join for these two: honest plain rows, no pairing guess.
    assert result["removed_members"] == ["sha-gone"]
    assert result["added_members"] == ["sha-new"]
    assert result["unchanged_members"] == ["sha-b"]
    assert result["ancestry_related"] is True
    engine.cleanup()


def test_engine_open_closed_registration() -> None:
    """
    Verify new grouped strategies extend the family without engine edits
    and duplicate names are refused.
    """
    class _SizeStrategy(GroupDiffStrategy):
        __slots__ = GroupDiffStrategy.__slots__

        @property
        def name(self) -> str:
            self.check_cleaned()
            return "sizes"

        def diff(self, left_material, right_material):
            self.check_cleaned()
            return {
                "left_size": len(left_material["member_spell_ids"]),
                "right_size": len(right_material["member_spell_ids"]),
            }

    materials = {
        "g-1": _material("g-1", ["sha-a"]),
        "g-2": _material("g-2", ["sha-a", "sha-b"]),
    }
    engine = GroupDiffEngine(_resolver_for(materials))
    engine.register_strategy(_SizeStrategy())

    verdict = engine.diff("g-1", "g-2", strategy="sizes")
    assert verdict["result"] == {"left_size": 1, "right_size": 2}
    with pytest.raises(ValueError, match="already owns"):
        engine.register_strategy(_SizeStrategy())
    engine.cleanup()
