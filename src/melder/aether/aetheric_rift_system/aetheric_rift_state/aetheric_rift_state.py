from typing import Dict, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.interfaces import IAethericRiftConfiguration, IAethericRiftState


class AethericRiftState(Cleanable, IAethericRiftState):
    """
    Internal

    Canonical state record for one Rift instance.

    Purpose:
        Store canonical Rift-level truth separate from the public Rift shell.

    Contract:
        - Owns the canonical per-Rift configuration object.
        - Carries the internal AR system-frame anchor and the configured target
          frame name for the Rift.
        - Stores stable Rift-level state such as active space and local conduit
          identity.
        - Does not become the room history/action system in this slice.

    Lifecycle:
        Owned by `AethericRiftSystem`. Cleanup clears canonical Rift fields,
        metadata, and the owned per-Rift configuration object.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_rift_name",
        "_configuration",
        "_system_frame_name",
        "_target_frame_name",
        "_mode",
        "_local_conduit_id",
        "_active_space_id",
        "_is_registered",
        "_is_active",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            configuration: IAethericRiftConfiguration,
            system_frame_name: str,
            rift_id: Optional[str] = None,
            rift_name: Optional[str] = None,
            local_conduit_id: Optional[str] = None,
            active_space_id: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Internal

        Initialize canonical state for one Rift.

        Args:
            configuration:
                Canonical per-Rift configuration already finalized by the
                hosting AR system.
            system_frame_name:
                Internal AR system frame anchor name for this Rift.
            rift_id:
                Optional explicit Rift id. When omitted a new id is created.
            rift_name:
                Optional stable Rift name.
            local_conduit_id:
                Optional local conduit id owned or referenced by this Rift.
            active_space_id:
                Optional currently active room id.
            metadata:
                Extensible Rift-level metadata.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = rift_id or IDBuilder.create_id()
        self._rift_name: Optional[str] = rift_name
        self._configuration: IAethericRiftConfiguration = configuration
        self._system_frame_name: str = system_frame_name
        self._target_frame_name: str = configuration.get_property("target_frame_name")
        self._mode: str = configuration.get_property("space_type").value
        self._local_conduit_id: Optional[str] = local_conduit_id
        self._active_space_id: Optional[str] = active_space_id
        self._is_registered: bool = False
        self._is_active: bool = False
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}

    def cleanup(self) -> None:
        """
        Internal

        Idempotently cleanup the canonical state container.

        Returns:
            None.
        """
        if self._cleaned:
            return

        self._cleaned = True
        self._configuration.cleanup()
        self._configuration = None
        self._rift_name = None
        self._system_frame_name = None
        self._target_frame_name = None
        self._mode = None
        self._local_conduit_id = None
        self._active_space_id = None
        self._is_registered = None
        self._is_active = None
        self._metadata.clear()
        self._metadata = None
        self._id = None

    @property
    def rift_id(self) -> str:
        """
        Purpose:
            Return the canonical Rift id.

        Returns:
            str: The Rift id.
        """
        self.check_cleaned()
        return self._id

    @property
    def rift_name(self) -> Optional[str]:
        """
        Purpose:
            Return the optional stable Rift name.

        Returns:
            Optional[str]: The Rift name, if one exists.
        """
        self.check_cleaned()
        return self._rift_name

    @property
    def configuration(self) -> IAethericRiftConfiguration:
        """
        Purpose:
            Return the canonical per-Rift configuration.

        Returns:
            IAethericRiftConfiguration: The owned per-Rift configuration object.
        """
        self.check_cleaned()
        return self._configuration

    @property
    def system_frame_name(self) -> str:
        """
        Purpose:
            Return the internal AR system frame anchor name for this Rift.

        Returns:
            str: Internal AR system frame name.
        """
        self.check_cleaned()
        return self._system_frame_name

    @property
    def target_frame_name(self) -> str:
        """
        Purpose:
            Return the target frame name bound to this Rift.

        Returns:
            str: The target `AethericFrame` name.
        """
        self.check_cleaned()
        return self._target_frame_name

    @property
    def mode(self) -> str:
        """
        Purpose:
            Return the current mode label for this Rift.

        Returns:
            str: The current mode string.
        """
        self.check_cleaned()
        return self._mode

    @property
    def local_conduit_id(self) -> Optional[str]:
        """
        Purpose:
            Return the optional local conduit id attached to this Rift.

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
            Optional[str]: Active room id, if one is set.
        """
        self.check_cleaned()
        return self._active_space_id

    @property
    def is_registered(self) -> bool:
        """
        Purpose:
            Return whether this canonical Rift state has been registered.

        Returns:
            bool: True when registered into the AR system.
        """
        self.check_cleaned()
        return self._is_registered

    @property
    def is_active(self) -> bool:
        """
        Purpose:
            Return whether this canonical Rift state is currently active/live.

        Returns:
            bool: True when active.
        """
        self.check_cleaned()
        return self._is_active

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Purpose:
            Return the canonical metadata map for this Rift state.

        Returns:
            Dict[str, object]: Extensible Rift-level metadata.
        """
        self.check_cleaned()
        return self._metadata

    def mark_registered(self) -> None:
        """
        Internal

        Mark this canonical Rift state as registered.

        Returns:
            None.
        """
        self.check_cleaned()
        self._is_registered = True

    def mark_active(self) -> None:
        """
        Internal

        Mark this canonical Rift state as active/live.

        Returns:
            None.
        """
        self.check_cleaned()
        self._is_active = True

    def mark_inactive(self) -> None:
        """
        Internal

        Mark this canonical Rift state as inactive.

        Returns:
            None.
        """
        self.check_cleaned()
        self._is_active = False
