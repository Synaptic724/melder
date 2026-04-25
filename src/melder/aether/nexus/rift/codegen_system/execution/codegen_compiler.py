from typing import Any

from melder.aether.nexus.rift.codegen_system.codegen_transaction_context import (
    CodegenTransactionContext,
)


class CodegenCompiler:
    """
    Internal

    Internal compile stage for codegen execution.

    Purpose:
        Compile generated Python source into one executable code object for the
        executor without absorbing execution or validation responsibilities.
    """

    __slots__ = []

    def compile(
            self,
            transaction_context: CodegenTransactionContext,
    ) -> Any:
        """
        Compile one codegen transaction into an executable code object.

        Args:
            transaction_context:
                Per-call codegen transaction context.

        Returns:
            Any: Compiled Python code object.

        Raises:
            TypeError:
                If `transaction_context` is None.
        """
        if transaction_context is None:
            raise TypeError("transaction_context cannot be None.")
        return compile(
            transaction_context.code,
            "<melder-codegen:{0}>".format(transaction_context.transaction_id),
            "exec",
        )

