from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.nexus.acl.profiles.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.profiles.frame_acl_profile import (
    FrameACLProfile,
)
from melder.aether.nexus.acl.profiles.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.aether.nexus.nexus import Nexus


def setup_function() -> None:
    """
    Reset singleton state before each Nexus ACL profile facade test.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()


def teardown_function() -> None:
    """
    Reset singleton state after each Nexus ACL profile facade test.

    Returns:
        None.
    """
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()


def test_nexus_exposes_acl_profile_version() -> None:
    """
    Verify Nexus exposes the manager-owned ACL version string.

    Returns:
        None.
    """
    nexus = Nexus(aether=Aether())

    assert nexus.get_frame_acl_version() == "0.0.1"


def test_nexus_profile_registry_facades_register_get_list_and_remove() -> None:
    """
    Verify Nexus facades the manager-owned ACL profile registry cleanly.

    Returns:
        None.
    """
    nexus = Nexus(aether=Aether())
    support_profile = FrameACLProfile(
        "support",
        view_profile=FrameACLViewProfile.create_default(),
        codegen_profile=FrameACLCodegenProfile.create_default(),
    )

    nexus.register_frame_acl_profile(support_profile)

    assert nexus.get_frame_acl_profile("support") is support_profile
    assert nexus.list_frame_acl_profile_names() == ["support"]
    assert nexus.remove_frame_acl_profile("support") is True
    assert support_profile.cleaned is True
    assert nexus.remove_frame_acl_profile("support") is False
