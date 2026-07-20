from typing import TYPE_CHECKING, Dict, Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.aether.spellbook.configuration.system_state import SystemState
from melder.utilities.general_base.cleanable import Cleanable

from melder.nexus.nexus_frame_configuration import NexusFrameConfiguration
if TYPE_CHECKING:
    from melder.aether.conduit.conduit import Conduit
    from melder.nexus.nexus_frame_manager import NexusFrameManager


class NexusFrameBuilder(Cleanable):
    """
    Fluent authored-frame builder for Nexus-managed frames.

    Purpose:
        Provide a compact fluent surface for users and agents to author one
        Nexus-managed frame configuration before creating it.

    Contract:
        - One builder instance is scoped to one frame name.
        - The builder defaults to the only valid Nexus-managed frame posture:
          dynamic, AI-native, and Rift-enabled.
        - The builder is mutable until `build()` or `create()` is called.
        - `create()` delegates to the owning `NexusFrameManager`.

    Lifecycle:
        Builders are lightweight, short-lived authoring helpers created by
        `NexusFrameManager.begin(...)` and typically consumed immediately by
        `build()` or `create()`.

    Threading:
        Short-lived and caller-confined; not intended for sharing across
        threads.

    Registration:
        MELDER KERNEL - guarded. Created by `NexusFrameManager.begin(...)`;
        never constructed directly.

    Subsystem Context:
        The fluent authoring front for `NexusFrameManager`, mirroring the
        builder pairing used by the Aether, Spellbook, crystallizer, and
        mutation-research configurations.

    System Context:
        Defaulting to the only valid managed posture - dynamic, AI-native,
        Rift-enabled - is what makes this builder honest rather than merely
        convenient. Offering those as configurable options would imply
        combinations that `NexusFrameManager` will refuse, so the builder
        presents the one shape that can actually be created.
        `create()` delegating to the manager keeps authoring and realization
        separate: the builder stages intent, the manager applies strict-create
        semantics and topology rules. That is why `build()` and `create()` are
        distinct - a caller may want the configuration without realizing it.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Fluent authored-frame builder for Nexus-managed frames. Melder kernel "
        "machinery: read it to understand the runtime, do not drive it directly."
    )

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
            manager: NexusFrameManager,
            frame_name: str,
    ) -> None:
        """
        Initialize one fluent authored-frame builder.

        Purpose:
            Bind the builder to its owning manager and stable frame name while
            defaulting the authored posture to the only valid Nexus-managed
            frame contract: dynamic, AI-native, and Rift-enabled.

        Args:
            manager:
                Owning `NexusFrameManager`.
            frame_name:
                Stable frame name being authored.

        Returns:
            None.

        Raises:
            TypeError:
                If `manager` is missing.
            ValueError:
                If `frame_name` is empty.
        """
        super().__init__()
        if manager is None:
            raise TypeError("manager cannot be None.")
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        self._manager: NexusFrameManager = manager
        self._frame_name: str = frame_name
        self._system_state: SystemState = SystemState.dynamic
        self._ai_native_enabled: Optional[bool] = True
        self._rift_enabled: Optional[bool] = True
        self._immutable: bool = False
        self._metadata: Dict[str, object] = {}
        self._root_conduit_name: str = "root"

    def cleanup(self) -> None:
        """
        Idempotently clear builder-owned temporary state.

        Purpose:
            Release transient builder state once authoring is complete or the
            builder is discarded.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._manager
        del self._frame_name
        del self._system_state
        del self._ai_native_enabled
        del self._rift_enabled
        del self._immutable
        del self._metadata
        del self._root_conduit_name

    def dynamic_defaults(self) -> "NexusFrameBuilder":
        """
        Apply the standard dynamic authored-frame posture.

        Purpose:
            Configure the builder for the common AI-native dynamic frame mode
            without requiring callers to set each posture field manually.

        Returns:
            NexusFrameBuilder: This builder for fluent chaining.
        """
        self.check_cleaned()
        self._system_state: SystemState = SystemState.dynamic
        self._ai_native_enabled: bool = True
        self._rift_enabled: bool = True
        return self

    def immutable(self, immutable: bool = True) -> "NexusFrameBuilder":
        """
        Override the authored immutability flag.

        Purpose:
            Mark the authored frame as protected from normal removal when the
            manager later realizes it.

        Args:
            immutable:
                True when the authored frame should reject normal removal.

        Returns:
            NexusFrameBuilder: This builder for fluent chaining.
        """
        self.check_cleaned()
        self._immutable = immutable
        return self

    def metadata(self, metadata: Dict[str, object]) -> "NexusFrameBuilder":
        """
        Replace the authored metadata payload.

        Purpose:
            Attach detached authoring metadata that the caller wants preserved
            on the authored configuration.

        Args:
            metadata:
                Authored metadata payload for the frame.

        Returns:
            NexusFrameBuilder: This builder for fluent chaining.
        """
        self.check_cleaned()
        self._metadata = dict(metadata) if metadata else {}
        return self

    def with_root_conduit(
            self,
            root_conduit_name: str = "root",
    ) -> "NexusFrameBuilder":
        """
        Request one root-conduit bootstrap after frame init.

        Purpose:
            Record the intent to create a starter root conduit immediately
            after the frame is realized, which gives agent-created frames a
            ready-to-use entry topology.

        Args:
            root_conduit_name:
                Root conduit name to bootstrap.

        Returns:
            NexusFrameBuilder: This builder for fluent chaining.
        """
        self.check_cleaned()
        if not root_conduit_name:
            raise ValueError("root_conduit_name cannot be empty.")
        self._root_conduit_name = root_conduit_name
        return self

    def build(self) -> NexusFrameConfiguration:
        """
        Build one immutable authored frame configuration.

        Purpose:
            Freeze the currently accumulated builder state into a detached
            authored configuration object that can be passed around or realized
            later.

        Contract:
            - Fails fast when required posture fields have not been set.
            - Returns a new `NexusFrameConfiguration` detached from future
              builder mutation.

        Returns:
            NexusFrameConfiguration: Built authored frame configuration.
        """
        self.check_cleaned()
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

    def create(self) -> Conduit:
        """
        Build and create the authored frame through the owning manager.

        Purpose:
            Provide the fluent one-shot path that both finalizes the authored
            configuration and realizes the rooted Nexus-managed conduit
            immediately.

        Returns:
            Conduit: Rooted conduit created through the owning manager.
        """
        self.check_cleaned()
        return self._manager.create(self.build())

