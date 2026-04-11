from melder.aether.nexus.acl.profiles.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.aether.nexus.acl.profiles.view.hybrid_profile import (
    create_hybrid_view_profile,
)


def test_hybrid_view_profile_exposes_expected_identity_and_rulesets() -> None:
    """
    Verify the reusable hybrid view profile exposes the expected contract.

    Returns:
        None.
    """
    profile = create_hybrid_view_profile()

    assert isinstance(profile, FrameACLViewProfile)
    assert profile.name == "hybrid"
    assert profile.required_nexus_label == "default"
    assert profile.required_nexus_version == "0.0.1"
    assert profile.minimum_spell_payload_type == "general"
    assert profile.minimum_spell_payload_version == "0.0.1"
    assert profile.frame_ruleset.name == "hybrid_frame"
    assert profile.conduit_ruleset.name == "hybrid_conduit"
    assert profile.spell_ruleset.name == "hybrid_spell"
    assert profile.member_ruleset.name == "hybrid_member"

    frame_rules = profile.frame_ruleset.rules_by_name
    conduit_rules = profile.conduit_ruleset.rules_by_name
    spell_rules = profile.spell_ruleset.rules_by_name
    member_rules = profile.member_ruleset.rules_by_name

    assert frame_rules["frame_visible"].effect == "allow"
    assert frame_rules["frame_show_payload"].effect == "allow"

    assert conduit_rules["conduit_visible"].effect == "allow"
    assert conduit_rules["conduit_show_payload"].effect == "allow"
    assert conduit_rules["conduit_show_policy"].effect == "allow"
    assert conduit_rules["conduit_show_peer_links"].effect == "allow"

    assert spell_rules["spell_visible"].effect == "allow"
    assert spell_rules["spell_show_binding_payload"].effect == "allow"
    assert spell_rules["spell_show_resolution_payload"].effect == "allow"
    assert spell_rules["spell_show_metadata"].effect == "allow"
    assert spell_rules["spell_show_class_profile"].effect == "allow"
    assert spell_rules["spell_show_callable_profile"].effect == "allow"
    assert spell_rules["spell_hide_instance_members"].effect == "deny"
    assert spell_rules["spell_hide_dynamic_access"].effect == "deny"

    assert member_rules["member_hide_dunder_pattern"].effect == "deny"
    assert member_rules["member_hide___dict__"].effect == "deny"
    assert member_rules["member_hide___class__"].effect == "deny"
