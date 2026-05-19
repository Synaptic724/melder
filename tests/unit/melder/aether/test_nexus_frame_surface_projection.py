import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.aetheric_frame_configuration import AethericFrameConfiguration
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
from melder.aether.nexus.nexus import Nexus
from melder.aether.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from melder.aether.nexus.rift.frame_viewer.static_frame_viewer import (
    StaticFrameViewer,
)
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
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
    posture = AethericFrameConfiguration(
        origin_spellbook_id="{0}-spellbook".format(frame_name),
        system_state=system_state,
        ai_native_enabled=ai_native_enabled,
        rift_enabled=rift_enabled,
    )
    aether._ensure_frame(frame_name).bind_frame_configuration(posture)


def _create_enabled_nexus(*allowed_target_frame_names: str) -> Nexus:
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
    configuration.with_multiple_target_frames(True)
    configuration.with_max_target_frame_count(
        max(2, len(allowed_target_frame_names))
    )
    configuration.with_allowed_target_frame_names(
        ("default",) + (
            allowed_target_frame_names if allowed_target_frame_names else ("ops",)
        )
    )
    nexus.enable(configuration)
    return nexus


def test_rift_get_frame_viewer_projects_multiple_assigned_frames() -> None:
    """
    Verify a Rift-backed room viewer hosts multiple assigned frames.

    Returns:
        None.
    """
    _bind_target_frame_configuration("ops", rift_enabled=True)
    _bind_target_frame_configuration("finance", rift_enabled=True)
    nexus = _create_enabled_nexus("ops", "finance")
    _populate_descriptor(nexus, "ops")
    _populate_descriptor(nexus, "finance")
    rift = nexus.create_rift(rift_name="ops_rift")
    rift.create_frame_link("ops")
    rift.create_frame_link("finance")

    viewer = rift.get_frame_viewer()

    assert isinstance(viewer, FrameViewer)
    assert rift._build_frame_viewer_metadata()["frame_count"] == 2
    assert viewer.list_frame_names() == ["finance", "ops"]


def test_rift_get_frame_viewer_hosts_descriptor_and_compiled_surface_maps() -> None:
    """
    Verify the attached room viewer hosts descriptor and compiled-surface maps
    directly.

    Returns:
        None.
    """
    _bind_target_frame_configuration("ops", rift_enabled=True)
    _bind_target_frame_configuration("finance", rift_enabled=True)
    nexus = _create_enabled_nexus("ops", "finance")
    _populate_descriptor(nexus, "ops")
    _populate_descriptor(nexus, "finance")
    rift = nexus.create_rift(rift_name="ops_rift")
    rift.create_frame_link("ops")
    rift.create_frame_link("finance")

    viewer = rift.get_frame_viewer()

    assert isinstance(viewer, FrameViewer)
    assert viewer._get_required_frame_descriptor("finance").frame_name == "finance"
    assert viewer._get_required_frame_descriptor("ops").frame_name == "ops"
    assert viewer._get_required_compiled_access_surface("finance").frame_name == "finance"
    assert viewer._get_required_compiled_access_surface("ops").frame_name == "ops"


def test_rift_refresh_runtime_projections_for_one_frame_preserves_other_room_projections() -> None:
    """
    Verify frame-scoped refresh keeps unrelated installed projections and the
    attached viewer.

    Returns:
        None.
    """
    _bind_target_frame_configuration("ops", rift_enabled=True)
    _bind_target_frame_configuration("finance", rift_enabled=True)
    nexus = _create_enabled_nexus("ops", "finance")
    _populate_descriptor(nexus, "ops")
    _populate_descriptor(nexus, "finance")
    rift = nexus.create_rift(rift_name="ops_rift")
    rift.create_frame_link("ops")
    rift.create_frame_link("finance")
    first_viewer = rift.get_frame_viewer()

    rift.refresh_runtime_projections(frame_names=("ops",))

    second_viewer = rift.get_frame_viewer()

    assert second_viewer is first_viewer
    assert second_viewer.list_frame_names() == ["finance", "ops"]
    assert rift._get_required_frame_projection_set("finance").frame_name == "finance"
    assert rift._get_required_frame_projection_set("ops").frame_name == "ops"


def test_rift_refresh_runtime_projections_for_multiple_frames_uses_one_projection_build_and_sync(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify explicit multi-frame refresh uses one projection-build call, one
    merge call, and one viewer sync.

    Args:
        monkeypatch:
            Pytest monkeypatch fixture.

    Returns:
        None.
    """
    _bind_target_frame_configuration("ops", rift_enabled=True)
    _bind_target_frame_configuration("finance", rift_enabled=True)
    nexus = _create_enabled_nexus("ops", "finance")
    _populate_descriptor(nexus, "ops")
    _populate_descriptor(nexus, "finance")
    rift = nexus.create_rift(rift_name="ops_rift")
    rift.create_frame_link("ops")
    rift.create_frame_link("finance")

    create_calls = []
    apply_calls = []
    sync_calls = []
    original_create_frame_projection_sets_for_rift = (
        nexus.create_frame_projection_sets_for_rift
    )
    original_apply_projection_sets = rift._apply_projection_sets
    def wrapped_create_frame_projection_sets_for_rift(
            rift_id: str,
            *,
            frame_names=None,
    ):
        create_calls.append(
            (
                rift_id,
                tuple(frame_names) if frame_names is not None else None,
            )
        )
        return original_create_frame_projection_sets_for_rift(
            rift_id,
            frame_names=frame_names,
        )

    def wrapped_apply_projection_sets(
            projection_sets_by_frame_name,
            *,
            merge: bool = False,
    ) -> None:
        apply_calls.append(
            (
                tuple(sorted(projection_sets_by_frame_name.keys())),
                merge,
            )
        )
        return original_apply_projection_sets(
            projection_sets_by_frame_name,
            merge=merge,
        )

    monkeypatch.setattr(
        nexus,
        "create_frame_projection_sets_for_rift",
        wrapped_create_frame_projection_sets_for_rift,
    )
    monkeypatch.setattr(
        rift,
        "_apply_projection_sets",
        wrapped_apply_projection_sets,
    )
    rift.refresh_runtime_projections(frame_names=("ops", "finance"))

    assert create_calls == [
        (rift.id, ("ops", "finance")),
    ]
    assert apply_calls == [
        (("finance", "ops"), True),
    ]
    assert sync_calls == []
    assert rift._build_frame_viewer_metadata()["assigned_frame_names"] == (
        "ops",
        "finance",
    )


def test_rift_target_frame_populates_room_owned_viewer_metadata_from_assigned_frames() -> None:
    """
    Verify the attached room-owned viewer carries Rift-assignment metadata.

    Returns:
        None.
    """
    _bind_target_frame_configuration("ops", rift_enabled=True)
    nexus = _create_enabled_nexus("ops")
    _populate_descriptor(nexus, "ops")
    rift = nexus.create_rift(rift_name="ops_rift")
    rift.create_frame_link("ops")

    viewer = rift.get_frame_viewer()

    viewer_metadata = rift._build_frame_viewer_metadata()

    assert viewer_metadata["rift_id"] == rift.id
    assert viewer_metadata["assigned_frame_names"] == ("ops",)
    assert viewer_metadata["selected_contract_names_by_frame_name"] == {
        "ops": {
            "view": "ops",
            "command": "ops",
            "codegen": "ops",
        }
    }

