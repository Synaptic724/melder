"""
Internal FrameLinkContract object.

Purpose:
    Represent one frame-local contract entry for one live Rift.
"""

import threading
from typing import Dict, Optional

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

    Threading:
        `_lock` serializes `cleanup()` against itself and against the
        lock-guarded reads (`get_selected_contract_names`,
        `get_selected_contract_name`, `describe`, `clone`). Each checks
        `_cleaned`, takes `_lock`, then checks again under it - Cleanable's
        double-check - so a second concurrent `cleanup()` returns and a read
        overtaken by a cleanup raises the cleaned `RuntimeError`. `cleanup()`
        keeps `_lock` so both can still take it. The property reads
        (`contract_id`, `rift_id`, `frame_name`, `metadata`) take no lock: one
        that races `cleanup()` past its check can raise `AttributeError`, and
        `metadata` can return the map cleanup has already cleared
        (GitHub #271).

    Registration:
        MELDER KERNEL - guarded. Created per Rift/frame pair during
        `Rift.create_frame_link(...)`.

    Subsystem Context:
        The per-frame ACL SELECTION for one Rift, distinct from the ACL
        containers themselves. `FrameACLManager` owns each frame's named
        revision chains for view, command, and codegen; this object records
        which contract name this Rift selected in each family for one frame.

    System Context:
        The storage layer allows the three families to hold DIVERGENT named
        contracts - same-name selection is convenience there, not law. The Rift
        frame-link path deliberately does not use that freedom: it pins a fixed
        same-name selection resolving view, command, and codegen to the attached
        `frame_name`, materializing from `default` when absent.
        That restriction is what keeps attachment predictable. Allowing a Rift
        to mix families - view from one contract, command from another - would
        make its effective permissions a cross-product no operator could reason
        about, and would make an ACL bump's blast radius depend on which
        combination each Rift happened to select.
        One contract per frame also means a Rift's total surface is the union of
        its per-frame contracts, so revoking one frame cannot silently widen or
        narrow another.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. FrameLinkContract runtime object. Melder kernel machinery: read it to
        understand the runtime, do not drive it directly.
    """

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
            - Keeps `_lock` as a documented post-cleanup tombstone: a
              concurrent `cleanup()` past its outer check, or a lock-guarded
              read, takes it after this teardown and observes `_cleaned` under
              it instead of a missing field (GitHub #271).

        Threading:
            Checks `_cleaned`, takes `_lock`, checks again under it, and sets
            `_cleaned` and deletes the state under it. Two concurrent calls
            tear the state down once and both return.

        Returns:
            None.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._cleaned = True
            self._selected_contract_names.clear()
            self._metadata.clear()

            del self._selected_contract_names
            del self._metadata
            del self._frame_name
            del self._rift_id
            del self._id
        # `_lock` is kept, a documented post-cleanup tombstone: deleting it here made a
        # concurrent cleanup() past its outer check, or a lock-guarded read past its
        # check, raise AttributeError on the missing `_lock` (GitHub #271).

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

        Threading:
            Checks `_cleaned` before and again under `_lock`, the lock
            `cleanup()` sets `_cleaned` and deletes the selection under, so the
            copy never sees a half-torn-down selection and a read overtaken by a
            concurrent cleanup raises the cleaned `RuntimeError`.

        Raises:
            RuntimeError: If the contract has been cleaned, including by a
                cleanup that finished while this read waited for `_lock`.

        Returns:
            Dict[str, str]: Selected view/command/codegen contract names.
        """
        self.check_cleaned()
        with self._lock:
            self.check_cleaned()
            return dict(self._selected_contract_names)

    def get_selected_contract_name(self) -> str:
        """
        Return the selected view ACL contract name for this frame.

        Contract:
            This same-name selection always matches the attached `frame_name`.

        Threading:
            Checks `_cleaned` before and again under `_lock`, as
            `get_selected_contract_names` does.

        Raises:
            RuntimeError: If the contract has been cleaned, including by a
                cleanup that finished while this read waited for `_lock`.

        Returns:
            str: Selected view ACL contract name.
        """
        self.check_cleaned()
        with self._lock:
            self.check_cleaned()
            return self._selected_contract_names["view"]

    def describe(self) -> Dict[str, object]:
        """
        Return one detached summary of this per-frame contract.

        Threading:
            Checks `_cleaned` before and again under `_lock`, so the summary is
            built from one consistent live state and a read overtaken by a
            concurrent cleanup raises the cleaned `RuntimeError`.

        Raises:
            RuntimeError: If the contract has been cleaned, including by a
                cleanup that finished while this read waited for `_lock`.

        Returns:
            Dict[str, object]: Detached contract summary.
        """
        self.check_cleaned()
        with self._lock:
            self.check_cleaned()
            return {
                "rift_id": self._rift_id,
                "frame_name": self._frame_name,
                "selected_contract_names": dict(self._selected_contract_names),
            }

    def clone(self) -> "FrameLinkContract":
        """
        Return a detached copy of this per-frame contract.

        Threading:
            Checks `_cleaned` before and again under `_lock`, so the copy is
            built from one consistent live state and a clone overtaken by a
            concurrent cleanup raises the cleaned `RuntimeError`.

        Raises:
            RuntimeError: If the contract has been cleaned, including by a
                cleanup that finished while this call waited for `_lock`.

        Returns:
            FrameLinkContract: Detached contract copy.
        """
        self.check_cleaned()
        with self._lock:
            self.check_cleaned()
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
