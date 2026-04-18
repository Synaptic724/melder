import gc
import logging
import threading
import weakref
from types import SimpleNamespace
from typing import Dict, Optional, Tuple

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
from melder.aether.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from melder.aether.nexus.rift.frame_viewer.static_frame_viewer import (
    StaticFrameViewer,
)
from melder.aether.nexus.rift.projection.codegen_projection import CodegenProjection
from melder.aether.nexus.rift.projection.command_projection import CommandProjection
from melder.aether.nexus.rift.projection.frame_projection_set import FrameProjectionSet
from melder.aether.nexus.rift.projection.view_projection import ViewProjection
from melder.aether.nexus.rift.command_system.capability_command_system import (
    CapabilityCommandSystem,
)
from melder.aether.nexus.rift.command_system.command_system import (
    CommandSystem,
)
from melder.aether.nexus.rift.command_system.codegen_command_system import (
    CodegenCommandSystem,
)
from melder.aether.nexus.rift.command_system.static_command_system import (
    StaticCommandSystem,
)
from melder.aether.nexus.rift.rift_space.capability_rift_space import CapabilityRiftSpace
from melder.aether.nexus.rift.rift_space.codegen_rift_space import CodegenRiftSpace
from melder.aether.nexus.rift.rift_space.rift_space import RiftSpace
from melder.aether.nexus.rift.rift_space.static_rift_space import StaticRiftSpace
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook


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
    allowed_kinds: Optional[Tuple[str, ...]] = None,
    visible_spell_keys: Optional[Tuple[Tuple[str, str], ...]] = None,
    visible_spell_index_ids: Optional[Tuple[str, ...]] = None,
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
        allowed_kinds:
            Optional visible kind names for the frame.
        visible_spell_keys:
            Optional visible spell record keys for the frame.
        visible_spell_index_ids:
            Optional visible spell lineage ids for the frame.
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
            allowed_kinds=(
                allowed_kinds
                if allowed_kinds is not None
                else compiled_access_surface.allowed_kinds
            ),
            allowed_commands=compiled_access_surface.allowed_commands,
            frame_payload_fields=compiled_access_surface.frame_payload_fields,
            visible_conduit_ids=compiled_access_surface.visible_conduit_ids,
            visible_spell_keys=(
                visible_spell_keys
                if visible_spell_keys is not None
                else compiled_access_surface.visible_spell_keys
            ),
            visible_spell_index_ids=(
                visible_spell_index_ids
                if visible_spell_index_ids is not None
                else compiled_access_surface.visible_spell_index_ids
            ),
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


def _build_projection_set_from_viewer(
    viewer: FrameViewer,
    frame_name: str,
) -> FrameProjectionSet:
    """
    Build one projection set from a descriptor-backed viewer snapshot.

    Args:
        viewer:
            Source viewer.
        frame_name:
            Hosted frame name.

    Returns:
        FrameProjectionSet: Detached projection set for the frame.
    """
    nexus = Nexus()
    frame_descriptor = viewer.frame_descriptors_by_name[frame_name]
    frame_acl_configuration = viewer.frame_acl_configurations_by_frame_name[frame_name]
    compiled_access_surface = viewer.compiled_access_surfaces_by_frame_name[frame_name]
    return FrameProjectionSet(
        frame_name=frame_name,
        view_projection=ViewProjection(
            frame_name=frame_name,
            frame_descriptor=frame_descriptor,
            frame_acl_configuration=nexus._clone_frame_acl_configuration(
                frame_acl_configuration,
                reason="test_view_projection_clone",
            ),
            compiled_access_surface=nexus._clone_compiled_access_surface(
                compiled_access_surface
            ),
            metadata={"surface": "view"},
        ),
        command_projection=CommandProjection(
            frame_name=frame_name,
            frame_descriptor=frame_descriptor,
            frame_acl_configuration=nexus._clone_frame_acl_configuration(
                frame_acl_configuration,
                reason="test_command_projection_clone",
            ),
            compiled_access_surface=nexus._clone_compiled_access_surface(
                compiled_access_surface
            ),
            metadata={"surface": "command"},
        ),
        codegen_projection=CodegenProjection(
            frame_name=frame_name,
            frame_descriptor=frame_descriptor,
            frame_acl_configuration=nexus._clone_frame_acl_configuration(
                frame_acl_configuration,
                reason="test_codegen_projection_clone",
            ),
            compiled_access_surface=nexus._clone_compiled_access_surface(
                compiled_access_surface
            ),
            metadata={"surface": "codegen"},
        ),
        metadata={"source": "test_viewer_clone"},
    )


def _attach_projection_backed_viewer(space: RiftSpace, viewer: FrameViewer) -> None:
    """
    Seed projection sets from a test viewer, then attach that viewer to the room.

    Args:
        space:
            Target room.
        viewer:
            Source viewer.

    Returns:
        None.
    """
    space.replace_projection_sets(
        {
            frame_name: _build_projection_set_from_viewer(viewer, frame_name)
            for frame_name in viewer.frame_descriptors_by_name.keys()
        }
    )
    space.attach_frame_viewer(viewer)


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
    assert rift.list_assigned_frame_names() == tuple()
    assert isinstance(rift.space, StaticRiftSpace)
    assert nexus.get_rift(rift.id) is rift
    assert nexus.get_rift_by_name("alpha") is rift
    assert nexus.list_rift_ids() == [rift.id]
    assert nexus.get_rift_gate(rift.id) is rift.rift_gate

    rift_id = rift.id
    nexus.remove_rift(rift_id)
    assert nexus.has_rift(rift_id) is False
    assert nexus.get_rift_gate(rift_id) is None


def test_nexus_rift_gate_controls_delegate_to_registered_gate() -> None:
    nexus = _create_enabled_nexus()
    rift = nexus.create_rift(rift_name="alpha")

    nexus.disable_rift_gate(rift.id)
    assert rift.rift_gate.enabled is False

    nexus.enable_rift_gate(rift.id)
    assert rift.rift_gate.enabled is True

    nexus.disable_all_rift_gates()
    assert rift.rift_gate.enabled is False

    nexus.enable_all_rift_gates()
    assert rift.rift_gate.enabled is True

    nexus.set_rift_gate_entry_mode(rift.id, "raise")
    assert rift.rift_gate.entry_mode == "raise"

    nexus.set_all_rift_gate_entry_mode("wait")
    assert rift.rift_gate.entry_mode == "wait"


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
    profile.with_space_type(RiftSpaceType.codegen)
    profile.with_space_name("ops-room")
    nexus.register_rift_profile("ops_profile", profile)

    profiled_configuration = nexus.create_rift_configuration(profile_name="ops_profile")
    second_profiled_configuration = nexus.create_rift_configuration(profile_name="ops_profile")

    assert profiled_configuration is not second_profiled_configuration
    assert profiled_configuration.get_property("space_type") == RiftSpaceType.codegen
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
    codegen_configuration = nexus.create_rift_configuration().with_space_type(
        RiftSpaceType.codegen
    )
    codegen_rift = nexus.create_rift(
        configuration=codegen_configuration,
        rift_name="beta",
    )

    assert isinstance(static_rift.space, StaticRiftSpace)
    assert isinstance(capability_rift.space, CapabilityRiftSpace)
    assert isinstance(codegen_rift.space, CodegenRiftSpace)


def test_rift_space_can_attach_and_detach_frame_viewer() -> None:
    """
    Verify a RiftSpace can own an attached frame viewer.

    Returns:
        None.
    """
    space = RiftSpace(owner_rift_id="rift-1", space_name="main")
    viewer = FrameViewer()

    _attach_projection_backed_viewer(space, viewer)

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


def test_rift_space_emits_weak_binding_collection_events_to_callbacks() -> None:
    """
    Verify weak binding collection publishes one room-local event.

    Returns:
        None.
    """
    class _Target:
        pass

    space = RiftSpace(owner_rift_id="rift-1", space_name="main", space_kind="static")
    received_events = []
    space.event_system.register_event_callback(lambda event: received_events.append(event))
    workstation = space.workstation
    target = _Target()

    workstation.bind_object("client", target, weak_ref=True)
    del target
    gc.collect()

    assert len(received_events) == 1
    assert received_events[0].event_type == "binding_collected"
    assert received_events[0].payload["binding_name"] == "client"
    assert received_events[0].payload["binding_store"] == "objects"
    assert received_events[0].space_id == space.space_id
    assert received_events[0].space_kind == "static"


def test_rift_space_can_register_and_unregister_event_callbacks() -> None:
    """
    Verify the room-local event system can register and unregister callbacks.

    Returns:
        None.
    """
    class _Target:
        pass

    space = RiftSpace(owner_rift_id="rift-1", space_name="main", space_kind="static")
    received_events = []
    subscription_id = space.event_system.register_event_callback(
        lambda event: received_events.append(event)
    )
    target = _Target()
    space.workstation.bind_object("client", target, weak_ref=True)
    del target
    gc.collect()

    assert len(received_events) == 1
    assert received_events[0].event_type == "binding_collected"

    space.event_system.unregister_event_callback(subscription_id)
    space.event_system.create_and_emit_event("manual", payload={"kind": "ignored"})
    assert len(received_events) == 1


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
    assert not isinstance(space.command_system, CodegenCommandSystem)


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


def test_codegen_rift_space_composes_codegen_command_system() -> None:
    """
    Verify codegen rooms compose the codegen command system variant.

    Returns:
        None.
    """
    space = CodegenRiftSpace(owner_rift_id="rift-1", space_name="main")

    assert isinstance(space.command_system, CodegenCommandSystem)


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


def test_command_system_execute_target_method_can_force_strong_result_binding() -> None:
    """
    Verify command execution can force strong result binding for one returned value.

    Returns:
        None.
    """
    class _Target:
        def run(self, prefix: str) -> str:
            return "{0}-done".format(prefix)

    space = StaticRiftSpace(owner_rift_id="rift-1", space_name="main")
    workstation = space.workstation
    target = _Target()
    workstation.bind_object("target", target, weak_ref=False)
    workstation.set_target("target", store="objects")

    result = space.command_system.execute_target_method(
        "run",
        "ops",
        bind_as_name="status",
        bind_as_store="attributes",
        bind_result_weak_ref=False,
    )

    assert result == "ops-done"
    assert workstation.get("status", store="attributes") == "ops-done"


def test_command_system_can_get_conduit_by_id_with_lesser_fallback(
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
    _attach_projection_backed_viewer(space, viewer)
    sentinel = object()
    root_conduit = SimpleNamespace(
        _conduit_ward=SimpleNamespace(
            _get_lesser_conduit=lambda conduit_id: sentinel,
        )
    )
    aether_stub = SimpleNamespace(
        get_conduit_by_id=lambda conduit_id, frame_name: (_ for _ in ()).throw(
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

    result = space.command_system.get_conduit_by_id(
        "lesser-1",
        frame_name="ops",
    )

    assert result is sentinel


def test_command_system_can_query_command_enabled_conduits() -> None:
    """
    Verify command-side conduit query helpers use published command-enabled truth.

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
    descriptor.upsert_conduit_record(
        ConduitRecord(
            conduit_id="shadow-conduit",
            root_conduit_id="shadow-conduit",
            frame_name="ops",
            origin_spellbook_id="ops-spellbook",
            payload=ConduitDescriptorPayload(
                conduit_name="shadow",
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
    _attach_projection_backed_viewer(space, viewer)

    assert space.command_system.list_conduit_ids(frame_name="ops") == ("ops-conduit",)
    assert space.command_system.list_conduit_names(frame_name="ops") == ("root",)
    assert space.command_system.count_conduits(frame_name="ops") == 1
    assert space.command_system.has_conduit_id("ops-conduit", frame_name="ops") is True
    assert space.command_system.has_conduit_id("shadow-conduit", frame_name="ops") is False
    assert space.command_system.has_conduit_name("root", frame_name="ops") is True
    assert space.command_system.has_conduit_name("shadow", frame_name="ops") is False
    assert (
        space.command_system.find_conduit_id_by_name("root", frame_name="ops")
        == "ops-conduit"
    )
    assert (
        space.command_system.find_conduit_id_by_name("shadow", frame_name="ops")
        is None
    )


def test_command_system_can_get_spell_by_id(
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
    _attach_projection_backed_viewer(space, viewer)
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

    result = space.command_system.get_spell_by_id(
        "sha-1",
        frame_name="ops",
    )

    assert result is spell


def test_command_system_can_get_spell_by_index_id(
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
    _attach_projection_backed_viewer(space, viewer)
    spell = object()
    owner_conduit = SimpleNamespace(
        get_spell_by_index_id=lambda spell_index_id: (
            spell if spell_index_id == "lineage-1" else None
        )
    )
    monkeypatch.setattr(
        type(space.command_system),
        "_get_conduit_by_id_locked",
        lambda self, conduit_id, *, frame_name=None: owner_conduit,
    )

    result = space.command_system.get_spell_by_index_id(
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
    _attach_projection_backed_viewer(space, viewer)
    with pytest.raises(ValueError, match="Command access is disabled for frame 'ops'"):
        space.command_system.get_conduit_cloud(frame_name="ops")


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
    _attach_projection_backed_viewer(space, viewer)
    monkeypatch.setattr(
        type(space.command_system),
        "_aether",
        SimpleNamespace(_get_conduit_by_id=lambda conduit_id, frame_name: object()),
    )

    with pytest.raises(
        ValueError,
        match="Command access to conduit 'ops-conduit' is disabled in frame 'ops'",
    ):
        space.command_system.get_conduit_by_id("ops-conduit", frame_name="ops")


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
    _attach_projection_backed_viewer(space, viewer)

    with pytest.raises(
        ValueError,
        match="Command access to spell lineage 'lineage-1' is disabled in frame 'ops'",
    ):
        space.command_system.get_spell_by_index_id(
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
    _attach_projection_backed_viewer(space, viewer)
    conduit_object = object()
    monkeypatch.setattr(
        type(space.command_system),
        "_aether",
        SimpleNamespace(
            get_conduit_by_id=lambda conduit_id, frame_name: conduit_object,
        ),
    )

    assert (
        space.command_system.get_conduit_by_id(
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
    _attach_projection_backed_viewer(space, viewer)
    live_spell_object = object()
    owner_conduit = SimpleNamespace(
        meld_existing_spell=lambda *, spell_name=None, spell=None, spellframe=None, binding_name=None: (
            live_spell_object if spell == "sha-1" else None
        )
    )
    monkeypatch.setattr(
        type(space.command_system)._aether,
        "_get_conduit_by_id",
        lambda conduit_id, frame_name: owner_conduit,
    )

    assert (
        space.command_system.get_spell_by_index_id(
            "lineage-1",
            frame_name="ops",
        ) is live_spell_object
    )


def test_static_room_wraps_viewer_and_filters_non_live_spells(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify static rooms attach a static viewer and expose only live spells.

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
            spell_id="live-sha",
            spell_index_id="lineage-live",
            spell_name="LiveSpell",
            spellframe=None,
            binding_name="live_spell",
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
    descriptor.upsert_spell_record(
        SpellRecord(
            origin_spellbook_id="ops-spellbook",
            frame_name="ops",
            owner_conduit_id="ops-conduit",
            spell_id="dead-sha",
            spell_index_id="lineage-dead",
            spell_name="DeadSpell",
            spellframe=None,
            binding_name="dead_spell",
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
        allowed_kinds=("frame", "spell"),
        visible_spell_keys=(
            ("ops-spellbook", "dead-sha"),
            ("ops-spellbook", "live-sha"),
        ),
        visible_spell_index_ids=(
            "lineage-dead",
            "lineage-live",
        ),
    )
    owner_conduit = SimpleNamespace(
        has_live_creation=lambda *, spell_name=None, spell=None, spellframe=None, binding_name=None: (
            spell == "live-sha"
        )
    )
    monkeypatch.setattr(
        StaticFrameViewer,
        "_aether",
        SimpleNamespace(
            get_conduit_by_id=lambda conduit_id, frame_name: owner_conduit,
        ),
    )

    _attach_projection_backed_viewer(space, viewer)

    assert isinstance(space.frame_viewer, StaticFrameViewer)
    assert space.frame_viewer.list_spell_source_ids_for_frame("ops") == [
        "ops-spellbook:live-sha"
    ]
    assert space.frame_viewer.list_spell_names(frame_name="ops") == ["LiveSpell"]

    with pytest.raises(ValueError, match="dead-sha"):
        space.frame_viewer.describe_spell_record(
            "ops-spellbook:dead-sha",
            frame_name="ops",
        )


def test_static_room_viewer_filters_non_live_spell_targets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify static viewer target projection exposes only live spell targets.

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
            spell_id="live-sha",
            spell_index_id="lineage-live",
            spell_name="LiveSpell",
            spellframe=None,
            binding_name="live_spell",
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
    descriptor.upsert_spell_record(
        SpellRecord(
            origin_spellbook_id="ops-spellbook",
            frame_name="ops",
            owner_conduit_id="ops-conduit",
            spell_id="dead-sha",
            spell_index_id="lineage-dead",
            spell_name="DeadSpell",
            spellframe=None,
            binding_name="dead_spell",
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
        allowed_kinds=("frame", "spell"),
        visible_spell_keys=(
            ("ops-spellbook", "dead-sha"),
            ("ops-spellbook", "live-sha"),
        ),
        visible_spell_index_ids=(
            "lineage-dead",
            "lineage-live",
        ),
    )
    owner_conduit = SimpleNamespace(
        has_live_creation=lambda *, spell_name=None, spell=None, spellframe=None, binding_name=None: (
            spell == "live-sha"
        )
    )
    monkeypatch.setattr(
        StaticFrameViewer,
        "_aether",
        SimpleNamespace(
            get_conduit_by_id=lambda conduit_id, frame_name: owner_conduit,
        ),
    )

    _attach_projection_backed_viewer(space, viewer)
    frame_links = space.frame_viewer.execute_method("list_targets", frame_name="ops")
    spell_source_ids = [
        frame_link.source_id
        for frame_link in frame_links
        if frame_link.source_kind == "spell"
    ]

    assert spell_source_ids == ["ops-spellbook:live-sha"]


def test_static_room_viewer_hides_many_and_spellspace_spells(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify static viewer excludes unsupported spell existences even when live.

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
            spell_id="many-sha",
            spell_index_id="lineage-many",
            spell_name="ManySpell",
            spellframe=None,
            binding_name="many_spell",
            permissions=Permissions.create,
            existence=Existence.many,
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
    descriptor.upsert_spell_record(
        SpellRecord(
            origin_spellbook_id="ops-spellbook",
            frame_name="ops",
            owner_conduit_id="ops-conduit",
            spell_id="spellspace-sha",
            spell_index_id="lineage-spellspace",
            spell_name="SpellspaceSpell",
            spellframe=None,
            binding_name="spellspace_spell",
            permissions=Permissions.create,
            existence=Existence.unique_per_spell_space,
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
        allowed_kinds=("frame", "spell"),
        visible_spell_keys=(
            ("ops-spellbook", "many-sha"),
            ("ops-spellbook", "spellspace-sha"),
        ),
        visible_spell_index_ids=(
            "lineage-many",
            "lineage-spellspace",
        ),
    )
    owner_conduit = SimpleNamespace(
        has_live_creation=lambda *, spell_name=None, spell=None, spellframe=None, binding_name=None: True
    )
    monkeypatch.setattr(
        StaticFrameViewer,
        "_aether",
        SimpleNamespace(
            get_conduit_by_id=lambda conduit_id, frame_name: owner_conduit,
        ),
    )

    _attach_projection_backed_viewer(space, viewer)

    assert space.frame_viewer.list_spell_source_ids_for_frame("ops") == []
    frame_links = space.frame_viewer.execute_method("list_targets", frame_name="ops")
    assert [frame_link for frame_link in frame_links if frame_link.source_kind == "spell"] == []


def test_static_room_denies_many_and_spellspace_spell_runtime_object_access(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify static command rejects unsupported spell existences explicitly.

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
            spell_id="many-sha",
            spell_index_id="lineage-many",
            spell_name="ManySpell",
            spellframe=None,
            binding_name="many_spell",
            permissions=Permissions.create,
            existence=Existence.many,
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
    descriptor.upsert_spell_record(
        SpellRecord(
            origin_spellbook_id="ops-spellbook",
            frame_name="ops",
            owner_conduit_id="ops-conduit",
            spell_id="spellspace-sha",
            spell_index_id="lineage-spellspace",
            spell_name="SpellspaceSpell",
            spellframe=None,
            binding_name="spellspace_spell",
            permissions=Permissions.create,
            existence=Existence.unique_per_spell_space,
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
        enabled_spell_index_ids=("lineage-many", "lineage-spellspace"),
    )
    _attach_projection_backed_viewer(space, viewer)
    owner_conduit = SimpleNamespace(
        meld_existing_spell=lambda *, spell_name=None, spell=None, spellframe=None, binding_name=None: object()
    )
    monkeypatch.setattr(
        type(space.command_system),
        "_aether",
        SimpleNamespace(
            _get_conduit_by_id=lambda conduit_id, frame_name: owner_conduit,
        ),
    )

    with pytest.raises(ValueError, match="unsupported static existence 'many'"):
        space.command_system.get_spell_by_index_id(
            "lineage-many",
            frame_name="ops",
        )

    with pytest.raises(
        ValueError,
        match="unsupported static existence 'unique_per_spell_space'",
    ):
        space.command_system.get_spell_by_index_id(
            "lineage-spellspace",
            frame_name="ops",
        )


def test_static_command_system_reports_spell_status_for_live_spell() -> None:
    """
    Verify static spell status reporting explains a live available spell.

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
            spell_id="live-sha",
            spell_index_id="lineage-live",
            spell_name="LiveSpell",
            spellframe=None,
            binding_name="live_spell",
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
        enabled_spell_index_ids=("lineage-live",),
    )
    _attach_projection_backed_viewer(space, viewer)
    owner_conduit = SimpleNamespace(
        has_live_creation=lambda *, spell_name=None, spell=None, spellframe=None, binding_name=None: (
            spell == "live-sha"
        )
    )
    space.command_system._aether = SimpleNamespace(
        _get_conduit_by_id=lambda conduit_id, frame_name: owner_conduit,
    )

    status = space.command_system.describe_spell_status_by_index_id(
        "lineage-live",
        frame_name="ops",
    )

    assert status["is_published"] is True
    assert status["is_command_enabled"] is True
    assert status["is_static_supported"] is True
    assert status["is_live"] is True
    assert status["is_available"] is True
    assert status["reason"] == "available"


def test_static_command_system_reports_spell_status_for_unsupported_spell() -> None:
    """
    Verify static spell status reporting explains unsupported static existence.

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
            spell_id="many-sha",
            spell_index_id="lineage-many",
            spell_name="ManySpell",
            spellframe=None,
            binding_name="many_spell",
            permissions=Permissions.create,
            existence=Existence.many,
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
        enabled_spell_index_ids=("lineage-many",),
    )
    _attach_projection_backed_viewer(space, viewer)
    owner_conduit = SimpleNamespace(
        has_live_creation=lambda *, spell_name=None, spell=None, spellframe=None, binding_name=None: True
    )
    space.command_system._aether = SimpleNamespace(
        _get_conduit_by_id=lambda conduit_id, frame_name: owner_conduit,
    )

    status = space.command_system.describe_spell_status_by_source_id(
        "ops-spellbook:many-sha",
        frame_name="ops",
    )

    assert status["is_published"] is True
    assert status["is_command_enabled"] is True
    assert status["is_static_supported"] is False
    assert status["is_live"] is True
    assert status["is_available"] is False
    assert status["reason"] == "unsupported_static_existence"


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
    _attach_projection_backed_viewer(space, viewer)
    owner_conduit = SimpleNamespace(
        meld_existing_spell=lambda *, spell_name=None, spell=None, spellframe=None, binding_name=None: (_ for _ in ()).throw(
            ValueError("Spell 'sha-1' is not live.")
        )
    )
    monkeypatch.setattr(
        type(space.command_system)._aether,
        "_get_conduit_by_id",
        lambda conduit_id, frame_name: owner_conduit,
    )

    with pytest.raises(
        ValueError,
        match="Spell lineage 'lineage-1' is not live in frame 'ops'",
    ):
        space.command_system.get_spell_by_index_id(
            "lineage-1",
            frame_name="ops",
        )


def test_capability_room_allows_direct_spell_runtime_object_access() -> None:
    """
    Verify capability rooms allow direct spell runtime-object access.

    Returns:
        None.
    """
    space = CapabilityRiftSpace(owner_rift_id="rift-1", space_name="main")
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
    _attach_projection_backed_viewer(space, viewer)
    spell = object()
    owner_conduit = SimpleNamespace(
        get_spell_by_index_id=lambda spell_index_id: (
            spell if spell_index_id == "lineage-1" else None
        )
    )
    space.command_system._aether = SimpleNamespace(
        get_conduit_by_id=lambda conduit_id, frame_name: owner_conduit,
    )

    assert (
        space.command_system.get_spell_by_index_id(
            "lineage-1",
            frame_name="ops",
        ) is spell
    )


def test_capability_rift_can_attach_to_automatic_target_frame_when_rift_enabled() -> None:
    """
    Verify capability Rift can attach to an automatic target frame.

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
        RiftSpaceType.capability
    )
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="ops-capability")
    rift.target_frame("ops")

    assert isinstance(rift.space, CapabilityRiftSpace)


def test_capability_room_broad_access_still_respects_automatic_runtime_floor() -> None:
    """
    Verify capability can fetch real objects but lower runtime still rejects automatic-only dynamic operations.

    Returns:
        None.
    """
    configuration = Configuration(aether_frame="ops_capability_auto")
    configuration.automatic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.set_property("rift_enabled", True)
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    spellbook = Spellbook(
        aetheric_frame="ops_capability_auto",
        configuration=configuration,
    )
    conduit = spellbook.conjure(name="root")
    try:
        space = CapabilityRiftSpace(owner_rift_id="rift-1", space_name="main")
        viewer = _build_descriptor_backed_viewer("ops")
        descriptor = viewer._get_required_frame_descriptor("ops")
        descriptor.upsert_conduit_record(
            ConduitRecord(
                conduit_id=conduit.id,
                root_conduit_id=conduit.id,
                frame_name="ops",
                origin_spellbook_id=spellbook.id,
                payload=ConduitDescriptorPayload(
                    conduit_name=conduit.name,
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
            enabled_conduit_ids=(conduit.id,),
        )
        _attach_projection_backed_viewer(space, viewer)
        space.command_system._aether = SimpleNamespace(
            get_conduit_by_id=lambda conduit_id, frame_name: conduit,
        )
        capability_conduit = space.command_system.get_conduit_by_id(
            conduit.id,
            frame_name="ops",
        )
        space.workstation.bind_object("root", capability_conduit, weak_ref=False)
        space.workstation.set_target("root", store="objects")

        with pytest.raises(RuntimeError, match="Dynamic environment is not enabled"):
            space.command_system.execute_target_method("get_conduit_cloud")
    finally:
        conduit.cleanup()
        spellbook.cleanup()


def test_capability_room_can_access_conduit_cloud_on_dynamic_frame() -> None:
    """
    Verify capability can access the conduit cloud on a dynamic frame.

    Returns:
        None.
    """
    configuration = Configuration(aether_frame="ops_capability_dynamic")
    configuration.dynamic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.set_property("rift_enabled", True)
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    spellbook = Spellbook(
        aetheric_frame="ops_capability_dynamic",
        configuration=configuration,
    )
    conduit = spellbook.conjure(name="root", automatic=False)
    try:
        space = CapabilityRiftSpace(owner_rift_id="rift-1", space_name="main")
        viewer = _build_descriptor_backed_viewer("ops")
        descriptor = viewer._get_required_frame_descriptor("ops")
        descriptor.upsert_conduit_record(
            ConduitRecord(
                conduit_id=conduit.id,
                root_conduit_id=conduit.id,
                frame_name="ops",
                origin_spellbook_id=spellbook.id,
                payload=ConduitDescriptorPayload(
                    conduit_name=conduit.name,
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
            enabled_conduit_ids=(conduit.id,),
        )
        _attach_projection_backed_viewer(space, viewer)
        space.command_system._aether = SimpleNamespace(
            get_conduit_cloud=lambda frame_name: conduit.get_conduit_cloud(),
        )
        conduit_cloud = space.command_system.get_conduit_cloud(frame_name="ops")

        assert conduit_cloud.has_conduit_name("root") is True
    finally:
        conduit.cleanup()
        spellbook.cleanup()


def test_capability_room_can_create_lesser_conduit_on_automatic_frame() -> None:
    """
    Verify capability can create lesser conduits on an automatic frame.

    Returns:
        None.
    """
    configuration = Configuration(aether_frame="ops_capability_auto_lesser")
    configuration.automatic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.set_property("rift_enabled", True)
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    spellbook = Spellbook(
        aetheric_frame="ops_capability_auto_lesser",
        configuration=configuration,
    )
    conduit = spellbook.conjure(name="root")
    try:
        space = CapabilityRiftSpace(owner_rift_id="rift-1", space_name="main")
        viewer = _build_descriptor_backed_viewer("ops")
        descriptor = viewer._get_required_frame_descriptor("ops")
        descriptor.upsert_conduit_record(
            ConduitRecord(
                conduit_id=conduit.id,
                root_conduit_id=conduit.id,
                frame_name="ops",
                origin_spellbook_id=spellbook.id,
                payload=ConduitDescriptorPayload(
                    conduit_name=conduit.name,
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
            enabled_conduit_ids=(conduit.id,),
        )
        _attach_projection_backed_viewer(space, viewer)
        space.command_system._aether = SimpleNamespace(
            get_conduit_by_id=lambda conduit_id, frame_name: conduit,
        )
        lesser = space.command_system.create_lesser_conduit(
            conduit.id,
            frame_name="ops",
        )

        assert lesser.id != conduit.id
    finally:
        conduit.cleanup()
        spellbook.cleanup()


def test_capability_room_can_manage_clusters_on_dynamic_frame() -> None:
    """
    Verify capability can create, join, and leave clusters on a dynamic frame.

    Returns:
        None.
    """
    configuration = Configuration(aether_frame="ops_capability_dynamic_cluster")
    configuration.dynamic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.set_property("rift_enabled", True)
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    spellbook = Spellbook(
        aetheric_frame="ops_capability_dynamic_cluster",
        configuration=configuration,
    )
    conduit = spellbook.conjure(name="root", automatic=False)
    try:
        space = CapabilityRiftSpace(owner_rift_id="rift-1", space_name="main")
        viewer = _build_descriptor_backed_viewer("ops")
        descriptor = viewer._get_required_frame_descriptor("ops")
        descriptor.upsert_conduit_record(
            ConduitRecord(
                conduit_id=conduit.id,
                root_conduit_id=conduit.id,
                frame_name="ops",
                origin_spellbook_id=spellbook.id,
                payload=ConduitDescriptorPayload(
                    conduit_name=conduit.name,
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
            enabled_conduit_ids=(conduit.id,),
        )
        _attach_projection_backed_viewer(space, viewer)
        space.command_system._aether = SimpleNamespace(
            get_conduit_by_id=lambda conduit_id, frame_name: conduit,
        )
        space.command_system.create_cluster(
            conduit.id,
            "alpha",
            frame_name="ops",
        )
        space.command_system.join_cluster(
            conduit.id,
            "alpha",
            frame_name="ops",
        )
        clusters = space.command_system.list_clusters(
            conduit.id,
            frame_name="ops",
        )
        space.command_system.leave_cluster(
            conduit.id,
            "alpha",
            frame_name="ops",
        )
        after_leave = space.command_system.list_clusters(
            conduit.id,
            frame_name="ops",
        )

        assert clusters == ("alpha",)
        assert after_leave == tuple()
    finally:
        conduit.cleanup()
        spellbook.cleanup()


def test_capability_room_can_link_on_dynamic_frame() -> None:
    """
    Verify capability can link conduits on a dynamic frame.

    Returns:
        None.
    """
    configuration = Configuration(aether_frame="ops_capability_dynamic_link")
    configuration.dynamic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.set_property("rift_enabled", True)
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    left_spellbook = Spellbook(
        aetheric_frame="ops_capability_dynamic_link",
        configuration=configuration,
    )
    right_spellbook = Spellbook(
        aetheric_frame="ops_capability_dynamic_link",
        configuration=configuration,
    )
    left_conduit = left_spellbook.conjure(name="left", automatic=False)
    right_conduit = right_spellbook.conjure(name="right", automatic=False)
    try:
        space = CapabilityRiftSpace(owner_rift_id="rift-1", space_name="main")
        viewer = _build_descriptor_backed_viewer("ops")
        descriptor = viewer._get_required_frame_descriptor("ops")
        for current_conduit, spellbook in (
            (left_conduit, left_spellbook),
            (right_conduit, right_spellbook),
        ):
            descriptor.upsert_conduit_record(
                ConduitRecord(
                    conduit_id=current_conduit.id,
                    root_conduit_id=current_conduit.id,
                    frame_name="ops",
                    origin_spellbook_id=spellbook.id,
                    payload=ConduitDescriptorPayload(
                        conduit_name=current_conduit.name,
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
            enabled_conduit_ids=(left_conduit.id, right_conduit.id),
        )
        _attach_projection_backed_viewer(space, viewer)
        space.command_system._aether = SimpleNamespace(
            get_conduit_by_id=lambda conduit_id, frame_name: (
                left_conduit if conduit_id == left_conduit.id else right_conduit
            ),
        )
        linked = space.command_system.link(
            left_conduit.id,
            right_conduit.id,
            frame_name="ops",
        )
        links = space.command_system.get_links(
            left_conduit.id,
            frame_name="ops",
        )

        assert linked is True
        assert links == (right_conduit,)
    finally:
        left_conduit.cleanup()
        right_conduit.cleanup()
        left_spellbook.cleanup()
        right_spellbook.cleanup()


def test_capability_room_can_meld_through_command_surface() -> None:
    """
    Verify capability can call the shared command-level `meld(...)` helper.

    Returns:
        None.
    """
    space = CapabilityRiftSpace(owner_rift_id="rift-1", space_name="main")
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
    _attach_projection_backed_viewer(space, viewer)
    runtime_object = object()
    owner_conduit = SimpleNamespace(
        meld=lambda **kwargs: runtime_object,
    )
    space.command_system._aether = SimpleNamespace(
        get_conduit_by_id=lambda conduit_id, frame_name: owner_conduit,
    )

    result = space.command_system.meld(
        "ops-conduit",
        spell="sha-1",
        frame_name="ops",
    )

    assert result is runtime_object


def test_capability_room_can_meld_existing_spell_through_command_surface() -> None:
    """
    Verify capability can call the shared reuse-only `meld_existing_spell(...)` helper.

    Returns:
        None.
    """
    space = CapabilityRiftSpace(owner_rift_id="rift-1", space_name="main")
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
    _attach_projection_backed_viewer(space, viewer)
    runtime_object = object()
    owner_conduit = SimpleNamespace(
        meld_existing_spell=lambda **kwargs: runtime_object,
    )
    space.command_system._aether = SimpleNamespace(
        get_conduit_by_id=lambda conduit_id, frame_name: owner_conduit,
    )

    result = space.command_system.meld_existing_spell(
        "ops-conduit",
        spell="sha-1",
        frame_name="ops",
    )

    assert result is runtime_object


def test_static_command_system_denies_shared_topology_mutation_methods() -> None:
    """
    Verify static rooms deny shared topology-mutation command methods.

    Returns:
        None.
    """
    space = StaticRiftSpace(owner_rift_id="rift-1", space_name="main")
    denied_calls = (
        lambda: space.command_system.create_lesser_conduit("conduit-1"),
        lambda: space.command_system.create_cluster("conduit-1", "alpha"),
        lambda: space.command_system.delete_cluster("conduit-1", "alpha"),
        lambda: space.command_system.join_cluster("conduit-1", "alpha"),
        lambda: space.command_system.leave_cluster("conduit-1", "alpha"),
        lambda: space.command_system.link("left", "right"),
        lambda: space.command_system.sever_link("left", "right"),
    )

    for denied_call in denied_calls:
        with pytest.raises(
                ValueError,
                match="Static command surface does not allow topology mutation method",
        ):
            denied_call()


def test_static_command_system_denies_direct_spell_activation_methods() -> None:
    """
    Verify static rooms deny direct command-level spell activation helpers.

    Returns:
        None.
    """
    space = StaticRiftSpace(owner_rift_id="rift-1", space_name="main")
    with pytest.raises(
            ValueError,
            match="Static command surface does not allow spell activation method 'meld'",
    ):
        space.command_system.meld("conduit-1", spell="sha-1")


def test_static_command_system_allows_meld_existing_spell() -> None:
    """
    Verify static rooms allow the reuse-only spell activation helper.

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
    _attach_projection_backed_viewer(space, viewer)
    runtime_object = object()
    owner_conduit = SimpleNamespace(
        meld_existing_spell=lambda **kwargs: runtime_object,
    )
    space.command_system._aether = SimpleNamespace(
        get_conduit_by_id=lambda conduit_id, frame_name: owner_conduit,
    )

    result = space.command_system.meld_existing_spell(
        "ops-conduit",
        spell="sha-1",
        frame_name="ops",
    )

    assert result is runtime_object


def test_static_command_system_denies_list_clusters() -> None:
    """
    Verify static rooms do not expose cluster topology through command.

    Returns:
        None.
    """
    space = StaticRiftSpace(owner_rift_id="rift-1", space_name="main")

    with pytest.raises(
            ValueError,
            match="Static command surface does not allow cluster query method 'list_clusters'",
    ):
        space.command_system.list_clusters("conduit-1")


def test_static_command_system_lists_only_supported_methods() -> None:
    """
    Verify static command introspection excludes denied topology-mutation methods.

    Returns:
        None.
    """
    space = StaticRiftSpace(owner_rift_id="rift-1", space_name="main")

    supported_methods = space.command_system.list_supported_command_methods()

    assert "create_lesser_conduit" not in supported_methods
    assert "create_cluster" not in supported_methods
    assert "list_clusters" not in supported_methods
    assert "link" not in supported_methods
    assert "sever_link" not in supported_methods
    assert "meld" not in supported_methods
    assert "meld_existing_spell" in supported_methods
    assert "get_conduit_by_id" in supported_methods
    assert "get_conduit_cloud" in supported_methods


def test_capability_command_system_lists_shared_manual_runtime_methods() -> None:
    """
    Verify capability command introspection exposes the shared manual-runtime methods.

    Returns:
        None.
    """
    space = CapabilityRiftSpace(owner_rift_id="rift-1", space_name="main")

    supported_methods = space.command_system.list_supported_command_methods()

    assert "get_conduit_cloud" in supported_methods
    assert "create_lesser_conduit" in supported_methods
    assert "create_cluster" in supported_methods
    assert "delete_cluster" in supported_methods
    assert "join_cluster" in supported_methods
    assert "leave_cluster" in supported_methods
    assert "list_clusters" in supported_methods
    assert "link" in supported_methods
    assert "sever_link" in supported_methods
    assert "get_links" in supported_methods
    assert "meld" in supported_methods
    assert "meld_existing_spell" in supported_methods


def test_command_system_can_delegate_conduit_introspection_helpers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify the shared command surface delegates the conduit introspection helpers.

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
        enabled_conduit_ids=("ops-conduit",),
    )
    _attach_projection_backed_viewer(space, viewer)
    lesser = object()
    initiated = object()
    provider = object()
    contract_spell = object()
    resolution_state = object()
    owner_conduit = SimpleNamespace(
        get_lesser_conduit=lambda conduit_id: lesser,
        get_initiated_conduit=lambda conduit_id: initiated,
        get_provider_conduit=lambda conduit_id: provider,
        get_initiated_conduits=lambda: [initiated],
        get_provider_conduits=lambda: [provider],
        get_contracted_conduits=lambda: [("peer", provider)],
        get_spell_in_contracts=lambda spell_id: ("peer", contract_spell),
        get_spells_in_contract_by_conduit=lambda conduit_id: {
            "outbound": [("sha-1", contract_spell)]
        },
        get_spells_in_contract_by_conduit_name=lambda conduit_name: {
            "outbound": [("sha-1", contract_spell)]
        },
        describe_spells_in_conduit=lambda: [{"spell_id": "sha-1"}],
        get_resolution_state=lambda: resolution_state,
    )
    monkeypatch.setattr(
        type(space.command_system),
        "_get_conduit_by_id_locked",
        lambda self, conduit_id, *, frame_name=None: owner_conduit,
    )

    assert (
        space.command_system.get_lesser_conduit(
            "ops-conduit",
            "lesser-1",
            frame_name="ops",
        ) is lesser
    )
    assert (
        space.command_system.get_initiated_conduit(
            "ops-conduit",
            "peer",
            frame_name="ops",
        ) is initiated
    )
    assert (
        space.command_system.get_provider_conduit(
            "ops-conduit",
            "peer",
            frame_name="ops",
        ) is provider
    )
    assert space.command_system.get_initiated_conduits(
        "ops-conduit",
        frame_name="ops",
    ) == (initiated,)
    assert space.command_system.get_provider_conduits(
        "ops-conduit",
        frame_name="ops",
    ) == (provider,)
    assert space.command_system.get_contracted_conduits(
        "ops-conduit",
        frame_name="ops",
    ) == [("peer", provider)]
    assert space.command_system.get_spell_in_contracts(
        "ops-conduit",
        "sha-1",
        frame_name="ops",
    ) == ("peer", contract_spell)
    assert space.command_system.get_spells_in_contract_by_conduit(
        "ops-conduit",
        "peer",
        frame_name="ops",
    ) == {"outbound": [("sha-1", contract_spell)]}
    assert space.command_system.get_spells_in_contract_by_conduit_name(
        "ops-conduit",
        "peer-name",
        frame_name="ops",
    ) == {"outbound": [("sha-1", contract_spell)]}
    assert space.command_system.describe_spells_in_conduit(
        "ops-conduit",
        frame_name="ops",
    ) == [{"spell_id": "sha-1"}]
    assert (
        space.command_system.get_resolution_state(
            "ops-conduit",
            frame_name="ops",
        ) is resolution_state
    )


def test_command_system_can_delegate_spell_query_and_snapshot_helpers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify the shared command surface delegates spell query/snapshot helpers.

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
        enabled_conduit_ids=("ops-conduit",),
    )
    _attach_projection_backed_viewer(space, viewer)
    spellspace = object()
    snapshot = {"conduit_id": "ops-conduit"}
    owner_conduit = SimpleNamespace(
        get_active_spellspace=lambda: spellspace,
        find_spell_id=lambda spellframe, spell_name, binding_name: "sha-1",
        find_spell_key=lambda spellframe, spell_name, binding_name: (
            spellframe,
            binding_name,
        ),
        get_spell_permissions=lambda spell_id: "create",
        snapshot_state=lambda: snapshot,
    )
    monkeypatch.setattr(
        type(space.command_system),
        "_get_conduit_by_id_locked",
        lambda self, conduit_id, *, frame_name=None: owner_conduit,
    )

    assert (
        space.command_system.get_active_spellspace(
            "ops-conduit",
            frame_name="ops",
        ) is spellspace
    )
    assert space.command_system.find_spell_id(
        "ops-conduit",
        "OpsFrame",
        "OpsSpell",
        "ops_binding",
        frame_name="ops",
    ) == "sha-1"
    assert space.command_system.find_spell_key(
        "ops-conduit",
        "OpsFrame",
        "OpsSpell",
        "ops_binding",
        frame_name="ops",
    ) == ("OpsFrame", "ops_binding")
    assert space.command_system.get_spell_permissions(
        "ops-conduit",
        "sha-1",
        frame_name="ops",
    ) == "create"
    assert space.command_system.snapshot_state(
        "ops-conduit",
        frame_name="ops",
    ) == snapshot


def test_rift_space_can_delegate_frame_surface_calls_to_attached_viewer() -> None:
    """
    Verify a RiftSpace delegates frame-surface calls through the attached viewer.

    Returns:
        None.
    """
    space = RiftSpace(owner_rift_id="rift-1", space_name="main")
    viewer = _build_descriptor_backed_viewer("ops")
    _attach_projection_backed_viewer(space, viewer)

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
    _attach_projection_backed_viewer(space, viewer)

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
    _attach_projection_backed_viewer(space, viewer)

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
    rift.target_frame("ops")

    assert rift.list_assigned_frame_names() == ("ops",)


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
    rift.target_frame("ops")

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

    rift.target_frame("ops")

    assert rift.get_frame_link_contract("ops").frame_name == "ops"


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
    rift.target_frame("ops", contract_name="ops_contract")

    viewer = rift.get_frame_viewer()

    assert rift.get_frame_link_contract("ops").get_selected_contract_name() == "ops_contract"
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
    rift.target_frame("ops")

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
    rift.target_frame("ops")
    space = rift.space
    viewer = rift.get_frame_viewer()

    assert viewer is space.frame_viewer
    assert rift.get_frame_viewer() is viewer
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
        rift.get_frame_viewer()

    with pytest.raises(ValueError, match="has no attached frame viewer"):
        rift.get_frame_viewer()


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
    rift.target_frame("ops")

    assert rift.list_assigned_frame_names() == ("ops",)


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


def test_codegen_rift_requires_target_frame_ai_native_enabled() -> None:
    """
    Verify codegen AR refuses frames that do not enable AI-native mode.

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
        RiftSpaceType.codegen
    )
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="ops-codegen")

    with pytest.raises(ValueError, match="ai_native_enabled"):
        rift.target_frame("ops")


def test_codegen_rift_requires_dynamic_target_frame_system_state() -> None:
    """
    Verify codegen AR refuses frames that are not in dynamic system_state.

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
        RiftSpaceType.codegen
    )
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="ops-codegen")

    with pytest.raises(ValueError, match="dynamic system_state"):
        rift.target_frame("ops")


def test_codegen_rift_can_attach_to_dynamic_ai_native_target_frame() -> None:
    """
    Verify codegen AR attaches successfully when the target frame is fully
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
        RiftSpaceType.codegen
    )
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="ops-codegen")
    rift.target_frame("ops")

    assert rift.list_assigned_frame_names() == ("ops",)
    assert rift.configuration.get_property("space_type") == RiftSpaceType.codegen


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
    rift.target_frame("ops")

    assert rift.list_assigned_frame_names() == ("ops",)
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


def test_shared_and_private_nexus_frames_are_realized_only_on_request() -> None:
    """
    Verify shared and one-per-workspace Nexus frames are realized only on
    explicit request.

    Returns:
        None.
    """
    shared_nexus = _create_enabled_nexus()
    shared_rift = shared_nexus.create_rift(rift_name="shared")
    assert "aetheric_frame_system" not in Aether()._aetheric_frames
    shared_frame = shared_rift.create_nexus_frame()
    assert shared_frame.name == "aetheric_frame_system"
    assert shared_rift.get_nexus_frame() is shared_nexus.get_nexus_frame_for_rift(shared_rift.id)

    isolated_nexus = Nexus()
    configuration = isolated_nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_nexus_frame_mode("one_per_workspace")
    configuration.with_max_nexus_frame_count(2)
    isolated_nexus.enable(configuration)

    isolated_rift = isolated_nexus.create_rift(rift_name="isolated")
    private_frame_name = "aetheric_frame_system:{0}".format(isolated_rift.id)
    assert private_frame_name not in Aether()._aetheric_frames
    private_frame = isolated_rift.create_nexus_frame()
    assert private_frame.name == private_frame_name


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
    shared_frame_name = "aetheric_frame_system"

    first.create_nexus_frame()
    second.create_nexus_frame()

    assert shared_frame_name in aether._aetheric_frames

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
    frame_name = rift.create_nexus_frame().name

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
    frame_name = rift.create_nexus_frame().name

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

    assert first.create_nexus_frame() is second.create_nexus_frame()


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
    second_frame = second.create_nexus_frame()

    with pytest.raises(ValueError, match="private Nexus frame"):
        nexus.get_nexus_frame_for_rift(first.id, frame_name=second_frame.name)


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

    with pytest.raises(ValueError, match="explicit frame_name"):
        first.get_nexus_frame()

    shared_frame = first.create_nexus_frame(frame_name="ops")
    looked_up_frame = second.get_nexus_frame(frame_name="ops")

    assert looked_up_frame is shared_frame
    assert "ops" in second.list_accessible_nexus_frame_names()


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
            rift_name="manual",
        )

    nexus.enable(configuration)
    nexus.disable()
    with pytest.raises(RuntimeError, match="enabled Nexus"):
        Rift(
            nexus,
            configuration=rift_configuration,
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
            rift_name="manual",
        )

