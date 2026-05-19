import threading
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.nexus.rift.codegen_system.observability.codegen_event_publisher import (
    CodegenEventPublisher,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.icodegenexecutionresult import ICodegenExecutionResult
from melder.utilities.interfaces.icodegentransactioncontext import ICodegenTransactionContext
from melder.utilities.interfaces.icodegenvalidationresult import ICodegenValidationResult


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
    """

    __melder_internal__ = _mrg.sentinel
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
            transaction_context: ICodegenTransactionContext,
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
            transaction_context: ICodegenTransactionContext,
            validation_result: ICodegenValidationResult,
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
            transaction_context: ICodegenTransactionContext,
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
            transaction_context: ICodegenTransactionContext,
            execution_result: ICodegenExecutionResult,
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
