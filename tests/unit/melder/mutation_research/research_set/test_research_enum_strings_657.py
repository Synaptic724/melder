"""Research enum string, family and historical-record contracts."""

import hashlib
import json
import pickle
from enum import Enum, StrEnum
from typing import Type

import pytest

from melder.mutation_research.research_set.research_lane import LaneState, LaneType, ResearchLane
from melder.mutation_research.research_set.research_set import ResearchSet
from melder.mutation_research.research_set.transition_entry import TransitionAct, TransitionEntry


class ForeignLaneType(StrEnum):
    """A distinct family with the same spelling as a lane policy."""

    production = "production"


@pytest.mark.parametrize("family", [LaneState, LaneType, TransitionAct])
def test_research_enums_preserve_values_and_support_strings(family: Type[Enum]) -> None:
    """Each existing value still constructs its member and is a JSON string."""
    assert issubclass(family, StrEnum)
    for member in family:
        assert member.name == member.value
        assert family(member.value) is member
        assert str(member) == member.name
        assert json.loads(json.dumps(member)) == member.name
        assert pickle.loads(pickle.dumps(member, protocol=4)) is member

    with pytest.raises(ValueError):
        family("not-a-research-value")


def test_foreign_lane_type_does_not_create_a_lane() -> None:
    """An equal foreign enum cannot be admitted as the LaneType family."""
    research = ResearchSet("family-check")
    try:
        with pytest.raises(ValueError, match="Unknown lane_type"):
            research.create_lane("wrong", lane_type=ForeignLaneType.production)
        assert "wrong" not in research.lane_names()
        assert research.create_lane("valid", lane_type=LaneType.production).lane_type is LaneType.production
        assert research.create_lane("raw", lane_type="production").lane_type is LaneType.production
    finally:
        research.cleanup()


def test_foreign_equal_enums_keep_payload_family_boundaries() -> None:
    """The shared joined spelling cannot turn a lane state into an event act."""
    lane = ResearchLane("research", lane_id="lane-stable")
    entry = TransitionEntry(7, TransitionAct.joined, "lane-stable")
    try:
        lane_payload = lane.describe()
        lane_payload["state"] = TransitionAct.joined
        rebuilt_lane = ResearchLane.from_payload(lane_payload)
        try:
            assert rebuilt_lane.state is LaneState.open
        finally:
            rebuilt_lane.cleanup()

        entry_payload = entry.describe()
        entry_payload["act"] = LaneState.joined
        with pytest.raises(ValueError, match="valid 'act'"):
            TransitionEntry.from_payload(entry_payload)
    finally:
        entry.cleanup()
        lane.cleanup()


def test_same_family_members_can_be_used_as_string_payload_values() -> None:
    """The selected string-backed family can hydrate its own recorded value."""
    lane = ResearchLane("research", lane_id="lane-stable")
    entry = TransitionEntry(7, TransitionAct.joined, "lane-stable")
    try:
        lane_payload = lane.describe()
        lane_payload["state"] = LaneState.joined
        rebuilt_lane = ResearchLane.from_payload(lane_payload)
        try:
            assert rebuilt_lane.state is LaneState.joined
        finally:
            rebuilt_lane.cleanup()

        entry_payload = entry.describe()
        entry_payload["act"] = TransitionAct.joined
        rebuilt_entry = TransitionEntry.from_payload(entry_payload)
        try:
            assert rebuilt_entry.act is TransitionAct.joined
        finally:
            rebuilt_entry.cleanup()
    finally:
        entry.cleanup()
        lane.cleanup()


def test_prechange_json_payloads_remain_exact_and_reload() -> None:
    """Fixed old lane and journal payloads retain their bytes and lifecycle."""
    lane = ResearchLane(
        "research", lane_type="production", lane_id="lane-stable",
        created_at="2026-01-01T00:00:00+00:00",
    )
    lane._mark_joined("lane-target")
    entry = TransitionEntry(
        7, TransitionAct.joined, "lane-stable",
        created_at="2026-01-01T00:00:00+00:00",
    )
    try:
        lane_json = json.dumps(lane.describe(), sort_keys=True, separators=(",", ":"))
        entry_json = json.dumps(entry.describe(), sort_keys=True, separators=(",", ":"))
        assert hashlib.sha256(lane_json.encode()).hexdigest() == (
            "16293263aef9e0bf636b9003de9b8b14aa906581bd818e0db298ee10b73f2924"
        )
        assert hashlib.sha256(entry_json.encode()).hexdigest() == (
            "1ab64da5bab04adbb97557ba667011edc6a6cfa92aba4027ab52b717783f60d6"
        )
        rebuilt_lane = ResearchLane.from_payload(json.loads(lane_json))
        rebuilt_entry = TransitionEntry.from_payload(json.loads(entry_json))
        try:
            assert rebuilt_lane.state is LaneState.joined
            assert rebuilt_lane.lane_type is LaneType.production
            assert rebuilt_entry.act is TransitionAct.joined
        finally:
            rebuilt_entry.cleanup()
            rebuilt_lane.cleanup()
    finally:
        entry.cleanup()
        lane.cleanup()


@pytest.mark.parametrize(
    ("expected", "payload_hex"),
    [
        (
            LaneState.joined,
            "80049552000000000000008c336d656c6465722e6d75746174696f6e5f7265736561726368"
            "2e72657365617263685f7365742e72657365617263685f6c616e65948c094c616e65537461"
            "74659493948c066a6f696e656494859452942e",
        ),
        (
            LaneType.production,
            "80049555000000000000008c336d656c6465722e6d75746174696f6e5f7265736561726368"
            "2e72657365617263685f7365742e72657365617263685f6c616e65948c084c616e65547970"
            "659493948c0a70726f64756374696f6e94859452942e",
        ),
        (
            TransitionAct.joined,
            "80049559000000000000008c366d656c6465722e6d75746174696f6e5f7265736561726368"
            "2e72657365617263685f7365742e7472616e736974696f6e5f656e747279948c0d5472616e"
            "736974696f6e4163749493948c066a6f696e656494859452942e",
        ),
    ],
)
def test_actual_pre_migration_pickle_still_loads(
    expected: Enum, payload_hex: str,
) -> None:
    """Historical protocol-4 values resolve to their original family members."""
    assert pickle.loads(bytes.fromhex(payload_hex)) is expected

@pytest.mark.parametrize(
    ("name", "expected"),
    [("default", LaneType.development), ("side", LaneType.experiment)],
)
@pytest.mark.parametrize("foreign", [LaneState.open, ForeignLaneType.production])
def test_foreign_enum_lane_type_payload_uses_wrong_type_fallback(
    name: str, expected: LaneType, foreign: Enum,
) -> None:
    """A foreign family follows the existing missing-type default for each lane."""
    original = ResearchLane(name, lane_type="production", lane_id="lane-stable")
    try:
        payload = original.describe()
        payload["lane_type"] = foreign
        rebuilt = ResearchLane.from_payload(payload)
        try:
            assert rebuilt.lane_type is expected
        finally:
            rebuilt.cleanup()
    finally:
        original.cleanup()
