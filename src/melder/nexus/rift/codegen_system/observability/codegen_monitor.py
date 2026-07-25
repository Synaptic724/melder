import threading
from typing import TYPE_CHECKING

from melder.nexus.rift.codegen_system.observability.codegen_event_publisher import (
    CodegenEventPublisher,
)
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.nexus.rift.codegen_system.codegen_transaction_context import (
        CodegenTransactionContext,
    )
    from melder.nexus.rift.codegen_system.execution.codegen_execution_result import (
        CodegenExecutionResult,
    )
    from melder.nexus.rift.codegen_system.validation.codegen_validation_result import (
        CodegenValidationResult,
    )


class CodegenMonitor(Cleanable):
    """
    Internal

    Thin room-event monitor for codegen lifecycle publication.

    Purpose:
        Provide one explicit monitoring seam for codegen that normalizes
        lifecycle events into the owning room's `RiftEventSystem` without
        owning retained state itself.

    Contract:
        - Owns one `CodegenEventPublisher`.
        - Does not own caches, history, or workflow state.
        - Exists only to keep codegen lifecycle publication explicit and
          bounded.

    Registration:
        MELDER KERNEL - guarded. Owned by `CodegenSystem`.

    Subsystem Context:
        The lifecycle observability seam, owning one `CodegenEventPublisher`
        and normalizing engine events into the room's `RiftEventSystem`.

    System Context:
        Owning NO retained state is the deliberate choice here. A monitor with
        its own history store would become a second source of truth about what
        happened, competing with the room's `RiftMemorySystem`, and would keep
        request state alive past the request.
        Normalizing into the ROOM's event system keeps one event ordering per
        room, so codegen lifecycle signals interleave coherently with everything
        else the room publishes rather than forming a private timeline.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Thin room-event monitor for codegen lifecycle publication. Melder "
        "kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_event_publisher",
    ]

    def __init__(self, *, space: object) -> None:
        """
        Initialize one codegen monitor.

        Args:
            space:
                Owning room whose event system should receive codegen events.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._event_publisher: CodegenEventPublisher = CodegenEventPublisher(
            space=space,
        )

    def cleanup(self) -> None:
        """
        Idempotently cleanup the monitor and its publisher.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._event_publisher.cleanup()
            del self._event_publisher
        del self._lock

    def on_validation_started(
            self,
            transaction_context: CodegenTransactionContext,
    ) -> None:
        """
        Publish one validation-started lifecycle signal.

        Args:
            transaction_context:
                Current codegen transaction context.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._event_publisher.publish_validation_started(transaction_context)

    def on_validation_finished(
            self,
            transaction_context: CodegenTransactionContext,
            validation_result: CodegenValidationResult,
    ) -> None:
        """
        Publish one validation-finished lifecycle signal.

        Args:
            transaction_context:
                Current codegen transaction context.
            validation_result:
                Validator-owned result.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._event_publisher.publish_validation_finished(
                transaction_context,
                validation_result,
            )

    def on_execution_started(
            self,
            transaction_context: CodegenTransactionContext,
    ) -> None:
        """
        Publish one execution-started lifecycle signal.

        Args:
            transaction_context:
                Current codegen transaction context.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._event_publisher.publish_execution_started(transaction_context)

    def on_execution_finished(
            self,
            transaction_context: CodegenTransactionContext,
            execution_result: CodegenExecutionResult,
    ) -> None:
        """
        Publish one execution-finished lifecycle signal.

        Args:
            transaction_context:
                Current codegen transaction context.
            execution_result:
                Executor-owned result.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._event_publisher.publish_execution_finished(
                transaction_context,
                execution_result,
            )
