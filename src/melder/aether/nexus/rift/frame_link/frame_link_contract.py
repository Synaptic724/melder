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
        "_selected_contract_names_by_frame_name",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            rift_id: str,
            assigned_frame_names: Optional[Sequence[str]] = None,
            default_frame_name: Optional[str] = None,
            selected_contract_names_by_frame_name: Optional[Dict[str, Dict[str, str]]] = None,
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
            selected_contract_names_by_frame_name:
                Optional mapping of frame name to selected ACL contract names
                keyed by `view`, `command`, and `codegen`.
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
        normalized_selected_contract_names_by_frame_name: Dict[str, Dict[str, str]] = {}
        for frame_name in normalized_assigned_frame_names:
            normalized_selected_contract_names_by_frame_name[frame_name] = {
                "view": "default",
                "command": "default",
                "codegen": "default",
            }
        if selected_contract_names_by_frame_name is not None:
            if not isinstance(selected_contract_names_by_frame_name, dict):
                raise TypeError(
                    "selected_contract_names_by_frame_name must be a dict when provided."
                )
            for frame_name, contract_selection in (
                    selected_contract_names_by_frame_name.items()
            ):
                if frame_name not in normalized_assigned_frame_names:
                    raise ValueError(
                        "selected contract frame '{0}' must be present in assigned_frame_names.".format(
                            frame_name
                        )
                    )
                normalized_selected_contract_names_by_frame_name[frame_name] = (
                    self._normalize_contract_selection_input(contract_selection)
                )
        self._contract_id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._rift_id: str = rift_id
        self._assigned_frame_names: Tuple[str, ...] = tuple(normalized_assigned_frame_names)
        self._default_frame_name: Optional[str] = default_frame_name
        self._selected_contract_names_by_frame_name: Dict[str, Dict[str, str]] = (
            normalized_selected_contract_names_by_frame_name
        )
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}

    @property
    def contract_id(self) -> str:
        """Return the canonical contract id for this Rift-local frame contract."""
        self.check_cleaned()
        return self._contract_id

    @property
    def rift_id(self) -> str:
        """Return the owning Rift id for this contract."""
        self.check_cleaned()
        return self._rift_id

    @property
    def assigned_frame_names(self) -> Tuple[str, ...]:
        """Return the currently assigned/available frame names as a stable tuple."""
        self.check_cleaned()
        return self._assigned_frame_names

    @property
    def default_frame_name(self) -> Optional[str]:
        """Return the default assigned frame name when one exists."""
        self.check_cleaned()
        return self._default_frame_name

    @property
    def metadata(self) -> Dict[str, object]:
        """Return a detached copy of the contract metadata map."""
        self.check_cleaned()
        return dict(self._metadata)

    @property
    def selected_contract_names_by_frame_name(self) -> Dict[str, Dict[str, str]]:
        """
        Return a detached snapshot of selected contract names by frame.

        Returns:
            Dict[str, Dict[str, str]]:
                Frame-name keyed selected contract names for view, command,
                and codegen.
        """
        self.check_cleaned()
        with self._lock:
            return {
                frame_name: dict(contract_selection)
                for frame_name, contract_selection in (
                    self._selected_contract_names_by_frame_name.items()
                )
            }

    def list_frame_names(self) -> List[str]:
        """
        Return the currently assigned frame names.

        Contract:
            Returns a snapshot list built from the current assigned-frame
            tuple.

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
            contract_name: str = "default",
            view_contract_name: Optional[str] = None,
            command_contract_name: Optional[str] = None,
            codegen_contract_name: Optional[str] = None,
    ) -> None:
        """
        Register one assigned frame on this contract.

        Args:
            frame_name:
                Frame name to assign.
            set_as_default:
                When True, the frame also becomes the default assigned frame.
            contract_name:
                Same-name ACL contract convenience selector.
            view_contract_name:
                Optional explicit selected view ACL contract name.
            command_contract_name:
                Optional explicit selected command ACL contract name.
            codegen_contract_name:
                Optional explicit selected codegen ACL contract name.

        Contract:
            - Deduplicates assigned frame names.
            - Sets the default frame when explicitly requested or when no
              default frame currently exists.
            - Records the selected contract names for the frame.

        Returns:
            None.
        """
        self.check_cleaned()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        normalized_contract_selection = self._normalize_contract_selection(
            contract_name,
            view_contract_name=view_contract_name,
            command_contract_name=command_contract_name,
            codegen_contract_name=codegen_contract_name,
        )
        with self._lock:
            if frame_name not in self._assigned_frame_names:
                self._assigned_frame_names = self._assigned_frame_names + (frame_name,)
            self._selected_contract_names_by_frame_name[frame_name] = (
                normalized_contract_selection
            )
            if set_as_default or self._default_frame_name is None:
                self._default_frame_name = frame_name

    def get_selected_contract_names(self, frame_name: str) -> Dict[str, str]:
        """
        Return the selected ACL contract names for one assigned frame.

        Args:
            frame_name:
                Assigned frame name whose selected contracts should be returned.

        Returns:
            Dict[str, str]: Selected view/command/codegen contract names.
        """
        self.check_cleaned()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        with self._lock:
            try:
                return dict(self._selected_contract_names_by_frame_name[frame_name])
            except KeyError as exc:
                raise KeyError(
                    "Frame '{0}' is not assigned on this Rift contract.".format(
                        frame_name
                    )
                ) from exc

    def get_selected_contract_name(self, frame_name: str) -> str:
        """
        Return the selected view ACL contract name for one assigned frame.

        Args:
            frame_name:
                Assigned frame name whose selected contract should be returned.

        Returns:
            str:
                Selected view ACL contract name for the frame.

        Raises:
            ValueError:
                If `frame_name` is empty.
            KeyError:
                If the frame is not assigned.
        """
        self.check_cleaned()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        with self._lock:
            try:
                return self._selected_contract_names_by_frame_name[frame_name]["view"]
            except KeyError as exc:
                raise KeyError(
                    "Frame '{0}' is not assigned on this Rift contract.".format(
                        frame_name
                    )
                ) from exc

    def set_selected_contract_name(
            self,
            frame_name: str,
            contract_name: str,
    ) -> None:
        """
        Update the selected ACL contract names for one assigned frame to the
        same-name convenience selection.

        Args:
            frame_name:
                Assigned frame name to update.
            contract_name:
                Selected ACL contract name for all three families.

        Returns:
            None.
        """
        self.check_cleaned()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        normalized_contract_selection = self._normalize_contract_selection(
            contract_name,
        )
        with self._lock:
            if frame_name not in self._assigned_frame_names:
                raise KeyError(
                    "Frame '{0}' is not assigned on this Rift contract.".format(
                        frame_name
                    )
                )
            self._selected_contract_names_by_frame_name[frame_name] = (
                normalized_contract_selection
            )

    def set_selected_contract_names(
            self,
            frame_name: str,
            *,
            contract_name: str = "default",
            view_contract_name: Optional[str] = None,
            command_contract_name: Optional[str] = None,
            codegen_contract_name: Optional[str] = None,
    ) -> None:
        """
        Update the selected ACL contract names for one assigned frame.

        Args:
            frame_name:
                Assigned frame name to update.
            contract_name:
                Same-name ACL contract convenience selector.
            view_contract_name:
                Optional explicit selected view ACL contract name.
            command_contract_name:
                Optional explicit selected command ACL contract name.
            codegen_contract_name:
                Optional explicit selected codegen ACL contract name.

        Returns:
            None.
        """
        self.check_cleaned()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        normalized_contract_selection = self._normalize_contract_selection(
            contract_name,
            view_contract_name=view_contract_name,
            command_contract_name=command_contract_name,
            codegen_contract_name=codegen_contract_name,
        )
        with self._lock:
            if frame_name not in self._assigned_frame_names:
                raise KeyError(
                    "Frame '{0}' is not assigned on this Rift contract.".format(
                        frame_name
                    )
                )
            self._selected_contract_names_by_frame_name[frame_name] = (
                normalized_contract_selection
            )

    def remove_frame(self, frame_name: str) -> None:
        """
        Remove one assigned frame from this contract.

        Args:
            frame_name:
                Frame name to remove.

        Contract:
            - Returns quietly when the frame is not assigned.
            - Recomputes the default frame when the removed frame was the
              current default.

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
            self._selected_contract_names_by_frame_name.pop(frame_name, None)
            if self._default_frame_name == frame_name:
                self._default_frame_name = (
                    self._assigned_frame_names[0]
                    if len(self._assigned_frame_names) > 0
                    else None
                )

    def describe(self) -> Dict[str, object]:
        """
        Return one detached summary of the Rift frame availability contract.

        Contract:
            Returns a detached summary payload built from the current contract
            state.

        Returns:
            Dict[str, object]: Detached contract summary.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "rift_id": self._rift_id,
                "assigned_frame_names": self._assigned_frame_names,
                "default_frame_name": self._default_frame_name,
                "selected_contract_names_by_frame_name": dict(
                    (
                        frame_name,
                        dict(contract_selection),
                    )
                    for frame_name, contract_selection in (
                        self._selected_contract_names_by_frame_name.items()
                    )
                ),
                "assigned_frame_count": len(self._assigned_frame_names),
            }

    def cleanup(self) -> None:
        """
        Idempotently clear contract-owned state.

        Contract:
            - Clears assigned-frame and metadata state.
            - Leaves the contract unusable after cleanup.

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
            self._selected_contract_names_by_frame_name.clear()
            self._selected_contract_names_by_frame_name = None
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
            selected_contract_names_by_frame_name=dict(
                (
                    frame_name,
                    dict(contract_selection),
                )
                for frame_name, contract_selection in (
                    self._selected_contract_names_by_frame_name.items()
                )
            ),
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

    @classmethod
    def _normalize_contract_selection_input(
            cls,
            contract_selection: object,
    ) -> Dict[str, str]:
        """
        Normalize one stored or incoming contract-selection value.

        Args:
            contract_selection:
                Either one same-name contract string or a dict keyed by family.

        Returns:
            Dict[str, str]: Normalized family selection map.
        """
        if isinstance(contract_selection, str):
            return cls._normalize_contract_selection(contract_selection)
        if not isinstance(contract_selection, dict):
            raise ValueError(
                "selected contract names must be provided as a string or dict."
            )
        return cls._normalize_contract_selection(
            contract_selection.get("contract_name"),
            view_contract_name=contract_selection.get("view"),
            command_contract_name=contract_selection.get("command"),
            codegen_contract_name=contract_selection.get("codegen"),
        )
