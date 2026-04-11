import json
from typing import Optional

import pytest

import melder
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.frame_acl_compiled_access_surface import (
    CompiledFrameACLAccessSurface,
)
from melder.aether.nexus.frame_descriptor.conduit_descriptor_payload import (
    ConduitDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.conduit_record import ConduitRecord
from melder.aether.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.aether.nexus.frame_descriptor.frame_descriptor_payload import (
    FrameDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.frame_record import FrameRecord
from melder.aether.nexus.frame_descriptor.spell_descriptor_payload import (
    SpellDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.spell_record import SpellRecord
from melder.aether.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from melder.aether.nexus.rift.frame_viewer.profiles.frame_viewer_profile import (
    FrameViewerProfile,
)
from melder.utilities.helpers.class_surface_ast_describer import (
    ClassSurfaceAstDescriber,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.existence.existence import Existence
from tests._nexus_viewer_matrix_support import (
    build_multi_frame_viewer,
    build_spell_record_key,
    build_viewer,
)


def _build_descriptor(frame_name: str) -> FrameDescriptor:
    descriptor = FrameDescriptor(frame_name)
    descriptor.set_frame_overview(
        FrameRecord(
            frame_name=frame_name,
            frame_id="{0}-frame".format(frame_name),
            config_origin_spellbook_id="{0}-spellbook".format(frame_name),
            payload=FrameDescriptorPayload(
                system_state=SystemState.dynamic,
                ai_native_enabled=True,
                rift_enabled=True,
                root_conduit_count=1,
                root_conduit_ids=("{0}-conduit".format(frame_name),),
                named_root_conduits=(( "{0}-conduit".format(frame_name), "root"),),
                conduit_cloud_entry_count=1,
                conduit_cloud_names=("root",),
                cluster_count=0,
                cluster_names=tuple(),
            ),
        )
    )
    descriptor.upsert_conduit_record(
        ConduitRecord(
            conduit_id="{0}-conduit".format(frame_name),
            root_conduit_id="{0}-conduit".format(frame_name),
            frame_name=frame_name,
            origin_spellbook_id="{0}-spellbook".format(frame_name),
            payload=ConduitDescriptorPayload(
                conduit_name="root",
                conduit_state=ConduitState.normal,
                policy=Policies.default,
                peer_conduit_ids=tuple(),
            ),
        )
    )
    descriptor.upsert_spell_record(
        SpellRecord(
            origin_spellbook_id="{0}-spellbook".format(frame_name),
            frame_name=frame_name,
            owner_conduit_id="{0}-conduit".format(frame_name),
            spell_id="{0}-spell".format(frame_name),
            lineage_id="{0}-lineage".format(frame_name),
            spell_name="{0}Spell".format(frame_name.title()),
            spellframe=None,
            binding_name="{0}_spell".format(frame_name),
            permissions=Permissions.create,
            existence=Existence.unique,
            payload=SpellDescriptorPayload(
                payload_type="general",
                binding_payload={"kind": "class"},
                resolution_payload={"requirements": []},
                class_profile=None,
                callable_profile=None,
                metadata={"frame": frame_name},
                instance_members={},
                dynamic_access={},
            ),
        )
    )
    return descriptor


def _build_detailed_descriptor(
        frame_name: str,
        *,
        include_dunders: bool = False,
) -> FrameDescriptor:
    descriptor = _build_descriptor(frame_name)
    class_profile = {"methods": ["run"]}
    instance_members = {"state": {"type": "str"}}
    if include_dunders:
        class_profile = {
            "members": {
                "__dict__": {"kind": "attribute"},
                "state": {"kind": "attribute"},
            },
            "methods": {
                "__enter__": {"signature": "() -> Self"},
                "run": {"signature": "() -> None"},
            },
        }
        instance_members = {
            "__dict__": {"type": "dict", "is_dunder": True},
            "state": {"type": "str", "is_dunder": False},
        }
    descriptor.upsert_spell_record(
        SpellRecord(
            nexus_label="default",
            nexus_version="0.0.1",
            origin_spellbook_id="{0}-spellbook".format(frame_name),
            frame_name=frame_name,
            owner_conduit_id="{0}-conduit".format(frame_name),
            spell_id="{0}-spell".format(frame_name),
            lineage_id="{0}-lineage".format(frame_name),
            spell_name="{0}Spell".format(frame_name.title()),
            spellframe=None,
            binding_name="{0}_spell".format(frame_name),
            permissions=Permissions.create,
            existence=Existence.unique,
            payload=SpellDescriptorPayload(
                payload_type="detailed",
                binding_payload={"kind": "class"},
                resolution_payload={"requirements": []},
                class_profile=class_profile,
                callable_profile={"signature": "() -> None"},
                metadata={"frame": frame_name},
                instance_members=instance_members,
                dynamic_access={"has_getattr": False},
            ),
        )
    )
    return descriptor


def _build_surface(
        frame_name: str,
        configuration: FrameACLConfiguration,
        *,
        conduit_sections_by_id: Optional[dict[str, tuple[str, ...]]] = None,
        spell_sections_by_key: Optional[dict[tuple[str, str], tuple[str, ...]]] = None,
) -> CompiledFrameACLAccessSurface:
    return CompiledFrameACLAccessSurface(
        frame_name=frame_name,
        configuration_id=configuration.configuration_id,
        view_profile_name=configuration.view_configuration.profile_name,
        view_profile_version=configuration.view_configuration.profile_version,
        codegen_profile_name=configuration.codegen_configuration.profile_name,
        codegen_profile_version=configuration.codegen_configuration.profile_version,
        allowed_kinds=("frame", "conduit", "spell"),
        allowed_commands=("query",),
        frame_payload_fields=("system_state", "rift_enabled"),
        visible_conduit_ids=("{0}-conduit".format(frame_name),),
        visible_spell_keys=(( "{0}-spellbook".format(frame_name), "{0}-spell".format(frame_name)),),
        conduit_payload_sections_by_id=conduit_sections_by_id or {
            "{0}-conduit".format(frame_name): ("conduit_name", "conduit_state")
        },
        spell_payload_sections_by_key=spell_sections_by_key or {
            ("{0}-spellbook".format(frame_name), "{0}-spell".format(frame_name)): (
                "binding_payload",
                "resolution_payload",
                "metadata",
            )
        },
        metadata={"visible_spell_count": 1},
    )


def _build_viewer(frame_names: tuple[str, ...]) -> FrameViewer:
    descriptors = {name: _build_descriptor(name) for name in frame_names}
    configurations = {
        name: FrameACLConfiguration.create_default(name)
        for name in frame_names
    }
    surfaces = {
        name: _build_surface(name, configurations[name])
        for name in frame_names
    }
    return FrameViewer(
        frame_descriptors_by_name=descriptors,
        frame_acl_configurations_by_frame_name=configurations,
        compiled_access_surfaces_by_frame_name=surfaces,
        default_view_frame_name=frame_names[0] if len(frame_names) > 0 else None,
    )


def _build_collision_viewer() -> FrameViewer:
    viewer = build_multi_frame_viewer(
        ("ops", "finance"),
        descriptor_kwargs_by_frame_name={
            "ops": {
                "spell_payload_types": ("general", "general"),
                "conduit_count": 1,
                "spellbook_ids": ("shared-book", "ops-book"),
                "spellframe_values": ("LogicFrame", "OpsFrame"),
                "permission_values": (Permissions.create, Permissions.read),
                "existence_values": (Existence.unique, Existence.many),
            },
            "finance": {
                "spell_payload_types": ("general", "general"),
                "conduit_count": 1,
                "spellbook_ids": ("shared-book", "shared-book"),
                "spellframe_values": ("LogicFrame", "FinanceFrame"),
                "permission_values": (Permissions.block, Permissions.create),
                "existence_values": (Existence.unique_per_conduit, Existence.unique),
            },
        },
    )
    for frame_name, spell_record_key in (
            ("ops", ("shared-book", "ops-spell-1")),
            ("finance", ("shared-book", "finance-spell-1")),
    ):
        descriptor = viewer.frame_descriptors_by_name[frame_name]
        spell_record = descriptor.spell_records_by_key[spell_record_key]
        spell_record.binding_name = "shared_binding"
        spell_record.spell_name = "SharedSpell"
        spell_record.lineage_id = "shared-lineage"
    return viewer


def _build_visible_collision_viewer() -> FrameViewer:
    viewer = build_viewer(
        "ops",
        spell_payload_types=("general", "detailed"),
        conduit_count=2,
        visible_conduit_ids=("ops-conduit-1", "ops-conduit-2"),
        visible_spell_keys=(
            build_spell_record_key("ops", 1),
            build_spell_record_key("ops", 2),
        ),
        conduit_sections_by_id={
            "ops-conduit-1": (
                "conduit_name",
                "conduit_state",
                "policy",
                "peer_conduit_ids",
            ),
            "ops-conduit-2": (
                "conduit_name",
                "conduit_state",
                "policy",
                "peer_conduit_ids",
            ),
        },
        spell_sections_by_key={
            build_spell_record_key("ops", 1): (
                "binding_payload",
                "resolution_payload",
                "metadata",
            ),
            build_spell_record_key("ops", 2): (
                "binding_payload",
                "resolution_payload",
                "metadata",
                "class_profile",
                "callable_profile",
                "instance_members",
                "dynamic_access",
            ),
        },
        frame_payload_fields=(
            "system_state",
            "rift_enabled",
            "ai_native_enabled",
            "root_conduit_count",
            "conduit_cloud_entry_count",
        ),
        include_detail_dunders=True,
    )
    descriptor = viewer.frame_descriptors_by_name["ops"]
    first_spell = descriptor.spell_records_by_key[("ops-spellbook", "ops-spell-1")]
    second_spell = descriptor.spell_records_by_key[("ops-spellbook", "ops-spell-2")]
    first_spell.binding_name = "shared_binding"
    second_spell.binding_name = "shared_binding"
    first_spell.spell_name = "SharedSpell"
    second_spell.spell_name = "SharedSpell"
    first_spell.lineage_id = "shared-lineage"
    second_spell.lineage_id = "shared-lineage"
    first_spell.spellframe = "SharedFrame"
    second_spell.spellframe = "SharedFrame"
    return viewer


def test_frame_viewer_lists_hosted_frame_names() -> None:
    viewer = _build_viewer(("ops", "finance"))

    assert viewer.list_frame_names() == ["finance", "ops"]


def test_frame_viewer_can_switch_default_frame() -> None:
    viewer = _build_viewer(("ops", "finance"))

    viewer.set_default_view("finance")

    assert viewer.default_view_frame_name == "finance"


def test_frame_viewer_describes_available_frames() -> None:
    viewer = _build_viewer(("ops", "finance"))

    descriptions = viewer.describe_available_views()

    assert descriptions == [
        {"frame_name": "finance", "is_default": False},
        {"frame_name": "ops", "is_default": True},
    ]


def test_frame_viewer_profile_lists_targets_for_one_frame() -> None:
    viewer = _build_viewer(("ops",))

    links = viewer.execute_method("list_targets", frame_name="ops")

    assert [link.source_kind for link in links] == ["frame", "conduit", "spell"]


def test_frame_viewer_describe_frames_summarizes_all_hosted_frames() -> None:
    viewer = _build_viewer(("ops", "finance"))

    descriptions = viewer.describe_frames()

    assert list(descriptions.keys()) == ["finance", "ops"]
    assert descriptions["finance"]["frame_name"] == "finance"
    assert descriptions["finance"]["spell_record_count"] == 1
    assert descriptions["ops"]["frame_name"] == "ops"
    assert descriptions["ops"]["is_default"] is True


def test_frame_viewer_profile_lists_targets_for_default_frame() -> None:
    viewer = _build_viewer(("ops",))

    targets = viewer.execute_method("list_targets")

    assert [target.source_kind for target in targets] == ["frame", "conduit", "spell"]


def test_frame_viewer_profile_describe_targets_adds_metadata_for_detailed_profile() -> None:
    viewer = _build_viewer(("ops",))

    descriptions = viewer.execute_method("describe_targets")

    assert descriptions[0]["source_kind"] == "frame"
    assert "metadata" in descriptions[0]


def test_frame_viewer_can_list_active_viewer_profiles_and_set_default() -> None:
    viewer = _build_viewer(("ops",))

    assert viewer.list_view_profile_names() == ["general"]

    viewer.set_default_view_profile("general")

    assert viewer.profile_name == "general"


def test_frame_viewer_execute_method_routes_through_profile_mapping() -> None:
    viewer = _build_viewer(("ops",))

    descriptions = viewer.execute_method(
        "describe_targets",
    )

    assert descriptions[0]["source_kind"] == "frame"
    assert "metadata" in descriptions[0]


def test_frame_viewer_bound_view_frame_can_get_required_target_by_source() -> None:
    viewer = _build_viewer(("ops",))

    link = viewer.get_selected_profile_for_frame("ops").view_frame.get_required_target_by_source(
        source_kind="spell",
        source_id="ops-spellbook:ops-spell",
    )

    assert link.display_name == "ops_spell"


def test_frame_viewer_profile_list_targets_can_filter_by_kind() -> None:
    viewer = _build_viewer(("ops", "finance"))

    ops_targets = viewer.execute_method("list_targets", frame_name="ops")
    ops_spells = viewer.execute_method(
        "list_targets",
        frame_name="ops",
        source_kind="spell",
    )

    assert len(ops_targets) == 3
    assert len(ops_spells) == 1
    assert [target.display_name for target in ops_targets] == ["ops", "root", "ops_spell"]


def test_frame_viewer_describe_frame_summarizes_descriptor_driven_surface() -> None:
    viewer = _build_viewer(("ops",))

    summary = viewer.execute_method(
        "describe_frame",
        frame_name="ops",
    )

    assert summary["frame_name"] == "ops"
    assert summary["frame_id"] == "ops-frame"
    assert summary["nexus_label"] == "default"
    assert summary["nexus_version"] == "0.0.1"
    assert summary["conduit_record_count"] == 1
    assert summary["root_conduit_count"] == 1
    assert summary["spell_record_count"] == 1
    assert summary["is_default"] is True


def test_frame_viewer_host_count_methods_report_descriptor_counts() -> None:
    viewer = _build_viewer(("ops", "finance"))

    assert viewer.execute_method("count_frames") == 2
    assert viewer.execute_method("count_root_conduits") == 2
    assert viewer.execute_method("count_spell_records") == 2


def test_frame_viewer_describe_frame_inventory_reports_visible_ids() -> None:
    viewer = _build_viewer(("ops",))

    inventory = viewer.execute_method(
        "describe_frame_inventory",
        frame_name="ops",
    )

    assert inventory == {
        "frame_name": "ops",
        "target_count": 3,
        "conduit_count": 1,
        "spell_count": 1,
        "conduit_ids": ("ops-conduit",),
        "spell_source_ids": ("ops-spellbook:ops-spell",),
    }


def test_frame_viewer_describe_frame_access_contract_reports_acl_surface() -> None:
    viewer = _build_viewer(("ops",))

    contract = viewer.execute_method(
        "describe_frame_access_contract",
        frame_name="ops",
    )

    assert contract["frame_name"] == "ops"
    assert contract["view_profile_name"] == "safe"
    assert contract["codegen_profile_name"] == "safe"
    assert contract["frame_payload_fields"] == ("system_state", "rift_enabled")


def test_frame_viewer_find_target_by_display_name_returns_exact_matches() -> None:
    viewer = _build_viewer(("ops",))

    targets = viewer.execute_method(
        "find_target_by_display_name",
        frame_name="ops",
        display_name="ops_spell",
    )

    assert len(targets) == 1
    assert targets[0].source_kind == "spell"


def test_frame_viewer_explain_target_access_reports_visible_spell_sections() -> None:
    viewer = _build_viewer(("ops",))

    explanation = viewer.execute_method(
        "explain_target_access",
        frame_name="ops",
        source_kind="spell",
        source_id="ops-spellbook:ops-spell",
    )

    assert explanation == {
        "source_kind": "spell",
        "source_id": "ops-spellbook:ops-spell",
        "target_exists": True,
        "visible": True,
        "reason": "visible",
        "visible_sections": (
            "binding_payload",
            "resolution_payload",
            "metadata",
        ),
    }


def test_frame_viewer_describe_frame_payload_filters_to_visible_fields() -> None:
    viewer = _build_viewer(("ops",))

    payload_description = viewer.execute_method(
        "describe_frame_payload",
        frame_name="ops",
    )

    assert payload_description["frame_name"] == "ops"
    assert payload_description["visible_fields"] == ("system_state", "rift_enabled")
    assert payload_description["payload"] == {
        "system_state": "dynamic",
        "rift_enabled": True,
    }


def test_frame_viewer_describe_conduit_returns_acl_filtered_payload() -> None:
    viewer = _build_viewer(("ops",))

    conduit_description = viewer.execute_method(
        "describe_conduit",
        frame_name="ops",
        conduit_id="ops-conduit",
    )

    assert conduit_description["source_kind"] == "conduit"
    assert conduit_description["visible_sections"] == (
        "conduit_name",
        "conduit_state",
    )
    assert conduit_description["payload"] == {
        "conduit_name": "root",
        "conduit_state": "normal",
    }


def test_frame_viewer_describe_conduit_topology_reports_visible_spell_links() -> None:
    viewer = _build_viewer(("ops",))

    topology = viewer.execute_method(
        "describe_conduit_topology",
        frame_name="ops",
        conduit_id="ops-conduit",
    )

    assert topology == {
        "conduit_id": "ops-conduit",
        "peer_conduit_ids": tuple(),
        "spell_count": 1,
        "spell_source_ids": ("ops-spellbook:ops-spell",),
    }


def test_frame_viewer_find_conduit_by_name_returns_exact_matches() -> None:
    viewer = _build_viewer(("ops",))

    conduits = viewer.execute_method(
        "find_conduit_by_name",
        frame_name="ops",
        conduit_name="root",
    )

    assert len(conduits) == 1
    assert conduits[0].source_kind == "conduit"


def test_frame_viewer_explain_conduit_access_reports_acl_flags() -> None:
    viewer = _build_viewer(("ops",))

    explanation = viewer.execute_method(
        "explain_conduit_access",
        frame_name="ops",
        conduit_id="ops-conduit",
    )

    assert explanation == {
        "source_kind": "conduit",
        "source_id": "ops-conduit",
        "target_exists": True,
        "visible": True,
        "reason": "visible",
        "visible_sections": ("conduit_name", "conduit_state"),
        "payload_visible": True,
        "policy_visible": False,
        "peer_links_visible": False,
    }


def test_frame_viewer_get_conduit_payload_field_returns_visible_value() -> None:
    viewer = _build_viewer(("ops",))

    conduit_state = viewer.execute_method(
        "get_conduit_payload_field",
        frame_name="ops",
        conduit_id="ops-conduit",
        field_name="conduit_state",
    )

    assert conduit_state == "normal"


def test_frame_viewer_describe_spell_returns_acl_filtered_payload() -> None:
    viewer = _build_viewer(("ops",))

    spell_description = viewer.execute_method(
        "describe_spell",
        frame_name="ops",
        spell_source_id="ops-spellbook:ops-spell",
    )

    assert spell_description["source_kind"] == "spell"
    assert spell_description["payload_type"] == "general"
    assert spell_description["visible_sections"] == (
        "binding_payload",
        "resolution_payload",
        "metadata",
    )
    assert spell_description["payload"] == {
        "binding_payload": {"kind": "class"},
        "resolution_payload": {"requirements": []},
        "metadata": {"frame": "ops"},
    }


def test_frame_viewer_describe_spell_omits_missing_detailed_sections_for_general_payload() -> None:
    descriptor = _build_descriptor("ops")
    configuration = FrameACLConfiguration.create_default("ops")
    surface = _build_surface(
        "ops",
        configuration,
        spell_sections_by_key={
            ("ops-spellbook", "ops-spell"): (
                "binding_payload",
                "class_profile",
                "callable_profile",
                "metadata",
            ),
        },
    )
    viewer = FrameViewer(
        frame_descriptors_by_name={"ops": descriptor},
        frame_acl_configurations_by_frame_name={"ops": configuration},
        compiled_access_surfaces_by_frame_name={"ops": surface},
        default_view_frame_name="ops",
    )

    spell_description = viewer.execute_method(
        "describe_spell",
        frame_name="ops",
        spell_source_id="ops-spellbook:ops-spell",
    )

    assert spell_description["payload_type"] == "general"
    assert spell_description["visible_sections"] == (
        "binding_payload",
        "class_profile",
        "callable_profile",
        "metadata",
    )
    assert spell_description["payload"] == {
        "binding_payload": {"kind": "class"},
        "metadata": {"frame": "ops"},
    }


def test_frame_viewer_describe_spell_detail_reports_payload_not_detailed() -> None:
    viewer = _build_viewer(("ops",))

    detail = viewer.execute_method(
        "describe_spell_detail",
        frame_name="ops",
        spell_source_id="ops-spellbook:ops-spell",
    )

    assert detail == {
        "spell_source_id": "ops-spellbook:ops-spell",
        "payload_type": "general",
        "detail_available": False,
        "reason": "payload_not_detailed",
        "visible_sections": (
            "binding_payload",
            "resolution_payload",
            "metadata",
        ),
        "payload": {},
    }


def test_frame_viewer_find_spell_by_binding_name_returns_exact_match() -> None:
    viewer = _build_viewer(("ops",))

    spells = viewer.execute_method(
        "find_spell_by_binding_name",
        frame_name="ops",
        binding_name="ops_spell",
    )

    assert len(spells) == 1
    assert spells[0].source_kind == "spell"


def test_frame_viewer_list_spells_by_payload_type_filters_visible_spells() -> None:
    viewer = _build_viewer(("ops",))

    spells = viewer.execute_method(
        "list_spells_by_payload_type",
        frame_name="ops",
        payload_type="general",
    )

    assert len(spells) == 1
    assert spells[0].source_id == "ops-spellbook:ops-spell"


def test_frame_viewer_explain_spell_access_reports_detail_reason() -> None:
    viewer = _build_viewer(("ops",))

    explanation = viewer.execute_method(
        "explain_spell_access",
        frame_name="ops",
        spell_source_id="ops-spellbook:ops-spell",
    )

    assert explanation == {
        "source_kind": "spell",
        "source_id": "ops-spellbook:ops-spell",
        "target_exists": True,
        "visible": True,
        "reason": "visible",
        "visible_sections": (
            "binding_payload",
            "resolution_payload",
            "metadata",
        ),
        "payload_type": "general",
        "detail_available": False,
        "detail_reason": "payload_not_detailed",
        "binding_payload_visible": True,
        "resolution_payload_visible": True,
        "metadata_visible": True,
        "rich_sections_visible": tuple(),
    }


def test_frame_viewer_get_spell_payload_section_returns_visible_section() -> None:
    viewer = _build_viewer(("ops",))

    binding_payload = viewer.execute_method(
        "get_spell_payload_section",
        frame_name="ops",
        spell_source_id="ops-spellbook:ops-spell",
        section_name="binding_payload",
    )

    assert binding_payload == {"kind": "class"}


def test_frame_viewer_describe_spell_detail_reports_acl_restricted_for_detailed_payload() -> None:
    configuration = FrameACLConfiguration.create_default("ops")
    surface = _build_surface(
        "ops",
        configuration,
        spell_sections_by_key={
            ("ops-spellbook", "ops-spell"): ("binding_payload", "metadata"),
        },
    )
    viewer = FrameViewer(
        frame_descriptors_by_name={"ops": _build_detailed_descriptor("ops")},
        frame_acl_configurations_by_frame_name={"ops": configuration},
        compiled_access_surfaces_by_frame_name={"ops": surface},
        default_view_frame_name="ops",
    )

    detail = viewer.execute_method(
        "describe_spell_detail",
        frame_name="ops",
        spell_source_id="ops-spellbook:ops-spell",
    )

    assert detail == {
        "spell_source_id": "ops-spellbook:ops-spell",
        "payload_type": "detailed",
        "detail_available": False,
        "reason": "acl_restricted",
        "visible_sections": ("binding_payload", "metadata"),
        "payload": {},
    }


def test_frame_viewer_describe_spell_detail_returns_rich_sections_for_detailed_payload() -> None:
    configuration = FrameACLConfiguration.create_default("ops")
    surface = _build_surface(
        "ops",
        configuration,
        spell_sections_by_key={
            ("ops-spellbook", "ops-spell"): (
                "binding_payload",
                "class_profile",
                "callable_profile",
                "instance_members",
                "dynamic_access",
            ),
        },
    )
    viewer = FrameViewer(
        frame_descriptors_by_name={"ops": _build_detailed_descriptor("ops")},
        frame_acl_configurations_by_frame_name={"ops": configuration},
        compiled_access_surfaces_by_frame_name={"ops": surface},
        default_view_frame_name="ops",
    )

    detail = viewer.execute_method(
        "describe_spell_detail",
        frame_name="ops",
        spell_source_id="ops-spellbook:ops-spell",
    )

    assert detail == {
        "spell_source_id": "ops-spellbook:ops-spell",
        "payload_type": "detailed",
        "detail_available": True,
        "reason": "available",
        "visible_sections": (
            "binding_payload",
            "class_profile",
            "callable_profile",
            "instance_members",
            "dynamic_access",
        ),
        "payload": {
            "class_profile": {"methods": ["run"]},
            "callable_profile": {"signature": "() -> None"},
            "instance_members": {"state": {"type": "str"}},
            "dynamic_access": {"has_getattr": False},
        },
    }


def test_frame_viewer_descriptor_host_methods_report_record_level_inventory() -> None:
    viewer = _build_viewer(("ops", "finance"))

    assert viewer.list_frame_ids() == ["finance-frame", "ops-frame"]
    assert viewer.list_nexus_contracts() == [
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
    ]
    assert viewer.count_conduit_records() == 2
    assert viewer.list_conduit_record_ids() == ["finance-conduit", "ops-conduit"]
    assert viewer.list_root_conduit_ids() == ["finance-conduit", "ops-conduit"]
    assert viewer.count_spellbooks() == 2
    assert viewer.list_origin_spellbook_ids() == ["finance-spellbook", "ops-spellbook"]
    assert viewer.list_spell_record_ids() == ["finance-spell", "ops-spell"]
    assert viewer.list_spell_record_keys() == [
        ("finance-spellbook", "finance-spell"),
        ("ops-spellbook", "ops-spell"),
    ]
    assert viewer.list_spell_names() == ["FinanceSpell", "OpsSpell"]
    assert viewer.list_binding_names() == ["finance_spell", "ops_spell"]
    assert viewer.list_lineage_ids() == ["finance-lineage", "ops-lineage"]
    assert viewer.list_spellframes() == []
    assert viewer.list_permissions() == ["create"]
    assert viewer.list_existence_kinds() == ["unique"]


def test_frame_viewer_descriptor_host_descriptions_report_topology_and_records() -> None:
    viewer = _build_viewer(("ops",))

    inventory = viewer.describe_descriptor_inventory(frame_name="ops")
    topology = viewer.describe_descriptor_topology("ops")
    conduit_records = viewer.describe_conduit_records("ops")
    spell_records = viewer.describe_spell_records("ops")
    spell_record = viewer.describe_spell_record("ops-spellbook:ops-spell")
    owned_spells = viewer.list_spells_by_owner_conduit("ops-conduit")
    spellbook_spells = viewer.list_spells_by_spellbook_id("ops-spellbook")
    permission_spells = viewer.list_spells_by_permission("create")
    existence_spells = viewer.list_spells_by_existence("unique")

    assert inventory == {
        "frame_count": 1,
        "frame_names": ("ops",),
        "frame_ids": ("ops-frame",),
        "conduit_record_count": 1,
        "root_conduit_ids": ("ops-conduit",),
        "spell_record_count": 1,
        "origin_spellbook_count": 1,
        "origin_spellbook_ids": ("ops-spellbook",),
        "permissions": ("create",),
        "existence_kinds": ("unique",),
    }
    assert topology == {
        "frame_name": "ops",
        "frame_id": "ops-frame",
        "root_conduit_ids": ("ops-conduit",),
        "conduit_ids_by_root_id": {"ops-conduit": ("ops-conduit",)},
        "spell_source_ids_by_conduit_id": {
            "ops-conduit": ("ops-spellbook:ops-spell",),
        },
        "spell_record_keys_by_spellbook_id": {
            "ops-spellbook": (("ops-spellbook", "ops-spell"),),
        },
    }
    assert conduit_records == [
        {
            "frame_name": "ops",
            "conduit_id": "ops-conduit",
            "root_conduit_id": "ops-conduit",
            "origin_spellbook_id": "ops-spellbook",
            "nexus_label": "default",
            "nexus_version": "0.0.1",
            "is_root_conduit": True,
            "owned_spell_record_count": 1,
        }
    ]
    assert spell_records == [spell_record]
    assert spell_record == {
        "frame_name": "ops",
        "source_id": "ops-spellbook:ops-spell",
        "record_key": ("ops-spellbook", "ops-spell"),
        "spell_id": "ops-spell",
        "lineage_id": "ops-lineage",
        "origin_spellbook_id": "ops-spellbook",
        "owner_conduit_id": "ops-conduit",
        "spell_name": "OpsSpell",
        "binding_name": "ops_spell",
        "spellframe": None,
        "permissions": "create",
        "existence": "unique",
        "payload_type": "general",
        "payload_version": "0.0.1",
        "nexus_label": "default",
        "nexus_version": "0.0.1",
    }
    assert owned_spells == ["ops-spellbook:ops-spell"]
    assert spellbook_spells == ["ops-spellbook:ops-spell"]
    assert permission_spells == ["ops-spellbook:ops-spell"]
    assert existence_spells == ["ops-spellbook:ops-spell"]


def test_frame_viewer_brief_and_compare_methods_report_expected_shapes() -> None:
    viewer = _build_viewer(("ops", "finance"))

    viewer_summary = viewer.describe_viewer()
    current_frame = viewer.describe_current_frame()
    frames_inventory = viewer.describe_frames_inventory()
    method_surface = viewer.describe_viewer_method_surface()

    assert viewer_summary == {
        "viewer_id": viewer.viewer_id,
        "frame_count": 2,
        "default_view_frame_name": "ops",
        "default_profile_name": "general",
        "default_profile_version": "0.0.1",
        "frame_names": ("finance", "ops"),
        "host_boundary": "descriptor_only",
    }
    assert current_frame == {
        "frame_name": "ops",
        "frame_id": "ops-frame",
        "nexus_label": "default",
        "nexus_version": "0.0.1",
        "conduit_record_count": 1,
        "root_conduit_count": 1,
        "spell_record_count": 1,
        "is_default": True,
    }
    assert frames_inventory == {
        "finance": {
            "frame_id": "finance-frame",
            "nexus_contract": "default:0.0.1",
            "conduit_record_count": 1,
            "root_conduit_count": 1,
            "spell_record_count": 1,
            "origin_spellbook_count": 1,
            "lineage_count": 1,
            "is_default": False,
        },
        "ops": {
            "frame_id": "ops-frame",
            "nexus_contract": "default:0.0.1",
            "conduit_record_count": 1,
            "root_conduit_count": 1,
            "spell_record_count": 1,
            "origin_spellbook_count": 1,
            "lineage_count": 1,
            "is_default": True,
        },
    }
    assert method_surface == {
        "host_boundary": "descriptor_only",
        "default_entrypoints": (
            "describe_viewer",
            "describe_host_inventory",
            "describe_current_frame",
            "describe_frames_inventory",
        ),
        "frame_summary_methods": (
            "list_frame_names",
            "describe_frame",
            "describe_frames",
            "describe_frame_brief",
            "describe_current_frame",
        ),
        "comparison_methods": (
            "compare_frames",
            "compare_frames_brief",
            "compare_frame_conduits",
            "compare_frame_spells",
        ),
        "record_methods": (
            "describe_conduit_records",
            "describe_spell_records",
            "describe_spell_record",
        ),
        "frame_local_method_entrypoint": "execute_method",
    }
    assert viewer.describe_frame_brief("ops") == {
        "frame_name": "ops",
        "frame_id": "ops-frame",
        "nexus_contract": "default:0.0.1",
        "conduit_record_count": 1,
        "root_conduit_count": 1,
        "spell_record_count": 1,
        "is_default": True,
    }
    assert viewer.describe_host_inventory() == {
        "frame_count": 2,
        "default_view_frame_name": "ops",
        "frame_names": ("finance", "ops"),
        "frame_ids": ("finance-frame", "ops-frame"),
        "conduit_record_count": 2,
        "root_conduit_count": 2,
        "spell_record_count": 2,
        "origin_spellbook_count": 2,
        "origin_spellbook_ids": ("finance-spellbook", "ops-spellbook"),
        "permissions": ("create",),
        "existence_kinds": ("unique",),
    }
    assert viewer.compare_frame_conduits("ops", "finance") == {
        "record_counts": {"left": 1, "right": 1},
        "conduit_ids": {
            "shared": tuple(),
            "left_only": ("ops-conduit",),
            "right_only": ("finance-conduit",),
        },
        "root_conduit_ids": {
            "shared": tuple(),
            "left_only": ("ops-conduit",),
            "right_only": ("finance-conduit",),
        },
    }
    assert viewer.compare_frame_spells("ops", "finance") == {
        "record_counts": {"left": 1, "right": 1},
        "spell_source_ids": {
            "shared": tuple(),
            "left_only": ("ops-spellbook:ops-spell",),
            "right_only": ("finance-spellbook:finance-spell",),
        },
        "lineage_ids": {
            "shared": tuple(),
            "left_only": ("ops-lineage",),
            "right_only": ("finance-lineage",),
        },
        "spell_names": {
            "shared": tuple(),
            "left_only": ("OpsSpell",),
            "right_only": ("FinanceSpell",),
        },
        "binding_names": {
            "shared": tuple(),
            "left_only": ("ops_spell",),
            "right_only": ("finance_spell",),
        },
    }
    comparison = viewer.compare_frames("ops", "finance")
    assert comparison["left_frame_name"] == "ops"
    assert comparison["right_frame_name"] == "finance"
    assert comparison["same_frame_id"] is False
    assert comparison["same_nexus_contract"] is True
    assert viewer.compare_frames_brief("ops", "finance") == {
        "left_frame_name": "ops",
        "right_frame_name": "finance",
        "same_frame_id": False,
        "same_nexus_contract": True,
        "left_only_conduit_count": 1,
        "right_only_conduit_count": 1,
        "left_only_spell_count": 1,
        "right_only_spell_count": 1,
        "shared_permission_count": 1,
        "shared_existence_kind_count": 1,
    }


def test_view_frame_visible_surface_methods_report_inventory_and_topology() -> None:
    viewer = _build_viewer(("ops",))
    view_frame = viewer.get_selected_profile_for_frame("ops").view_frame

    assert view_frame.list_visible_target_ids() == [
        "ops:frame:ops-frame",
        "ops:conduit:ops-conduit",
        "ops:spell:ops-spellbook:ops-spell",
    ]
    assert view_frame.list_visible_target_ids_by_kind() == {
        "conduit": ("ops:conduit:ops-conduit",),
        "frame": ("ops:frame:ops-frame",),
        "spell": ("ops:spell:ops-spellbook:ops-spell",),
    }
    assert view_frame.list_visible_conduit_ids() == ["ops-conduit"]
    assert view_frame.list_visible_spell_source_ids() == ["ops-spellbook:ops-spell"]
    assert [link.source_id for link in view_frame.list_visible_root_conduits()] == [
        "ops-conduit"
    ]
    assert view_frame.list_visible_binding_names() == ["ops_spell"]
    assert view_frame.list_visible_spell_names() == ["OpsSpell"]
    assert view_frame.list_visible_spellframes() == []
    assert view_frame.list_visible_lineage_ids() == ["ops-lineage"]
    assert view_frame.describe_visible_spell_ownership() == {
        "ops-conduit": ("ops-spellbook:ops-spell",)
    }
    assert view_frame.describe_visible_conduit_tree() == {
        "ops-conduit": ("ops-conduit",)
    }
    assert view_frame.describe_visible_inventory_by_kind() == {
        "conduit": {
            "count": 1,
            "target_ids": ("ops:conduit:ops-conduit",),
            "source_ids": ("ops-conduit",),
            "display_names": ("root",),
        },
        "frame": {
            "count": 1,
            "target_ids": ("ops:frame:ops-frame",),
            "source_ids": ("ops-frame",),
            "display_names": ("ops",),
        },
        "spell": {
            "count": 1,
            "target_ids": ("ops:spell:ops-spellbook:ops-spell",),
            "source_ids": ("ops-spellbook:ops-spell",),
            "display_names": ("ops_spell",),
        },
    }
    assert view_frame.describe_frame_topology() == {
        "frame_name": "ops",
        "root_conduit_ids": ("ops-conduit",),
        "conduit_ids_by_root_id": {"ops-conduit": ("ops-conduit",)},
        "spell_source_ids_by_conduit_id": {
            "ops-conduit": ("ops-spellbook:ops-spell",)
        },
        "visible_spell_source_ids": ("ops-spellbook:ops-spell",),
    }
    assert view_frame.describe_visible_surface()["frame_name"] == "ops"


def test_view_frame_brief_and_missing_surface_methods_work() -> None:
    viewer = _build_viewer(("ops",))
    view_frame = viewer.get_selected_profile_for_frame("ops").view_frame

    assert view_frame.describe_frame_brief() == {
        "frame_name": "ops",
        "visible_target_count": 3,
        "visible_conduit_count": 1,
        "visible_spell_count": 1,
        "allowed_kinds": ("frame", "conduit", "spell"),
        "frame_payload_field_count": 2,
    }
    assert view_frame.describe_target_brief(
        source_kind="spell",
        source_id="ops-spellbook:ops-spell",
    ) == {
        "target_id": "ops:spell:ops-spellbook:ops-spell",
        "source_kind": "spell",
        "source_id": "ops-spellbook:ops-spell",
        "display_name": "ops_spell",
        "visible": True,
        "reason": "visible",
        "visible_payload_keys": (
            "binding_payload",
            "resolution_payload",
            "metadata",
        ),
    }
    assert view_frame.describe_missing_surface() == {
        "frame_name": "ops",
        "hidden_frame_payload_fields": (
            "ai_native_enabled",
            "root_conduit_count",
            "root_conduit_ids",
            "named_root_conduits",
            "conduit_cloud_entry_count",
            "conduit_cloud_names",
            "cluster_count",
            "cluster_names",
        ),
        "hidden_conduit_ids": tuple(),
        "hidden_spell_source_ids": tuple(),
        "hidden_conduit_sections_by_id": {
            "ops-conduit": (
                "policy",
                "peer_conduit_ids",
                "parent_conduit_id",
                "lineage_depth",
            ),
        },
        "hidden_spell_sections_by_source_id": {
            "ops-spellbook:ops-spell": (
                "class_profile",
                "callable_profile",
                "instance_members",
                "dynamic_access",
            ),
        },
    }


def test_view_frame_search_and_identity_helpers_work() -> None:
    viewer = _build_viewer(("ops",))
    view_frame = viewer.get_selected_profile_for_frame("ops").view_frame

    contains_hits = view_frame.search_targets_contains("spell")
    prefix_hits = view_frame.search_targets_prefix("ops")
    grouped_targets = view_frame.group_targets_by_kind()
    spell_identity = view_frame.describe_target_identity(
        source_kind="spell",
        source_id="ops-spellbook:ops-spell",
    )

    assert [hit.source_id for hit in contains_hits] == ["ops-spellbook:ops-spell"]
    assert [hit.source_kind for hit in prefix_hits] == ["frame", "conduit", "spell"]
    assert tuple(grouped_targets.keys()) == ("conduit", "frame", "spell")
    assert spell_identity == {
        "frame_name": "ops",
        "target_id": "ops:spell:ops-spellbook:ops-spell",
        "source_kind": "spell",
        "source_id": "ops-spellbook:ops-spell",
        "display_name": "ops_spell",
        "spell_id": "ops-spell",
        "lineage_id": "ops-lineage",
        "owner_conduit_id": "ops-conduit",
        "origin_spellbook_id": "ops-spellbook",
        "spell_name": "OpsSpell",
        "binding_name": "ops_spell",
        "spellframe": None,
        "permissions": "create",
        "existence": "unique",
        "payload_type": "general",
        "payload_version": "0.0.1",
        "nexus_label": "default",
        "nexus_version": "0.0.1",
    }


def test_view_conduit_extended_methods_report_inventory_and_relationships() -> None:
    viewer = _build_viewer(("ops",))
    view_conduit = viewer.get_selected_profile_for_frame("ops").view_conduit

    assert [link.source_id for link in view_conduit.list_root_conduits()] == [
        "ops-conduit"
    ]
    assert view_conduit.is_root_conduit("ops-conduit") is True
    assert view_conduit.get_root_conduit_id("ops-conduit") == "ops-conduit"
    assert [link.source_id for link in view_conduit.list_conduits_by_root_id("ops-conduit")] == [
        "ops-conduit"
    ]
    assert [link.source_id for link in view_conduit.list_conduits_by_policy("default")] == [
        "ops-conduit"
    ]
    assert [link.source_id for link in view_conduit.list_conduits_by_state("normal")] == [
        "ops-conduit"
    ]
    assert view_conduit.list_peer_conduits("ops-conduit") == []
    assert view_conduit.list_peer_conduit_ids("ops-conduit") == tuple()
    assert view_conduit.list_spell_source_ids_for_conduit("ops-conduit") == (
        "ops-spellbook:ops-spell",
    )
    assert view_conduit.list_binding_names_for_conduit("ops-conduit") == ("ops_spell",)
    assert view_conduit.list_spell_names_for_conduit("ops-conduit") == ("OpsSpell",)
    assert view_conduit.describe_conduit_inventory("ops-conduit") == {
        "conduit_id": "ops-conduit",
        "is_root_conduit": True,
        "root_conduit_id": "ops-conduit",
        "visible_sections": ("conduit_name", "conduit_state"),
        "peer_conduit_ids": tuple(),
        "peer_count": 0,
        "spell_count": 1,
        "spell_source_ids": ("ops-spellbook:ops-spell",),
    }
    assert view_conduit.describe_conduit_relationships("ops-conduit") == {
        "conduit_id": "ops-conduit",
        "is_root_conduit": True,
        "root_conduit_id": "ops-conduit",
        "peer_conduit_ids": tuple(),
        "peer_conduits": tuple(),
        "spell_source_ids": ("ops-spellbook:ops-spell",),
    }
    assert view_conduit.describe_conduit_access_summary("ops-conduit")["access"][
        "visible"
    ] is True


def test_view_conduit_brief_and_missing_section_methods_work() -> None:
    viewer = _build_viewer(("ops",))
    view_conduit = viewer.get_selected_profile_for_frame("ops").view_conduit

    assert view_conduit.describe_conduit_brief("ops-conduit") == {
        "conduit_id": "ops-conduit",
        "display_name": "root",
        "is_root_conduit": True,
        "visible_section_count": 2,
        "visible_spell_count": 1,
    }
    assert view_conduit.describe_conduit_missing_sections("ops-conduit") == {
        "conduit_id": "ops-conduit",
        "visible_sections": ("conduit_name", "conduit_state"),
        "hidden_sections": (
            "policy",
            "peer_conduit_ids",
            "parent_conduit_id",
            "lineage_depth",
        ),
    }


def test_view_spell_extended_identity_origin_and_filter_methods_work() -> None:
    viewer = _build_viewer(("ops",))
    view_spell = viewer.get_selected_profile_for_frame("ops").view_spell

    assert view_spell.describe_spell_identity("ops-spellbook:ops-spell") == {
        "source_id": "ops-spellbook:ops-spell",
        "record_key": ("ops-spellbook", "ops-spell"),
        "spell_id": "ops-spell",
        "lineage_id": "ops-lineage",
        "spell_name": "OpsSpell",
        "binding_name": "ops_spell",
        "spellframe": None,
        "permissions": "create",
        "existence": "unique",
        "payload_type": "general",
        "payload_version": "0.0.1",
    }
    assert view_spell.describe_spell_origin("ops-spellbook:ops-spell") == {
        "frame_name": "ops",
        "origin_spellbook_id": "ops-spellbook",
        "owner_conduit_id": "ops-conduit",
        "nexus_label": "default",
        "nexus_version": "0.0.1",
        "source_profile_name": None,
        "source_profile_version": None,
    }
    assert view_spell.describe_spell_lineage("ops-spellbook:ops-spell") == {
        "source_id": "ops-spellbook:ops-spell",
        "lineage_id": "ops-lineage",
        "related_source_ids": ("ops-spellbook:ops-spell",),
        "visible_related_source_ids": ("ops-spellbook:ops-spell",),
    }
    assert view_spell.describe_spell_binding("ops-spellbook:ops-spell") == {
        "source_id": "ops-spellbook:ops-spell",
        "spell_name": "OpsSpell",
        "binding_name": "ops_spell",
        "spellframe": None,
        "binding_payload_visible": True,
        "binding_payload": {"kind": "class"},
    }
    assert view_spell.describe_spell_resolution("ops-spellbook:ops-spell") == {
        "source_id": "ops-spellbook:ops-spell",
        "resolution_payload_visible": True,
        "resolution_payload": {"requirements": []},
        "requirement_count": 0,
    }
    assert view_spell.describe_spell_metadata("ops-spellbook:ops-spell") == {
        "source_id": "ops-spellbook:ops-spell",
        "metadata_visible": True,
        "metadata": {"frame": "ops"},
    }
    assert [link.source_id for link in view_spell.list_spells_by_owner_conduit("ops-conduit")] == [
        "ops-spellbook:ops-spell"
    ]
    assert [link.source_id for link in view_spell.list_spells_by_spellbook_id("ops-spellbook")] == [
        "ops-spellbook:ops-spell"
    ]
    assert [link.source_id for link in view_spell.list_spells_by_lineage_id("ops-lineage")] == [
        "ops-spellbook:ops-spell"
    ]
    assert [link.source_id for link in view_spell.list_spells_by_permission("create")] == [
        "ops-spellbook:ops-spell"
    ]
    assert [link.source_id for link in view_spell.list_spells_by_existence("unique")] == [
        "ops-spellbook:ops-spell"
    ]
    assert [link.source_id for link in view_spell.list_spells_by_spell_name("OpsSpell")] == [
        "ops-spellbook:ops-spell"
    ]
    assert view_spell.list_spells_by_spellframe("LogicFrame") == []
    assert [link.source_id for link in view_spell.search_spells_contains("spell")] == [
        "ops-spellbook:ops-spell"
    ]
    assert [link.source_id for link in view_spell.search_spells_prefix("ops")] == [
        "ops-spellbook:ops-spell"
    ]
    assert view_spell.describe_spell_access_summary("ops-spellbook:ops-spell")[
        "access"
    ]["detail_reason"] == "payload_not_detailed"


def test_view_spell_brief_and_missing_section_methods_work() -> None:
    viewer = _build_viewer(("ops",))
    view_spell = viewer.get_selected_profile_for_frame("ops").view_spell

    assert view_spell.describe_spell_brief("ops-spellbook:ops-spell") == {
        "source_id": "ops-spellbook:ops-spell",
        "display_name": "ops_spell",
        "payload_type": "general",
        "visible_section_count": 3,
        "detail_reason": "payload_not_detailed",
    }
    assert view_spell.describe_spell_missing_sections("ops-spellbook:ops-spell") == {
        "source_id": "ops-spellbook:ops-spell",
        "visible_sections": (
            "binding_payload",
            "resolution_payload",
            "metadata",
        ),
        "published_sections": (
            "binding_payload",
            "metadata",
            "resolution_payload",
        ),
        "hidden_sections": (
            "class_profile",
            "callable_profile",
            "instance_members",
            "dynamic_access",
        ),
        "not_published_sections": tuple(),
    }


def test_execute_method_routes_new_brief_and_compare_methods() -> None:
    viewer = _build_viewer(("ops", "finance"))

    viewer_summary = viewer.execute_method("describe_viewer")
    current_frame = viewer.execute_method("describe_current_frame")
    frames_inventory = viewer.execute_method("describe_frames_inventory")
    frame_brief = viewer.execute_method("describe_frame_brief", frame_name="ops")
    host_inventory = viewer.execute_method("describe_host_inventory")
    frame_compare = viewer.execute_method(
        "compare_frames",
        left_frame_name="ops",
        right_frame_name="finance",
    )
    frame_compare_brief = viewer.execute_method(
        "compare_frames_brief",
        left_frame_name="ops",
        right_frame_name="finance",
    )
    method_surface = viewer.execute_method("describe_viewer_method_surface")
    frame_view_brief = viewer.execute_method(
        "describe_frame_brief_local",
        frame_name="ops",
    )
    missing_surface = viewer.execute_method(
        "describe_missing_surface",
        frame_name="ops",
    )
    conduit_brief = viewer.execute_method(
        "describe_conduit_brief",
        frame_name="ops",
        conduit_id="ops-conduit",
    )
    conduit_missing = viewer.execute_method(
        "describe_conduit_missing_sections",
        frame_name="ops",
        conduit_id="ops-conduit",
    )
    spell_brief = viewer.execute_method(
        "describe_spell_brief",
        frame_name="ops",
        spell_source_id="ops-spellbook:ops-spell",
    )
    spell_missing = viewer.execute_method(
        "describe_spell_missing_sections",
        frame_name="ops",
        spell_source_id="ops-spellbook:ops-spell",
    )

    assert viewer_summary["frame_count"] == 2
    assert current_frame["frame_name"] == "ops"
    assert frames_inventory["ops"]["spell_record_count"] == 1
    assert frame_brief["frame_name"] == "ops"
    assert host_inventory["frame_count"] == 2
    assert frame_compare["left_frame_name"] == "ops"
    assert frame_compare_brief["left_only_spell_count"] == 1
    assert method_surface["frame_local_method_entrypoint"] == "execute_method"
    assert frame_view_brief["visible_target_count"] == 3
    assert "hidden_frame_payload_fields" in missing_surface
    assert conduit_brief["conduit_id"] == "ops-conduit"
    assert conduit_missing["hidden_sections"] == (
        "policy",
        "peer_conduit_ids",
        "parent_conduit_id",
        "lineage_depth",
    )
    assert spell_brief["source_id"] == "ops-spellbook:ops-spell"
    assert spell_missing["hidden_sections"] == (
        "class_profile",
        "callable_profile",
        "instance_members",
        "dynamic_access",
    )


def test_frame_viewer_host_collision_methods_report_expected_groups() -> None:
    viewer = _build_collision_viewer()

    assert viewer.describe_binding_name_collisions() == {
        "shared_binding": (
            "shared-book:finance-spell-1",
            "shared-book:ops-spell-1",
        )
    }
    assert viewer.describe_spell_name_collisions() == {
        "SharedSpell": (
            "shared-book:finance-spell-1",
            "shared-book:ops-spell-1",
        )
    }
    assert viewer.describe_lineage_groups()["shared-lineage"] == (
        "shared-book:finance-spell-1",
        "shared-book:ops-spell-1",
    )
    assert viewer.describe_spellframe_groups()["LogicFrame"] == (
        "shared-book:finance-spell-1",
        "shared-book:ops-spell-1",
    )
    assert viewer.describe_spellbook_permission_mismatches() == {
        "shared-book": {
            "source_ids": (
                "shared-book:finance-spell-1",
                "shared-book:finance-spell-2",
                "shared-book:ops-spell-1",
            ),
            "values": ("block", "create"),
        }
    }
    assert viewer.describe_spellbook_existence_mismatches() == {
        "shared-book": {
            "source_ids": (
                "shared-book:finance-spell-1",
                "shared-book:finance-spell-2",
                "shared-book:ops-spell-1",
            ),
            "values": ("unique", "unique_per_conduit"),
        }
    }


def test_frame_viewer_host_record_compare_methods_work() -> None:
    viewer = _build_collision_viewer()

    spell_comparison = viewer.compare_spell_records(
        "shared-book:ops-spell-1",
        "shared-book:finance-spell-1",
    )
    conduit_comparison = viewer.compare_conduit_records(
        "ops-conduit-1",
        "finance-conduit-1",
        left_frame_name="ops",
        right_frame_name="finance",
    )

    assert spell_comparison == {
        "left_source_id": "shared-book:ops-spell-1",
        "right_source_id": "shared-book:finance-spell-1",
        "same_frame": False,
        "same_origin_spellbook": True,
        "same_owner_conduit": False,
        "same_lineage_id": True,
        "same_spell_name": True,
        "same_binding_name": True,
        "same_spellframe": True,
        "same_permissions": False,
        "same_existence": False,
        "same_payload_type": True,
        "same_nexus_contract": True,
    }
    assert conduit_comparison["same_frame"] is False
    assert conduit_comparison["same_policy"] is True
    assert conduit_comparison["same_conduit_state"] is True


def test_view_frame_visible_collision_method_reports_expected_groups() -> None:
    viewer = _build_visible_collision_viewer()
    view_frame = viewer.get_selected_profile_for_frame("ops").view_frame

    assert view_frame.describe_visible_collisions() == {
        "binding_name_collisions": {
            "shared_binding": (
                "ops-spellbook:ops-spell-1",
                "ops-spellbook:ops-spell-2",
            )
        },
        "spell_name_collisions": {
            "SharedSpell": (
                "ops-spellbook:ops-spell-1",
                "ops-spellbook:ops-spell-2",
            )
        },
        "lineage_groups": {
            "shared-lineage": (
                "ops-spellbook:ops-spell-1",
                "ops-spellbook:ops-spell-2",
            )
        },
        "spellframe_groups": {
            "SharedFrame": (
                "ops-spellbook:ops-spell-1",
                "ops-spellbook:ops-spell-2",
            )
        },
    }


def test_view_conduit_crosswalk_and_compare_methods_work() -> None:
    viewer = _build_visible_collision_viewer()
    view_conduit = viewer.get_selected_profile_for_frame("ops").view_conduit

    crosswalk = view_conduit.describe_conduit_crosswalk("ops-conduit-1")
    comparison = view_conduit.compare_conduits(
        "ops-conduit-1",
        "ops-conduit-2",
    )

    assert crosswalk == {
        "frame_name": "ops",
        "conduit_id": "ops-conduit-1",
        "root_conduit_id": "ops-conduit-1",
        "peer_conduit_ids": ("ops-conduit-2",),
        "peer_conduits": ("ops-conduit-2",),
        "spell_source_ids": ("ops-spellbook:ops-spell-1",),
        "binding_names": ("shared_binding",),
        "spell_names": ("SharedSpell",),
    }
    assert comparison["same_root_conduit_id"] is False
    assert comparison["same_policy"] is True
    assert comparison["peer_conduit_ids"]["shared"] == tuple()


def test_view_spell_crosswalk_and_compare_methods_work() -> None:
    viewer = _build_visible_collision_viewer()
    view_spell = viewer.get_selected_profile_for_frame("ops").view_spell

    crosswalk = view_spell.describe_spell_crosswalk("ops-spellbook:ops-spell-1")
    comparison = view_spell.compare_spells(
        "ops-spellbook:ops-spell-1",
        "ops-spellbook:ops-spell-2",
    )

    assert crosswalk == {
        "frame_name": "ops",
        "source_id": "ops-spellbook:ops-spell-1",
        "origin_spellbook_id": "ops-spellbook",
        "owner_conduit_id": "ops-conduit-1",
        "root_conduit_id": "ops-conduit-1",
        "peer_conduit_ids": ("ops-conduit-2",),
        "lineage_id": "shared-lineage",
        "related_visible_source_ids": (
            "ops-spellbook:ops-spell-1",
            "ops-spellbook:ops-spell-2",
        ),
        "permissions": "create",
        "existence": "unique",
        "payload_type": "general",
    }
    assert comparison == {
        "left_source_id": "ops-spellbook:ops-spell-1",
        "right_source_id": "ops-spellbook:ops-spell-2",
        "same_owner_conduit": False,
        "same_origin_spellbook": True,
        "same_lineage_id": True,
        "same_spell_name": True,
        "same_binding_name": True,
        "same_spellframe": True,
        "same_permissions": True,
        "same_existence": True,
        "same_payload_type": False,
        "visible_sections": {
            "shared": (
                "binding_payload",
                "metadata",
                "resolution_payload",
            ),
            "left_only": tuple(),
            "right_only": (
                "callable_profile",
                "class_profile",
                "dynamic_access",
                "instance_members",
            ),
        },
    }


def test_execute_method_routes_crosswalk_and_collision_methods() -> None:
    viewer = _build_visible_collision_viewer()

    visible_collisions = viewer.execute_method(
        "describe_visible_collisions",
        frame_name="ops",
    )
    conduit_crosswalk = viewer.execute_method(
        "describe_conduit_crosswalk",
        frame_name="ops",
        conduit_id="ops-conduit-1",
    )
    spell_crosswalk = viewer.execute_method(
        "describe_spell_crosswalk",
        frame_name="ops",
        spell_source_id="ops-spellbook:ops-spell-1",
    )
    spell_compare = viewer.execute_method(
        "compare_spells",
        frame_name="ops",
        left_spell_source_id="ops-spellbook:ops-spell-1",
        right_spell_source_id="ops-spellbook:ops-spell-2",
    )

    assert "binding_name_collisions" in visible_collisions
    assert conduit_crosswalk["conduit_id"] == "ops-conduit-1"
    assert spell_crosswalk["source_id"] == "ops-spellbook:ops-spell-1"
    assert spell_compare["same_lineage_id"] is True


def test_frame_viewer_ast_surface_methods_return_minified_json() -> None:
    viewer = _build_viewer(("ops",))

    method_names_json = viewer.list_viewer_method_names_ast_json()
    class_surface_json = viewer.describe_viewer_class_surface_ast_json()
    profile_method_names_json = viewer.list_selected_profile_method_names_ast_json(
        frame_name="ops"
    )
    profile_surface_json = viewer.describe_selected_profile_class_surface_ast_json(
        frame_name="ops"
    )
    helper_surfaces_json = viewer.describe_selected_profile_helper_class_surfaces_ast_json(
        frame_name="ops"
    )
    selected_surface_json = viewer.describe_selected_ast_surface_json(
        frame_name="ops"
    )

    assert "\n" not in method_names_json
    assert "\n" not in class_surface_json
    assert "\n" not in profile_method_names_json
    assert "\n" not in profile_surface_json
    assert "\n" not in helper_surfaces_json
    assert "\n" not in selected_surface_json

    method_names = json.loads(method_names_json)
    class_surface = json.loads(class_surface_json)
    profile_method_names = json.loads(profile_method_names_json)
    profile_surface = json.loads(profile_surface_json)
    helper_surfaces = json.loads(helper_surfaces_json)
    selected_surface = json.loads(selected_surface_json)

    assert method_names["class_name"] == "FrameViewer"
    assert "describe_frame" in method_names["method_names"]
    assert "__init__" not in method_names["method_names"]
    assert "_get_required_frame_descriptor" not in method_names["method_names"]

    assert class_surface["class_name"] == "FrameViewer"
    assert any(
        current_method["method_name"] == "describe_frame"
        for current_method in class_surface["methods"]
    )
    assert any(
        current_property["method_name"] == "profile"
        for current_property in class_surface["properties"]
    )

    assert profile_method_names["class_name"] == "GeneralFrameViewerProfile"
    assert "bind_to_frame" in profile_method_names["method_names"]
    assert "view_frame" not in profile_method_names["method_names"]

    assert profile_surface["class_name"] == "GeneralFrameViewerProfile"
    assert any(
        current_property["method_name"] == "view_frame"
        for current_property in profile_surface["properties"]
    )
    assert any(
        current_property["method_name"] == "view_conduit"
        for current_property in profile_surface["properties"]
    )
    assert any(
        current_property["method_name"] == "view_spell"
        for current_property in profile_surface["properties"]
    )

    assert set(helper_surfaces.keys()) == {"view_frame", "view_conduit", "view_spell"}
    assert helper_surfaces["view_frame"]["class_name"] == "GeneralViewFrame"
    assert any(
        current_method["method_name"] == "describe_frame"
        for current_method in helper_surfaces["view_frame"]["methods"]
    )
    assert helper_surfaces["view_conduit"]["class_name"] == "GeneralViewConduit"
    assert any(
        current_method["method_name"] == "describe_conduit"
        for current_method in helper_surfaces["view_conduit"]["methods"]
    )
    assert helper_surfaces["view_spell"]["class_name"] == "GeneralViewSpell"
    assert any(
        current_method["method_name"] == "describe_spell"
        for current_method in helper_surfaces["view_spell"]["methods"]
    )

    assert selected_surface["frame_name"] == "ops"
    assert selected_surface["profile_name"] == "general"
    assert selected_surface["helper_names"] == ["view_conduit", "view_frame", "view_spell"]
    assert selected_surface["viewer"]["class_name"] == "FrameViewer"
    assert selected_surface["profile"]["class_name"] == "GeneralFrameViewerProfile"
    assert set(selected_surface["helpers"].keys()) == {"view_frame", "view_conduit", "view_spell"}


def test_frame_viewer_ast_surface_methods_can_include_dunders() -> None:
    viewer = _build_viewer(("ops",))

    method_names = json.loads(
        viewer.list_viewer_method_names_ast_json(include_dunder=True)
    )

    assert "__init__" in method_names["method_names"]


def test_ast_describer_onboarding_and_agent_purpose_json_are_minified() -> None:
    viewer = _build_viewer(("ops",))

    onboarding = json.loads(viewer.describe_agent_onboarding_json())
    viewer_purpose = json.loads(viewer.describe_viewer_agent_purpose_json())
    profile_purpose = json.loads(
        viewer.describe_selected_profile_agent_purpose_json(frame_name="ops")
    )
    helper_purposes = json.loads(
        viewer.describe_selected_profile_helper_agent_purposes_json(
            frame_name="ops"
        )
    )

    assert onboarding["recommended_system_objects"] == [
        "__architecture__",
        "__components__",
        "__graph_network__",
        "__graph_details__",
    ]
    assert viewer_purpose["access"] == "public"
    assert "access: public" in viewer_purpose["agent_purpose"]
    assert profile_purpose["access"] == "public"
    assert set(helper_purposes.keys()) == {"view_frame", "view_conduit", "view_spell"}
    assert helper_purposes["view_frame"]["access"] == "public"


class _PrivateAstTarget:
    _ast_helper_access = "private"
    __agent_purpose__ = "access: private. Private target used for AST helper tests."

    def visible(self) -> None:
        raise AssertionError("Should never be described through the private AST path.")


class _MissingAstAccessTarget:
    __agent_purpose__ = "access: public. Missing access marker for AST helper tests."

    def visible(self) -> None:
        raise AssertionError("Should never be described when access metadata is missing.")


class _AstPurposeBase:
    __agent_purpose__ = "access: public. Parent AST purpose."


class _ExplicitAstChild(_AstPurposeBase):
    _ast_helper_access = "public"
    __agent_purpose__ = "access: public. Child AST purpose."

    def visible(self) -> None:
        raise AssertionError("Only class-surface metadata should be described.")


class _InheritedOnlyAstChild(_AstPurposeBase):
    _ast_helper_access = "public"

    def visible(self) -> None:
        raise AssertionError("Only class-surface metadata should be described.")


def test_ast_describer_private_and_missing_access_guards_work() -> None:
    private_target = _PrivateAstTarget()
    missing_access_target = _MissingAstAccessTarget()

    assert json.loads(
        ClassSurfaceAstDescriber.describe_agent_purpose_json(private_target)
    ) == {
        "class_name": "_PrivateAstTarget",
        "access": "private",
        "agent_purpose": "access: private. Private target used for AST helper tests.",
        "inherited_agent_purposes": [],
        "recommended_system_objects": [
            "__architecture__",
            "__components__",
            "__graph_network__",
            "__graph_details__",
        ],
    }
    with pytest.raises(ValueError, match="private class and cannot show any data"):
        ClassSurfaceAstDescriber.describe_class_surface_ast_json(private_target)
    with pytest.raises(ValueError, match="AST helper access is missing"):
        ClassSurfaceAstDescriber.describe_class_surface_ast_json(missing_access_target)


def test_ast_describer_reports_inherited_purposes_without_using_them_as_direct_purpose() -> None:
    explicit_child = _ExplicitAstChild()
    inherited_only_child = _InheritedOnlyAstChild()

    explicit_child_surface = json.loads(
        ClassSurfaceAstDescriber.describe_agent_purpose_json(explicit_child)
    )
    inherited_only_surface = json.loads(
        ClassSurfaceAstDescriber.describe_agent_purpose_json(inherited_only_child)
    )

    assert explicit_child_surface == {
        "class_name": "_ExplicitAstChild",
        "access": "public",
        "agent_purpose": "access: public. Child AST purpose.",
        "inherited_agent_purposes": [
            {
                "class_name": "_AstPurposeBase",
                "agent_purpose": "access: public. Parent AST purpose.",
            }
        ],
        "recommended_system_objects": [
            "__architecture__",
            "__components__",
            "__graph_network__",
            "__graph_details__",
        ],
    }
    assert inherited_only_surface == {
        "class_name": "_InheritedOnlyAstChild",
        "access": "public",
        "agent_purpose": (
            "access: public. Generic Melder object. Use the class surface and "
            "top-level system-doc objects for deeper orientation."
        ),
        "inherited_agent_purposes": [
            {
                "class_name": "_AstPurposeBase",
                "agent_purpose": "access: public. Parent AST purpose.",
            }
        ],
        "recommended_system_objects": [
            "__architecture__",
            "__components__",
            "__graph_network__",
            "__graph_details__",
        ],
    }


def test_top_level_system_document_objects_exist_and_render_placeholder_content() -> None:
    assert melder.__architecture__.render_json() == (
        '{"m":"placeholder: packaged Melder architecture hardcopy"}'
    )
    assert melder.__components__.render_json() == (
        '{"m":"placeholder: packaged Melder components hardcopy"}'
    )
    assert melder.__graph_network__.render_json() == (
        '{"m":"placeholder: packaged Melder graph network hardcopy"}'
    )
    assert melder.__graph_details__.render_json() == (
        '{"m":"placeholder: packaged Melder graph details hardcopy"}'
    )
    assert melder.__architecture__.render_markdown() == (
        "placeholder: packaged Melder architecture hardcopy"
    )


def test_view_spell_detailed_methods_surface_profile_sections_and_dunders() -> None:
    configuration = FrameACLConfiguration.create_default("ops")
    surface = _build_surface(
        "ops",
        configuration,
        spell_sections_by_key={
            ("ops-spellbook", "ops-spell"): (
                "binding_payload",
                "class_profile",
                "callable_profile",
                "instance_members",
                "dynamic_access",
                "metadata",
            ),
        },
    )
    viewer = FrameViewer(
        frame_descriptors_by_name={"ops": _build_detailed_descriptor("ops", include_dunders=True)},
        frame_acl_configurations_by_frame_name={"ops": configuration},
        compiled_access_surfaces_by_frame_name={"ops": surface},
        default_view_frame_name="ops",
    )
    view_spell = viewer.get_selected_profile_for_frame("ops").view_spell

    class_profile = view_spell.describe_spell_class_profile("ops-spellbook:ops-spell")
    callable_profile = view_spell.describe_spell_callable_profile("ops-spellbook:ops-spell")
    instance_members = view_spell.describe_spell_instance_members("ops-spellbook:ops-spell")
    dynamic_access = view_spell.describe_spell_dynamic_access("ops-spellbook:ops-spell")
    dunder_members = view_spell.describe_spell_dunder_members("ops-spellbook:ops-spell")

    assert class_profile["detail_available"] is True
    assert class_profile["payload"]["dunder_member_names"] == ("__dict__",)
    assert class_profile["payload"]["dunder_method_names"] == ("__enter__",)
    assert callable_profile["detail_available"] is True
    assert callable_profile["payload"]["signature"] == "() -> None"
    assert instance_members["detail_available"] is True
    assert "__dict__" in instance_members["payload"]
    assert dynamic_access["detail_available"] is True
    assert dynamic_access["payload"] == {"has_getattr": False}
    assert dunder_members == {
        "source_id": "ops-spellbook:ops-spell",
        "detail_available": True,
        "class_member_names": ("__dict__",),
        "class_method_names": ("__enter__",),
        "instance_member_names": ("__dict__",),
    }
    assert view_spell.list_spell_dunder_member_names("ops-spellbook:ops-spell") == (
        "__dict__",
        "__enter__",
    )


def test_frame_viewer_cleanup_cascades_to_owned_surfaces_and_profiles_only() -> None:
    viewer = _build_viewer(("ops",))
    descriptor = viewer.frame_descriptors_by_name["ops"]
    surface = viewer.compiled_access_surfaces_by_frame_name["ops"]

    viewer.cleanup()

    assert viewer.cleaned is True
    assert surface.cleaned is True
    assert descriptor.cleaned is False


def test_frame_viewer_clone_detaches_owned_surfaces_and_metadata() -> None:
    viewer = _build_viewer(("ops",))
    cloned = viewer.clone()

    assert cloned is not viewer
    assert cloned.frame_descriptors_by_name["ops"] is viewer.frame_descriptors_by_name["ops"]
    assert (
        cloned.compiled_access_surfaces_by_frame_name["ops"]
        is not viewer.compiled_access_surfaces_by_frame_name["ops"]
    )


def test_frame_viewer_constructor_rejects_invalid_registry_and_default_inputs() -> None:
    descriptor = _build_descriptor("ops")
    configuration = FrameACLConfiguration.create_default("ops")
    surface = _build_surface("ops", configuration)

    with pytest.raises(TypeError, match="profile_builder must be a FrameViewerProfileBuilder"):
        FrameViewer(profile_builder=object())

    with pytest.raises(ValueError, match="maps must have matching keys"):
        FrameViewer(
            frame_descriptors_by_name={"ops": descriptor},
            frame_acl_configurations_by_frame_name={"ops": configuration},
            compiled_access_surfaces_by_frame_name={},
        )

    with pytest.raises(ValueError, match="default_view_frame_name cannot be empty"):
        FrameViewer(
            frame_descriptors_by_name={"ops": descriptor},
            frame_acl_configurations_by_frame_name={"ops": configuration},
            compiled_access_surfaces_by_frame_name={"ops": surface},
            default_view_frame_name="",
        )

    with pytest.raises(ValueError, match="default_view_frame_name must be present"):
        FrameViewer(
            frame_descriptors_by_name={"ops": descriptor},
            frame_acl_configurations_by_frame_name={"ops": configuration},
            compiled_access_surfaces_by_frame_name={"ops": surface},
            default_view_frame_name="finance",
        )

    inspection_profile = FrameViewerProfile(
        "inspection",
        default_grouping="frame",
        default_detail_level="detailed",
        enabled_helpers=("list_frames",),
    )

    with pytest.raises(ValueError, match="default_profile_name cannot be empty"):
        FrameViewer(
            active_profiles_by_name={"inspection": inspection_profile},
            frame_descriptors_by_name={"ops": descriptor},
            frame_acl_configurations_by_frame_name={"ops": configuration},
            compiled_access_surfaces_by_frame_name={"ops": surface},
            default_profile_name="",
        )

    with pytest.raises(ValueError, match="default_profile_name must be present"):
        FrameViewer(
            active_profiles_by_name={"inspection": inspection_profile},
            frame_descriptors_by_name={"ops": descriptor},
            frame_acl_configurations_by_frame_name={"ops": configuration},
            compiled_access_surfaces_by_frame_name={"ops": surface},
            default_profile_name="general",
        )


def test_frame_viewer_empty_defaults_and_selected_profile_fallbacks_are_explicit() -> None:
    empty_viewer = FrameViewer(
        active_profiles_by_name={},
        frame_descriptors_by_name={},
        frame_acl_configurations_by_frame_name={},
        compiled_access_surfaces_by_frame_name={},
    )

    assert empty_viewer.default_view_frame_name is None
    assert empty_viewer.profile_name is None
    assert empty_viewer.profile_version is None
    assert empty_viewer.enabled_helpers == tuple()
    assert empty_viewer.default_grouping is None
    assert empty_viewer.default_detail_level is None
    assert empty_viewer.profile is None

    viewer = _build_viewer(("ops",))
    detached_selection_viewer = FrameViewer(
        frame_descriptors_by_name=viewer.frame_descriptors_by_name,
        frame_acl_configurations_by_frame_name=viewer.frame_acl_configurations_by_frame_name,
        compiled_access_surfaces_by_frame_name=viewer.compiled_access_surfaces_by_frame_name,
        selected_profile_names_by_frame_name={"ops": None},
        default_view_frame_name="ops",
    )

    assert detached_selection_viewer.profile_name == "general"
    assert detached_selection_viewer.profile is None
    assert detached_selection_viewer.selected_profile_names_by_frame_name == {}


def test_frame_viewer_rejects_invalid_frame_and_profile_inputs() -> None:
    viewer = _build_viewer(("ops",))

    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        viewer.set_default_view("")

    with pytest.raises(ValueError, match="Frame 'finance' was not found"):
        viewer.set_default_view("finance")

    with pytest.raises(ValueError, match="profile_name cannot be empty"):
        viewer.set_default_profile("")

    with pytest.raises(ValueError, match="FrameViewer profile 'missing' was not found"):
        viewer.set_default_profile("missing")


def test_frame_viewer_rejects_empty_tool_and_kind_inputs() -> None:
    viewer = _build_viewer(("ops",))

    with pytest.raises(ValueError, match="method_name cannot be empty"):
        viewer.execute_method("")

    with pytest.raises(ValueError, match="source_kind cannot be empty"):
        viewer.execute_method("list_targets", source_kind="")


def test_frame_viewer_selected_profile_is_bound_to_frame_context() -> None:
    viewer = _build_viewer(("ops",))

    selected_profile = viewer.get_selected_profile_for_frame("ops")

    assert selected_profile.is_bound is True
    assert selected_profile.bound_frame_name == "ops"
    assert selected_profile.frame_descriptor is viewer.frame_descriptors_by_name["ops"]
    assert (
        selected_profile.frame_acl_configuration
        is viewer.frame_acl_configurations_by_frame_name["ops"]
    )
    assert (
        selected_profile.compiled_access_surface
        is viewer.compiled_access_surfaces_by_frame_name["ops"]
    )


def test_frame_viewer_can_set_selected_profile_for_frame() -> None:
    viewer = _build_viewer(("ops",))

    viewer.set_selected_profile_for_frame("ops", "general")

    assert viewer.selected_profile_names_by_frame_name == {"ops": "general"}
    assert viewer.get_selected_profile_for_frame("ops").name == "general"


def test_frame_viewer_selected_profile_for_frame_shapes_execution() -> None:
    viewer = _build_viewer(("ops",))
    viewer.set_selected_profile_for_frame("ops", "general")

    descriptions = viewer.execute_method(
        "describe_spells",
        frame_name="ops",
    )

    assert len(descriptions) == 1
    assert descriptions[0]["source_kind"] == "spell"
    assert "payload" in descriptions[0]


def test_frame_viewer_profile_binding_rejects_acl_view_profile_requirement_mismatch() -> None:
    viewer = _build_viewer(("ops",))
    constrained_profile = FrameViewerProfile(
        "hybrid_only",
        required_acl_view_profile_name="hybrid",
        required_acl_view_profile_version="0.0.1",
        tool_handler_names_by_name={"list_frames": "list_frame_names"},
    )
    viewer.register_active_profile(constrained_profile)

    with pytest.raises(
            ValueError,
            match="requires ACL view profile 'hybrid:0.0.1', got 'safe:0.0.1'",
    ):
        viewer.set_selected_profile_for_frame("ops", "hybrid_only")


def test_frame_viewer_cleanup_is_idempotent_and_rechecks_cleaned_state_under_lock() -> None:
    class _FlipCleanedOnEnter:
        def __init__(self, owner: FrameViewer) -> None:
            self._owner = owner

        def __enter__(self) -> "_FlipCleanedOnEnter":
            self._owner._cleaned = True
            return self

        def __exit__(self, exc_type, exc, tb) -> bool:
            return False

    viewer = _build_viewer(("ops",))

    viewer._cleaned = True
    viewer.cleanup()

    viewer = _build_viewer(("ops",))
    original_lock = viewer._lock
    viewer._lock = _FlipCleanedOnEnter(viewer)
    try:
        viewer.cleanup()
    finally:
        viewer._lock = original_lock

    assert viewer.cleaned is True
