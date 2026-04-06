"""
Internal FrameLink placeholder.

Purpose:
    Represent one frame-surface connection unit that a future `FrameView`
    can hold and reason over.

Responsibilities:
    - Carry stable identity for one linked surface unit.
    - Point at the source frame and contract without exposing raw runtime
      objects directly.

Endgame:
    `FrameLink` should eventually represent the connection between a `Rift`
    and Nexus-owned frame-surface representations, carrying the applied
    contract boundary needed by `FrameView`.
"""

import threading
from typing import Dict, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.rift.frame_link.frame_link_contract import FrameLinkContract
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameLink(Cleanable):
    """
    Internal

    Placeholder link object for the frame-surface model.

    Purpose:
        Hold the minimum stable identity and contract pointer needed for the
        future frame-surface query/display system.

    Contract:
        - Does not expose raw frame/runtime objects.
        - Holds only stable ids/names plus the contract reference.
        - Cleanup is idempotent and clears owned references.

    Lifecycle:
        Placeholder only. Future ownership is expected to sit with `Rift`
        while source truth remains on the `Nexus` side.

    TODO(HLD):
        The final meaning of this object is more specific than a generic data
        bag:

        - Nexus should own and update the canonical `FrameLink`
          representations when frame/spell/conduit truth changes.
        - A `FrameLink` should be the canonical representational unit that a
          `FrameView` consumes, not the raw runtime object.
        - It should contain what the viewer is allowed to perceive, not the
          machinery that decides the ACLs.
        - It should not own:
            * raw runtime object references handed directly to the agent
            * binding/execution behavior
            * thread/eventloop/orchestration state
        - It should eventually expose enough stable identity for:
            * frame-scoped lookup
            * kind/source classification
            * display naming
            * command discovery
            * ACL-shaped representation
        - Think of this as the view-safe connection object between the Rift
          side and Nexus-owned representational truth.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_link_id",
        "_lock",
        "_frame_name",
        "_source_kind",
        "_source_id",
        "_display_name",
        "_contract",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            frame_name: str,
            source_kind: str,
            source_id: str,
            display_name: Optional[str] = None,
            contract: Optional[FrameLinkContract] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Internal

        Initialize one placeholder frame link.

        Args:
            frame_name:
                Source frame name.
            source_kind:
                Kind name for the source object (`spell`, `conduit`, etc.).
            source_id:
                Stable source identifier.
            display_name:
                Optional viewer-facing display name.
            contract:
                Optional frame-link contract.
            metadata:
                Optional free-form metadata.

        Returns:
            None.
        """
        super().__init__()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        if not source_kind:
            raise ValueError("source_kind cannot be empty.")
        if not source_id:
            raise ValueError("source_id cannot be empty.")
        if contract is not None and not isinstance(contract, FrameLinkContract):
            raise TypeError("contract must be a FrameLinkContract when provided.")
        self._link_id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._frame_name: str = frame_name
        self._source_kind: str = source_kind
        self._source_id: str = source_id
        self._display_name: str = display_name or source_id
        self._contract: Optional[FrameLinkContract] = contract
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}

    def cleanup(self) -> None:
        """
        Internal

        Idempotently clear link-owned state.

        Threading:
            Uses the instance lock because cleanup clears grouped state in one
            pass in a nogil runtime.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if self._contract is not None:
                try:
                    self._contract.cleanup()
                except Exception:
                    pass
            self._frame_name = None
            self._source_kind = None
            self._source_id = None
            self._display_name = None
            self._contract = None
            self._metadata.clear()
            self._metadata = None
            self._link_id = None
        self._lock = None

    @classmethod
    def from_contract_subject(
            cls,
            *,
            frame_name: str,
            source_kind: str,
            source_id: str,
            contract: FrameLinkContract,
            display_name: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> "FrameLink":
        """
        Internal

        Build one `FrameLink` from an already-derived frame-link contract and
        one view-safe subject identity.

        Purpose:
            Give `FrameView` a narrow construction path that does not expose
            raw runtime objects and that guarantees each link owns a detached
            contract instance.

        Args:
            frame_name:
                Source frame name.
            source_kind:
                Kind label such as `frame`, `conduit`, or `spell`.
            source_id:
                Stable source identifier for the link target.
            contract:
                Effective frame-link contract to attach to the link.
            display_name:
                Optional viewer-facing display name.
            metadata:
                Optional derived view metadata.

        Returns:
            FrameLink: New view-safe frame link.
        """
        if not isinstance(contract, FrameLinkContract):
            raise TypeError("contract must be a FrameLinkContract.")
        return cls(
            frame_name=frame_name,
            source_kind=source_kind,
            source_id=source_id,
            display_name=display_name,
            contract=contract.clone(),
            metadata=metadata,
        )

    @property
    def link_id(self) -> str:
        """Return the canonical link id."""
        self.check_cleaned()
        return self._link_id

    @property
    def frame_name(self) -> str:
        """Return the source frame name."""
        self.check_cleaned()
        return self._frame_name

    @property
    def source_kind(self) -> str:
        """Return the source kind."""
        self.check_cleaned()
        return self._source_kind

    @property
    def source_id(self) -> str:
        """Return the source identifier."""
        self.check_cleaned()
        return self._source_id

    @property
    def display_name(self) -> str:
        """Return the viewer-facing display name."""
        self.check_cleaned()
        return self._display_name

    @property
    def contract(self) -> Optional[FrameLinkContract]:
        """Return the associated contract, if present."""
        self.check_cleaned()
        return self._contract

    @property
    def metadata(self) -> Dict[str, object]:
        """Return the link metadata map."""
        self.check_cleaned()
        return dict(self._metadata)

    def clone(self) -> "FrameLink":
        """
        Internal

        Return a detached copy of the link.

        Purpose:
            Support safe cached projection returns where the cache keeps one
            canonical link object but callers receive their own cleanup-safe
            copy.

        Returns:
            FrameLink: Detached link copy.
        """
        self.check_cleaned()
        return FrameLink(
            frame_name=self._frame_name,
            source_kind=self._source_kind,
            source_id=self._source_id,
            display_name=self._display_name,
            contract=(self._contract.clone() if self._contract is not None else None),
            metadata=dict(self._metadata),
        )
