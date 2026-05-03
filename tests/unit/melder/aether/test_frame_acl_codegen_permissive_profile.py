from melder.aether.nexus.acl.configurations.profiles.codegen.permissive_profile import (
    PermissiveCodegenProfileStrategy,
)
from melder.aether.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)


def test_permissive_codegen_profile_exposes_expected_identity_and_rulesets() -> None:
    """
    Verify the reusable permissive codegen profile exposes the expected contract.

    Returns:
        None.
    """
    profile = PermissiveCodegenProfileStrategy().build()

    assert isinstance(profile, FrameACLCodegenProfile)
    assert profile.name == "permissive"
    assert profile.frame_ruleset.name == "permissive_frame_codegen"
    assert profile.conduit_ruleset.name == "permissive_conduit_codegen"
    assert profile.spell_ruleset.name == "permissive_spell_codegen"
    assert profile.capability_ruleset.name == "permissive_capability_codegen"

    frame_rules = profile.frame_ruleset.rules_by_name
    conduit_rules = profile.conduit_ruleset.rules_by_name
    spell_rules = profile.spell_ruleset.rules_by_name
    capability_rules = profile.capability_ruleset.rules_by_name

    assert frame_rules["frame_query"].effect == "allow"

    assert conduit_rules["conduit_query"].effect == "allow"
    assert conduit_rules["conduit_link"].effect == "allow"
    assert conduit_rules["conduit_unlink"].effect == "allow"
    assert conduit_rules["conduit_create_lesser"].effect == "allow"
    assert conduit_rules["conduit_transfer_ownership"].effect == "allow"

    assert spell_rules["spell_resolve_existing"].effect == "allow"
    assert spell_rules["spell_bind_existing"].effect == "allow"
    assert spell_rules["spell_local_create"].effect == "allow"
    assert spell_rules["spell_invoke_method"].effect == "allow"
    assert spell_rules["spell_read_attribute"].effect == "allow"
    assert spell_rules["spell_write_attribute"].effect == "allow"

    assert capability_rules["capability_dynamic_access"].effect == "allow"
    assert capability_rules["capability_contract_override"].effect == "allow"
    assert capability_rules["capability_mutation"].effect == "allow"
    assert capability_rules["capability_unsafe_reflection"].effect == "allow"
    assert capability_rules["capability_dunder_access"].effect == "allow"
    assert capability_rules["capability_recursive_codegen"].effect == "allow"
    assert capability_rules["capability_enable_imports"].effect == "allow"
    assert capability_rules["capability_allow_import_modules"].effect == "allow"
