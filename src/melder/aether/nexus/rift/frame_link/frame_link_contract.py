"""
Internal FrameLinkContract object.

Purpose:
    Represent the frame-availability contract for one live Rift.
"""

import threading
from typing import Dict, List, Optional, Sequence, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameLinkContract(Cleanable):
    """
    Internal

    Purpose:
        Represent the set of frames currently assigned/available to one Rift.

    Contract:
        - Owns the Rift-local frame availability state only.
        - Does not own ACL logic, payload filtering, or viewer commands.
        - Provides the frame names that may be materialized into assigned
          views on the viewer.
        - Cleanup is idempotent and clears the owned availability state.

    Lifecycle:
        Created for a Rift and cleaned with that Rift unless explicitly cloned
        into another local hosting object.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_contract_id",
        "_lock",
        "_rift_id",
        "_assigned_frame_names",
        "_default_frame_name",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            rift_id: str,
            assigned_frame_names: Optional[Sequence[str]] = None,
            default_frame_name: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize one Rift-local frame availability contract.

        Args:
            rift_id:
                Owning Rift id.
            assigned_frame_names:
                Optional assigned/available frame names.
            default_frame_name:
                Optional default assigned frame name.
            metadata:
                Optional contract-local metadata.

        Returns:
            None.
        """
        super().__init__()
        if not rift_id:
            raise ValueError("rift_id cannot be empty.")
        normalized_assigned_frame_names: List[str] = []
        for frame_name in assigned_frame_names or tuple():
            if not isinstance(frame_name, str) or not frame_name:
                raise ValueError(
                    "assigned_frame_names must contain non-empty strings."
                )
            if frame_name in normalized_assigned_frame_names:
                continue
            normalized_assigned_frame_names.append(frame_name)
        if default_frame_name is not None:
            if not default_frame_name:
                raise ValueError("default_frame_name cannot be empty.")
            if default_frame_name not in normalized_assigned_frame_names:
                raise ValueError(
                    "default_frame_name must be present in assigned_frame_names."
                )
        self._contract_id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._rift_id: str = rift_id
        self._assigned_frame_names: Tuple[str, ...] = tuple(normalized_assigned_frame_names)
        self._default_frame_name: Optional[str] = default_frame_name
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}

    @property
    def contract_id(self) -> str:
        """Return the canonical contract id."""
        self.check_cleaned()
        return self._contract_id

    @property
    def rift_id(self) -> str:
        """Return the owning Rift id."""
        self.check_cleaned()
        return self._rift_id

    @property
    def assigned_frame_names(self) -> Tuple[str, ...]:
        """Return the currently assigned/available frame names."""
        self.check_cleaned()
        return self._assigned_frame_names

    @property
    def default_frame_name(self) -> Optional[str]:
        """Return the default assigned frame name when one exists."""
        self.check_cleaned()
        return self._default_frame_name

    @property
    def metadata(self) -> Dict[str, object]:
        """Return the contract metadata map."""
        self.check_cleaned()
        return dict(self._metadata)

    def list_frame_names(self) -> List[str]:
        """
        Return the currently assigned frame names.

        Returns:
            List[str]: Assigned frame names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._assigned_frame_names)

    def has_frame(self, frame_name: str) -> bool:
        """
        Return whether one frame is assigned to this Rift.

        Args:
            frame_name:
                Frame name to inspect.

        Returns:
            bool: True when the frame is assigned.
        """
        self.check_cleaned()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        with self._lock:
            return frame_name in self._assigned_frame_names

    def register_frame(
            self,
            frame_name: str,
            *,
            set_as_default: bool = False,
    ) -> None:
        """
        Register one assigned frame on this contract.

        Args:
            frame_name:
                Frame name to assign.
            set_as_default:
                When True, the frame also becomes the default assigned frame.

        Returns:
            None.
        """
        self.check_cleaned()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        with self._lock:
            if frame_name not in self._assigned_frame_names:
                self._assigned_frame_names = self._assigned_frame_names + (frame_name,)
            if set_as_default or self._default_frame_name is None:
                self._default_frame_name = frame_name

    def remove_frame(self, frame_name: str) -> None:
        """
        Remove one assigned frame from this contract.

        Args:
            frame_name:
                Frame name to remove.

        Returns:
            None.
        """
        self.check_cleaned()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        with self._lock:
            if frame_name not in self._assigned_frame_names:
                return
            self._assigned_frame_names = tuple(
                assigned_frame_name
                for assigned_frame_name in self._assigned_frame_names
                if assigned_frame_name != frame_name
            )
            if self._default_frame_name == frame_name:
                self._default_frame_name = (
                    self._assigned_frame_names[0]
                    if len(self._assigned_frame_names) > 0
                    else None
                )

    def describe(self) -> Dict[str, object]:
        """
        Return one detached summary of the Rift frame availability contract.

        Returns:
            Dict[str, object]: Detached contract summary.
        """
        self.check_cleaned()
        return {
            "rift_id": self._rift_id,
            "assigned_frame_names": self._assigned_frame_names,
            "default_frame_name": self._default_frame_name,
            "assigned_frame_count": len(self._assigned_frame_names),
        }

    def cleanup(self) -> None:
        """
        Idempotently clear contract-owned state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._assigned_frame_names = None
            self._default_frame_name = None
            self._metadata.clear()
            self._metadata = None
            self._rift_id = None
            self._contract_id = None
        self._lock = None

    def clone(self) -> "FrameLinkContract":
        """
        Return a detached copy of this frame availability contract.

        Returns:
            FrameLinkContract: Detached contract copy.
        """
        self.check_cleaned()
        return FrameLinkContract(
            rift_id=self._rift_id,
            assigned_frame_names=self._assigned_frame_names,
            default_frame_name=self._default_frame_name,
            metadata=dict(self._metadata),
        )
