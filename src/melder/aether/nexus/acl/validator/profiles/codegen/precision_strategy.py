from melder.aether.nexus.acl.configurations.frame_acl_codegen_configuration import (
    FrameACLCodegenConfiguration,
)
from melder.aether.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)


def validate_profile_configuration(
        profile: FrameACLCodegenProfile,
        configuration: FrameACLCodegenConfiguration,
) -> None:
    """
    Validate that a precision codegen config keeps local creation closed.

    Returns:
        None.
    """
    _ = profile
    for rule in configuration.spell_override_ruleset.rules_by_name.values():
        if rule.effect == "allow" and rule.operation == "local_create":
            raise ValueError(
                "Precision codegen profile cannot allow local_create in spell overrides."
            )
