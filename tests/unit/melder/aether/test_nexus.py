import logging

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.nexus.rift.rift import Rift
from melder.aether.nexus.configuration.rift_space_type import RiftSpaceType
from melder.aether.nexus.configuration.rift_configuration import RiftConfiguration
from melder.aether.nexus.nexus import Nexus
from melder.aether.nexus.rift.rift_space.rift_space import RiftSpace
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.configuration.system_state import SystemState


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
    frame_configuration.with_ai_profiles(rift_enabled)
    frame_configuration.with_ai_native(ai_native_enabled)
    aether._bind_configuration(frame_configuration, frame_name)


def test_nexus_is_singleton() -> None:
    """
    Verify `Nexus` enforces the singleton contract.

    Returns:
        None.
    """
    first = Nexus()
    second = Nexus()

    assert first is second


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
    assert rift.default_target_frame_name == "default"
    assert rift.nexus_frame_names == ("aetheric_frame_system",)
    assert rift.target_frame_names == ("default",)
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

    assert config.get_property("target_frame_name") == "default"
    assert config.get_property("auto_activate_on_program") is True
    assert config.get_property("auto_create_space") is False


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
    profile.with_target_frame_name("ops")
    profile.with_space_name("ops-room")
    nexus.register_rift_profile("ops_profile", profile)

    profiled_configuration = nexus.create_rift_configuration(profile_name="ops_profile")
    second_profiled_configuration = nexus.create_rift_configuration(profile_name="ops_profile")

    assert profiled_configuration is not second_profiled_configuration
    assert profiled_configuration.get_property("target_frame_name") == "ops"
    assert profiled_configuration.get_property("space_name") == "ops-room"
    assert profiled_configuration.consumed is False
    assert second_profiled_configuration.consumed is False


def test_rift_can_use_spaces_without_separate_state_object() -> None:
    """
    Verify a live Rift directly owns its room registry state.

    Returns:
        None.
    """
    nexus = _create_enabled_nexus()
    rift = nexus.create_rift(rift_name="alpha")

    space = RiftSpace(owner_rift_id=rift.id, space_name="main")
    rift.register_space(space)

    assert rift.get_space(space.space_id) is space
    assert rift.get_space_by_name("main") is space
    assert rift.active_space_id == space.space_id


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

    blocked_config = nexus.create_rift_configuration().with_target_frame_name("ops")
    with pytest.raises(ValueError, match="denied"):
        nexus.create_rift(configuration=blocked_config, rift_name="blocked")

    replacement_configuration = nexus.create_system_configuration()
    replacement_configuration.with_rift_creation_enabled(True)
    replacement_configuration.with_target_frame_override(True)
    replacement_configuration.with_allowed_target_frame_names(("default", "ops"))
    replacement_configuration.with_denied_target_frame_names(tuple())
    nexus.enable(replacement_configuration)
    allowed_config = nexus.create_rift_configuration().with_target_frame_name("ops")
    rift = nexus.create_rift(configuration=allowed_config, rift_name="allowed")

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

    rift_configuration = (
        nexus.create_rift_configuration()
        .with_target_frame_name("ops")
        .with_space_type(RiftSpaceType.static)
    )

    with pytest.raises(ValueError, match="rift_enabled"):
        nexus.create_rift(configuration=rift_configuration, rift_name="ops-static")


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

    rift_configuration = (
        nexus.create_rift_configuration()
        .with_target_frame_name("ops")
        .with_space_type(RiftSpaceType.dynamic)
    )

    with pytest.raises(ValueError, match="ai_native_enabled"):
        nexus.create_rift(configuration=rift_configuration, rift_name="ops-dynamic")


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

    rift_configuration = (
        nexus.create_rift_configuration()
        .with_target_frame_name("ops")
        .with_space_type(RiftSpaceType.dynamic)
    )

    with pytest.raises(ValueError, match="dynamic system_state"):
        nexus.create_rift(configuration=rift_configuration, rift_name="ops-dynamic")


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

    rift_configuration = (
        nexus.create_rift_configuration()
        .with_target_frame_name("ops")
        .with_space_type(RiftSpaceType.dynamic)
    )
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="ops-dynamic")

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

    rift_configuration = (
        nexus.create_rift_configuration()
        .with_target_frame_name("ops")
        .with_space_type(RiftSpaceType.static)
    )
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="ops-static")

    assert rift.target_frame_names == ("ops",)
    assert rift.configuration.get_property("space_type") == RiftSpaceType.static


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
        target_frame_names=("default",),
        default_target_frame_name="default",
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
            target_frame_names=("default",),
            default_target_frame_name="default",
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
            target_frame_names=("default",),
            default_target_frame_name="default",
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
            target_frame_names=("default",),
            default_target_frame_name="default",
            rift_name="manual",
        )
