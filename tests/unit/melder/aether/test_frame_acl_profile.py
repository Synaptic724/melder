import pytest

from melder.aether.nexus.acl.frame_acl_profile import (
    CodegenACLDetails,
    FrameACLProfile,
    ViewACLDetails,
)
from melder.aether.nexus.frame_acl_manager import FrameACLManager


def test_view_acl_details_default_payload_is_empty_json_object() -> None:
    """
    Verify view details default to the normalized empty-object payload.

    Returns:
        None.
    """
    details = ViewACLDetails()

    assert details.to_json_dict() == {}
    assert details.to_json_string() == "{}"


def test_view_acl_details_normalizes_payload_and_exposes_id() -> None:
    """
    Verify view details normalize JSON payloads and expose a stable id.

    Returns:
        None.
    """
    details = ViewACLDetails('{"b":2,"a":1}')

    assert details.id is not None
    assert details.to_json_string() == '{"a": 1, "b": 2}'


def test_view_acl_details_rejects_invalid_payloads() -> None:
    """
    Verify view details reject non-string and invalid-JSON payloads.

    Returns:
        None.
    """
    with pytest.raises(TypeError, match="json_payload_string must be a string"):
        ViewACLDetails(None)

    with pytest.raises(ValueError, match="must be valid JSON"):
        ViewACLDetails("{invalid")


def test_codegen_acl_details_default_payload_is_empty_json_object() -> None:
    """
    Verify codegen details default to the normalized empty-object payload.

    Returns:
        None.
    """
    details = CodegenACLDetails()

    assert details.to_json_dict() == {}
    assert details.to_json_string() == "{}"


def test_codegen_acl_details_normalizes_payload_and_can_be_replaced() -> None:
    """
    Verify codegen details normalize payloads and support payload replacement.

    Returns:
        None.
    """
    details = CodegenACLDetails('{"b":2,"a":1}')
    details.set_json_payload_string('{"z":1,"m":2}')

    assert details.id is not None
    assert details.to_json_string() == '{"m": 2, "z": 1}'


def test_frame_acl_profile_builds_default_strategy_with_two_details_objects() -> None:
    """
    Verify a profile creates one default strategy entry on construction.

    Returns:
        None.
    """
    profile = FrameACLProfile("support")

    assert profile.id is not None
    assert profile.name == "support"
    assert profile.list_strategy_names() == ["default"]
    assert isinstance(profile.view_acl_details, ViewACLDetails)
    assert isinstance(profile.codegen_acl_details, CodegenACLDetails)
    assert profile.has_strategy("default") is True


def test_frame_acl_profile_registers_and_returns_named_strategy() -> None:
    """
    Verify named strategy registration stores the supplied details tuple.

    Returns:
        None.
    """
    profile = FrameACLProfile("support")
    view_acl_details = ViewACLDetails('{"view":"support"}')
    codegen_acl_details = CodegenACLDetails('{"codegen":"support"}')

    profile.register_strategy(
        "support_readonly",
        view_acl_details,
        codegen_acl_details,
    )

    stored_view_acl_details, stored_codegen_acl_details = (
        profile.get_required_strategy("support_readonly")
    )

    assert stored_view_acl_details is view_acl_details
    assert stored_codegen_acl_details is codegen_acl_details
    assert profile.list_strategy_names() == ["default", "support_readonly"]


def test_frame_acl_profile_rejects_invalid_construction_and_strategy_registration() -> None:
    """
    Verify profile construction and strategy registration fail fast on bad
    inputs.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="name cannot be empty"):
        FrameACLProfile("")

    with pytest.raises(TypeError, match="view_acl_details must be a ViewACLDetails"):
        FrameACLProfile("support", view_acl_details=object())

    with pytest.raises(TypeError, match="codegen_acl_details must be a CodegenACLDetails"):
        FrameACLProfile("support", codegen_acl_details=object())

    profile = FrameACLProfile("support")

    with pytest.raises(ValueError, match="strategy_name cannot be empty"):
        profile.register_strategy("", ViewACLDetails(), CodegenACLDetails())

    with pytest.raises(TypeError, match="view_acl_details must be a ViewACLDetails"):
        profile.register_strategy("bad", object(), CodegenACLDetails())

    with pytest.raises(TypeError, match="codegen_acl_details must be a CodegenACLDetails"):
        profile.register_strategy("bad", ViewACLDetails(), object())


def test_frame_acl_profile_cleanup_cleans_owned_details() -> None:
    """
    Verify profile cleanup cascades through owned strategy details.

    Returns:
        None.
    """
    profile = FrameACLProfile("support")
    default_view_acl_details = profile.view_acl_details
    default_codegen_acl_details = profile.codegen_acl_details
    extra_view_acl_details = ViewACLDetails('{"x":1}')
    extra_codegen_acl_details = CodegenACLDetails('{"y":2}')
    profile.register_strategy(
        "support_readonly",
        extra_view_acl_details,
        extra_codegen_acl_details,
    )

    profile.cleanup()

    assert profile.cleaned is True
    assert default_view_acl_details.cleaned is True
    assert default_codegen_acl_details.cleaned is True
    assert extra_view_acl_details.cleaned is True
    assert extra_codegen_acl_details.cleaned is True


def test_frame_acl_manager_exposes_version_and_profile_registry_surface() -> None:
    """
    Verify the manager exposes the version string and profile registry
    mechanics.

    Returns:
        None.
    """
    manager = FrameACLManager()
    support_profile = FrameACLProfile("support")

    manager._register_frame_acl_profile(support_profile)

    assert manager.version == "0.0.1"
    assert manager.id is not None
    assert manager._get_required_frame_acl_profile("support") is support_profile
    assert manager._list_frame_acl_profile_names() == ["support"]
    assert manager.frame_acl_profiles_by_name == {"support": support_profile}


def test_frame_acl_manager_profile_replace_and_remove_cleanup_old_profiles() -> None:
    """
    Verify manager profile replacement and removal clean old profile objects.

    Returns:
        None.
    """
    manager = FrameACLManager()
    first_profile = FrameACLProfile("support")
    second_profile = FrameACLProfile("support")

    manager._register_frame_acl_profile(first_profile)
    manager._register_frame_acl_profile(second_profile)

    assert first_profile.cleaned is True
    assert manager._get_required_frame_acl_profile("support") is second_profile
    assert manager._remove_frame_acl_profile("support") is True
    assert second_profile.cleaned is True
    assert manager._remove_frame_acl_profile("support") is False
    with pytest.raises(KeyError, match="support"):
        manager._get_required_frame_acl_profile("support")
