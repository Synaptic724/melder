from typing import Dict, Optional, Protocol, runtime_checkable

from melder.spellbook.configuration.system_state import SystemState
from melder.utilities.interfaces.iaethericframeconfiguration import IAethericFrameConfiguration
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iconfiguration import IConfiguration


@runtime_checkable
class INexusFrameConfiguration(ICleanable, Protocol):
    """
    Authored frame configuration for one Nexus-managed frame.

    Purpose:
        Capture the authored frame posture and required root-conduit bootstrap
        intent for one Nexus-managed frame before the manager realizes it.

    Contract:
        - Stores only Nexus frame-authoring inputs, not live frame objects.
        - Uses the narrower frame posture fields that later compile into
          `IAethericFrameConfiguration`.
        - Nexus-managed frames are always dynamic, AI-native, and Rift-enabled.
        - Always carries one root-conduit bootstrap name for rooted creation.
        - Is immutable-by-convention after construction.
    """

    @property
    def id(self) -> str:
        """Stable authored configuration identifier."""
        ...

    @property
    def frame_name(self) -> str:
        """Stable frame identity that the manager will realize."""
        ...

    @property
    def system_state(self) -> SystemState:
        """Authored runtime posture for the frame."""
        ...

    @property
    def ai_native_enabled(self) -> bool:
        """Whether AI-native posture is enabled."""
        ...

    @property
    def rift_enabled(self) -> bool:
        """Whether the frame should be Rift-visible."""
        ...

    @property
    def immutable(self) -> bool:
        """Whether the authored frame should reject normal removal."""
        ...

    @property
    def metadata(self) -> Dict[str, object]:
        """Detached authored metadata snapshot."""
        ...

    @property
    def root_conduit_name(self) -> str:
        """Requested bootstrap root conduit name."""
        ...

    def cleanup(self) -> None:
        """Idempotently clear authored configuration state."""
        ...

    @classmethod
    def create_dynamic_defaults(
            cls,
            frame_name: str,
            *,
            immutable: bool = False,
            metadata: Optional[Dict[str, object]] = None,
            root_conduit_name: str = "root",
    ) -> "INexusFrameConfiguration":
        """Create the default dynamic Nexus-managed frame posture."""
        ...

    def to_aetheric_frame_configuration(self) -> IAethericFrameConfiguration:
        """Compile the authored posture into the narrow frame runtime posture."""
        ...

    def to_spellbook_configuration(self) -> IConfiguration:
        """Compile the authored posture into a Spellbook configuration surface."""
        ...
