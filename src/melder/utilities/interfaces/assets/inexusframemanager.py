from typing import Protocol, runtime_checkable
from melder.utilities.interfaces.assets.icleanable import ICleanable

@runtime_checkable
class INexusFrameManager(ICleanable, Protocol):
    """
    Interface for the Nexus-managed frame authoring facade.

    Purpose:
        Expose the authored-frame creation contract used by collaborators that
        should depend on the frame-manager capability surface without importing
        the concrete runtime implementation directly.

    Contract:
        - Realizes only Nexus-managed frames that satisfy the fixed
          dynamic/AI-native/Rift-enabled posture contract.
        - Consumes authored `NexusFrameConfiguration` objects as immutable
          inputs to frame realization.
        - Returns rooted `IConduit` objects for the realized Nexus-managed
          workspace.
    """

    def create(
            self,
            configuration: "NexusFrameConfiguration",
    ) -> "IConduit":
        """
        Realize one rooted Nexus-managed conduit from authored configuration.

        Returns:
            IConduit: Root conduit for the realized Nexus-managed workspace.
        """
        ...
