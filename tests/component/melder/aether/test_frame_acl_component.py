from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.nexus.nexus import Nexus


def test_component_acl_container_is_provisioned_once_per_descriptor_creation_flow() -> None:
    """
    Purpose:
        Verify the Nexus/descriptor ACL component flow provisions one container
        per frame and reuses it across repeated descriptor access.
    Contract:
        - Repeated descriptor creation for one frame returns the same
          descriptor.
        - The ACL manager holds one matching container for that frame.
        - The builder object remains the same across repeated accesses.
    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    nexus = Nexus(aether=aether)

    try:
        first_descriptor = nexus._get_or_create_frame_descriptor("ops")
        second_descriptor = nexus._get_or_create_frame_descriptor("ops")
        container = nexus._frame_acl_manager._get_required_frame_acl_container("ops")
        builder_first = container.frame_acl_builder
        builder_second = nexus._frame_acl_manager._get_or_create_frame_acl_builder("ops")

        assert second_descriptor is first_descriptor
        assert container.frame_name == "ops"
        assert builder_second is builder_first
        assert list(nexus._frame_acl_manager.frame_acl_containers_by_name.keys()) == ["ops"]
    finally:
        Nexus._reset_singleton_for_tests()
        Aether._reset_singleton_for_tests()
        AetherUtilitySystem._reset_singleton_for_tests()


def test_component_frame_detach_cleans_acl_container_even_without_managed_frame_state() -> None:
    """
    Purpose:
        Verify the facade-driven frame-detach cleanup removes ACL state even
        when no Nexus-managed frame state exists for that frame.
    Contract:
        - Descriptor creation provisions the ACL container.
        - `check_for_aetheric_frame(...)` removes the matching ACL container.
    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    nexus = Nexus(aether=aether)
    configuration = nexus.create_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    nexus.activate(configuration)

    try:
        nexus._get_or_create_frame_descriptor("ops")
        container = nexus._frame_acl_manager._get_required_frame_acl_container("ops")

        nexus.check_for_aetheric_frame("ops")

        assert container.cleaned is True
        assert "ops" not in nexus._frame_acl_manager.frame_acl_containers_by_name
    finally:
        Nexus._reset_singleton_for_tests()
        Aether._reset_singleton_for_tests()
        AetherUtilitySystem._reset_singleton_for_tests()
