import gc
import logging
import threading
import weakref
from types import SimpleNamespace
from typing import Dict, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.nexus.rift.rift import Rift
from melder.aether.nexus.configuration.rift_space_type import RiftSpaceType
from melder.aether.nexus.configuration.rift_configuration import RiftConfiguration
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.frame_acl_compiled_access_surface import (
    CompiledFrameACLAccessSurface,
)
from melder.aether.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.aether.nexus.frame_descriptor.frame_record import FrameRecord
from melder.aether.nexus.frame_descriptor.frame_descriptor_payload import (
    FrameDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.conduit_descriptor_payload import (
    ConduitDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.conduit_record import ConduitRecord
from melder.aether.nexus.frame_descriptor.spell_descriptor_payload import (
    SpellDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.spell_record import SpellRecord
from melder.aether.nexus.nexus import Nexus
from melder.aether.nexus.rift.frame_link.frame_link import FrameLink
from melder.aether.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from melder.aether.nexus.rift.rift_space.command_system.capability_command_system import (
    CapabilityCommandSystem,
)
from melder.aether.nexus.rift.rift_space.command_system.command_system import (
    CommandSystem,
)
from melder.aether.nexus.rift.rift_space.command_system.dynamic_command_system import (
    DynamicCommandSystem,
)
from melder.aether.nexus.rift.rift_space.command_system.static_command_system import (
    StaticCommandSystem,
)
from melder.aether.nexus.rift.rift_space.rift_event_configuration import (
    RiftEventConfiguration,
)
from melder.aether.nexus.rift.rift_space.capability_rift_space import CapabilityRiftSpace
from melder.aether.nexus.rift.rift_space.dynamic_rift_space import DynamicRiftSpace
from melder.aether.nexus.rift.rift_space.rift_space import RiftSpace
from melder.aether.nexus.rift.rift_space.static_rift_space import StaticRiftSpace
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.existence.existence import Existence


@pytest.fixture(autouse=True)
def fresh_nexus() -> None:
    """
    Reset the Nexus singleton around each test.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    _bind_target_frame_configuration(
        "default",
        rift_enabled=True,
        ai_native_enabled=False,
        system_state=SystemState.automatic,
    )
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()


def _create_enabled_nexus() -> Nexus:
    """
    Create one enabled Nexus with the minimal policy needed for the core unit
    tests.

    Returns:
        Nexus: Enabled Nexus with direct creation and direct Rift access
        allowed.
    """
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
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
    Bind one Melder frame configuration for target-frame eligibility tests.

    Args:
        frame_name:
            Target frame name to configure.
        rift_enabled:
            Whether the frame enables AI profiles.
        ai_native_enabled:
            Whether the frame enables AI-native mode.
        system_state:
            Target frame Melder system state.

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


def _seed_frame_descriptor(frame_name: str) -> None:
    """
    Seed one minimal frame descriptor overview for frame-viewer tests.

    Args:
        frame_name:
            Frame name to seed.

    Returns:
        None.
    """
    descriptor = Nexus()._get_or_create_frame_descriptor(frame_name)
    descriptor.set_frame_handle(SimpleNamespace(name=frame_name))
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


def _build_descriptor_backed_viewer(
    frame_name: str,
    *,
    command_frame_enabled: bool = True,
    enabled_conduit_ids: Tuple[str, ...] = tuple(),
    enabled_spell_index_ids: Tuple[str, ...] = tuple(),
) -> FrameViewer:
    """
    Build one minimal descriptor-backed viewer for RiftSpace host tests.

    Args:
        frame_name:
            Hosted frame name.
        command_frame_enabled:
            Whether frame-level command access is enabled in the compiled ACL
            surface.
        enabled_conduit_ids:
            Command-enabled conduit ids for the hosted frame.
        enabled_spell_index_ids:
            Command-enabled spell lineage ids for the hosted frame.

    Returns:
        FrameViewer: Descriptor-backed viewer with one visible frame target.
    """
    _seed_frame_descriptor(frame_name)
    descriptor: FrameDescriptor = Nexus()._get_required_frame_descriptor(frame_name)
    frame_acl_configuration = FrameACLConfiguration.create_default(frame_name)
    compiled_access_surface = CompiledFrameACLAccessSurface(
        frame_name=frame_name,
        configuration_id=frame_acl_configuration.configuration_id,
        view_profile_name=frame_acl_configuration.view_configuration.profile_name,
        view_profile_version=frame_acl_configuration.view_configuration.profile_version,
        codegen_profile_name=frame_acl_configuration.codegen_configuration.profile_name,
        codegen_profile_version=frame_acl_configuration.codegen_configuration.profile_version,
        command_frame_enabled=command_frame_enabled,
        allowed_kinds=("frame",),
        allowed_commands=("query",),
        frame_payload_fields=("system_state", "rift_enabled"),
        visible_conduit_ids=tuple(),
        visible_spell_keys=tuple(),
        visible_spell_index_ids=tuple(),
        enabled_conduit_ids=enabled_conduit_ids,
        enabled_spell_index_ids=enabled_spell_index_ids,
        conduit_payload_sections_by_id={},
        spell_payload_sections_by_key={},
        metadata={"visible_spell_count": 0},
    )
    return FrameViewer(
        frame_descriptors_by_name={frame_name: descriptor},
        frame_acl_configurations_by_frame_name={
            frame_name: frame_acl_configuration,
        },
        compiled_access_surfaces_by_frame_name={
            frame_name: compiled_access_surface,
        },
        default_view_frame_name=frame_name,
    )


def _replace_compiled_access_surface(
    viewer: FrameViewer,
    frame_name: str,
    *,
    command_frame_enabled: bool,
    enabled_conduit_ids: Tuple[str, ...] = tuple(),
    enabled_spell_index_ids: Tuple[str, ...] = tuple(),
) -> None:
    """
    Replace one hosted compiled ACL surface with updated command-enablement data.

    Args:
        viewer:
            Hosted frame viewer whose compiled surface should be replaced.
        frame_name:
            Hosted frame name whose surface should be replaced.
        command_frame_enabled:
            Whether frame-level command access is enabled.
        enabled_conduit_ids:
            Command-enabled conduit ids for the frame.
        enabled_spell_index_ids:
            Command-enabled spell lineage ids for the frame.

    Returns:
        None.
    """
    compiled_access_surface = viewer._get_required_compiled_access_surface(frame_name)
    viewer._compiled_access_surfaces_by_frame_name[frame_name] = (
        CompiledFrameACLAccessSurface(
            frame_name=compiled_access_surface.frame_name,
            configuration_id=compiled_access_surface.configuration_id,
            view_profile_name=compiled_access_surface.view_profile_name,
            view_profile_version=compiled_access_surface.view_profile_version,
            codegen_profile_name=compiled_access_surface.codegen_profile_name,
            codegen_profile_version=compiled_access_surface.codegen_profile_version,
            command_frame_enabled=command_frame_enabled,
            allowed_kinds=compiled_access_surface.allowed_kinds,
            allowed_commands=compiled_access_surface.allowed_commands,
            frame_payload_fields=compiled_access_surface.frame_payload_fields,
            visible_conduit_ids=compiled_access_surface.visible_conduit_ids,
            visible_spell_keys=compiled_access_surface.visible_spell_keys,
            visible_spell_index_ids=compiled_access_surface.visible_spell_index_ids,
            enabled_conduit_ids=enabled_conduit_ids,
            enabled_spell_index_ids=enabled_spell_index_ids,
            conduit_payload_sections_by_id=(
                compiled_access_surface.conduit_payload_sections_by_id
            ),
            spell_payload_sections_by_key=(
                compiled_access_surface.spell_payload_sections_by_key
            ),
            metadata=compiled_access_surface.metadata,
        )
    )


def test_nexus_is_singleton() -> None:
    """
    Verify `Nexus` enforces the singleton contract.

    Returns:
        None.
    """
    first = Nexus()
    second = Nexus()

    assert first is second


def test_nexus_cold_start_requires_aether_and_does_not_publish_singleton() -> None:
    """
    Verify a cold Nexus bootstrap fails without `Aether` and leaves no
    half-published singleton behind.

    Returns:
        None.
    """
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()

    with pytest.raises(ValueError, match="Aether must be provided to initialize Nexus."):
        Nexus()

    assert Nexus._instance is None
    assert Nexus._initialized is False

    aether = Aether()
    nexus = Nexus()

    assert aether._nexus is nexus
    assert Nexus._instance is nexus
    assert Nexus._initialized is True


def test_nexus_uses_registered_channel_logger_provider() -> None:
    """
    Verify Nexus resolves its default logger through the hosted provider.

    Returns:
        None.
    """
    created_for = []

    def resolver(*, registrant: object, groups=None, system_groups=None, props=None, channels=None) -> logging.Logger:
        """
        Provide a stable stdlib logger and record the requesting object.

        Args:
            registrant:
                Object requesting a logger.

        Returns:
            logging.Logger: Logger instance for the registrant.
        """
        created_for.append(registrant)
        return logging.getLogger("nexus-provider.{0}".format(registrant.__class__.__name__))

    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem().register_channel_logger_resolver(resolver)
    _bind_target_frame_configuration(
        "default",
        rift_enabled=True,
        ai_native_enabled=False,
        system_state=SystemState.automatic,
    )

    aether = Aether()
    nexus = Nexus()

    assert aether._nexus is nexus
    assert any(isinstance(obj, Nexus) for obj in created_for)
    assert nexus._logger is not None
    assert nexus._logger._logger is not None


def test_nexus_default_logger_metadata_is_rich_and_stable() -> None:
    """
    Verify the default Nexus logger resolver receives the expected stable
    metadata.

    Returns:
        None.
    """
    captured_args = []

    def resolver(*, registrant: object, groups=None, system_groups=None, props=None, channels=None) -> logging.Logger:
        """
        Capture the logger metadata requested by Nexus.

        Args:
            registrant:
                Object requesting a logger.
            groups:
                Requested logger groups.
            system_groups:
                Requested logger system groups.
            props:
                Requested logger properties.
            channels:
                Requested logger channels.

        Returns:
            logging.Logger: Stable stdlib logger for the request.
        """
        captured_args.append(
            {
                "registrant": registrant,
                "groups": groups,
                "system_groups": system_groups,
                "props": props,
                "channels": channels,
            }
        )
        return logging.getLogger("nexus-provider.metadata")

    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    AetherUtilitySystem().register_channel_logger_resolver(resolver)
    _bind_target_frame_configuration(
        "default",
        rift_enabled=True,
        ai_native_enabled=False,
        system_state=SystemState.automatic,
    )

    nexus = Nexus()
    nexus_calls = [
        captured_call
        for captured_call in captured_args
        if captured_call["registrant"] is nexus
    ]

    assert len(nexus_calls) == 1
    assert nexus_calls[0]["groups"] == ["nexus", "lifecycle", "registry"]
    assert nexus_calls[0]["system_groups"] == ["nexus", "aether", "rift"]
    assert nexus_calls[0]["channels"] == "system"
    assert nexus_calls[0]["props"] == {
        "component": "nexus",
        "component_id": nexus.id,
        "singleton": True,
    }


def test_nexus_explicit_logger_override_is_used() -> None:
    """
    Verify an explicit Nexus logger override replaces the provider default.

    Returns:
        None.
    """
    explicit_logger = logging.getLogger("nexus-explicit")

    Aether()
    nexus = Nexus(logger=explicit_logger)

    assert nexus._logger._logger is explicit_logger


def test_nexus_starts_unconfigured_and_disabled() -> None:
    """
    Verify Nexus starts unconfigured and disabled.

    Returns:
        None.
    """
    nexus = Nexus()

    assert nexus.is_configured is False
    assert nexus.is_enabled is False
    with pytest.raises(RuntimeError, match="not configured"):
        _ = nexus.configuration


def test_create_rift_requires_enabled_nexus() -> None:
    """
    Verify Rift creation is blocked while Nexus is disabled.

    Returns:
        None.
    """
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    nexus.enable(configuration)
    nexus.disable()

    with pytest.raises(RuntimeError, match="disabled"):
        nexus.create_rift(rift_name="alpha")


def test_create_rift_requires_creation_permission() -> None:
    """
    Verify enabling Nexus alone does not open Rift creation.

    Returns:
        None.
    """
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(False)
    nexus.enable(configuration)

    with pytest.raises(ValueError, match="creation is disabled"):
        nexus.create_rift(rift_name="alpha")


def test_create_rift_registers_live_rift_after_enable() -> None:
    """
    Verify an enabled Nexus can create and register a live Rift.

    Returns:
        None.
    """
    nexus = _create_enabled_nexus()
    rift = nexus.create_rift(rift_name="alpha")

    assert nexus.has_rift(rift.id) is True
    assert rift.is_registered is True
    assert rift.is_active is True
    assert rift.default_nexus_frame_name == "aetheric_frame_system"
    assert rift.nexus_frame_names == ("aetheric_frame_system",)
    assert rift.target_frame_names == tuple()
    assert rift.default_target_frame_name is None
    assert len(rift.list_space_ids()) == 1
    assert isinstance(rift.get_space(rift.active_space_id), StaticRiftSpace)
    assert nexus.get_rift(rift.id) is rift
    assert nexus.get_rift_by_name("alpha") is rift
    assert nexus.list_rift_ids() == [rift.id]

    rift_id = rift.id
    nexus.remove_rift(rift_id)
    assert nexus.has_rift(rift_id) is False


def test_create_rift_uses_registered_channel_logger_provider() -> None:
    """
    Verify Rift resolves its default logger through the hosted provider.

    Returns:
        None.
    """
    created_for = []

    def resolver(*, registrant: object, groups=None, system_groups=None, props=None, channels=None) -> logging.Logger:
        """
        Provide a stable stdlib logger and record the requesting object.

        Args:
            registrant:
                Object requesting a logger.

        Returns:
            logging.Logger: Logger instance for the registrant.
        """
        created_for.append(registrant)
        return logging.getLogger("rift-provider.{0}".format(registrant.__class__.__name__))

    AetherUtilitySystem().register_channel_logger_resolver(resolver)

    nexus = _create_enabled_nexus()
    rift = nexus.create_rift(rift_name="alpha")

    assert any(isinstance(obj, Rift) for obj in created_for)
    assert rift._logger is not None
    assert rift._logger._logger is not None


def test_create_rift_explicit_logger_override_is_used() -> None:
    """
    Verify an explicit Rift logger override is preserved on creation.

    Returns:
        None.
    """
    nexus = _create_enabled_nexus()
    explicit_logger = logging.getLogger("rift-explicit")

    rift = nexus.create_rift(rift_name="alpha", logger=explicit_logger)

    assert rift._logger._logger is explicit_logger


def test_unnamed_rifts_receive_deterministic_default_names() -> None:
    """
    Verify unnamed Rifts receive deterministic Nexus-owned default names.

    Returns:
        None.
    """
    nexus = _create_enabled_nexus()

    first = nexus.create_rift()
    second = nexus.create_rift()

    assert first.rift_name == "nexus_rift_1"
    assert second.rift_name == "nexus_rift_2"


def test_default_rift_name_allocator_skips_existing_names() -> None:
    """
    Verify the default Rift-name allocator skips already-registered names and
    advances the stored incrementer.

    Returns:
        None.
    """
    nexus = _create_enabled_nexus()
    nexus._rift_ids_by_name["nexus_rift_1"] = "rift-occupied-1"
    nexus._rift_ids_by_name["nexus_rift_2"] = "rift-occupied-2"
    nexus._next_default_rift_number = 1

    allocated_name = nexus._allocate_default_rift_name()

    assert allocated_name == "nexus_rift_3"
    assert nexus._next_default_rift_number == 4


def test_default_rift_name_allocator_fails_when_bounded_probe_is_exhausted() -> None:
    """
    Verify the default Rift-name allocator fails fast instead of looping
    forever when the bounded probe cannot find a free name.

    Returns:
        None.
    """
    nexus = _create_enabled_nexus()

    class AlwaysTakenNameMap(dict):
        """
        Force the allocator down the bounded failure path for unit coverage.
        """

        def __contains__(self, key) -> bool:
            return True

    nexus._rift_ids_by_name = AlwaysTakenNameMap({"nexus_rift_1": "rift-1"})
    nexus._next_default_rift_number = 1

    with pytest.raises(RuntimeError, match="Failed to allocate a deterministic default Rift name"):
        nexus._allocate_default_rift_name()


def test_create_rift_consumes_configuration_after_success() -> None:
    """
    Verify a `RiftConfiguration` is single-use and cannot be reused after
    successful Rift creation.

    Returns:
        None.
    """
    nexus = _create_enabled_nexus()
    configuration = nexus.create_rift_configuration()
    rift = nexus.create_rift(configuration=configuration, rift_name="alpha")

    assert configuration.consumed is True
    assert rift.configuration is configuration

    with pytest.raises(ValueError, match="already been consumed"):
        nexus.create_rift(configuration=configuration, rift_name="beta")


def test_create_rift_configuration_uses_nexus_defaults() -> None:
    """
    Verify per-Rift configuration derives from the installed Nexus defaults.

    Returns:
        None.
    """
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    nexus.enable(configuration)
    config = nexus.create_rift_configuration()

    assert config.get_property("space_type") == RiftSpaceType.static
    assert config.get_property("space_name") is None
    assert config.get_property("auto_activate_on_program") is True
    assert config.get_property("validation_mode") is not None


def test_create_rift_configuration_can_clone_registered_profile() -> None:
    """
    Verify Nexus can register a named profile template and return fresh cloned
    `RiftConfiguration` objects from it.

    Returns:
        None.
    """
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    nexus.enable(configuration)

    profile = nexus.create_rift_configuration()
    profile.with_space_type(RiftSpaceType.dynamic)
    profile.with_space_name("ops-room")
    nexus.register_rift_profile("ops_profile", profile)

    profiled_configuration = nexus.create_rift_configuration(profile_name="ops_profile")
    second_profiled_configuration = nexus.create_rift_configuration(profile_name="ops_profile")

    assert profiled_configuration is not second_profiled_configuration
    assert profiled_configuration.get_property("space_type") == RiftSpaceType.dynamic
    assert profiled_configuration.get_property("space_name") == "ops-room"
    assert profiled_configuration.consumed is False
    assert second_profiled_configuration.consumed is False


def test_register_rift_profile_replaces_existing_template_and_cleans_old_clone() -> None:
    """
    Verify replacing a Rift profile cleans the displaced stored template.

    Returns:
        None.
    """
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    nexus.enable(configuration)

    first_profile = nexus.create_rift_configuration().with_space_name("ops-room")
    second_profile = nexus.create_rift_configuration().with_space_name("finance-room")

    nexus.register_rift_profile("ops_profile", first_profile)
    first_stored_template = nexus._rift_profiles_by_name["ops_profile"]
    nexus.register_rift_profile("ops_profile", second_profile)

    second_stored_template = nexus._rift_profiles_by_name["ops_profile"]

    assert first_stored_template.cleaned is True
    assert second_stored_template is not second_profile
    assert second_stored_template.get_property("space_name") == "finance-room"
    assert second_stored_template.frozen is True


def test_create_rift_configuration_profile_clone_detaches_event_configuration() -> None:
    """
    Verify Rift profile clones detach nested room-event configuration objects.

    Returns:
        None.
    """
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    nexus.enable(configuration)

    action_enricher = lambda action: None
    memory_observer = lambda memory: None
    event_configuration = RiftEventConfiguration(
        action_enrichers=[action_enricher],
        memory_observers=[memory_observer],
    )
    profile = nexus.create_rift_configuration().with_event_configuration(
        event_configuration
    )
    nexus.register_rift_profile("ops_profile", profile)

    first_clone = nexus.create_rift_configuration(profile_name="ops_profile")
    second_clone = nexus.create_rift_configuration(profile_name="ops_profile")
    first_event_configuration = first_clone.get_property("event_configuration")
    second_event_configuration = second_clone.get_property("event_configuration")

    assert first_event_configuration is not event_configuration
    assert second_event_configuration is not event_configuration
    assert first_event_configuration is not second_event_configuration
    assert first_event_configuration._action_enrichers is not event_configuration._action_enrichers
    assert first_event_configuration._memory_observers is not event_configuration._memory_observers
    assert first_event_configuration._action_enrichers == [action_enricher]
    assert second_event_configuration._memory_observers == [memory_observer]


def test_create_rift_programs_primary_space_from_space_type() -> None:
    """
    Verify Rift creation programs one primary space from the chosen space type.

    Returns:
        None.
    """
    nexus = _create_enabled_nexus()
    static_rift = nexus.create_rift(rift_name="alpha")
    capability_configuration = nexus.create_rift_configuration().with_space_type(
        RiftSpaceType.capability
    )
    capability_rift = nexus.create_rift(
        configuration=capability_configuration,
        rift_name="gamma",
    )
    dynamic_configuration = nexus.create_rift_configuration().with_space_type(
        RiftSpaceType.dynamic
    )
    dynamic_rift = nexus.create_rift(
        configuration=dynamic_configuration,
        rift_name="beta",
    )

    assert len(static_rift.list_space_ids()) == 1
    assert isinstance(static_rift.get_space(static_rift.active_space_id), StaticRiftSpace)
    assert len(capability_rift.list_space_ids()) == 1
    assert isinstance(
        capability_rift.get_space(capability_rift.active_space_id),
        CapabilityRiftSpace,
    )
    assert len(dynamic_rift.list_space_ids()) == 1
    assert isinstance(dynamic_rift.get_space(dynamic_rift.active_space_id), DynamicRiftSpace)


def test_rift_space_can_attach_and_detach_frame_viewer() -> None:
    """
    Verify a RiftSpace can own an attached frame viewer.

    Returns:
        None.
    """
    space = RiftSpace(owner_rift_id="rift-1", space_name="main")
    viewer = FrameViewer()

    space.attach_frame_viewer(viewer)

    assert space.frame_viewer is viewer

    space.detach_frame_viewer()

    assert viewer.cleaned is True
    assert space.frame_viewer is None


def test_rift_space_owns_workstation_canvas() -> None:
    """
    Verify a RiftSpace owns a live workstation canvas.

    Returns:
        None.
    """
    space = RiftSpace(owner_rift_id="rift-1", space_name="main")

    assert space.workstation.owner_space_id == space.space_id
    assert space.workstation.describe_bindings() == {
        "objects": [],
        "attributes": [],
        "methods": [],
        "target_name": [],
        "target_store": [],
    }


def test_workstation_can_bind_select_release_and_describe() -> None:
    """
    Verify the workstation stores bindings, tracks targets, and releases bindings.

    Returns:
        None.
    """
    space = RiftSpace(owner_rift_id="rift-1", space_name="main")
    workstation = space.workstation
    marker = object()

    workstation.bind_object("client", marker)
    workstation.bind_attribute("status", "ready")
    workstation.bind_method("runner", lambda: "ok")
    workstation.set_target("client", store="objects")

    assert workstation.get("client", store="objects") is marker
    assert workstation.get_target() is marker
    assert workstation.describe_bindings() == {
        "objects": ["client"],
        "attributes": ["status"],
        "methods": ["runner"],
        "target_name": ["client"],
        "target_store": ["objects"],
    }

    released = workstation.release("client", store="objects")

    assert released is marker
    assert workstation.describe_bindings() == {
        "objects": [],
        "attributes": ["status"],
        "methods": ["runner"],
        "target_name": [],
        "target_store": [],
    }


def test_workstation_call_target_can_bind_return_value() -> None:
    """
    Verify the workstation can call the active target and bind the result.

    Returns:
        None.
    """
    space = RiftSpace(owner_rift_id="rift-1", space_name="main")
    workstation = space.workstation

    workstation.bind_method("builder", lambda prefix: {"value": prefix})
    workstation.set_target("builder", store="methods")

    result = workstation.call_target(
        "ops",
        bind_as_name="payload",
        bind_as_store="attributes",
    )

    assert result == {"value": "ops"}
    assert workstation.get("payload", store="attributes") == {"value": "ops"}


def test_workstation_explicit_strong_binding_keeps_object_alive() -> None:
    """
    Verify explicit strong binding keeps one object alive even after local references are dropped.

    Returns:
        None.
    """
    class _Target:
        pass

    space = RiftSpace(owner_rift_id="rift-1", space_name="main", space_kind="static")
    workstation = space.workstation
    target = _Target()
    target_ref = weakref.ref(target)

    workstation.bind_object("client", target, weak_ref=False)
    del target
    gc.collect()

    assert target_ref() is not None
    assert workstation.get("client", store="objects") is target_ref()


def test_workstation_explicit_weak_binding_releases_object_after_collection() -> None:
    """
    Verify explicit weak binding does not keep one object alive after local references are dropped.

    Returns:
        None.
    """
    class _Target:
        pass

    space = RiftSpace(owner_rift_id="rift-1", space_name="main", space_kind="capability")
    workstation = space.workstation
    target = _Target()
    target_ref = weakref.ref(target)

    workstation.bind_object("client", target, weak_ref=True)
    del target
    gc.collect()

    assert target_ref() is None
    with pytest.raises(ValueError, match="was not found"):
        workstation.get("client", store="objects")


def test_workstation_static_room_defaults_none_to_weak_binding() -> None:
    """
    Verify `weak_ref=None` resolves to weak binding in static rooms.

    Returns:
        None.
    """
    class _Target:
        pass

    space = RiftSpace(owner_rift_id="rift-1", space_name="main", space_kind="static")
    workstation = space.workstation
    target = _Target()
    target_ref = weakref.ref(target)

    workstation.bind_object("client", target)
    del target
    gc.collect()

    assert target_ref() is None
    with pytest.raises(ValueError, match="was not found"):
        workstation.get("client", store="objects")


def test_workstation_capability_room_defaults_none_to_strong_binding() -> None:
    """
    Verify `weak_ref=None` resolves to strong binding in capability rooms.

    Returns:
        None.
    """
    class _Target:
        pass

    space = RiftSpace(
        owner_rift_id="rift-1",
        space_name="main",
        space_kind="capability",
    )
    workstation = space.workstation
    target = _Target()
    target_ref = weakref.ref(target)

    workstation.bind_object("client", target)
    del target
    gc.collect()

    assert target_ref() is not None
    assert workstation.get("client", store="objects") is target_ref()


def test_workstation_weak_binding_raises_for_non_weakrefable_value() -> None:
    """
    Verify explicit weak binding fails fast for values that cannot be weak-referenced.

    Returns:
        None.
    """
    space = RiftSpace(owner_rift_id="rift-1", space_name="main", space_kind="static")

    with pytest.raises(TypeError, match="support weak references"):
        space.workstation.bind_attribute("count", 3, weak_ref=True)


def test_rift_space_queues_weak_binding_collection_events() -> None:
    """
    Verify weak binding collection publishes one room-local queue event.

    Returns:
        None.
    """
    class _Target:
        pass

    space = RiftSpace(owner_rift_id="rift-1", space_name="main", space_kind="static")
    workstation = space.workstation
    target = _Target()

    workstation.bind_object("client", target, weak_ref=True)
    del target
    gc.collect()

    queued_events = space.describe_event_queue()

    assert len(queued_events) == 1
    assert queued_events[0]["event_type"] == "binding_collected"
    assert queued_events[0]["binding_name"] == "client"
    assert queued_events[0]["binding_store"] == "objects"
    assert queued_events[0]["space_id"] == space.space_id
    assert queued_events[0]["space_kind"] == "static"


def test_rift_space_can_manage_event_queue_with_optional_thread() -> None:
    """
    Verify the optional managed queue consumer drains published weak-binding events.

    Returns:
        None.
    """
    class _Target:
        pass

    space = RiftSpace(owner_rift_id="rift-1", space_name="main", space_kind="static")
    received_events = []
    handled_event = threading.Event()

    def _handler(event_payload: Dict[str, object]) -> None:
        received_events.append(event_payload)
        handled_event.set()

    space.manage_event_queue(_handler, poll_interval_seconds=0.01, drain_batch_size=4)
    target = _Target()
    space.workstation.bind_object("client", target, weak_ref=True)
    del target
    gc.collect()

    assert handled_event.wait(1.0) is True
    space.stop_managing_event_queue()

    assert len(received_events) == 1
    assert received_events[0]["event_type"] == "binding_collected"


def test_rift_space_stop_managing_event_queue_is_idempotent() -> None:
    """
    Verify stopping the managed queue thread is safe when no thread is active.

    Returns:
        None.
    """
    space = RiftSpace(owner_rift_id="rift-1", space_name="main")

    space.stop_managing_event_queue()
    space.stop_managing_event_queue()

    assert space.describe_event_queue() == []


def test_workstation_cleanup_target_calls_methods_then_clears_target() -> None:
    """
    Verify cleanup_target calls the requested cleanup methods then clears target selection.

    Returns:
        None.
    """
    class _Disposable:
        def __init__(self) -> None:
            self.calls = []

        def stop(self) -> None:
            self.calls.append("stop")

        def cleanup(self) -> None:
            self.calls.append("cleanup")

    space = RiftSpace(owner_rift_id="rift-1", space_name="main")
    workstation = space.workstation
    disposable = _Disposable()

    workstation.bind_object("job", disposable)
    workstation.set_target("job", store="objects")
    workstation.cleanup_target("stop", "cleanup")

    assert disposable.calls == ["stop", "cleanup"]
    assert workstation.describe_bindings()["target_name"] == []


def test_workstation_and_space_cleanup_are_integrated() -> None:
    """
    Verify RiftSpace cleanup cascades into the owned workstation.

    Returns:
        None.
    """
    space = RiftSpace(owner_rift_id="rift-1", space_name="main")
    workstation = space.workstation
    command_system = space.command_system
    workstation.bind_attribute("status", "ready")

    space.cleanup()

    assert workstation.cleaned is True
    assert command_system.cleaned is True


def test_rift_space_owns_command_system() -> None:
    """
    Verify a RiftSpace owns a live command system.

    Returns:
        None.
    """
    space = RiftSpace(owner_rift_id="rift-1", space_name="main")

    assert space.command_system.owner_space_id == space.space_id


def test_base_rift_space_composes_generic_command_system() -> None:
    """
    Verify the base room composes the shared generic command system.

    Returns:
        None.
    """
    space = RiftSpace(owner_rift_id="rift-1", space_name="main")

    assert isinstance(space.command_system, CommandSystem)
    assert not isinstance(space.command_system, StaticCommandSystem)
    assert not isinstance(space.command_system, CapabilityCommandSystem)
    assert not isinstance(space.command_system, DynamicCommandSystem)


def test_static_rift_space_composes_static_command_system() -> None:
    """
    Verify static rooms compose the static command system variant.

    Returns:
        None.
    """
    space = StaticRiftSpace(owner_rift_id="rift-1", space_name="main")

    assert isinstance(space.command_system, StaticCommandSystem)


def test_capability_rift_space_composes_capability_command_system() -> None:
    """
    Verify capability rooms compose the capability command system variant.

    Returns:
        None.
    """
    space = CapabilityRiftSpace(owner_rift_id="rift-1", space_name="main")

    assert isinstance(space.command_system, CapabilityCommandSystem)


def test_dynamic_rift_space_composes_dynamic_command_system() -> None:
    """
    Verify dynamic rooms compose the dynamic command system variant.

    Returns:
        None.
    """
    space = DynamicRiftSpace(owner_rift_id="rift-1", space_name="main")

    assert isinstance(space.command_system, DynamicCommandSystem)


def test_command_system_can_get_selected_target_link_and_record() -> None:
    """
    Verify the command system resolves the single selected viewer target link and record.

    Returns:
        None.
    """
    space = RiftSpace(owner_rift_id="rift-1", space_name="main")
    viewer = _build_descriptor_backed_viewer("ops")
    space.attach_frame_viewer(viewer)
    frame_link = viewer.execute_method("list_targets")[0]
    space.select_target(frame_link.link_id)

    selected_link = space.command_system.get_selected_target_link()
    selected_record = space.command_system.get_selected_target_record()

    assert selected_link.link_id == frame_link.link_id
    assert selected_link.source_kind == frame_link.source_kind
    assert selected_link.source_id == frame_link.source_id
    assert selected_record.frame_name == "ops"
    assert selected_record.frame_id == "ops-frame"


def test_command_system_can_get_selected_target_runtime_object_for_frame() -> None:
    """
    Verify the command system can resolve the live frame object for a selected frame target.

    Returns:
        None.
    """
    space = RiftSpace(owner_rift_id="rift-1", space_name="main")
    viewer = _build_descriptor_backed_viewer("ops")
    space.attach_frame_viewer(viewer)
    frame_link = viewer.execute_method("list_targets")[0]
    space.select_target(frame_link.link_id)

    frame_handle = space.command_system.get_selected_target_runtime_object()

    assert frame_handle.name == "ops"


def test_command_system_selected_target_requires_one_selection() -> None:
    """
    Verify selected-target getters fail fast when no target is selected.

    Returns:
        None.
    """
    space = RiftSpace(owner_rift_id="rift-1", space_name="main")
    viewer = _build_descriptor_backed_viewer("ops")
    space.attach_frame_viewer(viewer)

    with pytest.raises(ValueError, match="has no selected target"):
        space.command_system.get_selected_target_link()


def test_command_system_can_get_target_attribute_and_method() -> None:
    """
    Verify the command system reads attributes and methods from the current workstation target.

    Returns:
        None.
    """
    class _Target:
        def __init__(self) -> None:
            self.status = "ready"

        def run(self) -> str:
            return "ok"

    space = RiftSpace(owner_rift_id="rift-1", space_name="main")
    workstation = space.workstation
    target = _Target()
    workstation.bind_object("target", target)
    workstation.set_target("target", store="objects")

    method = space.command_system.get_target_method("run")

    assert space.command_system.get_target_attribute("status") == "ready"
    assert callable(method) is True
    assert method() == "ok"


def test_command_system_execute_target_method_can_bind_result() -> None:
    """
    Verify the command system can execute a method on the workstation target and bind the result.

    Returns:
        None.
    """
    class _Target:
        def run(self, prefix: str) -> str:
            return "{0}-done".format(prefix)

    space = RiftSpace(owner_rift_id="rift-1", space_name="main")
    workstation = space.workstation
    target = _Target()
    workstation.bind_object("target", target)
    workstation.set_target("target", store="objects")

    result = space.command_system.execute_target_method(
        "run",
        "ops",
        bind_as_name="status",
        bind_as_store="attributes",
    )

    assert result == "ops-done"
    assert workstation.get("status", store="attributes") == "ops-done"


def test_command_system_can_get_conduit_object_by_id_with_lesser_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify conduit lookup falls back to lesser-conduit lineage traversal when root lookup misses.

    Returns:
        None.
    """
    space = RiftSpace(owner_rift_id="rift-1", space_name="main")
    viewer = _build_descriptor_backed_viewer("ops")
    _replace_compiled_access_surface(
        viewer,
        "ops",
        command_frame_enabled=True,
        enabled_conduit_ids=("lesser-1",),
    )
    space.attach_frame_viewer(viewer)
    sentinel = object()
    root_conduit = SimpleNamespace(
        _conduit_ward=SimpleNamespace(
            _get_lesser_conduit=lambda conduit_id: sentinel,
        )
    )
    aether_stub = SimpleNamespace(
        _get_conduit_by_id=lambda conduit_id, frame_name: (_ for _ in ()).throw(
            ValueError("missing")
        ),
        _aetheric_frames={
            "ops": SimpleNamespace(
                _conduits={"root-1": root_conduit},
            )
        },
    )
    monkeypatch.setattr(
        type(space.command_system),
        "_aether",
        aether_stub,
    )

    result = space.command_system.get_conduit_object_by_id(
        "lesser-1",
        frame_name="ops",
    )

    assert result is sentinel


def test_command_system_can_get_spell_object_by_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify spell lookup resolves through the owning conduit and spellbook.

    Returns:
        None.
    """
    space = RiftSpace(owner_rift_id="rift-1", space_name="main")
    viewer = _build_descriptor_backed_viewer("ops")
    descriptor = viewer._get_required_frame_descriptor("ops")
    descriptor.upsert_conduit_record(
        ConduitRecord(
            conduit_id="ops-conduit",
            root_conduit_id="ops-conduit",
            frame_name="ops",
            origin_spellbook_id="ops-spellbook",
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
            origin_spellbook_id="ops-spellbook",
            frame_name="ops",
            owner_conduit_id="ops-conduit",
            spell_id="sha-1",
            spell_index_id="lineage-1",
            spell_name="OpsSpell",
            spellframe=None,
            binding_name="ops_spell",
            permissions=Permissions.create,
            existence=Existence.unique,
            payload=SpellDescriptorPayload(
                payload_type="detailed",
                binding_payload={"kind": "class"},
                resolution_payload={"requirements": []},
                class_profile=None,
                callable_profile=None,
                metadata={},
                instance_members={},
                dynamic_access={},
            ),
        )
    )
    _replace_compiled_access_surface(
        viewer,
        "ops",
        command_frame_enabled=True,
        enabled_spell_index_ids=("lineage-1",),
    )
    space.attach_frame_viewer(viewer)
    spell = object()

    class _SpellIndex:
        def has_version(self, version_id: str) -> bool:
            return version_id == "sha-1"

    owner_conduit = SimpleNamespace(
        _spellbook=SimpleNamespace(
            _spells={_SpellIndex(): spell},
        )
    )
    aether_stub = SimpleNamespace(
        _get_conduit_by_spell_id=lambda spell_id, frame_name: owner_conduit,
    )
    monkeypatch.setattr(
        type(space.command_system),
        "_aether",
        aether_stub,
    )

    result = space.command_system.get_spell_object_by_id(
        "sha-1",
        frame_name="ops",
    )

    assert result is spell


def test_command_system_can_get_spell_object_by_index_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify spell lookup resolves through spell_index_id using descriptor owner records.

    Returns:
        None.
    """
    space = RiftSpace(owner_rift_id="rift-1", space_name="main")
    viewer = _build_descriptor_backed_viewer("ops")
    descriptor = viewer._get_required_frame_descriptor("ops")
    descriptor.upsert_conduit_record(
        ConduitRecord(
            conduit_id="ops-conduit",
            root_conduit_id="ops-conduit",
            frame_name="ops",
            origin_spellbook_id="ops-spellbook",
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
            origin_spellbook_id="ops-spellbook",
            frame_name="ops",
            owner_conduit_id="ops-conduit",
            spell_id="sha-1",
            spell_index_id="lineage-1",
            spell_name="OpsSpell",
            spellframe=None,
            binding_name="ops_spell",
            permissions=Permissions.create,
            existence=Existence.unique,
            payload=SpellDescriptorPayload(
                payload_type="detailed",
                binding_payload={"kind": "class"},
                resolution_payload={"requirements": []},
                class_profile=None,
                callable_profile=None,
                metadata={},
                instance_members={},
                dynamic_access={},
            ),
        )
    )
    _replace_compiled_access_surface(
        viewer,
        "ops",
        command_frame_enabled=True,
        enabled_spell_index_ids=("lineage-1",),
    )
    space.attach_frame_viewer(viewer)
    spell = object()
    owner_conduit = SimpleNamespace(
        get_spell_by_index_id=lambda spell_index_id: (
            spell if spell_index_id == "lineage-1" else None
        )
    )
    monkeypatch.setattr(
        type(space.command_system),
        "get_conduit_object_by_id",
        lambda self, conduit_id, *, frame_name=None: owner_conduit,
    )

    result = space.command_system.get_spell_object_by_index_id(
        "lineage-1",
        frame_name="ops",
    )

    assert result is spell


def test_command_system_denies_selected_target_link_when_frame_command_disabled() -> None:
    """
    Verify selected-target access fails fast when frame command access is disabled.

    Returns:
        None.
    """
    space = RiftSpace(owner_rift_id="rift-1", space_name="main")
    viewer = _build_descriptor_backed_viewer(
        "ops",
        command_frame_enabled=False,
    )
    space.attach_frame_viewer(viewer)
    frame_link = viewer.execute_method("list_targets", frame_name="ops")[0]
    space.select_target(frame_link.link_id)

    with pytest.raises(ValueError, match="Command access is disabled for frame 'ops'"):
        space.command_system.get_selected_target_link()


def test_command_system_denies_conduit_object_by_id_when_conduit_acl_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify direct conduit access fails fast when the conduit is not command-enabled.

    Returns:
        None.
    """
    space = RiftSpace(owner_rift_id="rift-1", space_name="main")
    viewer = _build_descriptor_backed_viewer("ops")
    descriptor = viewer._get_required_frame_descriptor("ops")
    descriptor.upsert_conduit_record(
        ConduitRecord(
            conduit_id="ops-conduit",
            root_conduit_id="ops-conduit",
            frame_name="ops",
            origin_spellbook_id="ops-spellbook",
            payload=ConduitDescriptorPayload(
                conduit_name="root",
                conduit_state=ConduitState.normal,
                policy=Policies.default,
                peer_conduit_ids=tuple(),
            ),
        )
    )
    _replace_compiled_access_surface(
        viewer,
        "ops",
        command_frame_enabled=True,
        enabled_conduit_ids=tuple(),
    )
    space.attach_frame_viewer(viewer)
    monkeypatch.setattr(
        type(space.command_system),
        "_aether",
        SimpleNamespace(_get_conduit_by_id=lambda conduit_id, frame_name: object()),
    )

    with pytest.raises(
        ValueError,
        match="Command access to conduit 'ops-conduit' is disabled in frame 'ops'",
    ):
        space.command_system.get_conduit_object_by_id("ops-conduit", frame_name="ops")


def test_command_system_denies_spell_object_by_index_id_when_spell_acl_disabled() -> None:
    """
    Verify direct spell access fails fast when the spell lineage is not command-enabled.

    Returns:
        None.
    """
    space = RiftSpace(owner_rift_id="rift-1", space_name="main")
    viewer = _build_descriptor_backed_viewer("ops")
    descriptor = viewer._get_required_frame_descriptor("ops")
    descriptor.upsert_conduit_record(
        ConduitRecord(
            conduit_id="ops-conduit",
            root_conduit_id="ops-conduit",
            frame_name="ops",
            origin_spellbook_id="ops-spellbook",
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
            origin_spellbook_id="ops-spellbook",
            frame_name="ops",
            owner_conduit_id="ops-conduit",
            spell_id="sha-1",
            spell_index_id="lineage-1",
            spell_name="OpsSpell",
            spellframe=None,
            binding_name="ops_spell",
            permissions=Permissions.create,
            existence=Existence.unique,
            payload=SpellDescriptorPayload(
                payload_type="detailed",
                binding_payload={"kind": "class"},
                resolution_payload={"requirements": []},
                class_profile=None,
                callable_profile=None,
                metadata={},
                instance_members={},
                dynamic_access={},
            ),
        )
    )
    _replace_compiled_access_surface(
        viewer,
        "ops",
        command_frame_enabled=True,
        enabled_spell_index_ids=tuple(),
    )
    space.attach_frame_viewer(viewer)

    with pytest.raises(
        ValueError,
        match="Command access to spell lineage 'lineage-1' is disabled in frame 'ops'",
    ):
        space.command_system.get_spell_object_by_index_id(
            "lineage-1",
            frame_name="ops",
        )


def test_frame_viewer_clone_compiled_access_surface_preserves_command_acl_fields() -> None:
    """
    Verify compiled-surface cloning preserves command ACL enablement fields.

    Returns:
        None.
    """
    compiled_access_surface = CompiledFrameACLAccessSurface(
        frame_name="ops",
        configuration_id="cfg-1",
        view_profile_name="safe",
        view_profile_version="0.0.1",
        codegen_profile_name="safe",
        codegen_profile_version="0.0.1",
        command_frame_enabled=True,
        allowed_kinds=("frame", "conduit", "spell"),
        allowed_commands=("query",),
        frame_payload_fields=("system_state",),
        visible_conduit_ids=("ops-conduit",),
        visible_spell_keys=(("ops-spellbook", "sha-1"),),
        visible_spell_index_ids=("lineage-1",),
        enabled_conduit_ids=("ops-conduit",),
        enabled_spell_index_ids=("lineage-1",),
        conduit_payload_sections_by_id={"ops-conduit": ("conduit_name",)},
        spell_payload_sections_by_key={
            ("ops-spellbook", "sha-1"): ("binding_payload",)
        },
    )

    cloned_access_surface = FrameViewer._clone_compiled_access_surface(
        compiled_access_surface
    )

    assert cloned_access_surface.command_frame_enabled is True
    assert cloned_access_surface.enabled_conduit_ids == ("ops-conduit",)
    assert cloned_access_surface.enabled_spell_index_ids == ("lineage-1",)


def test_static_room_allows_selected_target_runtime_object_access_for_frame() -> None:
    """
    Verify static rooms can still return already-live frame runtime objects.

    Returns:
        None.
    """
    space = StaticRiftSpace(owner_rift_id="rift-1", space_name="main")
    viewer = _build_descriptor_backed_viewer("ops")
    descriptor = viewer._get_required_frame_descriptor("ops")
    frame_handle = object()
    descriptor.set_frame_handle(frame_handle)
    space.attach_frame_viewer(viewer)
    frame_link = viewer.execute_method("list_targets", frame_name="ops")[0]
    space.select_target(frame_link.link_id)

    assert space.command_system.get_selected_target_runtime_object() is frame_handle


def test_static_room_allows_direct_conduit_runtime_object_access(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify static rooms can still return already-live conduit runtime objects.

    Returns:
        None.
    """
    space = StaticRiftSpace(owner_rift_id="rift-1", space_name="main")
    viewer = _build_descriptor_backed_viewer("ops")
    descriptor = viewer._get_required_frame_descriptor("ops")
    descriptor.upsert_conduit_record(
        ConduitRecord(
            conduit_id="ops-conduit",
            root_conduit_id="ops-conduit",
            frame_name="ops",
            origin_spellbook_id="ops-spellbook",
            payload=ConduitDescriptorPayload(
                conduit_name="root",
                conduit_state=ConduitState.normal,
                policy=Policies.default,
                peer_conduit_ids=tuple(),
            ),
        )
    )
    _replace_compiled_access_surface(
        viewer,
        "ops",
        command_frame_enabled=True,
        enabled_conduit_ids=("ops-conduit",),
    )
    space.attach_frame_viewer(viewer)
    conduit_object = object()
    monkeypatch.setattr(
        type(space.command_system),
        "_aether",
        SimpleNamespace(
            _get_conduit_by_id=lambda conduit_id, frame_name: conduit_object,
        ),
    )

    assert (
        space.command_system.get_conduit_object_by_id(
            "ops-conduit",
            frame_name="ops",
        ) is conduit_object
    )


def test_static_room_returns_live_spell_runtime_object_by_index_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify static rooms return a spell runtime object only when it is already live.

    Returns:
        None.
    """
    space = StaticRiftSpace(owner_rift_id="rift-1", space_name="main")
    viewer = _build_descriptor_backed_viewer("ops")
    descriptor = viewer._get_required_frame_descriptor("ops")
    descriptor.upsert_conduit_record(
        ConduitRecord(
            conduit_id="ops-conduit",
            root_conduit_id="ops-conduit",
            frame_name="ops",
            origin_spellbook_id="ops-spellbook",
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
            origin_spellbook_id="ops-spellbook",
            frame_name="ops",
            owner_conduit_id="ops-conduit",
            spell_id="sha-1",
            spell_index_id="lineage-1",
            spell_name="OpsSpell",
            spellframe=None,
            binding_name="ops_spell",
            permissions=Permissions.create,
            existence=Existence.unique,
            payload=SpellDescriptorPayload(
                payload_type="detailed",
                binding_payload={"kind": "class"},
                resolution_payload={"requirements": []},
                class_profile=None,
                callable_profile=None,
                metadata={},
                instance_members={},
                dynamic_access={},
            ),
        )
    )
    _replace_compiled_access_surface(
        viewer,
        "ops",
        command_frame_enabled=True,
        enabled_conduit_ids=("ops-conduit",),
        enabled_spell_index_ids=("lineage-1",),
    )
    space.attach_frame_viewer(viewer)
    live_spell_object = object()
    owner_conduit = SimpleNamespace(
        _get_live_spell_runtime_object_by_index_id=lambda spell_index_id: (
            live_spell_object if spell_index_id == "lineage-1" else None
        )
    )
    monkeypatch.setattr(
        type(space.command_system),
        "get_conduit_object_by_id",
        lambda self, conduit_id, *, frame_name=None: owner_conduit,
    )

    assert (
        space.command_system.get_spell_object_by_index_id(
            "lineage-1",
            frame_name="ops",
        ) is live_spell_object
    )


def test_static_room_denies_spell_runtime_object_when_not_live(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify static rooms fail when the published spell does not already have a live creation.

    Returns:
        None.
    """
    space = StaticRiftSpace(owner_rift_id="rift-1", space_name="main")
    viewer = _build_descriptor_backed_viewer("ops")
    descriptor = viewer._get_required_frame_descriptor("ops")
    descriptor.upsert_conduit_record(
        ConduitRecord(
            conduit_id="ops-conduit",
            root_conduit_id="ops-conduit",
            frame_name="ops",
            origin_spellbook_id="ops-spellbook",
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
            origin_spellbook_id="ops-spellbook",
            frame_name="ops",
            owner_conduit_id="ops-conduit",
            spell_id="sha-1",
            spell_index_id="lineage-1",
            spell_name="OpsSpell",
            spellframe=None,
            binding_name="ops_spell",
            permissions=Permissions.create,
            existence=Existence.unique,
            payload=SpellDescriptorPayload(
                payload_type="detailed",
                binding_payload={"kind": "class"},
                resolution_payload={"requirements": []},
                class_profile=None,
                callable_profile=None,
                metadata={},
                instance_members={},
                dynamic_access={},
            ),
        )
    )
    _replace_compiled_access_surface(
        viewer,
        "ops",
        command_frame_enabled=True,
        enabled_conduit_ids=("ops-conduit",),
        enabled_spell_index_ids=("lineage-1",),
    )
    space.attach_frame_viewer(viewer)
    owner_conduit = SimpleNamespace(
        _get_live_spell_runtime_object_by_index_id=lambda spell_index_id: None
    )
    monkeypatch.setattr(
        type(space.command_system),
        "get_conduit_object_by_id",
        lambda self, conduit_id, *, frame_name=None: owner_conduit,
    )

    with pytest.raises(
        ValueError,
        match="Spell lineage 'lineage-1' is not live in frame 'ops'",
    ):
        space.command_system.get_spell_object_by_index_id(
            "lineage-1",
            frame_name="ops",
        )


def test_capability_room_denies_direct_spell_runtime_object_access() -> None:
    """
    Verify capability rooms reject direct spell runtime-object access.

    Returns:
        None.
    """
    space = CapabilityRiftSpace(owner_rift_id="rift-1", space_name="main")
    viewer = _build_descriptor_backed_viewer("ops")
    space.attach_frame_viewer(viewer)

    with pytest.raises(
        ValueError,
        match="Raw runtime-object access via 'get_spell_object_by_index_id' is disabled in capability RiftSpace",
    ):
        space.command_system.get_spell_object_by_index_id(
            "lineage-1",
            frame_name="ops",
        )


def test_rift_space_can_delegate_frame_surface_calls_to_attached_viewer() -> None:
    """
    Verify a RiftSpace delegates frame-surface calls through the attached viewer.

    Returns:
        None.
    """
    space = RiftSpace(owner_rift_id="rift-1", space_name="main")
    viewer = _build_descriptor_backed_viewer("ops")
    space.attach_frame_viewer(viewer)

    assert space.get_required_frame_viewer() is viewer
    assert space.list_frame_names() == ["ops"]
    assert len(space.list_available_targets()) == 1
    assert space.describe_available_targets()[0]["source_kind"] == "frame"


def test_rift_space_frame_surface_delegation_fails_fast_without_attached_viewer() -> None:
    """
    Verify RiftSpace delegation fails fast when no frame viewer is attached.

    Returns:
        None.
    """
    space = RiftSpace(owner_rift_id="rift-1", space_name="main")

    with pytest.raises(ValueError, match="has no attached frame viewer"):
        space.get_required_frame_viewer()

    with pytest.raises(ValueError, match="has no attached frame viewer"):
        space.list_frame_names()


def test_rift_space_can_select_and_describe_targets_from_attached_viewer() -> None:
    """
    Verify RiftSpace can hold a selected-target context over the hosted viewer.

    Returns:
        None.
    """
    space = RiftSpace(owner_rift_id="rift-1", space_name="main")
    viewer = _build_descriptor_backed_viewer("ops")
    space.attach_frame_viewer(viewer)

    frame_link = viewer.execute_method("list_targets")[0]

    space.select_target(frame_link.link_id)

    assert space.list_selected_target_ids() == [frame_link.link_id]
    assert space.describe_selected_targets() == [
        {
            "frame_name": "ops",
            "target_id": frame_link.link_id,
            "source_kind": "frame",
            "source_id": "ops-frame",
            "display_name": "ops",
        }
    ]


def test_rift_space_selection_helpers_reject_invalid_target_inputs() -> None:
    """
    Verify RiftSpace selection helpers fail fast on invalid target inputs.

    Returns:
        None.
    """
    space = RiftSpace(owner_rift_id="rift-1", space_name="main")
    viewer = _build_descriptor_backed_viewer("ops")
    space.attach_frame_viewer(viewer)

    with pytest.raises(ValueError, match="target_id cannot be empty"):
        space.select_target("")

    with pytest.raises(ValueError, match="was not found"):
        space.select_target("missing")


def test_rift_exposes_frame_link_contract_from_assigned_frames() -> None:
    """
    Verify a created Rift exposes the assigned-frame availability contract.

    Returns:
        None.
    """
    _bind_target_frame_configuration(
        "ops",
        rift_enabled=True,
        ai_native_enabled=False,
        system_state=SystemState.automatic,
    )
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_target_frame_override(True)
    configuration.with_multiple_target_frames(True)
    configuration.with_max_target_frame_count(2)
    configuration.with_allowed_target_frame_names(("default", "ops"))
    nexus.enable(configuration)
    _seed_frame_descriptor("ops")

    rift_configuration = nexus.create_rift_configuration()
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="ops_rift")
    rift.target_frame("ops", set_as_default=True)

    assert rift.list_assigned_frame_names() == ("ops",)
    assert rift.frame_link_contract.default_frame_name == "ops"


def test_rift_can_build_frame_viewer_from_assigned_frame_contract() -> None:
    """
    Verify a Rift can build a viewer directly from its assigned-frame contract.

    Returns:
        None.
    """
    _bind_target_frame_configuration(
        "ops",
        rift_enabled=True,
        ai_native_enabled=False,
        system_state=SystemState.automatic,
    )
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_target_frame_override(True)
    configuration.with_multiple_target_frames(True)
    configuration.with_max_target_frame_count(2)
    configuration.with_allowed_target_frame_names(("default", "ops"))
    nexus.enable(configuration)
    _seed_frame_descriptor("ops")

    rift_configuration = nexus.create_rift_configuration()
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="ops_rift")
    rift.target_frame("ops", set_as_default=True)

    viewer = rift.create_frame_viewer()

    assert viewer.metadata["rift_id"] == rift.id
    assert viewer.default_view_frame_name == "ops"
    assert viewer.frame_descriptors_by_name["ops"].frame_name == "ops"


def test_rift_can_target_frame_through_contract_after_nexus_validation() -> None:
    """
    Verify Rift engages a target frame through its contract after Nexus validation.

    Returns:
        None.
    """
    _bind_target_frame_configuration(
        "ops",
        rift_enabled=True,
        ai_native_enabled=False,
        system_state=SystemState.automatic,
    )
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_target_frame_override(True)
    configuration.with_multiple_target_frames(True)
    configuration.with_max_target_frame_count(2)
    configuration.with_allowed_target_frame_names(("default", "ops"))
    nexus.enable(configuration)
    _seed_frame_descriptor("ops")

    rift_configuration = nexus.create_rift_configuration()
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="ops_rift")

    rift.target_frame("ops", set_as_default=True)

    assert rift.frame_link_contract.has_frame("ops") is True
    assert rift.frame_link_contract.default_frame_name == "ops"
    assert rift.default_target_frame_name == "ops"


def test_nexus_can_register_and_list_named_frame_acl_configurations() -> None:
    """
    Verify Nexus can register and list named ACL configurations for one frame.

    Returns:
        None.
    """
    nexus = _create_enabled_nexus()
    named_configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        nexus.get_current_frame_acl_configuration("default"),
        reason="named",
    )
    named_configuration.finalize()

    registered = nexus.register_named_frame_acl_configuration(
        "default",
        named_configuration,
        contract_name="ops_contract",
    )

    assert registered.frame_name == "default"
    assert nexus.get_named_frame_acl_configuration(
        "default",
        "ops_contract",
    ).to_json_dict() == named_configuration.to_json_dict()
    assert nexus.list_named_frame_acl_configuration_names("default") == [
        "default",
        "ops_contract",
    ]


def test_rift_target_frame_uses_selected_named_acl_contract_for_viewer_projection() -> None:
    """
    Verify Rift targeting selects the named ACL contract used for viewer projection.

    Returns:
        None.
    """
    _bind_target_frame_configuration(
        "ops",
        rift_enabled=True,
        ai_native_enabled=False,
        system_state=SystemState.automatic,
    )
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_target_frame_override(True)
    configuration.with_multiple_target_frames(True)
    configuration.with_max_target_frame_count(2)
    configuration.with_allowed_target_frame_names(("default", "ops"))
    nexus.enable(configuration)
    _seed_frame_descriptor("ops")

    named_configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        nexus.get_current_frame_acl_configuration("ops"),
        reason="named",
    )
    named_configuration.finalize()
    nexus.register_named_frame_acl_configuration(
        "ops",
        named_configuration,
        contract_name="ops_contract",
    )

    rift = nexus.create_rift(rift_name="ops_rift")
    rift.target_frame("ops", contract_name="ops_contract", set_as_default=True)

    viewer = rift.get_space_frame_viewer()

    assert rift.frame_link_contract.get_selected_contract_name("ops") == "ops_contract"
    assert viewer.frame_acl_configurations_by_frame_name["ops"].to_json_dict() == (
        named_configuration.to_json_dict()
    )
    assert viewer.metadata["contract_names_by_frame_name"] == {
        "ops": {
            "view": "ops_contract",
            "command": "ops_contract",
            "codegen": "ops_contract",
        }
    }


def test_rift_can_create_new_frame_viewer_for_one_engaged_frame() -> None:
    """
    Verify Rift can create one frame-specific viewer transaction.

    Returns:
        None.
    """
    _bind_target_frame_configuration(
        "ops",
        rift_enabled=True,
        ai_native_enabled=False,
        system_state=SystemState.automatic,
    )
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_target_frame_override(True)
    configuration.with_multiple_target_frames(True)
    configuration.with_max_target_frame_count(2)
    configuration.with_allowed_target_frame_names(("default", "ops"))
    nexus.enable(configuration)
    _seed_frame_descriptor("ops")

    rift_configuration = nexus.create_rift_configuration()
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="ops_rift")
    rift.target_frame("ops", set_as_default=True)

    viewer = rift.create_new_frame_viewer("ops", viewer_profile_name="general")

    assert viewer.list_frame_names() == ["ops"]
    assert viewer.selected_profile_names_by_frame_name == {"ops": "general"}
    assert viewer.get_selected_profile_for_frame("ops").frame_descriptor is (
        viewer.frame_descriptors_by_name["ops"]
    )


def test_rift_can_attach_frame_viewer_to_active_space_and_read_it_back() -> None:
    """
    Verify a Rift can attach its frame viewer chain to the active space.

    Returns:
        None.
    """
    _bind_target_frame_configuration(
        "ops",
        rift_enabled=True,
        ai_native_enabled=False,
        system_state=SystemState.automatic,
    )
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_target_frame_override(True)
    configuration.with_allowed_target_frame_names(("default", "ops"))
    nexus.enable(configuration)
    _seed_frame_descriptor("ops")

    rift_configuration = nexus.create_rift_configuration().with_space_name("main")
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="ops_rift")
    rift.target_frame("ops", set_as_default=True)
    space = rift.get_space(rift.active_space_id)
    viewer = rift.get_space_frame_viewer()

    assert viewer is space.frame_viewer
    assert rift.get_space_frame_viewer() is viewer
    assert viewer.default_view_frame_name == "ops"


def test_rift_space_frame_viewer_helpers_fail_fast_without_target_space_or_attached_viewer() -> None:
    """
    Verify Rift viewer host helpers fail fast when the space/viewer is missing.

    Returns:
        None.
    """
    nexus = _create_enabled_nexus()
    rift = nexus.create_rift(rift_name="alpha")

    with pytest.raises(ValueError, match="has no attached frame viewer"):
        rift.get_space_frame_viewer()

    with pytest.raises(ValueError, match="has no attached frame viewer"):
        rift.get_space_frame_viewer()


def test_direct_rift_access_can_be_token_gated() -> None:
    """
    Verify direct live-Rift retrieval can be token-gated independently of
    creation.

    Returns:
        None.
    """
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_rift_access_token_required(True)
    configuration.with_rift_access_token("secret")
    nexus.enable(configuration)

    rift = nexus.create_rift(rift_name="alpha")

    with pytest.raises(ValueError, match="Valid Rift access token"):
        nexus.get_rift(rift.id)

    assert nexus.get_rift(rift.id, access_token="secret") is rift


def test_target_frame_allow_and_deny_lists_are_enforced() -> None:
    """
    Verify target-frame governance uses allow-list and deny-list policy with
    deny precedence.

    Returns:
        None.
    """
    _bind_target_frame_configuration(
        "ops",
        rift_enabled=True,
        ai_native_enabled=False,
        system_state=SystemState.automatic,
    )
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_target_frame_override(True)
    configuration.with_allowed_target_frame_names(("default", "ops"))
    configuration.with_denied_target_frame_names(("ops",))
    nexus.enable(configuration)

    blocked_rift = nexus.create_rift(rift_name="blocked")
    with pytest.raises(ValueError, match="denied"):
        blocked_rift.target_frame("ops")

    replacement_configuration = nexus.create_system_configuration()
    replacement_configuration.with_rift_creation_enabled(True)
    replacement_configuration.with_target_frame_override(True)
    replacement_configuration.with_allowed_target_frame_names(("default", "ops"))
    replacement_configuration.with_denied_target_frame_names(tuple())
    nexus.enable(replacement_configuration)
    _seed_frame_descriptor("ops")
    rift = nexus.create_rift(rift_name="allowed")
    rift.target_frame("ops", set_as_default=True)

    assert rift.target_frame_names == ("ops",)
    assert rift.default_target_frame_name == "ops"


def test_static_rift_requires_target_frame_ai_profiles() -> None:
    """
    Verify AR refuses to attach to a target frame without AI profiles enabled.

    Returns:
        None.
    """
    _bind_target_frame_configuration("ops", rift_enabled=False)
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_target_frame_override(True)
    configuration.with_allowed_target_frame_names(("default", "ops"))
    nexus.enable(configuration)

    rift_configuration = nexus.create_rift_configuration().with_space_type(
        RiftSpaceType.static
    )
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="ops-static")

    with pytest.raises(ValueError, match="rift_enabled"):
        rift.target_frame("ops")


def test_dynamic_rift_requires_target_frame_ai_native_enabled() -> None:
    """
    Verify dynamic AR refuses frames that do not enable AI-native mode.

    Returns:
        None.
    """
    _bind_target_frame_configuration(
        "ops",
        rift_enabled=True,
        ai_native_enabled=False,
        system_state=SystemState.dynamic,
    )
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_target_frame_override(True)
    configuration.with_allowed_target_frame_names(("default", "ops"))
    nexus.enable(configuration)

    rift_configuration = nexus.create_rift_configuration().with_space_type(
        RiftSpaceType.dynamic
    )
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="ops-dynamic")

    with pytest.raises(ValueError, match="ai_native_enabled"):
        rift.target_frame("ops")


def test_dynamic_rift_requires_dynamic_target_frame_system_state() -> None:
    """
    Verify dynamic AR refuses frames that are not in dynamic system_state.

    Returns:
        None.
    """
    _bind_target_frame_configuration(
        "ops",
        rift_enabled=True,
        ai_native_enabled=True,
        system_state=SystemState.automatic,
    )
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_target_frame_override(True)
    configuration.with_allowed_target_frame_names(("default", "ops"))
    nexus.enable(configuration)

    rift_configuration = nexus.create_rift_configuration().with_space_type(
        RiftSpaceType.dynamic
    )
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="ops-dynamic")

    with pytest.raises(ValueError, match="dynamic system_state"):
        rift.target_frame("ops")


def test_dynamic_rift_can_attach_to_dynamic_ai_native_target_frame() -> None:
    """
    Verify dynamic AR attaches successfully when the target frame is fully
    eligible.

    Returns:
        None.
    """
    _bind_target_frame_configuration(
        "ops",
        rift_enabled=True,
        ai_native_enabled=True,
        system_state=SystemState.dynamic,
    )
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_target_frame_override(True)
    configuration.with_allowed_target_frame_names(("default", "ops"))
    nexus.enable(configuration)
    _seed_frame_descriptor("ops")

    rift_configuration = nexus.create_rift_configuration().with_space_type(
        RiftSpaceType.dynamic
    )
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="ops-dynamic")
    rift.target_frame("ops", set_as_default=True)

    assert rift.target_frame_names == ("ops",)
    assert rift.configuration.get_property("space_type") == RiftSpaceType.dynamic


def test_static_rift_can_attach_to_automatic_target_frame_when_rift_enabled() -> None:
    """
    Verify static AR can attach to an automatic frame when AI profiles are
    enabled.

    Returns:
        None.
    """
    _bind_target_frame_configuration(
        "ops",
        rift_enabled=True,
        ai_native_enabled=False,
        system_state=SystemState.automatic,
    )
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_target_frame_override(True)
    configuration.with_allowed_target_frame_names(("default", "ops"))
    nexus.enable(configuration)
    _seed_frame_descriptor("ops")

    rift_configuration = nexus.create_rift_configuration().with_space_type(
        RiftSpaceType.static
    )
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="ops-static")
    rift.target_frame("ops", set_as_default=True)

    assert rift.target_frame_names == ("ops",)
    assert rift.configuration.get_property("space_type") == RiftSpaceType.static


def test_target_frame_requires_existing_descriptor_truth() -> None:
    """
    Verify a frame cannot be targeted until descriptor truth exists for it.

    Returns:
        None.
    """
    _bind_target_frame_configuration(
        "ops",
        rift_enabled=True,
        ai_native_enabled=False,
        system_state=SystemState.automatic,
    )
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_target_frame_override(True)
    configuration.with_allowed_target_frame_names(("default", "ops"))
    nexus.enable(configuration)

    rift = nexus.create_rift(rift_name="ops-static")

    with pytest.raises(ValueError, match="has no descriptor"):
        rift.target_frame("ops")


def test_shared_and_isolated_nexus_frame_names_are_assigned() -> None:
    """
    Verify Nexus-frame topology settings shape the Rift's assigned internal
    frame names correctly.

    Returns:
        None.
    """
    shared_nexus = _create_enabled_nexus()
    shared_rift = shared_nexus.create_rift(rift_name="shared")
    assert shared_rift.default_nexus_frame_name == "aetheric_frame_system"
    assert shared_rift.get_nexus_frame() is shared_nexus.get_nexus_frame_for_rift(shared_rift.id)

    isolated_nexus = Nexus()
    configuration = isolated_nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_nexus_frame_mode("one_per_workspace")
    configuration.with_max_nexus_frame_count(2)
    isolated_nexus.enable(configuration)

    isolated_rift = isolated_nexus.create_rift(rift_name="isolated")
    assert isolated_rift.default_nexus_frame_name.startswith("aetheric_frame_system:")
    assert isolated_rift.default_nexus_frame_name.endswith(isolated_rift.id)
    assert isolated_rift.nexus_frame_names == (isolated_rift.default_nexus_frame_name,)


def test_shared_nexus_frame_survives_until_last_rift_is_removed() -> None:
    """
    Verify the shared Nexus frame stays alive until the last attached Rift is
    removed.

    Returns:
        None.
    """
    nexus = _create_enabled_nexus()
    aether = Aether()
    first = nexus.create_rift(rift_name="first")
    second = nexus.create_rift(rift_name="second")
    shared_frame_name = second.default_nexus_frame_name

    assert first.default_nexus_frame_name in aether._aetheric_frames

    nexus.remove_rift(first.id)
    assert shared_frame_name in aether._aetheric_frames

    nexus.remove_rift(second.id)
    assert shared_frame_name not in aether._aetheric_frames
    assert nexus._get_nexus_frame_record(shared_frame_name) is None


def test_one_per_workspace_nexus_frame_is_removed_with_its_rift() -> None:
    """
    Verify a one-per-workspace Nexus frame is disposed when its owning Rift is
    removed.

    Returns:
        None.
    """
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_nexus_frame_mode("one_per_workspace")
    configuration.with_max_nexus_frame_count(2)
    nexus.enable(configuration)

    rift = nexus.create_rift(rift_name="isolated")
    frame_name = rift.default_nexus_frame_name

    assert frame_name in Aether()._aetheric_frames

    nexus.remove_rift(rift.id)

    assert frame_name not in Aether()._aetheric_frames
    assert nexus._get_nexus_frame_record(frame_name) is None


def test_external_aether_frame_cleanup_clears_nexus_frame_record() -> None:
    """
    Verify direct Aether frame disposal clears the corresponding Nexus frame
    record first.

    Returns:
        None.
    """
    nexus = _create_enabled_nexus()
    rift = nexus.create_rift(rift_name="alpha")
    frame_name = rift.default_nexus_frame_name

    assert nexus._get_nexus_frame_record(frame_name) is not None

    rift.get_nexus_frame().cleanup()

    assert nexus._get_nexus_frame_record(frame_name) is None


def test_shared_mode_returns_the_same_frame_to_any_rift() -> None:
    """
    Verify shared mode returns the same Nexus frame to all Rifts.

    Returns:
        None.
    """
    nexus = _create_enabled_nexus()
    first = nexus.create_rift(rift_name="first")
    second = nexus.create_rift(rift_name="second")

    assert first.get_nexus_frame() is second.get_nexus_frame()


def test_one_per_workspace_mode_rejects_other_rift_frame_access() -> None:
    """
    Verify one-per-workspace mode only returns the calling Rift's private
    Nexus frame.

    Returns:
        None.
    """
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_nexus_frame_mode("one_per_workspace")
    configuration.with_max_nexus_frame_count(3)
    nexus.enable(configuration)

    first = nexus.create_rift(rift_name="first")
    second = nexus.create_rift(rift_name="second")

    with pytest.raises(ValueError, match="private Nexus frame"):
        nexus.get_nexus_frame_for_rift(first.id, frame_name=second.default_nexus_frame_name)


def test_one_per_workspace_mode_rejects_immutable_private_frame_creation() -> None:
    """
    Verify one-per-workspace mode forbids immutable private Nexus frames.

    Returns:
        None.
    """
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_nexus_frame_mode("one_per_workspace")
    configuration.with_max_nexus_frame_count(3)
    nexus.enable(configuration)

    rift = nexus.create_rift(rift_name="isolated")

    with pytest.raises(ValueError, match="cannot be immutable"):
        nexus.create_nexus_frame_for_rift(rift.id, immutable=True)


def test_indexed_mode_allows_shared_lookup_by_explicit_name() -> None:
    """
    Verify indexed mode allows a Rift to request another indexed frame by name.

    Returns:
        None.
    """
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_nexus_frame_mode("indexed")
    configuration.with_max_nexus_frame_count(4)
    nexus.enable(configuration)

    first = nexus.create_rift(rift_name="first")
    second = nexus.create_rift(rift_name="second")

    shared_frame = first.get_nexus_frame()
    looked_up_frame = second.get_nexus_frame(frame_name=first.default_nexus_frame_name)

    assert looked_up_frame is shared_frame
    assert first.default_nexus_frame_name in second.nexus_frame_names


def test_indexed_mode_can_create_explicit_new_frame() -> None:
    """
    Verify indexed mode can create a new named Nexus frame explicitly.

    Returns:
        None.
    """
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_nexus_frame_mode("indexed")
    configuration.with_max_nexus_frame_count(4)
    nexus.enable(configuration)

    rift = nexus.create_rift(rift_name="builder")
    created_frame = rift.create_nexus_frame(frame_name="ops", immutable=True)

    assert nexus._get_nexus_frame_record("ops") is not None
    assert rift.get_nexus_frame("ops") is created_frame
    assert "ops" in rift.list_accessible_nexus_frame_names()


def test_direct_rift_construction_is_not_the_normal_registry_path() -> None:
    """
    Verify directly constructing a Rift does not register it automatically.

    Returns:
        None.
    """
    nexus = _create_enabled_nexus()
    configuration = nexus.create_rift_configuration()
    configuration.finalize()
    rift = Rift(
        nexus,
        configuration=configuration,
        nexus_frame_names=("aetheric_frame_system",),
        default_nexus_frame_name="aetheric_frame_system",
        target_frame_names=tuple(),
        default_target_frame_name=None,
        rift_name="manual",
    )

    assert nexus.has_rift(rift.id) is False
    assert rift.is_registered is False


def test_direct_rift_construction_requires_configured_enabled_nexus() -> None:
    """
    Verify direct Rift construction fails fast unless Nexus is configured and
    enabled.

    Returns:
        None.
    """
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    rift_configuration = RiftConfiguration().with_defaults().finalize()

    with pytest.raises(RuntimeError, match="configured Nexus"):
        Rift(
            nexus,
            configuration=rift_configuration,
            nexus_frame_names=("aetheric_frame_system",),
            default_nexus_frame_name="aetheric_frame_system",
            target_frame_names=tuple(),
            default_target_frame_name=None,
            rift_name="manual",
        )

    nexus.enable(configuration)
    nexus.disable()
    with pytest.raises(RuntimeError, match="enabled Nexus"):
        Rift(
            nexus,
            configuration=rift_configuration,
            nexus_frame_names=("aetheric_frame_system",),
            default_nexus_frame_name="aetheric_frame_system",
            target_frame_names=tuple(),
            default_target_frame_name=None,
            rift_name="manual",
        )


def test_direct_rift_construction_requires_nexus_argument() -> None:
    """
    Verify direct Rift construction fails if no Nexus is passed in.

    Returns:
        None.
    """
    configuration = RiftConfiguration().with_defaults().finalize()

    with pytest.raises(TypeError, match="nexus cannot be None"):
        Rift(
            None,
            configuration=configuration,
            nexus_frame_names=("aetheric_frame_system",),
            default_nexus_frame_name="aetheric_frame_system",
            target_frame_names=tuple(),
            default_target_frame_name=None,
            rift_name="manual",
        )
