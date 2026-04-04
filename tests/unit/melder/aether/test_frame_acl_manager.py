import pytest

from melder.aether.nexus.acl.frame_acl_builder import FrameACLBuilder
from melder.aether.nexus.acl.frame_acl_container import FrameACLContainer
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
