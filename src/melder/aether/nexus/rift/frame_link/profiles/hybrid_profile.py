from melder.aether.nexus.rift.frame_link.profiles.frame_link_codegen_profile import (
    FrameLinkCodegenProfile,
)
from melder.aether.nexus.rift.frame_link.profiles.frame_link_contract_profile import (
    FrameLinkContractProfile,
)
from melder.aether.nexus.rift.frame_link.profiles.frame_link_view_profile import (
    FrameLinkViewProfile,
)


def create_hybrid_frame_link_contract_profile() -> FrameLinkContractProfile:
    """
    Build the reusable downstream `hybrid` frame-link contract profile.

    Returns:
        FrameLinkContractProfile: Reusable downstream `hybrid` contract profile.
    """
    return FrameLinkContractProfile(
        "hybrid",
        view_profile=FrameLinkViewProfile(
            "hybrid",
            allowed_kinds=("frame", "conduit", "spell"),
            frame_payload_fields=("system_state", "rift_enabled", "root_conduit_count"),
            conduit_payload_sections=("conduit_name", "conduit_state", "policy"),
            spell_payload_sections=(
                "binding_payload",
                "resolution_payload",
                "metadata",
                "class_profile",
                "callable_profile",
            ),
        ),
        codegen_profile=FrameLinkCodegenProfile(
            "hybrid",
            allowed_commands=(
                "bind_existing",
                "invoke_method",
                "link",
                "query",
                "read_attribute",
                "resolve_existing",
                "unlink",
            ),
        ),
    )

