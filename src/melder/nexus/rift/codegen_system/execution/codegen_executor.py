import threading
from typing import TYPE_CHECKING
from types import CodeType

from melder.nexus.rift.codegen_system.execution.codegen_execution_result import (
    CodegenExecutionResult,
)
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.nexus.rift.codegen_system.codegen_transaction_context import (
        CodegenTransactionContext,
    )


class CodegenExecutor(Cleanable):
    """
    Internal

    Owner of governed code execution for one codegen request.

    Purpose:
        Execute one compiled code object against one built codegen namespace and
        return the execution-layer result.

    Registration:
        MELDER KERNEL - guarded. Owned by `CodegenSystem`.

    Subsystem Context:
        The final stage of the engine: it runs one compiled code object against
        one built `CodegenNamespace` and returns a `CodegenExecutionResult`.

    System Context:
        Execution is GOVERNED by construction rather than by policy checks at
        run time. By the moment this stage runs, the validator has accepted the
        source, the compiler has produced the code object, and the namespace
        builder has exposed only what configuration allowed - so the executor's
        safety comes from what the code can REACH, not from watching what it
        does.
        That is why the namespace is built only after accepted validation: the
        executor has no way to retract reach once execution begins.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Owner of governed code execution for one codegen request. Melder "
        "kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]

    def __init__(self) -> None:
        """
        Initialize one codegen executor.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        """
        Idempotently cleanup the executor.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
        del self._lock

    def execute(
            self,
            compiled_code: CodeType,
            transaction_context: CodegenTransactionContext,
    ) -> CodegenExecutionResult:
        """
        Execute one compiled code object against the transaction namespace.

        Args:
            compiled_code:
                Compiled Python code object produced by `CodegenCompiler`.
            transaction_context:
                Per-call transaction context holding the built namespace.

        Returns:
            CodegenExecutionResult: Execution result for the request.

        Raises:
            TypeError:
                If `transaction_context` is None.
            RuntimeError:
                If the transaction has no built namespace.
        """
        self.check_cleaned()
        with self._lock:
            if transaction_context is None:
                raise TypeError("transaction_context cannot be None.")
            namespace = transaction_context.namespace
            if namespace is None:
                raise RuntimeError("codegen transaction has no built namespace.")
            try:
                execution_namespace = namespace.globals_dict
                exec(compiled_code, execution_namespace, execution_namespace)
                namespace.locals_dict.clear()
                namespace.locals_dict.update(execution_namespace)
            except Exception as exc:
                return CodegenExecutionResult.runtime_failed(
                    frame_name=transaction_context.frame_name,
                    runtime_error="{0}: {1}".format(
                        exc.__class__.__name__,
                        exc,
                    ),
                    transaction_id=transaction_context.transaction_id,
                )
            return CodegenExecutionResult.executed(
                frame_name=transaction_context.frame_name,
                result=namespace.get_result(),
                transaction_id=transaction_context.transaction_id,
            )
