import threading
from typing import TYPE_CHECKING, Dict
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.nexus.rift.codegen_system.codegen_transaction_context import (
        CodegenTransactionContext,
    )
    from melder.nexus.rift.codegen_system.execution.codegen_execution_result import (
        CodegenExecutionResult,
    )
    from melder.nexus.rift.rift_space.codegen_rift_space import CodegenRiftSpace
    from melder.nexus.rift.codegen_system.validation.codegen_validation_result import (
        CodegenValidationResult,
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

    Registration:
        MELDER KERNEL - guarded. Owned by `CodegenMonitor`.

    Subsystem Context:
        The thin publication adapter between the codegen engine and the room's
        `RiftEventSystem`.

    System Context:
        BORROWING the owning room only to reach its event system - rather than
        owning a codegen-local queue, cache, or retained history - is what keeps
        event delivery consistent with the room's own ordering and lifecycle.
        A private queue would introduce a second delivery path with its own
        buffering semantics, and callbacks registered on the room would silently
        miss codegen events or receive them out of order relative to everything
        else.
    """

    __melder_internal__ = _mrg.sentinel
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
        self._space: CodegenRiftSpace = space

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
            del self._space
        del self._lock

    def publish_validation_started(
            self,
            transaction_context: CodegenTransactionContext,
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
            transaction_context: CodegenTransactionContext,
            validation_result: CodegenValidationResult,
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
            transaction_context: CodegenTransactionContext,
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
            transaction_context: CodegenTransactionContext,
            execution_result: CodegenExecutionResult,
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
            transaction_context: CodegenTransactionContext,
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
