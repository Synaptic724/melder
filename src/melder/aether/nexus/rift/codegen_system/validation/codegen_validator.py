import ast

from melder.aether.nexus.rift.codegen_system.codegen_transaction_context import (
    CodegenTransactionContext,
)
from melder.aether.nexus.rift.codegen_system.validation.codegen_validation_result import (
    CodegenValidationResult,
)


class CodegenValidator:
    """
    Internal

    Root validation orchestrator for one codegen request.

    Purpose:
        Own the validation boundary for generated Python without absorbing
        later execution or reporting responsibilities.

    Contract:
        - Validates one `CodegenTransactionContext`.
        - Performs AST parse as the first live validation step.
        - Returns syntax failure when parsing fails.
        - Returns the current not-implemented result when syntax is valid but
          the deeper strategy family is not yet implemented.
    """

    __slots__ = []

    def validate(
            self,
            transaction_context: CodegenTransactionContext,
    ) -> CodegenValidationResult:
        """
        Validate one codegen transaction context.

        Args:
            transaction_context:
                Per-call transaction context to validate.

        Returns:
            CodegenValidationResult: Validation result for the request.

        Raises:
            TypeError:
                If `transaction_context` is None.
        """
        if transaction_context is None:
            raise TypeError("transaction_context cannot be None.")
        try:
            ast.parse(transaction_context.code, mode="exec")
        except SyntaxError as exc:
            return CodegenValidationResult.syntax_error(
                frame_name=transaction_context.frame_name,
                transaction_id=transaction_context.transaction_id,
                message=self._build_syntax_error_message(exc),
            )
        return CodegenValidationResult.not_implemented(
            frame_name=transaction_context.frame_name,
            transaction_id=transaction_context.transaction_id,
        )

    @staticmethod
    def _build_syntax_error_message(exc: SyntaxError) -> str:
        """
        Build one stable syntax-error message for codegen validation output.

        Args:
            exc:
                Raised syntax error.

        Returns:
            str: Stable syntax-error message.
        """
        line_number = exc.lineno
        offset = exc.offset
        if line_number is None or offset is None:
            return "SyntaxError: {0}".format(exc.msg)
        return "SyntaxError at line {0}, column {1}: {2}".format(
            line_number,
            offset,
            exc.msg,
        )

