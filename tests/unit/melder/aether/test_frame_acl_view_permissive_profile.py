from melder.aether.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.aether.nexus.acl.configurations.profiles.view.permissive_profile import (
    create_permissive_view_profile,
)


def test_permissive_view_profile_exposes_expected_identity_and_rulesets() -> None:
    """
    Verify the reusable permissive view profile exposes the expected contract.

    Returns:
        None.
    """
    profile = create_permissive_view_profile()

    assert isinstance(profile, FrameACLViewProfile)
    assert profile.name == "permissive"
    assert profile.required_nexus_label == "default"
    assert profile.required_nexus_version == "0.0.1"
    assert profile.minimum_spell_payload_type == "general"
    assert profile.minimum_spell_payload_version == "0.0.1"
    assert profile.frame_ruleset.name == "permissive_frame"
    assert profile.conduit_ruleset.name == "permissive_conduit"
    assert profile.spell_ruleset.name == "permissive_spell"
    assert profile.member_ruleset.name == "permissive_member"

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
    assert spell_rules["spell_show_instance_members"].effect == "allow"
    assert spell_rules["spell_show_dynamic_access"].effect == "allow"

    assert member_rules["member_hide_dunder_pattern"].effect == "deny"
    assert member_rules["member_hide___dict__"].effect == "deny"
