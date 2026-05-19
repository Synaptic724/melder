from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.nexus.nexus import Nexus
from melder.nexus.nexus_frame_configuration import NexusFrameConfiguration
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.configuration.system_state import SystemState


def _reset_runtime_singletons() -> None:
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _create_enabled_nexus() -> Nexus:
    _reset_runtime_singletons()
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_target_frame_override(True)
    configuration.with_multiple_target_frames(True)
    configuration.with_max_target_frame_count(8)
    configuration.with_nexus_frame_mode("indexed")
    configuration.with_max_nexus_frame_count(8)
    nexus.enable(configuration)
    return nexus


def _create_enabled_single_nexus() -> Nexus:
    _reset_runtime_singletons()
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_nexus_frame_mode("single")
    configuration.with_max_nexus_frame_count(1)
    nexus.enable(configuration)
    return nexus


def test_nexus_frame_builder_builds_dynamic_configuration_with_root_conduit() -> None:
    nexus = _create_enabled_nexus()

    configuration = (
        nexus.frame_manager
        .begin("ops")
        .immutable(False)
        .with_root_conduit("root")
        .build()
    )

    assert configuration.frame_name == "ops"
    assert configuration.system_state == SystemState.dynamic
    assert configuration.ai_native_enabled is True
    assert configuration.rift_enabled is True
    assert configuration.root_conduit_name == "root"


def test_nexus_frame_configuration_rejects_non_dynamic_posture() -> None:
    nexus = _create_enabled_nexus()

    assert nexus is not None

    try:
        NexusFrameConfiguration(
            frame_name="ops",
            system_state=SystemState.automatic,
            ai_native_enabled=False,
            rift_enabled=True,
        )
    except ValueError as exc:
        assert "system_state=SystemState.dynamic" in str(exc)
    else:
        raise AssertionError(
            "NexusFrameConfiguration should reject automatic posture."
        )


def test_nexus_frame_manager_can_create_rooted_dynamic_conduit() -> None:
    nexus = _create_enabled_nexus()

    conduit = nexus.frame_manager.create_dynamic_frame("ops")
    descriptor = nexus._get_required_frame_descriptor("ops")

    assert conduit.name == "root"
    assert conduit._aetheric_frame == "ops"
    assert nexus.frame_manager.exists("ops") is True
    assert nexus.frame_manager.list_frame_names() == ("ops",)
    assert descriptor.frame_configuration is not None
    assert descriptor.frame_configuration.system_state == SystemState.dynamic
    assert descriptor.frame_overview is not None
    assert descriptor.frame_overview.payload.root_conduit_count == 1


def test_nexus_frame_manager_can_bootstrap_root_conduit() -> None:
    nexus = _create_enabled_nexus()

    conduit = (
        nexus.frame_manager
        .begin("ops")
        .dynamic_defaults()
        .with_root_conduit("root")
        .create()
    )
    descriptor = nexus._get_required_frame_descriptor("ops")

    assert conduit.name == "root"
    assert conduit._aetheric_frame == "ops"
    assert len(Aether()._ensure_frame("ops")._conduits) == 1
    assert descriptor.frame_overview is not None
    assert descriptor.frame_overview.payload.root_conduit_count == 1
    assert descriptor.frame_overview.payload.named_root_conduits == (
        next(iter(descriptor.frame_overview.payload.named_root_conduits)),
    )


def test_rift_create_nexus_frame_delegates_through_frame_manager() -> None:
    nexus = _create_enabled_single_nexus()
    rift = nexus.create_rift(rift_name="alpha")

    conduit = rift.create_nexus_frame()
    descriptor = nexus._get_required_frame_descriptor(conduit._aetheric_frame)

    assert conduit.name == "root"
    assert conduit._aetheric_frame == "aetheric_frame_system"
    assert nexus.frame_manager.exists(conduit._aetheric_frame) is True
    assert descriptor.frame_configuration is not None
    assert descriptor.frame_configuration.system_state == SystemState.dynamic
    assert descriptor.frame_configuration.ai_native_enabled is True
    assert descriptor.frame_configuration.rift_enabled is True
