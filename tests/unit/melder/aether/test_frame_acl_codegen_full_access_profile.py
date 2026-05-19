from melder.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.nexus.acl.configurations.profiles.codegen.full_access_profile import (
    FullAccessCodegenProfileStrategy,
)


def test_full_access_codegen_profile_exposes_expected_identity_and_rulesets() -> None:
    """
    Verify the reusable full-access codegen profile exposes the expected
    contract.

    Returns:
        None.
    """
    profile = FullAccessCodegenProfileStrategy().build()

    assert isinstance(profile, FrameACLCodegenProfile)
    assert profile.name == "full_access"
    assert profile.frame_ruleset.name == "full_access_frame_codegen"
    assert profile.conduit_ruleset.name == "full_access_conduit_codegen"
    assert profile.spell_ruleset.name == "full_access_spell_codegen"
    assert profile.capability_ruleset.name == "full_access_capability_codegen"

    capability_rules = profile.capability_ruleset.rules_by_name

    assert capability_rules["capability_enable_imports"].effect == "allow"
    assert capability_rules["capability_dynamic_access"].effect == "allow"
    assert capability_rules["capability_contract_override"].effect == "allow"
    assert capability_rules["capability_mutation"].effect == "allow"
    assert capability_rules["capability_unsafe_reflection"].effect == "allow"
    assert capability_rules["capability_dunder_access"].effect == "allow"
    assert capability_rules["capability_recursive_codegen"].effect == "allow"
