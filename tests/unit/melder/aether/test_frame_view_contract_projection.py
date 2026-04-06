import pytest

from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
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
from melder.aether.nexus.rift.frame_link.frame_link import FrameLink
from melder.aether.nexus.rift.frame_link.frame_link_contract import (
    FrameLinkContract,
)
from melder.aether.nexus.rift.frame_viewer.frame_view import FrameView
from melder.aether.nexus.rift.frame_viewer.profiles.frame_view_profile import (
    FrameViewProfile,
)
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.existence.existence import Existence


def _build_frame_descriptor() -> FrameDescriptor:
    """
    Build one payload-backed descriptor for frame-view projection tests.

    Returns:
        FrameDescriptor: Descriptor with frame, conduit, and spell records.
    """
    descriptor = FrameDescriptor("ops")
    descriptor.set_frame_overview(
        FrameRecord(
            frame_name="ops",
            frame_id="frame-1",
            config_origin_spellbook_id="spellbook-1",
            payload=FrameDescriptorPayload(
                system_state=SystemState.dynamic,
                ai_native_enabled=True,
                rift_enabled=True,
                root_conduit_count=1,
                root_conduit_ids=("conduit-1",),
                named_root_conduits=(("conduit-1", "root"),),
                conduit_cloud_entry_count=1,
                conduit_cloud_names=("root",),
                cluster_count=0,
                cluster_names=tuple(),
            ),
        )
    )
    descriptor.upsert_conduit_record(
        ConduitRecord(
            conduit_id="conduit-1",
            root_conduit_id="conduit-1",
            frame_name="ops",
            origin_spellbook_id="spellbook-1",
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
            origin_spellbook_id="spellbook-1",
            frame_name="ops",
            owner_conduit_id="conduit-1",
            spell_id="spell-1",
            lineage_id="lineage-1",
            spell_name="SpellOne",
            spellframe=None,
            binding_name="spell_one",
            permissions=Permissions.create,
            existence=Existence.unique,
            payload=SpellDescriptorPayload(
                profile_name="detailed",
                binding_payload={"kind": "class"},
                resolution_payload={"requirements": []},
                class_profile={"methods": []},
                callable_profile=None,
                metadata={"doc": "spell"},
                instance_members={},
                dynamic_access={},
            ),
        )
    )
    return descriptor


def _build_compiled_surface() -> CompiledFrameACLAccessSurface:
    """
    Build one compiled ACL access surface for frame-view projection tests.

    Returns:
        CompiledFrameACLAccessSurface: Surface with frame/conduit/spell access.
    """
    return CompiledFrameACLAccessSurface(
        frame_name="ops",
        configuration_id="cfg-1",
        view_profile_name="safe",
        view_profile_version="0.0.1",
        codegen_profile_name="safe",
        codegen_profile_version="0.0.1",
        allowed_kinds=("frame", "conduit", "spell"),
        allowed_commands=("bind_existing", "query", "resolve_existing"),
        frame_payload_fields=("system_state", "rift_enabled"),
        visible_conduit_ids=("conduit-1",),
        visible_spell_keys=(("spellbook-1", "spell-1"),),
        conduit_payload_sections_by_id={
            "conduit-1": ("conduit_name", "conduit_state"),
        },
        spell_payload_sections_by_key={
            ("spellbook-1", "spell-1"): (
                "binding_payload",
                "resolution_payload",
                "metadata",
            ),
        },
        metadata={"source": "compiled"},
    )


def test_frame_link_contract_clone_detaches_metadata() -> None:
    """
    Verify Rift availability contract clones detach metadata and assignments.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops",),
        default_frame_name="ops",
        metadata={"source": "rift"},
    )

    cloned = contract.clone()
    cloned.register_frame("finance")

    assert cloned is not contract
    assert contract.assigned_frame_names == ("ops",)
    assert cloned.assigned_frame_names == ("ops", "finance")


def test_frame_link_from_view_subject_detaches_metadata_input() -> None:
    """
    Verify link construction detaches metadata input.

    Returns:
        None.
    """
    metadata = {"payload_fields": ("system_state",)}

    link = FrameLink.from_view_subject(
        frame_name="ops",
        source_kind="frame",
        source_id="frame-1",
        display_name="ops",
        metadata=metadata,
    )
    metadata["mutated"] = True

    assert link.metadata == {"payload_fields": ("system_state",)}


def test_frame_view_from_compiled_access_surface_builds_frame_conduit_and_spell_links() -> None:
    """
    Verify frame-view projection builds links for all visible kinds.

    Returns:
        None.
    """
    frame_view = FrameView.from_compiled_access_surface(
        frame_descriptor=_build_frame_descriptor(),
        compiled_access_surface=_build_compiled_surface(),
    )

    assert frame_view.frame_name == "ops"
    assert frame_view.metadata["allowed_kinds"] == (
        "conduit",
        "frame",
        "spell",
    )
    assert frame_view.metadata["link_count"] == 3
    assert frame_view.metadata["available_target_count"] == 3
    assert set(frame_view.available_target_ids_by_kind.keys()) == {
        "conduit",
        "frame",
        "spell",
    }
    assert frame_view.list_active_profile_names() == ["general"]
    links = list(frame_view.links_by_id.values())
    source_kinds = sorted(link.source_kind for link in links)

    assert source_kinds == ["conduit", "frame", "spell"]
    frame_link = next(link for link in links if link.source_kind == "frame")
    conduit_link = next(link for link in links if link.source_kind == "conduit")
    spell_link = next(link for link in links if link.source_kind == "spell")
    assert frame_link.metadata["payload_fields"] == (
        "system_state",
        "rift_enabled",
    )
    assert conduit_link.display_name == "root"
    assert conduit_link.metadata["payload_sections"] == (
        "conduit_name",
        "conduit_state",
    )
    assert spell_link.display_name == "spell_one"
    assert spell_link.metadata["payload_sections"] == (
        "binding_payload",
        "resolution_payload",
        "metadata",
    )


def test_frame_view_available_targets_surface_is_queryable_by_kind_and_id() -> None:
    """
    Verify the frame view exposes available targets by kind and by target id.

    Returns:
        None.
    """
    frame_view = FrameView.from_compiled_access_surface(
        frame_descriptor=_build_frame_descriptor(),
        compiled_access_surface=_build_compiled_surface(),
    )

    spell_targets = frame_view.list_available_targets(source_kind="spell")
    fetched = frame_view.get_required_available_target(spell_targets[0].link_id)

    assert len(spell_targets) == 1
    assert spell_targets[0].source_kind == "spell"
    assert fetched is spell_targets[0]


def test_frame_view_can_set_default_profile_and_order_targets_by_profile() -> None:
    """
    Verify the default local profile can reorder available targets.

    Returns:
        None.
    """
    frame_view = FrameView.from_compiled_access_surface(
        frame_descriptor=_build_frame_descriptor(),
        compiled_access_surface=_build_compiled_surface(),
    )
    inspection_profile = FrameViewProfile(
        "inspection",
        preferred_kind_order=("spell", "conduit", "frame"),
        default_detail_level="summary",
    )
    frame_view.register_active_profile(inspection_profile)
    frame_view.set_default_profile("inspection")

    ordered_targets = frame_view.list_available_targets_in_profile_order()

    assert frame_view.default_profile_name == "inspection"
    assert [frame_link.source_kind for frame_link in ordered_targets] == [
        "spell",
        "conduit",
        "frame",
    ]


def test_frame_view_describe_available_targets_uses_profile_detail_level() -> None:
    """
    Verify target descriptions respect the selected local profile detail level.

    Returns:
        None.
    """
    frame_view = FrameView.from_compiled_access_surface(
        frame_descriptor=_build_frame_descriptor(),
        compiled_access_surface=_build_compiled_surface(),
    )
    detailed_profile = FrameViewProfile(
        "inspection",
        preferred_kind_order=("frame", "conduit", "spell"),
        default_detail_level="detailed",
    )
    frame_view.register_active_profile(detailed_profile)

    descriptions = frame_view.describe_available_targets(profile_name="inspection")

    assert all("metadata" in description for description in descriptions)


def test_frame_view_default_profile_helpers_reject_missing_and_invalid_names() -> None:
    """
    Verify default-profile helpers fail fast on missing or invalid inputs.

    Returns:
        None.
    """
    frame_view = FrameView.from_compiled_access_surface(
        frame_descriptor=_build_frame_descriptor(),
        compiled_access_surface=_build_compiled_surface(),
    )

    with pytest.raises(ValueError, match="profile_name cannot be empty"):
        frame_view.set_default_profile("")

    with pytest.raises(ValueError, match="was not found"):
        frame_view.set_default_profile("missing")


def test_frame_view_from_compiled_access_surface_rejects_mismatched_frame_name() -> None:
    """
    Verify frame-view projection rejects mismatched descriptor/compiled frames.

    Returns:
        None.
    """
    with pytest.raises(
            ValueError,
            match="compiled_access_surface targets frame 'ops', expected 'finance'",
    ):
        FrameView.from_compiled_access_surface(
            frame_descriptor=FrameDescriptor("finance"),
            compiled_access_surface=_build_compiled_surface(),
        )


def test_frame_view_from_compiled_access_surface_requires_frame_overview_for_frame_links() -> None:
    """
    Verify frame-view projection fails fast if frame access exists with no
    frame overview record.

    Returns:
        None.
    """
    descriptor = FrameDescriptor("ops")

    with pytest.raises(ValueError, match="FrameDescriptor must expose frame_overview"):
        FrameView.from_compiled_access_surface(
            frame_descriptor=descriptor,
            compiled_access_surface=_build_compiled_surface(),
        )


def test_frame_view_from_compiled_access_surface_rejects_missing_visible_records() -> None:
    """
    Verify projection fails fast if compiled visibility references missing
    descriptor records.

    Returns:
        None.
    """
    descriptor = _build_frame_descriptor()
    compiled_surface = CompiledFrameACLAccessSurface(
        frame_name="ops",
        configuration_id="cfg-1",
        view_profile_name="safe",
        view_profile_version="0.0.1",
        codegen_profile_name="safe",
        codegen_profile_version="0.0.1",
        allowed_kinds=("frame", "conduit", "spell"),
        allowed_commands=("query",),
        frame_payload_fields=("system_state",),
        visible_conduit_ids=("missing-conduit",),
        visible_spell_keys=(("spellbook-1", "spell-1"),),
        conduit_payload_sections_by_id={"missing-conduit": tuple()},
        spell_payload_sections_by_key={("spellbook-1", "spell-1"): tuple()},
        metadata={},
    )

    with pytest.raises(
            ValueError,
            match="Missing ConduitRecord for compiled conduit id 'missing-conduit'",
    ):
        FrameView.from_compiled_access_surface(
            frame_descriptor=descriptor,
            compiled_access_surface=compiled_surface,
        )


def test_frame_view_cleanup_cascades_into_owned_links() -> None:
    """
    Verify frame-view cleanup cascades into the owned links and profiles.

    Returns:
        None.
    """
    frame_view = FrameView.from_compiled_access_surface(
        frame_descriptor=_build_frame_descriptor(),
        compiled_access_surface=_build_compiled_surface(),
    )
    links = list(frame_view.links_by_id.values())

    frame_view.cleanup()

    assert frame_view.cleaned is True
    assert all(link.cleaned is True for link in links)
    assert frame_view._links_by_id is None
