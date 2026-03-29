import threading
from typing import Dict, Optional, Sequence, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.aether import Aether
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.interfaces import (
    IAether,
    INexus,
    IRift,
    IRiftConfiguration,
    IRiftSpace,
)


class Rift(Cleanable, IRift):
    """
    Internal

    Live Rift runtime object created and registered by `Nexus`.

    Purpose:
        Represent one live Rift that owns its own immediate runtime state,
        frame-name assignments/defaults, and room registry without requiring a
        separate public state object.

    Contract:
        - Owns per-Rift configuration snapshot, frame-name assignments, and
          local room registry state.
        - Owns only live Rift runtime state, not global registry or Nexus-wide
          configuration.
        - Treats `Aether` as hidden substrate reached later by lower runtime
          layers such as workstation/workspace logic.

    Lifecycle:
        Created by `Nexus`, then registered into the Nexus registry. Cleanup
        clears room registries and owned live-state references.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_rift_name",
        "_lock",
        "_nexus",
        "_aether",
        "_configuration",
        "_system_frame_names",
        "_default_system_frame_name",
        "_target_frame_names",
        "_default_target_frame_name",
        "_local_conduit_id",
        "_active_space_id",
        "_is_registered",
        "_is_active",
        "_metadata",
        "_spaces_by_id",
        "_space_ids_by_name",
    ]

    def __init__(
            self,
            nexus: INexus,
            *,
            configuration: IRiftConfiguration,
            system_frame_names: Sequence[str],
            default_system_frame_name: str,
            target_frame_names: Sequence[str],
            default_target_frame_name: str,
            rift_name: Optional[str] = None,
            rift_id: Optional[str] = None,
            local_conduit_id: Optional[str] = None,
            active_space_id: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Internal

        Initialize one live Rift object.

        Args:
            nexus:
                Owning Nexus singleton.
            configuration:
                Finalized per-Rift configuration snapshot.
            system_frame_names:
                Assigned internal system-frame names for this Rift.
            default_system_frame_name:
                Default internal system-frame name for this Rift.
            target_frame_names:
                Assigned target/userland frame names for this Rift.
            default_target_frame_name:
                Default target/userland frame name for this Rift.
            rift_name:
                Optional stable Rift name.
            rift_id:
                Optional explicit Rift id.
            local_conduit_id:
                Optional live local conduit id.
            active_space_id:
                Optional active room id.
            metadata:
                Optional Rift-level metadata.

        Returns:
            None.
        """
        if nexus is None:
            raise TypeError("nexus cannot be None.")
        if not isinstance(nexus, INexus):
            raise TypeError("nexus must satisfy INexus.")
        nexus.check_cleaned()
        if not nexus.is_configured:
            raise RuntimeError("Rift requires a configured Nexus.")
        if not nexus.is_enabled:
            raise RuntimeError("Rift requires an enabled Nexus.")
        if not configuration.frozen:
            raise RuntimeError("Rift requires a finalized RiftConfiguration.")
        if not system_frame_names:
            raise ValueError("system_frame_names cannot be empty.")
        if default_system_frame_name not in system_frame_names:
            raise ValueError("default_system_frame_name must be present in system_frame_names.")
        if not target_frame_names:
            raise ValueError("target_frame_names cannot be empty.")
        if default_target_frame_name not in target_frame_names:
            raise ValueError("default_target_frame_name must be present in target_frame_names.")

        super().__init__()
        self._id: str = rift_id or IDBuilder.create_id()
        self._rift_name: Optional[str] = rift_name
        self._lock: threading.RLock = threading.RLock()
        self._nexus: INexus = nexus
        self._aether: IAether = Aether()
        self._configuration: IRiftConfiguration = configuration
        self._system_frame_names: Tuple[str, ...] = tuple(system_frame_names)
        self._default_system_frame_name: str = default_system_frame_name
        self._target_frame_names: Tuple[str, ...] = tuple(target_frame_names)
        self._default_target_frame_name: str = default_target_frame_name
        self._local_conduit_id: Optional[str] = local_conduit_id
        self._active_space_id: Optional[str] = active_space_id
        self._is_registered: bool = False
        self._is_active: bool = False
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}
        self._spaces_by_id: Dict[str, IRiftSpace] = {}
        self._space_ids_by_name: Dict[str, str] = {}

    def cleanup(self) -> None:
        """
        Internal

        Idempotently cleanup the live Rift object.

        Contract:
            - Clears room registries and live state references.
            - Does not attempt to clean Nexus or Aether-owned global state.
            - Leaves the Rift unusable after cleanup.

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
            self._spaces_by_id.clear()
            self._space_ids_by_name.clear()
            self._metadata.clear()

            self._nexus = None
            self._aether = None
            self._configuration = None
            self._system_frame_names = None
            self._default_system_frame_name = None
            self._target_frame_names = None
            self._default_target_frame_name = None
            self._local_conduit_id = None
            self._active_space_id = None
            self._is_registered = None
            self._is_active = None
            self._metadata = None
            self._spaces_by_id = None
            self._space_ids_by_name = None
            self._rift_name = None
            self._id = None
        self._lock = None

    @property
    def id(self) -> str:
        """
        Purpose:
            Return the canonical Rift id.

        Returns:
            str: Stable Rift id.
        """
        self.check_cleaned()
        return self._id

    @property
    def rift_name(self) -> Optional[str]:
        """
        Purpose:
            Return the optional stable Rift name.

        Returns:
            Optional[str]: Rift name when one is assigned.
        """
        self.check_cleaned()
        return self._rift_name

    @property
    def configuration(self) -> IRiftConfiguration:
        """
        Purpose:
            Return the finalized per-Rift configuration snapshot.

        Returns:
            IRiftConfiguration: Owned configuration snapshot.
        """
        self.check_cleaned()
        return self._configuration

    @property
    def system_frame_names(self) -> Tuple[str, ...]:
        """
        Purpose:
            Return the assigned internal system-frame names for this Rift.

        Returns:
            Tuple[str, ...]: Internal system-frame names.
        """
        self.check_cleaned()
        return self._system_frame_names

    @property
    def default_system_frame_name(self) -> str:
        """
        Purpose:
            Return the default internal system-frame name for this Rift.

        Returns:
            str: Default system-frame name.
        """
        self.check_cleaned()
        return self._default_system_frame_name

    @property
    def target_frame_names(self) -> Tuple[str, ...]:
        """
        Purpose:
            Return the assigned target/userland frame names for this Rift.

        Returns:
            Tuple[str, ...]: Target frame names.
        """
        self.check_cleaned()
        return self._target_frame_names

    @property
    def default_target_frame_name(self) -> str:
        """
        Purpose:
            Return the default target/userland frame name for this Rift.

        Returns:
            str: Default target frame name.
        """
        self.check_cleaned()
        return self._default_target_frame_name

    @property
    def local_conduit_id(self) -> Optional[str]:
        """
        Purpose:
            Return the optional live local conduit id attached to this Rift.

        Returns:
            Optional[str]: Local conduit id, if one is set.
        """
        self.check_cleaned()
        return self._local_conduit_id

    @property
    def active_space_id(self) -> Optional[str]:
        """
        Purpose:
            Return the optional active room id for this Rift.

        Returns:
            Optional[str]: Active room id when one is selected.
        """
        self.check_cleaned()
        return self._active_space_id

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Purpose:
            Return the live Rift metadata map.

        Returns:
            Dict[str, object]: Rift-level metadata.
        """
        self.check_cleaned()
        return self._metadata

    @property
    def is_registered(self) -> bool:
        """
        Purpose:
            Return whether this Rift is registered in Nexus.

        Returns:
            bool: True when registered.
        """
        self.check_cleaned()
        return self._is_registered

    @property
    def is_active(self) -> bool:
        """
        Purpose:
            Return whether this Rift is currently active.

        Returns:
            bool: True when active.
        """
        self.check_cleaned()
        return self._is_active

    def mark_registered(self) -> None:
        """
        Internal

        Mark this Rift as registered in Nexus.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._is_registered = True

    def mark_active(self) -> None:
        """
        Internal

        Mark this Rift as active.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._is_active = True

    def mark_inactive(self) -> None:
        """
        Internal

        Mark this Rift as inactive.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._is_active = False

    def register_space(self, space: IRiftSpace) -> None:
        """
        Internal

        Register one `RiftSpace` under this Rift.

        Args:
            space:
                Room object to register.

        Returns:
            None.

        Raises:
            ValueError: If the room belongs to another Rift or collides by id or name.
        """
        self.check_cleaned()
        with self._lock:
            if space.owner_rift_id != self._id:
                raise ValueError("space.owner_rift_id must match the owning Rift id.")
            if space.space_id in self._spaces_by_id:
                raise ValueError("Space with id '{0}' already exists.".format(space.space_id))

            self._spaces_by_id[space.space_id] = space
            if space.space_name:
                if space.space_name in self._space_ids_by_name:
                    raise ValueError("Space name '{0}' already exists.".format(space.space_name))
                self._space_ids_by_name[space.space_name] = space.space_id
            if self._active_space_id is None:
                self._active_space_id = space.space_id

    def get_space(self, space_id: str) -> IRiftSpace:
        """
        Internal

        Return one registered space by id.

        Args:
            space_id:
                Canonical room id.

        Returns:
            IRiftSpace: Registered room object.
        """
        self.check_cleaned()
        try:
            return self._spaces_by_id[space_id]
        except KeyError as exc:
            raise ValueError("Space with id '{0}' was not found.".format(space_id)) from exc

    def get_space_by_name(self, space_name: str) -> IRiftSpace:
        """
        Internal

        Resolve one registered space through the name -> id index.

        Args:
            space_name:
                Stable room name.

        Returns:
            IRiftSpace: Registered room object.
        """
        self.check_cleaned()
        try:
            space_id = self._space_ids_by_name[space_name]
        except KeyError as exc:
            raise ValueError("Space with name '{0}' was not found.".format(space_name)) from exc
        return self.get_space(space_id)

    def set_active_space(self, space_id: str) -> None:
        """
        Internal

        Set the active space by canonical id.

        Args:
            space_id:
                Canonical room id.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self.get_space(space_id)
            self._active_space_id = space_id

    def list_space_ids(self) -> list[str]:
        """
        Internal

        Return the current registered space ids.

        Returns:
            list[str]: Snapshot of room ids.
        """
        self.check_cleaned()
        return list(self._spaces_by_id.keys())
