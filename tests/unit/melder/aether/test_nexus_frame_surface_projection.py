import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.spellbook.configuration.configuration import Configuration
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.nexus.frame_descriptor.conduit_descriptor_payload import (
    ConduitDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.conduit_record import ConduitRecord
from melder.aether.nexus.frame_descriptor.frame_descriptor_payload import (
    FrameDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.frame_record import FrameRecord
from melder.aether.nexus.frame_descriptor.spell_descriptor_payload import (
    SpellDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.spell_record import SpellRecord
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.nexus import Nexus
from melder.aether.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from melder.aether.nexus.rift.frame_viewer.static_frame_viewer import (
    StaticFrameViewer,
)
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from melder.aether.conduit.conduit import Conduit


@pytest.fixture(autouse=True)
def fresh_singletons() -> None:
    """
    Reset singleton runtime surfaces around each Nexus projection unit test.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    StaticFrameViewer._aether = aether
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    StaticFrameViewer._aether = aether


def _populate_descriptor(nexus: Nexus, frame_name: str) -> None:
    """
    Populate one descriptor with frame, conduit, and spell records.

    Args:
        nexus:
            Nexus instance that owns the descriptor manager.
        frame_name:
            Frame name to populate.

    Returns:
        None.
    """
    descriptor = nexus._get_or_create_frame_descriptor(frame_name)
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
                named_root_conduits=(
                    ("{0}-conduit".format(frame_name), "root"),
                ),
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
        spell_index_id="{0}-lineage".format(frame_name),
            spell_name="{0}Spell".format(frame_name.title()),
            spellframe=None,
            binding_name="{0}_spell".format(frame_name),
            permissions=Permissions.create,
            existence=Existence.unique,
            payload=SpellDescriptorPayload(
                payload_type="detailed",
                binding_payload={"kind": "class"},
                resolution_payload={"requirements": []},
                class_profile={"methods": []},
                callable_profile=None,
                metadata={"doc": frame_name},
                instance_members={},
                dynamic_access={},
            ),
        )
    )


def _bind_target_frame_configuration(
        frame_name: str,
        *,
        rift_enabled: bool,
        ai_native_enabled: bool = False,
        system_state: SystemState = SystemState.automatic,
) -> None:
    """
    Bind one Melder frame configuration for Rift target-frame eligibility.

    Args:
        frame_name:
            Target frame name to configure.
        rift_enabled:
            Whether Rift access is enabled on the frame.
        ai_native_enabled:
            Whether AI-native mode is enabled on the frame.
        system_state:
            Target frame system state.

    Returns:
        None.
    """
    aether = Aether()
    aether._ensure_frame(frame_name)
    frame_configuration = Configuration()
    if system_state == SystemState.dynamic:
        frame_configuration.dynamic_defaults()
    else:
        frame_configuration.automatic_defaults()
    frame_configuration.with_rift_enabled(rift_enabled)
    frame_configuration.with_ai_native(ai_native_enabled)
    aether._bind_configuration(frame_configuration, frame_name)


def _create_enabled_nexus() -> Nexus:
    """
    Create one enabled Nexus for Rift/viewer projection tests.

    Returns:
        Nexus: Enabled Nexus with Rift creation enabled.
    """
    nexus = Nexus(aether=Aether())
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_target_frame_override(True)
    configuration.with_allowed_target_frame_names(("default", "ops"))
    nexus.enable(configuration)
    return nexus



def test_nexus_create_frame_viewer_projects_multiple_frames() -> None:
    """
    Verify Nexus can assemble one viewer from multiple projected frames.

    Returns:
        None.
    """
    nexus = Nexus(aether=Aether())
    _populate_descriptor(nexus, "ops")
    _populate_descriptor(nexus, "finance")

    viewer = nexus.create_frame_viewer(["ops", "finance"])

    assert isinstance(viewer, FrameViewer)
    assert viewer.profile_name == "general"
    assert viewer.metadata["frame_count"] == 2
    assert viewer.metadata["viewer_profile_name"] == "general"
    assert viewer.list_frame_names() == ["finance", "ops"]


def test_nexus_create_frame_viewer_hosts_descriptor_and_compiled_surface_maps() -> None:
    """
    Verify viewer projection hosts descriptor and compiled-surface maps directly.

    Returns:
        None.
    """
    nexus = Nexus(aether=Aether())
    _populate_descriptor(nexus, "ops")
    _populate_descriptor(nexus, "finance")

    viewer = nexus.create_frame_viewer(["ops", "finance"])

    assert isinstance(viewer, FrameViewer)
    assert list(sorted(viewer.frame_descriptors_by_name.keys())) == ["finance", "ops"]
    assert list(sorted(viewer.compiled_access_surfaces_by_frame_name.keys())) == [
        "finance",
        "ops",
    ]


def test_nexus_create_cached_frame_viewer_reuses_cache_but_returns_detached_clone() -> None:
    """
    Verify cached viewer projection reuses one canonical cache entry but
    returns detached clones.

    Returns:
        None.
    """
    nexus = Nexus(aether=Aether())
    _populate_descriptor(nexus, "ops")

    first_viewer = nexus.create_cached_frame_viewer(["ops"])
    second_viewer = nexus.create_cached_frame_viewer(["ops"])

    assert first_viewer is not second_viewer
    assert first_viewer.metadata == second_viewer.metadata
    assert len(nexus._projected_frame_viewers_by_cache_key) == 1


def test_nexus_cached_frame_viewer_invalidates_on_acl_change() -> None:
    """
    Verify viewer cache invalidates when the current ACL configuration changes.

    Returns:
        None.
    """
    nexus = Nexus(aether=Aether())
    _populate_descriptor(nexus, "ops")
    nexus.create_cached_frame_viewer(["ops"])
    original = nexus.get_current_frame_acl_configuration("ops")
    draft = FrameACLConfiguration.create_new_from_acl_configuration(
        original,
        reason="viewer_cache_invalidation",
    )
    draft.set_json_configuration_string(
        '{"frame_name":"ops","view_configuration":{"profile_name":"hybrid","profile_version":"0.0.1","minimum_spell_payload_type":"general","frame_override_ruleset":{"name":"frame_override","rules":[]},"conduit_override_ruleset":{"name":"conduit_override","rules":[]},"spell_override_ruleset":{"name":"spell_override","rules":[]},"member_override_ruleset":{"name":"member_override","rules":[]}},"codegen_configuration":{"profile_name":"safe","profile_version":"0.0.1","frame_override_ruleset":{"name":"frame_override","rules":[]},"conduit_override_ruleset":{"name":"conduit_override","rules":[]},"spell_override_ruleset":{"name":"spell_override","rules":[]},"capability_override_ruleset":{"name":"capability_override","rules":[]}}}'
    )
    draft.finalize()

    nexus.insert_head_frame_acl_configuration("ops", draft, select_as_current=True)

    assert nexus._projected_frame_viewers_by_cache_key == {}


def test_nexus_create_cached_frame_viewer_rejects_invalid_frame_name_inputs() -> None:
    """
    Verify cached viewer projection rejects invalid frame-name inputs.

    Returns:
        None.
    """
    nexus = Nexus(aether=Aether())

    with pytest.raises(TypeError, match="frame_names must be a sequence"):
        nexus.create_cached_frame_viewer("ops")

    with pytest.raises(ValueError, match="frame_names must contain non-empty strings"):
        nexus.create_cached_frame_viewer(["ops", ""])


def test_nexus_create_frame_viewer_for_rift_populates_available_views_from_assigned_frames() -> None:
    """
    Verify Rift-assigned target frames populate the viewer's available views.

    Returns:
        None.
    """
    _bind_target_frame_configuration("ops", rift_enabled=True)
    nexus = _create_enabled_nexus()
    _populate_descriptor(nexus, "ops")
    rift_configuration = nexus.create_rift_configuration()
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="ops_rift")
    rift.target_frame("ops")

    viewer = nexus.create_frame_viewer_for_rift(rift.id)

    assert viewer.metadata["rift_id"] == rift.id
    assert viewer.metadata["assigned_frame_names"] == ("ops",)
    assert list(viewer.frame_descriptors_by_name.keys()) == ["ops"]
    assert viewer.frame_descriptors_by_name["ops"].frame_name == "ops"
    assert viewer.default_view_frame_name == "ops"
    assert len(viewer.execute_method("list_targets")) >= 1


def test_nexus_create_cached_frame_viewer_for_rift_reuses_cache_but_returns_detached_clone() -> None:
    """
    Verify cached Rift viewers reuse the cache entry while returning clones.

    Returns:
        None.
    """
    _bind_target_frame_configuration("ops", rift_enabled=True)
    nexus = _create_enabled_nexus()
    _populate_descriptor(nexus, "ops")
    rift_configuration = nexus.create_rift_configuration()
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="ops_rift")
    rift.target_frame("ops")

    first_viewer = nexus.create_cached_frame_viewer_for_rift(rift.id)
    second_viewer = nexus.create_cached_frame_viewer_for_rift(rift.id)

    assert first_viewer is not second_viewer
    assert first_viewer.metadata["rift_id"] == rift.id
    assert second_viewer.metadata["assigned_frame_names"] == ("ops",)
    assert len(nexus._projected_frame_viewers_by_cache_key) == 1


def test_nexus_create_frame_viewer_for_rift_frame_scopes_to_one_engaged_frame() -> None:
    """
    Verify the Nexus frame-specific viewer facade scopes to one engaged frame.

    Returns:
        None.
    """
    _bind_target_frame_configuration("ops", rift_enabled=True)
    nexus = _create_enabled_nexus()
    _populate_descriptor(nexus, "ops")
    rift_configuration = nexus.create_rift_configuration()
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="ops_rift")
    rift.target_frame("ops")

    viewer = nexus.create_frame_viewer_for_rift_frame(rift.id, "ops")

    assert viewer.list_frame_names() == ["ops"]
    assert viewer.default_view_frame_name == "ops"
    assert viewer.metadata["rift_id"] == rift.id
    assert viewer.metadata["assigned_frame_names"] == ("ops",)


def test_nexus_create_frame_viewer_for_rift_frame_rejects_missing_or_unengaged_inputs() -> None:
    """
    Verify the frame-specific Rift viewer facade rejects invalid requests.

    Returns:
        None.
    """
    _bind_target_frame_configuration("ops", rift_enabled=True)
    nexus = _create_enabled_nexus()
    _populate_descriptor(nexus, "ops")
    rift_configuration = nexus.create_rift_configuration()
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="ops_rift")
    rift.target_frame("ops")

    with pytest.raises(ValueError, match="rift_id cannot be empty"):
        nexus.create_frame_viewer_for_rift_frame("", "ops")

    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        nexus.create_frame_viewer_for_rift_frame(rift.id, "")

    with pytest.raises(ValueError, match="is not engaged with frame"):
        nexus.create_frame_viewer_for_rift_frame(rift.id, "finance")


def test_nexus_create_frame_viewer_rejects_string_sequence_input() -> None:
    """
    Verify Nexus viewer projection rejects bare string inputs.

    Returns:
        None.
    """
    nexus = Nexus(aether=Aether())

    with pytest.raises(TypeError, match="frame_names must be a sequence"):
        nexus.create_frame_viewer("ops")


def test_nexus_create_frame_viewer_rejects_empty_frame_names() -> None:
    """
    Verify Nexus viewer projection rejects empty frame names inside the sequence.

    Returns:
        None.
    """
    nexus = Nexus(aether=Aether())

    with pytest.raises(ValueError, match="frame_names must contain non-empty strings"):
        nexus.create_frame_viewer(["ops", ""])
