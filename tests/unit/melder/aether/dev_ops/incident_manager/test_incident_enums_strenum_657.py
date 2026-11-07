"""Incident enum string migration and historical by-value compatibility."""

import json
import pickle
from enum import Enum, StrEnum
from typing import cast

import pytest

from melder.aether.aetheric_frame.dev_ops.devops_information_registry import DevopsInformationRegistry
from melder.aether.aetheric_frame.dev_ops.incident_manager.incident_manager import IncidentManager
from melder.aether.aetheric_frame.dev_ops.incident_manager.incident_severity import IncidentSeverity
from melder.aether.aetheric_frame.dev_ops.incident_manager.incident_status import IncidentStatus


@pytest.mark.parametrize(
    ("enum_type", "pickle_prefix"),
    [
        (
            IncidentSeverity,
            "80049566000000000000008c476d656c6465722e6165746865722e61657468657269635f6672616d652e"
            "6465765f6f70732e696e636964656e745f6d616e616765722e696e636964656e745f7365766572697479"
            "948c10496e636964656e7453657665726974799493944b",
        ),
        (
            IncidentStatus,
            "80049562000000000000008c456d656c6465722e6165746865722e61657468657269635f6672616d652e"
            "6465765f6f70732e696e636964656e745f6d616e616765722e696e636964656e745f737461747573948c"
            "0e496e636964656e745374617475739493944b",
        ),
    ],
)
def test_incident_enums_keep_old_numeric_inputs_and_pickles(
    enum_type: type[Enum], pickle_prefix: str,
) -> None:
    """Each new value equals its name and each captured old pickle remains readable."""
    for number, member in enumerate(enum_type, start=1):
        old_pickle = bytes.fromhex(pickle_prefix) + bytes([number]) + bytes.fromhex("859452942e")
        assert isinstance(member, StrEnum)
        assert member.value == member.name
        assert str(member) == member.name
        assert json.loads(json.dumps(member)) == member.name
        assert enum_type(number) is member
        assert enum_type(float(number)) is member
        assert pickle.loads(old_pickle) is member


@pytest.mark.parametrize("enum_type", [IncidentSeverity, IncidentStatus])
@pytest.mark.parametrize("invalid", [0, 5, "unknown", None, []])
def test_incident_enums_reject_unknown_values(enum_type: type[Enum], invalid: object) -> None:
    """Unknown values remain invalid for both incident vocabularies."""
    with pytest.raises(ValueError):
        enum_type(invalid)


def test_incident_manager_filter_remains_member_identity_based() -> None:
    """String equality must not admit a non-member as an incident status filter."""
    class ForeignStatus(StrEnum):
        resolved = "resolved"

    registry = DevopsInformationRegistry("incident-test")
    manager = IncidentManager(registry)
    try:
        incident = manager.create_incident(kind="test", severity=IncidentSeverity.error, summary="failure")
        assert manager.list_incidents(status=IncidentStatus.open) == [incident]
        incident.resolve()
        assert manager.list_incidents(status=IncidentStatus.resolved) == [incident]
        assert manager.list_incidents(status=cast(IncidentStatus, "resolved")) == []
        assert manager.list_incidents(status=cast(IncidentStatus, ForeignStatus.resolved)) == []
    finally:
        manager.cleanup()
        registry.cleanup()