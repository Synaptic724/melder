import pytest

from melder.aether.nexus.rift.frame_viewer.profiles.frame_view_profile import (
    FrameViewProfile,
)
from melder.aether.nexus.rift.frame_viewer.profiles.frame_view_profile_builder import (
    FrameViewProfileBuilder,
)
from melder.aether.nexus.rift.frame_viewer.profiles.frame_viewer_profile import (
    FrameViewerProfile,
)
from melder.aether.nexus.rift.frame_viewer.profiles.frame_viewer_profile_builder import (
    FrameViewerProfileBuilder,
)


def test_frame_view_profile_requires_non_empty_core_fields() -> None:
    """
    Verify frame-view profiles reject invalid required identity/default fields.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="name cannot be empty"):
        FrameViewProfile("")

    with pytest.raises(ValueError, match="version cannot be empty"):
        FrameViewProfile("general", version="")

    with pytest.raises(ValueError, match="default_detail_level cannot be empty"):
        FrameViewProfile("general", default_detail_level="")


def test_frame_view_profile_create_general_exposes_expected_defaults() -> None:
    """
    Verify the seeded `general` frame-view profile exposes the expected defaults.

    Returns:
        None.
    """
    profile = FrameViewProfile.create_general()

    assert profile.name == "general"
    assert profile.version == "0.0.1"
    assert profile.default_detail_level == "summary"
    assert profile.preferred_kind_order == ("frame", "conduit", "spell")


def test_frame_view_profile_cleanup_clears_owned_state() -> None:
    """
    Verify frame-view profile cleanup clears owned state.

    Returns:
        None.
    """
    profile = FrameViewProfile.create_general()

    profile.cleanup()

    assert profile.cleaned is True
    assert profile._preferred_kind_order is None
    assert profile._default_detail_level is None
    assert profile._version is None
    assert profile._name is None


def test_frame_view_profile_clone_detaches_owned_metadata() -> None:
    """
    Verify frame-view profile clones detach the owned posture metadata.

    Returns:
        None.
    """
    profile = FrameViewProfile.create_general()

    cloned = profile.clone()

    assert cloned is not profile
    assert cloned.name == "general"
    assert cloned.preferred_kind_order == ("frame", "conduit", "spell")


def test_frame_view_profile_builder_seeds_and_registers_profiles() -> None:
    """
    Verify the frame-view profile builder seeds `general` and registers custom profiles.

    Returns:
        None.
    """
    builder = FrameViewProfileBuilder()
    custom_profile = FrameViewProfile(
        "inspection",
        default_detail_level="detailed",
        preferred_kind_order=("spell", "conduit", "frame"),
    )

    builder.register_profile(custom_profile)

    assert builder.list_profile_names() == ["general", "inspection"]
    assert builder.get_required_profile("inspection") is custom_profile


def test_frame_view_profile_builder_rejects_invalid_profile_and_missing_lookup() -> None:
    """
    Verify invalid frame-view profile registration and lookup fail fast.

    Returns:
        None.
    """
    builder = FrameViewProfileBuilder()

    with pytest.raises(TypeError, match="profile must be a FrameViewProfile"):
        builder.register_profile(None)

    with pytest.raises(KeyError, match="missing"):
        builder.get_required_profile("missing")


def test_frame_view_profile_builder_cleanup_cascades_to_profiles() -> None:
    """
    Verify frame-view profile builder cleanup cascades into owned profiles.

    Returns:
        None.
    """
    builder = FrameViewProfileBuilder()
    profile = builder.get_required_profile("general")

    builder.cleanup()

    assert builder.cleaned is True
    assert profile.cleaned is True
    assert builder._profiles_by_name is None


def test_frame_viewer_profile_requires_non_empty_core_fields() -> None:
    """
    Verify frame-viewer profiles reject invalid required identity/default fields.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="name cannot be empty"):
        FrameViewerProfile("")

    with pytest.raises(ValueError, match="version cannot be empty"):
        FrameViewerProfile("general", version="")

    with pytest.raises(ValueError, match="default_grouping cannot be empty"):
        FrameViewerProfile("general", default_grouping="")

    with pytest.raises(ValueError, match="default_detail_level cannot be empty"):
        FrameViewerProfile("general", default_detail_level="")


def test_frame_viewer_profile_create_general_exposes_expected_defaults() -> None:
    """
    Verify the seeded `general` frame-viewer profile exposes the expected defaults.

    Returns:
        None.
    """
    profile = FrameViewerProfile.create_general()

    assert profile.name == "general"
    assert profile.version == "0.0.1"
    assert profile.default_grouping == "frame"
    assert profile.default_detail_level == "summary"
    assert "list_frames" in profile.enabled_helpers
    assert "list_targets" in profile.enabled_helpers
    assert "describe_frames" in profile.enabled_helpers


def test_frame_viewer_profile_builder_seeds_navigation_and_inspection_profiles() -> None:
    """
    Verify the viewer profile builder seeds actionable navigation/inspection profiles.

    Returns:
        None.
    """
    builder = FrameViewerProfileBuilder()

    assert builder.list_profile_names() == ["general", "navigation", "inspection"]
    assert builder.get_required_profile("navigation").tool_handler_names_by_name[
        "select_view"
    ] == "set_default_view"
    assert builder.get_required_profile("inspection").tool_handler_names_by_name[
        "describe_targets"
    ] == "describe_available_targets"


def test_frame_viewer_profile_cleanup_clears_owned_state() -> None:
    """
    Verify frame-viewer profile cleanup clears owned state.

    Returns:
        None.
    """
    profile = FrameViewerProfile.create_general()

    profile.cleanup()

    assert profile.cleaned is True
    assert profile._tool_handler_names_by_name is None
    assert profile._default_grouping is None
    assert profile._default_detail_level is None
    assert profile._version is None
    assert profile._name is None


def test_frame_viewer_profile_can_expose_explicit_tool_handler_mapping() -> None:
    """
    Verify a frame-viewer profile can own an explicit tool -> handler mapping.

    Returns:
        None.
    """
    profile = FrameViewerProfile(
        "inspection",
        tool_handler_names_by_name={
            "inventory": "list_links",
            "summary": "describe_frames",
        },
        default_grouping="kind",
        default_detail_level="detailed",
    )

    assert profile.list_tool_names() == ("inventory", "summary")
    assert profile.has_tool("inventory") is True
    assert profile.enabled_helpers == ("inventory", "summary")
    assert profile.get_required_tool_handler_name("summary") == "describe_frames"


def test_frame_viewer_profile_rejects_invalid_tool_mapping_inputs() -> None:
    """
    Verify invalid explicit tool mappings fail fast.

    Returns:
        None.
    """
    with pytest.raises(
            ValueError,
            match="enabled_helpers and tool_handler_names_by_name cannot both be provided",
    ):
        FrameViewerProfile(
            "general",
            enabled_helpers=("list_links",),
            tool_handler_names_by_name={"inventory": "list_links"},
        )

    with pytest.raises(ValueError, match="tool_handler_names_by_name cannot be empty"):
        FrameViewerProfile("general", tool_handler_names_by_name={})

    with pytest.raises(
            ValueError,
            match="tool_handler_names_by_name cannot contain empty tool names",
    ):
        FrameViewerProfile("general", tool_handler_names_by_name={"": "list_links"})

    with pytest.raises(
            ValueError,
            match="tool_handler_names_by_name cannot contain empty handler names",
    ):
        FrameViewerProfile("general", tool_handler_names_by_name={"inventory": ""})


def test_frame_viewer_profile_clone_returns_detached_tool_mapping() -> None:
    """
    Verify frame-viewer profile clones detach the owned tool map.

    Returns:
        None.
    """
    profile = FrameViewerProfile(
        "inspection",
        tool_handler_names_by_name={"inventory": "list_links"},
    )

    cloned = profile.clone()

    assert cloned is not profile
    assert cloned.tool_handler_names_by_name == {"inventory": "list_links"}
    assert cloned.tool_handler_names_by_name is not profile.tool_handler_names_by_name


def test_frame_viewer_profile_builder_seeds_and_registers_profiles() -> None:
    """
    Verify the frame-viewer profile builder seeds `general` and registers custom profiles.

    Returns:
        None.
    """
    builder = FrameViewerProfileBuilder()
    custom_profile = FrameViewerProfile(
        "inspection",
        default_grouping="kind",
        default_detail_level="detailed",
        enabled_helpers=("list_links", "describe_frame"),
    )

    builder.register_profile(custom_profile)

    assert builder.list_profile_names() == ["general", "inspection"]
    assert builder.get_required_profile("inspection") is custom_profile


def test_frame_viewer_profile_builder_rejects_invalid_profile_and_missing_lookup() -> None:
    """
    Verify invalid frame-viewer profile registration and lookup fail fast.

    Returns:
        None.
    """
    builder = FrameViewerProfileBuilder()

    with pytest.raises(TypeError, match="profile must be a FrameViewerProfile"):
        builder.register_profile(None)

    with pytest.raises(KeyError, match="missing"):
        builder.get_required_profile("missing")


def test_frame_viewer_profile_builder_cleanup_cascades_to_profiles() -> None:
    """
    Verify frame-viewer profile builder cleanup cascades into owned profiles.

    Returns:
        None.
    """
    builder = FrameViewerProfileBuilder()
    profile = builder.get_required_profile("general")

    builder.cleanup()

    assert builder.cleaned is True
    assert profile.cleaned is True
    assert builder._profiles_by_name is None
