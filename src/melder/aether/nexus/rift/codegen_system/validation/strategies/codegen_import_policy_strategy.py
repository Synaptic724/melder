import ast
from typing import Optional

from melder.aether.nexus.rift.codegen_system.codegen_transaction_context import (
    CodegenTransactionContext,
)
from melder.aether.nexus.rift.codegen_system.validation.codegen_validation_result import (
    CodegenValidationResult,
)


class CodegenImportPolicyStrategy:
    """
    Internal

    Import-policy validation strategy.

    Purpose:
        Block import statements in the current governed codegen mode.
    """

    __slots__ = []

    def validate(
            self,
            transaction_context: CodegenTransactionContext,
            syntax_tree: ast.AST,
    ) -> Optional[CodegenValidationResult]:
        """
        Validate import policy rules for one codegen request.

        Args:
            transaction_context:
                Per-call codegen transaction context.
            syntax_tree:
                Parsed AST for the request.

        Returns:
            Optional[CodegenValidationResult]:
                Failure result when a rule is violated; otherwise None.
        """
        for node in ast.walk(syntax_tree):
            if isinstance(node, ast.Import):
                return self._reject(
                    transaction_context,
                    "Import statements are not allowed in this codegen mode.",
                )
            if isinstance(node, ast.ImportFrom):
                return self._reject(
                    transaction_context,
                    "Import-from statements are not allowed in this codegen mode.",
                )
        return None

    @staticmethod
    def _reject(
            transaction_context: CodegenTransactionContext,
            message: str,
    ) -> CodegenValidationResult:
        """
        Build one import-policy validation failure result.

        Args:
            transaction_context:
                Per-call transaction context.
            message:
                Failure message.

        Returns:
            CodegenValidationResult: Import-policy validation failure.
        """
        return CodegenValidationResult.validation_failed(
            frame_name=transaction_context.frame_name,
            message=message,
            transaction_id=transaction_context.transaction_id,
        )

