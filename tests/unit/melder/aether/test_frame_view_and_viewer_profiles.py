import pytest

from melder.aether.nexus.acl.frame_acl_compiled_access_surface import (
    CompiledFrameACLAccessSurface,
)
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.aether.nexus.rift.frame_viewer.profiles.frame_viewer_profile import (
    FrameViewerProfile,
)
from melder.aether.nexus.rift.frame_viewer.profiles.frame_viewer_profile_builder import (
    FrameViewerProfileBuilder,
)
from melder.aether.nexus.rift.frame_viewer.profiles.general.general_profile import (
    GeneralFrameViewerProfile,
)
from melder.utilities.general_base.cleanable import Cleanable

from tests.unit.melder.aether.test_frame_viewer_projection import (
    _build_descriptor,
    _build_surface,
    _build_viewer,
)


def test_frame_viewer_profile_requires_non_empty_core_fields() -> None:
    class _TruthyEmptyHelpers:
        def __bool__(self) -> bool:
            return True

        def __iter__(self):
            return iter(())

    with pytest.raises(ValueError, match="name cannot be empty"):
        FrameViewerProfile("")

    with pytest.raises(ValueError, match="version cannot be empty"):
        FrameViewerProfile("general", version="")

    with pytest.raises(ValueError, match="default_grouping cannot be empty"):
        FrameViewerProfile("general", default_grouping="")

    with pytest.raises(ValueError, match="default_detail_level cannot be empty"):
        FrameViewerProfile("general", default_detail_level="")

    with pytest.raises(
            ValueError,
            match="required_nexus_version requires required_nexus_label",
    ):
        FrameViewerProfile(
            "general",
            required_nexus_version="0.0.1",
        )

    with pytest.raises(
            ValueError,
            match="required_acl_view_profile_version requires required_acl_view_profile_name",
    ):
        FrameViewerProfile(
            "general",
            required_acl_view_profile_version="0.0.1",
        )

    with pytest.raises(ValueError, match="enabled_helpers cannot be empty"):
        FrameViewerProfile(
            "general",
            enabled_helpers=_TruthyEmptyHelpers(),
        )


def test_frame_viewer_profile_create_general_exposes_expected_defaults() -> None:
    profile = FrameViewerProfile.create_general()

    assert profile.name == "general"
    assert profile.version == "0.0.1"
    assert profile.default_grouping == "frame"
    assert profile.default_detail_level == "detailed"
    assert "list_frames" in profile.enabled_helpers
    assert "count_frames" in profile.enabled_helpers
    assert "count_root_conduits" in profile.enabled_helpers
    assert "count_spell_records" in profile.enabled_helpers
    assert "list_conduits" in profile.enabled_helpers
    assert "list_spells" in profile.enabled_helpers
    assert profile.tool_handler_names_by_name["list_frames"] == "list_frame_names"
    assert profile.tool_handler_names_by_name["describe_frame"] == "describe_frame"
    assert profile.tool_handler_names_by_name["list_spells"] == "view_spell.list_spells"
    assert profile.view_frame is not None
    assert profile.view_conduit is not None
    assert profile.view_spell is not None


def test_frame_viewer_profile_builder_seeds_general_profile_only() -> None:
    builder = FrameViewerProfileBuilder()

    assert builder.list_profile_names() == ["general"]
    assert builder.get_required_profile("general").tool_handler_names_by_name[
        "describe_targets"
    ] == "view_frame.describe_targets"


def test_frame_viewer_profile_cleanup_clears_owned_state() -> None:
    profile = FrameViewerProfile.create_general()

    profile.cleanup()
    profile.cleanup()

    assert profile.cleaned is True
    assert profile._tool_handler_names_by_name is None
    assert profile._default_grouping is None
    assert profile._default_detail_level is None
    assert profile._view_frame is None
    assert profile._view_conduit is None
    assert profile._view_spell is None
    assert profile._version is None
    assert profile._name is None


def test_frame_viewer_profile_cleanup_is_idempotent_for_plain_profile() -> None:
    profile = FrameViewerProfile(
        "plain",
        tool_handler_names_by_name={"inventory": "list_frames"},
    )

    profile.cleanup()
    profile.cleanup()

    assert profile.cleaned is True


def test_frame_viewer_profile_can_expose_explicit_tool_handler_mapping() -> None:
    profile = FrameViewerProfile(
        "inspection",
        required_nexus_label="default",
        required_nexus_version="0.0.1",
        required_acl_view_profile_name="safe",
        required_acl_view_profile_version="0.0.1",
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
    assert profile.required_nexus_label == "default"
    assert profile.required_nexus_version == "0.0.1"
    assert profile.required_acl_view_profile_name == "safe"
    assert profile.required_acl_view_profile_version == "0.0.1"


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


def test_frame_viewer_profile_helper_listing_ignores_none_and_non_cleanable_helpers() -> None:
    class _Helper(Cleanable):
        def cleanup(self) -> None:
            self._cleaned = True

    class _CustomProfile(FrameViewerProfile):
        @property
        def view_missing(self):
            return None

        @property
        def view_not_cleanable(self):
            return "bad"

        @property
        def view_helper(self):
            return _Helper()

    profile = _CustomProfile(
        "custom",
        tool_handler_names_by_name={"inventory": "list_frames"},
    )

    assert profile.list_helper_object_names() == ("view_helper",)


def test_frame_viewer_profile_tool_lookup_rejects_empty_and_missing_names() -> None:
    profile = FrameViewerProfile(
        "custom",
        tool_handler_names_by_name={"inventory": "list_frames"},
    )

    with pytest.raises(ValueError, match="tool_name cannot be empty"):
        profile.has_tool("")

    with pytest.raises(ValueError, match="tool_name cannot be empty"):
        profile.get_required_tool_handler_name("")

    with pytest.raises(ValueError, match="tool 'missing' is not exposed"):
        profile.get_required_tool_handler_name("missing")


def test_frame_viewer_profile_clone_returns_detached_general_profile() -> None:
    profile = FrameViewerProfile.create_general()

    cloned = profile.clone()

    assert cloned is not profile
    assert cloned.name == "general"
    assert cloned.tool_handler_names_by_name == profile.tool_handler_names_by_name
    assert cloned.tool_handler_names_by_name is not profile.tool_handler_names_by_name
    assert cloned.view_frame is not profile.view_frame


def test_frame_viewer_profile_bind_to_frame_rejects_invalid_binding_inputs() -> None:
    viewer = _build_viewer(("ops",))
    descriptor = viewer.frame_descriptors_by_name["ops"]
    configuration = viewer.frame_acl_configurations_by_frame_name["ops"]
    surface = viewer.compiled_access_surfaces_by_frame_name["ops"]
    profile = FrameViewerProfile.create_general()

    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        profile.bind_to_frame(
            frame_name="",
            frame_descriptor=descriptor,
            frame_acl_configuration=configuration,
            compiled_access_surface=surface,
        )

    with pytest.raises(TypeError, match="frame_descriptor must be a FrameDescriptor"):
        profile.bind_to_frame(
            frame_name="ops",
            frame_descriptor=object(),
            frame_acl_configuration=configuration,
            compiled_access_surface=surface,
        )

    with pytest.raises(
            TypeError,
            match="frame_acl_configuration must be a FrameACLConfiguration",
    ):
        profile.bind_to_frame(
            frame_name="ops",
            frame_descriptor=descriptor,
            frame_acl_configuration=object(),
            compiled_access_surface=surface,
        )

    with pytest.raises(
            TypeError,
            match="compiled_access_surface must be a CompiledFrameACLAccessSurface",
    ):
        profile.bind_to_frame(
            frame_name="ops",
            frame_descriptor=descriptor,
            frame_acl_configuration=configuration,
            compiled_access_surface=object(),
        )


def test_frame_viewer_profile_bind_to_frame_rejects_descriptor_and_surface_mismatches() -> None:
    viewer = _build_viewer(("ops",))
    descriptor = viewer.frame_descriptors_by_name["ops"]
    configuration = viewer.frame_acl_configurations_by_frame_name["ops"]
    surface = viewer.compiled_access_surfaces_by_frame_name["ops"]
    profile = FrameViewerProfile.create_general()

    other_descriptor = _build_descriptor("finance")
    with pytest.raises(ValueError, match="FrameDescriptor targets frame 'finance'"):
        profile.bind_to_frame(
            frame_name="ops",
            frame_descriptor=other_descriptor,
            frame_acl_configuration=configuration,
            compiled_access_surface=surface,
        )

    other_configuration = FrameACLConfiguration.create_default("finance")
    with pytest.raises(
            ValueError,
            match="FrameACLConfiguration targets frame 'finance'",
    ):
        profile.bind_to_frame(
            frame_name="ops",
            frame_descriptor=descriptor,
            frame_acl_configuration=other_configuration,
            compiled_access_surface=surface,
        )

    other_surface = _build_surface("finance", other_configuration)
    with pytest.raises(
            ValueError,
            match="CompiledFrameACLAccessSurface targets frame 'finance'",
    ):
        profile.bind_to_frame(
            frame_name="ops",
            frame_descriptor=descriptor,
            frame_acl_configuration=configuration,
            compiled_access_surface=other_surface,
        )


def test_frame_viewer_profile_bind_to_frame_rejects_configuration_and_contract_mismatches() -> None:
    viewer = _build_viewer(("ops",))
    descriptor = viewer.frame_descriptors_by_name["ops"]
    configuration = viewer.frame_acl_configurations_by_frame_name["ops"]
    surface = viewer.compiled_access_surfaces_by_frame_name["ops"]
    profile = FrameViewerProfile.create_general()

    wrong_configuration_surface = _build_surface("ops", configuration)
    wrong_configuration_surface._configuration_id = "other-config"
    with pytest.raises(ValueError, match="configuration_id 'other-config' does not match"):
        profile.bind_to_frame(
            frame_name="ops",
            frame_descriptor=descriptor,
            frame_acl_configuration=configuration,
            compiled_access_surface=wrong_configuration_surface,
        )

    wrong_view_surface = _build_surface("ops", configuration)
    wrong_view_surface._view_profile_name = "other"
    with pytest.raises(ValueError, match="Compiled ACL view profile 'other:0.0.1' does not match"):
        profile.bind_to_frame(
            frame_name="ops",
            frame_descriptor=descriptor,
            frame_acl_configuration=configuration,
            compiled_access_surface=wrong_view_surface,
        )

    descriptor_without_overview = FrameDescriptor("ops")
    constrained_profile = FrameViewerProfile(
        "constrained",
        required_nexus_label="default",
        required_nexus_version="0.0.1",
        tool_handler_names_by_name={"list_frames": "list_frame_names"},
    )
    with pytest.raises(ValueError, match="has no frame_overview for Nexus contract validation"):
        constrained_profile.bind_to_frame(
            frame_name="ops",
            frame_descriptor=descriptor_without_overview,
            frame_acl_configuration=configuration,
            compiled_access_surface=surface,
        )

    mismatched_profile = FrameViewerProfile(
        "constrained",
        required_nexus_label="other",
        required_nexus_version="9.9.9",
        tool_handler_names_by_name={"list_frames": "list_frame_names"},
    )
    with pytest.raises(ValueError, match="does not match required 'other:9.9.9'"):
        mismatched_profile.bind_to_frame(
            frame_name="ops",
            frame_descriptor=descriptor,
            frame_acl_configuration=configuration,
            compiled_access_surface=surface,
        )


def test_frame_viewer_profile_builder_seeds_and_registers_profiles() -> None:
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


def test_frame_viewer_profile_builder_register_replaces_existing_profile() -> None:
    builder = FrameViewerProfileBuilder()
    first_profile = FrameViewerProfile(
        "inspection",
        default_grouping="frame",
        default_detail_level="summary",
        enabled_helpers=("list_frames",),
    )
    second_profile = FrameViewerProfile(
        "inspection",
        default_grouping="kind",
        default_detail_level="detailed",
        enabled_helpers=("describe_frame",),
    )

    builder.register_profile(first_profile)
    builder.register_profile(second_profile)

    assert first_profile.cleaned is True
    assert builder.get_required_profile("inspection") is second_profile


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

    builder.cleanup()


def test_frame_viewer_profile_builder_cleanup_rechecks_cleaned_inside_lock() -> None:
    class _FlipCleanedOnEnter:
        def __init__(self, builder: FrameViewerProfileBuilder) -> None:
            self._builder = builder

        def __enter__(self):
            self._builder._cleaned = True
            return self

        def __exit__(self, exc_type, exc, tb) -> bool:
            return False

    builder = FrameViewerProfileBuilder()
    original_lock = builder._lock
    builder._lock = _FlipCleanedOnEnter(builder)
    try:
        builder.cleanup()
    finally:
        builder._lock = original_lock

    assert builder.cleaned is True


def test_general_frame_viewer_profile_cleanup_is_idempotent() -> None:
    profile = GeneralFrameViewerProfile()

    profile.cleanup()
    profile.cleanup()

    assert profile.cleaned is True
