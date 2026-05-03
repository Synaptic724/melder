"""
Internal FrameLinkContract object.

Purpose:
    Represent one frame-local contract entry for one live Rift.
"""

import threading
from typing import Dict, Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameLinkContract(Cleanable):
    """
    Internal

    Purpose:
        Represent the selected ACL contract names for one frame attached to one
        Rift.

    Contract:
        - Owns exactly one frame name.
        - Owns exactly one selected contract-name set for `view`, `command`,
          and `codegen`, and that same-name selection always matches the
          attached frame name.
        - Does not own aggregate frame membership or default-frame selection.
        - Cleanup is idempotent and clears the owned per-frame contract state.

    Lifecycle:
        Created for one Rift/frame pair and cleaned with the owning Rift unless
        explicitly cloned into another local hosting object.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_rift_id",
        "_frame_name",
        "_selected_contract_names",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            rift_id: str,
            frame_name: str,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize one Rift-local per-frame contract.

        Args:
            rift_id:
                Owning Rift id.
            frame_name:
                Attached frame name for this contract.
            metadata:
                Optional contract-local metadata.

        Returns:
            None.
        """
        super().__init__()
        if not rift_id:
            raise ValueError("rift_id cannot be empty.")
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._rift_id: str = rift_id
        self._frame_name: str = frame_name
        self._selected_contract_names: Dict[str, str] = (
            self._build_selected_contract_names(frame_name)
        )
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}

    def cleanup(self) -> None:
        """
        Idempotently clear contract-owned state.

        Contract:
            - Clears selected-contract and metadata state.
            - Leaves the contract unusable after cleanup.

        Returns:
            None.
        """
        if self._cleaned:
            return
        lock = self._lock
        with lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._selected_contract_names.clear()
            self._selected_contract_names = None
            self._metadata.clear()
            self._metadata = None
            self._frame_name = None
            self._rift_id = None
            self._id = None
        self._lock = None

    @property
    def contract_id(self) -> str:
        """Return the canonical contract id for this Rift-local frame contract."""
        self.check_cleaned()
        return self._id

    @property
    def rift_id(self) -> str:
        """Return the owning Rift id for this contract."""
        self.check_cleaned()
        return self._rift_id

    @property
    def frame_name(self) -> str:
        """Return the attached frame name for this contract."""
        self.check_cleaned()
        return self._frame_name

    @property
    def metadata(self) -> Dict[str, object]:
        """Return a detached copy of the contract metadata map."""
        self.check_cleaned()
        return dict(self._metadata)

    def get_selected_contract_names(self) -> Dict[str, str]:
        """
        Return the selected ACL contract names for this frame.

        Returns:
            Dict[str, str]: Selected view/command/codegen contract names.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._selected_contract_names)

    def get_selected_contract_name(self) -> str:
        """
        Return the selected view ACL contract name for this frame.

        Contract:
            This same-name selection always matches the attached `frame_name`.

        Returns:
            str: Selected view ACL contract name.
        """
        self.check_cleaned()
        with self._lock:
            return self._selected_contract_names["view"]

    def describe(self) -> Dict[str, object]:
        """
        Return one detached summary of this per-frame contract.

        Returns:
            Dict[str, object]: Detached contract summary.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "rift_id": self._rift_id,
                "frame_name": self._frame_name,
                "selected_contract_names": dict(self._selected_contract_names),
            }

    def clone(self) -> "FrameLinkContract":
        """
        Return a detached copy of this per-frame contract.

        Returns:
            FrameLinkContract: Detached contract copy.
        """
        self.check_cleaned()
        with self._lock:
            return FrameLinkContract(
                rift_id=self._rift_id,
                frame_name=self._frame_name,
                metadata=dict(self._metadata),
            )

    @staticmethod
    def _build_selected_contract_names(frame_name: str) -> Dict[str, str]:
        """
        Build the fixed same-name ACL contract selection for one frame.

        Args:
            frame_name:
                Attached frame name whose same-name ACL contract should be used
                across all three families.

        Returns:
            Dict[str, str]: Fixed family selection map for the frame.
        """
        if not isinstance(frame_name, str) or not frame_name:
            raise ValueError("frame_name must be a non-empty string.")
        return {
            "view": frame_name,
            "command": frame_name,
            "codegen": frame_name,
        }
