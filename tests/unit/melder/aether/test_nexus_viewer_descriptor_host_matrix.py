from typing import Optional

import pytest

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.spellbook.existence.existence import Existence
from tests._nexus_viewer_matrix_support import build_multi_frame_viewer


def _build_host_viewer():
    return build_multi_frame_viewer(
        ("ops", "finance"),
        descriptor_kwargs_by_frame_name={
            "ops": {
                "spell_payload_types": ("general", "detailed"),
                "conduit_count": 2,
                "spellframe_values": ("LogicFrame", "OpsFrame"),
                "permission_values": (Permissions.create, Permissions.read),
                "existence_values": (Existence.unique, Existence.many),
                "spellbook_ids": ("ops-spellbook-a", "ops-spellbook-b"),
                "visible_root_conduit_names": ("ops_root_1", "ops_root_2"),
            },
            "finance": {
                "spell_payload_types": ("general", "general"),
                "conduit_count": 1,
                "spellframe_values": ("FinanceFrame", "LogicFrame"),
                "permission_values": (Permissions.block, Permissions.create),
                "existence_values": (
                    Existence.unique_per_conduit,
                    Existence.unique,
                ),
                "spellbook_ids": ("finance-spellbook-a", "finance-spellbook-a"),
                "visible_root_conduit_names": ("finance_root_1",),
            },
        },
    )


HOST_LIST_CASES = [
    ("list_frame_ids", {}, ["finance-frame", "ops-frame"]),
    ("list_frame_ids", {"frame_name": "ops"}, ["ops-frame"]),
    ("list_frame_ids", {"frame_name": "finance"}, ["finance-frame"]),
    (
        "list_nexus_contracts",
        {},
        [
            {
                "frame_name": "finance",
                "nexus_label": "default",
                "nexus_version": "0.0.1",
            },
            {
                "frame_name": "ops",
                "nexus_label": "default",
                "nexus_version": "0.0.1",
            },
        ],
    ),
    (
        "list_nexus_contracts",
        {"frame_name": "ops"},
        [
            {
                "frame_name": "ops",
                "nexus_label": "default",
                "nexus_version": "0.0.1",
            }
        ],
    ),
    ("list_conduit_record_ids", {}, ["finance-conduit-1", "ops-conduit-1", "ops-conduit-2"]),
    ("list_conduit_record_ids", {"frame_name": "ops"}, ["ops-conduit-1", "ops-conduit-2"]),
    ("list_conduit_record_ids", {"frame_name": "finance"}, ["finance-conduit-1"]),
    ("list_root_conduit_ids", {}, ["finance-conduit-1", "ops-conduit-1", "ops-conduit-2"]),
    ("list_root_conduit_ids", {"frame_name": "ops"}, ["ops-conduit-1", "ops-conduit-2"]),
    ("list_root_conduit_ids", {"frame_name": "finance"}, ["finance-conduit-1"]),
    (
        "list_origin_spellbook_ids",
        {},
        ["finance-spellbook-a", "ops-spellbook-a", "ops-spellbook-b"],
    ),
    (
        "list_origin_spellbook_ids",
        {"frame_name": "ops"},
        ["ops-spellbook-a", "ops-spellbook-b"],
    ),
    (
        "list_origin_spellbook_ids",
        {"frame_name": "finance"},
        ["finance-spellbook-a"],
    ),
    (
        "list_spell_record_ids",
        {},
        ["finance-spell-1", "finance-spell-2", "ops-spell-1", "ops-spell-2"],
    ),
    (
        "list_spell_record_ids",
        {"frame_name": "ops"},
        ["ops-spell-1", "ops-spell-2"],
    ),
    (
        "list_spell_record_ids",
        {"frame_name": "finance"},
        ["finance-spell-1", "finance-spell-2"],
    ),
    (
        "list_spell_record_keys",
        {},
        [
            ("finance-spellbook-a", "finance-spell-1"),
            ("finance-spellbook-a", "finance-spell-2"),
            ("ops-spellbook-a", "ops-spell-1"),
            ("ops-spellbook-b", "ops-spell-2"),
        ],
    ),
    (
        "list_spell_record_keys",
        {"frame_name": "ops"},
        [("ops-spellbook-a", "ops-spell-1"), ("ops-spellbook-b", "ops-spell-2")],
    ),
    (
        "list_spell_record_keys",
        {"frame_name": "finance"},
        [
            ("finance-spellbook-a", "finance-spell-1"),
            ("finance-spellbook-a", "finance-spell-2"),
        ],
    ),
    (
        "list_spell_names",
        {},
        ["FinanceSpell1", "FinanceSpell2", "OpsSpell1", "OpsSpell2"],
    ),
    ("list_spell_names", {"frame_name": "ops"}, ["OpsSpell1", "OpsSpell2"]),
    (
        "list_binding_names",
        {},
        ["finance_spell_1", "finance_spell_2", "ops_spell_1", "ops_spell_2"],
    ),
    (
        "list_binding_names",
        {"frame_name": "finance"},
        ["finance_spell_1", "finance_spell_2"],
    ),
    (
        "list_lineage_ids",
        {},
        [
            "finance-lineage-1",
            "finance-lineage-2",
            "ops-lineage-1",
            "ops-lineage-2",
        ],
    ),
    (
        "list_spellframes",
        {},
        ["FinanceFrame", "LogicFrame", "OpsFrame"],
    ),
    (
        "list_spellframes",
        {"frame_name": "ops"},
        ["LogicFrame", "OpsFrame"],
    ),
    (
        "list_spellframes",
        {"frame_name": "finance"},
        ["FinanceFrame", "LogicFrame"],
    ),
    ("list_permissions", {}, ["block", "create", "read"]),
    ("list_permissions", {"frame_name": "ops"}, ["create", "read"]),
    ("list_permissions", {"frame_name": "finance"}, ["block", "create"]),
    ("list_existence_kinds", {}, ["many", "unique", "unique_per_conduit"]),
    ("list_existence_kinds", {"frame_name": "ops"}, ["many", "unique"]),
    (
        "list_existence_kinds",
        {"frame_name": "finance"},
        ["unique", "unique_per_conduit"],
    ),
]


@pytest.mark.parametrize(
    ("method_name", "kwargs", "expected"),
    HOST_LIST_CASES,
    ids=[
        "{0}_{1}".format(method_name, kwargs.get("frame_name", "all"))
        for method_name, kwargs, _ in HOST_LIST_CASES
    ],
)
def test_viewer_descriptor_host_list_matrix(
        method_name: str,
        kwargs: dict[str, object],
        expected: object,
) -> None:
    viewer = _build_host_viewer()

    result = getattr(viewer, method_name)(**kwargs)

    assert result == expected


HOST_COUNT_CASES = [
    ("count_frames", {}, 2),
    ("count_conduit_records", {}, 3),
    ("count_conduit_records", {"frame_name": "ops"}, 2),
    ("count_conduit_records", {"frame_name": "finance"}, 1),
    ("count_root_conduits", {}, 3),
    ("count_root_conduits", {"frame_name": "ops"}, 2),
    ("count_root_conduits", {"frame_name": "finance"}, 1),
    ("count_spell_records", {}, 4),
    ("count_spell_records", {"frame_name": "ops"}, 2),
    ("count_spell_records", {"frame_name": "finance"}, 2),
    ("count_spellbooks", {}, 3),
    ("count_spellbooks", {"frame_name": "ops"}, 2),
    ("count_spellbooks", {"frame_name": "finance"}, 1),
]


@pytest.mark.parametrize(
    ("method_name", "kwargs", "expected"),
    HOST_COUNT_CASES,
)
def test_viewer_descriptor_host_count_matrix(
        method_name: str,
        kwargs: dict[str, object],
        expected: int,
) -> None:
    viewer = _build_host_viewer()

    result = getattr(viewer, method_name)(**kwargs)

    assert result == expected


SPELL_FILTER_CASES = [
    ("list_spells_by_owner_conduit", {"conduit_id": "ops-conduit-1"}, ["ops-spellbook-a:ops-spell-1"]),
    ("list_spells_by_owner_conduit", {"conduit_id": "ops-conduit-2"}, ["ops-spellbook-b:ops-spell-2"]),
    ("list_spells_by_owner_conduit", {"conduit_id": "finance-conduit-1"}, ["finance-spellbook-a:finance-spell-1", "finance-spellbook-a:finance-spell-2"]),
    ("list_spells_by_owner_conduit", {"conduit_id": "ops-conduit-1", "frame_name": "ops"}, ["ops-spellbook-a:ops-spell-1"]),
    ("list_spells_by_spellbook_id", {"spellbook_id": "ops-spellbook-a"}, ["ops-spellbook-a:ops-spell-1"]),
    ("list_spells_by_spellbook_id", {"spellbook_id": "ops-spellbook-b"}, ["ops-spellbook-b:ops-spell-2"]),
    ("list_spells_by_spellbook_id", {"spellbook_id": "finance-spellbook-a"}, ["finance-spellbook-a:finance-spell-1", "finance-spellbook-a:finance-spell-2"]),
    ("list_spells_by_spellbook_id", {"spellbook_id": "finance-spellbook-a", "frame_name": "finance"}, ["finance-spellbook-a:finance-spell-1", "finance-spellbook-a:finance-spell-2"]),
    ("list_spells_by_permission", {"permission": "create"}, ["finance-spellbook-a:finance-spell-2", "ops-spellbook-a:ops-spell-1"]),
    ("list_spells_by_permission", {"permission": "read"}, ["ops-spellbook-b:ops-spell-2"]),
    ("list_spells_by_permission", {"permission": "block"}, ["finance-spellbook-a:finance-spell-1"]),
    ("list_spells_by_permission", {"permission": "create", "frame_name": "finance"}, ["finance-spellbook-a:finance-spell-2"]),
    ("list_spells_by_existence", {"existence": "unique"}, ["finance-spellbook-a:finance-spell-2", "ops-spellbook-a:ops-spell-1"]),
    ("list_spells_by_existence", {"existence": "many"}, ["ops-spellbook-b:ops-spell-2"]),
    ("list_spells_by_existence", {"existence": "unique_per_conduit"}, ["finance-spellbook-a:finance-spell-1"]),
    ("list_spells_by_existence", {"existence": "many", "frame_name": "ops"}, ["ops-spellbook-b:ops-spell-2"]),
    ("list_spells_by_spellframe", {"spellframe_name": "LogicFrame"}, ["finance-spellbook-a:finance-spell-2", "ops-spellbook-a:ops-spell-1"]),
    ("list_spells_by_spellframe", {"spellframe_name": "OpsFrame"}, ["ops-spellbook-b:ops-spell-2"]),
    ("list_spells_by_spellframe", {"spellframe_name": "FinanceFrame"}, ["finance-spellbook-a:finance-spell-1"]),
    ("list_spells_by_spellframe", {"spellframe_name": "LogicFrame", "frame_name": "ops"}, ["ops-spellbook-a:ops-spell-1"]),
]


@pytest.mark.parametrize(
    ("method_name", "kwargs", "expected"),
    SPELL_FILTER_CASES,
)
def test_viewer_descriptor_host_spell_filter_matrix(
        method_name: str,
        kwargs: dict[str, object],
        expected: list[str],
) -> None:
    viewer = _build_host_viewer()

    result = getattr(viewer, method_name)(**kwargs)

    assert result == expected


SPELL_RECORD_CASES = [
    (
        "ops-spellbook-a:ops-spell-1",
        None,
        {
            "frame_name": "ops",
            "source_id": "ops-spellbook-a:ops-spell-1",
            "record_key": ("ops-spellbook-a", "ops-spell-1"),
            "spell_id": "ops-spell-1",
            "spell_index_id": "ops-lineage-1",
            "origin_spellbook_id": "ops-spellbook-a",
            "owner_conduit_id": "ops-conduit-1",
            "spell_name": "OpsSpell1",
            "binding_name": "ops_spell_1",
            "spellframe": "LogicFrame",
            "permissions": "create",
            "existence": "unique",
            "payload_type": "general",
            "payload_version": "0.0.1",
            "nexus_label": "default",
            "nexus_version": "0.0.1",
        },
    ),
    (
        "ops-spellbook-b:ops-spell-2",
        "ops",
        {
            "frame_name": "ops",
            "source_id": "ops-spellbook-b:ops-spell-2",
            "record_key": ("ops-spellbook-b", "ops-spell-2"),
            "spell_id": "ops-spell-2",
            "spell_index_id": "ops-lineage-2",
            "origin_spellbook_id": "ops-spellbook-b",
            "owner_conduit_id": "ops-conduit-2",
            "spell_name": "OpsSpell2",
            "binding_name": "ops_spell_2",
            "spellframe": "OpsFrame",
            "permissions": "read",
            "existence": "many",
            "payload_type": "detailed",
            "payload_version": "0.0.1",
            "nexus_label": "default",
            "nexus_version": "0.0.1",
        },
    ),
    (
        "finance-spellbook-a:finance-spell-1",
        "finance",
        {
            "frame_name": "finance",
            "source_id": "finance-spellbook-a:finance-spell-1",
            "record_key": ("finance-spellbook-a", "finance-spell-1"),
            "spell_id": "finance-spell-1",
            "spell_index_id": "finance-lineage-1",
            "origin_spellbook_id": "finance-spellbook-a",
            "owner_conduit_id": "finance-conduit-1",
            "spell_name": "FinanceSpell1",
            "binding_name": "finance_spell_1",
            "spellframe": "FinanceFrame",
            "permissions": "block",
            "existence": "unique_per_conduit",
            "payload_type": "general",
            "payload_version": "0.0.1",
            "nexus_label": "default",
            "nexus_version": "0.0.1",
        },
    ),
]


@pytest.mark.parametrize(
    ("spell_source_id", "frame_name", "expected"),
    SPELL_RECORD_CASES,
)
def test_viewer_descriptor_host_spell_record_matrix(
        spell_source_id: str,
        frame_name: Optional[str],
        expected: dict[str, object],
) -> None:
    viewer = _build_host_viewer()

    result = viewer.describe_spell_record(
        spell_source_id,
        frame_name=frame_name,
    )

    assert result == expected


def test_viewer_descriptor_host_summary_methods_report_expected_shapes() -> None:
    viewer = _build_host_viewer()

    inventory = viewer.describe_descriptor_inventory()
    topology = viewer.describe_descriptor_topology("ops")
    conduit_records = viewer.describe_conduit_records("ops")
    spell_records = viewer.describe_spell_records("finance")

    assert inventory == {
        "frame_count": 2,
        "frame_names": ("finance", "ops"),
        "frame_ids": ("finance-frame", "ops-frame"),
        "conduit_record_count": 3,
        "root_conduit_ids": ("finance-conduit-1", "ops-conduit-1", "ops-conduit-2"),
        "spell_record_count": 4,
        "origin_spellbook_count": 3,
        "origin_spellbook_ids": ("finance-spellbook-a", "ops-spellbook-a", "ops-spellbook-b"),
        "permissions": ("block", "create", "read"),
        "existence_kinds": ("many", "unique", "unique_per_conduit"),
    }
    assert topology == {
        "frame_name": "ops",
        "frame_id": "ops-frame",
        "root_conduit_ids": ("ops-conduit-1", "ops-conduit-2"),
        "conduit_ids_by_root_id": {
            "ops-conduit-1": ("ops-conduit-1",),
            "ops-conduit-2": ("ops-conduit-2",),
        },
        "spell_source_ids_by_conduit_id": {
            "ops-conduit-1": ("ops-spellbook-a:ops-spell-1",),
            "ops-conduit-2": ("ops-spellbook-b:ops-spell-2",),
        },
        "spell_record_keys_by_spellbook_id": {
            "ops-spellbook-a": (("ops-spellbook-a", "ops-spell-1"),),
            "ops-spellbook-b": (("ops-spellbook-b", "ops-spell-2"),),
        },
    }
    assert conduit_records == [
        {
            "frame_name": "ops",
            "conduit_id": "ops-conduit-1",
            "root_conduit_id": "ops-conduit-1",
            "origin_spellbook_id": "ops-spellbook",
            "nexus_label": "default",
            "nexus_version": "0.0.1",
            "is_root_conduit": True,
            "owned_spell_record_count": 1,
        },
        {
            "frame_name": "ops",
            "conduit_id": "ops-conduit-2",
            "root_conduit_id": "ops-conduit-2",
            "origin_spellbook_id": "ops-spellbook",
            "nexus_label": "default",
            "nexus_version": "0.0.1",
            "is_root_conduit": True,
            "owned_spell_record_count": 1,
        },
    ]
    assert len(spell_records) == 2
    assert spell_records[0]["frame_name"] == "finance"
    assert spell_records[1]["origin_spellbook_id"] == "finance-spellbook-a"
