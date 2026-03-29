import pytest

from melder.aether.nexus.rift.rift import Rift
from melder.aether.nexus.configuration.rift_configuration import RiftConfiguration
from melder.aether.nexus.nexus import Nexus
from melder.aether.nexus.rift_space.rift_space import RiftSpace


@pytest.fixture(autouse=True)
def fresh_nexus() -> None:
    """
    Reset the Nexus singleton around each test.

    Returns:
        None.
    """
    Nexus._reset_singleton_for_tests()
    yield
    Nexus._reset_singleton_for_tests()


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


def test_nexus_is_singleton() -> None:
    """
    Verify `Nexus` enforces the singleton contract.

    Returns:
        None.
    """
    first = Nexus()
    second = Nexus()

    assert first is second


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
    assert rift.default_system_frame_name == "aetheric_frame_system"
    assert rift.default_target_frame_name == "default"
    assert rift.system_frame_names == ("aetheric_frame_system",)
    assert rift.target_frame_names == ("default",)
    assert nexus.get_rift(rift.id) is rift
    assert nexus.get_rift_by_name("alpha") is rift
    assert nexus.list_rift_ids() == [rift.id]

    nexus.remove_rift(rift.id)
    assert nexus.has_rift(rift.id) is False


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


def test_shared_and_isolated_system_frame_names_are_assigned() -> None:
    """
    Verify system-frame topology settings shape the Rift's assigned internal
    frame names correctly.

    Returns:
        None.
    """
    shared_nexus = _create_enabled_nexus()
    shared_rift = shared_nexus.create_rift(rift_name="shared")
    assert shared_rift.default_system_frame_name == "aetheric_frame_system"

    isolated_nexus = Nexus()
    configuration = isolated_nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_system_frame_mode("one_per_workspace")
    configuration.with_max_system_frame_count(2)
    isolated_nexus.enable(configuration)

    isolated_rift = isolated_nexus.create_rift(rift_name="isolated")
    assert isolated_rift.default_system_frame_name.startswith("aetheric_frame_system:")
    assert isolated_rift.default_system_frame_name.endswith(isolated_rift.id)
    assert isolated_rift.system_frame_names == (isolated_rift.default_system_frame_name,)


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
        system_frame_names=("aetheric_frame_system",),
        default_system_frame_name="aetheric_frame_system",
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
            system_frame_names=("aetheric_frame_system",),
            default_system_frame_name="aetheric_frame_system",
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
            system_frame_names=("aetheric_frame_system",),
            default_system_frame_name="aetheric_frame_system",
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
            system_frame_names=("aetheric_frame_system",),
            default_system_frame_name="aetheric_frame_system",
            target_frame_names=("default",),
            default_target_frame_name="default",
            rift_name="manual",
        )
