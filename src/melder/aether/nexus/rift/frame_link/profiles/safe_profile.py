from melder.aether.nexus.rift.frame_link.profiles.frame_link_codegen_profile import (
    FrameLinkCodegenProfile,
)
from melder.aether.nexus.rift.frame_link.profiles.frame_link_contract_profile import (
    FrameLinkContractProfile,
)
from melder.aether.nexus.rift.frame_link.profiles.frame_link_view_profile import (
    FrameLinkViewProfile,
)


def create_safe_frame_link_contract_profile() -> FrameLinkContractProfile:
    """
    Build the reusable downstream `safe` frame-link contract profile.

    Returns:
        FrameLinkContractProfile: Reusable downstream `safe` contract profile.
    """
    return FrameLinkContractProfile(
        "safe",
        view_profile=FrameLinkViewProfile(
            "safe",
            allowed_kinds=("frame", "conduit", "spell"),
            frame_payload_fields=("system_state", "rift_enabled"),
            conduit_payload_sections=("conduit_name", "conduit_state"),
            spell_payload_sections=("binding_payload", "resolution_payload", "metadata"),
        ),
        codegen_profile=FrameLinkCodegenProfile(
            "safe",
            allowed_commands=("bind_existing", "query", "resolve_existing"),
        ),
    )

