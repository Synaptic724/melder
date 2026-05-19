from typing import Optional, Protocol, runtime_checkable
from melder.aether.aetheric_frame.dev_ops.change_control_manager.orchestrator.staged_mutation import (
    ChangeControlStagedMutation,
)


@runtime_checkable
class IChangeControlOrchestrator(Protocol):
    """
    Interface for the change-control staged-mutation orchestrator.
    """

    def get_staged(self, request_id: str) -> Optional[ChangeControlStagedMutation]:
        """
        Return one staged mutation by request id, if present.
        """
        ...
