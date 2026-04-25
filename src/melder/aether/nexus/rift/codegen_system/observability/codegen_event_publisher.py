import threading
from typing import Dict

from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import (
    ICodegenExecutionResult,
    ICodegenRiftSpace,
    ICodegenTransactionContext,
    ICodegenValidationResult,
)


class CodegenEventPublisher(Cleanable):
    """
    Internal

    Room-event publisher for codegen lifecycle signals.

    Purpose:
        Reuse the owning room's `RiftEventSystem` for codegen lifecycle
        publication instead of introducing a codegen-local queue, cache, or
        retained history store.

    Contract:
        - Borrows the owning room only to reach its event system.
        - Emits lightweight descriptive lifecycle events.
        - Does not persist codegen history or own a retained event buffer.
        - Never emits the full code body into room events; full source belongs
          in room memory records instead.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_space",
    ]

    def __init__(self, *, space: object) -> None:
        """
        Initialize one codegen event publisher.

        Args:
            space:
                Owning room whose event system should receive codegen events.

        Returns:
            None.

        Raises:
            TypeError:
                If `space` is None.
        """
        super().__init__()
        if space is None:
            raise TypeError("space cannot be None.")
        self._lock: threading.RLock = threading.RLock()
        self._space: ICodegenRiftSpace = space

    def cleanup(self) -> None:
        """
        Idempotently clear publisher-owned references.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._space = None
        self._lock = None

    def publish_validation_started(
            self,
            transaction_context: ICodegenTransactionContext,
    ) -> None:
        """
        Emit one validation-started event.

        Args:
            transaction_context:
                Current codegen transaction context.

        Returns:
            None.
        """
        self._emit_event(
            event_type="codegen_validation_started",
            transaction_context=transaction_context,
            payload={
                "surface": "codegen",
                "phase": "validate",
            },
        )

    def publish_validation_finished(
            self,
            transaction_context: ICodegenTransactionContext,
            validation_result: ICodegenValidationResult,
    ) -> None:
        """
        Emit one validation-finished event.

        Args:
            transaction_context:
                Current codegen transaction context.
            validation_result:
                Validator-owned result for the request.

        Returns:
            None.
        """
        payload: Dict[str, object] = {
            "surface": "codegen",
            "phase": "validate",
            "accepted": validation_result.accepted,
            "validation_issue_count": len(validation_result.validation_issues),
        }
        if validation_result.reason is not None:
            payload["reason"] = validation_result.reason
        self._emit_event(
            event_type="codegen_validation_finished",
            transaction_context=transaction_context,
            payload=payload,
        )

    def publish_execution_started(
            self,
            transaction_context: ICodegenTransactionContext,
    ) -> None:
        """
        Emit one execution-started event.

        Args:
            transaction_context:
                Current codegen transaction context.

        Returns:
            None.
        """
        self._emit_event(
            event_type="codegen_execution_started",
            transaction_context=transaction_context,
            payload={
                "surface": "codegen",
                "phase": "execute",
            },
        )

    def publish_execution_finished(
            self,
            transaction_context: ICodegenTransactionContext,
            execution_result: ICodegenExecutionResult,
    ) -> None:
        """
        Emit one execution-finished event.

        Args:
            transaction_context:
                Current codegen transaction context.
            execution_result:
                Executor-owned result for the request.

        Returns:
            None.
        """
        payload: Dict[str, object] = {
            "surface": "codegen",
            "phase": "execute",
            "accepted": execution_result.accepted,
            "validation_issue_count": len(execution_result.validation_issues),
            "result_present": execution_result.result is not None,
        }
        if execution_result.reason is not None:
            payload["reason"] = execution_result.reason
        if execution_result.runtime_error is not None:
            payload["runtime_error"] = execution_result.runtime_error
        self._emit_event(
            event_type="codegen_execution_finished",
            transaction_context=transaction_context,
            payload=payload,
        )

    def _emit_event(
            self,
            *,
            event_type: str,
            transaction_context: ICodegenTransactionContext,
            payload: Dict[str, object],
    ) -> None:
        """
        Emit one room-local codegen event.

        Args:
            event_type:
                Stable event type name.
            transaction_context:
                Current codegen transaction context.
            payload:
                Lightweight descriptive payload for the event.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            if transaction_context is None:
                raise TypeError("transaction_context cannot be None.")
            event_payload: Dict[str, object] = {
                "transaction_id": transaction_context.transaction_id,
                "code_hash": transaction_context.code_hash,
                "code_length": len(transaction_context.code),
            }
            event_payload.update(payload)
            self._space.event_system.create_and_emit_event(
                event_type,
                frame_name=transaction_context.frame_name,
                payload=event_payload,
            )
