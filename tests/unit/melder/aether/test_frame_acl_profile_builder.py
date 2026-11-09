import pytest

from melder.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile_builder import (
    FrameACLCodegenProfileBuilder,
)
from melder.nexus.acl.configurations.profiles.builder.frame_acl_profile_builder import (
    FrameACLProfileBuilder,
)
from melder.nexus.acl.configurations.profiles.command.frame_acl_command_profile_builder import (
    FrameACLCommandProfileBuilder,
)
from melder.nexus.acl.configurations.profiles.view.frame_acl_view_profile_builder import (
    FrameACLViewProfileBuilder,
)
from melder.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from tests._cleanup_recheck_support import CleanupRecheckHandshake


def test_frame_acl_profile_builder_exposes_id_and_registry_snapshots() -> None:
    """
    Verify the builder exposes its stable id and detached registry snapshots.

    Returns:
        None.
    """
    builder = FrameACLProfileBuilder()
    view_snapshot = builder.view_profiles_by_name
    codegen_snapshot = builder.codegen_profiles_by_name

    assert builder.id is not None
    assert builder.version == "0.0.1"
    assert set(builder.list_view_profile_names()) == {"safe", "hybrid", "permissive"}
    assert set(builder.list_command_profile_names()) == {"safe", "hybrid", "permissive"}
    assert set(builder.list_codegen_profile_names()) == {
        "safe",
        "hybrid",
        "permissive",
        "full_access",
    }
    assert set(builder.list_view_precision_profile_names()) == {"precision"}
    assert set(builder.list_command_precision_profile_names()) == {"precision"}
    assert set(builder.list_codegen_precision_profile_names()) == {"precision"}

    view_snapshot.clear()
    codegen_snapshot.clear()

    assert set(builder.list_view_profile_names()) == {"safe", "hybrid", "permissive"}
    assert set(builder.list_command_profile_names()) == {"safe", "hybrid", "permissive"}
    assert set(builder.list_codegen_profile_names()) == {
        "safe",
        "hybrid",
        "permissive",
        "full_access",
    }


def test_frame_acl_view_profile_builder_loads_default_strategies() -> None:
    """
    Verify the dedicated view family builder exposes and builds the defaults.

    Returns:
        None.
    """
    builder = FrameACLViewProfileBuilder()

    assert set(builder.list_strategy_names()) == {
        "safe",
        "hybrid",
        "permissive",
        "precision",
    }
    assert builder.build_profile("safe").name == "safe"
    assert builder.build_profile("hybrid").name == "hybrid"
    assert builder.build_profile("permissive").name == "permissive"
    assert builder.build_profile("precision").name == "precision"


def test_frame_acl_profile_builder_exposes_view_family_builder() -> None:
    """
    Verify the top-level builder exposes its dedicated view family builder.

    Returns:
        None.
    """
    builder = FrameACLProfileBuilder()

    assert isinstance(builder.view_profile_builder, FrameACLViewProfileBuilder)
    assert set(builder.view_profile_builder.list_strategy_names()) == {
        "safe",
        "hybrid",
        "permissive",
        "precision",
    }


def test_frame_acl_command_profile_builder_loads_default_strategies() -> None:
    """
    Verify the dedicated command family builder exposes and builds the defaults.

    Returns:
        None.
    """
    builder = FrameACLCommandProfileBuilder()

    assert set(builder.list_strategy_names()) == {
        "safe",
        "hybrid",
        "permissive",
        "precision",
    }
    assert builder.build_profile("safe").name == "safe"
    assert builder.build_profile("hybrid").name == "hybrid"
    assert builder.build_profile("permissive").name == "permissive"
    assert builder.build_profile("precision").name == "precision"


def test_frame_acl_profile_builder_exposes_command_family_builder() -> None:
    """
    Verify the top-level builder exposes its dedicated command family builder.

    Returns:
        None.
    """
    builder = FrameACLProfileBuilder()

    assert isinstance(builder.command_profile_builder, FrameACLCommandProfileBuilder)
    assert set(builder.command_profile_builder.list_strategy_names()) == {
        "safe",
        "hybrid",
        "permissive",
        "precision",
    }


def test_frame_acl_codegen_profile_builder_loads_default_strategies() -> None:
    """
    Verify the dedicated codegen family builder exposes and builds the defaults.

    Returns:
        None.
    """
    builder = FrameACLCodegenProfileBuilder()

    assert set(builder.list_strategy_names()) == {
        "safe",
        "hybrid",
        "permissive",
        "full_access",
        "precision",
    }
    assert builder.build_profile("safe").name == "safe"
    assert builder.build_profile("hybrid").name == "hybrid"
    assert builder.build_profile("permissive").name == "permissive"
    assert builder.build_profile("full_access").name == "full_access"
    assert builder.build_profile("precision").name == "precision"


def test_frame_acl_profile_builder_exposes_codegen_family_builder() -> None:
    """
    Verify the top-level builder exposes its dedicated codegen family builder.

    Returns:
        None.
    """
    builder = FrameACLProfileBuilder()

    assert isinstance(builder.codegen_profile_builder, FrameACLCodegenProfileBuilder)
    assert set(builder.codegen_profile_builder.list_strategy_names()) == {
        "safe",
        "hybrid",
        "permissive",
        "full_access",
        "precision",
    }


def test_frame_acl_profile_builder_exposes_command_and_precision_registry_snapshots() -> None:
    """
    Verify command/codegen registry snapshots and precision helpers are exposed.

    Returns:
        None.
    """
    builder = FrameACLProfileBuilder()
    command_snapshot = builder.command_profiles_by_name
    view_precision_snapshot = builder.view_precision_profiles_by_name
    command_precision_snapshot = builder.command_precision_profiles_by_name
    codegen_precision_snapshot = builder.codegen_precision_profiles_by_name

    assert builder.get_required_view_precision_profile("precision").name == "precision"
    assert builder.get_required_command_precision_profile("precision").name == "precision"
    assert builder.get_required_codegen_precision_profile("precision").name == "precision"

    command_snapshot.clear()
    view_precision_snapshot.clear()
    command_precision_snapshot.clear()
    codegen_precision_snapshot.clear()

    assert set(builder.list_command_profile_names()) == {"safe", "hybrid", "permissive"}
    assert set(builder.list_view_precision_profile_names()) == {"precision"}
    assert set(builder.list_command_precision_profile_names()) == {"precision"}
    assert set(builder.list_codegen_precision_profile_names()) == {"precision"}


def test_frame_acl_profile_builder_register_replaces_and_cleans_old_profiles() -> None:
    """
    Verify registering a replacement profile cleans the displaced instance.

    Returns:
        None.
    """
    builder = FrameACLProfileBuilder()
    first_view = FrameACLViewProfile("custom_view", minimum_spell_payload_type="general")
    second_view = FrameACLViewProfile("custom_view", minimum_spell_payload_type="detailed")
    first_codegen = FrameACLCodegenProfile("custom_codegen")
    second_codegen = FrameACLCodegenProfile("custom_codegen")

    builder.register_view_profile(first_view)
    builder.register_view_profile(second_view)
    builder.register_codegen_profile(first_codegen)
    builder.register_codegen_profile(second_codegen)

    assert first_view.cleaned is True
    assert first_codegen.cleaned is True
    assert builder.get_required_view_profile("custom_view") is second_view
    assert builder.get_required_codegen_profile("custom_codegen") is second_codegen


def test_frame_acl_profile_builder_rejects_wrong_profile_types_and_missing_lookups() -> None:
    """
    Verify the builder enforces typed inputs and missing-profile lookup behavior.

    Returns:
        None.
    """
    builder = FrameACLProfileBuilder()

    with pytest.raises(TypeError, match="view_profile must be a FrameACLViewProfile"):
        builder.register_view_profile(None)

    with pytest.raises(TypeError, match="codegen_profile must be a FrameACLCodegenProfile"):
        builder.register_codegen_profile(None)

    with pytest.raises(KeyError, match="missing_view"):
        builder.get_required_view_profile("missing_view")

    with pytest.raises(KeyError, match="missing_codegen"):
        builder.get_required_codegen_profile("missing_codegen")


def test_frame_acl_profile_builder_remove_returns_false_for_missing_profiles() -> None:
    """
    Verify removing a non-existent profile reports False.

    Returns:
        None.
    """
    builder = FrameACLProfileBuilder()

    assert builder.remove_view_profile("missing_view") is False
    assert builder.remove_command_profile("missing_command") is False
    assert builder.remove_codegen_profile("missing_codegen") is False
    assert builder.remove_view_precision_profile("missing_view_precision") is False
    assert builder.remove_command_precision_profile("missing_command_precision") is False
    assert builder.remove_codegen_precision_profile("missing_codegen_precision") is False


def test_frame_acl_profile_builder_cleanup_is_idempotent() -> None:
    """
    Verify cleanup can be called repeatedly.

    Returns:
        None.
    """
    builder = FrameACLProfileBuilder()

    builder.cleanup()
    builder.cleanup()

    assert builder.cleaned is True


def test_frame_acl_profile_builder_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Verify cleanup returns early when another thread already cleaned the builder.

    The handshake holds the first caller inside the lock until the second has passed the outer `_cleaned` check
    and is about to block; the first caller then runs the real cleanup, including the registered profiles and the
    family builders. The second caller must return at the inner recheck - without it the teardown would run twice
    and a caller would raise on an attribute the other had already deleted - so both callers finish without
    raising and the builder reads cleaned with its `_lock` dropped. The callers are ordered by the handshake, not
    by timing: the earlier hand-made lock could lose its signal and failed on CI (GitHub #206;
    TASK-2026-11-08-deterministic_cleanup_recheck_handshake).

    Returns:
        None.
    """
    builder = FrameACLProfileBuilder()
    handshake = CleanupRecheckHandshake()
    builder._lock = handshake.lock

    handshake.run(builder.cleanup)

    assert builder.cleaned is True
    assert not hasattr(builder, '_lock')
