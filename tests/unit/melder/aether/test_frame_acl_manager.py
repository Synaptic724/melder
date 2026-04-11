import threading

import pytest

from melder.aether.nexus.acl.frame_acl_builder import FrameACLBuilder
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
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
    assert manager._get_named_frame_acl_configuration("ops") is current
    assert manager._list_named_frame_acl_configuration_names("ops") == ["default"]


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


def test_frame_acl_manager_can_register_and_get_named_frame_acl_configuration() -> None:
    """
    Verify the manager can register and resolve a named ACL configuration.

    Returns:
        None.
    """
    manager = FrameACLManager()
    named_configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        manager._get_current_frame_acl_configuration("ops"),
        reason="named",
    )
    named_configuration.finalize()

    registered = manager._register_named_frame_acl_configuration(
        "ops",
        named_configuration,
        contract_name="ops_contract",
    )

    assert registered is named_configuration
    assert (
        manager._get_named_frame_acl_configuration("ops", "ops_contract")
        is named_configuration
    )
    assert manager._list_named_frame_acl_configuration_names("ops") == [
        "default",
        "ops_contract",
    ]


def test_frame_acl_manager_rejects_duplicate_named_contract_name() -> None:
    """
    Verify the manager rejects duplicate contract names for one frame.

    Returns:
        None.
    """
    manager = FrameACLManager()
    first_named_configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        manager._get_current_frame_acl_configuration("ops"),
        reason="named-1",
    )
    first_named_configuration.finalize()
    second_named_configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        manager._get_current_frame_acl_configuration("ops"),
        reason="named-2",
    )
    second_named_configuration.finalize()

    manager._register_named_frame_acl_configuration(
        "ops",
        first_named_configuration,
        contract_name="ops_contract",
    )

    with pytest.raises(ValueError, match="already exists"):
        manager._register_named_frame_acl_configuration(
            "ops",
            second_named_configuration,
            contract_name="ops_contract",
        )


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
    assert manager._lock is None


def test_frame_acl_manager_exposes_identity_version_and_profile_snapshot_copy() -> None:
    """
    Verify id/version accessors and profile snapshots expose detached views.

    Returns:
        None.
    """
    manager = FrameACLManager()
    profile = manager._create_frame_acl_profile("support")

    snapshot = manager.frame_acl_profiles_by_name
    snapshot.clear()

    assert manager.id is not None
    assert manager.version == "0.0.1"
    assert snapshot == {}
    assert manager._get_required_frame_acl_profile("support") is profile


def test_frame_acl_manager_profile_builder_property_returns_builder_singleton() -> None:
    """
    Verify the manager exposes one stable profile builder object.

    Returns:
        None.
    """
    manager = FrameACLManager()

    assert manager.frame_acl_profile_builder is manager._frame_acl_profile_builder


def test_frame_acl_manager_insert_without_select_keeps_current_and_advances_head() -> None:
    """
    Verify non-selecting inserts validate and advance head without changing current.

    Returns:
        None.
    """
    manager = FrameACLManager()
    original = manager._get_current_frame_acl_configuration("ops")
    draft = FrameACLConfiguration.create_new_from_acl_configuration(
        original,
        reason="head_only",
    )
    draft.finalize()

    inserted = manager._insert_head_frame_acl_configuration(
        "ops",
        draft,
        select_as_current=False,
    )

    assert inserted is draft
    assert manager._get_head_frame_acl_configuration("ops") is draft
    assert manager._get_current_frame_acl_configuration("ops") is original


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


def test_frame_acl_manager_register_view_profile_delegates_to_builder() -> None:
    """
    Verify custom view profiles are registered through the shared builder.

    Returns:
        None.
    """
    manager = FrameACLManager()
    view_profile = FrameACLViewProfile(
        "custom_view",
        minimum_spell_payload_type="detailed",
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
            minimum_spell_payload_type="detailed",
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


def test_frame_acl_manager_registering_duplicate_profile_name_cleans_displaced_profile() -> None:
    """
    Verify replacing a distinct composed profile cleans the displaced instance.

    Returns:
        None.
    """
    manager = FrameACLManager()
    first_profile = FrameACLProfile(
        "support",
        view_profile=FrameACLViewProfile.create_safe(),
        codegen_profile=FrameACLCodegenProfile.create_safe(),
    )
    second_profile = FrameACLProfile(
        "support",
        view_profile=FrameACLViewProfile.create_hybrid(),
        codegen_profile=FrameACLCodegenProfile.create_permissive(),
    )

    manager._register_frame_acl_profile(first_profile)
    manager._register_frame_acl_profile(second_profile)

    assert first_profile.cleaned is True
    assert manager._get_required_frame_acl_profile("support") is second_profile


def test_frame_acl_manager_profile_registry_get_list_and_remove_contracts() -> None:
    """
    Verify profile registry lookup, listing, and removal semantics.

    Returns:
        None.
    """
    manager = FrameACLManager()
    profile = manager._create_frame_acl_profile("support")

    assert manager._list_frame_acl_profile_names() == ["support"]
    assert manager._get_required_frame_acl_profile("support") is profile
    assert manager._remove_frame_acl_profile("support") is True
    assert profile.cleaned is True
    assert manager._remove_frame_acl_profile("support") is False

    with pytest.raises(KeyError, match="support"):
        manager._get_required_frame_acl_profile("support")


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

