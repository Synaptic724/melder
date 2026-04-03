"""
Internal FrameLinkContract placeholder.

Purpose:
    Represent the contract boundary applied to a frame-surface connection
    without yet integrating it into the live `Nexus` / `Rift` update model.

Responsibilities:
    - Carry the current allowed kinds/commands/metadata for one frame-surface
      connection.
    - Stay lightweight and cleanup-safe while the HLD is still evolving.

Endgame:
    `FrameLinkContract` should eventually capture the effective policy contract
    that shapes what a `FrameView` may perceive from Nexus-owned frame
    representations.
"""

from typing import Dict, Optional, Sequence, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameLinkContract(Cleanable):
    """
    Internal

    Placeholder contract object for one frame-surface connection.

    Purpose:
        Hold the minimum stable shape for future frame-surface contract data
        without committing to the final ACL/update semantics yet.

    Contract:
        - Owns only lightweight immutable-ish policy/config snapshots.
        - Cleanup is idempotent and clears owned references.

    Lifecycle:
        Placeholder only. Future ownership is expected to sit close to the
        `Nexus`-owned frame-surface update path.

    TODO(HLD):
        This object still needs its final field contract, but the intended
        direction is now clear enough to record here:

        - This should carry the effective contract boundary for one
          frame-surface connection.
        - The contract should describe what a linked consumer is allowed to
          perceive and which generic commands are available at the view layer.
        - This object should not execute ACL logic itself. It should represent
          the contract after Nexus/policy evaluation has already happened.
        - The contract should stay separate from raw runtime object access.
          Real object acquisition still belongs to the Rift/conduit bind path.
        - This contract will likely shape:
            * visible kinds
            * command descriptors
            * view density / projection posture
            * later access flags or redaction posture
        - This object should remain lightweight so it can be updated often if
          lower truth churns quickly.
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
