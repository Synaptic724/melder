import threading
from typing import Dict, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.aetheric_frame_configuration import AethericFrameConfiguration
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.configuration.system_state import SystemState
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.utilities.helpers.id_builder import IDBuilder


class NexusFrameConfiguration(Cleanable):
    """
    Authored frame configuration for one Nexus-managed frame.

    Purpose:
        Capture the authored frame posture and optional root-conduit bootstrap
        intent for one Nexus-managed frame before the manager realizes it.

    Contract:
        - Stores only Nexus frame-authoring inputs, not live frame objects.
        - Uses the narrower frame posture fields that later compile into
          `AethericFrameConfiguration`.
        - May optionally request one root conduit bootstrap by name.
        - Is immutable-by-convention after construction.

    Lifecycle:
        Built by `NexusFrameBuilder` or direct helper constructors and consumed
        by `NexusFrameManager`.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_frame_name",
        "_system_state",
        "_ai_native_enabled",
        "_rift_enabled",
        "_immutable",
        "_metadata",
        "_root_conduit_name",
    ]

    def __init__(
            self,
            *,
            frame_name: str,
            system_state: SystemState,
            ai_native_enabled: bool,
            rift_enabled: bool,
            immutable: bool = False,
            metadata: Optional[Dict[str, object]] = None,
            root_conduit_name: Optional[str] = None,
    ) -> None:
        """
        Initialize one Nexus-managed frame authoring configuration.

        Args:
            frame_name:
                Stable frame name to author.
            system_state:
                Runtime posture for the authored frame.
            ai_native_enabled:
                Whether AI-native posture should be enabled.
            rift_enabled:
                Whether the frame should be Rift-visible.
            immutable:
                Whether the frame should reject normal removal.
            metadata:
                Optional authored metadata payload.
            root_conduit_name:
                Optional root conduit name to bootstrap after frame init.

        Returns:
            None.

        Raises:
            ValueError:
                If required identity fields are empty.
            TypeError:
                If boolean posture flags are invalid.
        """
        super().__init__()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        if not isinstance(ai_native_enabled, bool):
            raise TypeError("ai_native_enabled must be a bool.")
        if not isinstance(rift_enabled, bool):
            raise TypeError("rift_enabled must be a bool.")
        if not isinstance(immutable, bool):
            raise TypeError("immutable must be a bool.")
        if root_conduit_name is not None and not root_conduit_name:
            raise ValueError("root_conduit_name cannot be empty.")
        normalized_system_state = EnumHelpers.convert_enum_and_check(
            system_state,
            SystemState,
        )
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._frame_name: str = frame_name
        self._system_state: SystemState = normalized_system_state
        self._ai_native_enabled: bool = ai_native_enabled
        self._rift_enabled: bool = rift_enabled
        self._immutable: bool = immutable
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}
        self._root_conduit_name: Optional[str] = root_conduit_name

    @classmethod
    def create_dynamic_defaults(
            cls,
            frame_name: str,
            *,
            immutable: bool = False,
            metadata: Optional[Dict[str, object]] = None,
            root_conduit_name: Optional[str] = None,
    ) -> "NexusFrameConfiguration":
        """
        Create one dynamic authored frame configuration.

        Args:
            frame_name:
                Stable frame name to author.
            immutable:
                Whether the frame should reject normal removal.
            metadata:
                Optional authored metadata payload.
            root_conduit_name:
                Optional root conduit name to bootstrap after init.

        Returns:
            NexusFrameConfiguration: Dynamic authored frame configuration.
        """
        return cls(
            frame_name=frame_name,
            system_state=SystemState.dynamic,
            ai_native_enabled=True,
            rift_enabled=True,
            immutable=immutable,
            metadata=metadata,
            root_conduit_name=root_conduit_name,
        )

    @classmethod
    def create_automatic_defaults(
            cls,
            frame_name: str,
            *,
            immutable: bool = False,
            metadata: Optional[Dict[str, object]] = None,
            root_conduit_name: Optional[str] = None,
    ) -> "NexusFrameConfiguration":
        """
        Create one automatic authored frame configuration.

        Args:
            frame_name:
                Stable frame name to author.
            immutable:
                Whether the frame should reject normal removal.
            metadata:
                Optional authored metadata payload.
            root_conduit_name:
                Optional root conduit name to bootstrap after init.

        Returns:
            NexusFrameConfiguration: Automatic authored frame configuration.
        """
        return cls(
            frame_name=frame_name,
            system_state=SystemState.automatic,
            ai_native_enabled=False,
            rift_enabled=True,
            immutable=immutable,
            metadata=metadata,
            root_conduit_name=root_conduit_name,
        )

    @property
    def id(self) -> str:
        """
        Return the stable authored configuration id.

        Returns:
            str: Stable authored configuration id.
        """
        self.check_cleaned()
        return self._id

    @property
    def frame_name(self) -> str:
        """Return the authored frame name."""
        self.check_cleaned()
        return self._frame_name

    @property
    def system_state(self) -> SystemState:
        """Return the authored runtime posture."""
        self.check_cleaned()
        return self._system_state

    @property
    def ai_native_enabled(self) -> bool:
        """Return whether AI-native posture is enabled."""
        self.check_cleaned()
        return self._ai_native_enabled

    @property
    def rift_enabled(self) -> bool:
        """Return whether the frame should be Rift-visible."""
        self.check_cleaned()
        return self._rift_enabled

    @property
    def immutable(self) -> bool:
        """Return whether the frame is immutable."""
        self.check_cleaned()
        return self._immutable

    @property
    def metadata(self) -> Dict[str, object]:
        """Return a detached authored metadata copy."""
        self.check_cleaned()
        return dict(self._metadata)

    @property
    def root_conduit_name(self) -> Optional[str]:
        """Return the optional root conduit bootstrap name."""
        self.check_cleaned()
        return self._root_conduit_name

    def to_aetheric_frame_configuration(self) -> AethericFrameConfiguration:
        """
        Compile the authored posture into the narrow frame runtime posture.

        Returns:
            AethericFrameConfiguration: Narrow frame posture object.
        """
        self.check_cleaned()
        return AethericFrameConfiguration(
            origin_spellbook_id=None,
            system_state=self._system_state,
            ai_native_enabled=self._ai_native_enabled,
            rift_enabled=self._rift_enabled,
        )

    def to_spellbook_configuration(self) -> Configuration:
        """
        Compile the authored posture into a Spellbook configuration.

        Returns:
            Configuration: Spellbook configuration suitable for optional root
            conduit bootstrap.
        """
        self.check_cleaned()
        configuration = Configuration(aether_frame=self._frame_name)
        if self._system_state == SystemState.dynamic:
            configuration.dynamic_defaults()
        else:
            configuration.automatic_defaults()
        configuration.with_ai_native(self._ai_native_enabled)
        configuration.with_rift_enabled(self._rift_enabled)
        return configuration

    def cleanup(self) -> None:
        """
        Idempotently clear authored configuration state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._frame_name = None
            self._system_state = None
            self._ai_native_enabled = None
            self._rift_enabled = None
            self._immutable = None
            self._metadata = None
            self._root_conduit_name = None
            self._id = None
        self._lock = None
