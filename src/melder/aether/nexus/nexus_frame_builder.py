from typing import Any, Dict, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.spellbook.configuration.system_state import SystemState
from melder.utilities.general_base.cleanable import Cleanable

from melder.aether.nexus.nexus_frame_configuration import NexusFrameConfiguration


class NexusFrameBuilder(Cleanable):
    """
    Fluent authored-frame builder for Nexus-managed frames.

    Purpose:
        Provide a compact fluent surface for users and agents to author one
        Nexus-managed frame configuration before creating it.

    Contract:
        - One builder instance is scoped to one frame name.
        - The builder is mutable until `build()` or `create()` is called.
        - `create()` delegates to the owning `NexusFrameManager`.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_manager",
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
            manager: Any,
            frame_name: str,
    ) -> None:
        super().__init__()
        if manager is None:
            raise TypeError("manager cannot be None.")
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        self._manager = manager
        self._frame_name = frame_name
        self._system_state: Optional[SystemState] = None
        self._ai_native_enabled: Optional[bool] = None
        self._rift_enabled: Optional[bool] = None
        self._immutable: bool = False
        self._metadata: Dict[str, object] = {}
        self._root_conduit_name: Optional[str] = None

    def dynamic_defaults(self) -> "NexusFrameBuilder":
        """
        Apply the standard dynamic authored-frame posture.

        Returns:
            NexusFrameBuilder: This builder for fluent chaining.
        """
        self._system_state = SystemState.dynamic
        self._ai_native_enabled = True
        self._rift_enabled = True
        return self

    def automatic_defaults(self) -> "NexusFrameBuilder":
        """
        Apply the standard automatic authored-frame posture.

        Returns:
            NexusFrameBuilder: This builder for fluent chaining.
        """
        self._system_state = SystemState.automatic
        self._ai_native_enabled = False
        self._rift_enabled = True
        return self

    def system_state(self, system_state: SystemState) -> "NexusFrameBuilder":
        """
        Override the authored frame system state.

        Args:
            system_state:
                Desired authored runtime posture.

        Returns:
            NexusFrameBuilder: This builder for fluent chaining.
        """
        self._system_state = system_state
        return self

    def ai_native_enabled(self, enabled: bool = True) -> "NexusFrameBuilder":
        """
        Override the authored AI-native posture flag.

        Args:
            enabled:
                True when AI-native posture should be enabled.

        Returns:
            NexusFrameBuilder: This builder for fluent chaining.
        """
        self._ai_native_enabled = enabled
        return self

    def rift_enabled(self, enabled: bool = True) -> "NexusFrameBuilder":
        """
        Override the authored Rift-visible posture flag.

        Args:
            enabled:
                True when Rift-visible posture should be enabled.

        Returns:
            NexusFrameBuilder: This builder for fluent chaining.
        """
        self._rift_enabled = enabled
        return self

    def immutable(self, immutable: bool = True) -> "NexusFrameBuilder":
        """
        Override the authored immutability flag.

        Args:
            immutable:
                True when the authored frame should reject normal removal.

        Returns:
            NexusFrameBuilder: This builder for fluent chaining.
        """
        self._immutable = immutable
        return self

    def metadata(self, metadata: Dict[str, object]) -> "NexusFrameBuilder":
        """
        Replace the authored metadata payload.

        Args:
            metadata:
                Authored metadata payload for the frame.

        Returns:
            NexusFrameBuilder: This builder for fluent chaining.
        """
        self._metadata = dict(metadata) if metadata else {}
        return self

    def with_root_conduit(
            self,
            root_conduit_name: str = "root",
    ) -> "NexusFrameBuilder":
        """
        Request one root-conduit bootstrap after frame init.

        Args:
            root_conduit_name:
                Root conduit name to bootstrap.

        Returns:
            NexusFrameBuilder: This builder for fluent chaining.
        """
        if not root_conduit_name:
            raise ValueError("root_conduit_name cannot be empty.")
        self._root_conduit_name = root_conduit_name
        return self

    def without_root_conduit(self) -> "NexusFrameBuilder":
        """
        Clear any requested root-conduit bootstrap.

        Returns:
            NexusFrameBuilder: This builder for fluent chaining.
        """
        self._root_conduit_name = None
        return self

    def build(self) -> NexusFrameConfiguration:
        """
        Build one immutable authored frame configuration.

        Returns:
            NexusFrameConfiguration: Built authored frame configuration.
        """
        if self._system_state is None:
            raise ValueError("system_state must be configured before build().")
        if self._ai_native_enabled is None:
            raise ValueError("ai_native_enabled must be configured before build().")
        if self._rift_enabled is None:
            raise ValueError("rift_enabled must be configured before build().")
        return NexusFrameConfiguration(
            frame_name=self._frame_name,
            system_state=self._system_state,
            ai_native_enabled=self._ai_native_enabled,
            rift_enabled=self._rift_enabled,
            immutable=self._immutable,
            metadata=self._metadata,
            root_conduit_name=self._root_conduit_name,
        )

    def create(self):
        """
        Build and create the authored frame through the owning manager.

        Returns:
            IAethericFrame: Created managed frame.
        """
        return self._manager.create(self.build())

    def cleanup(self) -> None:
        """
        Idempotently clear builder-owned temporary state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._manager = None
        self._frame_name = None
        self._system_state = None
        self._ai_native_enabled = None
        self._rift_enabled = None
        self._immutable = None
        self._metadata = None
        self._root_conduit_name = None
