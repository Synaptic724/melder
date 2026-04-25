from typing import Any

from melder.aether.nexus.rift.codegen_system.codegen_transaction_context import (
    CodegenTransactionContext,
)
from melder.aether.nexus.rift.codegen_system.execution.codegen_execution_result import (
    CodegenExecutionResult,
)


class CodegenExecutor:
    """
    Internal

    Owner of governed code execution for one codegen request.

    Purpose:
        Execute one compiled code object against one built codegen namespace and
        return the execution-layer result.
    """

    __slots__ = []

    def execute(
            self,
            compiled_code: Any,
            transaction_context: CodegenTransactionContext,
    ) -> CodegenExecutionResult:
        """
        Execute one compiled code object against the transaction namespace.

        Args:
            compiled_code:
                Compiled Python code object.
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
        if transaction_context is None:
            raise TypeError("transaction_context cannot be None.")
        namespace = transaction_context.namespace
        if namespace is None:
            raise RuntimeError("codegen transaction has no built namespace.")
        try:
            exec(compiled_code, namespace.globals_dict, namespace.locals_dict)
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

