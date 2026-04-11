import logging
from types import SimpleNamespace
from typing import Optional
from unittest.mock import MagicMock

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.nexus.configuration.rift_configuration import RiftConfiguration
from melder.aether.nexus.configuration.rift_space_type import RiftSpaceType
from melder.aether.nexus.frame_descriptor.frame_descriptor_payload import (
    FrameDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.frame_record import FrameRecord
from melder.aether.nexus.nexus import Nexus
from melder.aether.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from melder.aether.nexus.rift.rift import Rift
from melder.aether.nexus.rift.rift_space.rift_event_configuration import (
    RiftEventConfiguration,
)
from melder.aether.nexus.rift.rift_space.static_rift_space import StaticRiftSpace
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.configuration.system_state import SystemState
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
    configuration = Configuration()
    if system_state == SystemState.dynamic:
        configuration.dynamic_defaults()
    else:
        configuration.automatic_defaults()
    configuration.with_rift_enabled(rift_enabled)
    configuration.with_ai_native(ai_native_enabled)
    aether._bind_configuration(configuration, frame_name)


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


def _create_registered_rift() -> Rift:
    """
    Create one real Rift through Nexus for runtime-contract tests.

    Returns:
        Rift: Registered Rift.
    """
    nexus = _create_enabled_nexus()
    return nexus.create_rift(rift_name="alpha")


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
            nexus_frame_names=("aetheric_frame_system",),
            default_nexus_frame_name="aetheric_frame_system",
            target_frame_names=tuple(),
            default_target_frame_name=None,
        )

    Aether()
    configured_only_nexus = Nexus()
    with pytest.raises(RuntimeError, match="configured Nexus"):
        Rift(
            configured_only_nexus,
            configuration=configuration,
            nexus_frame_names=("aetheric_frame_system",),
            default_nexus_frame_name="aetheric_frame_system",
            target_frame_names=tuple(),
            default_target_frame_name=None,
        )

    system_configuration = configured_only_nexus.create_system_configuration()
    configured_only_nexus.enable(system_configuration)
    configured_only_nexus.disable()
    with pytest.raises(RuntimeError, match="enabled Nexus"):
        Rift(
            configured_only_nexus,
            configuration=configuration,
            nexus_frame_names=("aetheric_frame_system",),
            default_nexus_frame_name="aetheric_frame_system",
            target_frame_names=tuple(),
            default_target_frame_name=None,
        )

    enabled_nexus = _create_enabled_nexus()
    unfrozen_configuration = RiftConfiguration().with_defaults()

    with pytest.raises(RuntimeError, match="finalized RiftConfiguration"):
        Rift(
            enabled_nexus,
            configuration=unfrozen_configuration,
            nexus_frame_names=("aetheric_frame_system",),
            default_nexus_frame_name="aetheric_frame_system",
            target_frame_names=tuple(),
            default_target_frame_name=None,
        )

    with pytest.raises(ValueError, match="nexus_frame_names cannot be empty"):
        Rift(
            enabled_nexus,
            configuration=configuration,
            nexus_frame_names=tuple(),
            default_nexus_frame_name="aetheric_frame_system",
            target_frame_names=tuple(),
            default_target_frame_name=None,
        )

    with pytest.raises(ValueError, match="default_nexus_frame_name must be present"):
        Rift(
            enabled_nexus,
            configuration=configuration,
            nexus_frame_names=("other",),
            default_nexus_frame_name="aetheric_frame_system",
            target_frame_names=tuple(),
            default_target_frame_name=None,
        )

    with pytest.raises(ValueError, match="default_target_frame_name must be present"):
        Rift(
            enabled_nexus,
            configuration=configuration,
            nexus_frame_names=("aetheric_frame_system",),
            default_nexus_frame_name="aetheric_frame_system",
            target_frame_names=tuple(),
            default_target_frame_name="ops",
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
        nexus_frame_names=("aetheric_frame_system",),
        default_nexus_frame_name="aetheric_frame_system",
        target_frame_names=tuple(),
        default_target_frame_name=None,
    )

    assert rift._logger is fallback_logger
    fallback_logger.error.assert_called_once()


def test_rift_target_frame_rejects_empty_inputs() -> None:
    """
    Verify target-frame engagement rejects empty frame and contract names.

    Returns:
        None.
    """
    _bind_target_frame_configuration("ops", rift_enabled=True)
    _seed_frame_descriptor("ops")
    rift = _create_registered_rift()

    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        rift.target_frame("")

    with pytest.raises(ValueError, match="must be a non-empty string"):
        rift.target_frame("ops", contract_name="")


def test_rift_engage_frame_alias_and_cached_viewer_path_work() -> None:
    """
    Verify the engage-frame alias and cached viewer wrapper both work.

    Returns:
        None.
    """
    _bind_target_frame_configuration("ops", rift_enabled=True)
    _seed_frame_descriptor("ops")
    rift = _create_registered_rift()

    rift.engage_frame("ops", set_as_default=True)
    viewer = rift.create_cached_frame_viewer()

    assert rift.frame_link_contract.has_frame("ops") is True
    assert isinstance(viewer, FrameViewer)
    assert viewer.default_view_frame_name == "ops"


def test_rift_create_new_frame_viewer_rejects_unengaged_frame() -> None:
    """
    Verify frame-specific viewer creation fails when the frame is not engaged.

    Returns:
        None.
    """
    rift = _create_registered_rift()

    with pytest.raises(ValueError, match="is not engaged with frame"):
        rift.create_new_frame_viewer("ops")


def test_rift_viewer_host_helpers_reject_missing_target_space() -> None:
    """
    Verify viewer host helpers fail fast when no target space is available.

    Returns:
        None.
    """
    rift = _create_registered_rift()
    rift._active_space_id = None

    with pytest.raises(ValueError, match="has no target space for frame viewer attachment"):
        rift.attach_frame_viewer_to_space()

    with pytest.raises(ValueError, match="has no target space for frame viewer access"):
        rift.get_space_frame_viewer()


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
    assert rift.local_conduit_id is None
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


def test_rift_register_space_rejects_wrong_owner_and_duplicates() -> None:
    """
    Verify space registration rejects wrong-owner and duplicate room state.

    Returns:
        None.
    """
    rift = _create_registered_rift()

    with pytest.raises(ValueError, match="must match the owning Rift id"):
        rift.register_space(
            SimpleNamespace(
                owner_rift_id="other",
                space_id="space-1",
                space_name="ops",
            )
        )

    rift.register_space(
        SimpleNamespace(
            owner_rift_id=rift.id,
            space_id="space-1",
            space_name="ops",
        )
    )

    with pytest.raises(ValueError, match="Space with id 'space-1' already exists"):
        rift.register_space(
            SimpleNamespace(
                owner_rift_id=rift.id,
                space_id="space-1",
                space_name="other",
            )
        )

    with pytest.raises(ValueError, match="Space name 'ops' already exists"):
        rift.register_space(
            SimpleNamespace(
                owner_rift_id=rift.id,
                space_id="space-2",
                space_name="ops",
            )
        )


def test_rift_space_lookup_and_active_space_errors_are_explicit() -> None:
    """
    Verify space lookup and active-space mutation errors are explicit.

    Returns:
        None.
    """
    rift = _create_registered_rift()

    with pytest.raises(ValueError, match="Space with id 'missing' was not found"):
        rift.get_space("missing")

    with pytest.raises(ValueError, match="Space with name 'missing' was not found"):
        rift.get_space_by_name("missing")

    with pytest.raises(ValueError, match="Space with id 'missing' was not found"):
        rift.set_active_space("missing")


def test_rift_space_lookup_and_active_space_success_paths_use_live_registry() -> None:
    """
    Verify named lookup and active-space updates use the live room registry.

    Returns:
        None.
    """
    rift = _create_registered_rift()
    room = SimpleNamespace(
        owner_rift_id=rift.id,
        space_id="space-2",
        space_name="ops",
    )
    rift.register_space(room)

    assert rift.get_space_by_name("ops") is room

    rift.set_active_space("space-2")

    assert rift.active_space_id == "space-2"


def test_rift_clones_event_configuration_and_deduplicates_nexus_frame_names() -> None:
    """
    Verify event-config cloning and Nexus-frame-name deduplication helpers work.

    Returns:
        None.
    """
    action_enricher = lambda action: None
    memory_observer = lambda memory: None
    event_configuration = RiftEventConfiguration(
        action_enrichers=[action_enricher],
        memory_observers=[memory_observer],
    )

    cloned = Rift._clone_rift_event_configuration(event_configuration)

    assert cloned is not event_configuration
    assert cloned._action_enrichers is not event_configuration._action_enrichers
    assert cloned._memory_observers is not event_configuration._memory_observers
    assert cloned._action_enrichers == [action_enricher]
    assert cloned._memory_observers == [memory_observer]

    rift = _create_registered_rift()
    original_names = rift.nexus_frame_names
    rift._attach_nexus_frame_name(original_names[0])

    assert rift.nexus_frame_names == original_names


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
        nexus_frame_names=("aetheric_frame_system",),
        default_nexus_frame_name="aetheric_frame_system",
        target_frame_names=tuple(),
        default_target_frame_name=None,
        active_space_id="space-explicit",
    )

    assert isinstance(rift.get_space("space-explicit"), StaticRiftSpace)
