import json
import threading

import pytest

from melder.aether.nexus.acl.builder.frame_acl_builder import FrameACLBuilder
from melder.aether.nexus.acl.frame_acl_container import FrameACLContainer
from melder.aether.nexus.acl.configurations.frame_acl_view_configuration import (
    FrameACLViewConfiguration,
)
from melder.aether.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.configurations.profiles.frame_acl_profile import (
    FrameACLProfile,
)
from melder.aether.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)


def test_frame_acl_builder_begin_change_seeds_typed_draft_from_current_config() -> None:
    """
    Verify begin_change seeds a typed draft cloned from the current config.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    builder = container.frame_acl_builder
    current_view_configuration = container.get_current_view_configuration()

    builder.begin_change("view")

    assert builder.change_active is True
    assert builder.draft_family_name == "view"
    assert builder.draft_contract_name == "default"
    assert builder._draft_configuration is not None
    assert (
        builder._draft_configuration.source_configuration_id
        == current_view_configuration.configuration_id
    )
    assert builder._draft_configuration.profile_name == current_view_configuration.profile_name


def test_frame_acl_builder_load_requires_active_change_and_string_payload() -> None:
    """
    Verify JSON loading requires an active change and a string payload.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    builder = container.frame_acl_builder

    with pytest.raises(RuntimeError, match="has no active change"):
        builder.load_json_configuration_string("{}")

    builder.begin_change("view")

    with pytest.raises(TypeError):
        builder.load_json_configuration_string(None)


def test_frame_acl_builder_apply_profile_requires_active_change() -> None:
    """
    Verify reusable profile application requires an active draft session.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    builder = container.frame_acl_builder
    frame_acl_profile = FrameACLProfile(
        "support",
        view_profile=FrameACLViewProfile.create_hybrid(),
        codegen_profile=FrameACLCodegenProfile.create_permissive(),
    )

    with pytest.raises(RuntimeError, match="has no active change"):
        builder.apply_frame_acl_profile(frame_acl_profile)


def test_frame_acl_builder_apply_profile_rejects_wrong_profile_type() -> None:
    """
    Verify reusable profile application rejects non-profile inputs.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    builder = container.frame_acl_builder

    with pytest.raises(TypeError, match="must satisfy IFrameACLProfile"):
        builder.apply_frame_acl_profile(None)


def test_frame_acl_builder_commit_requires_active_change() -> None:
    """
    Verify commit_change rejects commits without an active change session.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    builder = container.frame_acl_builder

    with pytest.raises(RuntimeError, match="has no active change"):
        builder.commit_change()


def test_frame_acl_builder_commit_installs_new_typed_configuration() -> None:
    """
    Verify commit_change installs and returns the next typed configuration
    revision.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    previous_configuration = container.get_current_view_configuration()
    builder = container.frame_acl_builder

    builder.begin_change("view")
    builder.apply_frame_acl_profile(
        FrameACLProfile(
            "support",
            view_profile=FrameACLViewProfile.create_hybrid(),
            codegen_profile=FrameACLCodegenProfile.create_permissive(),
        )
    )
    next_configuration = builder.commit_change()

    assert isinstance(next_configuration, FrameACLViewConfiguration)
    assert container.get_current_view_configuration() is next_configuration
    assert next_configuration.source_configuration_id is None
    assert next_configuration.locked is True
    assert next_configuration.profile_name == "hybrid"
    assert container.frame_acl_configuration.view_configuration.profile_name == "hybrid"
    assert container.frame_acl_configuration.codegen_configuration.profile_name == "safe"
    assert builder._draft_configuration is None
    assert builder.change_active is False


def test_frame_acl_builder_discard_resets_session_state() -> None:
    """
    Verify discard_change clears the draft and closes the change session.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    builder = container.frame_acl_builder

    builder.begin_change("view")
    builder.discard_change()

    assert builder.change_active is False
    assert builder._draft_configuration is None


def test_frame_acl_builder_rejects_double_begin_change() -> None:
    """
    Verify only one open change session exists per builder.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    builder = container.frame_acl_builder

    builder.begin_change("view")

    with pytest.raises(RuntimeError, match="already has an active change"):
        builder.begin_change("command")


def test_frame_acl_builder_init_rejects_missing_container() -> None:
    """
    Verify builder construction rejects a missing container.

    Returns:
        None.
    """
    with pytest.raises(TypeError, match="container cannot be None"):
        FrameACLBuilder(None)


def test_frame_acl_builder_cleanup_clears_fields() -> None:
    """
    Verify cleanup nulls builder-owned fields.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    builder = container.frame_acl_builder
    builder.begin_change("view")

    builder.cleanup()

    assert builder.cleaned is True
    assert builder._lock is None
    assert builder._container is None
    assert builder._change_active is None
    assert builder._draft_configuration is None


def test_frame_acl_builder_cleanup_is_idempotent() -> None:
    """
    Verify cleanup can be called more than once safely.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    builder = container.frame_acl_builder

    builder.cleanup()
    builder.cleanup()

    assert builder.cleaned is True


def test_frame_acl_builder_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Verify cleanup returns early when another thread marks the builder cleaned.

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
    builder = container.frame_acl_builder
    builder.begin_change("view")
    coordinated_lock = _CoordinatedLock()
    builder._lock = coordinated_lock

    thread_results = []

    def _run_cleanup() -> None:
        builder.cleanup()
        thread_results.append(True)

    first = threading.Thread(target=_run_cleanup)
    second = threading.Thread(target=_run_cleanup)
    first.start()
    coordinated_lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join(timeout=1.0)
    second.join(timeout=1.0)

    assert thread_results == [True, True]
    assert builder.cleaned is True
    assert builder._lock is None


def test_frame_acl_builder_load_json_rebuilds_typed_draft() -> None:
    """
    Verify loading JSON rebuilds the typed draft child configs.

    Returns:
        None.
    """
    container = FrameACLContainer("ops")
    builder = container.frame_acl_builder

    builder.begin_change("view")
    builder.load_json_configuration_string(
        json.dumps(
            {
                "profile_name": "hybrid",
                "profile_version": "0.0.1",
                "required_nexus_label": "default",
                "required_nexus_version": "0.0.1",
                "minimum_spell_payload_type": "detailed",
                "minimum_spell_payload_version": "0.0.1",
                "frame_override_ruleset": {"name": "frame_override", "rules": []},
                "conduit_override_ruleset": {"name": "conduit_override", "rules": []},
                "spell_override_ruleset": {"name": "spell_override", "rules": []},
                "member_override_ruleset": {"name": "member_override", "rules": []},
            },
            sort_keys=True,
        )
    )

    assert isinstance(builder._draft_configuration, FrameACLViewConfiguration)
    assert builder._draft_configuration.profile_name == "hybrid"
