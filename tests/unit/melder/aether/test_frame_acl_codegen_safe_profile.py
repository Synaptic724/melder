from melder.aether.nexus.acl.configurations.profiles.codegen.safe_profile import (
    create_safe_codegen_profile,
)
from melder.aether.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)


def test_safe_codegen_profile_exposes_expected_identity_and_rulesets() -> None:
    """
    Verify the reusable safe codegen profile exposes the expected contract.

    Returns:
        None.
    """
    profile = create_safe_codegen_profile()

    assert isinstance(profile, FrameACLCodegenProfile)
    assert profile.name == "safe"
    assert profile.frame_ruleset.name == "safe_frame_codegen"
    assert profile.conduit_ruleset.name == "safe_conduit_codegen"
    assert profile.spell_ruleset.name == "safe_spell_codegen"
    assert profile.capability_ruleset.name == "safe_capability_codegen"

    frame_rules = profile.frame_ruleset.rules_by_name
    conduit_rules = profile.conduit_ruleset.rules_by_name
    spell_rules = profile.spell_ruleset.rules_by_name
    capability_rules = profile.capability_ruleset.rules_by_name

    assert frame_rules["frame_query"].effect == "allow"

    assert conduit_rules["conduit_query"].effect == "allow"
    assert conduit_rules["conduit_link"].effect == "deny"
    assert conduit_rules["conduit_unlink"].effect == "deny"
    assert conduit_rules["conduit_create_lesser"].effect == "deny"
    assert conduit_rules["conduit_transfer_ownership"].effect == "deny"

    assert spell_rules["spell_resolve_existing"].effect == "allow"
    assert spell_rules["spell_bind_existing"].effect == "allow"
    assert spell_rules["spell_local_create"].effect == "deny"
    assert spell_rules["spell_invoke_method"].effect == "deny"
    assert spell_rules["spell_read_attribute"].effect == "deny"
    assert spell_rules["spell_write_attribute"].effect == "deny"

    assert capability_rules["capability_dynamic_access"].effect == "deny"
    assert capability_rules["capability_mutation"].effect == "deny"
    assert capability_rules["capability_contract_override"].effect == "deny"
    assert capability_rules["capability_unsafe_reflection"].effect == "deny"
    assert capability_rules["capability_dunder_access"].effect == "deny"
