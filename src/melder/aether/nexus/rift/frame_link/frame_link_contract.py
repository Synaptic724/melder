"""
Internal FrameLinkContract object.

Purpose:
    Represent the effective contract boundary applied to one frame-surface
    connection after ACL compilation and downstream projection shaping.
"""

from typing import Dict, Optional, Sequence, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.frame_acl_compiled_access_surface import (
    CompiledFrameACLAccessSurface,
)
from melder.aether.nexus.rift.frame_link.profiles.frame_link_contract_profile import (
    FrameLinkContractProfile,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameLinkContract(Cleanable):
    """
    Internal

    Purpose:
        Hold the effective consumer-facing contract for one frame-surface
        connection.

    Contract:
        - Carries derived allowed kinds/commands plus lightweight metadata.
        - Can be created directly or shaped from a compiled ACL access surface.
        - Optional downstream contract profiles may further narrow the compiled
          access output without redefining ACL truth.
        - Cleanup is idempotent and clears owned references.

    Lifecycle:
        Intended to sit close to the Nexus-owned frame-surface update path as
        the downstream consumer-facing contract object.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_contract_id",
        "_frame_name",
        "_allowed_kinds",
        "_allowed_commands",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            frame_name: str,
            allowed_kinds: Optional[Sequence[str]] = None,
            allowed_commands: Optional[Sequence[str]] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Internal

        Initialize one placeholder frame-link contract.

        Args:
            frame_name:
                Canonical frame name this contract applies to.
            allowed_kinds:
                Optional visible kind names for the linked surface.
            allowed_commands:
                Optional command descriptors allowed by this contract.
            metadata:
                Optional free-form contract metadata.

        Returns:
            None.
        """
        super().__init__()
        self._contract_id: str = IDBuilder.create_id()
        self._frame_name: str = frame_name
        self._allowed_kinds: Tuple[str, ...] = tuple(allowed_kinds) if allowed_kinds else tuple()
        self._allowed_commands: Tuple[str, ...] = (
            tuple(allowed_commands) if allowed_commands else tuple()
        )
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}

    @classmethod
    def from_compiled_access_surface(
            cls,
            compiled_access_surface: CompiledFrameACLAccessSurface,
            *,
            contract_profile: Optional[FrameLinkContractProfile] = None,
    ) -> "FrameLinkContract":
        """
        Build one frame-link contract from compiled ACL access output.

        Args:
            compiled_access_surface:
                Derived compiled ACL access surface.
            contract_profile:
                Optional downstream contract profile used to narrow the final
                projection.

        Returns:
            FrameLinkContract: Effective downstream frame-link contract.
        """
        if not isinstance(compiled_access_surface, CompiledFrameACLAccessSurface):
            raise TypeError(
                "compiled_access_surface must be a CompiledFrameACLAccessSurface."
            )
        if (
                contract_profile is not None
                and not isinstance(contract_profile, FrameLinkContractProfile)
        ):
            raise TypeError(
                "contract_profile must be a FrameLinkContractProfile."
            )

        allowed_kinds = set(compiled_access_surface.allowed_kinds)
        allowed_commands = set(compiled_access_surface.allowed_commands)
        metadata = compiled_access_surface.metadata

        if contract_profile is not None:
            view_profile = contract_profile.view_profile
            codegen_profile = contract_profile.codegen_profile
            if len(view_profile.allowed_kinds) > 0:
                allowed_kinds = allowed_kinds.intersection(
                    set(view_profile.allowed_kinds)
                )
            if len(codegen_profile.allowed_commands) > 0:
                allowed_commands = allowed_commands.intersection(
                    set(codegen_profile.allowed_commands)
                )
            metadata.update({
                "frame_link_profile_name": contract_profile.name,
                "frame_link_profile_version": contract_profile.version,
                "frame_link_view_profile_name": view_profile.name,
                "frame_link_view_profile_version": view_profile.version,
                "frame_link_codegen_profile_name": codegen_profile.name,
                "frame_link_codegen_profile_version": codegen_profile.version,
                "frame_payload_fields": tuple(
                    field_name
                    for field_name in compiled_access_surface.frame_payload_fields
                    if "frame" in allowed_kinds
                    and (
                        len(view_profile.frame_payload_fields) == 0
                        or field_name in view_profile.frame_payload_fields
                    )
                ),
                "conduit_payload_sections_by_id": {
                    conduit_id: tuple(
                        section_name
                        for section_name in sections
                        if "conduit" in allowed_kinds
                        and (
                            len(view_profile.conduit_payload_sections) == 0
                            or section_name in view_profile.conduit_payload_sections
                        )
                    )
                    for conduit_id, sections in (
                        compiled_access_surface.conduit_payload_sections_by_id.items()
                    )
                },
                "spell_payload_sections_by_key": {
                    record_key: tuple(
                        section_name
                        for section_name in sections
                        if "spell" in allowed_kinds
                        and (
                            len(view_profile.spell_payload_sections) == 0
                            or section_name in view_profile.spell_payload_sections
                        )
                    )
                    for record_key, sections in (
                        compiled_access_surface.spell_payload_sections_by_key.items()
                    )
                },
            })

        return cls(
            frame_name=compiled_access_surface.frame_name,
            allowed_kinds=tuple(sorted(allowed_kinds)),
            allowed_commands=tuple(sorted(allowed_commands)),
            metadata=metadata,
        )

    @property
    def contract_id(self) -> str:
        """Return the canonical contract id."""
        self.check_cleaned()
        return self._contract_id

    @property
    def frame_name(self) -> str:
        """Return the frame name this contract applies to."""
        self.check_cleaned()
        return self._frame_name

    @property
    def allowed_kinds(self) -> Tuple[str, ...]:
        """Return the currently declared visible kinds."""
        self.check_cleaned()
        return self._allowed_kinds

    @property
    def allowed_commands(self) -> Tuple[str, ...]:
        """Return the currently declared command descriptors."""
        self.check_cleaned()
        return self._allowed_commands

    @property
    def metadata(self) -> Dict[str, object]:
        """Return the contract metadata map."""
        self.check_cleaned()
        return self._metadata

    def cleanup(self) -> None:
        """
        Internal

        Idempotently clear contract-owned state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._frame_name = None
        self._allowed_kinds = None
        self._allowed_commands = None
        self._metadata.clear()
        self._metadata = None
        self._contract_id = None
