import pytest

from melder.aether.nexus.rift.frame_viewer.profiles.frame_viewer_profile import (
    FrameViewerProfile,
)
from melder.aether.nexus.rift.frame_viewer.profiles.frame_viewer_profile_builder import (
    FrameViewerProfileBuilder,
)


def test_frame_viewer_profile_requires_non_empty_core_fields() -> None:
    with pytest.raises(ValueError, match="name cannot be empty"):
        FrameViewerProfile("")

    with pytest.raises(ValueError, match="version cannot be empty"):
        FrameViewerProfile("general", version="")

    with pytest.raises(ValueError, match="default_grouping cannot be empty"):
        FrameViewerProfile("general", default_grouping="")

    with pytest.raises(ValueError, match="default_detail_level cannot be empty"):
        FrameViewerProfile("general", default_detail_level="")


def test_frame_viewer_profile_create_general_exposes_expected_defaults() -> None:
    profile = FrameViewerProfile.create_general()

    assert profile.name == "general"
    assert profile.version == "0.0.1"
    assert profile.default_grouping == "frame"
    assert profile.default_detail_level == "summary"
    assert "list_frames" in profile.enabled_helpers
    assert "list_targets" in profile.enabled_helpers
    assert "describe_frames" in profile.enabled_helpers


def test_frame_viewer_profile_builder_seeds_navigation_and_inspection_profiles() -> None:
    builder = FrameViewerProfileBuilder()

    assert builder.list_profile_names() == ["general", "navigation", "inspection"]
    assert builder.get_required_profile("navigation").tool_handler_names_by_name[
        "select_view"
    ] == "set_default_view"
    assert builder.get_required_profile("inspection").tool_handler_names_by_name[
        "describe_targets"
    ] == "describe_available_targets"


def test_frame_viewer_profile_cleanup_clears_owned_state() -> None:
    profile = FrameViewerProfile.create_general()

    profile.cleanup()

    assert profile.cleaned is True
    assert profile._tool_handler_names_by_name is None
    assert profile._default_grouping is None
    assert profile._default_detail_level is None
    assert profile._version is None
    assert profile._name is None


def test_frame_viewer_profile_can_expose_explicit_tool_handler_mapping() -> None:
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
    profile = FrameViewerProfile(
        "inspection",
        tool_handler_names_by_name={"inventory": "list_links"},
    )

    cloned = profile.clone()

    assert cloned is not profile
    assert cloned.tool_handler_names_by_name == {"inventory": "list_links"}
    assert cloned.tool_handler_names_by_name is not profile.tool_handler_names_by_name


def test_frame_viewer_profile_builder_seeds_and_registers_profiles() -> None:
    builder = FrameViewerProfileBuilder()
    custom_profile = FrameViewerProfile(
        "inspection",
        default_grouping="kind",
        default_detail_level="detailed",
        enabled_helpers=("list_links", "describe_frame"),
    )

    builder.register_profile(custom_profile)

    assert builder.list_profile_names() == ["general", "navigation", "inspection"]
    assert builder.get_required_profile("inspection") is custom_profile


def test_frame_viewer_profile_builder_rejects_invalid_profile_and_missing_lookup() -> None:
    builder = FrameViewerProfileBuilder()

    with pytest.raises(TypeError, match="profile must be a FrameViewerProfile"):
        builder.register_profile(None)

    with pytest.raises(KeyError, match="missing"):
        builder.get_required_profile("missing")


def test_frame_viewer_profile_builder_cleanup_cascades_to_profiles() -> None:
    builder = FrameViewerProfileBuilder()
    profile = builder.get_required_profile("general")

    builder.cleanup()

    assert builder.cleaned is True
    assert profile.cleaned is True
    assert builder._profiles_by_name is None
