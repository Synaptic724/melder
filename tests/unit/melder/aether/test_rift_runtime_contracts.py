from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.aetheric_frame_configuration import AethericFrameConfiguration
from melder.nexus.configuration.rift_configuration import RiftConfiguration
from melder.nexus.configuration.rift_space_type import RiftSpaceType
from melder.nexus.frame_descriptor.frame_descriptor_payload import (
    FrameDescriptorPayload,
)
from melder.nexus.frame_descriptor.frame_record import FrameRecord
from melder.nexus.nexus import Nexus
from melder.nexus.rift.rift_gate.rift_gate import RiftGate
from melder.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from melder.nexus.rift.rift import Rift
from melder.nexus.rift.rift_space.static_rift_space import StaticRiftSpace
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.utilities.helpers.init_helpers import InitHelpers

@pytest.fixture(autouse=True)
def fresh_singletons() -> None:
    """
    Reset singleton runtime surfaces around each Rift runtime-contract test.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()


def _create_enabled_nexus() -> Nexus:
    """
    Create one enabled Nexus with basic direct-create and direct-access policy.

    Returns:
        Nexus: Enabled Nexus.
    """
    Aether()
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_target_frame_override(True)
    configuration.with_multiple_target_frames(True)
    configuration.with_max_target_frame_count(2)
    configuration.with_allowed_target_frame_names(("default", "ops"))
    nexus.enable(configuration)
    return nexus


def _bind_target_frame_configuration(
        frame_name: str,
        *,
        rift_enabled: bool,
        ai_native_enabled: bool = False,
        system_state: SystemState = SystemState.automatic,
) -> None:
    """
    Bind one target-frame configuration for Rift targeting tests.

    Args:
        frame_name:
            Target frame name.
        rift_enabled:
            Whether Rift posture is enabled.
        ai_native_enabled:
            Whether AI-native posture is enabled.
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


def _seed_frame_descriptor(frame_name: str) -> None:
    """
    Seed one minimal frame descriptor overview for Rift viewer tests.

    Args:
        frame_name:
            Target frame name.

    Returns:
        None.
    """
    Aether()
    descriptor = Nexus()._get_or_create_frame_descriptor(frame_name)
    descriptor.set_frame_overview(
        FrameRecord(
            frame_name=frame_name,
            frame_id="{0}-frame".format(frame_name),
            config_origin_spellbook_id="{0}-spellbook".format(frame_name),
            payload=FrameDescriptorPayload(
                system_state=SystemState.automatic,
                ai_native_enabled=False,
                rift_enabled=True,
                root_conduit_count=0,
                root_conduit_ids=tuple(),
                named_root_conduits=tuple(),
                conduit_cloud_entry_count=0,
                conduit_cloud_names=tuple(),
                cluster_count=0,
                cluster_names=tuple(),
            ),
        )
    )


def _build_finalized_rift_configuration() -> RiftConfiguration:
    """
    Build one finalized Rift configuration for direct Rift construction tests.

    Returns:
        RiftConfiguration: Finalized configuration.
    """
    configuration = RiftConfiguration().with_defaults()
    configuration.finalize()
    return configuration


def _create_registered_rift(
        *,
        space_type: RiftSpaceType = RiftSpaceType.static,
) -> Rift:
    """
    Create one real Rift through Nexus for runtime-contract tests.

    Returns:
        Rift: Registered Rift.
    """
    nexus = _create_enabled_nexus()
    configuration = nexus.create_rift_configuration().with_space_type(space_type)
    return nexus.create_rift(configuration=configuration, rift_name="alpha")


def test_rift_constructor_rejects_invalid_nexus_and_configuration_inputs() -> None:
    """
    Verify direct Rift construction enforces Nexus/configuration guardrails.

    Returns:
        None.
    """
    configuration = _build_finalized_rift_configuration()

    with pytest.raises(TypeError, match="nexus must satisfy INexus"):
        Rift(
            object(),
            configuration=configuration,
        )

    Aether()
    configured_only_nexus = Nexus()
    with pytest.raises(RuntimeError, match="configured Nexus"):
        Rift(
            configured_only_nexus,
            configuration=configuration,
        )

    system_configuration = configured_only_nexus.create_system_configuration()
    configured_only_nexus.enable(system_configuration)
    configured_only_nexus.disable()
    with pytest.raises(RuntimeError, match="enabled Nexus"):
        Rift(
            configured_only_nexus,
            configuration=configuration,
        )

    enabled_nexus = _create_enabled_nexus()
    unfrozen_configuration = RiftConfiguration().with_defaults()

    with pytest.raises(RuntimeError, match="finalized RiftConfiguration"):
        Rift(
            enabled_nexus,
            configuration=unfrozen_configuration,
        )


def test_rift_logger_falls_back_when_channel_resolution_fails(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify Rift logger initialization falls back to a safe logger on resolver failure.

    Returns:
        None.
    """

    nexus = _create_enabled_nexus()
    configuration = _build_finalized_rift_configuration()
    fallback_logger = MagicMock()

    def _raise_channel_resolution(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        InitHelpers,
        "resolve_channel_logger",
        _raise_channel_resolution,
    )
    monkeypatch.setattr(
        InitHelpers,
        "resolve_safe_logger",
        lambda logger=None: fallback_logger,
    )

    rift = Rift(
        nexus,
        configuration=configuration,
    )

    assert rift._logger is fallback_logger
    fallback_logger.error.assert_called_once()


def test_rift_create_frame_link_rejects_empty_frame_name() -> None:
    """
    Verify frame-link creation rejects an empty frame name.

    Returns:
        None.
    """
    _bind_target_frame_configuration("ops", rift_enabled=True)
    _seed_frame_descriptor("ops")
    rift = _create_registered_rift()

    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        rift.create_frame_link("")


def test_rift_create_frame_link_attaches_room_owned_viewer_path() -> None:
    """
    Verify creating a frame link attaches the room-owned viewer path.

    Returns:
        None.
    """
    _bind_target_frame_configuration("ops", rift_enabled=True)
    _seed_frame_descriptor("ops")
    rift = _create_registered_rift()

    rift.create_frame_link("ops")
    viewer = rift.get_frame_viewer()

    assert rift.get_frame_link_contract("ops").frame_name == "ops"
    assert rift.get_frame_link_contract("ops").get_selected_contract_name() == "ops"
    assert isinstance(viewer, FrameViewer)
    assert viewer.list_frame_names() == ["ops"]


def test_rift_get_frame_viewer_returns_durable_viewer_before_targeting() -> None:
    """
    Verify `get_frame_viewer()` returns the durable viewer asset even before
    any frame is targeted.

    Returns:
        None.
    """
    rift = _create_registered_rift()
    viewer = rift.get_frame_viewer()

    assert isinstance(viewer, FrameViewer)
    assert viewer.count_frames() == 0


def test_rift_frame_viewer_asset_is_stable_before_targeting() -> None:
    """
    Verify repeated Rift viewer reads return the same durable asset before any
    frame is targeted.

    Returns:
        None.
    """
    rift = _create_registered_rift()
    first_viewer = rift.get_frame_viewer()
    second_viewer = rift.get_frame_viewer()

    assert first_viewer is second_viewer


def test_capability_rift_spaces_expose_conduit_discovery_through_command_system() -> None:
    """
    Verify conduit discovery routes through the room-owned command surface.

    Returns:
        None.
    """
    _bind_target_frame_configuration("ops", rift_enabled=True)
    _seed_frame_descriptor("ops")
    rift = _create_registered_rift(space_type=RiftSpaceType.capability)
    rift.create_frame_link("ops")
    space = rift.space
    command = space.command_system
    conduit_cloud = object()
    conduit_object = object()
    command._aether = SimpleNamespace(
        _get_existing_frame=lambda frame_name: SimpleNamespace(
            _conduit_cloud=conduit_cloud,
        ),
        get_conduit_by_id=lambda conduit_id, frame_name: conduit_object,
        get_conduit_by_name=lambda name, frame_name: conduit_object,
    )
    command._get_enabled_published_conduit_records = (
        lambda frame_name: (
            SimpleNamespace(
                conduit_id="c1",
                payload=SimpleNamespace(conduit_name="alpha"),
            ),
            SimpleNamespace(
                conduit_id="c2",
                payload=SimpleNamespace(conduit_name="beta"),
            ),
        )
    )
    command._assert_frame_command_enabled = lambda frame_name: None
    command._get_required_compiled_access_surface = (
        lambda frame_name: SimpleNamespace(enabled_conduit_ids=("c1",))
    )
    command._get_required_published_conduit_id_by_name = (
        lambda name, frame_name: "c1" if name == "alpha" else None
    )

    assert command.get_conduit_cloud(frame_name="ops") is conduit_cloud
    assert command.list_conduit_ids(frame_name="ops") == ("c1", "c2")
    assert command.list_conduit_names(frame_name="ops") == ("alpha", "beta")
    assert command.count_conduits(frame_name="ops") == 2
    assert command.has_conduit_id("c1", frame_name="ops") is True
    assert command.has_conduit_name("alpha", frame_name="ops") is True
    assert command.find_conduit_id_by_name("alpha", frame_name="ops") == "c1"
    assert command.get_conduit_by_id("c1", frame_name="ops") is conduit_object
    assert command.get_conduit_by_name("alpha", frame_name="ops") is conduit_object


def test_rift_exposes_live_metadata_and_active_state_helpers() -> None:
    """
    Verify metadata is live and active-state helpers mutate local flags.

    Returns:
        None.
    """
    rift = _create_registered_rift()

    metadata = rift.metadata
    metadata["note"] = "live"
    rift.mark_inactive()

    assert rift.metadata["note"] == "live"
    assert rift.is_active is False


def test_rift_cleanup_is_idempotent_and_rechecks_cleaned_state_under_lock() -> None:
    """
    Verify cleanup short-circuits both before and after lock entry.

    Returns:
        None.
    """
    class _FlipCleanedOnEnter:
        """
        Flip the owner's cleaned flag during lock entry to model the race
        guarded by Rift.cleanup().
        """

        def __init__(self, owner: Rift) -> None:
            self._owner = owner

        def __enter__(self) -> "_FlipCleanedOnEnter":
            self._owner._cleaned = True
            return self

        def __exit__(self, exc_type, exc, tb) -> bool:
            return False

    rift = _create_registered_rift()

    rift._cleaned = True
    rift.cleanup()

    rift._cleaned = False
    original_lock = rift._lock
    rift._lock = _FlipCleanedOnEnter(rift)
    try:
        rift.cleanup()
    finally:
        rift._lock = original_lock

    assert rift.cleaned is True

def test_rift_exposes_one_primary_space_surface() -> None:
    """
    Verify Rift exposes exactly one owned primary space.

    Returns:
        None.
    """
    rift = _create_registered_rift()

    assert isinstance(rift.space, StaticRiftSpace)
    assert rift.space.owner_rift_id == rift.id
    assert rift.rift_gate is not None


def test_rift_starts_without_assigned_frames() -> None:
    """
    Verify a newly registered Rift starts without assigned target frames.

    Returns:
        None.
    """
    rift = _create_registered_rift()
    assert rift.list_assigned_frame_names() == tuple()


def test_rift_create_primary_space_from_configuration_supports_explicit_space_id() -> None:
    """
    Verify explicit primary-space ids flow into the created room.

    Returns:
        None.
    """
    nexus = _create_enabled_nexus()
    configuration = RiftConfiguration().with_defaults().with_space_type(
        RiftSpaceType.static
    )
    configuration.finalize()

    rift = Rift(
        nexus,
        configuration=configuration,
        space_id="space-explicit",
    )

    assert isinstance(rift.space, StaticRiftSpace)
    assert rift.space.space_id == "space-explicit"
    assert isinstance(rift.rift_gate, RiftGate)

