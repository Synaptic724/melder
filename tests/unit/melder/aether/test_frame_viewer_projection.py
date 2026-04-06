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
                profile_name="general",
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


def _build_surface(
        frame_name: str,
        configuration: FrameACLConfiguration,
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
        conduit_payload_sections_by_id={
            "{0}-conduit".format(frame_name): ("conduit_name", "conduit_state")
        },
        spell_payload_sections_by_key={
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

    assert descriptions[0]["frame_name"] == "finance"
    assert descriptions[1]["frame_name"] == "ops"
    assert descriptions[1]["is_default"] is True


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
    viewer.register_active_profile(FrameViewerProfile.create_inspection())
    viewer.set_default_profile("inspection")

    descriptions = viewer.describe_available_targets()

    assert descriptions[0]["source_kind"] == "frame"
    assert "metadata" in descriptions[0]


def test_frame_viewer_can_list_active_viewer_profiles_and_set_default() -> None:
    viewer = _build_viewer(("ops",))
    viewer.register_active_profile(FrameViewerProfile.create_navigation())

    assert viewer.list_view_profile_names() == ["general", "navigation"]

    viewer.set_default_view_profile("navigation")

    assert viewer.profile_name == "navigation"


def test_frame_viewer_execute_tool_routes_through_profile_mapping() -> None:
    viewer = _build_viewer(("ops",))
    viewer.register_active_profile(FrameViewerProfile.create_inspection())

    descriptions = viewer.execute_tool(
        "describe_targets",
        profile_name="inspection",
    )

    assert descriptions[0]["source_kind"] == "frame"


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

    summary = viewer.describe_frame("ops")

    assert summary["frame_name"] == "ops"
    assert summary["link_count"] == 3
    assert summary["available_kinds"] == ("conduit", "frame", "spell")


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
    viewer.register_active_profile(FrameViewerProfile.create_inspection())

    viewer.set_selected_profile_for_frame("ops", "inspection")

    assert viewer.selected_profile_names_by_frame_name == {"ops": "inspection"}
    assert viewer.get_selected_profile_for_frame("ops").name == "inspection"


def test_frame_viewer_selected_profile_for_frame_shapes_execution() -> None:
    viewer = _build_viewer(("ops",))
    viewer.register_active_profile(FrameViewerProfile.create_inspection())
    viewer.set_selected_profile_for_frame("ops", "inspection")

    descriptions = viewer.describe_available_targets(frame_name="ops")

    assert "metadata" in descriptions[0]


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
