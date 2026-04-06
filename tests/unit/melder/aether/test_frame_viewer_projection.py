from typing import Optional

import pytest

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
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.existence.existence import Existence


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


def _build_detailed_descriptor(frame_name: str) -> FrameDescriptor:
    descriptor = _build_descriptor(frame_name)
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
                class_profile={"methods": ["run"]},
                callable_profile={"signature": "() -> None"},
                metadata={"frame": frame_name},
                instance_members={"state": {"type": "str"}},
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


def test_frame_viewer_lists_links_for_one_frame() -> None:
    viewer = _build_viewer(("ops",))

    links = viewer.list_links(frame_name="ops")

    assert [link.source_kind for link in links] == ["frame", "conduit", "spell"]


def test_frame_viewer_lists_links_across_frames_deterministically() -> None:
    viewer = _build_viewer(("ops", "finance"))

    links = viewer.list_links()

    assert [link.frame_name for link in links] == [
        "finance",
        "finance",
        "finance",
        "ops",
        "ops",
        "ops",
    ]


def test_frame_viewer_lists_available_targets_for_default_frame() -> None:
    viewer = _build_viewer(("ops",))

    targets = viewer.list_available_targets()

    assert [target.source_kind for target in targets] == ["frame", "conduit", "spell"]


def test_frame_viewer_describe_available_targets_adds_metadata_for_detailed_profile() -> None:
    viewer = _build_viewer(("ops",))

    descriptions = viewer.describe_available_targets()

    assert descriptions[0]["source_kind"] == "frame"
    assert "metadata" in descriptions[0]


def test_frame_viewer_can_list_active_viewer_profiles_and_set_default() -> None:
    viewer = _build_viewer(("ops",))

    assert viewer.list_view_profile_names() == ["general"]

    viewer.set_default_view_profile("general")

    assert viewer.profile_name == "general"


def test_frame_viewer_execute_tool_routes_through_profile_mapping() -> None:
    viewer = _build_viewer(("ops",))

    descriptions = viewer.execute_tool(
        "describe_targets",
    )

    assert descriptions[0]["source_kind"] == "frame"
    assert "metadata" in descriptions[0]


def test_frame_viewer_get_required_link_by_source_returns_matching_link() -> None:
    viewer = _build_viewer(("ops",))

    link = viewer.get_required_link_by_source(
        frame_name="ops",
        source_kind="spell",
        source_id="ops-spellbook:ops-spell",
    )

    assert link.display_name == "ops_spell"


def test_frame_viewer_display_names_and_counts_can_filter() -> None:
    viewer = _build_viewer(("ops", "finance"))

    assert viewer.count_links() == 6
    assert viewer.count_links(source_kind="spell") == 2
    assert viewer.list_display_names(frame_name="ops") == ["ops", "root", "ops_spell"]


def test_frame_viewer_describe_frame_summarizes_descriptor_driven_surface() -> None:
    viewer = _build_viewer(("ops",))

    summary = viewer.execute_tool(
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

    assert viewer.execute_tool("count_frames") == 2
    assert viewer.execute_tool("count_root_conduits") == 2
    assert viewer.execute_tool("count_spell_records") == 2


def test_frame_viewer_describe_frame_inventory_reports_visible_ids() -> None:
    viewer = _build_viewer(("ops",))

    inventory = viewer.execute_tool(
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

    contract = viewer.execute_tool(
        "describe_frame_access_contract",
        frame_name="ops",
    )

    assert contract["frame_name"] == "ops"
    assert contract["view_profile_name"] == "safe"
    assert contract["codegen_profile_name"] == "safe"
    assert contract["frame_payload_fields"] == ("system_state", "rift_enabled")


def test_frame_viewer_find_target_by_display_name_returns_exact_matches() -> None:
    viewer = _build_viewer(("ops",))

    targets = viewer.execute_tool(
        "find_target_by_display_name",
        frame_name="ops",
        display_name="ops_spell",
    )

    assert len(targets) == 1
    assert targets[0].source_kind == "spell"


def test_frame_viewer_explain_target_access_reports_visible_spell_sections() -> None:
    viewer = _build_viewer(("ops",))

    explanation = viewer.execute_tool(
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

    payload_description = viewer.execute_tool(
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

    conduit_description = viewer.execute_tool(
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

    topology = viewer.execute_tool(
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

    conduits = viewer.execute_tool(
        "find_conduit_by_name",
        frame_name="ops",
        conduit_name="root",
    )

    assert len(conduits) == 1
    assert conduits[0].source_kind == "conduit"


def test_frame_viewer_explain_conduit_access_reports_acl_flags() -> None:
    viewer = _build_viewer(("ops",))

    explanation = viewer.execute_tool(
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

    conduit_state = viewer.execute_tool(
        "get_conduit_payload_field",
        frame_name="ops",
        conduit_id="ops-conduit",
        field_name="conduit_state",
    )

    assert conduit_state == "normal"


def test_frame_viewer_describe_spell_returns_acl_filtered_payload() -> None:
    viewer = _build_viewer(("ops",))

    spell_description = viewer.execute_tool(
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

    spell_description = viewer.execute_tool(
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

    detail = viewer.execute_tool(
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

    spells = viewer.execute_tool(
        "find_spell_by_binding_name",
        frame_name="ops",
        binding_name="ops_spell",
    )

    assert len(spells) == 1
    assert spells[0].source_kind == "spell"


def test_frame_viewer_list_spells_by_payload_type_filters_visible_spells() -> None:
    viewer = _build_viewer(("ops",))

    spells = viewer.execute_tool(
        "list_spells_by_payload_type",
        frame_name="ops",
        payload_type="general",
    )

    assert len(spells) == 1
    assert spells[0].source_id == "ops-spellbook:ops-spell"


def test_frame_viewer_explain_spell_access_reports_detail_reason() -> None:
    viewer = _build_viewer(("ops",))

    explanation = viewer.execute_tool(
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

    binding_payload = viewer.execute_tool(
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

    detail = viewer.execute_tool(
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

    detail = viewer.execute_tool(
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

    with pytest.raises(ValueError, match="tool_name cannot be empty"):
        viewer.execute_tool("")

    with pytest.raises(ValueError, match="source_kind cannot be empty"):
        viewer.list_links_by_kind("")


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

    descriptions = viewer.execute_tool(
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
