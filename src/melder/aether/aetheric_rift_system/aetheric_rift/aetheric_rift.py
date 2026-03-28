from typing import Dict, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.interfaces import (
    IAethericRift,
    IAethericRiftState,
    IAethericRiftSystem,
    IRiftSpace,
)


class AethericRift(Cleanable, IAethericRift):
    """
    Internal

    Public AR shell/runtime object bound to one canonical Rift state.

    Purpose:
        Represent the public per-Rift runtime shell that binds against one
        canonical `AethericRiftState` and owns the room registry for that Rift.

    Contract:
        - Owns room/space registries local to this Rift.
        - Points at one canonical state id rather than owning canonical state.
        - Keeps fast id -> room and name -> id indexing for spaces.
        - Does not yet implement full validation/profile/history behavior.

    Lifecycle:
        Registered into `AethericRiftSystem`. Cleanup clears room registries and
        detaches the shell from the hosted system/state.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_rift_name",
        "_system",
        "_state",
        "_spaces_by_id",
        "_space_ids_by_name",
        "_active_space_id",
    ]

    def __init__(
            self,
            system: IAethericRiftSystem,
            *,
            rift_name: Optional[str] = None,
            rift_id: Optional[str] = None,
    ) -> None:
        """
        Internal

        Initialize the public Rift shell.

        Args:
            system:
                Hosting AR subsystem root.
            rift_name:
                Optional stable Rift name.
            rift_id:
                Optional explicit Rift id. When omitted a new id is created.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = rift_id or IDBuilder.create_id()
        self._rift_name: Optional[str] = rift_name
        self._system: IAethericRiftSystem = system
        self._state: Optional[IAethericRiftState] = None
        self._spaces_by_id: Dict[str, IRiftSpace] = {}
        self._space_ids_by_name: Dict[str, str] = {}
        self._active_space_id: Optional[str] = None

    def cleanup(self) -> None:
        """
        Internal

        Idempotently cleanup room registries and references.

        Contract:
            - Clears room registries without touching canonical state ownership
              outside the shell.
            - Detaches the shell from its hosted system and bound state.
            - Leaves the shell unusable after cleanup.

        Returns:
            None.
        """
        if self._cleaned:
            return

        self._cleaned = True
        self._spaces_by_id.clear()
        self._space_ids_by_name.clear()

        self._spaces_by_id = None
        self._space_ids_by_name = None
        self._active_space_id = None
        self._system = None
        self._state = None
        self._rift_name = None
        self._id = None

    @property
    def id(self) -> str:
        """
        Purpose:
            Return the canonical Rift id for this shell.

        Returns:
            str: The Rift id.
        """
        self.check_cleaned()
        return self._id

    @property
    def rift_name(self) -> Optional[str]:
        """
        Purpose:
            Return the stable optional Rift name.

        Returns:
            Optional[str]: The Rift name, if one is assigned.
        """
        self.check_cleaned()
        return self._rift_name

    @property
    def rift_state_id(self) -> str:
        """
        Purpose:
            Return the canonical state id bound to this Rift shell.

        Returns:
            str: The canonical RiftState id.

        Raises:
            RuntimeError: If no canonical state is currently bound.
        """
        return self.state.rift_id

    @property
    def active_space_id(self) -> Optional[str]:
        """
        Purpose:
            Return the currently active space id for this Rift.

        Returns:
            Optional[str]: Active space id when one has been selected.
        """
        self._require_live_state()
        return self._active_space_id

    @property
    def has_state(self) -> bool:
        """
        Purpose:
            Return whether this Rift shell currently has canonical state bound.

        Returns:
            bool: True when a state object is bound.
        """
        self.check_cleaned()
        return self._state is not None

    @property
    def state(self) -> IAethericRiftState:
        """
        Purpose:
            Return the canonical state bound to this Rift shell.

        Returns:
            IAethericRiftState: The bound canonical state.

        Raises:
            RuntimeError: If the Rift has not been programmed with state yet.
        """
        self.check_cleaned()
        if self._state is None:
            raise RuntimeError("AethericRift has not been programmed with state.")
        return self._state

    def bind_state(self, state: IAethericRiftState) -> None:
        """
        Internal

        Bind canonical state into this Rift shell.

        Args:
            state:
                Canonical state owned by `AethericRiftSystem`.

        Returns:
            None.

        Raises:
            ValueError:
                If the state belongs to a different Rift.

        Contract:
            Binds canonical state into the shell but does not itself register
            the shell into ARS.
        """
        self.check_cleaned()
        if state.rift_id != self._id:
            raise ValueError("state.rift_id must match this Rift id.")
        self._state = state

    def register_space(self, space: IRiftSpace) -> None:
        """
        Internal

        Register one `RiftSpace` under this Rift.

        Args:
            space:
                The room object to register.

        Returns:
            None.

        Raises:
            ValueError:
                If the room is owned by a different Rift, or if the room id/name
                collides with an existing registration.
            RuntimeError:
                If this Rift shell has not yet been programmed with state.

        Contract:
            - Requires the shell to be live.
            - Maintains both id -> room and name -> id indexes.
            - Sets the first registered room as active when no active room has
              been selected yet.
        """
        self._require_live_state()
        if space.owner_rift_id != self._id:
            raise ValueError("space.owner_rift_id must match the owning Rift id.")

        if space.space_id in self._spaces_by_id:
            raise ValueError(f"Space with id '{space.space_id}' already exists.")
        self._spaces_by_id[space.space_id] = space
        if space.space_name:
            if space.space_name in self._space_ids_by_name:
                raise ValueError(f"Space name '{space.space_name}' already exists.")
            self._space_ids_by_name[space.space_name] = space.space_id
        if self._active_space_id is None:
            self._active_space_id = space.space_id
            self._state._active_space_id = space.space_id

    def get_space(self, space_id: str) -> IRiftSpace:
        """
        Internal

        Purpose:
            Return one registered space by id.

        Args:
            space_id:
                Canonical room id.

        Returns:
            IRiftSpace: The registered room.

        Raises:
            RuntimeError: If this Rift shell has not yet been programmed with state.
            ValueError: If no room is registered for that id.
        """
        self._require_live_state()
        try:
            return self._spaces_by_id[space_id]
        except KeyError as exc:
            raise ValueError(f"Space with id '{space_id}' was not found.") from exc

    def get_space_by_name(self, space_name: str) -> IRiftSpace:
        """
        Internal

        Purpose:
            Resolve one registered space through the paired name -> id index.

        Args:
            space_name:
                Stable room name.

        Returns:
            IRiftSpace: The registered room.

        Raises:
            RuntimeError: If this Rift shell has not yet been programmed with state.
            ValueError: If no room is registered for that name.
        """
        self._require_live_state()
        try:
            space_id = self._space_ids_by_name[space_name]
        except KeyError as exc:
            raise ValueError(f"Space with name '{space_name}' was not found.") from exc

        return self.get_space(space_id)

    def set_active_space(self, space_id: str) -> None:
        """
        Internal

        Purpose:
            Set the active space by canonical id.

        Args:
            space_id:
                Canonical room id.

        Returns:
            None.

        Raises:
            RuntimeError: If this Rift shell has not yet been programmed with state.
            ValueError: If the requested room id is not registered.

        Contract:
            Updates both the shell's active room pointer and the canonical state
            active room id.
        """
        self._require_live_state()
        self.get_space(space_id)
        self._active_space_id = space_id
        self._state._active_space_id = space_id

    def list_space_ids(self) -> list[str]:
        """
        Internal

        Purpose:
            Return the current registered space ids.

        Returns:
            list[str]: Snapshot of current room ids.
        """
        self._require_live_state()
        return list(self._spaces_by_id.keys())

    def _require_live_state(self) -> None:
        """
        Internal

        Require that this Rift shell has been programmed with canonical state.

        Returns:
            None.

        Raises:
            RuntimeError: If no canonical state is currently bound.

        Contract:
            Treats the shell as inert until canonical state is bound.
        """
        self.check_cleaned()
        if self._state is None:
            raise RuntimeError("AethericRift shell is inert until state is bound.")
