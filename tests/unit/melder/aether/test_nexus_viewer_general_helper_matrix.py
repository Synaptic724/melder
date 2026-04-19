from typing import Dict, Optional, Sequence, Tuple

import pytest

from tests._nexus_viewer_matrix_support import (
    build_spell_record_key,
    build_viewer,
)


def _visible_conduit_ids(frame_name: str, conduit_count: int = 2) -> Tuple[str, ...]:
    return tuple(
        "{0}-conduit-{1}".format(frame_name, current_index)
        for current_index in range(1, conduit_count + 1)
    )


def _visible_spell_keys(frame_name: str, spell_count: int = 2) -> Tuple[Tuple[str, str], ...]:
    return tuple(
        build_spell_record_key(frame_name, current_index)
        for current_index in range(1, spell_count + 1)
    )


FRAME_FIELDSETS = (
    ("minimal", ("system_state", "rift_enabled")),
    ("ai", ("system_state", "rift_enabled", "ai_native_enabled")),
    ("counts", ("root_conduit_count", "conduit_cloud_entry_count")),
    (
        "all",
        (
            "system_state",
            "rift_enabled",
            "ai_native_enabled",
            "root_conduit_count",
            "conduit_cloud_entry_count",
        ),
    ),
)
FRAME_FIELD_EXPECTED = {
    "system_state": "dynamic",
    "rift_enabled": True,
    "ai_native_enabled": True,
    "root_conduit_count": 2,
    "conduit_cloud_entry_count": 2,
}
FRAME_FIELD_CASES = [
    pytest.param(field_name, fieldset_name, fieldset_fields)
    for field_name in FRAME_FIELD_EXPECTED.keys()
    for fieldset_name, fieldset_fields in FRAME_FIELDSETS
]


@pytest.mark.parametrize(
    ("field_name", "fieldset_name", "visible_fields"),
    FRAME_FIELD_CASES,
    ids=[
        "{0}_{1}".format(field_name, fieldset_name)
        for field_name, fieldset_name, _ in FRAME_FIELD_CASES
    ],
)
def test_frame_payload_field_matrix(
        field_name: str,
        fieldset_name: str,
        visible_fields: Tuple[str, ...],
) -> None:
    viewer = build_viewer(
        "ops",
        conduit_count=2,
        spell_payload_types=("general", "detailed"),
        visible_conduit_ids=_visible_conduit_ids("ops"),
        visible_spell_keys=_visible_spell_keys("ops"),
        conduit_sections_by_id={
            "ops-conduit-1": ("conduit_name", "conduit_state"),
            "ops-conduit-2": ("conduit_name", "conduit_state"),
        },
        spell_sections_by_key={
            build_spell_record_key("ops", 1): (
                "binding_payload",
                "resolution_payload",
                "metadata",
            ),
            build_spell_record_key("ops", 2): (
                "binding_payload",
                "class_profile",
                "callable_profile",
                "instance_members",
                "dynamic_access",
            ),
        },
        frame_payload_fields=visible_fields,
    )

    if field_name in visible_fields:
        assert viewer.get_frame_payload_field(
            frame_name="ops",
            field_name=field_name,
        ) == FRAME_FIELD_EXPECTED[field_name]
    else:
        with pytest.raises(
                ValueError,
                match="is not visible",
        ):
            viewer.get_frame_payload_field(
                frame_name="ops",
                field_name=field_name,
            )


TARGET_LOOKUP_CASES = [
    ("ops", None, 1),
    ("ops", "frame", 1),
    ("ops", "conduit", 0),
    ("ops", "spell", 0),
    ("root_1", None, 1),
    ("root_1", "frame", 0),
    ("root_1", "conduit", 1),
    ("root_1", "spell", 0),
    ("root_2", None, 1),
    ("root_2", "frame", 0),
    ("root_2", "conduit", 1),
    ("root_2", "spell", 0),
    ("ops_spell_1", None, 1),
    ("ops_spell_1", "frame", 0),
    ("ops_spell_1", "conduit", 0),
    ("ops_spell_1", "spell", 1),
    ("ops_spell_2", None, 1),
    ("ops_spell_2", "frame", 0),
    ("ops_spell_2", "conduit", 0),
    ("ops_spell_2", "spell", 1),
]


@pytest.mark.parametrize(
    ("display_name", "source_kind", "expected_count"),
    TARGET_LOOKUP_CASES,
    ids=[
        "{0}_{1}".format(display_name, source_kind or "any")
        for display_name, source_kind, _ in TARGET_LOOKUP_CASES
    ],
)
def test_find_target_by_display_name_matrix(
        display_name: str,
        source_kind: Optional[str],
        expected_count: int,
) -> None:
    viewer = build_viewer(
        "ops",
        conduit_count=2,
        spell_payload_types=("general", "detailed"),
        visible_conduit_ids=_visible_conduit_ids("ops"),
        visible_spell_keys=_visible_spell_keys("ops"),
        conduit_sections_by_id={
            "ops-conduit-1": ("conduit_name", "conduit_state"),
            "ops-conduit-2": ("conduit_name", "conduit_state"),
        },
        spell_sections_by_key={
            build_spell_record_key("ops", 1): ("binding_payload", "metadata"),
            build_spell_record_key("ops", 2): ("binding_payload", "metadata"),
        },
    )

    targets = viewer.find_target_by_display_name(
        frame_name="ops",
        display_name=display_name,
        source_kind=source_kind,
    )

    assert len(targets) == expected_count


CONDUIT_ACCESS_CASES = [
    (True, ("conduit_name", "conduit_state"), True, False, False),
    (True, ("policy",), False, True, False),
    (True, ("peer_conduit_ids",), False, False, True),
    (True, ("conduit_name", "policy"), True, True, False),
    (True, ("conduit_name", "peer_conduit_ids"), True, False, True),
    (True, ("conduit_state", "peer_conduit_ids"), True, False, True),
    (True, ("conduit_name", "conduit_state", "policy"), True, True, False),
    (True, ("conduit_name", "conduit_state", "peer_conduit_ids"), True, False, True),
    (True, ("policy", "peer_conduit_ids"), False, True, True),
    (True, ("conduit_name", "conduit_state", "policy", "peer_conduit_ids"), True, True, True),
    (False, tuple(), False, False, False),
    (False, ("conduit_name",), False, False, False),
    (False, ("conduit_state",), False, False, False),
    (False, ("policy",), False, False, False),
    (False, ("peer_conduit_ids",), False, False, False),
    (False, ("conduit_name", "policy"), False, False, False),
    (False, ("conduit_name", "peer_conduit_ids"), False, False, False),
    (False, ("conduit_state", "peer_conduit_ids"), False, False, False),
    (False, ("policy", "peer_conduit_ids"), False, False, False),
    (False, ("conduit_name", "conduit_state", "policy", "peer_conduit_ids"), False, False, False),
]


@pytest.mark.parametrize(
    ("visible", "visible_sections", "payload_visible", "policy_visible", "peer_links_visible"),
    CONDUIT_ACCESS_CASES,
)
def test_explain_conduit_access_matrix(
        visible: bool,
        visible_sections: Tuple[str, ...],
        payload_visible: bool,
        policy_visible: bool,
        peer_links_visible: bool,
) -> None:
    visible_ids = ("ops-conduit-1",) if visible else tuple()
    viewer = build_viewer(
        "ops",
        conduit_count=2,
        spell_payload_types=("general", "general"),
        visible_conduit_ids=visible_ids,
        visible_spell_keys=_visible_spell_keys("ops"),
        conduit_sections_by_id={"ops-conduit-1": visible_sections},
        spell_sections_by_key={
            build_spell_record_key("ops", 1): ("binding_payload",),
            build_spell_record_key("ops", 2): ("binding_payload",),
        },
    )

    explanation = viewer.explain_conduit_access(
        frame_name="ops",
        conduit_id="ops-conduit-1",
    )

    assert explanation["visible"] is visible
    assert explanation["payload_visible"] is payload_visible
    assert explanation["policy_visible"] is policy_visible
    assert explanation["peer_links_visible"] is peer_links_visible


CONDUIT_FIELD_CASES = [
    ("conduit_name", ("conduit_name",), "root_1"),
    ("conduit_state", ("conduit_state",), "normal"),
    ("policy", ("policy",), "default"),
    ("peer_conduit_ids", ("peer_conduit_ids",), ("ops-conduit-2",)),
    ("conduit_name", ("conduit_name", "conduit_state"), "root_1"),
    ("conduit_state", ("conduit_name", "conduit_state"), "normal"),
    ("policy", ("policy", "peer_conduit_ids"), "default"),
    ("peer_conduit_ids", ("policy", "peer_conduit_ids"), ("ops-conduit-2",)),
    ("conduit_name", ("conduit_name", "policy"), "root_1"),
    ("policy", ("conduit_name", "policy"), "default"),
    ("conduit_state", ("conduit_state", "peer_conduit_ids"), "normal"),
    ("peer_conduit_ids", ("conduit_state", "peer_conduit_ids"), ("ops-conduit-2",)),
    ("conduit_name", ("conduit_name", "conduit_state", "policy", "peer_conduit_ids"), "root_1"),
    ("policy", ("conduit_name", "conduit_state", "policy", "peer_conduit_ids"), "default"),
    ("peer_conduit_ids", ("conduit_name", "conduit_state", "policy", "peer_conduit_ids"), ("ops-conduit-2",)),
]


@pytest.mark.parametrize(
    ("field_name", "visible_sections", "expected_value"),
    CONDUIT_FIELD_CASES,
)
def test_get_conduit_payload_field_matrix(
        field_name: str,
        visible_sections: Tuple[str, ...],
        expected_value: object,
) -> None:
    viewer = build_viewer(
        "ops",
        conduit_count=2,
        spell_payload_types=("general", "general"),
        visible_conduit_ids=_visible_conduit_ids("ops"),
        visible_spell_keys=_visible_spell_keys("ops"),
        conduit_sections_by_id={
            "ops-conduit-1": visible_sections,
            "ops-conduit-2": ("conduit_name",),
        },
        spell_sections_by_key={
            build_spell_record_key("ops", 1): ("binding_payload",),
            build_spell_record_key("ops", 2): ("binding_payload",),
        },
        frame_payload_fields=("system_state",),
    )

    assert viewer.get_conduit_payload_field(
        frame_name="ops",
        conduit_id="ops-conduit-1",
        field_name=field_name,
    ) == expected_value


CONDUIT_TOPOLOGY_CASES = [
    ("ops-conduit-1", ("ops-conduit-2",), ("ops-spellbook", "ops-spell-1"), 1),
    ("ops-conduit-2", tuple(), ("ops-spellbook", "ops-spell-2"), 1),
    ("ops-conduit-1", ("ops-conduit-2",), ("ops-spellbook", "ops-spell-1"), 1),
    ("ops-conduit-2", tuple(), ("ops-spellbook", "ops-spell-2"), 1),
    ("ops-conduit-1", ("ops-conduit-2",), ("ops-spellbook", "ops-spell-1"), 1),
    ("ops-conduit-2", tuple(), ("ops-spellbook", "ops-spell-2"), 1),
    ("ops-conduit-1", ("ops-conduit-2",), ("ops-spellbook", "ops-spell-1"), 1),
    ("ops-conduit-2", tuple(), ("ops-spellbook", "ops-spell-2"), 1),
    ("ops-conduit-1", ("ops-conduit-2",), ("ops-spellbook", "ops-spell-1"), 1),
    ("ops-conduit-2", tuple(), ("ops-spellbook", "ops-spell-2"), 1),
]


@pytest.mark.parametrize(
    ("conduit_id", "expected_peer_ids", "expected_record_key", "expected_spell_count"),
    CONDUIT_TOPOLOGY_CASES,
)
def test_describe_conduit_topology_matrix(
        conduit_id: str,
        expected_peer_ids: Tuple[str, ...],
        expected_record_key: Tuple[str, str],
        expected_spell_count: int,
) -> None:
    viewer = build_viewer(
        "ops",
        conduit_count=2,
        spell_payload_types=("general", "detailed"),
        visible_conduit_ids=_visible_conduit_ids("ops"),
        visible_spell_keys=_visible_spell_keys("ops"),
        conduit_sections_by_id={
            "ops-conduit-1": ("conduit_name", "peer_conduit_ids"),
            "ops-conduit-2": ("conduit_name", "peer_conduit_ids"),
        },
        spell_sections_by_key={
            build_spell_record_key("ops", 1): ("binding_payload",),
            build_spell_record_key("ops", 2): ("binding_payload",),
        },
    )
    # Rebuild descriptor with peer links for this matrix.
    viewer = build_viewer(
        "ops",
        conduit_count=2,
        spell_payload_types=("general", "detailed"),
        visible_conduit_ids=_visible_conduit_ids("ops"),
        visible_spell_keys=_visible_spell_keys("ops"),
        conduit_sections_by_id={
            "ops-conduit-1": ("conduit_name", "peer_conduit_ids"),
            "ops-conduit-2": ("conduit_name", "peer_conduit_ids"),
        },
        spell_sections_by_key={
            build_spell_record_key("ops", 1): ("binding_payload",),
            build_spell_record_key("ops", 2): ("binding_payload",),
        },
    )

    topology = viewer.describe_conduit_topology(
        frame_name="ops",
        conduit_id=conduit_id,
    )

    assert topology["conduit_id"] == conduit_id
    assert topology["spell_count"] == expected_spell_count
    assert len(topology["spell_source_ids"]) == expected_spell_count


SPELL_PAYLOAD_CASES = [
    ("general", ("binding_payload",), "binding_payload"),
    ("general", ("resolution_payload",), "resolution_payload"),
    ("general", ("metadata",), "metadata"),
    ("general", ("binding_payload", "metadata"), "binding_payload"),
    ("general", ("binding_payload", "metadata"), "metadata"),
    ("general", ("binding_payload", "resolution_payload"), "binding_payload"),
    ("general", ("binding_payload", "resolution_payload"), "resolution_payload"),
    ("general", ("binding_payload", "resolution_payload", "metadata"), "metadata"),
    ("general", ("binding_payload", "resolution_payload", "metadata"), "binding_payload"),
    ("general", ("binding_payload", "resolution_payload", "metadata"), "resolution_payload"),
    ("detailed", ("class_profile",), "class_profile"),
    ("detailed", ("callable_profile",), "callable_profile"),
    ("detailed", ("instance_members",), "instance_members"),
    ("detailed", ("dynamic_access",), "dynamic_access"),
    ("detailed", ("class_profile", "callable_profile"), "class_profile"),
    ("detailed", ("class_profile", "callable_profile"), "callable_profile"),
    ("detailed", ("instance_members", "dynamic_access"), "instance_members"),
    ("detailed", ("instance_members", "dynamic_access"), "dynamic_access"),
    ("detailed", ("binding_payload", "class_profile"), "binding_payload"),
    ("detailed", ("binding_payload", "class_profile"), "class_profile"),
    ("detailed", ("metadata", "dynamic_access"), "metadata"),
    ("detailed", ("metadata", "dynamic_access"), "dynamic_access"),
    ("detailed", ("resolution_payload", "instance_members"), "resolution_payload"),
    ("detailed", ("resolution_payload", "instance_members"), "instance_members"),
    ("detailed", ("binding_payload", "resolution_payload", "metadata"), "metadata"),
]


@pytest.mark.parametrize(
    ("payload_type", "visible_sections", "section_name"),
    SPELL_PAYLOAD_CASES,
)
def test_get_spell_payload_section_matrix(
        payload_type: str,
        visible_sections: Tuple[str, ...],
        section_name: str,
) -> None:
    viewer = build_viewer(
        "ops",
        spell_payload_types=(payload_type,),
        conduit_count=1,
        visible_conduit_ids=("ops-conduit-1",),
        visible_spell_keys=(build_spell_record_key("ops", 1),),
        conduit_sections_by_id={"ops-conduit-1": ("conduit_name",)},
        spell_sections_by_key={build_spell_record_key("ops", 1): visible_sections},
        frame_payload_fields=("system_state",),
    )

    value = viewer.get_spell_payload_section(
        frame_name="ops",
        spell_source_id="ops-spellbook:ops-spell-1",
        section_name=section_name,
    )

    assert value is not None


SPELL_DETAIL_CASES = [
    ("general", ("binding_payload",), "payload_not_detailed", False),
    ("general", ("metadata",), "payload_not_detailed", False),
    ("general", ("binding_payload", "resolution_payload"), "payload_not_detailed", False),
    ("general", ("binding_payload", "metadata"), "payload_not_detailed", False),
    ("general", ("binding_payload", "resolution_payload", "metadata"), "payload_not_detailed", False),
    ("general", ("class_profile",), "payload_not_detailed", False),
    ("general", ("class_profile", "callable_profile"), "payload_not_detailed", False),
    ("general", ("instance_members",), "payload_not_detailed", False),
    ("general", ("dynamic_access",), "payload_not_detailed", False),
    ("general", ("class_profile", "dynamic_access"), "payload_not_detailed", False),
    ("detailed", ("binding_payload",), "acl_restricted", False),
    ("detailed", ("metadata",), "acl_restricted", False),
    ("detailed", ("binding_payload", "metadata"), "acl_restricted", False),
    ("detailed", ("class_profile",), "available", True),
    ("detailed", ("callable_profile",), "available", True),
    ("detailed", ("instance_members",), "available", True),
    ("detailed", ("dynamic_access",), "available", True),
    ("detailed", ("class_profile", "callable_profile"), "available", True),
    ("detailed", ("instance_members", "dynamic_access"), "available", True),
    ("detailed", ("class_profile", "instance_members", "dynamic_access"), "available", True),
]


@pytest.mark.parametrize(
    ("payload_type", "visible_sections", "expected_reason", "expected_available"),
    SPELL_DETAIL_CASES,
)
def test_describe_spell_detail_matrix(
        payload_type: str,
        visible_sections: Tuple[str, ...],
        expected_reason: str,
        expected_available: bool,
) -> None:
    viewer = build_viewer(
        "ops",
        spell_payload_types=(payload_type,),
        conduit_count=1,
        visible_conduit_ids=("ops-conduit-1",),
        visible_spell_keys=(build_spell_record_key("ops", 1),),
        conduit_sections_by_id={"ops-conduit-1": ("conduit_name",)},
        spell_sections_by_key={build_spell_record_key("ops", 1): visible_sections},
        frame_payload_fields=("system_state",),
    )

    detail = viewer.describe_spell_detail(
        frame_name="ops",
        spell_source_id="ops-spellbook:ops-spell-1",
    )

    assert detail["reason"] == expected_reason
    assert detail["detail_available"] is expected_available


SPELL_LOOKUP_CASES = [
    ("general", "ops_spell_1", 1),
    ("general", "ops_spell_2", 0),
    ("detailed", "ops_spell_1", 1),
    ("detailed", "ops_spell_2", 0),
    ("general", "missing", 0),
    ("detailed", "missing", 0),
    ("general", "ops_spell_1", 1),
    ("general", "ops_spell_1", 1),
    ("detailed", "ops_spell_1", 1),
    ("detailed", "ops_spell_1", 1),
]


@pytest.mark.parametrize(
    ("payload_type", "binding_name", "expected_count"),
    SPELL_LOOKUP_CASES,
)
def test_find_spell_by_binding_name_matrix(
        payload_type: str,
        binding_name: str,
        expected_count: int,
) -> None:
    viewer = build_viewer(
        "ops",
        spell_payload_types=(payload_type,),
        conduit_count=1,
        visible_conduit_ids=("ops-conduit-1",),
        visible_spell_keys=(build_spell_record_key("ops", 1),),
        conduit_sections_by_id={"ops-conduit-1": ("conduit_name",)},
        spell_sections_by_key={build_spell_record_key("ops", 1): ("binding_payload",)},
        frame_payload_fields=("system_state",),
    )

    spells = viewer.find_spell_by_binding_name(
        frame_name="ops",
        binding_name=binding_name,
    )

    assert len(spells) == expected_count


SPELL_TYPE_FILTER_CASES = [
    (("general",), "general", 1),
    (("general",), "detailed", 0),
    (("detailed",), "general", 0),
    (("detailed",), "detailed", 1),
    (("general", "detailed"), "general", 1),
    (("general", "detailed"), "detailed", 1),
    (("general", "general"), "general", 2),
    (("detailed", "detailed"), "detailed", 2),
    (("general", "general", "detailed"), "general", 2),
    (("general", "general", "detailed"), "detailed", 1),
]


@pytest.mark.parametrize(
    ("payload_types", "filter_type", "expected_count"),
    SPELL_TYPE_FILTER_CASES,
)
def test_list_spells_by_payload_type_matrix(
        payload_types: Sequence[str],
        filter_type: str,
        expected_count: int,
) -> None:
    visible_keys = tuple(
        build_spell_record_key("ops", current_index)
        for current_index in range(1, len(payload_types) + 1)
    )
    viewer = build_viewer(
        "ops",
        spell_payload_types=payload_types,
        conduit_count=1,
        visible_conduit_ids=("ops-conduit-1",),
        visible_spell_keys=visible_keys,
        conduit_sections_by_id={"ops-conduit-1": ("conduit_name",)},
        spell_sections_by_key={
            build_spell_record_key("ops", current_index): ("binding_payload",)
            for current_index in range(1, len(payload_types) + 1)
        },
        frame_payload_fields=("system_state",),
    )

    spells = viewer.list_spells_by_payload_type(
        frame_name="ops",
        payload_type=filter_type,
    )

    assert len(spells) == expected_count
