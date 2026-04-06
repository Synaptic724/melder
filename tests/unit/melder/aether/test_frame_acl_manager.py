import pytest

from melder.aether.nexus.acl.frame_acl_builder import FrameACLBuilder
from melder.aether.nexus.acl.frame_acl_container import FrameACLContainer
from melder.aether.nexus.acl.profiles.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.profiles.frame_acl_profile import (
    FrameACLProfile,
)
from melder.aether.nexus.acl.profiles.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.aether.nexus.frame_acl_manager import FrameACLManager


def test_frame_acl_manager_starts_empty() -> None:
    """
    Verify the ACL manager starts with no frame containers.

    Returns:
        None.
    """
    manager = FrameACLManager()

    assert manager.frame_acl_containers_by_name == {}


def test_frame_acl_manager_ensure_container_creates_and_reuses_container() -> None:
    """
    Verify ensure returns the same container for the same frame name.

    Returns:
        None.
    """
    manager = FrameACLManager()

    first_container = manager._ensure_frame_acl_container("ops")
    second_container = manager._ensure_frame_acl_container("ops")

    assert isinstance(first_container, FrameACLContainer)
    assert second_container is first_container


def test_frame_acl_manager_get_required_container_raises_when_missing() -> None:
    """
    Verify the manager raises when a required container does not exist.

    Returns:
        None.
    """
    manager = FrameACLManager()

    with pytest.raises(KeyError, match="ops"):
        manager._get_required_frame_acl_container("ops")


def test_frame_acl_manager_get_or_create_builder_returns_container_singleton() -> None:
    """
    Verify the manager returns the same builder object for repeated requests.

    Returns:
        None.
    """
    manager = FrameACLManager()

    first_builder = manager._get_or_create_frame_acl_builder("ops")
    second_builder = manager._get_or_create_frame_acl_builder("ops")

    assert isinstance(first_builder, FrameACLBuilder)
    assert second_builder is first_builder


def test_frame_acl_manager_remove_container_cleans_and_reports_status() -> None:
    """
    Verify remove cleans the container and reports whether it existed.

    Returns:
        None.
    """
    manager = FrameACLManager()
    container = manager._ensure_frame_acl_container("ops")

    assert manager._remove_frame_acl_container("ops") is True
    assert container.cleaned is True
    assert manager._remove_frame_acl_container("ops") is False


def test_frame_acl_manager_snapshot_returns_copy() -> None:
    """
    Verify the container snapshot is detached from internal manager state.

    Returns:
        None.
    """
    manager = FrameACLManager()
    manager._ensure_frame_acl_container("ops")

    snapshot = manager.frame_acl_containers_by_name
    snapshot.clear()

    assert "ops" in manager.frame_acl_containers_by_name


def test_frame_acl_manager_chain_facades_return_expected_configs() -> None:
    """
    Verify manager facades expose current/head/get/list behavior for one frame.

    Returns:
        None.
    """
    manager = FrameACLManager()
    container = manager._ensure_frame_acl_container("ops")
    current = manager._get_current_frame_acl_configuration("ops")
    head = manager._get_head_frame_acl_configuration("ops")
    fetched = manager._get_frame_acl_configuration("ops", current.configuration_id)

    assert current is container.frame_acl_configuration
    assert head is current
    assert fetched is current
    assert manager._list_frame_acl_configurations("ops") == [current]
    assert manager._list_frame_acl_configuration_ids("ops") == [current.configuration_id]


def test_frame_acl_manager_insert_select_rollback_and_create_from_facades() -> None:
    """
    Verify manager facades drive the chain mechanics for one frame.

    Returns:
        None.
    """
    manager = FrameACLManager()
    original = manager._get_current_frame_acl_configuration("ops")
    draft = manager._create_new_from_acl_configuration(
        "ops",
        original.configuration_id,
        reason="copy",
    )

    assert draft.locked is False
    draft.finalize()

    inserted = manager._insert_head_frame_acl_configuration(
        "ops",
        draft,
        select_as_current=True,
    )
    selected = manager._select_current_frame_acl_configuration(
        "ops",
        original.configuration_id,
    )
    rolled_back = manager._rollback_frame_acl_configuration(
        "ops",
        inserted.configuration_id,
    )

    assert inserted is draft
    assert draft.previous_configuration_id == original.configuration_id
    assert selected is original
    assert rolled_back is inserted


def test_frame_acl_manager_cleanup_cleans_all_owned_containers() -> None:
    """
    Verify cleanup cascades to all owned containers and clears manager state.

    Returns:
        None.
    """
    manager = FrameACLManager()
    ops_container = manager._ensure_frame_acl_container("ops")
    finance_container = manager._ensure_frame_acl_container("finance")

    manager.cleanup()

    assert ops_container.cleaned is True
    assert finance_container.cleaned is True
    assert manager._lock is None
    assert manager._frame_acl_containers_by_name is None


def test_frame_acl_manager_profile_builder_property_returns_builder_singleton() -> None:
    """
    Verify the manager exposes one stable profile builder object.

    Returns:
        None.
    """
    manager = FrameACLManager()

    assert manager.frame_acl_profile_builder is manager._frame_acl_profile_builder


def test_frame_acl_manager_register_view_profile_delegates_to_builder() -> None:
    """
    Verify custom view profiles are registered through the shared builder.

    Returns:
        None.
    """
    manager = FrameACLManager()
    view_profile = FrameACLViewProfile(
        "custom_view",
        minimum_spell_payload_profile_name="detailed",
    )

    manager._register_view_acl_profile(view_profile)

    assert manager._list_view_acl_profile_names() == [
        "safe",
        "hybrid",
        "permissive",
        "custom_view",
    ]
    assert (
        manager.frame_acl_profile_builder.get_required_view_profile("custom_view")
        is view_profile
    )


def test_frame_acl_manager_register_codegen_profile_delegates_to_builder() -> None:
    """
    Verify custom codegen profiles are registered through the shared builder.

    Returns:
        None.
    """
    manager = FrameACLManager()
    codegen_profile = FrameACLCodegenProfile("custom_codegen")

    manager._register_codegen_acl_profile(codegen_profile)

    assert manager._list_codegen_acl_profile_names() == [
        "safe",
        "hybrid",
        "permissive",
        "custom_codegen",
    ]
    assert (
        manager.frame_acl_profile_builder.get_required_codegen_profile(
            "custom_codegen"
        )
        is codegen_profile
    )


def test_frame_acl_manager_create_profile_uses_requested_catalog_names() -> None:
    """
    Verify composed profiles use the requested reusable catalog entries.

    Returns:
        None.
    """
    manager = FrameACLManager()
    manager._register_view_acl_profile(
        FrameACLViewProfile(
            "custom_view",
            minimum_spell_payload_profile_name="detailed",
        )
    )
    manager._register_codegen_acl_profile(FrameACLCodegenProfile("custom_codegen"))

    profile = manager._create_frame_acl_profile(
        "custom",
        view_profile_name="custom_view",
        codegen_profile_name="custom_codegen",
    )

    assert profile.view_profile.name == "custom_view"
    assert profile.codegen_profile.name == "custom_codegen"
    assert manager._get_required_frame_acl_profile("custom") is profile


def test_frame_acl_manager_register_frame_acl_profile_rejects_invalid_type() -> None:
    """
    Verify composed profile registration rejects invalid objects.

    Returns:
        None.
    """
    with pytest.raises(TypeError, match="frame_acl_profile must be a FrameACLProfile"):
        FrameACLManager()._register_frame_acl_profile(None)


def test_frame_acl_manager_cleanup_cleans_registered_profiles_and_builder() -> None:
    """
    Verify cleanup cascades into registered composed profiles and the builder.

    Returns:
        None.
    """
    manager = FrameACLManager()
    profile = manager._create_frame_acl_profile("support")
    builder = manager.frame_acl_profile_builder

    manager.cleanup()

    assert profile.cleaned is True
    assert builder.cleaned is True
    assert manager._frame_acl_profiles_by_name is None
    assert manager._frame_acl_profile_builder is None
