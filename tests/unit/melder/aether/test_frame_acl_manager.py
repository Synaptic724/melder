import threading

import pytest

from melder.aether.nexus.acl.builder.frame_acl_builder import FrameACLBuilder
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.frame_acl_container import FrameACLContainer
from melder.aether.nexus.frame_acl_manager import FrameACLManager
from tests._nexus_viewer_matrix_support import build_descriptor


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


def test_frame_acl_manager_current_bundle_and_same_name_named_config_work() -> None:
    """
    Verify current bundle assembly and same-name named registration work.

    Returns:
        None.
    """
    manager = FrameACLManager()
    current = manager._get_current_frame_acl_configuration("ops")

    assert current.frame_name == "ops"
    assert manager._get_named_frame_acl_configuration("ops") is not None
    assert manager._list_named_frame_acl_configuration_names("ops") == ["default"]

    named_configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        current,
        reason="named",
    )
    named_configuration.finalize()

    registered = manager._register_named_frame_acl_configuration(
        "ops",
        named_configuration,
        contract_name="ops_contract",
    )

    assert registered.frame_name == "ops"
    assert manager._list_named_frame_acl_configuration_names("ops") == [
        "default",
        "ops_contract",
    ]
    assert (
        manager._get_named_frame_acl_configuration("ops", "ops_contract").to_json_dict()
        == named_configuration.to_json_dict()
    )


def test_frame_acl_manager_exposes_family_current_configs() -> None:
    """
    Verify manager exposes current family configs for one frame/contract.

    Returns:
        None.
    """
    manager = FrameACLManager()

    view_configuration = manager._get_current_view_acl_configuration("ops")
    command_configuration = manager._get_current_command_acl_configuration("ops")
    codegen_configuration = manager._get_current_codegen_acl_configuration("ops")

    assert view_configuration.profile_name == "safe"
    assert command_configuration.profile_name == "safe"
    assert codegen_configuration.profile_name == "safe"


def test_frame_acl_manager_validates_configuration_against_descriptor() -> None:
    """
    Verify descriptor-backed validation delegates through the frame container.

    Returns:
        None.
    """
    manager = FrameACLManager()
    configuration = manager._get_current_frame_acl_configuration("ops")
    frame_descriptor = build_descriptor("ops")

    assert manager._validate_frame_acl_configuration_against_descriptor(
        "ops",
        configuration,
        frame_descriptor,
    ) is True


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
    assert not hasattr(manager, '_lock')
    assert not hasattr(manager, '_frame_acl_containers_by_name')


def test_frame_acl_manager_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Verify cleanup returns early when another thread already cleaned the manager.

    Returns:
        None.
    """

    class _CoordinatedLock:
        def __init__(self) -> None:
            self._entered_first = threading.Event()
            self._second_attempted = threading.Event()
            self._lock = threading.RLock()

        def __enter__(self):
            if self._entered_first.is_set():
                self._second_attempted.set()
            self._lock.acquire()
            if not self._entered_first.is_set():
                self._entered_first.set()
                assert self._second_attempted.wait(timeout=1.0)
            return self

        def __exit__(self, exc_type, exc, tb):
            self._lock.release()

    manager = FrameACLManager()
    manager._ensure_frame_acl_container("ops")
    coordinated_lock = _CoordinatedLock()
    manager._lock = coordinated_lock

    thread_results = []

    def _run_cleanup() -> None:
        manager.cleanup()
        thread_results.append(True)

    first = threading.Thread(target=_run_cleanup)
    second = threading.Thread(target=_run_cleanup)
    first.start()
    coordinated_lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join(timeout=1.0)
    second.join(timeout=1.0)

    assert thread_results == [True, True]
    assert manager.cleaned is True
    assert not hasattr(manager, '_lock')
