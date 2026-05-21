from typing import TYPE_CHECKING, Protocol, runtime_checkable

from melder.utilities.interfaces.iaethericframe import IAethericFrame
from melder.utilities.interfaces.iaethericframeconfiguration import (
    IAethericFrameConfiguration,
)

if TYPE_CHECKING:
    from melder.nexus.frame_descriptor.frame_record import FrameRecord


@runtime_checkable
class IFrameDescriptor(Protocol):
    """
    Interface for the frame-scoped Nexus descriptor aggregate.

    Purpose:
        Expose the runtime publication hooks that Nexus-managed frame
        orchestration uses without binding callers to the concrete
        `FrameDescriptor` implementation.

    Contract:
        - Accepts the live frame handle and live frame posture object used by
          Nexus publication flows.
        - Accepts one detached frame overview record.
        - Can clear runtime-owned publication state during frame disposal.
    """

    def set_frame_handle(self, frame: IAethericFrame) -> None:
        """
        Attach the live frame handle to the descriptor.
        """
        ...

    def set_frame_configuration(
            self,
            frame_configuration: IAethericFrameConfiguration,
    ) -> None:
        """
        Attach the live frame posture object to the descriptor.
        """
        ...

    def set_frame_overview(self, frame_record: "FrameRecord") -> None:
        """
        Publish one detached frame overview record into the descriptor.
        """
        ...

    def clear_runtime_publication_state(self) -> None:
        """
        Clear runtime-owned publication data from the descriptor.
        """
        ...


