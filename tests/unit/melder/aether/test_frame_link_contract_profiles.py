import pytest

from melder.aether.nexus.acl.frame_acl_compiled_access_surface import (
    CompiledFrameACLAccessSurface,
)
from melder.aether.nexus.rift.frame_link.frame_link_contract import (
    FrameLinkContract,
)
from melder.aether.nexus.rift.frame_link.profiles.frame_link_contract_profile import (
    FrameLinkContractProfile,
)
from melder.aether.nexus.rift.frame_link.profiles.frame_link_contract_profile_builder import (
    FrameLinkContractProfileBuilder,
)
from melder.aether.nexus.rift.frame_link.profiles.frame_link_view_profile import (
    FrameLinkViewProfile,
)
from melder.aether.nexus.rift.frame_link.profiles.hybrid_profile import (
    create_hybrid_frame_link_contract_profile,
)
from melder.aether.nexus.rift.frame_link.profiles.permissive_profile import (
    create_permissive_frame_link_contract_profile,
)
from melder.aether.nexus.rift.frame_link.profiles.safe_profile import (
    create_safe_frame_link_contract_profile,
)


def _build_compiled_surface() -> CompiledFrameACLAccessSurface:
    """
    Build one compiled ACL access surface for frame-link contract tests.

    Returns:
        CompiledFrameACLAccessSurface:
            Compiled surface with frame, conduit, and spell visibility.
    """
    return CompiledFrameACLAccessSurface(
        frame_name="ops",
        configuration_id="cfg-1",
        view_profile_name="safe",
        view_profile_version="0.0.1",
        codegen_profile_name="safe",
        codegen_profile_version="0.0.1",
        allowed_kinds=("frame", "conduit", "spell"),
        allowed_commands=("bind_existing", "query", "resolve_existing"),
        frame_payload_fields=("system_state", "rift_enabled", "root_conduit_count"),
        visible_conduit_ids=("conduit-1",),
        visible_spell_keys=(("spellbook-1", "spell-1"),),
        conduit_payload_sections_by_id={
            "conduit-1": ("conduit_name", "conduit_state", "policy"),
        },
        spell_payload_sections_by_key={
            ("spellbook-1", "spell-1"): (
                "binding_payload",
                "resolution_payload",
                "metadata",
                "class_profile",
            ),
        },
        metadata={"source": "compiled"},
    )


def test_frame_link_view_profile_requires_non_empty_name_and_version() -> None:
    """
    Verify frame-link view profiles reject invalid required identity fields.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="name cannot be empty"):
        FrameLinkViewProfile("")

    with pytest.raises(ValueError, match="version cannot be empty"):
        FrameLinkViewProfile("safe", version="")


def test_frame_link_view_profile_defaults_to_empty_filters() -> None:
    """
    Verify frame-link view profiles default to empty narrowing filters.

    Returns:
        None.
    """
    profile = FrameLinkViewProfile("safe")

    assert profile.allowed_kinds == tuple()
    assert profile.frame_payload_fields == tuple()
    assert profile.conduit_payload_sections == tuple()
    assert profile.spell_payload_sections == tuple()


def test_frame_link_view_profile_cleanup_clears_owned_state() -> None:
    """
    Verify frame-link view profile cleanup clears owned projection state.

    Returns:
        None.
    """
    profile = FrameLinkViewProfile(
        "safe",
        allowed_kinds=("frame",),
        frame_payload_fields=("system_state",),
    )

    profile.cleanup()

    assert profile.cleaned is True
    assert profile._allowed_kinds is None
    assert profile._frame_payload_fields is None
    assert profile._conduit_payload_sections is None
    assert profile._spell_payload_sections is None


def test_frame_link_contract_profile_requires_view_profile_only() -> None:
    """
    Verify downstream contract profiles only require a typed view profile.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="name cannot be empty"):
        FrameLinkContractProfile(
            "",
            view_profile=FrameLinkViewProfile("safe"),
        )

    with pytest.raises(TypeError, match="view_profile must be a FrameLinkViewProfile"):
        FrameLinkContractProfile(
            "safe",
            view_profile=object(),
        )


def test_frame_link_contract_profile_cleanup_clears_profile_reference() -> None:
    """
    Verify composed downstream contract profile cleanup clears the view ref.

    Returns:
        None.
    """
    profile = FrameLinkContractProfile(
        "safe",
        view_profile=FrameLinkViewProfile("safe"),
    )

    profile.cleanup()

    assert profile.cleaned is True
    assert profile._view_profile is None


def test_frame_link_contract_profile_builder_seeds_named_catalog() -> None:
    """
    Verify the downstream contract profile builder seeds safe/hybrid/permissive.

    Returns:
        None.
    """
    builder = FrameLinkContractProfileBuilder()

    assert builder.version == "0.0.1"
    assert builder.list_profile_names() == ["safe", "hybrid", "permissive"]


def test_frame_link_contract_profile_builder_get_required_profile_raises_missing_name() -> None:
    """
    Verify missing downstream contract profiles fail fast.

    Returns:
        None.
    """
    with pytest.raises(KeyError, match="missing"):
        FrameLinkContractProfileBuilder().get_required_profile("missing")


def test_frame_link_contract_profile_builder_replacing_profile_cleans_old_profile() -> None:
    """
    Verify replacing a downstream contract profile cleans the old object.

    Returns:
        None.
    """
    builder = FrameLinkContractProfileBuilder()
    first_profile = FrameLinkContractProfile(
        "custom",
        view_profile=FrameLinkViewProfile("custom"),
    )
    second_profile = FrameLinkContractProfile(
        "custom",
        view_profile=FrameLinkViewProfile("custom"),
    )

    builder.register_profile(first_profile)
    builder.register_profile(second_profile)

    assert first_profile.cleaned is True
    assert builder.get_required_profile("custom") is second_profile


def test_frame_link_contract_profile_builder_register_rejects_invalid_type() -> None:
    """
    Verify downstream profile registration rejects invalid objects.

    Returns:
        None.
    """
    with pytest.raises(TypeError, match="profile must be a FrameLinkContractProfile"):
        FrameLinkContractProfileBuilder().register_profile(None)


def test_frame_link_contract_profile_builder_cleanup_cascades_to_owned_profiles() -> None:
    """
    Verify downstream profile-builder cleanup cascades into owned profiles.

    Returns:
        None.
    """
    builder = FrameLinkContractProfileBuilder()
    safe_profile = builder.get_required_profile("safe")

    builder.cleanup()

    assert builder.cleaned is True
    assert safe_profile.cleaned is True
    assert builder._profiles_by_name is None


def test_safe_frame_link_contract_profile_has_expected_view_shape() -> None:
    """
    Verify the safe downstream contract profile carries the expected view filters.

    Returns:
        None.
    """
    profile = create_safe_frame_link_contract_profile()

    assert profile.name == "safe"
    assert profile.view_profile.allowed_kinds == ("frame", "conduit", "spell")
    assert profile.view_profile.frame_payload_fields == (
        "system_state",
        "rift_enabled",
    )


def test_hybrid_frame_link_contract_profile_has_expected_view_shape() -> None:
    """
    Verify the hybrid downstream contract profile carries the expected view filters.

    Returns:
        None.
    """
    profile = create_hybrid_frame_link_contract_profile()

    assert profile.name == "hybrid"
    assert "root_conduit_count" in profile.view_profile.frame_payload_fields
    assert "policy" in profile.view_profile.conduit_payload_sections


def test_permissive_frame_link_contract_profile_has_expected_view_shape() -> None:
    """
    Verify the permissive downstream contract profile carries the widest view filters.

    Returns:
        None.
    """
    profile = create_permissive_frame_link_contract_profile()

    assert profile.name == "permissive"
    assert "ai_native_enabled" in profile.view_profile.frame_payload_fields
    assert "peer_conduit_ids" in profile.view_profile.conduit_payload_sections


def test_frame_link_contract_from_compiled_access_surface_rejects_invalid_inputs() -> None:
    """
    Verify contract shaping rejects invalid compiled surfaces and profiles.

    Returns:
        None.
    """
    with pytest.raises(TypeError, match="compiled_access_surface must be a CompiledFrameACLAccessSurface"):
        FrameLinkContract.from_compiled_access_surface(None)

    with pytest.raises(TypeError, match="contract_profile must be a FrameLinkContractProfile"):
        FrameLinkContract.from_compiled_access_surface(
            _build_compiled_surface(),
            contract_profile=object(),
        )


def test_frame_link_contract_without_profile_retains_compiled_exposure() -> None:
    """
    Verify direct contract shaping retains compiled exposure without narrowing.

    Returns:
        None.
    """
    contract = FrameLinkContract.from_compiled_access_surface(
        _build_compiled_surface()
    )

    assert contract.frame_name == "ops"
    assert contract.allowed_kinds == ("conduit", "frame", "spell")
    assert contract.metadata["source"] == "compiled"


def test_frame_link_contract_with_profile_narrows_exposure() -> None:
    """
    Verify downstream profiles narrow the compiled exposure projection.

    Returns:
        None.
    """
    contract_profile = FrameLinkContractProfile(
        "frame_only",
        view_profile=FrameLinkViewProfile(
            "frame_only",
            allowed_kinds=("frame",),
            frame_payload_fields=("system_state",),
        ),
    )

    contract = FrameLinkContract.from_compiled_access_surface(
        _build_compiled_surface(),
        contract_profile=contract_profile,
    )

    assert contract.allowed_kinds == ("frame",)
    assert contract.metadata["frame_payload_fields"] == ("system_state",)
    assert contract.metadata["conduit_payload_sections_by_id"] == {
        "conduit-1": tuple(),
    }
    assert contract.metadata["spell_payload_sections_by_key"] == {
        ("spellbook-1", "spell-1"): tuple(),
    }


def test_frame_link_contract_profile_with_empty_filters_does_not_narrow_exposure() -> None:
    """
    Verify empty downstream filters preserve the compiled exposure.

    Returns:
        None.
    """
    contract_profile = FrameLinkContractProfile(
        "passthrough",
        view_profile=FrameLinkViewProfile("passthrough"),
    )

    contract = FrameLinkContract.from_compiled_access_surface(
        _build_compiled_surface(),
        contract_profile=contract_profile,
    )

    assert contract.allowed_kinds == tuple(sorted(_build_compiled_surface().allowed_kinds))
    assert contract.metadata["frame_payload_fields"] == (
        "system_state",
        "rift_enabled",
        "root_conduit_count",
    )


def test_frame_link_contract_cleanup_clears_owned_state() -> None:
    """
    Verify frame-link contract cleanup clears owned state.

    Returns:
        None.
    """
    contract = FrameLinkContract.from_compiled_access_surface(
        _build_compiled_surface()
    )

    contract.cleanup()

    assert contract.cleaned is True
    assert contract._frame_name is None
    assert contract._allowed_kinds is None
    assert contract._metadata is None


def test_frame_link_contract_helper_methods_expose_effective_contract_shape() -> None:
    """
    Verify contract helper APIs expose the effective exposure shape.

    Returns:
        None.
    """
    contract = FrameLinkContract.from_compiled_access_surface(
        _build_compiled_surface()
    )

    assert contract.allows_kind("frame") is True
    assert contract.allows_kind("mutation") is False
    assert contract.get_frame_payload_fields() == (
        "system_state",
        "rift_enabled",
        "root_conduit_count",
    )
    assert contract.get_conduit_payload_sections("conduit-1") == (
        "conduit_name",
        "conduit_state",
        "policy",
    )
    assert contract.get_spell_payload_sections(("spellbook-1", "spell-1")) == (
        "binding_payload",
        "resolution_payload",
        "metadata",
        "class_profile",
    )
    assert contract.describe() == {
        "frame_name": "ops",
        "allowed_kinds": ("conduit", "frame", "spell"),
        "frame_payload_fields": (
            "system_state",
            "rift_enabled",
            "root_conduit_count",
        ),
        "conduit_count": 1,
        "spell_count": 1,
    }


def test_frame_link_contract_helper_methods_reject_invalid_inputs() -> None:
    """
    Verify contract helper APIs reject invalid subject keys.

    Returns:
        None.
    """
    contract = FrameLinkContract.from_compiled_access_surface(
        _build_compiled_surface()
    )

    with pytest.raises(ValueError, match="source_kind cannot be empty"):
        contract.allows_kind("")

    with pytest.raises(ValueError, match="conduit_id cannot be empty"):
        contract.get_conduit_payload_sections("")

    with pytest.raises(ValueError, match="record_key must be a non-empty 2-item tuple"):
        contract.get_spell_payload_sections(("spellbook-1",))
