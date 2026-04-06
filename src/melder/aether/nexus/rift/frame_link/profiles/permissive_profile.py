from melder.aether.nexus.rift.frame_link.profiles.frame_link_contract_profile import (
    FrameLinkContractProfile,
)
from melder.aether.nexus.rift.frame_link.profiles.frame_link_view_profile import (
    FrameLinkViewProfile,
)


def create_permissive_frame_link_contract_profile() -> FrameLinkContractProfile:
    """
    Build the reusable downstream `permissive` frame-link contract profile.

    Returns:
        FrameLinkContractProfile: Reusable downstream `permissive` contract
        profile.
    """
    return FrameLinkContractProfile(
        "permissive",
        view_profile=FrameLinkViewProfile(
            "permissive",
            allowed_kinds=("frame", "conduit", "spell"),
            frame_payload_fields=(
                "system_state",
                "ai_native_enabled",
                "rift_enabled",
                "root_conduit_count",
                "root_conduit_ids",
            ),
            conduit_payload_sections=(
                "conduit_name",
                "conduit_state",
                "policy",
                "peer_conduit_ids",
            ),
            spell_payload_sections=(
                "binding_payload",
                "resolution_payload",
                "metadata",
                "class_profile",
                "callable_profile",
                "instance_members",
                "dynamic_access",
            ),
        ),
    )
