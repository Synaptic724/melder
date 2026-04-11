import threading

import pytest

from melder.aether.nexus.acl.builder.frame_acl_builder import FrameACLBuilder
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.frame_acl_container import FrameACLContainer
from melder.aether.nexus.acl.validator.compatibility.frame_acl_set_compatibility_validator import (
    FrameACLSetCompatibilityValidator,
)
from melder.aether.nexus.acl.validator.frame_acl_validator import FrameACLValidator


def test_frame_acl_container_builds_family_defaults() -> None:
    """
    Verify the container seeds default family chains and services.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")

    assert container.frame_name == "ops"
    assert isinstance(container.frame_acl_builder, FrameACLBuilder)
    assert isinstance(container.frame_acl_configuration, FrameACLConfiguration)
    assert isinstance(container.frame_acl_validator, FrameACLValidator)
    assert isinstance(
        container.frame_acl_set_compatibility_validator,
        FrameACLSetCompatibilityValidator,
    )
    assert container.view_chain_names == ["default"]
    assert container.command_chain_names == ["default"]
    assert container.codegen_chain_names == ["default"]
    assert container.list_named_configuration_names() == ["default"]


def test_frame_acl_container_can_register_same_name_bundle_across_families() -> None:
    """
    Verify one named bundle seeds matching view/command/codegen chains.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    named_configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        container.frame_acl_configuration,
        reason="named",
    )
    named_configuration.finalize()

    registered = container.register_named_configuration(
        named_configuration,
        contract_name="ops_contract",
    )

    assert registered.frame_name == "ops"
    assert container.view_chain_names == ["default", "ops_contract"]
    assert container.command_chain_names == ["default", "ops_contract"]
    assert container.codegen_chain_names == ["default", "ops_contract"]
    assert container.list_named_configuration_names() == ["default", "ops_contract"]
    assert container.get_named_configuration("ops_contract").to_json_dict() == (
        named_configuration.to_json_dict()
    )


def test_frame_acl_container_install_advances_default_family_chains() -> None:
    """
    Verify installing a same-name bundle advances the default family chains.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    previous_configuration = container.frame_acl_configuration
    next_configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        previous_configuration,
        reason="install",
    )
    next_configuration.finalize()

    installed = container.install_configuration(next_configuration)

    assert installed.frame_name == "ops"
    assert container.get_named_configuration("default").configuration_id == (
        installed.configuration_id
    )
    assert container.get_current_view_configuration().profile_name == (
        next_configuration.view_configuration.profile_name
    )


def test_frame_acl_container_family_drafts_clone_current_named_revisions() -> None:
    """
    Verify family draft creation clones the current named family revision.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    current_view = container.get_current_view_configuration()
    current_command = container.get_current_command_configuration()
    current_codegen = container.get_current_codegen_configuration()

    draft_view = container.create_new_from_view_configuration(
        current_view.configuration_id,
        reason="view_draft",
    )
    draft_command = container.create_new_from_command_configuration(
        current_command.configuration_id,
        reason="command_draft",
    )
    draft_codegen = container.create_new_from_codegen_configuration(
        current_codegen.configuration_id,
        reason="codegen_draft",
    )

    assert draft_view.source_configuration_id == current_view.configuration_id
    assert draft_command.source_configuration_id == current_command.configuration_id
    assert draft_codegen.source_configuration_id == current_codegen.configuration_id
    assert draft_view.locked is False
    assert draft_command.locked is False
    assert draft_codegen.locked is False


def test_frame_acl_container_rejects_duplicate_same_name_bundle_registration() -> None:
    """
    Verify duplicate same-name bundle registration is rejected.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    first_named_configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        container.frame_acl_configuration,
        reason="named-1",
    )
    first_named_configuration.finalize()
    second_named_configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        container.frame_acl_configuration,
        reason="named-2",
    )
    second_named_configuration.finalize()

    container.register_named_configuration(
        first_named_configuration,
        contract_name="ops_contract",
    )

    with pytest.raises(ValueError, match="already exists"):
        container.register_named_configuration(
            second_named_configuration,
            contract_name="ops_contract",
        )


def test_frame_acl_container_build_selected_configuration_can_mix_names() -> None:
    """
    Verify the container can assemble a mixed-family selection snapshot.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    named_configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        container.frame_acl_configuration,
        reason="named",
    )
    named_configuration.finalize()
    container.register_named_configuration(
        named_configuration,
        contract_name="ops_contract",
    )

    mixed_configuration = container.build_selected_configuration(
        view_contract_name="ops_contract",
        command_contract_name="default",
        codegen_contract_name="ops_contract",
    )

    assert mixed_configuration.frame_name == "ops"
    assert mixed_configuration.view_configuration.profile_name == (
        named_configuration.view_configuration.profile_name
    )
    assert mixed_configuration.command_configuration.profile_name == (
        container.get_current_command_configuration().profile_name
    )


def test_frame_acl_container_cleanup_cleans_all_owned_acl_objects() -> None:
    """
    Verify cleanup cascades through builder, validators, and family chains.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    builder = container.frame_acl_builder
    validator = container.frame_acl_validator
    compatibility_validator = container.frame_acl_set_compatibility_validator
    view_configuration = container.get_current_view_configuration()
    command_configuration = container.get_current_command_configuration()
    codegen_configuration = container.get_current_codegen_configuration()

    container.cleanup()

    assert builder.cleaned is True
    assert validator.cleaned is True
    assert compatibility_validator.cleaned is True
    assert view_configuration.cleaned is True
    assert command_configuration.cleaned is True
    assert codegen_configuration.cleaned is True
    assert container._lock is None


def test_frame_acl_container_cleanup_is_idempotent() -> None:
    """
    Verify cleanup can be called repeatedly.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")

    container.cleanup()
    container.cleanup()

    assert container.cleaned is True


def test_frame_acl_container_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Verify cleanup returns early when another thread already cleaned the container.

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

    container = FrameACLContainer("ops")
    coordinated_lock = _CoordinatedLock()
    container._lock = coordinated_lock

    thread_results = []

    def _run_cleanup() -> None:
        container.cleanup()
        thread_results.append(True)

    first = threading.Thread(target=_run_cleanup)
    second = threading.Thread(target=_run_cleanup)
    first.start()
    coordinated_lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join(timeout=1.0)
    second.join(timeout=1.0)

    assert thread_results == [True, True]
    assert container.cleaned is True
    assert container._lock is None
