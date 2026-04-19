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
          and `codegen`.
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
            contract_name: str = "default",
            view_contract_name: Optional[str] = None,
            command_contract_name: Optional[str] = None,
            codegen_contract_name: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize one Rift-local per-frame contract.

        Args:
            rift_id:
                Owning Rift id.
            frame_name:
                Attached frame name for this contract.
            contract_name:
                Same-name ACL contract convenience selector.
            view_contract_name:
                Optional explicit selected view contract name.
            command_contract_name:
                Optional explicit selected command contract name.
            codegen_contract_name:
                Optional explicit selected codegen contract name.
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
            self._normalize_contract_selection(
                contract_name,
                view_contract_name=view_contract_name,
                command_contract_name=command_contract_name,
                codegen_contract_name=codegen_contract_name,
            )
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

        Returns:
            str: Selected view ACL contract name.
        """
        self.check_cleaned()
        with self._lock:
            return self._selected_contract_names["view"]

    def set_selected_contract_name(self, contract_name: str) -> None:
        """
        Update the selected ACL contract names for this frame to the same-name
        convenience selection.

        Args:
            contract_name:
                Selected ACL contract name for all three families.

        Returns:
            None.
        """
        self.check_cleaned()
        normalized_contract_selection = self._normalize_contract_selection(
            contract_name,
        )
        with self._lock:
            self._selected_contract_names = normalized_contract_selection

    def set_selected_contract_names(
            self,
            *,
            contract_name: str = "default",
            view_contract_name: Optional[str] = None,
            command_contract_name: Optional[str] = None,
            codegen_contract_name: Optional[str] = None,
    ) -> None:
        """
        Update the selected ACL contract names for this frame.

        Args:
            contract_name:
                Same-name ACL contract convenience selector.
            view_contract_name:
                Optional explicit selected view contract name.
            command_contract_name:
                Optional explicit selected command contract name.
            codegen_contract_name:
                Optional explicit selected codegen contract name.

        Returns:
            None.
        """
        self.check_cleaned()
        normalized_contract_selection = self._normalize_contract_selection(
            contract_name,
            view_contract_name=view_contract_name,
            command_contract_name=command_contract_name,
            codegen_contract_name=codegen_contract_name,
        )
        with self._lock:
            self._selected_contract_names = normalized_contract_selection

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
                view_contract_name=self._selected_contract_names["view"],
                command_contract_name=self._selected_contract_names["command"],
                codegen_contract_name=self._selected_contract_names["codegen"],
                metadata=dict(self._metadata),
            )

    @staticmethod
    def _normalize_contract_selection(
            contract_name: Optional[str],
            *,
            view_contract_name: Optional[str] = None,
            command_contract_name: Optional[str] = None,
            codegen_contract_name: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Normalize one frame ACL contract selection payload.

        Args:
            contract_name:
                Same-name convenience selector applied to all families when the
                family-specific names are omitted.
            view_contract_name:
                Optional explicit selected view contract name.
            command_contract_name:
                Optional explicit selected command contract name.
            codegen_contract_name:
                Optional explicit selected codegen contract name.

        Returns:
            Dict[str, str]: Normalized family selection map.
        """
        if contract_name == "":
            raise ValueError("contract_name cannot be empty.")
        if view_contract_name == "":
            raise ValueError("view_contract_name must be a non-empty string.")
        if command_contract_name == "":
            raise ValueError("command_contract_name must be a non-empty string.")
        if codegen_contract_name == "":
            raise ValueError("codegen_contract_name must be a non-empty string.")
        base_contract_name = contract_name or "default"
        normalized_selection = {
            "view": view_contract_name or base_contract_name,
            "command": command_contract_name or base_contract_name,
            "codegen": codegen_contract_name or base_contract_name,
        }
        for family_name, selected_contract_name in normalized_selection.items():
            if not isinstance(selected_contract_name, str) or not selected_contract_name:
                raise ValueError(
                    "{0}_contract_name must be a non-empty string.".format(
                        family_name
                    )
                )
        return normalized_selection
